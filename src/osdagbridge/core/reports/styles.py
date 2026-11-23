# =============================================================================
# Centralized Formatting & Style System (Single Source of Truth)
# Defines page margins, header/footer clearance, color palette, table spacing,
# and repeating longtable builder consumed by all report modules.
# =============================================================================

COLORS = {
    "primary_hex": "91B014",        # Osdag signature green
    "primary_dark_hex": "6E870F",   # Darker green accent
    "header_bg_hex": "F2F6E4",      # Soft green header tint
    "zebra_bg_hex": "F9FBF4",       # Light row tint
    "pass_hex": "1E7E34",           # Pass / safe bar color
    "warn_hex": "D97706",           # Warning band (0.90 <= UR < 1.00)
    "fail_hex": "C82333",           # Fail / UR > 1.00 color
    "threshold_hex": "D62728",      # Red dashed threshold line (UR = 1.00)
    "text_dark_hex": "1F2937",      # Dark charcoal typography
    "grid_hex": "D1D5DB",           # Subtle gridline color
}

PAGE_GEOMETRY = {
    "paper": "a4paper",
    "font_size": "12pt",
    "margin_top": "0.90in",
    "margin_bottom": "1.15in",
    "margin_left": "0.85in",
    "margin_right": "0.85in",
    "headheight": "15pt",
    "headsep": "12pt",
    "footskip": "36pt",
}

TABLE_STYLE = {
    "tabcolsep": "6pt",
    "compact_tabcolsep": "3.5pt",
    "arraystretch": "1.14",
    "extrarowheight": "0.8pt",
    "arrayrulewidth": "0.5pt",
    "lt_pre": "4pt",
    "lt_post": "8pt",
    "needspace_lines": "6",
    "line_stretch": "1.15",
}


def sanitize_caption_text(text: str) -> str:
    """Clean caption/header text so dashes, pipes, and math symbols render safely."""
    if not text:
        return ""
    s = str(text)
    s = s.replace("---", "--")
    s = s.replace("|", "/")
    s = s.replace("&", r"\&")
    s = s.replace("%", r"\%")
    s = s.replace("_", r"\_")
    return s.strip()


def get_geometry_options() -> str:
    """Return geometry package options from PAGE_GEOMETRY."""
    g = PAGE_GEOMETRY
    return (
        f"{g['paper']}, top={g['margin_top']}, bottom={g['margin_bottom']}, "
        f"left={g['margin_left']}, right={g['margin_right']}, "
        f"headheight={g['headheight']}, headsep={g['headsep']}, "
        f"footskip={g['footskip']}"
    )


def get_color_definitions() -> str:
    """Return LaTeX \\definecolor commands from COLORS."""
    c = COLORS
    return (
        f"\\definecolor{{osdagGreen}}{{HTML}}{{{c['primary_hex']}}}\n"
        f"\\definecolor{{osdagHeaderBg}}{{HTML}}{{{c['header_bg_hex']}}}\n"
        f"\\definecolor{{osdagZebra}}{{HTML}}{{{c['zebra_bg_hex']}}}\n"
        f"\\definecolor{{osdagPass}}{{HTML}}{{{c['pass_hex']}}}\n"
        f"\\definecolor{{osdagFail}}{{HTML}}{{{c['fail_hex']}}}\n"
    )


def get_table_setup_latex() -> str:
    """Return global table spacing and page-break protection setup."""
    t = TABLE_STYLE
    return (
        f"\\setlength{{\\tabcolsep}}{{{t['tabcolsep']}}}\n"
        f"\\renewcommand{{\\arraystretch}}{{{t['arraystretch']}}}\n"
        f"\\setlength{{\\LTpre}}{{{t['lt_pre']}}}\n"
        f"\\setlength{{\\LTpost}}{{{t['lt_post']}}}\n"
        f"\\setlength{{\\arrayrulewidth}}{{{t['arrayrulewidth']}}}\n"
        f"\\setlength{{\\extrarowheight}}{{{t['extrarowheight']}}}\n"
    )


def get_header_footer_styles(pn: str, jn: str, rd: str, rv: str) -> str:
    """Return fancyhdr page styles with safe bottom rule clearance."""
    foot_rule_block = r"""  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{-22pt}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{4pt}%
    }{%
      \vspace{-8pt}%
    }%
    \color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}%
  }"""

    return (
        r"\fancypagestyle{main}{" + "\n"
        r"  \fancyhf{}" + "\n"
        r"  \fancyhead[L]{" + pn + r" $|$ " + jn + r"}" + "\n"
        r"  \fancyhead[R]{" + rd + r" $|$ " + rv + r"}" + "\n"
        r"  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}" + "\n"
        r"  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}" + "\n"
        r"  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}" + "\n"
        + foot_rule_block + "\n"
        r"}" + "\n"
        r"\fancypagestyle{plain}{" + "\n"
        r"  \fancyhf{}" + "\n"
        r"  \fancyhead[L]{" + pn + r" $|$ " + jn + r"}" + "\n"
        r"  \fancyhead[R]{" + rd + r" $|$ " + rv + r"}" + "\n"
        r"  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}" + "\n"
        r"  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}" + "\n"
        r"  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{2pt}}" + "\n"
        + foot_rule_block + "\n"
        r"}" + "\n"
        r"\fancypagestyle{firstpage}{" + "\n"
        r"  \fancyhf{}" + "\n"
        r"  \renewcommand{\headrulewidth}{0pt}" + "\n"
        r"  \fancyfoot[L]{Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay}" + "\n"
        r"  \fancyfoot[R]{Page \thepage\ of \pageref{LastPage}}" + "\n"
        r"  \renewcommand{\footrule}{\vspace{-8pt}\color{osdagGreen}\hrule width\headwidth height 1pt \vspace{6pt}}" + "\n"
        r"}" + "\n"
        r"\pagestyle{main}" + "\n"
        f"\\setstretch{{{TABLE_STYLE['line_stretch']}}}\n"
    )


def make_longtable(
    col_spec: str,
    caption: str,
    header_row: str,
    body_rows: str,
    note: str = "",
    compact: bool = False,
) -> str:
    """Build a LaTeX longtable with repeating headers and zero orphan headers."""
    clean_cap = sanitize_caption_text(caption)
    styled_header = r"\rowcolor{osdagHeaderBg} " + header_row

    prefix = ""
    suffix = ""
    if compact:
        prefix = (
            "\\begingroup\n"
            "\\footnotesize\n"
            f"\\setlength{{\\tabcolsep}}{{{TABLE_STYLE['compact_tabcolsep']}}}\n"
        )
        suffix = "\\endgroup\n"

    note_tex = f"\\noindent\\textit{{{note}}}\n" if note else ""

    return (
        "\n\\vspace{0.8em}\n"
        + prefix
        + f"\\begin{{longtable}}{{{col_spec}}}\n"
        + f"\\caption{{\\textbf{{{clean_cap}}}}} \\\\\n"
        + "\\hline\n"
        + styled_header + "\n"
        + "\\hline\n"
        + "\\endfirsthead\n\n"
        + "\\hline\n"
        + styled_header + "\n"
        + "\\hline\n"
        + "\\endhead\n\n"
        + "\\hline\n"
        + "\\endfoot\n\n"
        + "\\hline\n"
        + "\\endlastfoot\n\n"
        + body_rows + "\n"
        + "\\end{longtable}\n"
        + suffix
        + note_tex
    )


