# Repository operating instructions

## Permanent FIO / FreedomHub reporting rules — 2026-10-08

1. Record every meaningful development task in `DEV_LOG.md` and the existing `changelog.md` or `CHANGELOG.md`; commit the records with the work.
2. Completed-work entries must include date, work performed, changed files/systems, verification results, deployment status, and relevant commit or PR.
3. Name the actual implementer using `**Agent:** Adaptive`, `Hub Agent`, `ChatGPT`, `Claude`, or `Grok`; record the model separately when known. Adaptive work uses the exact line `**Agent:** Adaptive`.
4. Never infer implementing agent from commit author, repository owner, or AI-platform references. Mark unknown attribution as not recorded.
5. Never claim completion or deployment without evidence. Distinguish source/local completion, staging verification, and production verification.
6. Check FreedomHub's activity-source registry in `caseystubbs/Freedom-Hub/projects.json`. Flag unregistered repositories or incorrect source paths; do not invent configuration, deployments, or roadmap tasks.
7. The Roadmap task board owns planned tasks and statuses. Changelogs are evidence, not automatic task transitions. Reference matching existing tasks and verified progress; never automatically close unrelated tasks.
8. Preserve implementation decisions, discovered problems, lessons learned, and unfinished work for subsequent agents.
9. Audit existing records before backfilling. Backfill only verifiable missing work, label retrospective records, cite evidence, and never count one deliverable repeatedly.
10. Durable memory records decisions and verified facts; it is not proof that an unverified action succeeded.

Preserve all trading safety and approval requirements. Reporting does not authorize orders, changing automation/risk settings, deployment, or unrelated changes.

## Email sending rule — 2026-10-27

Directed by Casey on October 27, 2026. Applies to every agent and session.

- Never send email from Casey's personal Gmail (caseystubbs@gmail.com) unless Casey explicitly tells you to send that specific message. This covers sending, replying and forwarding through the Gmail connector.
- Otherwise, create a Gmail draft and tell Casey it is waiting for Casey's review.
- A request to "send" or "email" someone does not by itself authorize the personal Gmail account. If Casey has not named the sending account, draft and ask.
