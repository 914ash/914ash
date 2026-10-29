#!/usr/bin/env python3
"""Refresh observed U.S.-China frontier lag from the official Epoch ECI CSV.

Automated daily source ingestion. Changes to IFP policy model assumptions require
analyst review and must not be silently inferred from fresh news.
"""
from __future__ import annotations
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parents[1]
ECI_CSV = "https://epoch.ai/data/eci_scores.csv"
MONTH_DAYS = 365.25 / 12
BEGIN = dt.date(2024, 1, 1)
COUNTRIES = {"United States of America": "US", "China": "CN"}
CALIBRATION = 13 / math.log10(16)
CHINA_STOCK = {
    "2026": {"domestic": 1.729, "legal": .846, "smuggled": 1.004, "remote": 1.054277},
    "2027": {"domestic": 3.029, "legal": 1.346, "smuggled": 1.572, "remote": 2.834351},
}


def date_month(date: str) -> float:
    return (dt.date.fromisoformat(date) - BEGIN).days / MONTH_DAYS


def regression(records: list[dict]) -> dict:
    if len(records) < 6:
        raise ValueError("At least six distinct new frontier records required")
    x = [date_month(r["date"]) for r in records]
    y = [r["eci"] for r in records]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    denom = sum((v-mx) ** 2 for v in x)
    if denom == 0:
        raise ValueError("Repeated dates in frontier regression")
    m = sum((x[i]-mx) * (y[i]-my) for i in range(len(x))) / denom
    b = my - m * mx
    sse = sum((y[i]-m*x[i]-b) ** 2 for i in range(len(x)))
    sst = sum((v-my) ** 2 for v in y)
    if not (m > 0 and sst > 0):
        raise ValueError("Nonprogressing national model frontier")
    return {"slope": m, "intercept": b, "r2": 1 - sse/sst, "n": len(records)}


def record_frontier(records: list[dict]) -> list[dict]:
    """One best model per release date, then monotone increasing ECI record."""
    by_date = {}
    for r in records:
        d = r["date"]
        if d not in by_date or r["eci"] > by_date[d]["eci"]:
            by_date[d] = r
    best = -math.inf
    result = []
    for r in sorted(by_date.values(), key=lambda p: p["date"]):
        if r["eci"] > best:
            result.append(r)
            best = r["eci"]
    return result


def compile_snapshot(raw: str, checked: dt.datetime | None = None,
                     source_http_last_modified: str | None = None,
                     previous: dict | None = None) -> dict:
    checked = checked or dt.datetime.now(dt.timezone.utc)
    previous = previous or {}
    source_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if previous.get("sha256_source_csv") == source_sha:
        source_changed = previous.get("source_changed_at_utc") or previous.get("retrieved_at_utc")
    else:
        source_changed = checked.isoformat(timespec="seconds")
    reader = csv.DictReader(io.StringIO(raw))
    required = {"Model", "date", "eci", "eci_ci_low", "eci_ci_high", "Country (of organization)", "Organization"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        raise ValueError(f"ECI source schema changed; expected {required}; received {reader.fieldnames}")
    data = {"US": [], "CN": []}
    count = 0
    for item in reader:
        count += 1
        country = COUNTRIES.get(item.get("Country (of organization)", "").strip())
        if not country:
            continue
        try:
            release = dt.date.fromisoformat(item["date"])
            eci = float(item["eci"])
            low = float(item["eci_ci_low"])
            high = float(item["eci_ci_high"])
        except (ValueError, TypeError):
            continue
        if (release < BEGIN or release > checked.date()
                or not math.isfinite(eci) or not 0 < eci < 400 or not low <= eci <= high):
            continue
        data[country].append({
            "date": release.isoformat(), "eci": eci,
            "name": item["Model"], "org": item["Organization"],
            "lo": low, "hi": high,
        })
    if count < 100:
        raise ValueError(f"ECI feed incomplete: only {count} rows")
    regions = {}
    for country in ("US", "CN"):
        points = record_frontier(data[country])
        fit = regression(points)
        if fit["r2"] < .7:
            raise ValueError(f"{country}: abnormal regression fit; review new data or definitions")
        regions[country] = {
            "frontier": points, "fit": fit,
            "models_in_scope": len(data[country]),
            "latest_release": max(p["date"] for p in data[country])
        }
    target = regions["CN"]["frontier"][-1]["eci"]
    us, cn = regions["US"]["fit"], regions["CN"]["fit"]
    lag = ((target - cn["intercept"]) / cn["slope"]
           - (target - us["intercept"]) / us["slope"])
    if not -24 < lag < 48:
        raise ValueError(f"Computed lag {lag} months outside review thresholds")
    return {
        "retrieved_at_utc": checked.isoformat(timespec="seconds"),
        "source_content_last_changed_at_utc": source_changed,
        "source_http_last_modified": source_http_last_modified,
        "source_url": ECI_CSV,
        "sha256_source_csv": source_sha,
        "total_rows": count,
        "observed": {
            "lead_months": lag, "target_china_eci": target,
            "regions": regions,
            "method": "Unweighted OLS per record-setting release day since January 2024; horizontal lag at newest Chinese frontier ECI."
        },
        "ifp": {
            "published": "2026-10-19", "reported_lag_months": 6.5,
            "training_compute_ratio": 16, "distillation_share": 0.5,
            "K": CALIBRATION, "china_stock_h100e_millions": CHINA_STOCK,
            "source_url": "https://ifp.org/how-to-increase-americas-ai-lead-over-china/",
            "status": "Unrefreshed original paper's estimates, not observations."
        }
    }


def read_source() -> str:
    req = urllib.request.Request(
        ECI_CSV,
        headers={"User-Agent": "AIFrontierMonitor/1.0 (public research dashboard; Epoch AI credited)"}
    )
    with urllib.request.urlopen(req, timeout=55) as response:
        body = response.read(10_000_000)
        source_http_last_modified = response.headers.get("Last-Modified")
    if not body or len(body) > 9_900_000:
        raise ValueError("Source missing or unexpectedly large")
    return body.decode("utf-8-sig"), source_http_last_modified


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Use local CSV as a test fixture")
    parser.add_argument("--out", default=str(BASE / "data/latest.json"))
    args = parser.parse_args()
    dest = Path(args.out)
    previous = {}
    if dest.exists():
        try:
            previous = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    raw, last_modified = ((Path(args.csv).read_text(encoding="utf-8"), None)
                          if args.csv else read_source())
    result = compile_snapshot(raw, source_http_last_modified=last_modified, previous=previous)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_suffix(".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    os.replace(temporary, dest)
    print("Recalculated %.3f months from %d rows as of %s"
          % (result["observed"]["lead_months"], result["total_rows"], result["retrieved_at_utc"]))


if __name__ == "__main__":
    main()
