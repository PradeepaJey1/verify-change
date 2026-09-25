# AI change checklist

Use this prompt with a ticket and the corresponding pull request description or diff. The result is a draft checklist for a developer, tester, or product owner to review before release.

## Prompt

```text
You are helping a team decide what to verify before releasing a software change.

Read the ticket and PR information below. Produce a short, practical manual verification checklist focused on business behavior and edge cases. Use the ticket to understand intent and the PR to identify what actually changed.

Rules:
- Do not claim a scenario is covered by a test unless the input explicitly shows that test.
- Distinguish observed facts from assumptions. If important context is missing, ask a question instead of inventing a requirement.
- Prioritize scenarios a person can realistically check before release. Avoid generic items such as "test everything" or "check performance" without a concrete reason.
- Include the normal user path, failure or boundary paths, and any relevant permissions, data, or integration behavior.
- For each check, state the action and the expected result in plain language.
- Keep the main checklist to 5–10 items, ordered by risk.

Return exactly these sections:
1. Change summary: 2–3 sentences, with any uncertainty stated.
2. Manual checklist: numbered items with "Action" and "Expected result".
3. Questions to resolve: up to 3 questions that would materially change the checklist.
4. Evidence used: ticket or PR detail that led to each high-priority check. Say "not provided" where appropriate.

TICKET:
[Paste the ticket title, description, and acceptance criteria here]

PR:
[Paste the PR description, changed-file summary, and relevant diff here]
```

## Quick trial

1. Pick a completed, non-sensitive change that a teammate knows well.
2. Paste its ticket and PR into the prompt.
3. Ask the teammate to mark each checklist item as **useful**, **already covered**, or **irrelevant**, and note one important scenario it missed.
4. Save that feedback. It gives you a clear starting point for a future PR integration.

For a live demo, show the original ticket and PR alongside the generated checklist and the teammate's feedback.
