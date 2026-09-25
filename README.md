# VerifyChange

Know what to check before release.

A small Python application that prepares a prompt to generate manual release checks from a ticket and PR. It uses only the Python standard library and makes no AI API calls yet.

## Use

Save a ticket and PR description or diff as UTF-8 text files, then run:

```bash
PYTHONPATH=src python3 -m change_checklist ticket.txt pr.txt -o checklist-prompt.txt
```

Paste `checklist-prompt.txt` into your organization's approved AI tool. The prompt asks for concrete checks, expected results, missing context, and supporting evidence. See [change-checklist-prompt.md](change-checklist-prompt.md) for the prompt and a quick trial procedure.

For the next Innovation Day, this CLI can be extended to fetch ticket and PR data and call an approved AI model automatically.
