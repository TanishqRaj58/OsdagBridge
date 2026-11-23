from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_TS_NO_OF_GIRDERS,
)
from osdagbridge.core.reports.styles import make_longtable


def _tex(value):
    """Escape a Python value safely for LaTeX embedding without stray glyphs."""
    s = str(value) if value is not None else ""
    if not s:
        return ""
    for uni, ascii_ in [("∠", "L"), ("ⅹ", "x"), ("×", "x"), ("¿", ">")]:
        s = s.replace(uni, ascii_)
    s = s.replace("\\", r"\textbackslash{}")
    s = s.replace("|", "/")
    for ch, esc in [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("_", r"\_\allowbreak{}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\^{}"),
    ]:
        s = s.replace(ch, esc)
    s = s.replace(":", r":\allowbreak{}")
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return "---"
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """Retrieve all girder labels and member IDs from backend keys."""
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0) or 0)
    entries = []
    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", f"G{i}"),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", f"G{i}M1"),
            )
        )
    return entries


def _fig_or_placeholder(path, caption, width=r"0.9\textwidth"):
    """Embed figure if path is provided, else show placeholder box."""
    if path:
        p = path.replace("\\", "/")
        return (
            r"\begin{figure}[H]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[width=" + width + "]{" + p + "}\n"
            r"\caption*{" + caption + "}\n"
            r"\end{figure}"
        )
    return (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\fbox{\parbox{0.97\textwidth}{" + "\n"
        r"\textit{[ PLACEHOLDER: " + caption + r" ]}" + "\n"
        r"}}" + "\n"
        r"\caption*{" + caption + "}\n"
        r"\end{figure}"
    )


def _fig_embed(path, caption, width=r"\textwidth", height=None):
    """Embed a real figure when path is provided; otherwise use an fbox placeholder."""
    if path:
        p = path.replace("\\", "/")
        opts = "width=" + width
        if height:
            opts += ",height=" + height + ",keepaspectratio"
        return (
            r"\begin{figure}[H]" + "\n"
            r"\vspace{-0.2em}" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[" + opts + "]{" + p + "}\n"
            r"\vspace{0.3em}" + "\n"
            r"\caption*{\small " + caption + "}\n"
            r"\vspace{-0.2em}" + "\n"
            r"\end{figure}"
        )
    return (
        r"\noindent\fbox{\parbox{0.97\textwidth}{" + "\n"
        r"\textit{[ PLACEHOLDER: " + caption + r" ]}" + "\n"
        r"}}"
    )