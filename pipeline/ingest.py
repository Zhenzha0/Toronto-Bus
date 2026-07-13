"""Ingestion stage.

Resolve the current download URLs from the CKAN API, download the GTFS ZIP
and the yearly delay files into data/raw, unzip the GTFS tables, and write a
manifest.json describing everything that was fetched.
"""

import hashlib
import json
import re
import zipfile

import requests

import config

# Matches the historical yearly delay resources, e.g. "ttc-bus-delay-data-2019".
_YEARLY_RE = re.compile(r"ttc-bus-delay-data-(\d{4})$", re.IGNORECASE)


def ckan_package(slug):
    """Fetch a dataset's metadata (including its resource list) from CKAN."""
    url = config.CKAN_HOST + "/api/3/action/package_show"
    resp = requests.get(url, params={"id": slug}, timeout=30)
    resp.raise_for_status()          # turn any HTTP error into an exception
    return resp.json()["result"]


def _pick_gtfs(resources):
    """The routes/schedules dataset has a single ZIP resource; return it."""
    for res in resources:
        if (res.get("format") or "").upper() == "ZIP":
            return res
    raise RuntimeError("No ZIP resource found in the GTFS dataset")


def _pick_delay(resources, years):
    """Choose one delay resource per requested year.

    2014-2024 are yearly XLSX files. 2025 onward is a rolling file, which we
    take as CSV (simpler than XLSX and it carries a last_modified timestamp).
    """
    by_year = {}
    for res in resources:
        name = res.get("name") or ""
        match = _YEARLY_RE.match(name)
        if match:
            by_year[int(match.group(1))] = res
        elif name == "TTC Bus Delay Data since 2025.csv":
            by_year[2025] = res
    # Keep only the requested years, in order.
    return [(year, by_year[year]) for year in years if year in by_year]


def selected_resources():
    """Return the resources to ingest as a list of (dataset, year, resource).

    dataset is "gtfs" or "delay"; year is None for GTFS, else the delay year.
    """
    years = config.DELAY_YEARS_FULL if config.FULL_LOAD else config.SAMPLE_YEARS

    gtfs_pkg = ckan_package(config.DATASET_GTFS)
    delay_pkg = ckan_package(config.DATASET_DELAY)

    plan = [("gtfs", None, _pick_gtfs(gtfs_pkg["resources"]))]
    for year, res in _pick_delay(delay_pkg["resources"], years):
        plan.append(("delay", year, res))
    return plan


def _target_path(dataset, year, res):
    """Where a resource's file should land in data/raw."""
    fmt = (res.get("format") or "bin").lower()
    if dataset == "gtfs":
        return config.RAW_DIR / "gtfs.zip"
    return config.RAW_DIR / f"delay_{year}.{fmt}"


def download_resource(res, dest_path):
    """Stream a resource's file to dest_path; return its SHA-256 checksum."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256()
    with requests.get(res["url"], stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
                sha.update(chunk)     # feed each chunk into the running fingerprint
    return sha.hexdigest()


def unzip_gtfs(zip_path, dest_dir):
    """Extract the GTFS .txt tables from the ZIP into dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    return sorted(p.name for p in dest_dir.iterdir())


def _write_manifest(entries):
    """Record what was fetched (for the bronze loader and for lineage)."""
    path = config.RAW_DIR / "manifest.json"
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    print(f"wrote {path.name} ({len(entries)} resources)")


def run():
    """Download every selected resource into data/raw and write a manifest."""
    entries = []
    for dataset, year, res in selected_resources():
        dest = _target_path(dataset, year, res)
        print(f"downloading {res['name']!r} -> {dest.name}")
        checksum = download_resource(res, dest)

        entry = {
            "dataset": dataset,
            "year": year,
            "resource_id": res.get("id"),
            "name": res.get("name"),
            "format": (res.get("format") or "").upper(),
            "url": res.get("url"),
            "last_modified": res.get("last_modified"),
            "checksum": checksum,
            "path": dest.relative_to(config.PROJECT_ROOT).as_posix(),
        }
        if dataset == "gtfs":
            files = unzip_gtfs(dest, config.RAW_DIR / "gtfs")
            entry["gtfs_files"] = files
            print(f"  unzipped {len(files)} files")
        entries.append(entry)

    _write_manifest(entries)
    return entries

