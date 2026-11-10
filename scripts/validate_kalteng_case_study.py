#!/usr/bin/env python3
"""Validate publishable Karhutla Signal Review assets without network access."""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "karhutla-kalteng" / "processed"


class Validator(HTMLParser):
    def error(self, message):
        raise RuntimeError(message)


def load_collection(filename, required_properties, geometry_types={"Point"}):
    data = json.loads((BASE / filename).read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection" or not data.get("features"):
        raise SystemExit(f"Invalid or empty GeoJSON: {filename}")
    for feature in data["features"]:
        if feature.get("type") != "Feature":
            raise SystemExit(f"Invalid feature type in {filename}")
        geometry = feature.get("geometry") or {}
        if geometry.get("type") not in geometry_types:
            raise SystemExit(f"Unexpected geometry type in {filename}")
        if geometry.get("type") == "Point":
            coordinates = geometry.get("coordinates", [])
            if len(coordinates) != 2 or not (-180 <= coordinates[0] <= 180 and -90 <= coordinates[1] <= 90):
                raise SystemExit(f"Invalid point coordinates in {filename}")
        properties = feature.get("properties") or {}
        missing = [key for key in required_properties if key not in properties]
        if missing:
            raise SystemExit(f"Missing properties in {filename}: {', '.join(missing)}")
    return data["features"]


def main():
    page = ROOT / "karhutla-review" / "index.html"
    source = page.read_text(encoding="utf-8")
    Validator().feed(source)
    Validator().close()
    for fragment in (
        "<main", "id=\"map\"", "id=\"map-state\"", "vendor/leaflet-1.9.4.css",
        "style.css", "app.js", "not an emergency-warning system",
        "not a confirmed fire register", "not a burned-area estimate",
    ):
        if fragment not in source:
            raise SystemExit(f"Case-study page missing: {fragment}")

    admin = load_collection("kalteng-admin2.geojson", {"adm1_name", "adm2_name"}, {"Polygon", "MultiPolygon"})
    signals = load_collection("signals-high.geojson", {"acq_date", "confidence", "snapshot_id", "kabupaten"})
    clusters = load_collection("clusters-review.geojson", {
        "cluster_id", "snapshot_id", "signal_count", "high_confidence_count",
        "first_seen_utc", "last_seen_utc", "review_status", "interpretation_note",
    })
    if any(feature["properties"]["adm1_name"] != "Kalimantan Tengah" for feature in admin):
        raise SystemExit("Administrative display layer contains non-Central Kalimantan feature")
    if any(feature["properties"]["confidence"] != "high" for feature in signals):
        raise SystemExit("Display signal layer contains non-high confidence feature")
    if any(feature["properties"]["signal_count"] < 5 for feature in clusters):
        raise SystemExit("Display cluster layer contains fewer than 5 signals")

    metadata = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
    for key in ("snapshot_id", "region", "period", "source", "processing", "display_filters", "counts", "limitations"):
        if not metadata.get(key):
            raise SystemExit(f"Missing provenance metadata: {key}")
    if metadata["snapshot_id"] != "kalteng-2026-09-v1" or metadata["region"] != "Central Kalimantan, Indonesia":
        raise SystemExit("Unexpected snapshot identity")
    if metadata["period"] != ["2026-09-01", "2026-09-30"] or metadata["source"] != "VIIRS_NOAA20_NRT":
        raise SystemExit("Unexpected source provenance")
    if metadata["display_filters"] != {"signals_high_confidence_only": True, "clusters_minimum_signal_count": 5}:
        raise SystemExit("Unexpected display filters")
    if "not confirmed fire incidents" not in metadata["limitations"]:
        raise SystemExit("Metadata limitation is incomplete")
    counts = metadata["counts"]
    expected = (len(signals), len(clusters), sum(item["properties"]["signal_count"] for item in clusters))
    actual = (counts.get("display_high_confidence_signals"), counts.get("display_review_clusters"), counts.get("display_cluster_signals"))
    if actual != expected:
        raise SystemExit("Metadata display counts do not match GeoJSON")
    print("karhutla_case_study_assets=valid")


if __name__ == "__main__":
    main()
