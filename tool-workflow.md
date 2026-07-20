# Tool Workflow

How AI-assisted development is organized for this project.

## Tools

| Tool | Role |
|------|------|
| Cursor | Primary IDE with AI agent; rules in `.cursor/rules/` |
| Git | Version control; feature branches recommended |
| Pytest / Vitest | Automated verification gates |

## Session Workflow

1. **Plan** — Update requirements, acceptance criteria, implementation plan (`ai-prompts/planning.md`)
2. **Design** — Refine API contract, data model, UI flows (`ai-prompts/design.md`)
3. **Implement** — Code per milestone (`ai-prompts/implementation.md`)
4. **Test** — Run suites; record in `test-results.md` (`ai-prompts/testing.md`)
5. **Debug** — Log issues in `debugging-notes.md` (`ai-prompts/debugging.md`)
6. **Review** — Self-review via `code-review-notes.md` (`ai-prompts/code-review.md`)
7. **Document** — PR description, reflection, AI usage summary

## Prompt History

Each significant AI session should be logged using the template in:

`artifacts/prompt-history/TEMPLATE.md`

## Cursor-Specific

See `tool-specific/cursor-workflow/README.md` for branch naming, rules, and agent conventions.

## Quality Gates

Before marking a milestone complete:

- [ ] Tests pass (`pytest`, `npm test`)
- [ ] Lint/typecheck clean where configured
- [ ] Planning docs updated if behavior changed
- [ ] Prompt history entry added
