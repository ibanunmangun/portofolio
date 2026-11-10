# Fixed Plan — Karhutla Signal Review: Central Kalimantan

**Status:** Approved direction, pending data-key setup and implementation approval.

**Portfolio project:** `ibanunmangun/portofolio`

**Proposed route:** `/portofolio/karhutla-review/`

**Purpose:** Build a reproducible, public-data portfolio demonstrator that turns satellite thermal detections into a bounded spatial-review workflow for Central Kalimantan.

## 1. Product statement

> **Karhutla Signal Review — Central Kalimantan**
>
> A portfolio demonstrator for exploring public satellite thermal signals with time, confidence, clustering, and administrative context.

This is not an emergency-warning system, a fire-incident register, a burned-area estimate, or a response recommendation tool.

## 2. What v1 will show

### Map layers

1. **Satellite thermal signals**
   - VIIRS 375 m detections from NASA FIRMS.
   - Point fields: acquisition date/time, satellite, confidence, fire radiative power, and day/night flag where supplied.
   - Rendering: confidence-sensitive point styling; no language that turns a point into a confirmed fire event.

2. **Derived review clusters**
   - A cluster is a grouping of nearby signals within the selected time window.
   - Each cluster receives a stable snapshot ID, signal count, confidence mix, first/last acquisition time, centroid, and intersecting kabupaten.
   - Every cluster starts with the neutral status: `requires contextual review`.

3. **Administrative context**
   - Central Kalimantan provincial outline.
   - Kabupaten boundaries and names.
   - Used for navigation and aggregation only; never used to assign responsibility.

### Interface

- Full-width interactive map with a desktop and mobile-safe layout.
- Time-window selector for the fixed snapshot period.
- Confidence filter: all / nominal / high.
- Toggle for raw signals, review clusters, and administrative boundaries.
- Detail panel for a selected cluster.
- Method, data, caveats, and source links below the map.

## 3. Scope boundaries

### In scope

- One reproducible data snapshot for Central Kalimantan.
- A static web map served from GitHub Pages.
- Source data retained in a documented, compact portfolio-friendly format.
- Client-side map interaction with no backend, user accounts, tracking, or live refresh.
- A transparent pipeline that can be rerun when a new snapshot is intentionally chosen.

### Out of scope for v1

- Live fire monitoring or alerting.
- Push notifications, recommended deployment locations, patrol plans, or incident response instructions.
- Burned-area calculation or causal attribution.
- Land-concession, company, individual, or blame-related overlays.
- Dynamic third-party API calls from the published page.
- Bundling BNPB InaRISK risk rasters or other restricted government layers.
- Papua comparison, peatland overlays, and imagery classification. These are later additions only after license and narrative review.

## 4. Data feasibility decision

| Need | Chosen source | Decision | Reason |
|---|---|---|---|
| Thermal-signal snapshot | NASA FIRMS, VIIRS NOAA-20 or NOAA-21 | **Use** | Publicly documented source; VIIRS represents a 375 m thermal-detection pixel centre and exposes confidence and acquisition attributes. The area API supports historical bounded requests but requires a free MAP_KEY. |
| Historical period | NASA FIRMS standard-processing product when available; otherwise explicitly labelled NRT snapshot | **Use with provenance label** | Standard processing is preferable for a reproducible analysis; NRT is acceptable only when the page labels it as a snapshot and records extraction date/version. |
| Admin boundaries | HDX COD-AB Indonesia, filtered to Central Kalimantan | **Use with attribution** | Public administrative boundaries from BPS-derived humanitarian dataset. Keep source and attribution in the project. |
| Official Indonesia fire context | SiPongi+ | **Link only** | It is an official public reference for current fire-monitoring information, but v1 will not scrape or redistribute its data. |
| Fire-risk raster | BNPB InaRISK | **Do not bundle in v1** | The portal metadata includes use restrictions and states that hazard/risk information is not an early-warning product. Do not copy or redistribute without explicit permission. |
| Peatland context | No source selected for v1 | **Defer** | A useful future overlay, but needs a source, license, scale, and interpretation review before inclusion. |

## 5. Required input before implementation

### NASA FIRMS MAP_KEY

Create a free NASA FIRMS MAP_KEY for the data-preparation step. The key will be used locally only and must not be committed, embedded in the published site, logged, or sent in chat.

The published map will contain a static, attributed snapshot rather than a browser-side query to FIRMS. This prevents key exposure and keeps the case study reproducible.

## 6. Snapshot specification

**Recommended initial period:** `2026-09-01` through `2026-09-30`.

Why this period:

- It gives enough observations for meaningful clustering without turning the first release into a nationwide dashboard.
- It is fixed, reproducible, and separate from current operational monitoring.
- The page can later include a second snapshot as an intentionally versioned comparison, not a silent live update.

**Spatial boundary:** Central Kalimantan province boundary, expanded by a small processing buffer only when needed to avoid losing edge clusters. Displayed results must be clipped to the province boundary.

**Sensor policy:** Start with a single VIIRS product to avoid double-counting across sensors. Prefer NOAA-20 standard processing when the selected dates are available; record exact FIRMS dataset/version in `data/metadata.json`.

## 7. Data pipeline

```text
FIRMS request with MAP_KEY
  → raw CSV retained outside public web bundle
  → schema validation and date/bounds checks
  → Central Kalimantan spatial filter
  → confidence normalization
  → spatial + temporal clustering
  → point and cluster GeoJSON
  → simplify / size-budget check
  → static map assets + metadata + attribution
```

### 7.1 Validation gates

1. **Schema gate**
   - Required columns: latitude, longitude, acquisition date/time, confidence, satellite/instrument, and version.
   - Reject records outside valid coordinate/date ranges.

2. **Spatial gate**
   - Point must intersect Central Kalimantan after the final geographic filter.
   - No manual coordinate edits.

3. **Temporal gate**
   - Every record must fall inside the declared snapshot period.
   - Extraction timestamp and source version are stored in metadata.

4. **Cluster gate**
   - Initial proposal: DBSCAN using a documented geographic distance threshold and a fixed time-bucket rule.
   - Tune threshold only using documented alternatives; no visual cherry-picking.
   - A cluster remains a `satellite signal cluster`, not a confirmed incident.

5. **Publish gate**
   - Validate GeoJSON syntax and feature properties.
   - Confirm data contains no API key, personal data, client data, or unsupported claims.
   - Check mobile interaction, keyboard focus, map attribution, disclaimer, and asset size.

## 8. Proposed data model

### `signals.geojson`

```json
{
  "id": "firms-20260912-001",
  "acq_date": "2026-09-12",
  "acq_time_utc": "06:24",
  "sensor": "VIIRS NOAA-20",
  "confidence": "high",
  "frp_mw": 12.3,
  "daynight": "D",
  "snapshot_id": "kalteng-2026-09-v1"
}
```

### `clusters.geojson`

```json
{
  "cluster_id": "KALTENG-202609-C014",
  "snapshot_id": "kalteng-2026-09-v1",
  "signal_count": 18,
  "high_confidence_count": 7,
  "first_seen_utc": "2026-09-12T06:24:00Z",
  "last_seen_utc": "2026-09-15T18:11:00Z",
  "kabupaten": "Derived by spatial join",
  "review_status": "requires contextual review",
  "interpretation_note": "Satellite thermal-signal cluster; not a confirmed fire incident or burned-area boundary."
}
```

## 9. Web implementation

### Technical posture

- Plain HTML/CSS/JavaScript, keeping the current GitHub Pages deployment model.
- Leaflet is the preferred first map library because the interaction needs are bounded and transparent.
- Use a well-attributed public basemap only if its terms permit portfolio display. Include a no-basemap fallback using boundaries and neutral background.
- Package derived small GeoJSON assets locally; do not make secret-bearing or availability-sensitive browser calls.
- Add a dedicated CI check for JSON/GeoJSON parseability and the presence of the mandatory disclaimer/attribution.

### Content structure

```text
Case-study context
→ question and scope boundary
→ interactive map and controls
→ selected-cluster detail panel
→ method: signals → clusters → review
→ data provenance and snapshot metadata
→ limitations / what this does not claim
→ source links and attribution
```

## 10. Copy guardrails

Allowed terms:

- satellite thermal signal
- hotspot detection
- signal cluster
- confidence category
- public-data snapshot
- requires contextual review

Prohibited terms unless independently supported by a separate source and review:

- confirmed fire
- fire incident
- burned area
- cause
- responsible party
- illegal activity
- priority response
- evacuation recommendation

## 11. Implementation sequence

1. Obtain and locally store the FIRMS MAP_KEY outside Git.
2. Pull and inspect the proposed September 2026 FIRMS data snapshot.
3. Download and filter Central Kalimantan administrative boundaries; record attribution.
4. Build a small, deterministic preprocessing script and tests.
5. Produce a first static GeoJSON snapshot plus metadata.
6. Review counts, clusters, and wording with Nulla before map UI work.
7. Build the interactive case-study page on a feature branch.
8. Add CI for HTML and GeoJSON validation.
9. Browser-test desktop and mobile; perform an independent review.
10. Open a PR. Do not merge or publish further changes without Nulla's explicit approval.

## 12. Acceptance criteria for v1

- Map loads on GitHub Pages without a backend or exposed API key.
- Every displayed point has traceable snapshot provenance.
- Every displayed cluster is labelled as a derived review unit, not an incident.
- Filtering works by confidence and layer visibility.
- Selecting a cluster exposes its count, time span, confidence mix, and administrative context.
- Page includes source attribution, snapshot date, method summary, and non-alert disclaimer.
- Static CI passes for page and GeoJSON assets.
- No client, personal, restricted, or unlicensed data is committed.

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hotspots are misunderstood as confirmed fires | Use neutral labels and an explicit limitation next to the legend and detail panel. |
| Data-source/API availability changes | Freeze a documented local snapshot; link to the source instead of depending on live loading. |
| API key leaks | Keep it out of Git, generated assets, browser code, logs, and chat. |
| Sensor data is double-counted | Start with one documented VIIRS product only. |
| Map becomes a generic dashboard | Keep one region, one question, a constrained review workflow, and a small layer set. |
| Restricted context layers introduce reuse risk | Do not bundle them until license/permission is verified. |

## Sources

- NASA FIRMS Area API: https://firms.modaps.eosdis.nasa.gov/api/area/
- NASA FIRMS Active Fire data overview: https://www.earthdata.nasa.gov/data/tools/firms
- NASA FIRMS active-fire attributes: https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs
- HDX Indonesia administrative boundaries: https://data.humdata.org/dataset/cod-ab-idn
- SiPongi+ (Ministry of Forestry): https://sipongi.gakkum.kehutanan.go.id/
- BNPB Indonesia disaster-risk map catalogue: https://data.bnpb.go.id/dataset/peta-risiko-bencana-indonesia

## Decision needed

Approve this fixed plan and provide the NASA FIRMS MAP_KEY through an approved secret mechanism when ready. Do not paste the key into Telegram.
