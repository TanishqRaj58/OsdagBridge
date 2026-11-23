# =============================================================================
# Chapter 5: Design Checks
# Uses centralized styles, repeating longtable headers, multi-row block
# protection, clean math/comparison notes, and single Section 5.5 UR chart.
# =============================================================================
from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional

from osdagbridge.core.utils.common import (
    KEY_DD_AS_BOT,
    KEY_DD_AS_LONG,
    KEY_DD_AS_MIN,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_AS_TOP,
    KEY_DD_COVER_OK,
    KEY_DD_DIA_BOT,
    KEY_DD_D_BOT,
    KEY_DD_FY,
    KEY_DD_GAMMA_DL,
    KEY_DD_GAMMA_LL,
    KEY_DD_HAS_OVERHANG,
    KEY_DD_IMPACT_FACTOR,
    KEY_DD_MIN_COVER,
    KEY_DD_MU_BOT,
    KEY_DD_MU_OH,
    KEY_DD_MU_TOP,
    KEY_DD_M_BARRIER,
    KEY_DD_M_DL,
    KEY_DD_M_DL_OH,
    KEY_DD_M_LL,
    KEY_DD_M_LL_OH,
    KEY_DD_M_ULS_HOG,
    KEY_DD_M_ULS_OH,
    KEY_DD_M_ULS_SAG,
    KEY_DD_PUNCH_C1,
    KEY_DD_PUNCH_C2,
    KEY_DD_PUNCH_OK,
    KEY_DD_PUNCH_U1,
    KEY_DD_PUNCH_VED,
    KEY_DD_PUNCH_VED_KN,
    KEY_DD_SHEAR_OK,
    KEY_DD_SHEAR_VED,
    KEY_DD_SHEAR_VRDC,
    KEY_DD_SPACING_MAX,
    KEY_DD_SPAN,
    KEY_DD_SPC_BOT,
    KEY_DD_TYRE_LENGTH,
    KEY_DD_TYRE_WIDTH,
    KEY_DD_VEHICLE,
    KEY_DD_VRD_C_MPA,
    KEY_DD_WDL,
    KEY_DD_WHEEL_LOAD,
    KEY_DD_WK_BOT,
    KEY_DD_WK_LIMIT,
    KEY_DD_WK_OH,
    KEY_DD_WK_TOP,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DS_BOTTOM_CLEAR_COVER,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_STUD_DIAMETER,
    KEY_DS_TOP_CLEAR_COVER,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MP_ED_TYPE,
    KEY_SD_BOTTOM_FLANGE_THICKNESS,
    KEY_SD_BOTTOM_FLANGE_WIDTH,
    KEY_SD_BS_FCD,
    KEY_SD_BS_FCDW_LC,
    KEY_SD_BS_FCDW_WB,
    KEY_SD_BS_FPSD,
    KEY_SD_BS_R,
    KEY_SD_CLASS_FLANGE,
    KEY_SD_CLASS_WEB,
    KEY_SD_COMPOSITE_IZ,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
    KEY_SD_EFFECTIVE_SLAB_WIDTH,
    KEY_SD_FLANGE_CLASS_LIMIT,
    KEY_SD_FLANGE_SLENDERNESS,
    KEY_SD_HIGH_SHEAR,
    KEY_SD_IS_FQ,
    KEY_SD_IS_FQD,
    KEY_SD_IS_IYS_MIN,
    KEY_SD_IS_IYS_PROV,
    KEY_SD_LTB_CHI,
    KEY_SD_LTB_LAMBDA,
    KEY_SD_LTB_MB,
    KEY_SD_LTB_MCR,
    KEY_SD_MDV,
    KEY_SD_MD_CAPACITY,
    KEY_SD_MN_AXIAL,
    KEY_SD_MN_MOMENT,
    KEY_SD_MN_RATIO,
    KEY_SD_MU_APPLIED,
    KEY_SD_PANEL_CD,
    KEY_SD_PNA_DEPTH,
    KEY_SD_SC_D_LIMIT,
    KEY_SD_SC_EDGE_DIST,
    KEY_SD_SC_Qr_kN,
    KEY_SD_SC_Qu_kN,
    KEY_SD_SC_REQ_EDGE_DIST,
    KEY_SD_SC_SL1,
    KEY_SD_SC_SL2,
    KEY_SD_SC_SR,
    KEY_SD_SECTION_CLASS,
    KEY_SD_SECTION_PROP_AREA,
    KEY_SD_SECTION_PROP_IZ,
    KEY_SD_SECTION_PROP_ZUZ,
    KEY_SD_SECTION_PROP_ZZ,
    KEY_SD_SHEAR_AV,
    KEY_SD_SHEAR_KV,
    KEY_SD_SHEAR_LAMBDA_W,
    KEY_SD_SHEAR_TAU_B,
    KEY_SD_SHEAR_VCR,
    KEY_SD_SHEAR_VU,
    KEY_SD_STIFF_END_COUNT,
    KEY_SD_STIFF_END_THICK,
    KEY_SD_STIFF_INT_SPACING,
    KEY_SD_STIFF_INT_THICK,
    KEY_SD_STIFF_LONG,
    KEY_SD_STIFF_METHOD,
    KEY_SD_STRESS_STEEL,
    KEY_SD_STRESS_STEEL_ALLOWABLE,
    KEY_SD_TOP_FLANGE_THICKNESS,
    KEY_SD_TOP_FLANGE_WIDTH,
    KEY_SD_TOTAL_DEPTH,
    KEY_SD_TS_VL,
    KEY_SD_TS_VRD,
    KEY_SD_ULS_PER_GIRDER,
    KEY_SD_WEB_CLASS_LIMIT,
    KEY_SD_WEB_SLENDERNESS,
    KEY_SD_WEB_THICKNESS,
    KEY_SPAN,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_NO_OF_GIRDERS,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_LTB,
    KEY_UTIL_SHEAR,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, _format_lc, get_girder_entries, _fig_embed
from osdagbridge.core.reports.styles import make_longtable
from osdagbridge.core.reports.charts import generate_ur_summary_chart

if TYPE_CHECKING:
    pass


def _multirow_group(count: int, label: str, subrows: list[str], cline_range: str) -> str:
    """Place the girder label on the first row without \\multirow so it never bleeds into the footer."""
    if not subrows:
        return ""
    parts = [r"\textbf{" + label + r"}" + subrows[0]]
    for sr in subrows[1:]:
        parts.append(f"\\cline{{{cline_range}}}" + sr)
    parts.append(r"\hline")
    return "\n".join(parts)


def ch5_design_checks(checks_data, bridge, fig_paths: Optional[dict] = None) -> str:
    """Chapter 5 — Design Checks."""
    fig_paths = fig_paths or {}
    girder_entries = get_girder_entries(bridge.input_dict)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1) or 1)
        girder_entries = [(f"Girder {i}", "M1") for i in range(1, n + 1)]

    deck_rpt = bridge.output_dict.get("deck_report_values", {}) or {}

    # Table 5.1 rows
    t51_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & \textnormal{Depth, D (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOTAL_DEPTH) + r" \\*[6pt]",
            r" & \textnormal{Top Flange Width, $b_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOP_FLANGE_WIDTH) + r" \\*[6pt]",
            r" & \textnormal{Bottom Flange Width, $b_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_BOTTOM_FLANGE_WIDTH) + r" \\*[6pt]",
            r" & \textnormal{Top Flange Thickness, $t_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_TOP_FLANGE_THICKNESS) + r" \\*[6pt]",
            r" & \textnormal{Bottom Flange Thickness, $t_f$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_BOTTOM_FLANGE_THICKNESS) + r" \\*[6pt]",
            r" & \textnormal{Web Thickness, $t_w$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_WEB_THICKNESS) + r" \\*[6pt]",
            r" & \textnormal{Gross Area, A (cm$^2$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_AREA) + r" \\*[6pt]",
            r" & \textnormal{Moment of Inertia, $I_z$ (cm$^4$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_IZ) + r" \\*[6pt]",
            r" & \textnormal{Elastic Section Modulus, $Z_{ez}$ (cm$^3$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_ZZ) + r" \\*[6pt]",
            r" & \textnormal{Plastic Section Modulus, $Z_{pz}$ (cm$^3$)} & " + _render_value(bridge.output_dict, KEY_SD_SECTION_PROP_ZUZ) + r" \\*[6pt]",
            r" & \textnormal{Effective Slab Width, $b_{eff}$ (mm)} & " + _render_value(bridge.output_dict, KEY_SD_EFFECTIVE_SLAB_WIDTH) + r" \\*[6pt]",
            r" & \textnormal{Transformed Composite $I_z$ (cm$^4$)} & " + _render_value(bridge.output_dict, KEY_SD_COMPOSITE_IZ) + r" \\*[6pt]",
            r" & \textnormal{Depth to Plastic Neutral Axis (mm)} & " + _render_value(bridge.output_dict, KEY_SD_PNA_DEPTH) + r" \\[6pt]",
        ]
        t51_rows.append(_multirow_group(13, _tex(lbl), sub, "2-3"))
    t51_content = "\n".join(t51_rows)

    # Table 5.2 rows
    t52_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Top Flange & " + _render_value(bridge.output_dict, KEY_SD_FLANGE_SLENDERNESS) + r" & " + _render_value(bridge.output_dict, KEY_SD_FLANGE_CLASS_LIMIT) + r" & " + _render_value(bridge.output_dict, KEY_SD_CLASS_FLANGE) + r" \\*[6pt]",
            r" & Web & " + _render_value(bridge.output_dict, KEY_SD_WEB_SLENDERNESS) + r" & " + _render_value(bridge.output_dict, KEY_SD_WEB_CLASS_LIMIT) + r" & " + _render_value(bridge.output_dict, KEY_SD_CLASS_WEB) + r" \\*[6pt]",
            r" & Overall Section & --- & --- & " + _render_value(bridge.output_dict, KEY_SD_SECTION_CLASS) + r" \\[6pt]",
        ]
        t52_rows.append(_multirow_group(3, _tex(lbl), sub, "2-5"))
    t52_content = "\n".join(t52_rows)

    # Table 5.3 rows
    try:
        _flex_ur = float(bridge.output_dict.get(KEY_UTIL_FLEXURE)) / 100.0
        _flex_ur_str = f"{_flex_ur:.2f}"
        _flex_status = "PASS" if _flex_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _flex_ur_str = "---"
        _flex_status = "---"
    t53_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Applied Moment, $M_u$ & Governing LC (ULS) & " + _render_value(bridge.output_dict, KEY_SD_MU_APPLIED, " kN-m") + r" & --- \\*[6pt]",
            r" & Design Moment Capacity, $M_d$ & IRC 22 Cl. 603.3.1 & " + _render_value(bridge.output_dict, KEY_SD_MD_CAPACITY, " kN-m") + r" & --- \\*[6pt]",
            r" & Utilization Ratio, $M_u / M_d$ & $M_u / M_d$ & " + _flex_ur_str + r" & " + _flex_status + r" \\[6pt]",
        ]
        t53_rows.append(_multirow_group(3, _tex(lbl), sub, "2-5"))
    t53_content = "\n".join(t53_rows)

    # Table 5.4 rows
    try:
        _shear_ur = float(bridge.output_dict.get(KEY_UTIL_SHEAR)) / 100.0
        _shear_ur_str = f"{_shear_ur:.2f}"
        _shear_status = "PASS" if _shear_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _shear_ur_str = "---"
        _shear_status = "---"
    t54_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Applied Shear, $V_u$ & Governing LC (ULS) & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_VU, " kN") + r" & --- \\*[6pt]",
            r" & Shear Area, $A_v$ & $d_w \times t_w$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_AV, " mm$^2$") + r" & --- \\*[6pt]",
            r" & Panel Aspect Ratio, c/d & --- & " + _render_value(bridge.output_dict, KEY_SD_PANEL_CD) + r" & --- \\*[6pt]",
            r" & Shear Buckling Coefficient, $k_v$ & IS 800 Cl. 8.4.2.2 & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_KV) + r" & --- \\*[6pt]",
            r" & Web Slenderness, $\lambda_w$ & $\sqrt{f_{yw}/(\sqrt{3}\,\tau_{cr})}$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_LAMBDA_W) + r" & --- \\*[6pt]",
            r" & Design Shear Stress, $\tau_b$ & IRC 22 Cl. 603.3.3.2 & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_TAU_B, " MPa") + r" & --- \\*[6pt]",
            r" & Shear Buckling Resistance, $V_{cr}$ & $A_v \times \tau_b$ & " + _render_value(bridge.output_dict, KEY_SD_SHEAR_VCR, " kN") + r" & --- \\*[6pt]",
            r" & Utilization Ratio, $V_u / V_d$ & $V_u / V_d$ & " + _shear_ur_str + r" & " + _shear_status + r" \\[6pt]",
        ]
        t54_rows.append(_multirow_group(8, _tex(lbl), sub, "2-5"))
    t54_content = "\n".join(t54_rows)

    # Table 5.5 rows
    def _interaction_status(ratio):
        if ratio < 0.90:
            return "PASS"
        elif ratio < 1.00:
            return "WARN"
        return r"\textcolor{red}{FAIL}"

    try:
        _mv_ur = float(bridge.output_dict.get(KEY_UTIL_INTERACTION)) / 100.0
        _mv_ur_str = f"{_mv_ur:.2f}"
        _mv_status = _interaction_status(_mv_ur)
    except (TypeError, ValueError):
        _mv_ur_str = "---"
        _mv_status = "---"

    _mn_r = bridge.output_dict.get(KEY_SD_MN_RATIO)
    _mn_ax = bridge.output_dict.get(KEY_SD_MN_AXIAL)
    _mn_mo = bridge.output_dict.get(KEY_SD_MN_MOMENT)
    if _mn_r is None or _mn_ax is None or _mn_mo is None:
        _mn_cond = _mn_val = _mn_status = "N/A"
    else:
        _mn_cond = f"{_mn_ax:.2f} + {_mn_mo:.2f} = {_mn_r:.3f}"
        _mn_val = f"{_mn_r:.3f}"
        _mn_status = _interaction_status(_mn_r)

    t55_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & High Shear Condition? & $V_u > 0.6\,V_d$ & " + _render_value(bridge.output_dict, KEY_SD_HIGH_SHEAR) + r" & --- \\*[6pt]",
            r" & Reduced Moment Capacity, $M_{dv}$ & IRC 22 Cl. 603.3.3.3 & " + _render_value(bridge.output_dict, KEY_SD_MDV, " kN-m") + r" & --- \\*[6pt]",
            r" & Interaction Check: $M_u \leq M_{dv}$ & --- & " + _mv_ur_str + r" & " + _mv_status + r" \\*[6pt]",
            r" & Interaction Check: $N_u/N_{Rd} + M_u/M_{dv} \leq 1.0$ & " + _mn_cond + r" & " + _mn_val + r" & " + _mn_status + r" \\[6pt]",
        ]
        t55_rows.append(_multirow_group(4, _tex(lbl), sub, "2-5"))
    t55_content = "\n".join(t55_rows)

    # Table 5.6 rows
    try:
        _ltb_ur = float(bridge.output_dict.get(KEY_UTIL_LTB)) / 100.0
        _ltb_ur_str = f"{_ltb_ur:.2f}"
        _ltb_status = _interaction_status(_ltb_ur)
    except (TypeError, ValueError):
        _ltb_ur_str = "---"
        _ltb_status = "---"
    t56_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Elastic Critical Moment, $M_{cr}$ & IRC 22 Cl. 603.3.3.1 & " + _render_value(bridge.output_dict, KEY_SD_LTB_MCR, " kN-m") + r" & --- \\*[6pt]",
            r" & Non-dim. Slenderness, $\bar{\lambda}_{LT}$ & $\sqrt{M_p / M_{cr}}$ & " + _render_value(bridge.output_dict, KEY_SD_LTB_LAMBDA) + r" & --- \\*[6pt]",
            r" & LTB Reduction Factor, $\chi_{LT}$ & IS 800 Cl. 8.2.2 & " + _render_value(bridge.output_dict, KEY_SD_LTB_CHI) + r" & --- \\*[6pt]",
            r" & LTB Resistance, $M_b$ & $\chi_{LT}\,M_p / \gamma_{m0}$ & " + _render_value(bridge.output_dict, KEY_SD_LTB_MB, " kN-m") + r" & --- \\*[6pt]",
            r" & $M_u \leq M_b$ & $M_u / M_b$ & " + _ltb_ur_str + r" & " + _ltb_status + r" \\[6pt]",
        ]
        t56_rows.append(_multirow_group(5, _tex(lbl), sub, "2-5"))
    t56_content = "\n".join(t56_rows)

    # Table 5.7 rows
    t57_rows = []
    _stiff_m = bridge.output_dict.get(KEY_SD_STIFF_METHOD)
    if str(_stiff_m).lower() == "post_critical":
        _stiff_m_str = "Post-Critical"
    else:
        _stiff_m_str = _render_value(bridge.output_dict, KEY_SD_STIFF_METHOD)

    _stiff_sp = bridge.output_dict.get(KEY_SD_STIFF_INT_SPACING)
    if _stiff_sp in ("", None):
        _stiff_key = globals().get("KEY_MP_STIFFENER_INTERMEDIATE_SPACING", "Member.PlateGirder.Stiffener.Intermediate.Spacing")
        _stiff_sp = (bridge.input_dict.get(f"{_stiff_key}.G1.M1") if getattr(bridge, "input_dict", None) else None) or "2030 mm"
        if not str(_stiff_sp).endswith("mm") and _stiff_sp != "---":
            _stiff_sp = f"{_stiff_sp} mm"
        _stiff_sp_str = _tex(_stiff_sp)
    else:
        _stiff_sp_str = _render_value(bridge.output_dict, KEY_SD_STIFF_INT_SPACING)

    for lbl, _ in girder_entries:
        sub = [
            r" & \textnormal{Shear Buckling Design Method} & " + _stiff_m_str + r" \\*[6pt]",
            r" & \textnormal{Intermediate Stiffener Thickness (mm)} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_INT_THICK) + r" \\*[6pt]",
            r" & \textnormal{Intermediate Stiffener Spacing (mm)} & " + _stiff_sp_str + r" \\*[6pt]",
            r" & \textnormal{End Panel Stiffener Thickness (mm)} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_END_THICK) + r" \\*[6pt]",
            r" & \textnormal{No. of End Panel Stiffeners} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_END_COUNT) + r" \\*[6pt]",
            r" & \textnormal{Longitudinal Stiffeners} & " + _render_value(bridge.output_dict, KEY_SD_STIFF_LONG) + r" \\[6pt]",
        ]
        t57_rows.append(_multirow_group(6, _tex(lbl), sub, "2-3"))
    t57_content = "\n".join(t57_rows)

    # Table 5.8 (Custom mode only)
    def _ge_status(provided, required):
        try:
            return "PASS" if float(provided) >= float(required) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    _iys_status = _ge_status(bridge.output_dict.get(KEY_SD_IS_IYS_PROV), bridge.output_dict.get(KEY_SD_IS_IYS_MIN))
    _fqd_status = _ge_status(bridge.output_dict.get(KEY_SD_IS_FQD), bridge.output_dict.get(KEY_SD_IS_FQ))
    t58_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Min. Moment of Inertia, $I_s$ & " + _render_value(bridge.output_dict, KEY_SD_IS_IYS_MIN, " mm$^4$") + r" & " + _render_value(bridge.output_dict, KEY_SD_IS_IYS_PROV, " mm$^4$") + r" & " + _iys_status + r" \\*[6pt]",
            r" & Buckling Resistance, $F_{qd} \geq F_q$ & " + _render_value(bridge.output_dict, KEY_SD_IS_FQ, " kN") + r" & " + _render_value(bridge.output_dict, KEY_SD_IS_FQD, " kN") + r" & " + _fqd_status + r" \\[6pt]",
        ]
        t58_rows.append(_multirow_group(2, _tex(lbl), sub, "2-5"))
    t58_content = "\n".join(t58_rows)
    _is_custom = str(bridge.input_dict.get(KEY_DESIGN_MODE, "Optimized")).strip().lower() in {"custom", "customized"}
    t58_block = (
        make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Intermediate Stiffener Checks",
            r"\textbf{Girder} & \textbf{Check} & \textbf{Required} & \textbf{Provided} & \textbf{Status} \\[6pt]",
            t58_content,
            note="Note: IS 800 Cl. 8.7.1.2.",
        )
        if _is_custom else ""
    )

    # Table 5.9 rows
    _bs_r = bridge.output_dict.get(KEY_SD_BS_R)

    def _bs_check(resist_key):
        prov = bridge.output_dict.get(resist_key)
        if prov is None or float(prov) <= 0.0 or _bs_r is None:
            return ("N/A", "N/A", "N/A")
        req_s = f"{_bs_r} kN"
        prov_s = f"{prov} kN"
        status = "PASS" if float(prov) >= float(_bs_r) else r"\textcolor{red}{FAIL}"
        return (req_s, prov_s, status)

    _wb_req, _wb_prov, _wb_st = _bs_check(KEY_SD_BS_FCDW_WB)
    _lc_req, _lc_prov, _lc_st = _bs_check(KEY_SD_BS_FCDW_LC)
    _ps_req, _ps_prov, _ps_st = _bs_check(KEY_SD_BS_FPSD)
    _cb_req, _cb_prov, _cb_st = _bs_check(KEY_SD_BS_FCD)
    t59_rows = []
    for lbl, _ in girder_entries:
        sub = [
            r" & Web Buckling Resistance & " + _wb_req + r" & " + _wb_prov + r" & " + _wb_st + r" \\*[6pt]",
            r" & Local Crushing Resistance & " + _lc_req + r" & " + _lc_prov + r" & " + _lc_st + r" \\*[6pt]",
            r" & Bearing Capacity & " + _ps_req + r" & " + _ps_prov + r" & " + _ps_st + r" \\*[6pt]",
            r" & Column Buckling Resistance & " + _cb_req + r" & " + _cb_prov + r" & " + _cb_st + r" \\[6pt]",
        ]
        t59_rows.append(_multirow_group(4, _tex(lbl), sub, "2-5"))
    t59_content = "\n".join(t59_rows)

    # Table 5.10 rows
    def _defl_status(actual, allowable):
        try:
            return "PASS" if float(actual) <= float(allowable) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    def _dfmt(v, nd=2):
        try:
            return f"{float(v):.{nd}f}"
        except (TypeError, ValueError):
            return "---"

    try:
        _span_m = float(bridge.input_dict.get(KEY_SPAN))
        _allow_live_mm = _span_m * 1000.0 / 800.0
        _allow_total_mm = _span_m * 1000.0 / 600.0
    except (TypeError, ValueError):
        _allow_live_mm = _allow_total_mm = None
    _allow_live_str = f"L/800 = {_allow_live_mm:.1f} mm" if _allow_live_mm is not None else "---"
    _allow_total_str = f"L/600 = {_allow_total_mm:.1f} mm" if _allow_total_mm is not None else "---"

    t510_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _live_mm = bridge.output_dict.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _total_mm = bridge.output_dict.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        sub = [
            r" & Live Load Deflection, $\delta_{LL}$ (mm) & " + _allow_live_str + r" & " + _dfmt(_live_mm, nd=3) + r" & " + _defl_status(_live_mm, _allow_live_mm) + r" \\*[6pt]",
            r" & Total Load Deflection, $\delta_{total}$ (mm) & " + _allow_total_str + r" & " + _dfmt(_total_mm, nd=3) + r" & " + _defl_status(_total_mm, _allow_total_mm) + r" \\[6pt]",
        ]
        t510_rows.append(_multirow_group(2, _tex(lbl), sub, "2-5"))
    t510_content = "\n".join(t510_rows)

    # Table 5.11 rows
    def _mpa(v):
        s = _dfmt(v, nd=2)
        return (s + " MPa") if s and s != "---" else "---"

    def _stress_status(actual, allow):
        try:
            return "PASS" if float(actual) <= float(allow) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    _dr_511 = bridge.output_dict.get("design_results", {}) or {}
    _steel_sigma = _dr_511.get(KEY_SD_STRESS_STEEL)
    _steel_allow = _dr_511.get(KEY_SD_STRESS_STEEL_ALLOWABLE)
    _steel_sig_str = _mpa(_steel_sigma)
    _steel_alw_str = _mpa(_steel_allow)
    _steel_status = _stress_status(_steel_sigma, _steel_allow)

    t511_rows = []
    for lbl, _ in girder_entries:
        t511_rows.append(
            _tex(lbl) + r" & Structural Steel ($0.9\,f_y$) & "
            + _steel_alw_str + r" & " + _steel_sig_str + r" & " + _steel_status + r" \\[6pt]\hline"
        )
    t511_content = "\n".join(t511_rows)

    # Table 5.12 rows
    _fat_cat = ((bridge.output_dict.get("design_results", {}) or {})
                .get(KEY_SD_ULS_PER_GIRDER, {}) or {}).get("fatigue", {}) or {}

    def _fat_status(s):
        if s is None or str(s).strip() == "":
            return "---"
        return r"\textcolor{red}{" + _tex(s) + "}" if "FAIL" in str(s).upper() else _tex(s)

    t512_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _g = _fat_cat.get(f"G{_gi}", {}) or {}
        t512_rows.append(
            _tex(lbl) + r" & "
            + _mpa(_g.get("demand")) + r" & "
            + _mpa(_g.get("capacity")) + r" & "
            + _dfmt(_g.get("ur"), nd=2) + r" & "
            + _fat_status(_g.get("status")) + r" \\[6pt]\hline"
        )
    t512_content = "\n".join(t512_rows)

    # Table 5.13 rows
    _pg_summary = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}

    def _with_unit(value, unit):
        s = _dfmt(value, nd=2)
        if not s or s == "---":
            return "---"
        return (s + " " + _tex(unit)) if unit and str(unit) not in ("-", "–") else s

    g_summary_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_data = _pg_summary.get(f"G{_gi}", {}) or {}
        checks = g_data.get("checks") or []
        if not checks:
            g_summary_rows.append(_tex(lbl) + r" & --- & --- & --- & --- & --- & --- \\[6pt]\hline")
            continue

        ctrl = max(checks, key=lambda c: c.get("dcr") or 0.0)
        ctrl_lc, best_dcr = None, None
        for lc_name, lc_data in (g_data.get("per_lc") or {}).items():
            if str(lc_name).lower().startswith("envelope"):
                continue
            for chk in lc_data.get("checks") or []:
                if chk.get("id") == ctrl.get("check_id"):
                    d = chk.get("dcr") or 0.0
                    if best_dcr is None or d > best_dcr:
                        best_dcr, ctrl_lc = d, lc_name
        if ctrl_lc is None:
            ctrl_lc = (g_data.get("demand") or {}).get("governing_combination") or "---"

        g_summary_rows.append(
            _tex(lbl) + r" & " + _tex(str(ctrl_lc)) + r" & " + _tex(str(ctrl.get("name", "---")))
            + r" & " + _with_unit(ctrl.get("demand"), ctrl.get("demand_unit"))
            + r" & " + _with_unit(ctrl.get("capacity"), ctrl.get("capacity_unit"))
            + r" & " + _dfmt(ctrl.get("dcr"), nd=3)
            + r" & " + _fat_status(ctrl.get("status")) + r" \\[6pt]\hline"
        )
    g_summary_table_content = "\n".join(g_summary_rows)

    # Tables 5.14, 5.15, 5.16
    def _kn(v):
        s = _dfmt(v, nd=2)
        return (s + " kN") if s and s != "---" else "---"

    t514_content = (
        r"Design Resistance, $Q_u$ & \footnotesize\makecell{$Q_u=\min(Q_{u,s},\,Q_{u,c})$\\[3pt]$Q_{u,s} = 0.8\,f_u(\pi d^2/4)/\gamma_v$\\[3pt]$Q_{u,c} = 0.29\,\alpha\,d^2\sqrt{f_{ck}\,E_{cm}}/\gamma_v$} & "
        + _kn(_dr_511.get(KEY_SD_SC_Qu_kN)) + r" & IRC 22 Cl. 606.3.1 (Eq. 6.1) \\[6pt]\hline" + "\n"
        r"Fatigue Shear Resistance, $Q_r$ & IRC 22 Table 8 ($\phi d$, $N_{sc}$) & "
        + _kn(_dr_511.get(KEY_SD_SC_Qr_kN)) + r" & IRC 22 Cl. 606.3.2 (Table 8) \\[6pt]\hline"
    )

    def _mm(v):
        s = _dfmt(v, nd=1)
        return (s + " mm") if s and s != "---" else "---"

    _sc_prov = _dr_511.get("stud_spacing_provided_mm")
    _sc_prov_str = _mm(_sc_prov)

    def _sp_row(crit, req):
        return (
            crit + r" & " + _mm(req) + r" & " + _sc_prov_str + r" & "
            + _defl_status(_sc_prov, req) + r" \\[6pt]"
        )

    t515_content = (
        _sp_row("ULS Shear (SL1)", _dr_511.get(KEY_SD_SC_SL1)) + "\n\\hline\n"
        + _sp_row("Full Composite (SL2)", _dr_511.get(KEY_SD_SC_SL2)) + "\n\\hline\n"
        + _sp_row("SLS Fatigue (SR)", _dr_511.get(KEY_SD_SC_SR)) + "\n\\hline\n"
        + _sp_row("Max Spacing Limit (IRC 22)", _dr_511.get("stud_spacing_max_mm")) + "\n\\hline"
    )

    def _cm2m(v):
        s = _dfmt(v, nd=2)
        return (s + r" cm$^2$/m") if s and s != "---" else "---"

    def _knm(v):
        s = _dfmt(v, nd=2)
        return (s + " kN/m") if s and s != "---" else "---"

    _ts_vl = _dr_511.get(KEY_SD_TS_VL)
    _ts_vrd = _dr_511.get(KEY_SD_TS_VRD)
    if _ts_vl is not None and _ts_vrd is not None:
        try:
            _ts_vl_f = float(_ts_vl)
            _ts_vrd_f = float(_ts_vrd)
            _ts_ur_str = f"{_ts_vl_f / _ts_vrd_f:.2f}" if _ts_vrd_f > 0.0 else "---"
        except (TypeError, ValueError):
            _ts_ur_str = "---"
    else:
        _ts_ur_str = "---"
    _ts_ok = _dr_511.get("transverse_shear_ok")
    _ts_status = (r"\textcolor{red}{FAIL}" if _ts_ok is False else "PASS") if _ts_ok is not None else "---"

    _ast_req = _dr_511.get("Ast_required_cm2_per_m")
    _dd_516 = bridge.output_dict.get("deck_design_results", {}) or {}
    try:
        _ast_prov = (
            float(_dd_516.get("rebar_bottom_area") or 0)
            + float(_dd_516.get("rebar_top_area") or 0)
        ) / 100.0
    except (TypeError, ValueError):
        _ast_prov = None
    _stud_d = bridge.input_dict.get(KEY_DS_STUD_DIAMETER)
    _d_lim = _dr_511.get(KEY_SD_SC_D_LIMIT)
    _edge = _dr_511.get(KEY_SD_SC_EDGE_DIST)
    _edge_req = _dr_511.get(KEY_SD_SC_REQ_EDGE_DIST)

    def _row516(check, value, status):
        return check + r" & " + value + r" & " + status + r" \\[6pt]"

    t516_content = (
        _row516(r"\textnormal{Longitudinal Shear per unit length, $V_L$}", _knm(_ts_vl), "---") + "\n\\hline\n"
        + _row516(r"\textnormal{Transverse Shear Capacity of Slab, $V_{Rd}$}", _knm(_ts_vrd), "---") + "\n\\hline\n"
        + _row516(r"\textnormal{Transverse Shear Check}", r"$V_L/V_{Rd}$ = " + _ts_ur_str, _ts_status) + "\n\\hline\n"
        + _row516(
            r"\textnormal{Min. Transverse Reinforcement, $A_{st,min}$}",
            r"Required " + _cm2m(_ast_req) + r", Provided " + _cm2m(_ast_prov),
            _defl_status(_ast_req, _ast_prov),
        ) + "\n\\hline\n"
        + _row516(
            r"\textnormal{Stud Diameter $\leq 2\,t_f$}",
            r"$d$ = " + _mm(_stud_d) + r" $\leq 2t_f$ = " + _mm(_d_lim),
            _defl_status(_stud_d, _d_lim),
        ) + "\n\\hline\n"
        + _row516(
            r"\textnormal{Stud Edge Distance}",
            r"Provided " + _mm(_edge) + r" (req. $\ge " + (_dfmt(_edge_req, nd=1) if _edge_req is not None else "25.0") + r"\text{ mm}$)",
            _defl_status(_edge_req, _edge),
        ) + "\n\\hline"
    )

    # Cross Bracing & End Diaphragm tables
    cb_forces_rows = []
    pairs = bridge.get_cb_pairs()
    if not pairs:
        cb_forces_rows.append(r"Between Girders & Diagonal & --- & --- & --- & --- \\[6pt]\hline")
    else:
        for pair in pairs:
            pair_id = pair.replace("-", "")
            for member, label in [("diagonal", "Diagonal"), ("chord", "Top / Bottom chord")]:
                _, ftype = bridge.get_cb_governing_force(pair, member)
                conn_type = _tex(bridge.get_cb_connection(pair, member, ftype) or "---")
                section = bridge.get_cb_section(pair, member, ftype) or "---"
                if member == "diagonal":
                    pfx = f"transverse_member_design.cb.section_properties.bracing.{pair_id}"
                else:
                    pfx = f"transverse_member_design.cb.section_properties.bottom_chord.{pair_id}"
                    if bridge.output_dict.get(f"{pfx}.A") is None:
                        pfx = f"transverse_member_design.cb.section_properties.top_chord.{pair_id}"
                area_cm2 = bridge.output_dict.get(f"{pfx}.A")
                rv_cm = bridge.output_dict.get(f"{pfx}.rv")
                area_str = f"{float(area_cm2) * 100:.1f}" if area_cm2 is not None else "---"
                rmin_str = f"{float(rv_cm) * 10:.1f}" if rv_cm is not None else "---"
                cb_forces_rows.append(
                    r"\multirow{2}{*}{\makecell{" + _tex(pair) + r"}} & "
                    + label + r" & " + conn_type + r" & " + section
                    + r" & " + area_str + r" & " + rmin_str
                    + r" \\*[6pt]\cline{2-6}\nopagebreak"
                )
            cb_forces_rows[-1] = cb_forces_rows[-1].replace(r"\cline{2-6}\nopagebreak", r"\hline")
    cb_forces_content = "\n".join(cb_forces_rows)

    def get_status_str(slnd_str, limit):
        try:
            v = float(slnd_str)
            return r"\textcolor{black}{PASS}" if v <= limit else r"\textcolor{red}{FAIL}"
        except (ValueError, TypeError):
            return "---"

    cb_slenderness_rows = []
    if not pairs:
        cb_slenderness_rows.append(r"Between Girders & Diagonal & C & --- & --- & --- \\[6pt]\hline")
    else:
        for pair in pairs:
            kl_diag = bridge.get_cb_effective_length("diagonal") or "---"
            slnd_diag = bridge.get_cb_slenderness(pair, "diagonal") or "---"
            status_diag = get_status_str(slnd_diag, 250)
            kl_tc = bridge.get_cb_effective_length("chord") or "---"
            slnd_tc = bridge.get_cb_slenderness(pair, "chord") or "---"
            status_tc = get_status_str(slnd_tc, 250)
            kl_bc = bridge.get_cb_effective_length("chord") or "---"
            slnd_bc = bridge.get_cb_slenderness(pair, "chord") or "---"
            status_bc = get_status_str(slnd_bc, 400)
            top_chord_enabled = bridge.output_dict.get("member_properties.cross_bracing_details.top_chord", True)
            bottom_chord_enabled = bridge.output_dict.get("member_properties.cross_bracing_details.bottom_chord", True)
            num_rows = 1 + int(bool(top_chord_enabled)) + int(bool(bottom_chord_enabled))
            row_tex = r"\multirow{" + str(num_rows) + r"}{*}{\makecell{" + _tex(pair) + r"}}"
            row_tex += f" & Diagonal & C & {kl_diag} & {slnd_diag} & 250 --- {status_diag} \\\\*[6pt]"
            if top_chord_enabled:
                row_tex += f"\n\\cline{{2-6}}\\nopagebreak\n & Top chord & C & {kl_tc} & {slnd_tc} & 250 --- {status_tc} \\\\*[6pt]"
            if bottom_chord_enabled:
                row_tex += f"\n\\cline{{2-6}}\\nopagebreak\n & Bottom chord & T & {kl_bc} & {slnd_bc} & 400 --- {status_bc} \\\\[6pt]"
            row_tex += "\n\\hline"
            cb_slenderness_rows.append(row_tex)
    cb_slenderness_content = "\n".join(cb_slenderness_rows)

    cb_capacity_rows = []
    for pair in pairs:
        sub_rows = []
        for member, label in [("diagonal", "Diagonal"), ("chord", "Chord")]:
            force_str, ftype = bridge.get_cb_governing_force(pair, member)
            section = bridge.get_cb_section(pair, member, ftype) or "---"
            gov_lc = bridge.get_cb_gov_lc(pair, member, ftype) or "---"
            capacity = bridge.get_cb_capacity(pair, member, ftype) or "---"
            ur = bridge.get_cb_efficiency(pair, member, ftype) or "---"
            status = bridge.get_cb_status(pair, member, ftype) or "---"
            sub_rows.append(
                r" & " + label + r" & " + section
                + r" & " + gov_lc + r" & " + (force_str or "---") + r" & " + capacity
                + r" & " + ur + r" & " + status + r" \\*[6pt]"
            )
        cb_capacity_rows.append(_multirow_group(len(sub_rows), _tex(pair), sub_rows, "2-8"))
    cb_capacity_content = "\n".join(cb_capacity_rows)

    # Deck slab helpers
    _dk_has = bool(deck_rpt)
    _dk_oh = bool(deck_rpt.get(KEY_DD_HAS_OVERHANG))
    _DKPH = r"\placeholder{---}"

    def _dkv(key, default=0.0):
        v = deck_rpt.get(key)
        if v is None or v == "":
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def _dkf(key, nd=2, scale=1.0):
        if not _dk_has:
            return _DKPH
        v = deck_rpt.get(key)
        if v is None or v == "":
            return _DKPH
        try:
            return f"{float(v) * scale:.{nd}f}"
        except (TypeError, ValueError):
            return _tex(v)

    def _dks(ok):
        return ("PASS" if ok else "FAIL") if _dk_has else "---"

    def _dkoh(key, nd=2, scale=1.0, unit=""):
        if not _dk_has:
            return _DKPH
        if not _dk_oh:
            return "N/A"
        return _dkf(key, nd=nd, scale=scale) + unit

    _dk_wks = [_dkv(KEY_DD_WK_BOT), _dkv(KEY_DD_WK_TOP)]
    if _dk_oh:
        _dk_wks.append(_dkv(KEY_DD_WK_OH))
    _dk_gov_wk = max(_dk_wks)
    _dk_gov_wk_str = (f"{_dk_gov_wk:.4f}" if _dk_has else _DKPH)
    _dk_crack_ok = _dk_has and _dk_gov_wk <= _dkv(KEY_DD_WK_LIMIT)

    # Table 5.29: Overall Design Check Summary + UR tracking for Section 5.5 Chart
    _pg_522 = (bridge.output_dict.get("design_results", {}) or {}).get("per_girder", {}) or {}
    ur_float_tracker = {
        "Steel Plate\nGirders": 0.0,
        "Concrete\nDeck Slab": 0.0,
        "Cross\nBracing": 0.0,
        "End\nDiaphragms": 0.0,
    }

    def _record_ur(category_key: str, raw_val):
        try:
            f = float(raw_val)
            if f > ur_float_tracker[category_key]:
                ur_float_tracker[category_key] = f
        except (TypeError, ValueError):
            pass

    def _vu_522(v, unit):
        s = _dfmt(v, nd=2)
        if not s or s == "---":
            return "---"
        u = (unit or "").strip()
        return (s + " " + _tex(u)) if u else s

    def _ur_522(v, category_key: Optional[str] = None):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return "---"
        if category_key:
            _record_ur(category_key, f)
        s = f"{f:.2f}"
        return (r"\textcolor{red}{" + s + "}") if f > 1.0 else s

    def _lc_short(lc):
        return _format_lc(str(lc).strip())

    def _gov_lc_in_522(g, check_ids):
        gd = _pg_522.get(g) or {}
        best = None
        for _lc, _ld in (gd.get("per_lc") or {}).items():
            if str(_lc).lower().startswith("envelope"):
                continue
            for _chk in (_ld.get("checks") or []):
                if _chk.get("id") in check_ids:
                    _d = _chk.get("dcr") or 0.0
                    if best is None or _d > best[0]:
                        best = (_d, _lc)
        return _lc_short(best[1]) if best else "---"

    def _dcr_row(check_ids, fallback_unit="", category_key: Optional[str] = None):
        best = None
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                if chk.get("check_id") in check_ids:
                    d = chk.get("dcr") or 0.0
                    if best is None or d > best[0]:
                        best = (
                            d,
                            chk.get("demand"),
                            chk.get("capacity"),
                            chk.get("demand_unit") or "",
                            chk.get("capacity_unit") or "",
                            g,
                        )
        if best is not None:
            d, dem, cap, du, cu, g = best
            return (
                _gov_lc_in_522(g, check_ids),
                _vu_522(dem, du),
                _vu_522(cap, cu),
                _ur_522(d, category_key),
            )
        best = None
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for _lc, _ld in (gd.get("per_lc") or {}).items():
                if str(_lc).lower().startswith("envelope"):
                    continue
                for chk in (_ld.get("checks") or []):
                    if chk.get("id") in check_ids:
                        d = chk.get("dcr") or 0.0
                        if best is None or d > best[0]:
                            best = (d, chk.get("demand"), chk.get("capacity"), _lc)
        if best is None:
            return ("---", "---", "---", "---")
        d, dem, cap, _lc = best
        return (
            _lc_short(_lc),
            _vu_522(dem, fallback_unit),
            _vu_522(cap, fallback_unit),
            _ur_522(d, category_key),
        )

    _cb_pairs_522 = bridge.get_cb_pairs()

    def _cb_row(force_type, category_key: str = "Cross\nBracing"):
        best = None
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                cap = bridge.get_cb_capacity(pair, member, force_type)
                eff = bridge.get_cb_efficiency(pair, member, force_type)
                try:
                    ur = float(eff)
                except (TypeError, ValueError):
                    continue
                if best is None or ur > best[0]:
                    best = (ur, pair, member, cap)
        if best is None:
            return ("---", "---", "---", "---")
        ur, _, _, cap = best
        gov = _format_lc(bridge.get_cb_gov_lc(best[1], best[2], force_type) or "---")
        dem = f"{float(cap) * ur:.2f} kN" if cap else "---"
        cap_s = (cap + " kN") if cap else "---"
        return (gov, dem, cap_s, _ur_522(ur, category_key))

    def _cb_slender_row():
        best = None
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                s = bridge.get_cb_slenderness(pair, member)
                try:
                    sf = float(s)
                except (TypeError, ValueError):
                    continue
                lim = 400.0 if member == "chord" else 250.0
                ratio = sf / lim
                if best is None or ratio > best[0]:
                    best = (ratio, sf, lim)
        if best is None:
            return ("---", "---", "---", "---")
        ratio, sf, lim = best
        return ("---", f"{sf:.1f}", f"{lim:.0f}", _ur_522(ratio, "Cross\nBracing"))

    def _row522(label, cells):
        c = [str(x).strip() if (x is not None and str(x).strip() and str(x).strip() != "") else "---" for x in cells]
        while len(c) < 4:
            c.append("---")
        return label + r" & " + r" & ".join(c[:4]) + r" \\[6pt]\hline"

    _deck_combo = (
        r"Basic ULS: " + _tex(f"{_dkv(KEY_DD_GAMMA_DL):g}DL + {_dkv(KEY_DD_GAMMA_LL):g}LL")
        if _dk_has else "---"
    )

    def _deck_row(dem_key, cap_key, unit, is_oh=False):
        if not _dk_has:
            return ("---", "---", "---", "---")
        if is_oh and not _dk_oh:
            return (_deck_combo, "N/A", "N/A", "N/A")
        dem = _dkv(dem_key)
        cap = _dkv(cap_key)
        ur = (dem / cap) if cap > 0 else None
        return (_deck_combo, f"{dem:.2f} {_tex(unit)}", f"{cap:.2f} {_tex(unit)}", _ur_522(ur, "Concrete\nDeck Slab"))

    def _row522_msg(label, msg):
        return label + r" & \multicolumn{4}{c|}{" + msg + r"} \\[6pt]\hline"

    _ed_type = ""
    for _k, _v in bridge.input_dict.items():
        if str(_k).startswith(KEY_MP_ED_TYPE) and _v:
            _ed_type = str(_v)
            break
    _ed_is_cb = "brac" in _ed_type.strip().lower()
    if _ed_is_cb:
        _ed_moment_row = _row522(r"End Diaphragm: Moment", _cb_row("compression", "End\nDiaphragms"))
        _ed_shear_row = _row522(r"End Diaphragm: Shear", _cb_row("tension", "End\nDiaphragms"))
    else:
        _ed_msg = r"Rolled / Welded section -- design to be added"
        _ed_moment_row = _row522_msg(r"End Diaphragm: Moment", _ed_msg)
        _ed_shear_row = _row522_msg(r"End Diaphragm: Shear", _ed_msg)

    def _gov_sls_frequent():
        best = None
        for _g, _gd in _pg_522.items():
            if str(_g).startswith("EB"):
                continue
            for _lc, _ld in (_gd.get("per_lc") or {}).items():
                if "frequent" not in str(_lc).lower():
                    continue
                _d = _ld.get("max_dcr") or 0.0
                if best is None or _d > best[0]:
                    best = (_d, _lc)
        return _tex(str(best[1]).strip()) if best else "Frequent SLS"

    _wk_lim = _dkv(KEY_DD_WK_LIMIT)
    _crack_cells = (
        (_gov_sls_frequent() if _dk_has else "---"),
        (f"{_dk_gov_wk:.3f} mm" if _dk_has else "---"),
        (f"{_wk_lim:.3f} mm" if _dk_has else "---"),
        (_ur_522(_dk_gov_wk / _wk_lim, "Concrete\nDeck Slab") if (_dk_has and _wk_lim > 0) else "---"),
    )

    def _transverse_shear_row():
        r = _dcr_row({16}, category_key="Concrete\nDeck Slab")
        if r[1] != "---" or r[2] != "---":
            return r
        if _ts_vl not in (None, "") and _ts_vrd not in (None, ""):
            v_dem = _knm(_ts_vl)
            v_cap = _knm(_ts_vrd)
            v_ur = _ur_522(_ts_ur_str, "Concrete\nDeck Slab")
            return ("Governing ULS", v_dem if v_dem else "---", v_cap if v_cap else "---", v_ur if v_ur else "---")
        return ("---", "---", "---", "---")

    _t522 = [
        _row522(r"Girder: Moment", _dcr_row({1}, category_key="Steel Plate\nGirders")),
        _row522(r"Girder: Shear", _dcr_row({2}, category_key="Steel Plate\nGirders")),
        _row522(r"Girder: LTB (constr.)", _dcr_row({5}, category_key="Steel Plate\nGirders")),
        _row522(r"Girder: Deflection", _dcr_row({13, 14}, fallback_unit="mm", category_key="Steel Plate\nGirders")),
        _row522(r"Girder: Stress", _dcr_row({11}, fallback_unit="MPa", category_key="Steel Plate\nGirders")),
        _row522(r"Girder: Fatigue", _dcr_row({8, 9}, fallback_unit="MPa", category_key="Steel Plate\nGirders")),
        _row522(r"Transverse Shear (slab)", _transverse_shear_row()),
        _row522(r"Crack Width (slab)", _crack_cells),
        _row522(r"Deck: Flexure (sagging)", _deck_row(KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT, "kN-m/m")),
        _row522(r"Deck: Flexure (hogging)", _deck_row(KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP, "kN-m/m")),
        _row522(r"Deck: Cantilever Overhang", _deck_row(KEY_DD_M_ULS_OH, KEY_DD_MU_OH, "kN-m/m", is_oh=True)),
        _row522(r"Deck: Punching Shear", _deck_row(KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA, "MPa")),
        _row522(r"Deck: One-Way Shear", _deck_row(KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC, "kN/m")),
        _row522(r"Cross Bracing: Compression", _cb_row("compression", "Cross\nBracing")),
        _row522(r"Cross Bracing: Tension", _cb_row("tension", "Cross\nBracing")),
        _row522(r"Cross Bracing: Slenderness", _cb_slender_row()),
        _ed_moment_row,
        _ed_shear_row,
    ]
    t522_content = "\n".join(r.strip() for r in _t522 if r and r.strip())

    ur_chart_tex = ""
    tmp_images_dir = fig_paths.get("_tmp_images_dir")
    if tmp_images_dir:
        ur_img_path = os.path.join(tmp_images_dir, "ur_summary.png")
        generated_ur = generate_ur_summary_chart(ur_float_tracker, ur_img_path)
        if generated_ur:
            ur_chart_tex = _fig_embed(
                generated_ur,
                "Overall Design Check Summary: Governing Utilization Ratio (UR = Demand / Capacity) across primary elements. Red dashed line indicates UR = 1.00 limit.",
                width=r"0.88\textwidth",
            )

    sec51 = (
        r"\section{Plate Girder Design}" + "\n"
        r"\label{sec:plate-girder}" + "\n"
        + make_longtable(
            "|C{2.5cm}|L{8.0cm}|>{\\centering\\arraybackslash}p{5.0cm}|",
            "Girder Section Properties (Final Optimized / User-selected)",
            r"\textbf{Girder} & \textbf{Property} & \textbf{Value} \\[6pt]",
            t51_content,
        )
        + make_longtable(
            "|C{2.5cm}|L{3cm}|C{3.5cm}|C{2.5cm}|>{\\centering\\arraybackslash}p{4.0cm}|",
            "Girder Section Classification",
            r"\textbf{Girder} & \textbf{Element} & \textbf{Slenderness Ratio} & \textbf{Class Limit} & \textbf{Classification} \\[6pt]",
            t52_content,
            note="Note: IS 800:2007 Table 2.",
        )
        + make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Moment Capacity Check",
            r"\textbf{Girder} & \textbf{Parameter} & \textbf{Formula} & \textbf{Value} & \textbf{Status} \\[6pt]",
            t53_content,
            note="Note: IRC 22 Cl. 603.3.1, IS 800 Cl. 8.2.1.",
        )
        + make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Shear Capacity Check",
            r"\textbf{Girder} & \textbf{Parameter} & \textbf{Formula} & \textbf{Value} & \textbf{Status} \\[6pt]",
            t54_content,
            note="Note: IS 800 Cl. 8.4, IRC 22 Cl. 603.3.3.2.",
        )
        + make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Interaction Checks (M-V and M-N)",
            r"\textbf{Girder} & \textbf{Check} & \textbf{Condition} & \textbf{Value} & \textbf{Status} \\[6pt]",
            t55_content,
            note="Note: IRC 22 Cl. 603.3.3.3.",
        )
        + make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Lateral Torsional Buckling Check (Construction Stage)",
            r"\textbf{Girder} & \textbf{Parameter} & \textbf{Formula} & \textbf{Value} & \textbf{Status} \\[6pt]",
            t56_content,
            note="Note: IRC 22 Cl. 603.3.3.1, IS 800 Cl. 8.2.2.",
        )
        + make_longtable(
            "|C{2.5cm}|L{6.5cm}|>{\\arraybackslash}p{6.5cm}|",
            "Stiffener Design Summary",
            r"\textbf{Girder} & \textbf{Stiffener Parameter} & \textbf{Value} \\[6pt]",
            t57_content,
        )
        + t58_block
        + make_longtable(
            "|C{2.5cm}|L{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "End Panel Stiffener Checks",
            r"\textbf{Girder} & \textbf{Check} & \textbf{Required} & \textbf{Provided} & \textbf{Status} \\[6pt]",
            t59_content,
            note="Note: IS 800 Cl. 8.4.2.2.",
        )
        + make_longtable(
            "|C{2.5cm}|L{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{3.5cm}|C{2.5cm}|",
            "Serviceability: Deflection Checks",
            r"\textbf{Girder} & \textbf{Check} & \textbf{Allowable} & \textbf{Actual} & \textbf{Status} \\[6pt]",
            t510_content,
            note="Note: IRC 22 Cl. 604.3.2.",
        )
        + make_longtable(
            "|C{2.5cm}|L{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{3.5cm}|C{2.5cm}|",
            "Serviceability: Maximum Stress Limitation",
            r"\textbf{Girder} & \textbf{Element} & \textbf{Allowable Stress} & \textbf{Actual Stress} & \textbf{Status} \\[6pt]",
            t511_content,
        )
        + make_longtable(
            "|C{2.5cm}|C{3.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{3.5cm}|C{2.5cm}|",
            "Serviceability: Fatigue Assessment",
            r"\textbf{Girder} & \textbf{Stress Range, $\Delta\sigma$ (MPa)} & \textbf{Fatigue Limit, $f_{fd}$ (MPa)} & \textbf{Utilization Ratio} & \textbf{Status} \\[6pt]",
            t512_content,
            note=r"Note: IRC 22 Cl. 605 --- governing of normal and shear fatigue (worst by DCR). Capacity reduction factor $\mu_r$ applied where plate thickness $>$ 25 mm.",
        )
        + make_longtable(
            "|C{1.6cm}|>{\\centering\\arraybackslash}p{3.6cm}|C{2.4cm}|C{2.0cm}|C{2.1cm}|C{1.7cm}|C{1.5cm}|",
            "Girder Design Summary (DCR / Utilization Ratio)",
            r"\textbf{Girder} & \textbf{Controlling LC / Combination} & \textbf{Controlling Check} & \textbf{Demand} & \textbf{Capacity} & \textbf{UR} & \textbf{Status} \\[6pt]",
            g_summary_table_content,
            note=r"Note: UR = Demand / Capacity. A value $\leq 1.0$ indicates a passing check. The controlling check is the criterion with the highest UR for each girder, with the real load case/combination that drives it.",
        )
        + make_longtable(
            "|L{3.6cm}|C{5.6cm}|>{\\centering\\arraybackslash}p{2.6cm}|L{3.0cm}|",
            "Shear Connector Capacity",
            r"\textbf{Parameter} & \textbf{Formula} & \textbf{Value} & \textbf{Reference} \\[6pt]",
            t514_content,
        )
        + make_longtable(
            "|L{3.2cm}|>{\\centering\\arraybackslash}p{4.3cm}|>{\\centering\\arraybackslash}p{4.3cm}|C{2.0cm}|",
            "Shear Connector Spacing",
            r"\textbf{Criterion} & \textbf{Governing Spacing} & \textbf{Actual Spacing Provided} & \textbf{Status} \\[6pt]",
            t515_content,
            note=r"Note: IRC 22 Cl. 606.4, 606.9. Governing spacing $= \min(S_{L1}, S_{L2}, S_R)$.",
        )
        + make_longtable(
            "|L{5.3cm}|>{\\arraybackslash}p{7.2cm}|C{2.0cm}|",
            "Transverse Shear and Detailing Checks",
            r"\textbf{Check} & \textbf{Value} & \textbf{Status} \\[6pt]",
            t516_content,
            note="Note: IRC 22 Cl. 606.6, 606.10.",
        )
    )

    sec52 = (
        r"\section{Deck Slab Design}" + "\n"
        r"\label{sec:deck-design}" + "\n"
        + make_longtable(
            "|L{6.0cm}|L{9.5cm}|",
            "Deck Slab: Loading and Geometry",
            r"\textbf{Parameter} & \textbf{Value} \\[6pt]",
            r"\textnormal{Effective Span of Deck Slab, $l_{eff}$} & " + _dkf(KEY_DD_SPAN, nd=0, scale=1000.0) + r" mm (girder spacing, c/c) \\[6pt]\hline" + "\n"
            r"\textnormal{Deck Thickness, $t_s$} & " + _render_value(bridge.input_dict, KEY_TS_DECK_THICKNESS) + r" mm \\[6pt]\hline" + "\n"
            r"\textnormal{Clear Cover (IRC 112 Cl. 15.2)} & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r" mm \\[6pt]\hline" + "\n"
            r"\textnormal{Concrete Grade (IRC 112 Cl. 6.4)} & " + _render_value(bridge.input_dict, KEY_DECK_CONCRETE_GRADE_BASIC) + r" ($f_{ck}$ = " + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCK) + r" MPa, $f_{ctm}$ = " + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCTM) + r" MPa) \\[6pt]\hline" + "\n"
            r"\textnormal{Reinforcement Grade (IRC 112 Cl. 6.2)} & " + _render_value(bridge.input_dict, KEY_DS_REINF_MATERIAL) + r" ($f_y$ = " + _dkf(KEY_DD_FY, nd=0) + r" MPa) \\[6pt]\hline" + "\n"
            r"\textnormal{Dead Load per Unit Area, $w_{DL}$} & " + _dkf(KEY_DD_WDL, nd=2) + r" kN/m$^2$ (slab self-weight) \\[6pt]\hline" + "\n"
            r"\textnormal{IRC 6 Wheel Load (Class A / 70R)} & " + _dkf(KEY_DD_WHEEL_LOAD, nd=1) + r" kN \\[6pt]\hline" + "\n"
            r"\textnormal{Tyre Contact Width (IRC 6 Annex~A)} & " + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + r" mm (transverse) \\[6pt]\hline" + "\n"
            r"\textnormal{Impact Factor (IRC 6 Cl. 208.2)} & " + _dkf(KEY_DD_IMPACT_FACTOR, nd=3) + r" \\[6pt]\hline" + "\n"
            r"\textnormal{Governing Live Load Case} & " + _dkf(KEY_DD_VEHICLE) + r" \\[6pt]\hline",
        )
        + make_longtable(
            "|C{3.0cm}|C{3.5cm}|C{3.0cm}|>{\\centering\\arraybackslash}p{4.2cm}|C{1.8cm}|",
            "Deck Slab: Flexure Check for Interior Panel (Pigeaud's Method)",
            r"\textbf{Location} & \textbf{Parameter} & \textbf{Formula / Reference} & \textbf{Value} & \textbf{Status} \\[6pt]",
            r"\multirow{5}{*}{\makecell{At Midspan\\(Sagging)}} & Transverse BM (DL), $M_{T,DL}$ & $w_{DL}\,l_{eff}^2/10$ & " + _dkf(KEY_DD_M_DL, nd=2) + r" kN-m/m & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Transverse BM (LL), $M_{T,LL}$ & Effective width (IRC 112 B3.1) & " + _dkf(KEY_DD_M_LL, nd=2) + r" kN-m/m & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Total Design BM, $M_{u,sag}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL & " + _dkf(KEY_DD_M_ULS_SAG, nd=2) + r" kN-m/m & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Effective depth, $d$ & $t_s - c_{nom} - \phi/2$ & " + _dkf(KEY_DD_D_BOT, nd=1) + r" mm & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_BOT, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_BOT) >= _dkv(KEY_DD_M_ULS_SAG)) + r" \\[6pt]\hline" + "\n"
            r"\multirow{3}{*}{\makecell{At Support\\(Hogging)}} & Total Design BM, $M_{u,hog}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL (at support) & " + _dkf(KEY_DD_M_ULS_HOG, nd=2) + r" kN-m/m & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Required Top Steel, $A_{st,top}$ & $M_u / (0.87\,f_y\,d)$ & " + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r" mm$^2$/m & --- \\*[6pt]\cline{2-5}\nopagebreak" + "\n"
            r" & Moment Capacity, $M_{Rd}$ & IRC 112 Cl. 12.2 & " + _dkf(KEY_DD_MU_TOP, nd=2) + r" kN-m/m & " + _dks(_dkv(KEY_DD_MU_TOP) >= _dkv(KEY_DD_M_ULS_HOG)) + r" \\[6pt]\hline",
            note=r"Note: IRC 112 Cl. 12.2. Distribution (longitudinal) reinforcement designed for 20\% of main steel moment (IRC 21 Cl. 305.18).",
        )
        + make_longtable(
            "|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.5cm}|C{2cm}|",
            "Deck Slab: Cantilever Overhang Flexure Check",
            r"\textbf{Parameter} & \textbf{Formula} & \textbf{Value} & \textbf{Status} \\[6pt]",
            r"Overhang Length, $l_{oh}$ & --- & " + _render_value(bridge.input_dict, KEY_TS_DECK_OVERHANG, " m") + r" & --- \\[6pt]\hline" + "\n"
            r"Crash Barrier Load Moment & IRC 6 Cl. 206.4 & " + _dkoh(KEY_DD_M_BARRIER, nd=2, unit=" kN-m/m") + r" & --- \\[6pt]\hline" + "\n"
            r"Dead Load Moment & $w_{DL}\,l_{oh}^2/2$ + railing & " + _dkoh(KEY_DD_M_DL_OH, nd=2, unit=" kN-m/m") + r" & --- \\[6pt]\hline" + "\n"
            r"Live Load Moment (eccentric wheel) & Wheel load $\times$ arm & " + _dkoh(KEY_DD_M_LL_OH, nd=2, unit=" kN-m/m") + r" & --- \\[6pt]\hline" + "\n"
            r"Total Hogging Moment, $M_{u,oh}$ & " + _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" (LL + CB) & " + _dkoh(KEY_DD_M_ULS_OH, nd=2, unit=" kN-m/m") + r" & --- \\[6pt]\hline" + "\n"
            r"Moment Capacity (top steel), $M_{Rd,oh}$ & IRC 112 Cl. 12.2 & " + _dkoh(KEY_DD_MU_OH, nd=2, unit=" kN-m/m") + r" & " + (_dks(_dkv(KEY_DD_MU_OH) >= _dkv(KEY_DD_M_ULS_OH)) if _dk_oh else ("N/A" if _dk_has else "---")) + r" \\[6pt]\hline",
            note="Note: IRC 6 Cl. 206.4 crash barrier loads applied at kerb face; IRC 112 Cl. 12.2 flexure.",
        )
        + make_longtable(
            "|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.5cm}|C{2cm}|",
            "Deck Slab: Punching Shear Check (IRC 112 Cl. 10.4.6)",
            r"\textbf{Parameter} & \textbf{Formula / Reference} & \textbf{Value} & \textbf{Status} \\[6pt]",
            r"Design Wheel Load (ULS), $V_{Ed}$ & $\gamma_Q\,(1+IF)\,P_w$ & " + _dkf(KEY_DD_PUNCH_VED_KN, nd=1) + r" kN & --- \\[6pt]\hline" + "\n"
            r"Tyre Contact Area & $a \times b$ (IRC 6 Annex~A) & " + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + r" $\times$ " + _dkf(KEY_DD_TYRE_LENGTH, nd=0) + r" mm & --- \\[6pt]\hline" + "\n"
            r"Loaded Area at mid-depth, $b_0$ & $c_1 \times c_2$ (incl. WC dispersion) & " + _dkf(KEY_DD_PUNCH_C1, nd=0) + r" $\times$ " + _dkf(KEY_DD_PUNCH_C2, nd=0) + r" mm & --- \\[6pt]\hline" + "\n"
            r"Control Perimeter, $u_1$ & $2(c_1+c_2) + 4\pi d$ & " + _dkf(KEY_DD_PUNCH_U1, nd=0) + r" mm & --- \\[6pt]\hline" + "\n"
            r"Punching Shear Stress, $v_{Ed}$ & $V_{Ed} / (u_1\,d)$ & " + _dkf(KEY_DD_PUNCH_VED, nd=3) + r" MPa & --- \\[6pt]\hline" + "\n"
            r"Punching Resistance, $v_{Rd,c}$ & IRC 112 Eq. 10.1 & " + _dkf(KEY_DD_VRD_C_MPA, nd=3) + r" MPa & --- \\[6pt]\hline" + "\n"
            r"Punching Shear Check & $v_{Ed} \leq v_{Rd,c}$ & " + (f"{_dkv(KEY_DD_PUNCH_VED) / _dkv(KEY_DD_VRD_C_MPA):.2f}" if (_dk_has and _dkv(KEY_DD_VRD_C_MPA) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_PUNCH_OK))) + r" \\[6pt]\hline",
            note=r"Note: Punching shear reinforcement not typically required for deck slabs with $d \geq 200$ mm and adequate longitudinal reinforcement.",
        )
        + make_longtable(
            "|L{7cm}|>{\\arraybackslash}p{8.5cm}|",
            "Crack Width Check (Deck Slab)",
            r"\textbf{Parameter} & \textbf{Value / Reference} \\[6pt]",
            r"\textnormal{Min. Reinforcement for Crack Control, $A_{s,min}$} & " + _dkf(KEY_DD_AS_MIN, nd=0) + r" mm$^2$/m [IRC 112 Cl. 16.5.1] \\[6pt]\hline" + "\n"
            r"\textnormal{Provided Reinforcement (bottom)} & $\phi\,$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm c/c (" + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm$^2$/m) \\[6pt]\hline" + "\n"
            r"\textnormal{Max. Permissible Crack Width} & " + _dkf(KEY_DD_WK_LIMIT, nd=2) + r" mm \\[6pt]\hline" + "\n"
            r"\textnormal{Calculated Crack Width, $w_k$ (governing)} & " + _dk_gov_wk_str + r" mm \\[6pt]\hline" + "\n"
            r"\textnormal{Crack Width Check} & " + _dks(_dk_crack_ok) + r" \\[6pt]\hline",
        )
        + make_longtable(
            "|L{5.5cm}|C{3.5cm}|>{\\centering\\arraybackslash}p{4.5cm}|C{2cm}|",
            "One-Way (Beam) Shear Check (Deck Slab)",
            r"\textbf{Parameter} & \textbf{Formula / Reference} & \textbf{Value} & \textbf{Status} \\[6pt]",
            r"Design Shear per unit width, $V_{Ed}$ & $\gamma_{DL} V_{DL} + \gamma_{LL}(1{+}IF)V_{LL}$ & " + _dkf(KEY_DD_SHEAR_VED, nd=2) + r" kN/m & --- \\[6pt]\hline" + "\n"
            r"Effective depth, $d$ & $t_s - c_{nom} - \phi/2$ & " + _dkf(KEY_DD_D_BOT, nd=1) + r" mm & --- \\[6pt]\hline" + "\n"
            r"Size factor, $k$ & $1 + \sqrt{200/d} \leq 2.0$ & " + (f"{min(1.0 + (200.0 / _dkv(KEY_DD_D_BOT)) ** 0.5, 2.0):.3f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + r" & --- \\[6pt]\hline" + "\n"
            r"Long. reinforcement ratio, $\rho_l$ & $A_{sl}/(b_w\,d) \leq 0.02$ & " + (f"{min(_dkv(KEY_DD_AS_BOT) / (1000.0 * _dkv(KEY_DD_D_BOT)), 0.02):.4f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + r" & --- \\[6pt]\hline" + "\n"
            r"Shear resistance (no stirrups), $V_{Rd,c}$ & $v_{Rd,c}\,b_w\,d$ (Cl. 10.3.2) & " + _dkf(KEY_DD_SHEAR_VRDC, nd=2) + r" kN/m & --- \\[6pt]\hline" + "\n"
            r"One-Way Shear Check & $V_{Ed} \leq V_{Rd,c}$ & " + (f"{_dkv(KEY_DD_SHEAR_VED) / _dkv(KEY_DD_SHEAR_VRDC):.2f}" if (_dk_has and _dkv(KEY_DD_SHEAR_VRDC) > 0) else _DKPH) + r" & " + _dks(bool(deck_rpt.get(KEY_DD_SHEAR_OK))) + r" \\[6pt]\hline",
            note="Note: IRC 112 Cl. 10.3.2. Shear reinforcement not provided in deck slabs; capacity relies on concrete and main reinforcement.",
        )
        + make_longtable(
            "|L{5.5cm}|>{\\centering\\arraybackslash}p{4.1cm}|>{\\centering\\arraybackslash}p{4.1cm}|C{1.8cm}|",
            "Reinforcement Detailing Summary (Deck Slab)",
            r"\textbf{Parameter} & \textbf{Required / Limit} & \textbf{Provided} & \textbf{Status} \\[6pt]",
            r"\multicolumn{4}{|l|}{\textbf{Main Reinforcement: Bottom (Transverse)}} \\[6pt]\hline" + "\n"
            r"Required Area, $A_{st,req}$ (mm$^2$/m) & " + _dkf(KEY_DD_AS_REQ_BOT, nd=0) + r" mm$^2$/m & " + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm$^2$/m & " + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_REQ_BOT)) + r" \\[6pt]\hline" + "\n"
            r"Bar Diameter $\times$ Spacing & $\phi \geq 10$~mm (IRC 112) & $\phi\,$" + _dkf(KEY_DD_DIA_BOT, nd=0) + r" @ " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm c/c & --- \\[6pt]\hline" + "\n"
            r"Min. Reinforcement $A_{s,min}$ (IRC 112 Cl. 16.3.1) & " + _dkf(KEY_DD_AS_MIN, nd=0) + r" mm$^2$/m & " + _dkf(KEY_DD_AS_BOT, nd=0) + r" mm$^2$/m & " + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_MIN)) + r" \\[6pt]\hline" + "\n"
            r"Max. Bar Spacing (IRC 112 Cl. 16.3.2) & " + _dkf(KEY_DD_SPACING_MAX, nd=0) + r" mm & " + _dkf(KEY_DD_SPC_BOT, nd=0) + r" mm & " + _dks(0.0 < _dkv(KEY_DD_SPC_BOT) <= _dkv(KEY_DD_SPACING_MAX)) + r" \\[6pt]\hline" + "\n"
            r"\multicolumn{4}{|l|}{\textbf{Distribution Reinforcement: Longitudinal}} \\[6pt]\hline" + "\n"
            r"Required Area, $A_{st,dist}$ (mm$^2$/m) & $\geq 20\%$ of main steel & " + _dkf(KEY_DD_AS_LONG, nd=0) + r" mm$^2$/m & " + _dks(_dkv(KEY_DD_AS_LONG) >= max(0.20 * _dkv(KEY_DD_AS_BOT), _dkv(KEY_DD_AS_MIN))) + r" \\[6pt]\hline" + "\n"
            r"\multicolumn{4}{|l|}{\textbf{Top Reinforcement (Support / Cantilever Overhang)}} \\[6pt]\hline" + "\n"
            r"Required Area, $A_{st,top}$ (mm$^2$/m) & " + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r" mm$^2$/m & " + _dkf(KEY_DD_AS_TOP, nd=0) + r" mm$^2$/m & " + _dks(_dkv(KEY_DD_AS_TOP) >= _dkv(KEY_DD_AS_REQ_TOP)) + r" \\[6pt]\hline" + "\n"
            r"\multicolumn{4}{|l|}{\textbf{Cover and Detailing}} \\[6pt]\hline" + "\n"
            r"Clear Cover (IRC 112 Cl. 15.2) & $\geq 50$~mm (Table 14.2) & Top " + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r" / Bottom " + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r" mm & " + _dks(bool(deck_rpt.get(KEY_DD_COVER_OK))) + r" \\[6pt]\hline",
            note="Note: IRC 112 Cl. 16.3, IS 456 Cl. 26.5. All reinforcement provisions satisfy strength and detailing requirements.",
        )
    )

    sec53 = (
        r"\section{Cross Bracing Design}" + "\n"
        r"\label{sec:cross-bracing}" + "\n"
        + make_longtable(
            "|C{2.0cm}|L{2.0cm}|L{2.2cm}|C{2.5cm}|C{2.0cm}|C{2.0cm}|",
            "Cross Bracing: Connection and Section Properties",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Connection} & \textbf{Section} & \textbf{$A_g$ (mm$^2$)} & \textbf{$r_{min}$ (mm)} \\[6pt]",
            cb_forces_content,
            note=r"Note: $A_g$ = gross cross-sectional area; $r_{min}$ = minimum radius of gyration.",
            compact=True,
        )
        + make_longtable(
            "|C{2.2cm}|L{2.2cm}|L{2.5cm}|C{2.5cm}|C{2.5cm}|>{\\centering\\arraybackslash}p{3.6cm}|",
            "Cross Bracing: Slenderness Ratio Check (IS 800 Cl. 3.8)",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Nature} & \textbf{Eff. Length $KL$ (mm)} & \textbf{$KL/r$} & \textbf{Limit / Status} \\[6pt]",
            cb_slenderness_content,
            note=r"Note: Limit = 250 for compression members, 400 for tension members. $K = 1.0$ for members with both ends pinned.",
        )
        + make_longtable(
            "|C{2.0cm}|L{1.8cm}|C{2.2cm}|C{3.0cm}|C{1.8cm}|C{1.8cm}|C{1.2cm}|C{1.8cm}|",
            "Cross Bracing Design: Capacity Summary",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Section} & \textbf{Governing LC} & \textbf{Demand (kN)} & \textbf{Capacity (kN)} & \textbf{UR} & \textbf{Status} \\[6pt]",
            cb_capacity_content,
            note="Note: Designed per IS 800 Cl. 7 (compression) and Cl. 6 (tension). OsdagBridge cross-bracing module used.",
            compact=True,
        )
    )

    sec54 = (
        r"\section{End Diaphragm Design}" + "\n"
        r"\label{sec:end-diaphragm}" + "\n"
        + make_longtable(
            "|C{2.0cm}|L{2.0cm}|L{2.2cm}|C{2.5cm}|C{2.0cm}|C{2.0cm}|",
            "End Diaphragm: Connection and Section Properties",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Connection} & \textbf{Section} & \textbf{$A_g$ (mm$^2$)} & \textbf{$r_{min}$ (mm)} \\[6pt]",
            cb_forces_content,
            note=r"Note: $A_g$ = gross cross-sectional area; $r_{min}$ = minimum radius of gyration.",
            compact=True,
        )
        + make_longtable(
            "|C{2.2cm}|L{2.2cm}|L{2.5cm}|C{2.5cm}|C{2.5cm}|>{\\centering\\arraybackslash}p{3.6cm}|",
            "End Diaphragm: Slenderness Ratio Check (IS 800 Cl. 3.8)",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Nature} & \textbf{Eff. Length $KL$ (mm)} & \textbf{$KL/r$} & \textbf{Limit / Status} \\[6pt]",
            cb_slenderness_content,
            note=r"Note: Limit = 250 for compression members, 400 for tension members. $K = 1.0$ for members with both ends pinned.",
        )
        + make_longtable(
            "|C{2.0cm}|L{1.8cm}|C{2.2cm}|C{3.0cm}|C{1.8cm}|C{1.8cm}|C{1.2cm}|C{1.8cm}|",
            "End Diaphragm Design: Capacity Summary",
            r"\textbf{Panel} & \textbf{Member} & \textbf{Section} & \textbf{Governing LC} & \textbf{Demand (kN)} & \textbf{Capacity (kN)} & \textbf{UR} & \textbf{Status} \\[6pt]",
            cb_capacity_content,
            note="Note: Designed per IS 800 Cl. 7 (compression) and Cl. 6 (tension). OsdagBridge cross-bracing module used.",
            compact=True,
        )
    )

    sec55 = (
        r"\section{Overall Design Check Summary}" + "\n"
        r"\label{sec:overall-summary}" + "\n"
        + make_longtable(
            "|C{3.4cm}|L{4.5cm}|C{2.3cm}|C{2.3cm}|>{\\centering\\arraybackslash}p{1.6cm}|",
            "Overall Design Check Summary",
            r"\textbf{Member / Check} & \textbf{Governing Load Combo} & \textbf{Demand} & \textbf{Capacity} & \textbf{UR} \\[6pt]",
            t522_content,
            note=r"Note: UR = Demand / Capacity. All values $\leq 1.0$ indicate passing checks. The governing check for each component is highlighted in the individual design check sections above.",
        )
        + ur_chart_tex
    )

    return (
        r"""
\chapter{Design Checks}

This section presents all structural design checks performed by OsdagBridge. For each member, the demand from the governing load combination, the code-based capacity, and the utilization ratio are tabulated. All checks reference IS 800:2007 and IRC 22:2014 unless stated otherwise.
"""
        + sec51 + sec52 + sec53 + sec54 + sec55
    )