
import os
import math
import warnings


def _valid_number(value):
    """Return a finite, nonnegative float, or None for invalid values."""
    try:
        number = float(value)
        return number if math.isfinite(number) and number >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def _max_value(values):
    """Return the maximum valid utilization ratio."""
    valid = [_valid_number(value) for value in values]
    valid = [value for value in valid if value is not None]
    return max(valid) if valid else None



def _extract_end_diaphragm_values(output_dict):
    """Extract available end-diaphragm member efficiencies."""
    pair_designs = output_dict.get("end_diaphragm_design_results", {})
    observations = []

    if not isinstance(pair_designs, dict):
        return observations

    for pair, members in pair_designs.items():
        if not isinstance(members, dict):
            continue

        for member, force_types in members.items():
            if not isinstance(force_types, dict):
                continue

            for force_type, raw in force_types.items():
                if not isinstance(raw, dict):
                    continue

                efficiency = raw.get("Member.efficiency")
                if efficiency is None:
                    efficiency = raw.get("Optimum.UR")

                value = _valid_number(efficiency)

                if value is not None:
                    label = f"{pair} {member} {force_type}"
                    observations.append((label, value))

    return observations



def _save_bar_chart(plt, labels, values, path, title, xlabel,
                    threshold_orientation="vertical", figsize=(9, 5)):
    """Create and save a utilization bar chart."""
    fig, ax = plt.subplots(figsize=figsize)

    if threshold_orientation == "horizontal":
        ax.bar(labels, values)
        ax.axhline(
            1.0, color="red", linestyle="--",
            linewidth=1.5, label="Limit: UR = 1.0"
        )
        ax.set_ylabel(xlabel)
        ax.tick_params(axis="x", rotation=20)
    else:
        ax.barh(labels, values)
        ax.axvline(
            1.0, color="red", linestyle="--",
            linewidth=1.5, label="Limit: UR = 1.0"
        )
        ax.set_xlabel(xlabel)

    ax.set_title(title)
    ax.legend()
    ax.grid(
        axis="y" if threshold_orientation == "horizontal" else "x",
        linestyle="--",
        alpha=0.35,
    )

    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _figure_latex(path, caption, width=0.9):
    """Return LaTeX for a saved chart."""
    image_path = path.replace("\\", "/")
    return (
        r"\begin{figure}[H]\centering"
        r"\includegraphics[width="
        + str(width)
        + r"\textwidth]{"
        + image_path
        + r"}\caption{"
        + caption
        + r"}\end{figure}"
    )


def create_utilization_charts(output_dict, image_dir, bridge=None):
    """Create individual and overall utilization charts from design results."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        warnings.warn("Matplotlib is unavailable; utilization charts skipped.")
        return ""

    os.makedirs(image_dir, exist_ok=True)

    figures = []
    category_maxima = {}

    # ---------------------------------------------------------
    # 1. STEEL PLATE GIRDER
    # Source stores these eight values as percentages.
    # ---------------------------------------------------------
    girder_keys = [
        ("Flexure", "util.flexure"),
        ("Shear", "util.shear"),
        ("Interaction", "util.interaction"),
        ("Lateral torsional buckling", "util.ltb"),
        ("Longitudinal/transverse shear", "util.long_trans_shear"),
        ("Fatigue", "util.fatigue"),
        ("Stress limitation", "util.stress_limitation"),
        ("Deflection/crack", "util.deflection_crack"),
    ]

    girder_labels = []
    girder_values = []

    for label, key in girder_keys:
        percentage = _valid_number(output_dict.get(key))
        if percentage is not None:
            girder_labels.append(label)
            girder_values.append(percentage / 100.0)

    if girder_values:
        category_maxima["Steel Plate Girders"] = max(girder_values)

        path = os.path.join(image_dir, "girder_utilization.png")
        _save_bar_chart(
            plt, girder_labels, girder_values, path,
            "Plate Girder Design Utilization",
            "Utilization Ratio",
        )
        figures.append(
            _figure_latex(path, "Plate girder utilization ratios")
        )
    else:
        warnings.warn("No valid steel plate girder utilization data found.")

    # ---------------------------------------------------------
    # 2. CONCRETE DECK SLAB
    # Source values are already utilization ratios.
    # ---------------------------------------------------------
    deck = output_dict.get("deck_design_results", {})
    if not isinstance(deck, dict):
        deck = {}

    deck_keys = [
        ("Bottom ULS flexure", "ur_bot_uls"),
        ("Top ULS flexure", "ur_top_uls"),
        ("Bottom concrete stress", "ur_bot_sls_c"),
        ("Top concrete stress", "ur_top_sls_c"),
        ("Bottom reinforcement stress", "ur_bot_sls_s"),
        ("Top reinforcement stress", "ur_top_sls_s"),
        ("Bottom crack width", "ur_bot_crack"),
        ("Top crack width", "ur_top_crack"),
        ("Bottom shear", "ur_bot_shear"),
        ("Bottom punching", "ur_bot_punch"),
        ("Overhang ULS flexure", "ur_oh_uls"),
        ("Overhang concrete stress", "ur_oh_sls_c"),
        ("Overhang reinforcement stress", "ur_oh_sls_s"),
        ("Overhang crack width", "ur_oh_crack"),
    ]

    deck_labels = []
    deck_values = []

    for label, key in deck_keys:
        value = _valid_number(deck.get(key))
        if value is not None:
            deck_labels.append(label)
            deck_values.append(value)

    if deck_values:
        category_maxima["Concrete Deck Slab"] = max(deck_values)

        path = os.path.join(image_dir, "deck_utilization.png")
        _save_bar_chart(
            plt, deck_labels, deck_values, path,
            "Concrete Deck Slab Design Utilization",
            "Utilization Ratio",
            figsize=(9, 6),
        )
        figures.append(
            _figure_latex(path, "Concrete deck slab utilization ratios")
        )
    else:
        warnings.warn("No valid concrete deck slab utilization data found.")

    # ---------------------------------------------------------
    # 3. CROSS BRACING
    # Values come from the existing ReportDataBridge accessor.
    # ---------------------------------------------------------
    bracing_labels = []
    bracing_values = []

    if bridge is not None:
        try:
            for pair in bridge.get_cb_pairs():
                for member in ("diagonal", "chord"):
                    for force_type in ("compression", "tension"):
                        value = _valid_number(
                            bridge.get_cb_efficiency(
                                pair, member, force_type
                            )
                        )
                        if value is not None:
                            bracing_labels.append(
                                f"{pair} {member} {force_type}"
                            )
                            bracing_values.append(value)
        except (AttributeError, TypeError, ValueError):
            warnings.warn("Could not extract all cross-bracing results.")

    if bracing_values:
        category_maxima["Cross Bracing"] = max(bracing_values)

        path = os.path.join(image_dir, "bracing_utilization.png")
        _save_bar_chart(
            plt, bracing_labels, bracing_values, path,
            "Cross-Bracing Utilization",
            "Utilization Ratio",
        )
        figures.append(
            _figure_latex(path, "Cross-bracing utilization ratios")
        )
    else:
        warnings.warn("No valid cross-bracing utilization data found.")

    # ---------------------------------------------------------
    # 4. END DIAPHRAGMS
    # Extract available raw Osdag efficiencies.
    # ---------------------------------------------------------
    diaphragm_observations = _extract_end_diaphragm_values(output_dict)

    if diaphragm_observations:
        diaphragm_labels = [
            label for label, _ in diaphragm_observations
        ]
        diaphragm_values = [
            value for _, value in diaphragm_observations
        ]

        category_maxima["End Diaphragms"] = max(diaphragm_values)

        path = os.path.join(image_dir, "end_diaphragm_utilization.png")
        _save_bar_chart(
            plt, diaphragm_labels, diaphragm_values, path,
            "End Diaphragm Utilization",
            "Utilization Ratio",
            figsize=(10, 6),
        )
        figures.append(
            _figure_latex(path, "End diaphragm utilization ratios")
        )
    else:
        warnings.warn(
            "No valid end-diaphragm member efficiencies were available. "
            "Some diaphragm types may not produce per-member design results."
        )

    # ---------------------------------------------------------
    # 5. OVERALL UTILIZATION COMPARISON
    # Each bar represents the maximum valid UR in its category.
    # ---------------------------------------------------------
    if category_maxima:
        overall_labels = list(category_maxima.keys())
        overall_values = list(category_maxima.values())

        path = os.path.join(image_dir, "overall_utilization.png")
        _save_bar_chart(
            plt, overall_labels, overall_values, path,
            "Overall Structural Utilization Comparison",
            "Maximum Utilization Ratio",
            threshold_orientation="horizontal",
            figsize=(9, 5),
        )
        figures.append(
            _figure_latex(
                path,
                "Maximum utilization ratio across structural components",
            )
        )
    else:
        warnings.warn(
            "No valid utilization data found; overall chart was not generated."
        )

    if not figures:
        return ""

    return (
        "\n\\chapter{Structural Utilization Ratios}\n"
        "\\label{ch:utilization-ratios}\n"
        + "\n\n".join(figures)
        + "\n"
    )
