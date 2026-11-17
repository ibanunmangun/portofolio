#!/usr/bin/env python3
"""Build publishable Aceh Tamiang report-footprint assets from local HDX data."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_ARCHIVE = ROOT / "data" / "karhutla-kalteng" / "raw" / "hdx-idn-admin.geojson.zip"
OUTPUT = ROOT / "data" / "aceh-tamiang-flood" / "processed"

SNAPSHOT_ID = "aceh-tamiang-flood-report-2026-11-16-v1"
REPORT_DATE = "2026-11-16"
REPORT_PUBLISHED = "2026-11-16"
REPORT_SOURCE = "https://en.tempo.co/read/2123741/over-2600-displaced-as-floods-hit-aceh-tamiang-again"
BOUNDARY_SOURCE = "https://data.humdata.org/dataset/cod-ab-idn"
BOUNDARY_VERSION = "HDX COD-AB Indonesia administrative boundaries, 2020"
REPORTED_SUBDISTRICTS = (
    "Kota Kuala Simpang",
    "Kejuruan Muda",
    "Karang Baru",
    "Rantau",
    "Bendahara",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_feature(feature: dict, required_properties: tuple[str, ...]) -> None:
    if feature.get("type") != "Feature":
        raise ValueError("Expected GeoJSON Feature")
    geometry = feature.get("geometry") or {}
    if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Expected Polygon or MultiPolygon")
    if not geometry.get("coordinates"):
        raise ValueError("Geometry must have coordinates")
    properties = feature.get("properties") or {}
    missing = [name for name in required_properties if not properties.get(name)]
    if missing:
        raise ValueError(f"Feature missing required properties: {', '.join(missing)}")


def public_feature(feature: dict, *, reported: bool) -> dict:
    properties = feature["properties"]
    return {
        "type": "Feature",
        "geometry": feature["geometry"],
        "properties": {
            "admin_id": properties["adm3_pcode"],
            "subdistrict": properties["adm3_name"],
            "regency": properties["adm2_name"],
            "province": properties["adm1_name"],
            "boundary_version": BOUNDARY_VERSION,
            "snapshot_id": SNAPSHOT_ID,
            "report_date": REPORT_DATE,
            "report_state": "named_in_report" if reported else "not_named_in_snapshot",
        },
    }


def main() -> None:
    if not RAW_ARCHIVE.is_file():
        raise SystemExit(f"Missing local boundary archive: {RAW_ARCHIVE}")
    with zipfile.ZipFile(RAW_ARCHIVE) as archive:
        raw = json.loads(archive.read("idn_admin3.geojson"))
    selected = [
        feature for feature in raw["features"]
        if feature.get("properties", {}).get("adm2_name") == "Aceh Tamiang"
    ]
    if len(selected) != 12:
        raise SystemExit(f"Expected 12 Aceh Tamiang subdistricts, got {len(selected)}")
    for feature in selected:
        validate_feature(feature, ("adm1_name", "adm2_name", "adm3_name", "adm3_pcode"))
    names = {feature["properties"]["adm3_name"] for feature in selected}
    missing = sorted(set(REPORTED_SUBDISTRICTS) - names)
    if missing:
        raise SystemExit(f"Report names not found in boundary source: {', '.join(missing)}")

    selected.sort(key=lambda feature: feature["properties"]["adm3_name"])
    admin_features = [public_feature(feature, reported=feature["properties"]["adm3_name"] in REPORTED_SUBDISTRICTS) for feature in selected]
    report_features = [feature for feature in admin_features if feature["properties"]["report_state"] == "named_in_report"]
    if len(report_features) != len(REPORTED_SUBDISTRICTS):
        raise SystemExit("Report footprint count mismatch")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "aceh-tamiang-admin3.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": admin_features}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    (OUTPUT / "reported-impact-footprint.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": report_features}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    output_checksums = {
        "aceh-tamiang-admin3.geojson": sha256_file(OUTPUT / "aceh-tamiang-admin3.geojson"),
        "reported-impact-footprint.geojson": sha256_file(OUTPUT / "reported-impact-footprint.geojson"),
    }
    metadata = {
        "snapshot_id": SNAPSHOT_ID,
        "title": "Aceh Tamiang Flood Context Review, November 2026",
        "region": "Aceh Tamiang Regency, Aceh, Indonesia",
        "report_snapshot_date": REPORT_DATE,
        "report_published_date": REPORT_PUBLISHED,
        "report_source": REPORT_SOURCE,
        "boundary_source": BOUNDARY_SOURCE,
        "boundary_version": BOUNDARY_VERSION,
        "boundary_archive_sha256": sha256_file(RAW_ARCHIVE),
        "output_checksums_sha256": output_checksums,
        "processing": "Filter local HDX ADM3 features where adm2_name is Aceh Tamiang; select report-named subdistricts using an explicit fixed name list.",
        "reported_subdistricts": list(REPORTED_SUBDISTRICTS),
        "counts": {
            "aceh_tamiang_subdistrict_context": len(admin_features),
            "report_named_subdistricts": len(report_features),
        },
        "limitations": [
            "This is not an emergency-warning system.",
            "This is not a flood-extent map.",
            "This does not estimate water depth, damage, or response priority.",
            "Highlighted polygons are administrative areas named in a dated report.",
            "An area not highlighted was not named in this report snapshot and may still have been affected.",
            "Administrative boundaries are reference geometry and do not trace the edge of floodwater.",
            "Boundary geometry is from a 2020 HDX administrative-boundary release and is used as reference context, not an authoritative legal boundary determination.",
        ],
    }
    (OUTPUT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"context_subdistricts={len(admin_features)}")
    print(f"report_named_subdistricts={len(report_features)}")


if __name__ == "__main__":
    main()
