"""Prepare the change checklist prompt from a ticket and PR."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = ROOT / "change-checklist-prompt.md"


def build_prompt(ticket: str, pr: str) -> str:
    document = PROMPT_FILE.read_text(encoding="utf-8")
    prompt = document.split("```text\n", 1)[1].split("\n```", 1)[0]
    prompt = prompt.replace(
        "[Paste the ticket title, description, and acceptance criteria here]",
        ticket.strip(),
    )
    prompt = prompt.replace(
        "[Paste the PR description, changed-file summary, and relevant diff here]",
        pr.strip(),
    )
    return prompt + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine a ticket and PR into a ready-to-use AI checklist prompt."
    )
    parser.add_argument("ticket", type=Path, help="Text file containing the ticket")
    parser.add_argument("pr", type=Path, help="Text file containing the PR details")
    parser.add_argument("-o", "--output", type=Path, help="Write to this file instead of stdout")
    args = parser.parse_args()

    try:
        result = build_prompt(
            args.ticket.read_text(encoding="utf-8"),
            args.pr.read_text(encoding="utf-8"),
        )
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Prompt written to {args.output}")
        else:
            print(result, end="")
    except OSError as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
