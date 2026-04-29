---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

## Issue tracker (local markdown)

Issues and PRDs for this repo live as markdown files in `.scratch/`.

Conventions:

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each file using the role strings below
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

When this skill says "publish to the issue tracker", create a new file under `.scratch/<feature-slug>/issues/` (creating the directory if needed). When this skill says "fetch the relevant ticket", read the file at the referenced path — the user will normally pass the path or the issue number directly.

## Triage labels

Five canonical triage roles, recorded on the `Status:` line:

| Role              | Meaning                                  |
| ----------------- | ---------------------------------------- |
| `needs-triage`    | Maintainer needs to evaluate this issue  |
| `needs-info`      | Waiting on reporter for more information |
| `ready-for-agent` | Fully specified, ready for an AFK agent  |
| `ready-for-human` | Requires human implementation            |
| `wontfix`         | Will not be actioned                     |

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number or path) as an argument, read the file at that path (or `.scratch/<feature-slug>/issues/<NN>-*.md`) and use its full body and any `## Comments` section.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues. Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

<vertical-slice-rules>
- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests)
- A completed slice is demoable or verifiable on its own
- Prefer many thin slices over few thick ones
</vertical-slice-rules>

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, write a new file at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first) so you can reference real issue numbers in the "Blocked by" field.

The slices were just approved by the user, so they bypass the `needs-triage` step. Set the `Status:` based on the slice type:

- AFK slice → `Status: ready-for-agent`
- HITL slice → `Status: ready-for-human`

The first lines of each file must be:

```
Status: <ready-for-agent | ready-for-human>

# <Issue Title>
```

Then use the body template below.

<issue-template>
## Parent

A reference to the parent PRD (e.g. `../PRD.md`) or parent issue file. Omit this section if there is no parent.

## What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Blocked by

- A reference to the blocking issue file (e.g. `01-schema-bootstrap.md`)

Or "None - can start immediately" if no blockers.

</issue-template>

Do NOT modify the parent PRD or any other parent issue.
