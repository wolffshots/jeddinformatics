import sys
import os
from typing import Callable
from loguru import logger
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from jeddinformatics import schema_model


def default_translation(input: str, _: object = {}) -> str:
    return input


def color_for_series(series: str, colors: object = {}) -> str:
    return colors.get(series, "purple")


def plot_formatted_csv(
    config: schema_model.Model,
    input: str = "data.csv",
    output: str = "output.png",
    translation_func: Callable[[str, object], str] = default_translation,
    cancer_type: str = "",
    is_gene: bool = False,
):
    # Read the scatter data from the CSV file
    scatter_data = pd.read_csv(input)

    # Initialize a Plotly figure
    fig = go.Figure()

    mappings = config["mappings"]
    colors = config["colors"]
    precedence = config["precedence"]

    sorted_unique_series = sorted(
        scatter_data["Series Name"].unique(),
        key=lambda x: (
            x not in precedence,
            precedence.index(x) if x in precedence else 0,
            x,
        ),
    )

    # Iterate over each unique series name in the scatter data
    for series_name in sorted_unique_series:
        # Filter data for the current series
        mask = scatter_data["Series Name"] == series_name
        if is_gene:
            scatter_data.loc[mask, "Y"] = np.log2(scatter_data.loc[mask, "Y"])

        name = (
            translation_func(cancer_type, mappings=mappings)
            if series_name == "Primary tumor" and cancer_type != ""
            else translation_func(series_name, mappings=mappings)
        )

        fig.add_trace(
            go.Box(
                y=scatter_data.loc[mask, "Y"],
                name=name,
                boxpoints="outliers",
                pointpos=0,
                marker=dict(
                    color=color_for_series(name, colors), size=config["point_size"]
                ),
                line=dict(
                    color=color_for_series("box", colors), width=config["line_width"]
                ),
                fillcolor="rgba(0,0,0,0)",
                jitter=config["jitter"],
            )
        )
    yaxes_title = "Z-value" if not is_gene else "log2(TPM)"

    # Update layout with titles and axis labels
    fig.update_layout(
        xaxis={"type": "category", "showline": True, "linecolor": "black"},
        yaxis={"showline": True, "linecolor": "black"},
        yaxis_title=translation_func(yaxes_title, mappings=mappings),
        showlegend=False,
        plot_bgcolor=colors["plot_background_color"],
        paper_bgcolor=colors["paper_background_color"],
    )

    # Save the image
    fig.write_image(
        file=output,
        format="png",
        engine="auto",
        width=config["plot_width"],
        height=config["plot_height"],
        scale=4,
    )
    logger.debug(f"wrote {output} from {input}")


def plot_formatted_csvs(
    config: schema_model.Model,
    inputs: list[str] = ["data.csv"],
    output: str = "output.png",
    translation_func: Callable[[str, object], str] = default_translation,
    cancer_type: str = "",
    is_gene: bool = False,
):
    # Initialize a Plotly figure
    fig = go.Figure()

    mappings = config["mappings"]
    colors = config["colors"]
    precedence = config["precedence"]
    for input in inputs:
        scatter_data = pd.read_csv(input)

        sorted_unique_series = sorted(
            scatter_data["Series Name"].unique(),
            key=lambda x: (
                x not in precedence,
                precedence.index(x) if x in precedence else 0,
                x,
            ),
        )

        # Iterate over each unique series name in the scatter data
        for series_name in sorted_unique_series:
            # Filter data for the current series
            mask = scatter_data["Series Name"] == series_name
            if is_gene:
                scatter_data.loc[mask, "Y"] = np.log2(scatter_data.loc[mask, "Y"])

            name: str = (
                translation_func(cancer_type, mappings=mappings)
                if series_name == "Primary tumor" and cancer_type != ""
                else translation_func(series_name, mappings=mappings)
            ) + " \n" + input.split(os.sep)[-2]

            fig.add_trace(
                go.Box(
                    y=scatter_data.loc[mask, "Y"],
                    name=name,
                    boxpoints="outliers",
                    pointpos=0,
                    marker=dict(
                        color=color_for_series(name.split(" ")[0], colors), size=config["point_size"]
                    ),
                    line=dict(
                        color=color_for_series("box", colors), width=config["line_width"]
                    ),
                    fillcolor="rgba(0,0,0,0)",
                    jitter=config["jitter"],
                )
            )
        yaxes_title = "Z-value" if not is_gene else "log2(TPM)"

    # Update layout with titles and axis labels
    fig.update_layout(
        xaxis={"type": "category", "showline": True, "linecolor": "black"},
        yaxis={"showline": True, "linecolor": "black"},
        yaxis_title=translation_func(yaxes_title, mappings=mappings),
        showlegend=False,
        plot_bgcolor=colors["plot_background_color"],
        paper_bgcolor=colors["paper_background_color"],
    )

    # Save the image
    fig.write_image(
        file=output,
        format="png",
        engine="auto",
        width=config["plot_width"],
        height=config["plot_height"],
        scale=4,
    )
    logger.debug(f"wrote {output} from {input}")


# Running the main function
if __name__ == "__main__":
    logger.remove(0)
    logger.add(sys.stdout)
    logger.success("Starting plot data.")
    logger.add("plot_data.log", retention="5 minute")
    with logger.catch(onerror=lambda _: sys.exit(1)):
        plot_formatted_csv()
