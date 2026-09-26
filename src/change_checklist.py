"""Prepare a prompt or generate a release checklist from a ticket and PR."""

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "change-checklist-prompt.md"
RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-6-sol"


def get_api_key() -> str | None:
    """Prefer the process environment, then read the repository's local .env."""
    if key := os.environ.get("OPENAI_API_KEY"):
        return key

    env_file = ROOT / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == "OPENAI_API_KEY":
            value = value.strip()
            if value.startswith(("'", '"')) and value.endswith(value[0]):
                value = value[1:-1]
            return value or None
    return None


def build_prompt(ticket: str, pr: str) -> str:
    document = PROMPT_FILE.read_text(encoding="utf-8")
    try:
        prompt = document.split("```text\n", 1)[1].split("\n```", 1)[0]
    except IndexError as error:
        raise ValueError(f"No text prompt found in {PROMPT_FILE}") from error
    prompt = prompt.replace(
        "[Paste the ticket title, description, and acceptance criteria here]",
        ticket.strip(),
    )
    prompt = prompt.replace(
        "[Paste the PR description, changed-file summary, and relevant diff here]",
        pr.strip(),
    )
    return prompt + "\n"


def generate_checklist(prompt: str, model: str, api_key: str) -> str:
    payload = {
        "model": model,
        "input": prompt,
        "reasoning": {"effort": "medium"},
        "max_output_tokens": 4000,
        "store": False,
    }
    request = Request(
        RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.load(response)
    except HTTPError as error:
        try:
            detail = json.load(error).get("error", {}).get("message", error.reason)
        except (ValueError, OSError):
            detail = error.reason
        raise RuntimeError(f"OpenAI API returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach the OpenAI API: {error.reason}") from error

    if result.get("status") != "completed":
        raise RuntimeError(f"OpenAI response did not complete: {result.get('status')}")
    text_parts = [
        content["text"]
        for item in result.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
        if content.get("type") == "output_text" and content.get("text")
    ]
    if not text_parts:
        raise RuntimeError("OpenAI response contained no checklist text")
    return "\n".join(text_parts).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare a prompt or generate a checklist from a ticket and PR."
    )
    parser.add_argument("ticket", type=Path, help="Text file containing the ticket")
    parser.add_argument("pr", type=Path, help="Text file containing the PR details")
    parser.add_argument("--generate", action="store_true", help="Call the OpenAI API")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model for --generate")
    parser.add_argument("-o", "--output", type=Path, help="Write to this file instead of stdout")
    args = parser.parse_args()

    try:
        prompt = build_prompt(
            args.ticket.read_text(encoding="utf-8"),
            args.pr.read_text(encoding="utf-8"),
        )
        if args.generate:
            api_key = get_api_key()
            if not api_key:
                parser.error("Add OPENAI_API_KEY to .env or set it in the environment")
            result = generate_checklist(prompt, args.model, api_key)
        else:
            result = prompt
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            label = "Checklist" if args.generate else "Prompt"
            print(f"{label} written to {args.output}")
        else:
            print(result, end="")
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
