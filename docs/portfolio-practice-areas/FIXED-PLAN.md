# Portfolio Practice Areas: Fixed Plan

## Decision

Evolve the portfolio homepage from a broad positioning page into a concise portfolio navigator. The homepage will make four areas of practice legible while preserving one evidence-led featured case study.

The four practice areas are:

1. **Remote Sensing**
2. **Cartography**
3. **AI Automations**
4. **3D GIS Visualization**

This is a portfolio structure, not a claim that every area already contains a public project.

## Positioning

The portfolio continues to position Ibanun Mangun Kusumo at the intersection of geospatial intelligence, AI and automation, and dependable operational systems.

`3D GIS Visualization` means processing and communicating spatial data in three dimensions. Its scope includes terrain, built environments, point clouds, 3D spatial processing, landscape or city scenes, and interactive 3D map outputs. It does not position the portfolio as general-purpose 3D art or character modelling.

## Information Architecture

### Homepage

The homepage remains the primary entry point and will contain:

- A direct navigation item named `Work` that lands on the practice-area section.
- A featured-work CTA for the existing Karhutla Signal Review case study.
- An `Areas of practice` section using four content-led lanes rather than a generic card grid.
- A concise description for each practice area.
- A visible evidence marker only where a public project exists.

### Present public route

- **Remote Sensing**
  - Featured work: [Karhutla Signal Review](../../karhutla-review/)
  - Public route: `/karhutla-review/`

### Future routes, only when evidence exists

Do not ship routes or navigation links for these areas until each has a real public artifact:

- `/cartography/`
- `/ai-automations/`
- `/3d-gis-visualization/`

Until then, the areas are plainly presented as practice areas, not as clickable portfolio pages or completed case studies.

## Homepage Content Plan

### Navigation

Replace the current `Focus` navigation label with `Work`, pointing to the practice-area section. Keep `Approach` and LinkedIn because both destinations already exist.

### Featured work

Keep the hero CTA specific:

- `View Karhutla Signal Review`

It remains the primary action because it leads to the first live, evidence-led public case study.

### Areas of practice section

Rename the current section to `Areas of practice`.

Use four vertically structured lanes, with no icon set and no invented metrics:

1. **Remote Sensing**
   - Satellite imagery, thermal-signal review, raster analysis, and reproducible detection workflows.
   - Link only the verified case study: `Karhutla Signal Review, Central Kalimantan`.

2. **Cartography**
   - Thematic maps, interactive web mapping, spatial communication, and decision-oriented map design.
   - No case-study link until a public artifact exists.

3. **AI Automations**
   - Python workflows, agent-assisted processes, review boundaries, and automation that reduces operational friction.
   - No case-study link until a public artifact exists.

4. **3D GIS Visualization**
   - 3D spatial data processing, terrain and built-environment visualization, point-cloud workflows, and interpretable 3D geospatial scenes.
   - No case-study link until a public artifact exists.

## Visual Direction

The existing dark, technical field-workbench language remains. It is suitable because the portfolio is evidence-led and includes data-rich geospatial work, not because dark mode is generically "tech".

- **ENERGY 2**: restrained, confident, and evidence-first.
- **RHYTHM 3**: the hero, practice lanes, approach, and contact each use distinct compositions.
- **MOTION 1**: hover/focus feedback only. No decorative scrolling or looping animation.

Major design decisions:

- **Four lanes, not feature cards:** the areas are domains of practice, not equivalent app features. Lanes make the hierarchy clear and leave room for real evidence links.
- **Lime accent reserved for action and focus:** it continues to direct attention to the featured case study and keyboard focus without turning every category into a CTA.
- **No category icons:** each label is more specific and honest than a generic icon family.
- **No inactive links:** an area without a public artifact is informative text, not a false navigation destination.
- **Featured work remains singular:** one verified map case study is more credible than a fabricated four-project grid.

## Accessibility and Interaction Requirements

- Every navigation item and case-study link must have a real destination.
- The single case-study link in the Remote Sensing lane must be a native anchor.
- Non-linked practice areas must not look or behave like controls.
- All interactive elements retain visible keyboard focus, pointer affordance, and a minimum 44px touch target where applicable.
- Validate desktop and mobile for horizontal overflow and link behavior.
- Keep no em dashes in new UI copy.

## Implementation Sequence

1. Create a feature branch from current `main`.
2. Update homepage copy, navigation, and the practice-area section.
3. Add the single verified Remote Sensing link to Karhutla Signal Review.
4. Do not create future category routes or placeholder links.
5. Run HTML parsing, link/copy checks, whitespace checks, and browser verification on desktop and mobile.
6. Run the anti-slop Delivery Gate with recorded evidence.
7. Commit on the feature branch, push, open a PR, wait for CI, and merge only with explicit approval.
8. Verify the deployed homepage after GitHub Pages completes.

## Acceptance Criteria

- Homepage shows all four practice areas by their exact names.
- `Work` navigation reaches the practice-area section.
- `Remote Sensing` exposes the live Karhutla Signal Review as the only linked public artifact.
- Cartography, AI Automations, and 3D GIS Visualization are present but have no fake or dead links.
- Hero CTA still opens `/karhutla-review/`.
- The homepage has no email placeholder, generic CTA, fabricated metric, fabricated project, or em dash introduced by this work.
- All homepage controls are keyboard-accessible and work on mobile without horizontal overflow.
