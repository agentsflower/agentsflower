---
name: frontend-art-direction
description: Anti-slop UI design system, modern aesthetics, typography scales, micro-motion easing rules, and accessible contrast guidelines. Use for any frontend or UI task — landing pages, dashboards, components, dark mode, animations, design reviews — to avoid generic "AI-slop" output, pick a deliberate visual direction, and ship WCAG 2.1 AA-compliant interfaces.
license: MIT
metadata:
  domain: 1
  source:
    - Leonxlnx/taste-skill@main
    - emilkowalski/design-eng@main
  license: MIT
  version: 1.0.0
---

# Frontend Art Direction (`frontend-art-direction`)

Use this skill whenever a task produces or reviews user-facing UI: pages,
components, layouts, color systems, or motion. Its job is to replace the
generic LLM default ("centered hero + three icon cards + soft gradient") with a
deliberate, verifiable design direction.

## Core rules (non-negotiable)

1. **Deal a direction first.** Before writing markup, name the visual
   direction (e.g. editorial, swiss-grid, brutalist, glass, retro-terminal) and
   derive palette, type, spacing and motion from it. "No direction" is not a
   direction.
2. **Separate surfaces with translucent shadows, not opaque borders.** A flat
   `1px solid` border is the default that makes everything look the same.
   Layer shadows and background tints instead.
3. **Typography comes from a scale, not from `font-size` guesses.** One display
   face, one text face, a fixed modular scale, and a strict weight hierarchy.
4. **Enter animations decelerate.** Only `ease-out`-family curves on enter;
   `ease-in` is reserved for exits. Motion honors `prefers-reduced-motion`.
5. **Contrast is measured, not eyeballed.** Text >= 4.5:1, large text and UI
   components >= 3:1 (WCAG 2.1 AA); every palette choice is tokenized and
   checkable.

## Load references on demand

| Reference | Load when |
|---|---|
| [references/anti-slop-guidelines.md](references/anti-slop-guidelines.md) | Choosing layout, visual direction, surfaces, or typography — before the first line of markup. |
| [references/micro-motion-easing.md](references/micro-motion-easing.md) | Writing or reviewing any transition, keyframe, or animation library call. |
| [references/design-tokens-wcag.md](references/design-tokens-wcag.md) | Defining colors, building a dark mode palette, or verifying contrast. |

## Definition of done (self-check before reporting)

- [ ] A named design direction is stated and the implementation follows it.
- [ ] Zero anti-slop items: no centered hero + icon-card row + soft gradient
      shipped as the whole design.
- [ ] Enter animations use ease-out / decelerating curves; zero `ease-in` or
      `linear` on enter.
- [ ] All motion respects `prefers-reduced-motion`; no hover-only affordances.
- [ ] Colors are semantic tokens; text >= 4.5:1, large text / UI >= 3:1.
- [ ] Verified in a real browser at 3 widths (e.g. 375 / 768 / 1440 px), not
      only in markup review.
