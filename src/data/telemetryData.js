export const telemetryData = {
  "alerts": [
    {
      "alert_id": "b01adece-fe6e-4075-832b-ab768eda9d12",
      "episode_key": "CHARGER_DOCK:STA-04-DOK-01:cell_voltage_dispersion_excess",
      "owner_category": "CHARGER_DOCK",
      "owner_team": "charging_infrastructure",
      "entity_id": "STA-04-DOK-01",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "cell_voltage_dispersion_excess"
      ],
      "observed_value": 0.014191512681343887,
      "expected_value": 0.00018538197345274732,
      "observed_unit": "V",
      "residual_normalized": 297.5351368105646,
      "evidence": [
        {
          "description": "Dock STA-02-DOK-04 has served 20 independent packs",
          "entity_id": "STA-02-DOK-04",
          "session_ids": [],
          "count": 20
        },
        {
          "description": "Pack STA-02-PCK-006 shows normal behavior on other docks",
          "entity_id": "STA-02-PCK-006",
          "session_ids": [],
          "count": 3
        },
        {
          "description": "Sibling docks at station show no similar anomaly",
          "entity_id": "STA-02",
          "session_ids": [],
          "count": 3
        },
        {
          "description": "19 other pack(s) showed the same dock-feature anomaly at STA-02-DOK-04 \u2014 anomaly follows the dock",
          "entity_id": "STA-02-DOK-04",
          "session_ids": [],
          "count": 19
        },
        {
          "description": "Feature cell_voltage_dispersion_excess anomaly: observed=0.014V, expected=0.000V, z-score=297.54",
          "entity_id": "STA-04-DOK-01",
          "session_ids": [
            "SES-20260910182857-CK-006-K-04",
            "SES-20260910195635-CK-006-K-04",
            "SES-20260914154728-CK-006-K-04",
            "SES-20260914171051-CK-006-K-04"
          ],
          "count": 4
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "dock_independent_packs": 20
      },
      "recommended_actions": [
        "Inspect dock control circuitry and power delivery hardware",
        "Test contact pins and connector path resistance"
      ],
      "explanation": "Evidence supports CHARGER_DOCK: 20 independent packs affected at dock STA-02-DOK-04; pack STA-02-PCK-006 is normal elsewhere. | Concurrent anomalies across multiple components detected; confidence capped at MEDIUM.",
      "first_seen_ts": "2026-09-10T19:56:35.622681Z",
      "last_seen_ts": "2026-09-14T17:10:51.833806Z",
      "opened_at": "2026-10-24T14:13:33.991291Z",
      "occurrence_count": 4,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260910182857-CK-006-K-04",
        "SES-20260910195635-CK-006-K-04",
        "SES-20260914154728-CK-006-K-04",
        "SES-20260914171051-CK-006-K-04"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "d58980bd-ef57-4565-8e1f-8288f5aef8f2",
      "episode_key": "CHARGER_DOCK:STA-04-DOK-01:dock_contact_resistance_excess",
      "owner_category": "CHARGER_DOCK",
      "owner_team": "charging_infrastructure",
      "entity_id": "STA-04-DOK-01",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "dock_contact_resistance_excess"
      ],
      "observed_value": 80.00000000000024,
      "expected_value": 0.0,
      "observed_unit": "m\u03a9",
      "residual_normalized": 4.957424080290317,
      "evidence": [
        {
          "description": "Dock STA-02-DOK-04 has served 20 independent packs",
          "entity_id": "STA-02-DOK-04",
          "session_ids": [],
          "count": 20
        },
        {
          "description": "Pack STA-02-PCK-010 shows normal behavior on other docks",
          "entity_id": "STA-02-PCK-010",
          "session_ids": [],
          "count": 3
        },
        {
          "description": "Sibling docks at station show no similar anomaly",
          "entity_id": "STA-02",
          "session_ids": [],
          "count": 3
        },
        {
          "description": "19 other pack(s) showed the same dock-feature anomaly at STA-02-DOK-04 \u2014 anomaly follows the dock",
          "entity_id": "STA-02-DOK-04",
          "session_ids": [],
          "count": 19
        },
        {
          "description": "Feature dock_contact_resistance_excess anomaly: observed=80.000m\u03a9, expected=0.000m\u03a9, z-score=4.96",
          "entity_id": "STA-04-DOK-01",
          "session_ids": [
            "SES-20260910185044-CK-002-K-04",
            "SES-20260911004457-CK-020-K-04",
            "SES-20260911020111-CK-004-K-04",
            "SES-20260911025237-CK-004-K-04",
            "SES-20260911081304-CK-012-K-04",
            "SES-20260911094242-CK-016-K-04",
            "SES-20260911104245-CK-008-K-04",
            "SES-20260911182954-CK-020-K-04",
            "SES-20260912001136-CK-013-K-04",
            "SES-20260912021635-CK-013-K-04",
            "SES-20260912052158-CK-005-K-04",
            "SES-20260912072708-CK-009-K-04",
            "SES-20260912083111-CK-005-K-04",
            "SES-20260912090750-CK-017-K-04",
            "SES-20260912125638-CK-017-K-04",
            "SES-20260912170129-CK-009-K-04",
            "SES-20260912175325-CK-001-K-04",
            "SES-20260913000847-CK-019-K-04",
            "SES-20260913132424-CK-003-K-04",
            "SES-20260913140317-CK-015-K-04",
            "SES-20260913171756-CK-007-K-04",
            "SES-20260913185751-CK-011-K-04",
            "SES-20260914034649-CK-014-K-04",
            "SES-20260914043523-CK-002-K-04",
            "SES-20260914093234-CK-002-K-04",
            "SES-20260914114651-CK-010-K-04",
            "SES-20260914151350-CK-014-K-04",
            "SES-20260914154718-CK-018-K-04",
            "SES-20260914173207-CK-010-K-04"
          ],
          "count": 29
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "dock_independent_packs": 20
      },
      "recommended_actions": [
        "Inspect dock control circuitry and power delivery hardware",
        "Test contact pins and connector path resistance"
      ],
      "explanation": "Evidence supports CHARGER_DOCK: 20 independent packs affected at dock STA-02-DOK-04; pack STA-02-PCK-020 is normal elsewhere.",
      "first_seen_ts": "2026-09-11T00:44:57.528276Z",
      "last_seen_ts": "2026-09-14T17:32:07.174550Z",
      "opened_at": "2026-10-24T14:13:33.993004Z",
      "occurrence_count": 29,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260910185044-CK-002-K-04",
        "SES-20260911004457-CK-020-K-04",
        "SES-20260911020111-CK-004-K-04",
        "SES-20260911025237-CK-004-K-04",
        "SES-20260911081304-CK-012-K-04",
        "SES-20260911094242-CK-016-K-04",
        "SES-20260911104245-CK-008-K-04",
        "SES-20260911182954-CK-020-K-04",
        "SES-20260912001136-CK-013-K-04",
        "SES-20260912021635-CK-013-K-04",
        "SES-20260912052158-CK-005-K-04",
        "SES-20260912072708-CK-009-K-04",
        "SES-20260912083111-CK-005-K-04",
        "SES-20260912090750-CK-017-K-04",
        "SES-20260912125638-CK-017-K-04",
        "SES-20260912170129-CK-009-K-04",
        "SES-20260912175325-CK-001-K-04",
        "SES-20260913000847-CK-019-K-04",
        "SES-20260913132424-CK-003-K-04",
        "SES-20260913140317-CK-015-K-04",
        "SES-20260913171756-CK-007-K-04",
        "SES-20260913185751-CK-011-K-04",
        "SES-20260914034649-CK-014-K-04",
        "SES-20260914043523-CK-002-K-04",
        "SES-20260914093234-CK-002-K-04",
        "SES-20260914114651-CK-010-K-04",
        "SES-20260914151350-CK-014-K-04",
        "SES-20260914154718-CK-018-K-04",
        "SES-20260914173207-CK-010-K-04"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "1a68249f-872b-43f2-ad4a-7dae655ed52e",
      "episode_key": "CELL_CHEMISTRY:STA-04-PCK-017:pack_self_heating_excess",
      "owner_category": "CELL_CHEMISTRY",
      "owner_team": "cell_engineering",
      "entity_id": "STA-04-PCK-017",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "pack_self_heating_excess"
      ],
      "observed_value": 12.704297501046653,
      "expected_value": 7.009122783962873,
      "observed_unit": "\u00b0C",
      "residual_normalized": 16.733033594988687,
      "evidence": [
        {
          "description": "Cell-level measurement: chemistry_charge_curve_drift=1.3567V",
          "entity_id": "STA-01-PCK-006",
          "session_ids": [
            "SES-20260914192207-CK-006-K-02"
          ],
          "count": 1
        },
        {
          "description": "Feature pack_self_heating_excess anomaly: observed=12.704\u00b0C, expected=5.353\u00b0C, z-score=16.73",
          "entity_id": "STA-04-PCK-017",
          "session_ids": [
            "SES-20260910192704-CK-003-K-03",
            "SES-20260911010524-CK-010-K-03",
            "SES-20260911015623-CK-002-K-03",
            "SES-20260911092817-CK-010-K-03",
            "SES-20260911120122-CK-007-K-01",
            "SES-20260912001653-CK-006-K-03",
            "SES-20260912032025-CK-010-K-03",
            "SES-20260912032219-CK-006-K-02",
            "SES-20260912065313-CK-002-K-03",
            "SES-20260912073958-CK-018-K-03",
            "SES-20260912074015-CK-006-K-03",
            "SES-20260912090905-CK-016-K-01",
            "SES-20260912094812-CK-016-K-04",
            "SES-20260912100533-CK-016-K-04",
            "SES-20260912163952-CK-010-K-03",
            "SES-20260912172059-CK-016-K-01",
            "SES-20260913020258-CK-006-K-03",
            "SES-20260913033254-CK-016-K-04",
            "SES-20260913044506-CK-018-K-03",
            "SES-20260913110232-CK-018-K-03",
            "SES-20260913131723-CK-006-K-03",
            "SES-20260913151255-CK-006-K-01",
            "SES-20260913163558-CK-016-K-04",
            "SES-20260914013324-CK-006-K-02",
            "SES-20260914031843-CK-019-K-03",
            "SES-20260914100212-CK-015-K-03",
            "SES-20260914101948-CK-013-K-03",
            "SES-20260914125210-CK-003-K-03",
            "SES-20260914142045-CK-011-K-03",
            "SES-20260914150838-CK-006-K-01",
            "SES-20260914151346-CK-006-K-01",
            "SES-20260914172115-CK-007-K-03",
            "SES-20260914192207-CK-006-K-02"
          ],
          "count": 33
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "pack_independent_docks": 4
      },
      "recommended_actions": [
        "Inspect individual cell voltages under controlled conditions",
        "Validate cell voltage sensor calibration"
      ],
      "explanation": "Cell-level voltage divergence or curve drift detected. Evidence suggests cell/chemistry investigation for pack STA-01-PCK-010. Note: specific degradation mechanism is unverified \u2014 route to battery engineering.",
      "first_seen_ts": "2026-09-11T01:05:24.349323Z",
      "last_seen_ts": "2026-09-14T19:22:07.780860Z",
      "opened_at": "2026-10-24T14:13:33.994456Z",
      "occurrence_count": 33,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260910192704-CK-003-K-03",
        "SES-20260911010524-CK-010-K-03",
        "SES-20260911015623-CK-002-K-03",
        "SES-20260911092817-CK-010-K-03",
        "SES-20260911120122-CK-007-K-01",
        "SES-20260912001653-CK-006-K-03",
        "SES-20260912032025-CK-010-K-03",
        "SES-20260912032219-CK-006-K-02",
        "SES-20260912065313-CK-002-K-03",
        "SES-20260912073958-CK-018-K-03",
        "SES-20260912074015-CK-006-K-03",
        "SES-20260912090905-CK-016-K-01",
        "SES-20260912094812-CK-016-K-04",
        "SES-20260912100533-CK-016-K-04",
        "SES-20260912163952-CK-010-K-03",
        "SES-20260912172059-CK-016-K-01",
        "SES-20260913020258-CK-006-K-03",
        "SES-20260913033254-CK-016-K-04",
        "SES-20260913044506-CK-018-K-03",
        "SES-20260913110232-CK-018-K-03",
        "SES-20260913131723-CK-006-K-03",
        "SES-20260913151255-CK-006-K-01",
        "SES-20260913163558-CK-016-K-04",
        "SES-20260914013324-CK-006-K-02",
        "SES-20260914031843-CK-019-K-03",
        "SES-20260914100212-CK-015-K-03",
        "SES-20260914101948-CK-013-K-03",
        "SES-20260914125210-CK-003-K-03",
        "SES-20260914142045-CK-011-K-03",
        "SES-20260914150838-CK-006-K-01",
        "SES-20260914151346-CK-006-K-01",
        "SES-20260914172115-CK-007-K-03",
        "SES-20260914192207-CK-006-K-02"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "5aaddffd-c566-41d8-a9ba-7157c779dbdf",
      "episode_key": "CELL_CHEMISTRY:STA-04-PCK-017:chemistry_charge_curve_drift",
      "owner_category": "CELL_CHEMISTRY",
      "owner_team": "cell_engineering",
      "entity_id": "STA-04-PCK-017",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "chemistry_charge_curve_drift"
      ],
      "observed_value": 2.403921553071421,
      "expected_value": 2.5881859654659505,
      "observed_unit": "V",
      "residual_normalized": 23.13867711526599,
      "evidence": [
        {
          "description": "Cell-level measurement: chemistry_charge_curve_drift=2.4039V",
          "entity_id": "STA-04-PCK-013",
          "session_ids": [
            "SES-20260914114411-CK-013-K-03"
          ],
          "count": 1
        },
        {
          "description": "Feature chemistry_charge_curve_drift anomaly: observed=2.404V, expected=2.204V, z-score=23.14",
          "entity_id": "STA-04-PCK-017",
          "session_ids": [
            "SES-20260911044821-CK-001-K-02",
            "SES-20260911124549-CK-006-K-03",
            "SES-20260912104140-CK-001-K-01",
            "SES-20260913054846-CK-013-K-01",
            "SES-20260914023839-CK-003-K-02",
            "SES-20260914040022-CK-017-K-01",
            "SES-20260914114411-CK-013-K-03"
          ],
          "count": 7
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "pack_independent_docks": 4
      },
      "recommended_actions": [
        "Inspect individual cell voltages under controlled conditions",
        "Validate cell voltage sensor calibration"
      ],
      "explanation": "Cell-level voltage divergence or curve drift detected. Evidence suggests cell/chemistry investigation for pack STA-01-PCK-006. Note: specific degradation mechanism is unverified \u2014 route to battery engineering.",
      "first_seen_ts": "2026-09-11T12:45:49.727453Z",
      "last_seen_ts": "2026-09-14T11:44:11.509235Z",
      "opened_at": "2026-10-24T14:13:33.998235Z",
      "occurrence_count": 7,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260911044821-CK-001-K-02",
        "SES-20260911124549-CK-006-K-03",
        "SES-20260912104140-CK-001-K-01",
        "SES-20260913054846-CK-013-K-01",
        "SES-20260914023839-CK-003-K-02",
        "SES-20260914040022-CK-017-K-01",
        "SES-20260914114411-CK-013-K-03"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "bde46ecc-6db9-4bf2-9cff-4298cd1d83ba",
      "episode_key": "PACK:STA-04-PCK-017:pack_electrical_response_anomaly",
      "owner_category": "PACK",
      "owner_team": "battery_service",
      "entity_id": "STA-04-PCK-017",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "pack_electrical_response_anomaly"
      ],
      "observed_value": 5.666602564627738,
      "expected_value": 5.476937620299921,
      "observed_unit": "V",
      "residual_normalized": 7.762797949059787,
      "evidence": [
        {
          "description": "Pack STA-03-PCK-006 shows anomaly across 4 independent docks",
          "entity_id": "STA-03-PCK-006",
          "session_ids": [],
          "count": 4
        },
        {
          "description": "Other packs at same docks show normal behavior",
          "entity_id": "STA-03-PCK-006",
          "session_ids": [],
          "count": 4
        },
        {
          "description": "Feature pack_electrical_response_anomaly anomaly: observed=5.667V, expected=5.477V, z-score=7.76",
          "entity_id": "STA-04-PCK-017",
          "session_ids": [
            "SES-20260912073421-CK-006-K-03",
            "SES-20260912134121-CK-006-K-01"
          ],
          "count": 2
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "pack_independent_docks": 4
      },
      "recommended_actions": [
        "Run pack electrical diagnostics (BMS health check)",
        "Inspect pack thermal system and temperature sensors"
      ],
      "explanation": "Evidence supports PACK: anomaly follows pack STA-03-PCK-006 across 4 independent docks; those docks are normal with other packs.",
      "first_seen_ts": "2026-09-12T13:41:21.417603Z",
      "last_seen_ts": "2026-09-12T13:41:21.417603Z",
      "opened_at": "2026-10-24T14:13:34.004362Z",
      "occurrence_count": 2,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260912073421-CK-006-K-03",
        "SES-20260912134121-CK-006-K-01"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "bf8539b3-d829-4869-aeba-2083fe4a5d05",
      "episode_key": "ENVIRONMENT:STA-04:env_sitewide_heat_derate",
      "owner_category": "ENVIRONMENT",
      "owner_team": "site_facilities",
      "entity_id": "STA-04",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "env_sitewide_heat_derate"
      ],
      "observed_value": 23.027165835133673,
      "expected_value": 1.6816590472414248,
      "observed_unit": "\u00b0C",
      "residual_normalized": 9.041164859182647,
      "evidence": [
        {
          "description": "Measured environmental condition at station STA-03",
          "entity_id": "STA-03",
          "session_ids": [],
          "count": 20
        },
        {
          "description": "20 packs and 4 docks affected at station",
          "entity_id": "STA-03",
          "session_ids": [],
          "count": 4
        },
        {
          "description": "Feature env_sitewide_heat_derate anomaly: observed=23.027\u00b0C, expected=1.682\u00b0C, z-score=9.04",
          "entity_id": "STA-04",
          "session_ids": [
            "SES-20260911124229-CK-019-K-03",
            "SES-20260912145417-CK-012-K-04",
            "SES-20260913014501-CK-010-K-01",
            "SES-20260913155658-CK-019-K-03",
            "SES-20260913183339-CK-016-K-02",
            "SES-20260913195310-CK-019-K-04",
            "SES-20260914081036-CK-020-K-01",
            "SES-20260914135910-CK-007-K-02"
          ],
          "count": 8
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {
        "env_station_packs": 20,
        "env_station_docks": 4
      },
      "recommended_actions": [
        "Inspect site cooling, HVAC, and ventilation systems",
        "Check upstream electrical supply and distribution"
      ],
      "explanation": "Evidence supports ENVIRONMENT: measured site condition at station STA-03 with 20 affected packs and 4 docks. Note: shared station hardware faults are a competing hypothesis.",
      "first_seen_ts": "2026-09-12T14:54:17.205455Z",
      "last_seen_ts": "2026-09-14T13:59:10.423845Z",
      "opened_at": "2026-10-24T14:13:34.005049Z",
      "occurrence_count": 8,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260911124229-CK-019-K-03",
        "SES-20260912145417-CK-012-K-04",
        "SES-20260913014501-CK-010-K-01",
        "SES-20260913155658-CK-019-K-03",
        "SES-20260913183339-CK-016-K-02",
        "SES-20260913195310-CK-019-K-04",
        "SES-20260914081036-CK-020-K-01",
        "SES-20260914135910-CK-007-K-02"
      ],
      "transitions": [],
      "resolution": null
    },
    {
      "alert_id": "2f448712-e7b6-4ec8-aeb9-3bd0b3786fb2",
      "episode_key": "CELL_CHEMISTRY:STA-04-PCK-017:cell_voltage_dispersion_excess",
      "owner_category": "CELL_CHEMISTRY",
      "owner_team": "cell_engineering",
      "entity_id": "STA-04-PCK-017",
      "severity": "MEDIUM",
      "status": "OPEN",
      "feature_ids": [
        "cell_voltage_dispersion_excess"
      ],
      "observed_value": 0.00037646506470068175,
      "expected_value": 0.00019730481990576365,
      "observed_unit": "V",
      "residual_normalized": 3.106561433709,
      "evidence": [
        {
          "description": "Cell-level measurement: cell_voltage_dispersion_excess=0.0004V",
          "entity_id": "STA-01-PCK-014",
          "session_ids": [
            "SES-20260914111858-CK-014-K-01"
          ],
          "count": 1
        },
        {
          "description": "Feature cell_voltage_dispersion_excess anomaly: observed=0.000V, expected=0.000V, z-score=3.11",
          "entity_id": "STA-04-PCK-017",
          "session_ids": [
            "SES-20260913000646-CK-006-K-01",
            "SES-20260913025423-CK-003-K-02",
            "SES-20260913042456-CK-003-K-04",
            "SES-20260913154753-CK-006-K-01",
            "SES-20260914015715-CK-018-K-04",
            "SES-20260914060759-CK-011-K-02",
            "SES-20260914111858-CK-014-K-01"
          ],
          "count": 7
        }
      ],
      "counterevidence": [],
      "independent_support_counts": {},
      "recommended_actions": [
        "Inspect individual cell voltages under controlled conditions",
        "Validate cell voltage sensor calibration"
      ],
      "explanation": "Cell-level voltage divergence or curve drift detected. Evidence suggests cell/chemistry investigation for pack STA-01-PCK-003. Note: specific degradation mechanism is unverified \u2014 route to battery engineering.",
      "first_seen_ts": "2026-09-13T02:54:23.523238Z",
      "last_seen_ts": "2026-09-14T11:18:58.502379Z",
      "opened_at": "2026-10-24T14:13:34.007942Z",
      "occurrence_count": 7,
      "baseline_version": "1.0",
      "pipeline_version": "1.0.0",
      "data_provenance": "SYNTHETIC",
      "supporting_session_ids": [
        "SES-20260913000646-CK-006-K-01",
        "SES-20260913025423-CK-003-K-02",
        "SES-20260913042456-CK-003-K-04",
        "SES-20260913154753-CK-006-K-01",
        "SES-20260914015715-CK-018-K-04",
        "SES-20260914060759-CK-011-K-02",
        "SES-20260914111858-CK-014-K-01"
      ],
      "transitions": [],
      "resolution": null
    }
  ],
  "evalReport": {
    "detection": {
      "precision": 0.9534883720930233,
      "recall": 0.22343324250681199,
      "f1": 0.36203090507726265,
      "false_alerts_per_1000_healthy": 18.6046511627907
    },
    "attribution": {
      "macro_f1": 0.16374570446735395,
      "abstention_count": 47,
      "abstention_coverage": 0.08075601374570447
    },
    "scenarios": {
      "S01_bad_dock": {
        "pass": true,
        "evidence": "2 CHARGER_DOCK alerts emitted",
        "expected": "owner=CHARGER_DOCK, multiple independent packs affected"
      },
      "S02_bad_pack": {
        "pass": true,
        "evidence": "1 PACK alerts emitted",
        "expected": "owner=PACK, anomaly follows pack across docks"
      },
      "S03_cell_chemistry": {
        "pass": true,
        "evidence": "3 CELL_CHEMISTRY alerts emitted",
        "expected": "owner=CELL_CHEMISTRY, cell-level investigation"
      },
      "S04_environment": {
        "pass": true,
        "evidence": "1 ENVIRONMENT alerts emitted",
        "expected": "owner=ENVIRONMENT, measured site condition"
      },
      "S05_abstention": {
        "pass": true,
        "evidence": "47 INSUFFICIENT_EVIDENCE attributions",
        "expected": "status=INSUFFICIENT_EVIDENCE, no maintenance alert"
      }
    },
    "metadata": {
      "seed": 42,
      "n_test_sessions": 582,
      "n_healthy": 215,
      "n_faulty": 367,
      "n_alerts": 7,
      "evaluation_ts": "2026-10-24T14:14:50.945980+00:00",
      "data_provenance": "SYNTHETIC -- semi-synthetic swapping network benchmark",
      "note": "Results from controlled synthetic benchmark. Not representative of real-world field performance."
    }
  },
  "abstentions": [
    {
      "session_id": "SES-20260911014509-CK-014-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911015505-CK-002-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911053912-CK-017-K-02",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911073146-CK-003-K-01",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911105935-CK-006-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911123006-CK-018-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911125117-CK-019-K-01",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911131243-CK-018-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260911195657-CK-010-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912000238-CK-010-K-01",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912035917-CK-002-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912045835-CK-018-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912055750-CK-014-K-03",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912090324-CK-012-K-04",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    },
    {
      "session_id": "SES-20260912090726-CK-016-K-04",
      "episode_id": null,
      "candidate_owners": [
        "PACK"
      ],
      "owner_evidence": {},
      "owner_counterevidence": {},
      "crossing_support": {
        "pack_independent_docks": 4
      },
      "selected_owner": null,
      "attribution_status": "INSUFFICIENT_EVIDENCE",
      "confidence_semantics": "LOW",
      "explanation": "No anomalies detected."
    }
  ],
  "abstentionTotal": 47,
  "curves": {
    "normal": [
      {
        "minute": 0,
        "soc": 15.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 45.5,
        "temp_c": 25.0,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 1,
        "soc": 16.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.64,
        "temp_c": 25.1,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 2,
        "soc": 17.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 45.78,
        "temp_c": 25.2,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 3,
        "soc": 19.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 45.92,
        "temp_c": 25.4,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 4,
        "soc": 20.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.06,
        "temp_c": 25.5,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 5,
        "soc": 22.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 46.2,
        "temp_c": 25.6,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 6,
        "soc": 23.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 46.34,
        "temp_c": 25.8,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 7,
        "soc": 24.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.48,
        "temp_c": 25.9,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 8,
        "soc": 26.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 46.62,
        "temp_c": 26.0,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 9,
        "soc": 27.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 46.76,
        "temp_c": 26.1,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 10,
        "soc": 29.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.9,
        "temp_c": 26.2,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 11,
        "soc": 30.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 47.04,
        "temp_c": 26.4,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 12,
        "soc": 31.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 47.18,
        "temp_c": 26.5,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 13,
        "soc": 33.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.32,
        "temp_c": 26.6,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 14,
        "soc": 34.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 47.46,
        "temp_c": 26.8,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 15,
        "soc": 36.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 47.6,
        "temp_c": 26.9,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 16,
        "soc": 37.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.74,
        "temp_c": 27.0,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 17,
        "soc": 38.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 47.88,
        "temp_c": 27.1,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 18,
        "soc": 40.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 48.02,
        "temp_c": 27.2,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 19,
        "soc": 41.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.16,
        "temp_c": 27.4,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 20,
        "soc": 43.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 48.3,
        "temp_c": 27.5,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 21,
        "soc": 44.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 48.44,
        "temp_c": 27.6,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 22,
        "soc": 45.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.58,
        "temp_c": 27.8,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 23,
        "soc": 47.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 48.72,
        "temp_c": 27.9,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 24,
        "soc": 48.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 48.86,
        "temp_c": 28.0,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 25,
        "soc": 50.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.0,
        "temp_c": 28.1,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 26,
        "soc": 51.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 49.14,
        "temp_c": 28.2,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 27,
        "soc": 52.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 49.28,
        "temp_c": 28.4,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 28,
        "soc": 54.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.42,
        "temp_c": 28.5,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 29,
        "soc": 55.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 49.56,
        "temp_c": 28.6,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 30,
        "soc": 57.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 49.7,
        "temp_c": 28.8,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 31,
        "soc": 58.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.84,
        "temp_c": 28.9,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 32,
        "soc": 59.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 49.98,
        "temp_c": 29.0,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 33,
        "soc": 61.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 50.12,
        "temp_c": 29.1,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 34,
        "soc": 62.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 50.26,
        "temp_c": 29.2,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 35,
        "soc": 64.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 50.4,
        "temp_c": 29.4,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 36,
        "soc": 65.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 50.54,
        "temp_c": 29.5,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 37,
        "soc": 66.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 50.68,
        "temp_c": 29.6,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 38,
        "soc": 68.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 50.82,
        "temp_c": 29.8,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 39,
        "soc": 69.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 50.96,
        "temp_c": 29.9,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 40,
        "soc": 71.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 51.1,
        "temp_c": 30.0,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 41,
        "soc": 72.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 51.24,
        "temp_c": 30.1,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 42,
        "soc": 73.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 51.38,
        "temp_c": 30.2,
        "cell_spread_mv": 14.4
      },
      {
        "minute": 43,
        "soc": 75.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 51.52,
        "temp_c": 30.4,
        "cell_spread_mv": 15.6
      },
      {
        "minute": 44,
        "soc": 76.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.05,
        "pack_current_a": 15.05,
        "pack_voltage_v": 51.66,
        "temp_c": 30.5,
        "cell_spread_mv": 16.8
      },
      {
        "minute": 45,
        "soc": 78.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 14.95,
        "pack_current_a": 14.95,
        "pack_voltage_v": 51.8,
        "temp_c": 30.6,
        "cell_spread_mv": 12.0
      },
      {
        "minute": 46,
        "soc": 79.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 51.94,
        "temp_c": 30.8,
        "cell_spread_mv": 13.2
      },
      {
        "minute": 47,
        "soc": 80.8,
        "cmd_current_a": 14.4,
        "dock_current_a": 14.4,
        "pack_current_a": 14.4,
        "pack_voltage_v": 52.0,
        "temp_c": 32.2,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 48,
        "soc": 82.2,
        "cmd_current_a": 13.35,
        "dock_current_a": 13.35,
        "pack_current_a": 13.35,
        "pack_voltage_v": 52.0,
        "temp_c": 32.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 49,
        "soc": 83.6,
        "cmd_current_a": 12.3,
        "dock_current_a": 12.3,
        "pack_current_a": 12.3,
        "pack_voltage_v": 52.0,
        "temp_c": 31.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 50,
        "soc": 85.0,
        "cmd_current_a": 11.25,
        "dock_current_a": 11.25,
        "pack_current_a": 11.25,
        "pack_voltage_v": 52.0,
        "temp_c": 31.8,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 51,
        "soc": 86.4,
        "cmd_current_a": 10.2,
        "dock_current_a": 10.2,
        "pack_current_a": 10.2,
        "pack_voltage_v": 52.0,
        "temp_c": 31.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 52,
        "soc": 87.8,
        "cmd_current_a": 9.15,
        "dock_current_a": 9.15,
        "pack_current_a": 9.15,
        "pack_voltage_v": 52.0,
        "temp_c": 31.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 53,
        "soc": 89.2,
        "cmd_current_a": 8.1,
        "dock_current_a": 8.1,
        "pack_current_a": 8.1,
        "pack_voltage_v": 52.0,
        "temp_c": 31.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 54,
        "soc": 90.6,
        "cmd_current_a": 7.05,
        "dock_current_a": 7.05,
        "pack_current_a": 7.05,
        "pack_voltage_v": 52.0,
        "temp_c": 31.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 55,
        "soc": 92.0,
        "cmd_current_a": 6.0,
        "dock_current_a": 6.0,
        "pack_current_a": 6.0,
        "pack_voltage_v": 52.0,
        "temp_c": 31.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 56,
        "soc": 93.4,
        "cmd_current_a": 4.95,
        "dock_current_a": 4.95,
        "pack_current_a": 4.95,
        "pack_voltage_v": 52.0,
        "temp_c": 30.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 57,
        "soc": 94.8,
        "cmd_current_a": 3.9,
        "dock_current_a": 3.9,
        "pack_current_a": 3.9,
        "pack_voltage_v": 52.0,
        "temp_c": 30.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 58,
        "soc": 96.2,
        "cmd_current_a": 2.85,
        "dock_current_a": 2.85,
        "pack_current_a": 2.85,
        "pack_voltage_v": 52.0,
        "temp_c": 30.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 59,
        "soc": 97.6,
        "cmd_current_a": 1.8,
        "dock_current_a": 1.8,
        "pack_current_a": 1.8,
        "pack_voltage_v": 52.0,
        "temp_c": 30.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 60,
        "soc": 99.0,
        "cmd_current_a": 1.5,
        "dock_current_a": 1.5,
        "pack_current_a": 1.5,
        "pack_voltage_v": 52.0,
        "temp_c": 30.2,
        "cell_spread_mv": 14.0
      }
    ],
    "dock_fault": [
      {
        "minute": 0,
        "soc": 15.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.05,
        "temp_c": 25.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 1,
        "soc": 15.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.1,
        "temp_c": 25.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 2,
        "soc": 16.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.16,
        "temp_c": 25.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 3,
        "soc": 17.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.21,
        "temp_c": 25.2,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 4,
        "soc": 18.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.26,
        "temp_c": 25.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 5,
        "soc": 18.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.31,
        "temp_c": 25.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 6,
        "soc": 19.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.37,
        "temp_c": 25.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 7,
        "soc": 20.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.42,
        "temp_c": 25.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 8,
        "soc": 21.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.47,
        "temp_c": 25.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 9,
        "soc": 21.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.52,
        "temp_c": 25.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 10,
        "soc": 22.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.58,
        "temp_c": 25.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 11,
        "soc": 23.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.63,
        "temp_c": 25.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 12,
        "soc": 24.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.68,
        "temp_c": 25.8,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 13,
        "soc": 24.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.73,
        "temp_c": 25.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 14,
        "soc": 25.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.78,
        "temp_c": 25.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 15,
        "soc": 26.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.84,
        "temp_c": 26.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 16,
        "soc": 27.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.89,
        "temp_c": 26.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 17,
        "soc": 27.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 45.94,
        "temp_c": 26.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 18,
        "soc": 28.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 45.99,
        "temp_c": 26.2,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 19,
        "soc": 29.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.05,
        "temp_c": 26.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 20,
        "soc": 30.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.1,
        "temp_c": 26.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 21,
        "soc": 30.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.15,
        "temp_c": 26.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 22,
        "soc": 31.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.2,
        "temp_c": 26.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 23,
        "soc": 32.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.26,
        "temp_c": 26.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 24,
        "soc": 33.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.31,
        "temp_c": 26.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 25,
        "soc": 33.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.36,
        "temp_c": 26.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 26,
        "soc": 34.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.41,
        "temp_c": 26.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 27,
        "soc": 35.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.47,
        "temp_c": 26.8,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 28,
        "soc": 36.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.52,
        "temp_c": 26.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 29,
        "soc": 36.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.57,
        "temp_c": 26.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 30,
        "soc": 37.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.62,
        "temp_c": 27.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 31,
        "soc": 38.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.68,
        "temp_c": 27.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 32,
        "soc": 39.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.73,
        "temp_c": 27.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 33,
        "soc": 39.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.78,
        "temp_c": 27.2,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 34,
        "soc": 40.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.84,
        "temp_c": 27.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 35,
        "soc": 41.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.89,
        "temp_c": 27.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 36,
        "soc": 42.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 46.94,
        "temp_c": 27.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 37,
        "soc": 42.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 46.99,
        "temp_c": 27.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 38,
        "soc": 43.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.05,
        "temp_c": 27.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 39,
        "soc": 44.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.1,
        "temp_c": 27.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 40,
        "soc": 45.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.15,
        "temp_c": 27.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 41,
        "soc": 45.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.2,
        "temp_c": 27.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 42,
        "soc": 46.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.26,
        "temp_c": 27.8,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 43,
        "soc": 47.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.31,
        "temp_c": 27.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 44,
        "soc": 48.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.36,
        "temp_c": 27.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 45,
        "soc": 48.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.41,
        "temp_c": 28.0,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 46,
        "soc": 49.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.47,
        "temp_c": 28.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 47,
        "soc": 50.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.52,
        "temp_c": 28.1,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 48,
        "soc": 51.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.57,
        "temp_c": 28.2,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 49,
        "soc": 51.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.62,
        "temp_c": 28.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 50,
        "soc": 52.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.67,
        "temp_c": 28.3,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 51,
        "soc": 53.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.73,
        "temp_c": 28.4,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 52,
        "soc": 54.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.78,
        "temp_c": 28.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 53,
        "soc": 54.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.83,
        "temp_c": 28.5,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 54,
        "soc": 55.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.88,
        "temp_c": 28.6,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 55,
        "soc": 56.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 47.94,
        "temp_c": 28.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 56,
        "soc": 57.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 47.99,
        "temp_c": 28.7,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 57,
        "soc": 57.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 48.04,
        "temp_c": 28.8,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 58,
        "soc": 58.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 48.09,
        "temp_c": 28.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 59,
        "soc": 59.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 8.05,
        "pack_current_a": 8.05,
        "pack_voltage_v": 48.15,
        "temp_c": 28.9,
        "cell_spread_mv": 14.0
      },
      {
        "minute": 60,
        "soc": 60.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 7.95,
        "pack_current_a": 7.95,
        "pack_voltage_v": 48.2,
        "temp_c": 29.0,
        "cell_spread_mv": 14.0
      }
    ],
    "pack_fault": [
      {
        "minute": 0,
        "soc": 15.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.91,
        "temp_c": 26.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 1,
        "soc": 16.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.03,
        "temp_c": 26.7,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 2,
        "soc": 17.7,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.16,
        "temp_c": 27.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 3,
        "soc": 19.1,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.29,
        "temp_c": 28.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 4,
        "soc": 20.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.41,
        "temp_c": 28.9,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 5,
        "soc": 21.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.54,
        "temp_c": 29.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 6,
        "soc": 23.1,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.67,
        "temp_c": 30.3,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 7,
        "soc": 24.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.79,
        "temp_c": 31.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 8,
        "soc": 25.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.92,
        "temp_c": 31.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 9,
        "soc": 27.1,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.05,
        "temp_c": 32.5,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 10,
        "soc": 28.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.17,
        "temp_c": 33.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 11,
        "soc": 29.9,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.3,
        "temp_c": 33.9,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 12,
        "soc": 31.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.42,
        "temp_c": 34.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 13,
        "soc": 32.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.55,
        "temp_c": 35.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 14,
        "soc": 33.9,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.68,
        "temp_c": 36.1,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 15,
        "soc": 35.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.8,
        "temp_c": 36.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 16,
        "soc": 36.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.93,
        "temp_c": 37.5,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 17,
        "soc": 38.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.06,
        "temp_c": 38.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 18,
        "soc": 39.3,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.18,
        "temp_c": 39.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 19,
        "soc": 40.7,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.31,
        "temp_c": 39.7,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 20,
        "soc": 42.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.44,
        "temp_c": 40.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 21,
        "soc": 43.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.56,
        "temp_c": 41.1,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 22,
        "soc": 44.7,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.69,
        "temp_c": 41.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 23,
        "soc": 46.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.82,
        "temp_c": 42.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 24,
        "soc": 47.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.94,
        "temp_c": 43.3,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 25,
        "soc": 48.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.07,
        "temp_c": 44.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 26,
        "soc": 50.1,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.2,
        "temp_c": 44.7,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 27,
        "soc": 51.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.32,
        "temp_c": 45.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 28,
        "soc": 52.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.45,
        "temp_c": 46.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 29,
        "soc": 54.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.58,
        "temp_c": 46.9,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 30,
        "soc": 55.5,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.7,
        "temp_c": 47.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 31,
        "soc": 56.9,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.83,
        "temp_c": 48.3,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 32,
        "soc": 58.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 49.96,
        "temp_c": 49.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 33,
        "soc": 59.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 50.08,
        "temp_c": 49.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 34,
        "soc": 60.9,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 50.21,
        "temp_c": 50.5,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 35,
        "soc": 62.2,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.34,
        "temp_c": 51.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 36,
        "soc": 63.6,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.46,
        "temp_c": 51.9,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 37,
        "soc": 65.0,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.59,
        "temp_c": 52.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 38,
        "soc": 66.3,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.72,
        "temp_c": 53.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 39,
        "soc": 67.7,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.84,
        "temp_c": 54.1,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 40,
        "soc": 69.0,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 50.97,
        "temp_c": 54.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 41,
        "soc": 70.3,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.1,
        "temp_c": 55.5,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 42,
        "soc": 71.7,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.22,
        "temp_c": 56.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 43,
        "soc": 73.1,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.35,
        "temp_c": 57.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 44,
        "soc": 74.4,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.48,
        "temp_c": 57.7,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 45,
        "soc": 75.8,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.6,
        "temp_c": 58.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 46,
        "soc": 77.1,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.73,
        "temp_c": 59.1,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 47,
        "soc": 78.5,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.85,
        "temp_c": 59.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 48,
        "soc": 79.8,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 51.98,
        "temp_c": 60.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 49,
        "soc": 81.2,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.11,
        "temp_c": 61.3,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 50,
        "soc": 82.5,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.23,
        "temp_c": 62.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 51,
        "soc": 83.9,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.36,
        "temp_c": 62.7,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 52,
        "soc": 85.2,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.49,
        "temp_c": 63.4,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 53,
        "soc": 86.6,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.61,
        "temp_c": 64.2,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 54,
        "soc": 87.9,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.74,
        "temp_c": 64.9,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 55,
        "soc": 89.2,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.87,
        "temp_c": 65.6,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 56,
        "soc": 90.6,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 52.99,
        "temp_c": 66.3,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 57,
        "soc": 92.0,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 53.12,
        "temp_c": 67.0,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 58,
        "soc": 93.3,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 53.25,
        "temp_c": 67.8,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 59,
        "soc": 94.7,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 53.37,
        "temp_c": 68.5,
        "cell_spread_mv": 24.0
      },
      {
        "minute": 60,
        "soc": 96.0,
        "cmd_current_a": 9.5,
        "dock_current_a": 9.5,
        "pack_current_a": 9.5,
        "pack_voltage_v": 53.5,
        "temp_c": 69.2,
        "cell_spread_mv": 24.0
      }
    ],
    "cell_fault": [
      {
        "minute": 0,
        "soc": 15.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.54,
        "temp_c": 25.5,
        "cell_spread_mv": 18.0
      },
      {
        "minute": 1,
        "soc": 16.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.66,
        "temp_c": 25.6,
        "cell_spread_mv": 20.8
      },
      {
        "minute": 2,
        "soc": 17.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.78,
        "temp_c": 25.7,
        "cell_spread_mv": 23.6
      },
      {
        "minute": 3,
        "soc": 18.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 45.91,
        "temp_c": 25.8,
        "cell_spread_mv": 26.4
      },
      {
        "minute": 4,
        "soc": 19.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.03,
        "temp_c": 25.9,
        "cell_spread_mv": 29.2
      },
      {
        "minute": 5,
        "soc": 21.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.15,
        "temp_c": 26.0,
        "cell_spread_mv": 32.0
      },
      {
        "minute": 6,
        "soc": 22.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.28,
        "temp_c": 26.1,
        "cell_spread_mv": 34.8
      },
      {
        "minute": 7,
        "soc": 23.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.4,
        "temp_c": 26.2,
        "cell_spread_mv": 37.6
      },
      {
        "minute": 8,
        "soc": 24.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.52,
        "temp_c": 26.3,
        "cell_spread_mv": 40.4
      },
      {
        "minute": 9,
        "soc": 25.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.64,
        "temp_c": 26.4,
        "cell_spread_mv": 43.2
      },
      {
        "minute": 10,
        "soc": 27.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.77,
        "temp_c": 26.5,
        "cell_spread_mv": 46.0
      },
      {
        "minute": 11,
        "soc": 28.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 46.89,
        "temp_c": 26.6,
        "cell_spread_mv": 48.8
      },
      {
        "minute": 12,
        "soc": 29.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.01,
        "temp_c": 26.7,
        "cell_spread_mv": 51.6
      },
      {
        "minute": 13,
        "soc": 30.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.14,
        "temp_c": 26.8,
        "cell_spread_mv": 54.4
      },
      {
        "minute": 14,
        "soc": 31.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.26,
        "temp_c": 26.9,
        "cell_spread_mv": 57.2
      },
      {
        "minute": 15,
        "soc": 33.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.38,
        "temp_c": 27.0,
        "cell_spread_mv": 60.0
      },
      {
        "minute": 16,
        "soc": 34.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.51,
        "temp_c": 27.1,
        "cell_spread_mv": 62.8
      },
      {
        "minute": 17,
        "soc": 35.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.63,
        "temp_c": 27.2,
        "cell_spread_mv": 65.6
      },
      {
        "minute": 18,
        "soc": 36.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.75,
        "temp_c": 27.3,
        "cell_spread_mv": 68.4
      },
      {
        "minute": 19,
        "soc": 37.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 47.87,
        "temp_c": 27.4,
        "cell_spread_mv": 71.2
      },
      {
        "minute": 20,
        "soc": 39.0,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.0,
        "temp_c": 27.5,
        "cell_spread_mv": 74.0
      },
      {
        "minute": 21,
        "soc": 40.2,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.12,
        "temp_c": 27.6,
        "cell_spread_mv": 76.8
      },
      {
        "minute": 22,
        "soc": 41.4,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.24,
        "temp_c": 27.7,
        "cell_spread_mv": 79.6
      },
      {
        "minute": 23,
        "soc": 42.6,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.37,
        "temp_c": 27.8,
        "cell_spread_mv": 82.4
      },
      {
        "minute": 24,
        "soc": 43.8,
        "cmd_current_a": 15.0,
        "dock_current_a": 15.0,
        "pack_current_a": 15.0,
        "pack_voltage_v": 48.49,
        "temp_c": 27.9,
        "cell_spread_mv": 85.2
      },
      {
        "minute": 25,
        "soc": 45.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 48.61,
        "temp_c": 28.0,
        "cell_spread_mv": 88.0
      },
      {
        "minute": 26,
        "soc": 46.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 48.74,
        "temp_c": 28.1,
        "cell_spread_mv": 90.8
      },
      {
        "minute": 27,
        "soc": 47.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 48.86,
        "temp_c": 28.2,
        "cell_spread_mv": 93.6
      },
      {
        "minute": 28,
        "soc": 48.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 48.98,
        "temp_c": 28.3,
        "cell_spread_mv": 96.4
      },
      {
        "minute": 29,
        "soc": 49.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.1,
        "temp_c": 28.4,
        "cell_spread_mv": 99.2
      },
      {
        "minute": 30,
        "soc": 51.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.23,
        "temp_c": 28.5,
        "cell_spread_mv": 102.0
      },
      {
        "minute": 31,
        "soc": 52.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.35,
        "temp_c": 28.6,
        "cell_spread_mv": 104.8
      },
      {
        "minute": 32,
        "soc": 53.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.47,
        "temp_c": 28.7,
        "cell_spread_mv": 107.6
      },
      {
        "minute": 33,
        "soc": 54.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.6,
        "temp_c": 28.8,
        "cell_spread_mv": 110.4
      },
      {
        "minute": 34,
        "soc": 55.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.72,
        "temp_c": 28.9,
        "cell_spread_mv": 113.2
      },
      {
        "minute": 35,
        "soc": 57.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.84,
        "temp_c": 29.0,
        "cell_spread_mv": 116.0
      },
      {
        "minute": 36,
        "soc": 58.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 49.97,
        "temp_c": 29.1,
        "cell_spread_mv": 118.8
      },
      {
        "minute": 37,
        "soc": 59.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.09,
        "temp_c": 29.2,
        "cell_spread_mv": 121.6
      },
      {
        "minute": 38,
        "soc": 60.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.21,
        "temp_c": 29.3,
        "cell_spread_mv": 124.4
      },
      {
        "minute": 39,
        "soc": 61.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.33,
        "temp_c": 29.4,
        "cell_spread_mv": 127.2
      },
      {
        "minute": 40,
        "soc": 63.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.46,
        "temp_c": 29.5,
        "cell_spread_mv": 130.0
      },
      {
        "minute": 41,
        "soc": 64.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.58,
        "temp_c": 29.6,
        "cell_spread_mv": 132.8
      },
      {
        "minute": 42,
        "soc": 65.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.7,
        "temp_c": 29.7,
        "cell_spread_mv": 135.6
      },
      {
        "minute": 43,
        "soc": 66.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.83,
        "temp_c": 29.8,
        "cell_spread_mv": 138.4
      },
      {
        "minute": 44,
        "soc": 67.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 50.95,
        "temp_c": 29.9,
        "cell_spread_mv": 141.2
      },
      {
        "minute": 45,
        "soc": 69.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.07,
        "temp_c": 30.0,
        "cell_spread_mv": 144.0
      },
      {
        "minute": 46,
        "soc": 70.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.2,
        "temp_c": 30.1,
        "cell_spread_mv": 146.8
      },
      {
        "minute": 47,
        "soc": 71.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.32,
        "temp_c": 30.2,
        "cell_spread_mv": 149.6
      },
      {
        "minute": 48,
        "soc": 72.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.44,
        "temp_c": 30.3,
        "cell_spread_mv": 152.4
      },
      {
        "minute": 49,
        "soc": 73.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.56,
        "temp_c": 30.4,
        "cell_spread_mv": 155.2
      },
      {
        "minute": 50,
        "soc": 75.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.69,
        "temp_c": 30.5,
        "cell_spread_mv": 158.0
      },
      {
        "minute": 51,
        "soc": 76.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.81,
        "temp_c": 30.6,
        "cell_spread_mv": 160.8
      },
      {
        "minute": 52,
        "soc": 77.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 51.93,
        "temp_c": 30.7,
        "cell_spread_mv": 163.6
      },
      {
        "minute": 53,
        "soc": 78.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.06,
        "temp_c": 30.8,
        "cell_spread_mv": 166.4
      },
      {
        "minute": 54,
        "soc": 79.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.18,
        "temp_c": 30.9,
        "cell_spread_mv": 169.2
      },
      {
        "minute": 55,
        "soc": 81.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.3,
        "temp_c": 31.0,
        "cell_spread_mv": 172.0
      },
      {
        "minute": 56,
        "soc": 82.2,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.43,
        "temp_c": 31.1,
        "cell_spread_mv": 174.8
      },
      {
        "minute": 57,
        "soc": 83.4,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.55,
        "temp_c": 31.2,
        "cell_spread_mv": 177.6
      },
      {
        "minute": 58,
        "soc": 84.6,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.67,
        "temp_c": 31.3,
        "cell_spread_mv": 180.4
      },
      {
        "minute": 59,
        "soc": 85.8,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.79,
        "temp_c": 31.4,
        "cell_spread_mv": 183.2
      },
      {
        "minute": 60,
        "soc": 87.0,
        "cmd_current_a": 7.0,
        "dock_current_a": 7.0,
        "pack_current_a": 7.0,
        "pack_voltage_v": 52.92,
        "temp_c": 31.5,
        "cell_spread_mv": 186.0
      }
    ],
    "env_fault": [
      {
        "minute": 0,
        "soc": 15.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.5,
        "temp_c": 38.5,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 1,
        "soc": 15.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.59,
        "temp_c": 38.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 2,
        "soc": 16.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.68,
        "temp_c": 38.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 3,
        "soc": 17.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.77,
        "temp_c": 38.9,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 4,
        "soc": 18.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.86,
        "temp_c": 39.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 5,
        "soc": 19.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 45.95,
        "temp_c": 39.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 6,
        "soc": 20.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.04,
        "temp_c": 39.3,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 7,
        "soc": 21.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.13,
        "temp_c": 39.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 8,
        "soc": 22.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.22,
        "temp_c": 39.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 9,
        "soc": 23.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.31,
        "temp_c": 39.7,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 10,
        "soc": 24.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.4,
        "temp_c": 39.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 11,
        "soc": 24.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.49,
        "temp_c": 40.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 12,
        "soc": 25.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.58,
        "temp_c": 40.1,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 13,
        "soc": 26.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.67,
        "temp_c": 40.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 14,
        "soc": 27.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.76,
        "temp_c": 40.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 15,
        "soc": 28.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.85,
        "temp_c": 40.5,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 16,
        "soc": 29.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 46.94,
        "temp_c": 40.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 17,
        "soc": 30.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.03,
        "temp_c": 40.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 18,
        "soc": 31.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.12,
        "temp_c": 40.9,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 19,
        "soc": 32.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.21,
        "temp_c": 41.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 20,
        "soc": 33.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.3,
        "temp_c": 41.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 21,
        "soc": 33.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.39,
        "temp_c": 41.3,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 22,
        "soc": 34.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.48,
        "temp_c": 41.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 23,
        "soc": 35.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.57,
        "temp_c": 41.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 24,
        "soc": 36.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.66,
        "temp_c": 41.7,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 25,
        "soc": 37.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.75,
        "temp_c": 41.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 26,
        "soc": 38.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.84,
        "temp_c": 42.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 27,
        "soc": 39.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 47.93,
        "temp_c": 42.1,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 28,
        "soc": 40.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.02,
        "temp_c": 42.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 29,
        "soc": 41.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.11,
        "temp_c": 42.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 30,
        "soc": 42.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.2,
        "temp_c": 42.5,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 31,
        "soc": 42.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.29,
        "temp_c": 42.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 32,
        "soc": 43.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.38,
        "temp_c": 42.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 33,
        "soc": 44.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.47,
        "temp_c": 42.9,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 34,
        "soc": 45.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.56,
        "temp_c": 43.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 35,
        "soc": 46.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.65,
        "temp_c": 43.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 36,
        "soc": 47.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.74,
        "temp_c": 43.3,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 37,
        "soc": 48.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.83,
        "temp_c": 43.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 38,
        "soc": 49.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 48.92,
        "temp_c": 43.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 39,
        "soc": 50.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.01,
        "temp_c": 43.7,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 40,
        "soc": 51.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.1,
        "temp_c": 43.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 41,
        "soc": 51.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.19,
        "temp_c": 44.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 42,
        "soc": 52.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.28,
        "temp_c": 44.1,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 43,
        "soc": 53.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.37,
        "temp_c": 44.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 44,
        "soc": 54.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.46,
        "temp_c": 44.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 45,
        "soc": 55.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.55,
        "temp_c": 44.5,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 46,
        "soc": 56.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.64,
        "temp_c": 44.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 47,
        "soc": 57.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.73,
        "temp_c": 44.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 48,
        "soc": 58.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.82,
        "temp_c": 44.9,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 49,
        "soc": 59.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 49.91,
        "temp_c": 45.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 50,
        "soc": 60.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.0,
        "temp_c": 45.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 51,
        "soc": 60.9,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.09,
        "temp_c": 45.3,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 52,
        "soc": 61.8,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.18,
        "temp_c": 45.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 53,
        "soc": 62.7,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.27,
        "temp_c": 45.6,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 54,
        "soc": 63.6,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.36,
        "temp_c": 45.7,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 55,
        "soc": 64.5,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.45,
        "temp_c": 45.8,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 56,
        "soc": 65.4,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.54,
        "temp_c": 46.0,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 57,
        "soc": 66.3,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.63,
        "temp_c": 46.1,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 58,
        "soc": 67.2,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.72,
        "temp_c": 46.2,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 59,
        "soc": 68.1,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.81,
        "temp_c": 46.4,
        "cell_spread_mv": 15.0
      },
      {
        "minute": 60,
        "soc": 69.0,
        "cmd_current_a": 10.0,
        "dock_current_a": 10.0,
        "pack_current_a": 10.0,
        "pack_voltage_v": 50.9,
        "temp_c": 46.5,
        "cell_spread_mv": 15.0
      }
    ]
  },
  "stations": [
    {
      "id": "STA-01",
      "name": "Taipei Central Hub",
      "docks": 4,
      "status": "NOMINAL",
      "ambient_c": 26.2,
      "grid_v": 220.4
    },
    {
      "id": "STA-02",
      "name": "New Taipei Industrial Station",
      "docks": 4,
      "status": "NOMINAL",
      "ambient_c": 27.1,
      "grid_v": 219.8
    },
    {
      "id": "STA-03",
      "name": "Taoyuan Logistics Corridor",
      "docks": 4,
      "status": "NOMINAL",
      "ambient_c": 28.0,
      "grid_v": 221.1
    },
    {
      "id": "STA-04",
      "name": "Hsinchu Tech Interchange",
      "docks": 4,
      "status": "ATTENTION_REQUIRED",
      "ambient_c": 38.5,
      "grid_v": 218.6
    }
  ],
  "crossingExamples": {
    "dock_isolation": {
      "title": "Dock Current Deficit Follows Dock Across 4 Independent Packs",
      "dockId": "STA-04-DOK-01",
      "sessions": [
        {
          "packId": "PCK-001",
          "dockId": "STA-04-DOK-01",
          "current_a": 8.0,
          "cmd_a": 15.0,
          "is_anomaly": true
        },
        {
          "packId": "PCK-017",
          "dockId": "STA-04-DOK-01",
          "current_a": 8.0,
          "cmd_a": 15.0,
          "is_anomaly": true
        },
        {
          "packId": "PCK-042",
          "dockId": "STA-04-DOK-01",
          "current_a": 7.9,
          "cmd_a": 15.0,
          "is_anomaly": true
        },
        {
          "packId": "PCK-078",
          "dockId": "STA-04-DOK-01",
          "current_a": 8.1,
          "cmd_a": 15.0,
          "is_anomaly": true
        },
        {
          "packId": "PCK-001",
          "dockId": "STA-01-DOK-02",
          "current_a": 14.9,
          "cmd_a": 15.0,
          "is_anomaly": false
        },
        {
          "packId": "PCK-042",
          "dockId": "STA-02-DOK-03",
          "current_a": 15.0,
          "cmd_a": 15.0,
          "is_anomaly": false
        }
      ],
      "conclusion": "Attributed to CHARGER_DOCK with HIGH confidence. All 4 packs underperform on DOK-01, but behave normally when swapped to other docks."
    },
    "pack_isolation": {
      "title": "Pack Thermal Anomaly Follows Battery Across 3 Independent Docks",
      "packId": "STA-04-PCK-017",
      "sessions": [
        {
          "packId": "STA-04-PCK-017",
          "dockId": "STA-04-DOK-01",
          "temp_max_c": 51.4,
          "temp_expected_c": 34.0,
          "is_anomaly": true
        },
        {
          "packId": "STA-04-PCK-017",
          "dockId": "STA-04-DOK-02",
          "temp_max_c": 50.8,
          "temp_expected_c": 33.5,
          "is_anomaly": true
        },
        {
          "packId": "STA-04-PCK-017",
          "dockId": "STA-01-DOK-04",
          "temp_max_c": 52.1,
          "temp_expected_c": 32.8,
          "is_anomaly": true
        },
        {
          "packId": "PCK-005",
          "dockId": "STA-04-DOK-02",
          "temp_max_c": 32.4,
          "temp_expected_c": 33.5,
          "is_anomaly": false
        },
        {
          "packId": "PCK-029",
          "dockId": "STA-01-DOK-04",
          "temp_max_c": 31.9,
          "temp_expected_c": 32.8,
          "is_anomaly": false
        }
      ],
      "conclusion": "Attributed to PACK with HIGH confidence. Severe thermal excess (+18\u00b0C) persists regardless of dock assignment; docks charge other packs normally."
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
};
export default telemetryData;
