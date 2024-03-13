import json
import csv

def convert_highchart_to_csv(input:str="data.json", output:str="data.csv"):
    # Load the Highcharts configuration from a JSON file
    with open('data.json', 'r') as file:
        highcharts_config = json.load(file)

    # Extract scatter data (assume all remaining series are scatter data)
    scatter_data = []
    for series in highcharts_config['series'][1:]:
        for point in series['data']:
            scatter_data.append([series['name'], point['y']])

    # Write scatter data to CSV
    with open(output, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Series Name', 'Y'])
        writer.writerows(scatter_data)

    print("highchart_to_csv> wrote {output} from {input}")

# Running the main function
if __name__ == "__main__":
    convert_highchart_to_csv()
