# Micro-Motion & Easing Rules

Motion quality is decided by three choices: easing direction, duration, and
the animated property. Get one wrong and the interface feels broken even when
it works.

## 1. Easing direction — the cardinal rule

Objects entering the screen are arriving; they must **decelerate**. Objects
leaving may accelerate away.

| Moment | Curve family | Examples |
|---|---|---|
| Enter (appear, expand, slide-in) | `ease-out` / decelerating | `ease-out`, `cubic-bezier(0.16, 1, 0.3, 1)`, `cubic-bezier(0.22, 1, 0.36, 1)` |
| Exit (dismiss, collapse, slide-out) | `ease-in` / accelerating | `ease-in`, `cubic-bezier(0.7, 0, 0.84, 0)` |
| Move (already visible, reposition) | `ease-in-out` / symmetric | `ease-in-out`, `cubic-bezier(0.65, 0, 0.35, 1)` |

- **Never `ease-in` on enter.** An entering element that starts slow reads as
  laggy or loading. This is the single most common agent mistake.
- Never `linear` for UI chrome — reserved for progress indicators, marquees,
  and continuously rotating spinners only.
- Bounce/elastic overshoot only where the direction calls for playfulness;
  never on dropdowns, modals, or other functional chrome.

## 2. Durations

- Micro-interactions (hover, press, toggle): **100-200 ms**.
- UI transitions (menu open, card expand, tab switch): **200-300 ms**.
- Large moves (page transition, hero entrance, sheet slide): **300-500 ms**,
  hard ceiling — past 500 ms motion reads as a performance bug.
- Stagger between sibling items: 20-50 ms, first item last.

## 3. Properties

- Animate `transform` (translate/scale/rotate) and `opacity` only — both are
  compositor-cheap.
- Never animate `width`, `height`, `top`, `left`, `margin`, `padding`,
  `box-shadow` (layout/paint thrash). Use `scale`/`translate`, or `clip-path`
  when a reveal genuinely needs geometry.
- `will-change` only on elements that actually animate; remove it after.
- Prefer CSS transitions over JS timers/intervals so every state stays
  interruptible and reversible mid-flight.

## 4. Springs (framer-motion / physics libraries)

- Default UI spring: `stiffness` 250-400, `damping` 25-35 — snappy, settles
  without visible oscillation.
- Raise damping (40+) to kill bounce on functional surfaces; lower stiffness
  (120-200) only for large, deliberate moves.
- A spring's job is feel, not ornament: if the library does not let you reason
  about settle time, fall back to a tuned `cubic-bezier`.

## 5. `prefers-reduced-motion` — mandatory

Every animation must respect the OS-level reduced-motion setting:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- Reduced motion means *reduced*, not frozen content: swap translate/scale
  motion for a quick `opacity` crossfade; never gate content visibility on an
  animation completing.
- JS-driven motion must check
  `window.matchMedia('(prefers-reduced-motion: reduce)').matches` and take the
  same fallback path.
- Never strip focus outlines inside the reduced-motion block.

## 6. Affordances

- No hover-only affordances: anything revealed on `hover` must also be
  reachable via `focus-visible` and touch. Hover is an enhancement layer, not
  the only path.
- Motion must not be the sole carrier of state (e.g. a pulsing error field
  still needs text/icon state).

## Checklist

- [ ] Every enter animation uses an ease-out / decelerating curve; zero
      `ease-in` or `linear` on enter.
- [ ] Exits may accelerate; in-place moves use symmetric curves.
- [ ] Durations inside budget: <=200 ms micro, <=300 ms UI, <=500 ms max.
- [ ] Only `transform`/`opacity` animated; no layout-property animation.
- [ ] `prefers-reduced-motion` handled in CSS and JS; content never gated on
      animation.
- [ ] No hover-only affordance; every hover path has a focus/tap equivalent.
