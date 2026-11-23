# OsdagBridge Design Report Module — Refactoring & Visual Enhancements

**Project:** Short Span Steel Girder Bridge - Mumbai (`Job Number: 01` | `Report Version: 2.0`)  
**Author:** Tanishq Raj[cite: 12]  
**Repository / Branch:** `https://github.com/TanishqRaj58/OsdagBridge` (`dev`)  
**Target Module:** `D:\Coding\OsdagBridge\src\osdagbridge\core\reports\`  
**Baseline vs. Final Output:** `Report_Before.pdf` vs. `Report_After.pdf` (62 pages verified)[cite: 12]

---

## 1. Objective & Scope

This refactoring improves layout stability, load-combination text wrapping in narrow table columns, LaTeX/PyLaTeX escaping and unit formatting, multi-page table pagination, and engineering visualization quality in the **OsdagBridge** PDF Design Report generator without modifying core structural analysis or design check calculations. The baseline export (`Report_Before.pdf`) was compared against the refactored output (`Report_After.pdf`, `Page 1 of 62` through `Page 62 of 62`)[cite: 12] to resolve table column overflow, pagination, and visual defects.

---

## 2. Key Code & LaTeX / PyLaTeX Modifications

### Load-Combination Wrapping & String Safety (`report_utils.py`, `chap4.py`, `chap5.py`)
- Updated `_format_lc()` in `report_utils.py` to avoid locking entire load-combination strings inside single unbreakable `\mbox{...}` boxes, allowing long load combinations in narrow columns (including **Table 4.1**, **Table 4.2**, and **Table 5.29**) to wrap cleanly across lines without overlapping adjacent columns.
- Hardened `_tex()` and chapter string formatting so special characters, underscores, subscripts/superscripts, comparison operators, and engineering units (`kN/m³`, `m/s`, `°C`, `mm`, `m`, `MT`, `m³`) render cleanly under `pdflatex`.

### Centralized Styling & Pagination (`styles.py`, `report_generator.py`)
- Centralizes page margins/geometry, header/footer clearance, color definitions, and table/spacing parameters in `styles.py`.
- Configures repeating `longtable` headers (`\endfirsthead` and `\endhead`) across multi-page tables and keeps page numbering synchronized (`Page 1 of 62` through `Page 62 of 62`)[cite: 12].

### Chapter-Wise Refinements (`executive_summary.py`, `chap2.py`–`chap8.py`)
- **Executive Summary & Input Parameters (`executive_summary.py`, `chap2.py`):** Reconciled executive summary status consistency with detailed design outcomes, added missing units (`m`, `mm`) in project overview entries, and standardized girder section dimension units (`mm`) in `Table 2.7`.
- **Loads & Load Combinations (`chap3.py`):** Separated **Vehicle Live Loads (LL)** (`Table 3.3`) and **Footpath Live Loads (LL)** (`Table 3.4`) into dedicated **Parameter | Value | Unit** tables, formatted units (`kN/m³`, `m/s`, `°C`), marked missing entries explicitly as `N/A`, and cleaned load combination tables (`Table 3.8`).
- **Analysis & Design Checks (`chap4.py`, `chap5.py`):** Populated support reactions in `Table 4.2`, improved load-case wrapping in `Table 4.1`, `Table 4.2`, and `Table 5.29`, resolved girder block spacing/footer clearance, removed stray `*` characters, and formatted `Post-Critical` and intermediate stiffener spacing (`2030 mm`).
- **Drawings, Material Take-off & Codes (`chap6.py`, `chap7.py`, `chap8.py`):** Added float placement barriers around Section 6.3, reconciled `Table 7.1` quantities with structural steel breakdown figures (including End Diaphragms), and aligned reference/code formatting with the centralized style rules.

### Programmatic 300-DPI Visualizations (`charts.py`)
- **Section 5.5 (Overall Design Check Summary):** Generates a bar chart of governing Utilization Ratios ($\text{UR} = \text{Demand} / \text{Capacity}$) across primary structural elements with a dashed $\text{UR} = 1.00$ reference line.
- **Chapter 7 (Material Take-off & Quantity Summary):** Generates **Structural Steel Quantity Breakdown by Component (MT)** and **Deck Slab Material Summary (Concrete Volume in $\text{m}^3$ vs. Reinforcement Steel Weight in MT)** with adjusted title padding to prevent top clipping.

---

## 3. Reproducing the Report

1. Launch OsdagBridge from the source directory using Python (`-B` avoids stale `.pyc` bytecode):
   ```cmd
   cd /d D:\Coding\OsdagBridge\src
   python -B -m osdagbridge.desktop