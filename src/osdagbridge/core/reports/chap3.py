# =============================================================================
# Chapter 3: Loads and Load Combinations
# Separates Vehicle Live Loads (LL) and Footpath Live Loads (LL) with dedicated
# Parameter, Value, and Unit columns, clean captions, and repeating headers.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, make_longtable


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    vehicles = []
    if input_dict.get(KEY_LL_IRC_CLASS_A):
        vehicles.append("IRC Class A")
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        vehicles.append("IRC Class 70R (Wheeled)")
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        vehicles.append("IRC Class 70R (Tracked)")
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        vehicles.append("IRC Class AA (Wheeled)")
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        vehicles.append("IRC Class AA (Tracked)")
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicles.append("IRC Class SV")
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        vehicles.append("IRC Class 70R (Bogie)")
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicles.append("IRC Class Fatigue")

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            if isinstance(c, dict) and c.get("name"):
                vehicles.append(f"Custom: {c['name']}")
            elif isinstance(c, str) and c.strip():
                vehicles.append(f"Custom: {c.strip()}")

    vehicles_str = ", ".join(vehicles) if vehicles else "None selected"

    span = input_dict.get(KEY_SPAN)
    impact_factor_str = "---"
    if span not in (None, ""):
        try:
            span_m = float(span)
            factors = []
            if input_dict.get(KEY_LL_IRC_CLASS_A):
                im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
                factors.append(f"Class A: {1.0 + im_a:.3f}")
            is_wheeled_heavy = (
                input_dict.get(KEY_LL_IRC_70R_WHEELED)
                or input_dict.get(KEY_LL_IRC_AA_WHEELED)
                or input_dict.get(KEY_LL_IRC_70R_BOGIE)
            )
            is_tracked_heavy = (
                input_dict.get(KEY_LL_IRC_70R_TRACKED)
                or input_dict.get(KEY_LL_IRC_AA_TRACKED)
            )
            if is_wheeled_heavy or is_tracked_heavy:
                im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
                factors.append(f"Class AA / 70R: {1.0 + im_aa:.3f}")
            impact_factor_str = ", ".join(factors) if factors else "---"
        except Exception:
            impact_factor_str = "---"

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    braking_val_str = "N/A"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
            braking_force_kN = braking_force_t * 9.81
            braking_val_str = f"{braking_force_kN:.2f} ({braking_force_t:.2f} t)"
        except Exception:
            braking_val_str = "N/A"

    centrifugal_val_str = "0.00 (Straight Bridge)"

    fp_mode_raw = str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")).strip()
    fp_value_raw = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    footpath_cfg = str(
        input_dict.get("superstructure.footpath", input_dict.get("footpath", ""))
    ).strip()
    fp_pressure_str = "---"
    fp_mode_display = fp_mode_raw if fp_mode_raw else "As per IRC 6"
    fp_applicable_str = (
        footpath_cfg if footpath_cfg and footpath_cfg.lower() != "none"
        else "Applicable if footpath provided"
    )

    if fp_mode_raw.lower() in ("as per irc 6", "as per irc6", "automatic", ""):
        try:
            fp_calc = IRC6_2017.cl_206_1_footway_load()
            fp_pressure_str = f"{fp_calc:.3f}"
        except Exception:
            if fp_value_raw not in (None, ""):
                fp_pressure_str = _tex(fp_value_raw)
    elif fp_value_raw not in (None, ""):
        fp_pressure_str = _tex(fp_value_raw)

    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get("wind_speed")
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    # Store computed fallbacks so _render_value can find them
    if vz_val and not input_dict.get(KEY_WL_HOURLY_MEAN_WIND):
        input_dict[KEY_WL_HOURLY_MEAN_WIND] = f"{float(vz_val):.2f}"
    if pz_val and not input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE):
        input_dict[KEY_WL_HOURLY_WIND_PRESSURE] = f"{float(pz_val):.2f}"

    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get("seismic_zone")
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {
                "Type I – Rocky or Hard": 1,
                "Type II – Medium Soil": 2,
                "Type III – Soft Soil": 3,
            }
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = (
                float(_dl_v)
                if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v
                else 0.0
            )
            _live = (
                float(_ll_v)
                if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v
                else 0.0
            )
            _res = IRC6_2017.cl_218_5_1(
                zone=f"Zone {_z}",
                soil_type=_st,
                dead_load_kN=_dead,
                live_load_kN=_live,
                period_T=float(_tp) if _tp else None,
                damping_percent=float(_damp),
            )
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass
    # Store computed seismic fallbacks so _render_value can find them
    if sl_zone_factor and not input_dict.get(KEY_SL_ZONE_FACTOR):
        input_dict[KEY_SL_ZONE_FACTOR] = f"{float(sl_zone_factor):.4f}"
    if sl_spectral and not input_dict.get(KEY_SL_SPECTRAL_COEFF):
        input_dict[KEY_SL_SPECTRAL_COEFF] = f"{float(sl_spectral):.4f}"
    if sl_ah and not input_dict.get(KEY_SL_HORIZONTAL_COEFF):
        input_dict[KEY_SL_HORIZONTAL_COEFF] = f"{float(sl_ah):.6f}"
    if sl_av and not input_dict.get(KEY_SL_VERTICAL_COEFF):
        input_dict[KEY_SL_VERTICAL_COEFF] = f"{float(sl_av):.6f}"

    _LOAD_LABEL_MAP = {
        "dead_load": "DL",
        "surfacing": "SIDL",
        "live_load": "LL",
        "wind_load": "WL",
        "thermal_load": "TL",
        "vehicle_collision": "VC",
        "barge_impact": "BI",
        "floating_bodies": "FB",
        "seismic": "EQ",
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get("adding")
                rel = val.get("relieving")
                add_s = f"{add:.2f}" if add is not None else "--"
                rel_s = f"{rel:.2f}" if rel is not None else "--"
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return _tex(" + ".join(parts))

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo["factors"])
        lc_rows.append(f"ULS-{i:02d} & {_tex(cases) if cases else '---'} \\\\[6pt]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo["factors"])
        lc_rows.append(f"SLS-{i:02d} & {_tex(cases) if cases else '---'} \\\\[6pt]\n\\hline")
    lc_rows_str = "\n".join(lc_rows)

    t_dl_body = (
        r"\textnormal{Steel Self-Weight Applied} & " + _render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY) + r" & kN/m\textsuperscript{3} \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Concrete Deck Weight} & " + _render_value(input_dict, KEY_MATERIAL_DECK_DENSITY) + r" & kN/m\textsuperscript{3} \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Self-Weight Factor} & " + _render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR) + r" & --- \\[6pt]"
    )
    t_dl = make_longtable(
        "|L{6.0cm}|C{6.5cm}|C{3.0cm}|",
        "Dead Load: Self Weight",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_dl_body,
    )

    t_dw_body = (
        r"\textnormal{Wearing Course Load} & " + _render_value(input_dict, KEY_WC_MATERIAL) + r" x " + _render_value(input_dict, KEY_WC_THICKNESS) + r" & mm \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Additional SIDL (Crash Barrier)} & " + _render_value(input_dict, KEY_CB_LOAD) + r" & kN/m \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Railing Load} & " + _render_value(input_dict, KEY_RL_LOAD_VALUE) + r"\sdstar{} & kN/m \\[6pt]"
    )
    t_dw = make_longtable(
        "|L{6.0cm}|C{6.5cm}|C{3.0cm}|",
        "Dead Load for Surfacing (DW)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_dw_body,
    )

    t_veh_body = (
        r"\textnormal{Selected Vehicle Class(es)} & " + _tex(vehicles_str) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Design Traffic Lanes} & " + (_tex(lanes) if lanes not in (None, "") else "N/A") + r" & Nos. \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Impact Factor (1 + IF, IRC 6 Cl. 208)} & " + _tex(impact_factor_str) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Longitudinal Braking Load (IRC 6 Cl. 211.2)} & " + _tex(braking_val_str) + r" & kN \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Centrifugal Force (IRC 6 Cl. 212)} & " + _tex(centrifugal_val_str) + r" & kN \\[6pt]"
    )
    t_veh = make_longtable(
        "|L{6.2cm}|L{6.8cm}|C{2.5cm}|",
        "Vehicle Live Loads (LL)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_veh_body,
        note="Note: Per IRC 6:2017. Vehicle classes reflect selections in the Loading tab of Additional Inputs.",
    )

    t_fp_body = (
        r"\textnormal{Footpath Configuration} & " + _tex(fp_applicable_str) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Footpath Loading Mode} & " + _tex(fp_mode_display) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Footway Live Load Intensity (IRC 6 Cl. 206.1)} & " + _tex(fp_pressure_str) + r" & kN/m\textsuperscript{2} \\[6pt]"
    )
    t_fp = make_longtable(
        "|L{6.2cm}|L{6.8cm}|C{2.5cm}|",
        "Footpath Live Loads (LL)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_fp_body,
        note="Note: Per IRC 6:2017 Cl. 206.1. Footway loading evaluated separately from vehicular live loads.",
    )

    t_wl_body = (
        r"\textnormal{Basic Wind Speed, Vb} & " + _render_value(input_dict, "wind_speed") + r" [Project Location] & m/s \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Terrain Type} & " + _render_value(input_dict, KEY_WL_TERRAIN_TYPE) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Average Exposed Height, H} & " + _render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT) + r" & m \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Hourly Mean Wind Speed, Vz} & " + (_tex(f"{float(vz_val):.2f}") if vz_val not in (None, "") else "---") + r" & m/s \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Hourly Wind Pressure, Pz} & " + (_tex(f"{float(pz_val):.2f}") if pz_val not in (None, "") else "---") + r" & N/m\textsuperscript{2} \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Transverse Wind Force} & " + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE) if input_dict.get(KEY_WL_TRANSVERSE_WIND_FORCE) not in (None, "") else "N/A") + r" & kN \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Longitudinal Wind Force} & " + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE) if input_dict.get(KEY_WL_LONGITUDINAL_WIND_FORCE) not in (None, "") else "N/A") + r" & kN \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Vertical Wind Force} & " + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE) if input_dict.get(KEY_WL_VERTICAL_WIND_FORCE) not in (None, "") else "N/A") + r" & kN \\[6pt]"
    )
    t_wl = make_longtable(
        "|L{6.0cm}|C{6.5cm}|C{3.0cm}|",
        "Wind Load (WL)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_wl_body,
        note="Note: Evaluated per IRC 6:2017.",
    )

    t_el_body = (
        r"\textnormal{Seismic Zone} & " + _render_value(input_dict, "seismic_zone") + r" [Project Location] & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Zone Factor, Z} & " + (_tex(f"{float(sl_zone_factor):.4f}") if sl_zone_factor not in (None, "") else "---") + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Importance Factor, I} & " + _render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Type of Soil} & " + _render_value(input_dict, KEY_SL_SOIL_TYPE) + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Spectral Acceleration Coeff., Sa/g} & " + (_tex(f"{float(sl_spectral):.4f}") if sl_spectral not in (None, "") else "---") + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Horizontal Seismic Coefficient, Ah} & " + (_tex(f"{float(sl_ah):.6f}") if sl_ah not in (None, "") else "---") + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Vertical Seismic Coefficient, Av} & " + (_tex(f"{float(sl_av):.6f}") if sl_av not in (None, "") else "---") + r" & --- \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Horizontal Seismic Force (Longitudinal)} & N/A & kN \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Horizontal Seismic Force (Transverse)} & N/A & kN \\[6pt]"
    )
    t_el = make_longtable(
        "|L{6.0cm}|C{6.5cm}|C{3.0cm}|",
        "Earthquake Load (EL)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_el_body,
        note="Note: Evaluated per IRC 6:2017.",
    )

    t_tl_body = (
        r"\textnormal{Maximum Shade Temperature} & " + _render_value(input_dict, "shade_temp_max") + r" & $^\circ$C \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Minimum Shade Temperature} & " + _render_value(input_dict, "shade_temp_min") + r" & $^\circ$C \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Effective Bridge Temp. Range} & " + _render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN) + r" to " + _render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX) + r" & $^\circ$C \\[6pt]" + "\n\\hline\n"
        r"\textnormal{Temperature Rise / Fall for Design} & +" + _render_value(input_dict, KEY_TL_TEMP_RISE) + r" / -" + _render_value(input_dict, KEY_TL_TEMP_FALL) + r" & $^\circ$C \\[6pt]"
    )
    t_tl = make_longtable(
        "|L{6.0cm}|C{6.5cm}|C{3.0cm}|",
        "Temperature Load (TL)",
        r"\textbf{Parameter} & \textbf{Value} & \textbf{Unit} \\[6pt]",
        t_tl_body,
        note="Note: Evaluated per IRC 6:2017.",
    )

    t_lc = make_longtable(
        "|C{3.5cm}|L{12.0cm}|",
        "Load Combinations (IRC 6:2017)",
        r"\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]",
        lc_rows_str,
        note="Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.",
    )

    return (
        r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.
"""
        + t_dl
        + t_dw
        + t_veh
        + t_fp
        + t_wl
        + t_el
        + t_tl
        + t_lc
    )