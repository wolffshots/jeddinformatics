import os
import sys
import json
import fnmatch
from loguru import logger
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jeddinformatics import oncodb_to_csv
from jeddinformatics import highchart_json_to_csv
from jeddinformatics import plot_data
from jeddinformatics import generate_types

try:
    # Attempt to generate and import the model
    schema_file_path = "./schema.json"
    if not os.path.exists(schema_file_path):
        schema_file_path = os.path.join(os.path.dirname(__file__), "schema.json")
    if os.path.exists(schema_file_path):
        generate_types.generate_models_from_schema(
            schema_file_path, os.path.join(os.path.dirname(__file__), "schema_model.py")
        )
    else:
        raise FileNotFoundError(filename=schema_file_path)
    from schema_model import Model

    MappingsType = Model.__annotations__["mappings"]
except ImportError as e:
    logger.error(
        "the schema model could not be imported, did something go wrong generating it?"
    )
    raise e
except FileNotFoundError as e:
    logger.error(f"schema file '{schema_file_path}' does not exist")
    raise e
except Exception as e:
    logger.error(f"uncaught exception when trying to generate and import schema: {e}")
    raise e


def translate_in_mapping(input: str, mappings: MappingsType = {}) -> str:
    if input in mappings:
        logger.debug(
            f"string '{input}' found in mappings and updated to '{mappings[input]}'"
        )
        return mappings[input]
    return input


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
    new_extension = new_extension.lstrip(".")

    # Return the new file path
    return f"{base}.{new_extension}"


def process_csv(
    file_path: str, mappings: MappingsType, cancer_type: str = "", is_gene: bool = False
) -> None:
    logger.debug(f"processing CSV file: {file_path}")
    plot_data.plot_formatted_csv(
        input=file_path,
        output=replace_file_extension(file_path, "png"),
        mappings=mappings,
        translation_func=translate_in_mapping,
        cancer_type=cancer_type,
        is_gene=is_gene,
    )


def process_json(
    file_path: str, mappings: MappingsType, cancer_type: str = "", is_gene: bool = False
) -> None:
    logger.debug(f"processing JSON file: {file_path}")
    output_path = replace_file_extension(file_path, "csv")
    highchart_json_to_csv.convert_highchart_to_csv(input=file_path, output=output_path)
    process_csv(
        file_path=output_path,
        mappings=mappings,
        cancer_type=cancer_type,
        is_gene=is_gene,
    )


def process_txt(
    file_path: str, mappings: MappingsType, cancer_type: str = "", is_gene: bool = False
) -> None:
    logger.debug(f"processing TXT file: {file_path}")
    output_path = replace_file_extension(file_path, "csv")
    oncodb_to_csv.convert_onco_to_csv(input=file_path, output=output_path)
    process_csv(
        file_path=output_path,
        mappings=mappings,
        cancer_type=cancer_type,
        is_gene=is_gene,
    )


def process_files(root_directory: str = ".") -> None:  # noqa: C901
    config_file_path = "./config.json"
    if not os.path.exists(config_file_path):
        config_file_path = os.path.join(os.path.dirname(__file__), "config.json")

    ignored_file_path = "./.fileignore"
    if not os.path.exists(ignored_file_path):
        ignored_file_path = os.path.join(os.path.dirname(__file__), ".fileignore")

    ignored_dir_path = "./.dirignore"
    if not os.path.exists(ignored_dir_path):
        ignored_dir_path = os.path.join(os.path.dirname(__file__), ".dirignore")

    count_json = 0
    count_txt = 0

    try:
        with open(config_file_path, "r") as config_file:
            config: Model = json.load(config_file)
    except Exception as e:
        logger.warning(
            f"config file not found '{config_file_path}' with {e}, using default config"
        )
        config: Model = {"$schema": f"{schema_file_path}", "mappings": {}}
    mappings = config["mappings"]
    logger.debug(f"using mappings: {mappings}")
    # validate that the schema matches the config
    try:
        with open(schema_file_path, "r") as schema_file:
            schema = json.load(schema_file)
            validate(instance=config, schema=schema)
            logger.success("validation successful!")
    except ValidationError as e:
        logger.error(f"validation failed: {e}")
        raise e
    except Exception as e:
        raise e

    try:
        with open(ignored_file_path, "r") as ignore_file_file:
            ignored_file_patterns = [line.strip() for line in ignore_file_file]
    except Exception as e:
        logger.warning(
            f"ignored file '{ignored_file_path}' couldn't be parsed with {e}, using default of none"
        )
        ignored_file_patterns = []

    try:
        with open(ignored_dir_path, "r") as ignore_dir_file:
            ignored_dir_patterns = [line.strip() for line in ignore_dir_file]
    except Exception as e:
        logger.warning(
            f"ignored dirs '{ignored_dir_patterns}' couldn't be parsed with {e}, using default of none"
        )
        ignored_dir_patterns = []

    for root, _, files in os.walk(root_directory):
        for file in files:
            file_path: str = os.path.join(root, file)
            matching_ignored_file_patterns = [
                ignored_file_pattern
                for ignored_file_pattern in ignored_file_patterns
                if fnmatch.fnmatch(file, ignored_file_pattern)
            ]
            plural = "s" if len(matching_ignored_file_patterns) > 1 else ""
            if matching_ignored_file_patterns:
                logger.debug(
                    f"skipping {file_path} because it matched ignored file pattern{plural}: {matching_ignored_file_patterns}"
                )
                continue
            matching_ignored_dir_patterns = [
                ignored_dir_pattern
                for ignored_dir_pattern in ignored_dir_patterns
                if fnmatch.fnmatch(file_path, ignored_dir_pattern)
            ]
            if matching_ignored_dir_patterns:
                logger.debug(
                    f"""\
                    skipping {file_path} because it matched ignored dir \
                    pattern{'s' if len(matching_ignored_dir_patterns) > 1 else ''}: \
                    {matching_ignored_dir_patterns}\
                    """
                )
                continue
            # Split the path to extract directory levels
            path_components = file_path.split(os.sep)

            # Assign variables from the lowest level (nearest the data file) up to the highest known level
            gene_or_protein_name = path_components[-2]
            cancer_type = path_components[-3]
            source_database = path_components[-4]
            is_gene = path_components[-5].lower().find("gene") != -1
            gene_or_protein_expression = "gene" if is_gene else "protein"
            name_string = f"starting {gene_or_protein_expression} with name: {gene_or_protein_name}"
            logger.info(
                f"{name_string}, cancer type: {cancer_type}, source: {source_database}"
            )

            if file == "data.json":
                process_json(
                    file_path=file_path,
                    mappings=mappings,
                    cancer_type=cancer_type,
                    is_gene=is_gene,
                )
                count_json += 1
            elif file == "data.txt":
                process_txt(
                    file_path=file_path,
                    mappings=mappings,
                    cancer_type=cancer_type,
                    is_gene=is_gene,
                )
                count_txt += 1
    logger.info(
        f"finished processing {count_json} JSON files and {count_txt} TXT files"
    )


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
        logger.add(sys.stdout, level="INFO")
        logger.success("Starting jeddinformatics.")
        logger.add("jeddinformatics.log", retention="5 minute", level="DEBUG")
        process_files(sys.argv[1]) if len(sys.argv) > 1 else process_files()


if __name__ == "__main__":
    main()
