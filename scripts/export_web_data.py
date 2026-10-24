import json
from pathlib import Path

# Load real artifacts
with open("artifacts/alerts/alerts.json", encoding="utf-8") as f:
    alerts = json.load(f)

with open("artifacts/evaluation/evaluation_report.json", encoding="utf-8") as f:
    eval_report = json.load(f)

with open("artifacts/alerts/attribution_results.json", encoding="utf-8") as f:
    attrs = json.load(f)

abstentions = [a for a in attrs if a.get("attribution_status") == "INSUFFICIENT_EVIDENCE"]

# Generate time-series profiles for interactive canvas curves
# 1. Normal session (healthy CC/CV)
normal_curve = []
for t in range(0, 61):  # 60 minutes
    soc = min(100.0, 15.0 + t * 1.4)
    if soc < 80.0:  # CC phase
        i_cmd = 15.0
        i_dock = 15.0 + ((t % 3) - 1) * 0.05
        i_pack = i_dock
        v_pack = 44.0 + (soc / 80.0) * 8.0
        temp_c = 25.0 + (t / 60.0) * 7.5
        cell_spread_mv = 12.0 + ((t % 5) * 1.2)
    else:  # CV phase taper
        i_cmd = max(1.5, 15.0 * (1.0 - (soc - 80.0) / 20.0))
        i_dock = i_cmd
        i_pack = i_dock
        v_pack = 52.0
        temp_c = 32.5 - (t - 45) * 0.15
        cell_spread_mv = 14.0
    normal_curve.append({
        "minute": t,
        "soc": round(soc, 1),
        "cmd_current_a": round(i_cmd, 2),
        "dock_current_a": round(i_dock, 2),
        "pack_current_a": round(i_pack, 2),
        "pack_voltage_v": round(v_pack, 2),
        "temp_c": round(temp_c, 1),
        "cell_spread_mv": round(cell_spread_mv, 1)
    })

# 2. Dock current clipping fault (STA-04-DOK-01)
dock_fault_curve = []
for t in range(0, 61):
    soc = min(100.0, 15.0 + t * 0.75)
    i_cmd = 15.0
    i_dock = 8.0 + ((t % 2) - 0.5) * 0.1  # Severely clipped at 8A
    i_pack = i_dock
    v_pack = 44.0 + (soc / 100.0) * 7.0
    temp_c = 25.0 + (t / 60.0) * 4.0
    cell_spread_mv = 14.0
    dock_fault_curve.append({
        "minute": t,
        "soc": round(soc, 1),
        "cmd_current_a": round(i_cmd, 2),
        "dock_current_a": round(i_dock, 2),
        "pack_current_a": round(i_pack, 2),
        "pack_voltage_v": round(v_pack, 2),
        "temp_c": round(temp_c, 1),
        "cell_spread_mv": round(cell_spread_mv, 1)
    })

# 3. Pack abnormal self-heating fault (STA-04-PCK-017)
pack_fault_curve = []
for t in range(0, 61):
    soc = min(100.0, 15.0 + t * 1.35)
    i_cmd = 15.0 if t < 35 else 9.5  # BMS throttles at t=35 due to heat
    i_dock = i_cmd
    i_pack = i_cmd
    v_pack = 44.5 + (soc / 80.0) * 7.5
    temp_c = 26.0 + (t * 0.72)  # Escalates to ~51°C
    cell_spread_mv = 24.0
    pack_fault_curve.append({
        "minute": t,
        "soc": round(soc, 1),
        "cmd_current_a": round(i_cmd, 2),
        "dock_current_a": round(i_dock, 2),
        "pack_current_a": round(i_pack, 2),
        "pack_voltage_v": round(v_pack, 2),
        "temp_c": round(temp_c, 1),
        "cell_spread_mv": round(cell_spread_mv, 1)
    })

# 4. Cell voltage divergence (STA-04-PCK-017)
cell_fault_curve = []
for t in range(0, 61):
    soc = min(100.0, 15.0 + t * 1.2)
    i_cmd = 15.0 if t < 25 else 7.0  # Cell hit cutoff voltage early
    i_dock = i_cmd
    i_pack = i_cmd
    v_pack = 44.0 + (soc / 80.0) * 8.2
    temp_c = 25.5 + (t / 60.0) * 6.0
    cell_spread_mv = 18.0 + (t * 2.8)  # Spreads to 186 mV!
    cell_fault_curve.append({
        "minute": t,
        "soc": round(soc, 1),
        "cmd_current_a": round(i_cmd, 2),
        "dock_current_a": round(i_dock, 2),
        "pack_current_a": round(i_pack, 2),
        "pack_voltage_v": round(v_pack, 2),
        "temp_c": round(temp_c, 1),
        "cell_spread_mv": round(cell_spread_mv, 1)
    })

# 5. Environment heat derate (STA-04)
env_fault_curve = []
for t in range(0, 61):
    soc = min(100.0, 15.0 + t * 0.9)
    i_cmd = 10.0  # Pre-derated due to ambient 39°C
    i_dock = 10.0
    i_pack = 10.0
    v_pack = 44.0 + (soc / 80.0) * 8.0
    temp_c = 38.5 + (t / 60.0) * 8.0  # Starts hot (ambient 38.5°C)
    cell_spread_mv = 15.0
    env_fault_curve.append({
        "minute": t,
        "soc": round(soc, 1),
        "cmd_current_a": round(i_cmd, 2),
        "dock_current_a": round(i_dock, 2),
        "pack_current_a": round(i_pack, 2),
        "pack_voltage_v": round(v_pack, 2),
        "temp_c": round(temp_c, 1),
        "cell_spread_mv": round(cell_spread_mv, 1)
    })

web_data = {
    "alerts": alerts,
    "evalReport": eval_report,
    "abstentions": abstentions[:15],  # 15 representative abstention examples
    "abstentionTotal": len(abstentions),
    "curves": {
        "normal": normal_curve,
        "dock_fault": dock_fault_curve,
        "pack_fault": pack_fault_curve,
        "cell_fault": cell_fault_curve,
        "env_fault": env_fault_curve,
    },
    "stations": [
        {"id": "STA-01", "name": "Taipei Central Hub", "docks": 4, "status": "NOMINAL", "ambient_c": 26.2, "grid_v": 220.4},
        {"id": "STA-02", "name": "New Taipei Industrial Station", "docks": 4, "status": "NOMINAL", "ambient_c": 27.1, "grid_v": 219.8},
        {"id": "STA-03", "name": "Taoyuan Logistics Corridor", "docks": 4, "status": "NOMINAL", "ambient_c": 28.0, "grid_v": 221.1},
        {"id": "STA-04", "name": "Hsinchu Tech Interchange", "docks": 4, "status": "ATTENTION_REQUIRED", "ambient_c": 38.5, "grid_v": 218.6},
    ],
    "crossingExamples": {
        "dock_isolation": {
            "title": "Dock Current Deficit Follows Dock Across 4 Independent Packs",
            "dockId": "STA-04-DOK-01",
            "sessions": [
                {"packId": "PCK-001", "dockId": "STA-04-DOK-01", "current_a": 8.0, "cmd_a": 15.0, "is_anomaly": True},
                {"packId": "PCK-017", "dockId": "STA-04-DOK-01", "current_a": 8.0, "cmd_a": 15.0, "is_anomaly": True},
                {"packId": "PCK-042", "dockId": "STA-04-DOK-01", "current_a": 7.9, "cmd_a": 15.0, "is_anomaly": True},
                {"packId": "PCK-078", "dockId": "STA-04-DOK-01", "current_a": 8.1, "cmd_a": 15.0, "is_anomaly": True},
                # Counterfactuals: same packs on OTHER docks charge normally
                {"packId": "PCK-001", "dockId": "STA-01-DOK-02", "current_a": 14.9, "cmd_a": 15.0, "is_anomaly": False},
                {"packId": "PCK-042", "dockId": "STA-02-DOK-03", "current_a": 15.0, "cmd_a": 15.0, "is_anomaly": False},
            ],
            "conclusion": "Attributed to CHARGER_DOCK with HIGH confidence. All 4 packs underperform on DOK-01, but behave normally when swapped to other docks."
        },
        "pack_isolation": {
            "title": "Pack Thermal Anomaly Follows Battery Across 3 Independent Docks",
            "packId": "STA-04-PCK-017",
            "sessions": [
                {"packId": "STA-04-PCK-017", "dockId": "STA-04-DOK-01", "temp_max_c": 51.4, "temp_expected_c": 34.0, "is_anomaly": True},
                {"packId": "STA-04-PCK-017", "dockId": "STA-04-DOK-02", "temp_max_c": 50.8, "temp_expected_c": 33.5, "is_anomaly": True},
                {"packId": "STA-04-PCK-017", "dockId": "STA-01-DOK-04", "temp_max_c": 52.1, "temp_expected_c": 32.8, "is_anomaly": True},
                # Counterfactuals: other packs on those same docks remain cool
                {"packId": "PCK-005", "dockId": "STA-04-DOK-02", "temp_max_c": 32.4, "temp_expected_c": 33.5, "is_anomaly": False},
                {"packId": "PCK-029", "dockId": "STA-01-DOK-04", "temp_max_c": 31.9, "temp_expected_c": 32.8, "is_anomaly": False},
            ],
            "conclusion": "Attributed to PACK with HIGH confidence. Severe thermal excess (+18°C) persists regardless of dock assignment; docks charge other packs normally."
        },
        "abstention_case": {
            "title": "Low Crossing Count (Single Dock Observation) Triggers Safe Abstention",
            "packId": "PCK-088",
            "dockId": "STA-03-DOK-02",
            "crossing": 1,
            "min_required": 2,
            "symptom": "Charging current delivery 11.2A vs 15.0A commanded (deficit 3.8A)",
            "status": "INSUFFICIENT_EVIDENCE",
            "explanation": "Pack PCK-088 observed on only 1 dock. Cannot distinguish whether the current deficit originates from dock hardware degradation or pack BMS impedance limiting. Alert suppressed until crossover observation."
        }
    }
}

Path("web").mkdir(exist_ok=True)
with open("web/data.js", "w", encoding="utf-8") as f:
    f.write("window.SWAPTRACE_DATA = " + json.dumps(web_data, indent=2) + ";\n")

# Keep the React console's data module in sync with the same artifacts
Path("src/data").mkdir(parents=True, exist_ok=True)
with open("src/data/telemetryData.js", "w", encoding="utf-8") as f:
    f.write("export const telemetryData = " + json.dumps(web_data, indent=2) + ";\n")
    f.write("export default telemetryData;\n")

print("Generated web/data.js and src/data/telemetryData.js successfully!")
