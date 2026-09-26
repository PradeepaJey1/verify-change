# VerifyChange

Know what to check before release.

A small Python application that generates manual release checks from a ticket and PR through the OpenAI Responses API. It uses only the Python standard library.

## Use

Save a ticket and PR description or diff as UTF-8 text files in `inputs/` (this folder is ignored by Git). To prepare a prompt without calling the API, run:

```bash
PYTHONPATH=src python3 -m change_checklist inputs/ticket.txt inputs/pr.txt -o checklist-prompt.txt
```

Paste `checklist-prompt.txt` into your organization's approved AI tool. The prompt asks for concrete checks, expected results, missing context, and supporting evidence. See [change-checklist-prompt.md](change-checklist-prompt.md) for the prompt and a quick trial procedure.

To generate the checklist directly, open the local `.env` file and add your OpenAI API key after `OPENAI_API_KEY=`. The file is ignored by Git. Then run:

```bash
PYTHONPATH=src python3 -m change_checklist test/ticket.md test/pr.md --generate -o checklist.md
```

If you need a fresh `.env`, copy `.env.example` to `.env`. A key already set in your shell takes precedence over `.env`.

The default model is `gpt-6-sol` with medium reasoning. Use `--model MODEL_ID` to try another model. The API request sets `store` to `false`. Keep the API key out of the repository and use only ticket and PR content your organization permits you to send to the API.
