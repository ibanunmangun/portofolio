#!/usr/bin/env python3
"""Validate publishable Aceh Tamiang flood context review assets offline."""
from __future__ import annotations
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "aceh-tamiang-flood" / "processed"
EXPECTED = {"Kota Kuala Simpang", "Kejuruan Muda", "Karang Baru", "Rantau", "Bendahara"}

class Validator(HTMLParser):
    def error(self, message):
        raise RuntimeError(message)

def coordinate_pair(value):
    return isinstance(value, list) and len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2])

def validate_ring(ring, name):
    if not isinstance(ring, list) or len(ring) < 4 or not all(coordinate_pair(point) for point in ring):
        raise SystemExit(f"Invalid linear ring in {name}")
    if ring[0][:2] != ring[-1][:2]:
        raise SystemExit(f"Unclosed linear ring in {name}")
    for lon, lat, *_ in ring:
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise SystemExit(f"Out-of-range coordinate in {name}")

def validate_geometry(geometry, name):
    if geometry.get("type") == "Polygon":
        polygons = [geometry.get("coordinates")]
    elif geometry.get("type") == "MultiPolygon":
        polygons = geometry.get("coordinates")
    else:
        raise SystemExit(f"Unexpected geometry type in {name}")
    if not isinstance(polygons, list) or not polygons:
        raise SystemExit(f"Missing geometry coordinates in {name}")
    for polygon in polygons:
        if not isinstance(polygon, list) or not polygon:
            raise SystemExit(f"Invalid polygon structure in {name}")
        for ring in polygon:
            validate_ring(ring, name)

def collection(name: str, expected_count: int):
    data = json.loads((BASE / name).read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection" or len(data.get("features", [])) != expected_count:
        raise SystemExit(f"Unexpected GeoJSON collection: {name}")
    ids = set()
    for feature in data["features"]:
        if feature.get("type") != "Feature": raise SystemExit(f"Invalid feature in {name}")
        geometry = feature.get("geometry") or {}
        validate_geometry(geometry, name)
        p = feature.get("properties") or {}
        for key in ("admin_id", "subdistrict", "regency", "province", "boundary_version", "snapshot_id", "report_date", "report_state"):
            if not p.get(key): raise SystemExit(f"Missing {key} in {name}")
        if p["admin_id"] in ids: raise SystemExit(f"Duplicate admin ID in {name}")
        ids.add(p["admin_id"])
    return data["features"]

def main():
    home = ROOT / "index.html"
    home_source = home.read_text(encoding="utf-8")
    home_parser = Validator(); home_parser.feed(home_source); home_parser.close()
    if '<a href="#work">Work</a>' not in home_source:
        raise SystemExit("Homepage Work navigation missing")
    for href in ('karhutla-review/', 'aceh-tamiang-flood-review/'):
        if href not in home_source:
            raise SystemExit(f"Homepage case-study route missing: {href}")
    page = ROOT / "aceh-tamiang-flood-review" / "index.html"
    source = page.read_text(encoding="utf-8")
    parser = Validator(); parser.feed(source); parser.close()
    for text in ("not an emergency-warning system", "not a flood-extent map", "does not estimate water depth, damage, or response priority", "vendor/leaflet-1.9.4.css"):
        if text not in source: raise SystemExit(f"Page missing required limitation or asset: {text}")
    admin = collection("aceh-tamiang-admin3.geojson", 12)
    report = collection("reported-impact-footprint.geojson", 5)
    if {x["properties"]["subdistrict"] for x in report} != EXPECTED:
        raise SystemExit("Report footprint names do not match dated report snapshot")
    if any(x["properties"]["report_state"] != "named_in_report" for x in report):
        raise SystemExit("Report layer contains non-report feature")
    if any(x["properties"]["report_state"] not in {"named_in_report", "not_named_in_snapshot"} for x in admin):
        raise SystemExit("Context layer has unexpected report state")
    meta = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
    for key in ("snapshot_id", "report_snapshot_date", "report_source", "boundary_source", "boundary_version", "processing", "reported_subdistricts", "counts", "limitations"):
        if not meta.get(key): raise SystemExit(f"Metadata missing: {key}")
    if meta["report_snapshot_date"] != "2026-11-16" or set(meta["reported_subdistricts"]) != EXPECTED:
        raise SystemExit("Metadata report snapshot mismatch")
    if meta["boundary_version"] != "HDX COD-AB Indonesia administrative boundaries, 2020":
        raise SystemExit("Unexpected boundary version")
    if any(feature["properties"]["boundary_version"] != meta["boundary_version"] for feature in admin + report):
        raise SystemExit("Feature boundary version does not match metadata")
    if meta["counts"] != {"aceh_tamiang_subdistrict_context": len(admin), "report_named_subdistricts": len(report)}:
        raise SystemExit("Metadata counts mismatch")
    checksums = meta.get("output_checksums_sha256")
    expected_checksums = {
        name: hashlib.sha256((BASE / name).read_bytes()).hexdigest()
        for name in ("aceh-tamiang-admin3.geojson", "reported-impact-footprint.geojson")
    }
    if checksums != expected_checksums:
        raise SystemExit("Metadata output checksums do not match GeoJSON assets")
    required_limits = ("not an emergency-warning system", "not a flood-extent map", "does not estimate water depth")
    limits = " ".join(meta["limitations"]).lower()
    if not all(value in limits for value in required_limits): raise SystemExit("Metadata limitations incomplete")
    print("aceh_tamiang_flood_context_assets=valid")

if __name__ == "__main__": main()
