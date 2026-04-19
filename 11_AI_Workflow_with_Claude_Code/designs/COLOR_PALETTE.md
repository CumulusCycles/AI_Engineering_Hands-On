# ScriptSprout — Color palette (design specification)

**Prepared by:** Graphic design  
**For:** Engineering & implementation partners  
**Purpose:** Single source of truth for **color decisions** on screens supplied as **HTML mockup pages** in **`designs/mockup-pages/`**.  
**Note:** Hex values are **final design tokens** for implementation. Typography and spacing are shown in those HTML/CSS mockups; this document covers **color only**.

---

## 1. Brand primaries

These three colors anchor the product: **trust and depth** (navy), **growth and success** (green), **energy and emphasis** (gold).

| Token (design name) | Hex | Usage |
|---------------------|-----|--------|
| **Navy — primary** | `#2F3E57` | Primary headings, wordmark emphasis, default primary buttons, active nav “pill” background, key borders when a strong edge is needed. |
| **Green — secondary / success** | `#4CAF50` | Positive feedback, secondary accents, hover accents on navy controls, decorative accents in hero treatments, “success” inline states. |
| **Gold — highlight / attention** | `#F4C542` | Highlights, focus rings, hero glows, left accent bar on elevated panels, token-style callouts paired with dark fields (see §6). |

---

## 2. Neutrals and text

| Token | Hex | Usage |
|-------|-----|--------|
| **Page background** | `#FFFFFF` | Default canvas; cards and panels sit on white or very light tints. |
| **Body text** | `#4D6573` | Primary reading color (mix of navy with a cool slate — readable on white). |
| **Heading text** | `#2F3E57` | Same as navy primary for H1/H2 and strong titles. |
| **Muted / secondary copy** | `#5C6F82` | Supporting lines, italic subheads (slightly more navy than body for hierarchy). |
| **Subtle border** | `#D1D5DA` | Inputs, cards, tables — soft separation without heavy lines. |
| **Slate deep (data chrome)** | `#1E293B` | Admin-style dark tracks, “token” surfaces, bar chart backgrounds — **not** default body text. |
| **Slate mist (on dark)** | `#E2E8F0` | Secondary labels or counts placed **on** `#1E293B` surfaces. |

---

## 3. Page atmosphere (backgrounds)

The app should feel **bright and editorial**, not flat gray.

| Token | Hex / value | Usage |
|-------|-------------|--------|
| **App wash (vertical gradient)** | Top `#F8FBFF` → mid `#F3F6FB` → bottom `#F7F9FC` | Full-height background behind main content (subtle cool lift). |
| **Top bar glass** | ~`#FFFFFF` at **92%** over `#EEF3FB` (implement as translucent layer + blur if desired) | Sticky header strip; reads as frosted white with a hint of blue. |
| **Hero / marketing card base** | `#FFFFFF` with **soft radial glows**: gold at **~18%** opacity top-right, green at **~16%** opacity bottom-left | Hero panels and welcome-style cards — **spirit** of warmth + growth without heavy color blocks. |
| **Hero outer border** | Navy at **~14%** over white → approximately `#E8EBF0` | Thin outer frame on hero-style cards. |
| **Metric / admin card tint** | ~white **82%** mixed with `#EEF4FF` | Light KPI tiles on admin-style screens. |

---

## 4. Interactive states (buttons & links)

### Primary action (navy button)

| State | Background | Text / border | Notes |
|-------|--------------|----------------|-------|
| Default | `#2F3E57` | `#FFFFFF` | 8px corner radius; semibold label. |
| Hover | `#2F3E57` (keep) | **Green** `#4CAF50` for label; border shifts to green | Subtle lift shadow: `0 8px 16px -14px` with navy at **~50%** opacity. |
| Disabled | Navy **~40%** mixed with `#E2E8F0` | White text, reduced contrast | Opacity **~0.7**; not-allowed cursor. |

### Success / approve (bright green)

| Role | Hex |
|------|-----|
| Default | `#22C55E` |
| Hover / pressed | `#15803D` |
| Alternate solid (some flows) | `#15803D` default, hover `#166534` |
| Disabled fill | `#BBF7D0` |

### Regenerate / “warm action” (amber)

| State | Hex |
|-------|-----|
| Default | `#F59E42` |
| Hover | `#EA580C` |
| Disabled | Amber **~40%** over `#E2E8F0` (same treatment philosophy as navy disabled) |

### Links

| Element | Color |
|---------|--------|
| Default link | Navy `#2F3E57`, underline tinted with green **~45%** transparent |
| Hover link | Green `#4CAF50` |
| Focus visible | **2px** outline in **Gold** `#F4C542`, **3px** offset |

---

## 5. Semantic feedback

| Meaning | Color | Hex |
|---------|--------|-----|
| Success message | Green (secondary) | `#4CAF50` |
| Error message | Red | `#C62828` |
| Warning / caution | Use **Gold** or **Amber** from §4 — pick one per screen in **`mockup-pages/`** | `#F4C542` / `#F59E42` |

---

## 6. Component-specific notes (align with `mockup-pages/`)

| Component | Colors |
|-----------|--------|
| **Inline code** | Text navy `#2F3E57`; background **warm cream** from **~14%** gold on white → approximately `#FDF7E5`. |
| **Nav pills (inactive)** | Text `#2F3E57`; fill ~65% white / 35% `#EDF2FB`; border subtle `#D1D5DA`. |
| **Nav pills (active)** | Fill + border navy `#2F3E57`; text white. |
| **User pill** | Border: green **~40%** on `#DBE7D8`; fill: green **~12%** on white; text: navy-heavy mix toward `#334155`. |
| **Panel / card shadow** | Very soft navy shadow, e.g. `0 20px 36px -34px` at **~45%** navy opacity, plus 1px highlight feel. |
| **“Token display” row** | Background `#1E293B`, value text **Gold** `#F4C542`; adjacent **Copy** button `#4CAF50` hover `#43A047`. |
| **Bar chart** | Track `#1E293B`; fills use **Green** / **Gold** / **Navy** as shown per bar in the mockup HTML; count text `#E2E8F0`. |

---

## 7. Shadows & overlays (recipe, not a second palette)

Use **navy `#2F3E57`** at **low** alpha for elevation shadows (see button tables).  
Use **gold** and **green** at **low** alpha only in **radial** hero treatments — do not saturate large flat areas.

---

## 8. Accessibility guidance (design intent)

- Primary **body on white** pairing: `#4D6573` on `#FFFFFF` — design targets **WCAG AA** for normal text; if a variant fails in QA, darken body text slightly **toward navy** without changing brand primaries.
- **Gold on white** is for **accents and focus**, not long-form body copy.
- Primary **white on navy** buttons: maintain **AA** large-text contrast; keep button labels **short and bold**.

---

## 9. Do not (without new `mockup-pages/` comps)

- Do not introduce a second primary hue (e.g. purple/teal) for marketing chrome.  
- Do not use **true black** `#000000` for large UI areas — use **Slate deep** `#1E293B` only for compact data widgets.  
- Do not replace **success green** with **approve green** interchangeably on the same screen without a design note — they are **kin** but not identical; follow the mockup page for each control.

---

## 10. Revision

| Rev | Date | Notes |
|-----|------|--------|
| A | — | Initial palette handoff for ScriptSprout UI implementation. |
