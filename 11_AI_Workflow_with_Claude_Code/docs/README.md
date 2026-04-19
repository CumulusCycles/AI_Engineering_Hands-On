# Documentation

Specifications and milestone slices for the product live under **`docs/`**. Use this file as the **map**. The **master trio** (business, functional, technical) sits in **`docs/reqs/`** at the top level of that folder; **MVP** and **post-MVP enhancement** pointers live in **`docs/reqs/mvp/`** and **`docs/reqs/enhancements/`**.

---

## Layout

| Path | Role |
|------|------|
| **`README.md`** | This file — how `docs/` is organized and what to read first. |
| **[`reqs/BUSINESS_REQS.md`](reqs/BUSINESS_REQS.md)** | Business requirements: vision, personas, scope, business rules. |
| **[`reqs/FUNCTIONAL_REQS.md`](reqs/FUNCTIONAL_REQS.md)** | Functional requirements: observable behavior, roles, journeys — **authoritative** for *what the system does*. |
| **[`reqs/TECHNICAL_REQS.md`](reqs/TECHNICAL_REQS.md)** | Technical requirements: stack, architecture, security, data and AI integration intent. |
| **[`reqs/mvp/`](reqs/mvp/)** | MVP milestone: which master sections apply first; pointers, not a second spec. |
| **[`reqs/enhancements/`](reqs/enhancements/)** | Post-MVP tracks (E1–E5): same pattern on top of MVP. |

**UI contract** (mockups, palette, brand): **[`../designs/README.md`](../designs/README.md)**.

---

## Reading order

1. **`reqs/`** (master trio) — `BUSINESS_REQS.md` → `FUNCTIONAL_REQS.md` → `TECHNICAL_REQS.md` (follow cross-links inside each file as needed).
2. **`reqs/mvp/`** — the three `MVP_*` files after the master trio, for the first shippable slice.
3. **`reqs/enhancements/`** — the three `ENHANCEMENTS_*` files after MVP, in the order described there.

If anything in **`reqs/mvp/`** or **`reqs/enhancements/`** disagrees with the master **`reqs/*_REQS.md`** files at the root of **`reqs/`**, the **master trio wins**.

---

## Revision

| Version | Notes |
|---------|--------|
| 1.0 | Baseline map: **`docs/README.md`**, **`reqs/`** master trio, **`reqs/mvp/`**, **`reqs/enhancements/`**. |
