#!/usr/bin/env python3
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

REFERENCE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_measurements.json'))

MODE_KEYS = ["a0_hz", "a1_hz", "b1_minus_hz", "b1_plus_hz", "cbr_hz"]
MODE_LABELS = {
    "a0_hz": "A0 (Helmholtz)",
    "a1_hz": "A1 (cavity)",
    "b1_minus_hz": "B1- (structural)",
    "b1_plus_hz": "B1+ (structural)",
    "cbr_hz": "CBR (structural)",
}


def load_reference(path=None):
    if path is None:
        path = REFERENCE_FILE
    with open(path) as f:
        return json.load(f)


def compute_correlation(ref_values, sim_values):
    if len(ref_values) < 3 or len(sim_values) < 3:
        return None
    n = len(ref_values)
    mean_r = sum(ref_values) / n
    mean_s = sum(sim_values) / n
    num = sum((r - mean_r) * (s - mean_s) for r, s in zip(ref_values, sim_values))
    den_r = math.sqrt(sum((r - mean_r) ** 2 for r in ref_values))
    den_s = math.sqrt(sum((s - mean_s) ** 2 for s in sim_values))
    if den_r == 0 or den_s == 0:
        return None
    return num / (den_r * den_s)


def compute_weighted_targets(entries):
    targets = {}
    total_weight = 0
    weighted_sum = {k: 0.0 for k in MODE_KEYS}
    for entry in entries:
        w = 1.0 / (entry.get("mass_g", 380.0) / 380.0)
        total_weight += w
        for k in MODE_KEYS:
            weighted_sum[k] += w * entry["modes"].get(k, 0.0)
    for k in MODE_KEYS:
        targets[k] = (weighted_sum[k] / total_weight) if total_weight > 0 and weighted_sum[k] > 0 else None
    return targets


def calibrate(entries, sim_mappings=None):
    report_lines = []
    report_lines.append("# Calibration Report")
    report_lines.append("")

    ref_masses = [e["mass_g"] for e in entries if e.get("mass_g")]
    avg_mass = sum(ref_masses) / len(ref_masses) if ref_masses else None
    report_lines.append(f"Reference entries: {len(entries)}")
    if avg_mass:
        report_lines.append(f"Average measured mass: {avg_mass:.1f}g")
    report_lines.append("")

    weighted_targets = compute_weighted_targets(entries)
    report_lines.append("## Calibrated Targets (mass-weighted mean of reference entries)")
    for k in MODE_KEYS:
        v = weighted_targets[k]
        report_lines.append(f"  target_{k}: {v:.1f} Hz" if v else f"  target_{k}: (no data)")
    report_lines.append("")

    report_lines.append("## Target Calibration vs Previous Defaults")
    previous = {"a0_hz": 290.0, "b1_minus_hz": 400.0, "b1_plus_hz": 540.0}
    for k, prev_val in previous.items():
        new_val = weighted_targets.get(k)
        if new_val:
            diff = new_val - prev_val
            report_lines.append(f"  {k}: {prev_val:.0f} -> {new_val:.1f} Hz ({diff:+.1f} Hz)")
    report_lines.append("")

    report_lines.append("## Per-Entry Mode Listing")
    report_lines.append(f"  {'ID':<25s} {'Mass':>7s} {'A0':>8s} {'A1':>8s} {'B1-':>8s} {'B1+':>8s} {'CBR':>8s}")
    report_lines.append(f"  {'-'*25} {'-'*7} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for entry in entries:
        m = entry["modes"]
        report_lines.append(
            f"  {entry['id']:<25s} {entry.get('mass_g',0):>7.0f} "
            f"{m.get('a0_hz',0):>8.1f} {m.get('a1_hz',0):>8.1f} "
            f"{m.get('b1_minus_hz',0):>8.1f} {m.get('b1_plus_hz',0):>8.1f} "
            f"{m.get('cbr_hz',0):>8.1f}"
        )

    if sim_mappings:
        report_lines.append("")
        report_lines.append("## Simulation vs Measurement Comparison")
        for sm in sim_mappings:
            entry = next((e for e in entries if e["id"] == sm["entry_id"]), None)
            if not entry:
                continue
            sim = sm["simulation"]
            ref = entry["modes"]
            report_lines.append(f"\n### {entry['id']}: {entry['label']}")
            report_lines.append(f"  {'Mode':<12s} {'Ref (Hz)':>10s} {'Sim (Hz)':>10s} {'Error (Hz)':>10s}")
            report_lines.append(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10}")
            for k in MODE_KEYS:
                r, s = ref.get(k), sim.get(k)
                if r and s:
                    report_lines.append(f"  {MODE_LABELS[k]:<12s} {r:>10.1f} {s:>10.1f} {s - r:>+10.1f}")

        report_lines.append("")
        report_lines.append("## Overall Correlation")
        all_ref, all_sim = [], []
        for sm in sim_mappings:
            entry = next((e for e in entries if e["id"] == sm["entry_id"]), None)
            if not entry:
                continue
            for k in MODE_KEYS:
                r, s = entry["modes"].get(k), sm["simulation"].get(k)
                if r and s:
                    all_ref.append(r)
                    all_sim.append(s)
        corr = compute_correlation(all_ref, all_sim)
        if corr is not None:
            report_lines.append(f"  Pearson r: {corr:.4f} ({'MEETS TARGET >= 0.8' if corr >= 0.8 else 'BELOW TARGET'})")
        else:
            report_lines.append("  Pearson r: insufficient data (< 3 paired points)")

    report_lines.append("")
    report_lines.append("## Weight Recommendations")
    report_lines.append("  Frequency error terms should dominate. Current defaults:")
    report_lines.append("    MASS_WEIGHT = 0.05 (score per gram)")
    report_lines.append("    MISSING_DATA_PENALTY = 1000.0 (per absent source)")
    report_lines.append("  If mass correlates strongly with frequency error, reduce MASS_WEIGHT.")
    report_lines.append("  If simulation frequently misses modes, increase MISSING_DATA_PENALTY.")

    return "\n".join(report_lines)


def main(ref_path=None, add_measurement=False, targets_only=False, sim_mappings=None):
    if ref_path is None:
        ref_path = REFERENCE_FILE
    ref = load_reference(ref_path)
    if add_measurement:
        print("Edit data/reference_measurements.json directly to add measurements.")
        return 1
    report = calibrate(ref["entries"], sim_mappings=sim_mappings)
    print(report)
    if targets_only:
        print("\n## Machine-readable targets")
        cal = compute_weighted_targets(ref["entries"])
        out = {"calibrated_targets": {k: round(cal[k], 1) for k in MODE_KEYS if cal[k]}}
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate objective targets against reference measurements")
    parser.add_argument("--reference", default=REFERENCE_FILE, help="Path to reference measurement JSON")
    parser.add_argument("--add-measurement", action="store_true", help="Prompt to add a new measurement")
    parser.add_argument("--targets-only", action="store_true", help="Only print calibrated targets in JSON")
    parser.add_argument("--sim-entry", action="append", nargs=2, metavar=("ENTRY_ID", "SIM_JSON"),
                        help="Simulation result for an entry (repeatable)")
    args = parser.parse_args()
    sim_mappings = []
    if args.sim_entry:
        for eid, sim_json in args.sim_entry:
            sim_mappings.append({"entry_id": eid, "simulation": json.loads(sim_json)})
    sys.exit(main(args.reference, args.add_measurement, args.targets_only, sim_mappings))
