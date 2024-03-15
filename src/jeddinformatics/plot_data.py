import sys
from typing import Callable
from loguru import logger
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def default_translation(input: str, _: object = {}) -> str:
    return input


def plot_formatted_csv(
    input: str = "data.csv",
    output: str = "output.png",
    mappings: object = {},
    translation_func: Callable[[str, object], str] = default_translation,
    cancer_type: str = "",
    is_gene: bool = False,
):
    # Read the scatter data from the CSV file
    scatter_data = pd.read_csv(input)

    # Initialize a Plotly figure
    fig = go.Figure()

    # Iterate over each unique series name in the scatter data
    for series_name in scatter_data["Series Name"].unique():
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
                boxpoints="all",
                pointpos=0,
            )
        )
    yaxes_title = "Z-value" if not is_gene else "log2(TPM)"

    # Update layout with titles and axis labels
    fig.update_layout(
        xaxis={"type": "category"},
        yaxis_title=translation_func(yaxes_title, mappings=mappings),
        legend_title=translation_func("Sample type", mappings=mappings),
    )

    # Save the image
    fig.write_image(
        file=output, format="png", engine="auto", width=960, height=540, scale=4
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
