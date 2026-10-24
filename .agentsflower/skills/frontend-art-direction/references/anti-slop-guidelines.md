# Anti-Slop Guidelines

"AI slop" is the category-average layout a model emits when it picks no
direction: a centered hero, a row of three icon cards, a soft purple-blue
gradient, and a mono caption. It is technically correct and instantly
forgettable. These rules exist to fail that output on sight.

## 1. The banned default

Never ship this as the entire design of a page or section:

- A perfectly centered hero (centered headline + centered subtext + two
  centered buttons), followed by
- a symmetric row of exactly three icon cards, over
- a generic soft gradient background (typically indigo-to-purple or
  blue-to-cyan), captioned in
- a small mono/uppercase "eyebrow" label.

One of these elements alone is fine; all four together as the whole
composition is the slop signature. If the page is recognizable as the default,
pick again.

## 2. Deal a direction first

Before markup, choose and name a direction. Examples that force real
decisions: editorial magazine (serif display, ruled lines, asymmetric grid),
swiss/international (grotesque type, strict grid, flat color blocks),
brutalist (raw borders, oversized type, hard shadows), glass (translucent
layers, backdrop blur, real depth), retro-terminal (mono type, scanline
accents, phosphor palette).

Rules of engagement:

- The direction decides the palette, the type scale, the spacing rhythm, and
  the motion language — write those tokens down before components.
- At least one composition choice must break the default: an off-center hero,
  a left-rail layout, a sticky asymmetric split, a horizontal scroll section,
  oversized type as the visual itself.
- Do not mix directions; one page = one direction, applied ruthlessly.

## 3. Surfaces: translucent shadows, not opaque borders

Opaque `1px solid` borders around every box are the other slop tell. Separate
surfaces by depth:

- Light mode: replace `border: 1px solid #e5e7eb` with a layered translucent
  shadow, e.g.
  `box-shadow: 0 1px 2px rgb(0 0 0 / 0.05), 0 8px 24px rgb(0 0 0 / 0.08);`
  plus a 1-2% background tint between levels.
- Dark mode: never add borders to show elevation. Raise the surface
  luminance per level (`--surface-1` < `--surface-2` < `--surface-3`) and add
  a soft shadow; reserve borders for actual strokes (inputs, dividers).
- If a border is genuinely needed (input fields, table rules), use a
  translucent border color (`rgb(255 255 255 / 0.08)` on dark,
  `rgb(0 0 0 / 0.08)` on light), not an opaque gray.

## 4. Strict typography hierarchy

- Build from one modular scale — e.g. ratio 1.25:
  `12 / 14 / 16 / 20 / 25 / 31 / 39 / 49 / 61 px`. Every font-size on the page
  must be a scale step; no arbitrary `17px`/`19px` one-offs.
- One display face maximum (a serif or a characterful grotesque) + one text
  face (neutral sans or mono for data). Two families total, including the UI.
- Hierarchy is carried by size and weight contrast (e.g. 400 vs 700), not by
  color spam: keep body text to 2-3 tints of one neutral.
- Line-height: 1.05-1.2 for display sizes, 1.4-1.5 for headings, 1.5-1.7 for
  body. Line length (measure) for paragraphs: 60-75 characters.
- Letter-spacing: only tighten large display text (`-0.02em`); never letterspace
  body text, and reserve `text-transform: uppercase` tracking (+0.05-0.12em)
  for small labels only.

## 5. Other slop tells to reject

- Inter + gray everything as the entire identity with no accent decision.
- Emoji or stock glyph icons as bullet substitutes in feature lists.
- Rainbow/violet gradient text on headlines as the only "design".
- Equal padding and equal-width columns everywhere; perfect symmetry with no
  focal point.
- Rounded-2xl + shadow-xl on every element (the "Tailwind default" look).
- Copy that says nothing: "Lorem ipsum"-level placeholders shipped as final
  text, or marketing filler ("seamless", "cutting-edge") with no specifics.

## Checklist

- [ ] Design direction named; palette/type/spacing/motion tokens derive from it.
- [ ] The page is not "centered hero + 3 icon cards + soft gradient" as its
      whole design.
- [ ] At least one deliberate non-default composition choice exists.
- [ ] Surfaces separated by translucent shadows / tints; opaque gray borders
      only where a stroke is semantically required.
- [ ] All font sizes land on one named scale; <= 2 font families.
- [ ] No emoji-as-icon bullets, no gradient-text headline as sole identity.
