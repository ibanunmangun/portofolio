# Design Read — Karhutla Signal Review

**Audience:** Technical recruiters and GIS practitioners reviewing Ibanun Mangun Kusumo's public portfolio.

**Page job:** Let a visitor inspect the distinction between satellite thermal signals, derived review clusters, and confirmed operational events. The page must not imply operational authority.

**Design Read:** A focused technical case-study map for portfolio reviewers, using a field-notebook visual language. **ENERGY 2 / RHYTHM 3 / MOTION 1.**

## Decision log

- **Dark ground:** Continues the established portfolio identity and provides high contrast for thin administrative boundaries and signal markers. This is a fixed portfolio theme, not a generic "tech" default.
- **Amber signal accent:** Used only for thermal signals and derived review clusters, so it denotes data focus rather than decorative emphasis.
- **Lime focus accent:** Reserved for keyboard focus and navigational feedback, making accessibility state distinct from geographic signal meaning.
- **Editorial serif headings with plain system UI body:** Headings establish the case-study voice; body and controls prioritize compact map-reading clarity and avoid a generic developer-tool type system.
- **Three-part workspace:** Controls, map, and selected-unit detail follow the actual review task. The map is the focal point, not a card grid or a dashboard metric row.
- **No decorative grid, icons, badge, glow, hero image, or animation:** None improves the review task. The administrative boundary and signal geometry provide the page-specific visual structure.
- **Static snapshot assets:** The page reads local derived GeoJSON and never calls FIRMS in the browser. This keeps the API key out of the published artifact and makes the demonstrator reproducible.
- **Motion 1:** Map pan and native control feedback support user actions. No automatic motion runs.
