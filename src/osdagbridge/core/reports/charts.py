# =============================================================================
# Programmatic Matplotlib Chart Generators for OsdagBridge Design Report
# Generates high-DPI (300 DPI) non-clipped PNG visualizations:
#   1. Section 5.5 — Overall Utilization Ratio (Demand / Capacity) with UR = 1.00
#   2. Chapter 7   — Structural Steel Quantity Breakdown (MT)
#   3. Chapter 7   — Deck Slab Concrete Volume (m3) vs. Reinforcement Weight (MT)
# =============================================================================

import os
import re
import logging
from typing import Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from osdagbridge.core.reports.styles import COLORS

logger = logging.getLogger(__name__)


def _parse_float(val) -> Optional[float]:
    """Safely parse a float from numbers or formatted strings."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ("N.A.", "N/A", "NONE", "---", "-"):
        return None
    match = re.search(r"[-+]?\d*\.?\d+", s.replace(",", ""))
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def generate_ur_summary_chart(
    ur_records: Dict[str, float],
    output_path: str,
) -> Optional[str]:
    """Generate Section 5.5 Utilization Ratio bar chart with UR = 1.00 limit line."""
    if not ur_records:
        return None

    labels = list(ur_records.keys())
    values = [max(0.0, float(v)) for v in ur_records.values()]

    fig, ax = plt.subplots(figsize=(8.2, 4.3), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    bar_colors = [
        f"#{COLORS['fail_hex']}" if v > 1.0
        else (f"#{COLORS['warn_hex']}" if v >= 0.90 else f"#{COLORS['pass_hex']}")
        for v in values
    ]

    x = np.arange(len(labels))
    bars = ax.bar(
        x,
        values,
        width=0.50,
        color=bar_colors,
        edgecolor=f"#{COLORS['text_dark_hex']}",
        linewidth=0.75,
        zorder=3,
    )

    ax.axhline(
        1.0,
        color=f"#{COLORS['threshold_hex']}",
        linestyle="--",
        linewidth=1.8,
        zorder=4,
        label="Allowable Limit (UR = 1.00)",
    )

    y_max = max(max(values) * 1.24, 1.25)
    ax.set_ylim(0, y_max)
    ax.set_ylabel(
        "Utilization Ratio (Demand / Capacity)",
        fontsize=10,
        fontweight="bold",
        color=f"#{COLORS['text_dark_hex']}",
    )
    ax.set_title(
        "Overall Design Check Summary — Governing Utilization Ratios",
        fontsize=11,
        fontweight="bold",
        pad=14,
        color=f"#{COLORS['text_dark_hex']}",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(
        labels,
        fontsize=9.5,
        fontweight="bold",
        color=f"#{COLORS['text_dark_hex']}",
    )
    ax.grid(axis="y", linestyle=":", color=f"#{COLORS['grid_hex']}", zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for bar, val in zip(bars, values):
        status_tag = "FAIL" if val > 1.0 else "PASS"
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + (y_max * 0.022),
            f"{val:.3f}\n({status_tag})",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color=f"#{COLORS['fail_hex']}" if val > 1.0 else f"#{COLORS['text_dark_hex']}",
        )

    ax.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor=f"#{COLORS['grid_hex']}",
        fontsize=9,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.20)
    plt.close(fig)
    return output_path.replace("\\", "/")


def generate_material_charts(
    inputs: dict,
    tmp_images_dir: str,
) -> Dict[str, str]:
    """Generate Chapter 7 charts for Structural Steel (MT) and Concrete vs. Rebar."""
    generated: Dict[str, str] = {}

    girders_mt = _parse_float(inputs.get("steel_girders_wt_total")) or 0.0
    cb_top_mt = _parse_float(inputs.get("bracing_top_wt_total")) or 0.0
    cb_bot_mt = _parse_float(inputs.get("bracing_bot_wt_total")) or 0.0
    cb_diag_mt = _parse_float(inputs.get("bracing_diag_wt_total")) or 0.0
    cross_bracing_mt = cb_top_mt + cb_bot_mt + cb_diag_mt
    end_diaphragm_mt = (
        _parse_float(inputs.get("end_diaphragm_wt_total"))
        or _parse_float(inputs.get("diaphragm_wt_total"))
        or 0.0
    )

    steel_labels = ["Steel Plate\nGirders", "Cross\nBracing", "End\nDiaphragms"]
    steel_vals = [girders_mt, cross_bracing_mt, end_diaphragm_mt]

    if any(v > 0 for v in steel_vals):
        steel_path = os.path.join(tmp_images_dir, "steel_quantities.png")
        fig, ax = plt.subplots(figsize=(7.8, 4.0), dpi=300)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#FAFAFA")

        palette = [f"#{COLORS['primary_hex']}", "#3B82F6", "#6366F1"]
        bars = ax.bar(
            steel_labels,
            steel_vals,
            width=0.44,
            color=palette,
            edgecolor=f"#{COLORS['text_dark_hex']}",
            linewidth=0.75,
            zorder=3,
        )
        y_top = max(steel_vals) * 1.25
        ax.set_ylim(0, y_top if y_top > 0 else 1.0)
        ax.set_ylabel(
            "Structural Steel Weight (MT)",
            fontsize=10,
            fontweight="bold",
            color=f"#{COLORS['text_dark_hex']}",
        )
        ax.set_title(
            "Structural Steel Quantity Breakdown by Component (MT)",
            fontsize=11,
            fontweight="bold",
            pad=14,
            color=f"#{COLORS['text_dark_hex']}",
        )
        ax.grid(axis="y", linestyle=":", color=f"#{COLORS['grid_hex']}", zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar, val in zip(bars, steel_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() + (y_top * 0.025),
                f"{val:.2f} MT",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color=f"#{COLORS['text_dark_hex']}",
            )

        fig.savefig(steel_path, dpi=300, bbox_inches="tight", pad_inches=0.20)
        plt.close(fig)
        generated["steel_quantities"] = steel_path.replace("\\", "/")

    concrete_m3 = _parse_float(inputs.get("concrete_deck_vol_total")) or 0.0
    rebar_mt = _parse_float(inputs.get("rebar_deck_wt_total")) or 0.0

    if concrete_m3 > 0 or rebar_mt > 0:
        deck_mat_path = os.path.join(tmp_images_dir, "concrete_rebar_quantities.png")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 4.2), dpi=300)
        fig.patch.set_facecolor("white")
        fig.subplots_adjust(top=0.78, wspace=0.35)

        ax1.set_facecolor("#FAFAFA")
        b1 = ax1.bar(
            ["Deck Concrete\n(M40)"],
            [concrete_m3],
            width=0.38,
            color="#64748B",
            edgecolor=f"#{COLORS['text_dark_hex']}",
            linewidth=0.75,
            zorder=3,
        )
        y1 = max(concrete_m3 * 1.28, 1.0)
        ax1.set_ylim(0, y1)
        ax1.set_ylabel("Volume (m³)", fontsize=9.5, fontweight="bold", color=f"#{COLORS['text_dark_hex']}")
        ax1.set_title("Deck Concrete Volume (m³)", fontsize=10, fontweight="bold", pad=10, color=f"#{COLORS['text_dark_hex']}")
        ax1.grid(axis="y", linestyle=":", color=f"#{COLORS['grid_hex']}", zorder=0)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.text(
            b1[0].get_x() + b1[0].get_width() / 2.0,
            concrete_m3 + y1 * 0.03,
            f"{concrete_m3:.2f} m³",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=f"#{COLORS['text_dark_hex']}",
        )

        ax2.set_facecolor("#FAFAFA")
        b2 = ax2.bar(
            ["Reinforcement Steel\n(Fe 500)"],
            [rebar_mt],
            width=0.38,
            color=f"#{COLORS['primary_hex']}",
            edgecolor=f"#{COLORS['text_dark_hex']}",
            linewidth=0.75,
            zorder=3,
        )
        y2 = max(rebar_mt * 1.28, 1.0)
        ax2.set_ylim(0, y2)
        ax2.set_ylabel("Weight (MT)", fontsize=9.5, fontweight="bold", color=f"#{COLORS['text_dark_hex']}")
        ax2.set_title("Reinforcement Steel Weight (MT)", fontsize=10, fontweight="bold", pad=10, color=f"#{COLORS['text_dark_hex']}")
        ax2.grid(axis="y", linestyle=":", color=f"#{COLORS['grid_hex']}", zorder=0)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.text(
            b2[0].get_x() + b2[0].get_width() / 2.0,
            rebar_mt + y2 * 0.03,
            f"{rebar_mt:.2f} MT",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=f"#{COLORS['text_dark_hex']}",
        )

        fig.suptitle(
            "Deck Slab Material Summary: Concrete Volume vs. Reinforcement Weight",
            fontsize=11,
            fontweight="bold",
            y=0.98,
            color=f"#{COLORS['text_dark_hex']}",
        )

        fig.savefig(deck_mat_path, dpi=300, bbox_inches="tight", pad_inches=0.28)
        plt.close(fig)
        generated["concrete_rebar_quantities"] = deck_mat_path.replace("\\", "/")

    return generated