import os
import sys
import fnmatch
from loguru import logger
from jeddinformatics import oncodb_to_csv
from jeddinformatics import highchart_json_to_csv
from jeddinformatics import plot_data

def replace_file_extension(file_path: str, new_extension: str) -> str:
    """
    Replaces the file extension of 'file_path' with 'new_extension'.

    Parameters:
    - file_path (str): The original file path.
    - new_extension (str): The new extension to replace the old one with.
      The extension should not contain a leading dot ('.').

    Returns:
    - str: The modified file path with the new extension.
    """
    # Split the file path into the path without the extension and the original extension
    base, _ = os.path.splitext(file_path)
    
    # Ensure the new extension does not start with a dot, and then append it
    new_extension = new_extension.lstrip('.')
    
    # Return the new file path
    return f"{base}.{new_extension}"

def process_csv(file_path: str) -> None:
    logger.info(f"processing CSV file: {file_path}")
    plot_data.plot_formatted_csv(input=file_path, output=replace_file_extension(file_path, "png"))

def process_json(file_path: str) -> None:    
    logger.info(f"processing JSON file: {file_path}")
    output_path = replace_file_extension(file_path, "csv")
    highchart_json_to_csv.convert_highchart_to_csv(input=file_path, output=output_path)
    process_csv(file_path=output_path)

def process_txt(file_path: str) -> None:
    logger.info(f"processing TXT file: {file_path}")
    output_path = replace_file_extension(file_path, "csv")
    oncodb_to_csv.convert_onco_to_csv(input=file_path, output=output_path)
    process_csv(file_path=output_path)

def process_files(root_directory: str = ".") -> None:
    ignored_file_path = './.fileignore'
    if not os.path.exists(ignored_file_path):
        ignored_file_path = os.path.join(os.path.dirname(__file__), ".fileignore")
    ignored_dir_path = './.dirignore'
    if not os.path.exists(ignored_dir_path):
        ignored_dir_path = os.path.join(os.path.dirname(__file__), ".dirignore")
    count_json = 0
    count_txt = 0

    try:
        with open(ignored_file_path, 'r') as ignore_file_file:
            ignored_file_patterns = [line.strip() for line in ignore_file_file]
    except:
        ignored_file_patterns = []

    try:
        with open(ignored_dir_path, 'r') as ignore_dir_file:
            ignored_dir_patterns = [line.strip() for line in ignore_dir_file]
    except:
        ignored_dir_patterns = []

    for root, _, files in os.walk(root_directory):
        for file in files:
            file_path: str = os.path.join(root, file)
            matching_ignored_file_patterns = [ignored_file_pattern for ignored_file_pattern in ignored_file_patterns if fnmatch.fnmatch(file, ignored_file_pattern)]
            if matching_ignored_file_patterns:
                logger.debug(f"skipping {file_path} because it matched ignored file pattern{'s' if len(matching_ignored_file_patterns) > 1 else ''}: {matching_ignored_file_patterns}")
                continue
            matching_ignored_dir_patterns = [ignored_dir_pattern for ignored_dir_pattern in ignored_dir_patterns if fnmatch.fnmatch(file_path, ignored_dir_pattern)]
            if matching_ignored_dir_patterns:
                logger.debug(f"skipping {file_path} because it matched ignored dir pattern{'s' if len(matching_ignored_dir_patterns) > 1 else ''}: {matching_ignored_dir_patterns}")
                continue
            # Split the path to extract directory levels
            path_components = file_path.split(os.sep)

            # Assign variables from the lowest level (nearest the data file) up to the highest known level
            gene_or_protein_name = path_components[-2]
            type_of_cancer = path_components[-3]
            source_database = path_components[-4]
            gene_or_protein_expression = path_components[-5]
            logger.info(f"starting {'gene' if gene_or_protein_expression.lower().find('gene') != -1 else 'protein'} name: {gene_or_protein_name}, cancer type: {type_of_cancer}, source: {source_database}")

            if file == 'data.json':
                process_json(file_path=file_path)
                count_json += 1
            elif file == 'data.txt':
                process_txt(file_path=file_path)
                count_txt += 1
    logger.info(f"finished processing {count_json} JSON files and {count_txt} TXT files")

# Assumed structure:
# ```
#  {gene or protein expression}
#   └───{source database}
#        └───{type of cancer}
#             └───{gene or protein name}
#                  └───{data.json or data.txt}
# ```

def main():
    with logger.catch(onerror=lambda _: sys.exit(1)):
        logger.remove(0)
        logger.add(sys.stdout)
        logger.success("Starting jeddinformatics.")
        logger.add("jeddinformatics.log", retention="5 minute")
        process_files(sys.argv[1]) if len(sys.argv) > 1 else process_files()

if __name__=="__main__":
    main()