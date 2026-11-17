#!/usr/bin/env python3
"""Validate publishable Aceh Tamiang flood context review assets offline."""
from __future__ import annotations

import hashlib
import json
import math
import struct
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "aceh-tamiang-flood" / "processed"
EXPECTED = {"Kota Kuala Simpang", "Kejuruan Muda", "Karang Baru", "Rantau", "Bendahara"}
TERRAIN_NAME = "terrain-hillshade.png"
TERRAIN_ATTRIBUTION = "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014"
GIBS_URL = "MODIS_Terra_CorrectedReflectance_TrueColor/default/2026-11-16"


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
        if feature.get("type") != "Feature":
            raise SystemExit(f"Invalid feature in {name}")
        validate_geometry(feature.get("geometry") or {}, name)
        p = feature.get("properties") or {}
        for key in ("admin_id", "subdistrict", "regency", "province", "boundary_version", "snapshot_id", "report_date", "report_state"):
            if not p.get(key):
                raise SystemExit(f"Missing {key} in {name}")
        if p["admin_id"] in ids:
            raise SystemExit(f"Duplicate admin ID in {name}")
        ids.add(p["admin_id"])
    return data["features"]


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(24)
    if signature[:8] != b"\x89PNG\r\n\x1a\n" or signature[12:16] != b"IHDR":
        raise SystemExit("Terrain asset is not a valid PNG")
    return struct.unpack(">II", signature[16:24])


def main():
    home_source = (ROOT / "index.html").read_text(encoding="utf-8")
    home_parser = Validator()
    home_parser.feed(home_source)
    home_parser.close()
    if '<a href="#work">Work</a>' not in home_source:
        raise SystemExit("Homepage Work navigation missing")
    for href in ("karhutla-review/", "aceh-tamiang-flood-review/"):
        if href not in home_source:
            raise SystemExit(f"Homepage case-study route missing: {href}")

    page = ROOT / "aceh-tamiang-flood-review" / "index.html"
    source = page.read_text(encoding="utf-8")
    parser = Validator()
    parser.feed(source)
    parser.close()
    required_page = (
        "not an emergency-warning system",
        "not a flood-extent map",
        "does not estimate water depth, damage, or response priority",
        "Reference imagery, not event-date flood evidence.",
        "reference-imagery",
        "terrain-attribution",
        "vendor/leaflet-1.9.4.css",
    )
    if missing := [text for text in required_page if text not in source]:
        raise SystemExit(f"Page missing required limitation or asset: {', '.join(missing)}")

    app = (ROOT / "aceh-tamiang-flood-review" / "app.js").read_text(encoding="utf-8")
    required_app = ("L.imageOverlay", "terrain.output", GIBS_URL, "imageryToggle.checked", "imageryNotice.hidden", "imageryAttribution.hidden", "maxBounds: terrainBounds", "maxBoundsViscosity: 1.0", "const viewPadding = [20, 20];", "map.fitBounds(bounds, { padding: viewPadding });", "map.setMinZoom(map.getZoom())", "reset-map")
    if missing := [text for text in required_app if text not in app]:
        raise SystemExit(f"Map application missing required relief or imagery behavior: {', '.join(missing)}")
    initial_fit = app.index("map.fitBounds(bounds, { padding: viewPadding });")
    min_zoom = app.index("map.setMinZoom(map.getZoom())")
    reset_handler = app.index("document.getElementById('reset-map').addEventListener")
    reset_fit = app.index("map.fitBounds(bounds, { padding: viewPadding })", reset_handler)
    if not initial_fit < min_zoom < reset_handler < reset_fit:
        raise SystemExit("Map bounds, min zoom, and reset order mismatch")
    if "L.tileLayer('https://{s}.tile.openstreetmap.org" in app:
        raise SystemExit("OSM basemap must not be restored")

    admin = collection("aceh-tamiang-admin3.geojson", 12)
    report = collection("reported-impact-footprint.geojson", 5)
    if {x["properties"]["subdistrict"] for x in report} != EXPECTED:
        raise SystemExit("Report footprint names do not match dated report snapshot")
    if any(x["properties"]["report_state"] != "named_in_report" for x in report):
        raise SystemExit("Report layer contains non-report feature")
    if any(x["properties"]["report_state"] not in {"named_in_report", "not_named_in_snapshot"} for x in admin):
        raise SystemExit("Context layer has unexpected report state")

    meta = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
    for key in ("snapshot_id", "report_snapshot_date", "report_source", "boundary_source", "boundary_version", "processing", "reported_subdistricts", "counts", "limitations", "terrain_relief", "satellite_reference"):
        if not meta.get(key):
            raise SystemExit(f"Metadata missing: {key}")
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
    limits = " ".join(meta["limitations"]).lower()
    for limit in ("not an emergency-warning system", "not a flood-extent map", "does not estimate water depth", "terrain relief is a general reference context"):
        if limit not in limits:
            raise SystemExit("Metadata limitations incomplete")

    satellite = meta["satellite_reference"]
    expected_satellite = {
        "role": "Optional reference imagery, not event-date flood evidence.",
        "provider": "NASA Global Imagery Browse Services (GIBS)",
        "product_id": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "fixed_date": "2026-11-16",
        "default_enabled": False,
    }
    if any(satellite.get(key) != value for key, value in expected_satellite.items()):
        raise SystemExit("Satellite reference metadata mismatch")
    if GIBS_URL not in satellite.get("tile_endpoint", "") or "NASA's Global Imagery Browse Services" not in satellite.get("acknowledgement", ""):
        raise SystemExit("Satellite reference endpoint or acknowledgement incomplete")

    terrain = meta["terrain_relief"]
    for key in ("role", "source", "source_version", "source_urls", "source_tile_sha256", "attribution", "buffer_km", "bounds_wgs84", "processing", "output", "pixel_dimensions", "byte_size", "sha256"):
        if not terrain.get(key):
            raise SystemExit(f"Terrain metadata missing: {key}")
    if terrain["source"] != "Copernicus WorldDEM-30 GLO-30" or terrain["role"] != "Reference terrain context, not flood evidence.":
        raise SystemExit("Unexpected terrain source or role")
    if terrain["buffer_km"] != 15 or len(terrain["source_urls"]) != 4:
        raise SystemExit("Unexpected terrain buffer or source tile count")
    if TERRAIN_ATTRIBUTION not in terrain["attribution"]:
        raise SystemExit("Terrain attribution incomplete")
    bounds = terrain["bounds_wgs84"]
    if len(bounds) != 4 or not (bounds[0] < bounds[2] and bounds[1] < bounds[3]):
        raise SystemExit("Invalid terrain bounds")
    context_coordinates = []
    for feature in admin:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        else:
            polygons = geometry["coordinates"]
        context_coordinates.extend(point for polygon in polygons for ring in polygon for point in ring)
    context_west = min(point[0] for point in context_coordinates)
    context_south = min(point[1] for point in context_coordinates)
    context_east = max(point[0] for point in context_coordinates)
    context_north = max(point[1] for point in context_coordinates)
    if not (bounds[0] < context_west and bounds[1] < context_south and bounds[2] > context_east and bounds[3] > context_north):
        raise SystemExit("Terrain bounds do not contain administrative context")
    center_latitude = (context_south + context_north) / 2
    expected_latitude_delta = terrain["buffer_km"] / 110.574
    expected_longitude_delta = terrain["buffer_km"] / (111.320 * math.cos(math.radians(center_latitude)))
    expected_bounds = [
        context_west - expected_longitude_delta,
        context_south - expected_latitude_delta,
        context_east + expected_longitude_delta,
        context_north + expected_latitude_delta,
    ]
    # Bounds are stored to nine decimal places, so one nanodegree permits only serialization rounding.
    tolerance = 0.000000001
    if any(abs(actual - expected) > tolerance for actual, expected in zip(bounds, expected_bounds)):
        raise SystemExit("Terrain bounds do not match the documented buffer")
    terrain_path = BASE / terrain["output"]
    if terrain_path.name != TERRAIN_NAME or not terrain_path.is_file():
        raise SystemExit("Terrain image is missing")
    width, height = png_dimensions(terrain_path)
    if terrain["pixel_dimensions"] != {"width": width, "height": height} or min(width, height) < 500:
        raise SystemExit("Terrain PNG dimensions mismatch")
    if terrain["byte_size"] != terrain_path.stat().st_size or terrain["sha256"] != hashlib.sha256(terrain_path.read_bytes()).hexdigest():
        raise SystemExit("Terrain PNG checksum or size mismatch")
    print("aceh_tamiang_flood_context_assets=valid")


if __name__ == "__main__":
    main()
