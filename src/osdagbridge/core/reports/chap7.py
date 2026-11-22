
import os
import math


def _numeric_value(value):
    """Convert a quantity to a finite number; ignore unavailable values."""
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def _create_quantity_charts(input_dict, image_dir):
    """Create material quantity charts from calculated report values."""
    if not image_dir:
        return ""

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return ""

    os.makedirs(image_dir, exist_ok=True)
    figures = []

    # Steel weights in metric tonnes
    steel_items = [
        ("Girders", "steel_girders_wt_total"),
        ("Top bracing", "bracing_top_wt_total"),
        ("Bottom bracing", "bracing_bot_wt_total"),
        ("Diagonal bracing", "bracing_diag_wt_total"),
    ]

    labels, values = [], []
    for label, key in steel_items:
        value = _numeric_value(input_dict.get(key))
        if value is not None:
            labels.append(label)
            values.append(value)

    if values:
        path = os.path.join(image_dir, "steel_quantities.png")
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(labels, values)
        ax.set_title("Structural Steel Quantities")
        ax.set_ylabel("Weight (MT)")
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        figures.append(
            r"\begin{figure}[H]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[width=0.85\textwidth]{"
            + path.replace("\\", "/") + "}" + "\n"
            r"\caption{Structural steel quantities}" + "\n"
            r"\end{figure}"
        )

    # Concrete volume and reinforcement weight have different units.
    concrete = _numeric_value(input_dict.get("concrete_deck_vol_total"))
    reinforcement = _numeric_value(input_dict.get("rebar_deck_wt_total"))

    if concrete is not None or reinforcement is not None:
        path = os.path.join(image_dir, "concrete_reinforcement.png")
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))

        if concrete is not None:
            axes[0].bar(["Deck slab"], [concrete])
            axes[0].set_title("Concrete")
            axes[0].set_ylabel("Volume (m³)")
            axes[0].grid(axis="y", linestyle="--", alpha=0.35)
        else:
            axes[0].set_visible(False)

        if reinforcement is not None:
            axes[1].bar(["Deck reinforcement"], [reinforcement])
            axes[1].set_title("Reinforcement")
            axes[1].set_ylabel("Weight (MT)")
            axes[1].grid(axis="y", linestyle="--", alpha=0.35)
        else:
            axes[1].set_visible(False)

        fig.tight_layout()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        figures.append(
            r"\begin{figure}[H]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[width=0.85\textwidth]{"
            + path.replace("\\", "/") + "}" + "\n"
            r"\caption{Concrete and reinforcement quantities}" + "\n"
            r"\end{figure}"
        )

    if not figures:
        return ""

    return (
        "\n\\noindent\\textbf{Material Quantity Charts}\n\n"
        + "\n\n".join(figures)
        + "\n"
    )


def ch7_quantities(input_dict, image_dir=None):
    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

\noindent\textbf{Table 7.1  Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}

\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
\hline
\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\
\hline
\endfirsthead

\hline
\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\
\hline
\endhead

\hline
\multicolumn{7}{r}{\textit{Continued on next page}} \\
\endfoot

\hline
\endlastfoot
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
\end{longtable}
\endgroup
""" + _create_quantity_charts(input_dict, image_dir)
