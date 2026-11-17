# Architecture

## Site model

The portfolio is a static HTML, CSS, and JavaScript site published from the repository default branch by GitHub Pages.

```text
index.html
├─ /karhutla-review/
└─ /aceh-tamiang-flood-review/
```

The homepage is a practice-area navigator. It links only to case studies that have a public artifact and a verified route.

## Case-study pattern

Each case study contains:

- a standalone route directory with `index.html`, `style.css`, and `app.js`;
- browser-oriented GeoJSON and `metadata.json` under `data/<case-study>/processed/`;
- a deterministic local builder in `scripts/`;
- an offline validator in `scripts/`;
- a case-study PRD or plan in `docs/<case-study>/`.

Map pages may use Leaflet. Locally vendor static CSS where practical. Remote scripts must be pinned with integrity metadata or replaced with a local asset after review.

## Data boundaries

### Published assets

Only reviewed, lightweight display layers and metadata are publishable. Validators check feature counts, geometry and property contracts, source metadata, display filters, limitations, and checksum relationships where the case study requires them.

### Local-only material

Raw API responses, source downloads, caches, credentials, full heavy processing artifacts, and temporary logs remain outside the published bundle and must be ignored by Git.

### Evidence vocabulary

Case studies must label data by what it supports:

- NASA FIRMS thermal detections are signals, not confirmed fire incidents.
- Derived signal clusters are review units, not confirmed events.
- Aceh Tamiang highlighted polygons are report-named administrative areas, not physical flood extent.
- Reference boundaries do not determine legal responsibility or the edge of a hazard.

## Validation architecture

`.github/workflows/validate-site.yml` runs on pull requests and pushes to `main`.

It validates:

- homepage HTML structure;
- Karhutla display assets, metadata, and limitations;
- Aceh Tamiang report-footprint assets, metadata, geometry, checksums, and limitations;
- case-study JavaScript syntax;
- published asset patterns that could indicate credential assignment.

The local browser check complements CI. It verifies rendering, interactive controls, map states, keyboard access, mobile layout, and absence of horizontal overflow.

## Change boundaries

A change to a published case-study source, snapshot period, boundary version, data method, display threshold, or limitation is a new evidence decision. Update the relevant PRD, builder, metadata, validator, map copy, and CI expectation together.
