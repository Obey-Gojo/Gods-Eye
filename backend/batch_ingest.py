import argparse
import json
import os
import sys
import time
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def calculate_contributor_risk(results: list[dict]) -> dict:
    """Computes aggregate compliance metrics and forensic risk rollup."""
    total = len(results)
    if total == 0:
        return {"risk_score": 0.0, "risk_level": "LOW", "compliance_rate": "0%"}

    breakdown = {
        "VERIFIED": 0,
        "DUPLICATE ASSET": 0,
        "PLAGIARISM ALERT": 0,
        "IMAGE TAMPERED": 0,
        "DATA POISONED": 0,
        "MODEL COMPROMISED": 0,
        "INFERENCE TAMPERED": 0,
        "NON-COMPLIANT ASSET": 0,
        "FAILED_REQUEST": 0,
    }

    for r in results:
        st = r.get("status", "FAILED_REQUEST")
        breakdown[st] = breakdown.get(st, 0) + 1

    compliance_rate = round((breakdown["VERIFIED"] / total) * 100, 1)

    penalty = (
        (breakdown.get("PLAGIARISM ALERT", 0) * 30.0)
        + (breakdown.get("IMAGE TAMPERED", 0) * 25.0)
        + (breakdown.get("DATA POISONED", 0) * 35.0)
        + (breakdown.get("MODEL COMPROMISED", 0) * 40.0)
        + (breakdown.get("INFERENCE TAMPERED", 0) * 25.0)
        + (breakdown.get("DUPLICATE ASSET", 0) * 10.0)
        + (breakdown.get("NON-COMPLIANT ASSET", 0) * 5.0)
    )
    raw_score = min(100.0, penalty)

    if raw_score >= 60.0:
        risk_level = "CRITICAL"
    elif raw_score >= 30.0:
        risk_level = "ELEVATED"
    elif raw_score > 0.0:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW / TRUSTED"

    return {
        "total_assets": total,
        "compliance_rate": f"{compliance_rate}%",
        "threat_penalty_score": round(raw_score, 1),
        "risk_level": risk_level,
        "status_distribution": breakdown,
    }


def ingest_folder(folder_path: str, contributor: str, output_report: str = None):
    if not os.path.exists(folder_path):
        print(f"[!] Error: Directory '{folder_path}' does not exist.")
        sys.exit(1)

    candidate_files = [
        f for f in sorted(os.listdir(folder_path))
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
        and not f.startswith("batch_audit_")
    ]

    if not candidate_files:
        print(f"[!] No valid image assets found in '{folder_path}'.")
        sys.exit(1)

    print("=" * 70)
    print(f"GOD'S EYE BATCH INGESTION ENGINE")
    print(f"Target Directory: {os.path.abspath(folder_path)}")
    print(f"Submitting Contributor: {contributor}")
    print(f"Total Assets Queued: {len(candidate_files)}")
    print("=" * 70)

    batch_results = []
    t_start = time.time()

    for idx, fname in enumerate(candidate_files, 1):
        fpath = os.path.join(folder_path, fname)
        print(f"[{idx:03d}/{len(candidate_files):03d}] Processing: {fname:<30}", end="", flush=True)

        try:
            with open(fpath, "rb") as f_data:
                file_bytes = f_data.read()
        except Exception as e:
            print(f" -> \033[91mFILE READ ERROR: {e}\033[0m")
            continue

        try:
            files = {"file": (fname, file_bytes, "image/jpeg")}
            data = {"contributor": contributor}

            t_req = time.time()
            resp = requests.post(f"{API_URL}/process-pipeline", files=files, data=data)
            req_latency = round((time.time() - t_req) * 1000, 1)

            if resp.status_code == 200:
                payload = resp.json()
                status = payload.get("status", "UNKNOWN")
                pred = payload.get("prediction", "N/A")
                conf = payload.get("confidence", "0%")
                tx = payload.get("blockchain_tx", "N/A")

                batch_results.append({
                    "filename": fname,
                    "status": status,
                    "is_trusted": payload.get("is_trusted", False),
                    "prediction": pred,
                    "confidence": conf,
                    "tx_hash": tx,
                    "bound_digest": payload.get("bound_digest", "N/A"),
                    "checks": payload.get("checks", {}),
                    "latency_ms": req_latency,
                })

                flag_color = "\033[92m" if status == "VERIFIED" else "\033[91m"
                reset_color = "\033[0m"
                print(f" -> {flag_color}{status:<20}{reset_color} ({pred} {conf}) [{req_latency}ms]")
            else:
                err_detail = resp.text[:120].replace("\n", " ")
                print(f" -> \033[91mHTTP {resp.status_code}: {err_detail}\033[0m")
                batch_results.append({
                    "filename": fname,
                    "status": f"HTTP_{resp.status_code}",
                    "is_trusted": False,
                    "latency_ms": req_latency,
                })
        except Exception as ex:
            print(f" -> \033[91mEXCEPTION: {ex}\033[0m")
            batch_results.append({
                "filename": fname,
                "status": "CONNECTION_ERROR",
                "is_trusted": False,
                "latency_ms": 0,
            })

    total_duration = round(time.time() - t_start, 2)
    risk_summary = calculate_contributor_risk(batch_results)

    print("\n" + "=" * 70)
    print("INGESTION TELEMETRY SUMMARY")
    print("=" * 70)
    print(f"Elapsed Runtime:        {total_duration}s")
    print(f"Throughput:             {round(len(candidate_files)/max(total_duration, 0.01), 2)} assets/sec")
    print(f"Compliance Ratio:       {risk_summary['compliance_rate']}")
    print(f"Risk Rating:            {risk_summary['risk_level']} (Penalty Index: {risk_summary['threat_penalty_score']})")
    print("-" * 70)
    print("Status Breakdown:")
    for stat, count in risk_summary["status_distribution"].items():
        if count > 0:
            print(f"  • {stat:<25}: {count}")
    print("=" * 70)

    if not output_report:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_report = os.path.join(folder_path, f"batch_audit_{timestamp_str}.json")

    report_data = {
        "metadata": {
            "execution_timestamp": datetime.now().isoformat(),
            "target_directory": os.path.abspath(folder_path),
            "contributor": contributor,
            "total_runtime_seconds": total_duration,
        },
        "risk_summary": risk_summary,
        "asset_evaluations": batch_results,
    }

    with open(output_report, "w") as f_out:
        json.dump(report_data, f_out, indent=4)

    print(f"[✔] Batch audit ledger exported to: {output_report}\n")
    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="God's Eye Bulk Dataset Ingestion Utility")
    parser.add_argument("--dir", required=True, help="Absolute or relative path to image directory")
    parser.add_argument("--contributor", required=True, help="Agency or Contributor submitting batch")
    parser.add_argument("--output", default=None, help="Path to write output audit JSON")
    args = parser.parse_args()

    ingest_folder(args.dir, args.contributor, args.output)