from datamodel_code_generator import InputFileType, generate
from pathlib import Path


def generate_models_from_schema(
    schema_filename: str = "./schema.json", output_filename: str = "./schema_model.py"
):
    schema_path = Path(schema_filename)
    output_path = Path(output_filename)

    generate(
        input_=schema_path, input_file_type=InputFileType.JsonSchema, output=output_path
    )


if __name__ == "__main__":
    generate_models_from_schema()
