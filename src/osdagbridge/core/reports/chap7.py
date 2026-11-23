# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Uses centralized styles, sanitized table cells, repeating longtable headers,
# and non-clipped Matplotlib charts for Structural Steel and Concrete/Rebar.
# =============================================================================

from typing import Optional
from osdagbridge.core.reports.report_utils import make_longtable, _fig_embed, _tex


def ch7_quantities(input_dict, fig_paths: Optional[dict] = None) -> str:
    fig_paths = fig_paths or {}

    rows = [
        (
            "1",
            "Structural Steel (IS 2062) for Girders",
            "steel_girders_vol_formula",
            "steel_girders_qty",
            "steel_girders_vol_total",
            "steel_girders_wt_single",
            "steel_girders_wt_total",
        ),
        (
            "2(a)",
            "Cross Bracing - Top Chord",
            "bracing_top_vol_formula",
            "bracing_top_qty",
            "bracing_top_vol_total",
            "bracing_top_wt_single",
            "bracing_top_wt_total",
        ),
        (
            "2(b)",
            "Cross Bracing - Bottom Chord",
            "bracing_bot_vol_formula",
            "bracing_bot_qty",
            "bracing_bot_vol_total",
            "bracing_bot_wt_single",
            "bracing_bot_wt_total",
        ),
        (
            "2(c)",
            "Cross Bracing - Diagonal Chord",
            "bracing_diag_vol_formula",
            "bracing_diag_qty",
            "bracing_diag_vol_total",
            "bracing_diag_wt_single",
            "bracing_diag_wt_total",
        ),
        (
            "3",
            "Concrete (M40) for Deck Slab",
            "concrete_deck_vol_formula",
            "concrete_deck_qty",
            "concrete_deck_vol_total",
            "concrete_deck_wt_single",
            "concrete_deck_wt_total",
        ),
        (
            "4",
            "Reinforcement Steel (Fe 500)",
            "rebar_deck_vol_formula",
            "rebar_deck_qty",
            "rebar_deck_vol_total",
            "rebar_deck_wt_single",
            "rebar_deck_wt_total",
        ),
        (
            "5",
            "Shear Stud Connectors",
            "shear_studs_vol_formula",
            "shear_studs_qty",
            "shear_studs_vol_total",
            "shear_studs_wt_single",
            "shear_studs_wt_total",
        ),
        (
            "6",
            "Crash Barrier",
            "crash_barrier_vol_formula",
            "crash_barrier_qty",
            "crash_barrier_vol_total",
            "crash_barrier_wt_single",
            "crash_barrier_wt_total",
        ),
    ]

    def _cell(key):
        raw = input_dict.get(key)
        if raw in (None, ""):
            return "N.A."
        return _tex(raw)

    def _formula_cell(key):
        """Return *_vol_formula values verbatim (they already contain LaTeX math)."""
        raw = input_dict.get(key)
        if raw in (None, ""):
            return "N.A."
        return str(raw)

    body_lines = []
    for sn, desc, k_vf, k_q, k_vt, k_ws, k_wt in rows:
        body_lines.append(
            f"{_tex(sn)} & {_tex(desc)} & {_formula_cell(k_vf)} & {_cell(k_q)} & "
            f"{_cell(k_vt)} & {_cell(k_ws)} & {_cell(k_wt)} \\\\[6pt]\n\\hline"
        )

    table_tex = make_longtable(
        "|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|",
        "Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        r"\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\[6pt]",
        "\n".join(body_lines),
        note="Note: Quantities computed from structural design outputs and material densities.",
        compact=True,
    )

    steel_fig = _fig_embed(
        fig_paths.get("steel_quantities"),
        "Structural Steel Quantity Breakdown by Component (Girders, Cross Bracing, and End Diaphragms) in Metric Tonnes (MT).",
        width=r"0.85\textwidth",
    )
    concrete_rebar_fig = _fig_embed(
        fig_paths.get("concrete_rebar_quantities"),
        "Deck Slab Material Summary: Concrete Volume (m$^3$) versus Reinforcement Steel Weight (MT).",
        width=r"0.88\textwidth",
    )

    return (
        r"\chapter{Material Take-off \& Quantity Summary}" + "\n"
        r"\label{ch:material-takeoff}" + "\n"
        + table_tex
        + steel_fig
        + concrete_rebar_fig
    )