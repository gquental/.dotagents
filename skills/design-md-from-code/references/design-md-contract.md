# DESIGN.md contract

Use this contract for a design system extracted from code. Omit unsupported optional token groups. Do not fill gaps with framework defaults or tasteful guesses.

## Location and naming

Write `DESIGN.md` at the repository root unless the user or repository specifies another path. Use uppercase so the artifact reads as a repository contract beside files such as `AGENTS.md` and `CONTEXT.md`.

## Frontmatter

Start with YAML frontmatter. Quote strings and literal design values.

```yaml
---
name: "Product name"
version: 1
status: "extracted"
source_mode: "runtime-verified"
last_verified: "YYYY-MM-DD"
colors:
  canvas: "#FFFFFF"
  surface: "#F7F7F8"
  ink: "#171719"
  accent: "#5E6AD2"
typography:
  body:
    family: "Inter, sans-serif"
    size: "16px"
    weight: "400"
    line_height: "24px"
spacing:
  unit: "4px"
radii:
  control: "8px"
elevation:
  overlay: "0 16px 48px rgb(0 0 0 / 16%)"
motion:
  control: "150ms ease-out"
breakpoints:
  compact: "640px"
---
```

The required scalar keys are `name`, `version`, `status`, `source_mode`, and `last_verified`. `version` is `1`, `status` is `extracted`, and `source_mode` is one of the modes named in `SKILL.md`.

Keep popular DESIGN.md token groups at the top level so tools and agents can read them without a custom parser. Use semantic role names such as `canvas`, `ink-muted`, `accent`, and `error`. If the source already has canonical names, retain them and explain their roles in the body. For multiple themes, nest the theme variants under a clearly named `themes` group instead of merging values.

Do not promote a literal to frontmatter only because it occurs once. Do not add a full scale when the product defines only two values.

## Required sections

Use one H1 followed by these H2 sections in this order.

### System character

Name the default canvas, the main accent, its scarcity rule, density, and the concrete choices that distinguish the product. Avoid unsupported intent and broad labels such as "modern" or "premium."

### Foundations

Explain the canonical tokens and how the product uses them. Cover only the groups that exist:

- color roles and theme differences
- typography roles, metrics, fallbacks, and content measure
- spacing, shape, borders, and elevation
- motion and reduced-motion behavior
- iconography, illustration, photography, and data visualization

Use tables when several exact mappings need comparison. Reference frontmatter tokens as `{colors.canvas}` rather than duplicating raw values throughout the prose.

### Layout and responsive behavior

Document containers, grid or flow, gutters, content widths, breakpoints, and what changes at each width. A breakpoint list without behavioral changes is incomplete.

### Components and states

Describe shared component anatomy, variants, sizes, and interaction states. Prioritize navigation, controls, forms, cards or containers, overlays, and domain-specific components. Record visible focus, disabled, error, loading, empty, and selected behavior when present.

### Composition patterns

Describe how components combine into recurring page sections or product workflows. Name actual patterns such as a marketing hero, dense data table, editor layout, settings form, or mobile bottom navigation. Do not invent templates the product does not ship.

### Accessibility

Record observable and code-backed behavior such as focus indicators, keyboard states, target sizes, contrast checks, reduced motion, text alternatives, and non-color status cues. State what was tested. Put untested areas in Known gaps and drift.

### Rules

Write concise Do and Don't lists. Each rule must follow from canonical tokens, repeated usage, or a verified screen. Negative rules should name the specific wrong value or pattern when the evidence supports it.

### Evidence and confidence

Include a table with this shape:

```markdown
| Claim or token | Evidence | Confidence | Notes |
| --- | --- | --- | --- |
| `{colors.canvas}` | `src/styles/tokens.css:12`; `/dashboard`, 1440x900, light | high | Named token and rendered match |
```

Use repository-relative file paths with line numbers. For rendered evidence, record route or screen, viewport, theme, and state. Group closely related tokens when they share the same source, but do not use one citation to support unrelated claims.

### Known gaps and drift

List missing coverage and contradictions between intended and shipped design. Examples include an untested dark theme, a one-off radius, a component bypassing the token layer, or a font that failed to load. Separate facts from recommendations. Add recommendations only when the user requested an audit or redesign advice.

## Quality checks

- Exact values have evidence.
- Token names describe roles or preserve established source names.
- Light and dark values are not collapsed into one palette.
- Responsive rules describe behavior at each breakpoint.
- Components include real states, not only resting appearance.
- Accessibility claims say what was checked.
- Low-confidence observations stay out of canonical frontmatter.
- Known gaps name untested routes, states, themes, locales, and assets.
- The document contains no placeholder values or invented rationale.
