#!/usr/bin/env python3
"""Build a bounded, reproducible Central Kalimantan FIRMS snapshot.

Reads FIRMS_MAP_KEY from the process environment. The key is never written to
output. Raw FIRMS CSV responses stay in data/.../raw and are git-ignored.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import os
import pathlib
import time
import urllib.request
import zipfile
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "karhutla-kalteng"
RAW = DATA / "raw"
OUT = DATA / "processed"
ZIP = RAW / "hdx-idn-admin.geojson.zip"
START = dt.date(2026, 9, 1)
END = dt.date(2026, 9, 30)
SOURCE = "VIIRS_NOAA20_NRT"
# Broad request boundary; final results are clipped to the HDX province polygon.
BBOX = "110.0,-4.2,116.1,-0.4"


def feature_collection(features):
    return {"type": "FeatureCollection", "features": features}


def ring_contains(point, ring):
    x, y = point
    inside = False
    for i, (x1, y1) in enumerate(ring):
        x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > y) != (y2 > y):
            cross = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < cross:
                inside = not inside
    return inside


def geometry_contains(point, geometry):
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    for polygon in polygons:
        if ring_contains(point, polygon[0]) and not any(ring_contains(point, hole) for hole in polygon[1:]):
            return True
    return False


def geometry_bbox(geometry):
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    points = [point for polygon in polygons for ring in polygon for point in ring]
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)


def load_boundaries():
    with zipfile.ZipFile(ZIP) as zf:
        data = json.loads(zf.read("idn_admin2.geojson"))
    features = [f for f in data["features"] if f["properties"].get("adm1_name") == "Kalimantan Tengah"]
    if not features:
        raise RuntimeError("No Central Kalimantan features in HDX boundary source")
    for feature in features:
        feature["_bbox"] = geometry_bbox(feature["geometry"])
    return features


def fetch_day(key, day):
    path = RAW / f"firms-{day.isoformat()}.csv"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        print(f"using cached {day.isoformat()}")
        return list(csv.DictReader(text.splitlines()))
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{SOURCE}/{BBOX}/1/{day.isoformat()}"
    request = urllib.request.Request(url, headers={"User-Agent": "portfolio-snapshot/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        text = response.read().decode("utf-8")
    path.write_text(text, encoding="utf-8")
    return list(csv.DictReader(text.splitlines()))


def confidence(value):
    v = str(value).strip().lower()
    return {"h": "high", "high": "high", "n": "nominal", "nominal": "nominal", "l": "low", "low": "low"}.get(v, "unknown")


def to_feature(row, number, boundaries):
    lon, lat = float(row["longitude"]), float(row["latitude"])
    matched = None
    for boundary in boundaries:
        west, south, east, north = boundary["_bbox"]
        if west <= lon <= east and south <= lat <= north and geometry_contains((lon, lat), boundary["geometry"]):
            matched = boundary
            break
    if not matched:
        return None
    props = matched["properties"]
    return {
        "type": "Feature",
        "id": f"KALTENG-{row['acq_date'].replace('-', '')}-{number:06d}",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "acq_date": row["acq_date"], "acq_time_utc": str(row["acq_time"]).zfill(4),
            "sensor": f"VIIRS {row.get('satellite', 'NOAA-20')}",
            "confidence": confidence(row.get("confidence")), "frp_mw": float(row.get("frp") or 0),
            "daynight": row.get("daynight"), "kabupaten": props.get("adm2_name"),
            "kabupaten_pcode": props.get("adm2_pcode"), "source_version": row.get("version"),
            "snapshot_id": "kalteng-2026-09-v1",
        },
    }


def cluster_key(feature):
    lon, lat = feature["geometry"]["coordinates"]
    date = dt.date.fromisoformat(feature["properties"]["acq_date"])
    # Transparent first-pass review unit: ~10 km cell and 3-day bucket, not an incident model.
    return (round(lat / 0.09), round(lon / 0.09), (date - START).days // 3)


def build_clusters(signals):
    groups = defaultdict(list)
    for signal in signals:
        groups[cluster_key(signal)].append(signal)
    output = []
    for index, key in enumerate(sorted(groups), 1):
        group = sorted(groups[key], key=lambda feature: (
            feature["properties"]["acq_date"],
            feature["properties"]["acq_time_utc"],
            feature["geometry"]["coordinates"][1],
            feature["geometry"]["coordinates"][0],
        ))
        coords = [f["geometry"]["coordinates"] for f in group]
        props = [f["properties"] for f in group]
        lon = sum(c[0] for c in coords) / len(coords)
        lat = sum(c[1] for c in coords) / len(coords)
        dates = sorted(p["acq_date"] for p in props)
        names = sorted({p["kabupaten"] for p in props if p["kabupaten"]})
        output.append({
            "type": "Feature", "id": f"KALTENG-202609-C{index:03d}",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {"cluster_id": f"KALTENG-202609-C{index:03d}", "snapshot_id": "kalteng-2026-09-v1",
                "signal_count": len(group), "high_confidence_count": sum(p["confidence"] == "high" for p in props),
                "first_seen_utc": f"{dates[0]}T00:00:00Z", "last_seen_utc": f"{dates[-1]}T23:59:59Z",
                "kabupaten": ", ".join(names), "review_status": "requires contextual review",
                "interpretation_note": "Satellite thermal-signal cluster; not a confirmed fire incident or burned-area boundary."},
        })
    return sorted(output, key=lambda f: (-f["properties"]["signal_count"], f["id"]))


def main():
    key = os.environ.get("FIRMS_MAP_KEY")
    if not key:
        raise SystemExit("FIRMS_MAP_KEY is required in the environment")
    OUT.mkdir(parents=True, exist_ok=True)
    boundaries = load_boundaries()
    signals, raw_count = [], 0
    day = START
    while day <= END:
        rows = fetch_day(key, day)
        raw_count += len(rows)
        for number, row in enumerate(rows, 1):
            feature = to_feature(row, number, boundaries)
            if feature:
                signals.append(feature)
        print(f"fetched {day.isoformat()}: {len(rows)} bounded rows")
        day += dt.timedelta(days=1)
        time.sleep(0.4)
    clusters = build_clusters(signals)
    display_signals = [feature for feature in signals if feature["properties"]["confidence"] == "high"]
    display_clusters = [feature for feature in clusters if feature["properties"]["signal_count"] >= 5]
    (OUT / "kalteng-admin2.geojson").write_text(json.dumps(feature_collection(boundaries), ensure_ascii=False), encoding="utf-8")
    (OUT / "signals.geojson").write_text(json.dumps(feature_collection(signals), ensure_ascii=False), encoding="utf-8")
    (OUT / "clusters.geojson").write_text(json.dumps(feature_collection(clusters), ensure_ascii=False), encoding="utf-8")
    (OUT / "signals-high.geojson").write_text(json.dumps(feature_collection(display_signals), ensure_ascii=False), encoding="utf-8")
    (OUT / "clusters-review.geojson").write_text(json.dumps(feature_collection(display_clusters), ensure_ascii=False), encoding="utf-8")
    meta = {"snapshot_id": "kalteng-2026-09-v1", "region": "Central Kalimantan, Indonesia", "period": [START.isoformat(), END.isoformat()], "source": SOURCE, "processing": "NRT snapshot; points clipped to HDX COD-AB Central Kalimantan boundary; review clusters use ~10 km grid cells and 3-day buckets.", "display_filters": {"signals_high_confidence_only": True, "clusters_minimum_signal_count": 5}, "counts": {"raw_bounded_rows": raw_count, "province_clipped_signals": len(signals), "review_clusters": len(clusters), "display_high_confidence_signals": len(display_signals), "display_review_clusters": len(display_clusters), "display_cluster_signals": sum(feature["properties"]["signal_count"] for feature in display_clusters)}, "limitations": "Thermal detections and derived clusters are not confirmed fire incidents, burned-area boundaries, cause, or response recommendations."}
    (OUT / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta["counts"]))


if __name__ == "__main__":
    main()
