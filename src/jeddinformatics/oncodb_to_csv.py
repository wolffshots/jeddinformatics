import csv
import sys
from loguru import logger


def convert_onco_to_csv(input: str = "data.txt", output: str = "data.csv") -> None:
    # Open the input file in read mode and the output file in write mode
    with open(input, "r") as infile, open(output, "w", newline="") as outfile:
        # Create a CSV reader object to read the tab-separated values
        reader = csv.reader(infile, delimiter="\t")

        # Create a CSV writer object to write the comma-separated values
        writer = csv.writer(outfile)

        # Write the header for the output file
        writer.writerow(["Series Name", "Y"])

        # Skip the header of the input file
        next(reader)

        # Iterate over the rows of the input file
        for row in reader:
            # Extract the 'Sample' and 'KPNB1_expression_value' values
            sample = row[0]
            expression_value = row[2]

            # Write the extracted values to the output file
            writer.writerow([sample, expression_value])
    logger.debug(f"wrote {output} from {input}")


# Running the main function
if __name__ == "__main__":
    logger.remove(0)
    logger.add(sys.stdout)
    logger.success("Starting oncodb to csv.")
    logger.add("oncodb_to_csv.log", retention="5 minute")
    with logger.catch(onerror=lambda _: sys.exit(1)):
        convert_onco_to_csv()
