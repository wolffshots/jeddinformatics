import pandas as pd
import plotly.graph_objects as go

def plot_formatted_csv(input: str ="data.csv", output: str = "output.png"):
    # Read the scatter data from the CSV file
    scatter_data = pd.read_csv(input)

    # Initialize a Plotly figure
    fig = go.Figure()

    # Iterate over each unique series name in the scatter data
    for series_name in scatter_data['Series Name'].unique():
        # Filter data for the current series
        series_data = scatter_data[scatter_data['Series Name'] == series_name]

        fig.add_trace(go.Box(
            y=series_data['Y'],
            name=series_name,
            boxpoints='all',
            pointpos=0,
        ))

    # Update layout with titles and axis labels
    fig.update_layout(
        title='Scatter Data with Box and Whisker Plot',
        xaxis={'type': 'category'},
        xaxis_title='Data set',
        yaxis_title='Z-value',
        legend_title='Sample type'
    )

    # Save the image
    fig.write_image(file=output,format='png', engine='auto', width=960, height=540, scale=4)
    print("plot_data> wrote {output} from {input}")

# Running the main function
if __name__ == "__main__":
    plot_formatted_csv()
