# Frontend Quality Gates

## Preserve Behavior

- Verify every existing route, control, link, form, keyboard action, and data transition affected by the change.
- Cover loading, empty, error, success, disabled, selected, focused, stale, and overflow states where relevant.
- Confirm destructive actions retain confirmation and recovery behavior.
- Confirm asynchronous actions prevent duplicate submission and expose progress and failure.
- Test long content, missing content, malformed values, and realistic data density.

## Validate Responsive Layout

- Inspect at 320 and 375 pixel phone widths.
- Inspect near 768 pixels for tablet and small-window behavior.
- Inspect at 1280 and 1440 pixel desktop widths.
- Inspect one ultrawide condition for runaway line lengths and detached controls.
- Inspect a short laptop viewport near 700 to 800 pixels high.
- Verify navigation, dialogs, sticky regions, tables, charts, and forms at each applicable size.
- Prevent horizontal page scrolling unless the component explicitly requires a contained scroller.
- Keep primary actions reachable without hiding essential content behind viewport assumptions.
- Preserve readable line lengths, stable alignment, and useful density as space changes.

## Validate Accessibility

- Use semantic landmarks, headings, lists, buttons, links, tables, and form controls.
- Preserve a logical heading outline and DOM reading order.
- Provide accessible names, instructions, error associations, and status announcements.
- Make all actions operable by keyboard without traps.
- Keep focus visible, ordered, restored after overlays, and moved intentionally when context changes.
- Meet WCAG AA contrast for text, controls, focus indicators, and meaningful graphics.
- Avoid color-only distinctions and pair status color with text, shape, icon, or pattern.
- Provide text alternatives for meaningful media and ignore purely decorative media appropriately.
- Respect reduced motion, forced colors, text resizing, and browser zoom.
- Use practical pointer targets and spacing without making compact desktop tools inefficient.
- Avoid hover-only disclosure for required information or actions.
- Check disabled states without removing necessary explanation.

## Validate Visual Integrity

- Compare spacing, typography, color, radius, icon, and elevation use against the selected token system.
- Check baseline alignment, optical balance, truncation, wrapping, clipping, and stacking contexts.
- Verify dialogs, menus, tooltips, and popovers remain on-screen and layer correctly.
- Confirm empty and error states retain the same visual hierarchy as populated states.
- Confirm dark and light variants independently when both are supported.
- Remove decorative elements that resemble controls or compete with state indicators.

## Validate Performance

- Run existing lint, type, unit, integration, and production-build checks.
- Avoid adding dependencies for behavior achievable with the existing stack.
- Reserve image and media dimensions to prevent layout shift.
- Optimize asset formats and sizes; defer noncritical media without delaying primary content.
- Avoid repeated layout measurement, unbounded listeners, excessive observers, and animation-driven reflow.
- Keep expensive rendering proportional to visible content and expected data scale.
- Record measurements only when tooling actually produced them.

## Collect Evidence

- Capture representative screenshots when browser tooling is available.
- Exercise keyboard navigation and reduced-motion behavior directly.
- Use existing accessibility automation when configured; do not install or claim a scanner silently.
- Report commands run, viewports inspected, states exercised, and failures observed.
- Label checks requiring real devices, assistive technology, authenticated data, or production scale.
- Never claim pixel perfection, full accessibility, cross-browser parity, or performance compliance without evidence.
