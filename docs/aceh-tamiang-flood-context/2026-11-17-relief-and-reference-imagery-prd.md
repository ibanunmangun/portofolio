# PRD: Relief and Reference Imagery Context

## Approval state

Approved for implementation by Nulla on 17 November 2026.

This enhancement changes map context only. It does not change the evidence layer, report snapshot, five report-named subdistricts, or the evidence boundaries of Aceh Tamiang Flood Context Review.

## Context

The current map intentionally shows a report-named administrative footprint over muted administrative context. It is accurate but visually sparse. This enhancement adds terrain context and an optional satellite reference layer while preserving the report footprint as the visual figure.

## Cartographic design read

Reading this as: a thematic cartographic review for portfolio readers, answering how report-named subdistricts sit within terrain context, with the 16 November 2026 report footprint as figure and terrain plus imagery as ground.

- ENERGY 2: restrained and evidence-first.
- RHYTHM 3: map workspace remains the focal composition; supporting method and provenance sections explain the visual boundary.
- MOTION 1: toggle and focus feedback only.

## Objective

Add a local, reproducible terrain-relief snapshot and a user-controlled satellite imagery reference layer to improve orientation without implying physical flood extent, event-date inundation, severity, or response priority.

## Evidence boundary

### Primary evidence, unchanged

The highlighted polygons remain the only evidence layer. They represent the five Aceh Tamiang subdistricts named in the report snapshot dated 16 November 2026:

- Bendahara
- Karang Baru
- Kejuruan Muda
- Kota Kuala Simpang
- Rantau

### Reference context

- **Terrain relief:** a local hillshade derived from a Copernicus DEM GLO-30 snapshot, used to provide terrain orientation only.
- **Satellite imagery:** an optional NASA GIBS fixed-date visualization, used for reference orientation only.
- **Administrative boundaries:** existing HDX COD-AB 2020 ADM3 context geometry.

None of these reference layers establish flood extent, water depth, damage, cause, response priority, or current conditions.

## Scope

### In scope

- Build a hillshade raster derived from Copernicus WorldDEM-30 GLO-30 with a 15 km context buffer around Aceh Tamiang.
- Package the rendered hillshade as a local, static web-map overlay with source, processing, checksum, and attribution metadata.
- Use muted green-gray styling with multidirectional hillshade as the selected terrain treatment.
- Add an optional NASA GIBS satellite imagery layer fixed to 16 November 2026 and disabled by default.
- Add controls, legend entries, source and attribution behavior, metadata, CI validation, and browser regression checks for these layers.
- Update the case-study method and limitation text to describe the layers as reference context.

### Out of scope

- Generating a flood extent from DEM, imagery, or any other source.
- Hydrologic modelling, watershed delineation, slope risk, water depth, terrain classification, or drainage analysis.
- Live imagery, latest imagery, user-adjustable imagery dates, or browser-side source-data queries requiring credentials.
- Satellite imagery caching, downloading, redistribution, or image classification.
- Changes to the report-named footprint data, its five named areas, or its dated-report interpretation.
- 3D terrain view, vertical exaggeration, fly-through, or viewshed analysis.

## Data decisions

### Terrain source

Use Copernicus WorldDEM-30 GLO-30 if a reproducible public-access route can retrieve the Aceh Tamiang region at implementation time. The source is a Digital Surface Model, not a bare-earth flood model.

Required public attribution for a modified derivative:

> Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.

Fallback: SRTM 1 Arc-Second Global, approximately 30 m, only if Copernicus GLO-30 retrieval cannot be completed through a reproducible, permitted path. The final PRD and metadata must name the selected source; no silent fallback is allowed.

### Hillshade processing

- Region: Aceh Tamiang administrative extent plus 15 km buffer.
- Method: multidirectional hillshade.
- Rendering: muted green-gray, low contrast, with no elevation color ramp that could imply hazard intensity.
- Output: local browser-friendly image overlay plus deterministic bounds metadata and SHA-256 checksum.
- Layer role: reference terrain context.

The hillshade must remain visibly subordinate to report footprint polygons at default, selected, desktop, tablet, and mobile views.

### Satellite imagery

Use NASA GIBS through its public, standards-based tile service only after confirming the selected fixed-date product is available at 16 November 2026 and works in Leaflet's Web Mercator view.

- Default state: off.
- Fixed date: 16 November 2026.
- Label: `Reference satellite imagery, 16 Nov 2026`.
- Required map note: `Reference imagery, not event-date flood evidence.`
- Required acknowledgement: `We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS).`
- GIBS attribution must become visible when the layer is active.

If a suitable fixed-date product cannot be verified, do not substitute latest imagery. Retain relief-only context and document the blocker.

## Layer stack

From background to foreground:

1. Dark map ground.
2. Local muted green-gray hillshade, always visible.
3. Optional fixed-date NASA GIBS imagery, default off.
4. HDX administrative context polygons and boundaries.
5. Report-named administrative footprint, warm fill and light outline.
6. Selection state and keyboard focus.
7. Map controls, legend, evidence limitation, layer attribution, and source links.

## Legend and controls

Legend groups by role:

```text
Evidence
- Named in 16 Nov report

Reference context
- Administrative boundary
- Terrain relief
- Satellite imagery, optional
```

Controls:

- Terrain relief stays on and is not a user toggle.
- Satellite imagery is a native checkbox, off by default.
- Reset returns to the full context extent. It does not change the imagery toggle state.
- Satellite imagery control, attribution, and limitation remain keyboard-accessible and mobile-safe.

## Validation requirements

### Asset and metadata checks

- Validate local hillshade image exists, has documented pixel dimensions, byte size, geographic bounds, processing method, source URL, source version, attribution, and SHA-256 checksum.
- Validate hillshade bounds include the Aceh Tamiang context extent and do not exceed the documented 15 km buffer by an unexplained amount.
- Validate the evidence footprint remains exactly the five report-named subdistricts.
- Validate imagery product ID, fixed date, tile endpoint, acknowledgement string, default-off UI copy, and reference-only limitation text.
- Scan published local assets for secrets.

### Browser checks

- Hillshade renders as local context at page load without a network tile dependency.
- Evidence footprint remains visually primary over hillshade.
- Satellite imagery is absent at load, appears after toggle, and disappears after toggle off.
- Satellite acknowledgement is visible only when imagery is active.
- List selection, polygon selection, reset, error, empty, loading, keyboard focus, desktop, tablet, and mobile remain functional.
- No horizontal overflow or clipped controls.

### Cartographic review

- Check figure-ground with hillshade only and with imagery active.
- Check legend symbol fidelity and evidence/reference grouping.
- Check screenshot at default extent and selected area for hierarchy, contrast, and balance.
- Check grayscale or color-vision-safe distinction between report footprint and reference layers.

## Rollout

1. Verify source access, attribution, terms, product/date availability, and technical compatibility.
2. Build the local hillshade and metadata in a deterministic pipeline.
3. Add imagery only after a fixed-date NASA GIBS product works in a local browser.
4. Implement controls and visual hierarchy.
5. Extend validators and CI.
6. Run independent review and anti-slop Delivery Gate.
7. Commit to this feature branch. Push, PR, merge, and deployment require separate explicit approval.

## Sources

- Copernicus WorldDEM-30 public licence: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/DEM/resources/license/License-COPDEM-30.pdf
- Copernicus DEM overview and access: https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
- NASA GIBS access basics: https://nasa-gibs.github.io/gibs-api-docs/access-basics
- NASA GIBS acknowledgement guidance: https://www.earthdata.nasa.gov/engage/open-data-services-software/earthdata-developer-portal/gibs-api
- Cartographic terrain representation: https://gistbok-topics.ucgis.org/CV-04-014
