# Design Tokens & WCAG Contrast

Colors are data. Hardcoding hex values inside components is how palettes rot
and how contrast bugs ship. Define tokens once, reference them everywhere, and
verify contrast numerically.

## 1. Token architecture

Three tiers, in order of abstraction:

1. **Primitive palette** — raw hues: `--blue-500`, `--neutral-900`, etc.
   Components never reference these directly.
2. **Semantic tokens** — meaning, not color:
   `--color-surface-1..3`, `--color-text-primary`, `--color-text-secondary`,
   `--color-text-muted`, `--color-accent`, `--color-border-subtle`,
   `--color-focus-ring`, `--color-danger`, `--color-success`.
3. **Component tokens** (optional) — `--button-bg`, `--card-surface` mapping to
   semantic tokens.

Rule: components consume semantic tokens only. A hex value inside a component
file is a defect.

```css
:root {
  --color-surface-1: #ffffff;
  --color-surface-2: #f6f7f8;
  --color-text-primary: #16181d;
  --color-text-secondary: #4b5563;
  --color-accent: #355cff;
  --color-border-subtle: rgb(0 0 0 / 0.08);
}
```

## 2. Dark mode palettes

- Implement dark mode by re-defining the **same semantic tokens** under a
  `[data-theme="dark"]` / `.dark` scope or `prefers-color-scheme` query —
  never by inverting at the component level.
- Elevation in dark mode is luminance, not borders: `--surface-1` darkest,
  each level slightly lighter (`#0b0d10` → `#12151a` → `#181c22`-range).
- Avoid pure `#000` surfaces and pure `#fff` text: near-black surfaces and
  90-95% white text read better and keep OLED smear and halation down.
- Desaturate accents ~10-20% in dark mode; saturated brand hues vibrate on
  dark surfaces.
- Translucent borders replace opaque ones:
  `rgb(255 255 255 / 0.08-0.12)` is the dark-mode equivalent of a hairline.

## 3. WCAG 2.1 contrast requirements

| Element | AA minimum | AAA target |
|---|---|---|
| Normal text (< 24 px, or < 18.66 px bold) | **4.5:1** | 7:1 |
| Large text (>= 24 px, or >= 18.66 px bold) | **3:1** | 4.5:1 |
| UI components & graphical objects (control boundaries that convey state, icons, charts) | **3:1** | — |
| Focus indicator vs. adjacent color | **3:1** | — |

Applies to: text on surfaces, placeholder text, disabled-but-meaningful
controls, icon-only buttons, chart legends. Exempt: purely decorative
elements, logos, genuinely disabled controls.

## 4. Applying it

- Pick token *pairs*, not lone colors: every `--color-text-*` is paired and
  measured against every `--color-surface-*` it can render on, in both themes.
- `:focus-visible` must produce a visible indicator at >= 3:1 contrast against
  the adjacent background; never `outline: none` without a replacement.
- State layers: hover/active tints applied via `color-mix()` or translucent
  overlays must not drop the text ratio below 4.5:1 — re-measure the worst
  case, not the resting state.
- Measure with a contrast checker (browser DevTools, `wcag-contrast` tooling,
  or the APCA/ WCAG 2 formula) — do not eyeball. Record the worst pair in the
  change description.

## Checklist

- [ ] All component colors resolve through semantic tokens; zero hardcoded
      hex in components.
- [ ] Light and dark palettes defined on the same token names; dark elevation
      via luminance steps, not borders.
- [ ] Normal text >= 4.5:1, large text >= 3:1, UI components / focus
      indicators >= 3:1 — measured, in both themes.
- [ ] `focus-visible` visible and >= 3:1 vs. adjacent colors.
- [ ] No pure `#000`/`#fff` extremes in dark palettes; accents desaturated.
