---
name: frontend-design
description: Design and implement distinctive, production-ready frontend interfaces with responsive behavior, accessibility, visual hierarchy, and interaction polish. Use for new pages, components, dashboards, landing experiences, UI redesigns, design-system work, or requests to make an interface beautiful, memorable, or less generic.
---

# Frontend Design

## Preflight

1. Obey the root `AGENTS.md`, the user's scope, and repository-local conventions.
2. Inspect the existing design system, route chrome, controls, data flow, content, assets, breakpoints, and tests.
3. Preserve functional behavior, public routes, state semantics, and established brand decisions unless change is explicit.
4. Identify the audience, primary task, information hierarchy, content density, and constrained surfaces.
5. Read [visual-systems.md](references/visual-systems.md) before selecting or materially changing a visual system.

## Design Direction

1. Choose one coherent visual thesis and one restrained signature motif.
2. Define a bounded typography, color, spacing, radius, elevation, and motion system.
3. Use composition, scale, whitespace, and content-specific detail to create hierarchy.
4. Prefer decisive, context-appropriate choices over interchangeable template styling.
5. Ask only when missing brand or product direction would materially change the interface.

## Build Contract

- Implement complete responsive behavior rather than a static mockup.
- Cover loading, empty, error, success, disabled, focus, selection, and overflow states where applicable.
- Use semantic structure, correct labels, keyboard operation, visible focus, and non-color status cues.
- Meet WCAG AA contrast, support reduced motion, preserve zoom usability, and provide practical touch targets.
- Make layouts fluid across narrow phones, tablets, desktops, ultrawide screens, and short laptop heights.
- Keep motion causal and optional; prevent layout shift, clipping, accidental overflow, and focus loss.
- Reuse existing assets and dependencies first; add external assets or packages only with appropriate authority.
- Keep privileged, destructive, credentialed, deployment, and external mutations behind explicit approval.

## Anti-Generic Rules

- Apply the rules in [visual-systems.md](references/visual-systems.md); do not fight an established product language.
- Avoid generic gradients, gratuitous glass, card-everything grids, pill-everything controls, and empty oversized heroes.
- Avoid uniform centered sections, decorative scroll reveal, emoji icons, random font imports, and generic filler copy.
- Use at most one dominant decorative effect and make it reinforce the product's purpose.

## Quality Gates

1. Read and execute the applicable checks in [quality-gates.md](references/quality-gates.md).
2. Run the repository's existing lint, type, test, and build checks in risk-appropriate order.
3. Inspect the rendered interface at representative widths and short-height conditions when browser tooling is available.
4. Validate keyboard navigation, visible focus, reduced motion, state coverage, content stress, and contrast.
5. Claim only checks actually run; label browser, assistive-technology, device, or performance gaps.

## Output Contract

- Lead with the implemented result and name the changed surfaces.
- State the visual direction in one sentence, then report preserved behavior and validation evidence.
- Report only material accessibility, responsiveness, performance, or browser risks that remain.
- Omit generic praise, taste-process narration, and unsupported claims of polish or compliance.
