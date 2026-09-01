---
name: design-md-from-code
description: Create or update a repository-root DESIGN.md by extracting the shipped design system from frontend source code and, when runnable, representative rendered screens. Use for requests to document, reverse-engineer, audit, or refresh a product's visual system from a codebase. Do not use for greenfield visual direction or URL- or screenshot-only brand extraction.
---

# DESIGN.md from code

Produce an evidence-backed design contract that another coding agent can use without seeing the original UI. Document the product that exists. Do not quietly redesign it.

## Boundary

- The default deliverable is `DESIGN.md` at the repository root. Respect a user-specified path or an established project convention.
- Read an existing `DESIGN.md` before changing it. Preserve valid decisions, names, and scope unless current evidence disproves them.
- This workflow authorizes documentation changes only. Do not refactor styles, normalize tokens, or alter UI code unless the user asks.
- Use this skill for a codebase. For a public URL or screenshots without source code, use a URL- or brand-extraction workflow instead. For a new visual direction, use a design exploration workflow.

## Evidence model

Treat these sources differently:

1. Named tokens, theme files, design-system packages, and documented component variants describe intended design.
2. Rendered screens and computed styles describe shipped design.
3. Repeated component usage describes convention.
4. One-off literals describe exceptions until stronger evidence says otherwise.

Do not average conflicts or rename established tokens to make the system look cleaner. Record intended and shipped values separately under drift. Keep proposed improvements out of canonical tokens unless the user asked for a proposal.

Confidence has three levels:

- `high`: a named source token or component contract, confirmed by repeated use or a rendered screen
- `medium`: repeated source usage or a rendered value without a named contract
- `low`: one occurrence, an incomplete screen sample, or interpretation

Only high- and medium-confidence values belong in frontmatter. Put low-confidence observations in Known gaps and drift.

## Workflow

### 1. Set scope

Find the repository root and read its instructions, existing design documents, manifests, route definitions, theme files, global styles, shared components, and component-library configuration. State which product surfaces, themes, locales, states, and viewport classes are in scope.

Run the evidence scanner from this skill directory:

```bash
python3 <skill-directory>/scripts/scan_design_evidence.py --root <repository-root> --output <temporary-evidence.json>
```

Use the report as an index, not as the final interpretation. Inspect the high-signal files and representative component implementations yourself. Do not scan generated dependencies or treat framework defaults as product decisions unless the product uses them unchanged.

### 2. Check the real UI when feasible

Use the project's existing start or preview command when dependencies are available. Do not change lockfiles or product code just to make the audit run. If the app cannot run, continue in `source-only` mode and state why.

In a browser-capable runtime, inspect representative routes at a narrow mobile width and a desktop width. Cover every supported theme and the states that materially change styling, such as focus, hover, selected, disabled, error, empty, loading, and overlay states. Wait for fonts and lazy media before judging the screen. Record route, viewport, theme, state, and visible result.

Use one of these exact source modes in the output:

- `source-only`: source files were inspected, but no rendered pixels were checked
- `code-and-screenshots`: source files and static screenshots or design exports were inspected, but the app was not executed and interacted with
- `runtime-verified`: the app was executed and representative routes, viewports, themes, or states were checked in a browser

### 3. Reconcile the system

Preserve existing token names when they are coherent. Add semantic aliases only when they clarify use without hiding the canonical name. Separate themes and product surfaces when they differ. Describe responsive behavior, component anatomy, variants, states, motion, iconography, and image treatment only where evidence exists.

Every exact color, type metric, spacing value, radius, shadow, duration, easing, breakpoint, or component rule needs a file-and-line citation, a rendered-screen citation, or both. Never infer accessibility conformance from visual appearance alone.

### 4. Write the contract

Read [references/design-md-contract.md](references/design-md-contract.md) before authoring. Follow its frontmatter and section contract. Keep prose short and specific. State the canvas, the main accent and its scarcity rule, the dominant type behavior, and the layout behavior without generic adjectives.

### 5. Verify

Run:

```bash
python3 <skill-directory>/scripts/validate_design_md.py <repository-root>/DESIGN.md
```

Then spot-check each canonical token against its cited source. If runtime verification was possible, compare the document against the captured routes and viewports. Report the output path, source mode, surfaces checked, and remaining gaps. Do not claim full coverage when routes, themes, states, locales, or assets were not exercised.
