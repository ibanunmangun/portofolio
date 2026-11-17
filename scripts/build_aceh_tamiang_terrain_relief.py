#!/usr/bin/env python3
"""Build a local Copernicus DEM hillshade reference overlay for Aceh Tamiang."""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "aceh-tamiang-flood" / "processed"
RAW = ROOT / "data" / "aceh-tamiang-flood" / "raw" / "copernicus-dem-glo-30"
CONTEXT = PROCESSED / "aceh-tamiang-admin3.geojson"
OUTPUT = PROCESSED / "terrain-hillshade.png"
WORK = ROOT / ".cache" / "aceh-terrain-relief"
BUFFER_KM = 15
SOURCE_BASE = "https://copernicus-dem-30m.s3.amazonaws.com"
SOURCE_VERSION = "Copernicus DEM GLO-30, COG 10 degree tiles"
ATTRIBUTION = (
    "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and "
    "Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved."
)


def run(*command: str) -> None:
    subprocess.run(command, check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coordinates(value: object):
    if isinstance(value, list) and value and isinstance(value[0], (int, float)):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from coordinates(child)


def buffered_bounds() -> tuple[float, float, float, float]:
    data = json.loads(CONTEXT.read_text(encoding="utf-8"))
    pairs = [pair for feature in data["features"] for pair in coordinates(feature["geometry"]["coordinates"])]
    min_lon, max_lon = min(pair[0] for pair in pairs), max(pair[0] for pair in pairs)
    min_lat, max_lat = min(pair[1] for pair in pairs), max(pair[1] for pair in pairs)
    center_lat = (min_lat + max_lat) / 2
    latitude_degrees = BUFFER_KM / 110.574
    longitude_degrees = BUFFER_KM / (111.320 * math.cos(math.radians(center_lat)))
    return (
        min_lon - longitude_degrees,
        min_lat - latitude_degrees,
        max_lon + longitude_degrees,
        max_lat + latitude_degrees,
    )


def tiles_for(bounds: tuple[float, float, float, float]) -> list[tuple[int, int]]:
    min_lon, min_lat, max_lon, max_lat = bounds
    return [
        (latitude, longitude)
        for latitude in range(math.floor(min_lat), math.floor(max_lat) + 1)
        for longitude in range(math.floor(min_lon), math.floor(max_lon) + 1)
    ]


def tile_path(latitude: int, longitude: int) -> tuple[Path, str]:
    lat_part = f"N{latitude:02d}" if latitude >= 0 else f"S{abs(latitude):02d}"
    lon_part = f"E{longitude:03d}" if longitude >= 0 else f"W{abs(longitude):03d}"
    stem = f"Copernicus_DSM_COG_10_{lat_part}_00_{lon_part}_00_DEM"
    return RAW / f"{stem}.tif", f"{SOURCE_BASE}/{stem}/{stem}.tif"


def fetch_tiles(bounds: tuple[float, float, float, float]) -> list[Path]:
    RAW.mkdir(parents=True, exist_ok=True)
    output = []
    for latitude, longitude in tiles_for(bounds):
        path, url = tile_path(latitude, longitude)
        if not path.exists():
            print(f"download={url}")
            urllib.request.urlretrieve(url, path)
        output.append(path)
    return output


def main() -> None:
    if not CONTEXT.is_file():
        raise SystemExit(f"Missing context geometry: {CONTEXT}")
    for binary in ("gdalbuildvrt", "gdalwarp", "gdaldem", "gdal_translate", "gdalinfo"):
        if not shutil.which(binary):
            raise SystemExit(f"Required GDAL executable missing: {binary}")
    bounds = buffered_bounds()
    tiles = fetch_tiles(bounds)
    WORK.mkdir(parents=True, exist_ok=True)
    vrt = WORK / "terrain.vrt"
    warped = WORK / "terrain-webmercator.tif"
    hillshade = WORK / "terrain-hillshade.tif"
    run("gdalbuildvrt", "-overwrite", str(vrt), *(str(tile) for tile in tiles))
    min_lon, min_lat, max_lon, max_lat = (f"{value:.9f}" for value in bounds)
    run(
        "gdalwarp", "-overwrite", "-t_srs", "EPSG:3857", "-te_srs", "EPSG:4326",
        "-te", min_lon, min_lat, max_lon, max_lat, "-tr", "100", "100", "-r", "bilinear",
        "-dstnodata", "0", "-co", "COMPRESS=DEFLATE", str(vrt), str(warped),
    )
    run("gdaldem", "hillshade", "-multidirectional", "-compute_edges", str(warped), str(hillshade), "-co", "COMPRESS=DEFLATE")
    run("gdal_translate", "-of", "PNG", "-ot", "Byte", "-scale", "0", "255", "32", "220", str(hillshade), str(OUTPUT))
    OUTPUT.with_suffix(".png.aux.xml").unlink(missing_ok=True)
    info = json.loads(subprocess.check_output(["gdalinfo", "-json", str(OUTPUT)], text=True))
    width, height = info["size"]
    metadata_path = PROCESSED / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["satellite_reference"] = {
        "role": "Optional reference imagery, not event-date flood evidence.",
        "provider": "NASA Global Imagery Browse Services (GIBS)",
        "product_id": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "fixed_date": "2026-11-16",
        "tile_endpoint": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2026-11-16/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg",
        "acknowledgement": "We acknowledge the use of imagery provided by services from NASA's Global Imagery Browse Services (GIBS), part of NASA's Earth Science Data and Information System (ESDIS).",
        "default_enabled": False,
    }
    metadata["terrain_relief"] = {
        "role": "Reference terrain context, not flood evidence.",
        "source": "Copernicus WorldDEM-30 GLO-30",
        "source_version": SOURCE_VERSION,
        "source_urls": [tile_path(lat, lon)[1] for lat, lon in tiles_for(bounds)],
        "source_tile_sha256": {path.name: sha256(path) for path in tiles},
        "attribution": ATTRIBUTION,
        "buffer_km": BUFFER_KM,
        "bounds_wgs84": [round(value, 9) for value in bounds],
        "processing": "Web Mercator reprojection at 100 m pixels, then GDAL multidirectional hillshade with compute_edges; PNG display scale 32-220.",
        "output": "terrain-hillshade.png",
        "pixel_dimensions": {"width": width, "height": height},
        "byte_size": OUTPUT.stat().st_size,
        "sha256": sha256(OUTPUT),
    }
    metadata["limitations"] = list(dict.fromkeys(metadata["limitations"] + [
        "Terrain relief is a general reference context derived from a Copernicus digital surface model and is not flood evidence.",
    ]))
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"terrain_bounds_wgs84={','.join(f'{value:.9f}' for value in bounds)}")
    print(f"terrain_pixels={width}x{height}")
    print(f"terrain_hillshade_sha256={sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
