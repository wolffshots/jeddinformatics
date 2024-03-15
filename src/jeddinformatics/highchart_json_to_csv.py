import json
import csv
import sys
from loguru import logger


def convert_highchart_to_csv(input: str = "data.json", output: str = "data.csv"):
    # Load the Highcharts configuration from a JSON file
    with open(input, "r") as file:
        highcharts_config = json.load(file)

    # Extract scatter data (assume all remaining series are scatter data)
    scatter_data = []
    for series in highcharts_config["series"][1:]:
        for point in series["data"]:
            scatter_data.append([series["name"], point["y"]])

    # Write scatter data to CSV
    with open(output, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Series Name", "Y"])
        writer.writerows(scatter_data)

    logger.debug(f"wrote {output} from {input}")


# Running the main function
if __name__ == "__main__":
    logger.remove(0)
    logger.add(sys.stdout)
    logger.success("Starting oncodb to csv.")
    logger.add("oncodb_to_csv.log", retention="5 minute")
    with logger.catch(onerror=lambda _: sys.exit(1)):
        convert_highchart_to_csv()
