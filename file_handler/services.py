# file_handler/services.py
import pandas as pd
from io import BytesIO
import re
import math


def sanitize_floats(value):
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    elif isinstance(value, list):
        return [sanitize_floats(v) for v in value]
    elif isinstance(value, dict):
        return {k: sanitize_floats(v) for k, v in value.items()}
    return value


def extract_number_from_string(value):
    numbers = re.findall(r'\d+', value)
    if numbers:
        return int(numbers[0])
    return None


def excel_formatter(file_obj, start_col=1, format_type="indexed_dict"):

    try:
        df = pd.read_excel(BytesIO(file_obj.read()))

        start_idx = start_col - 1
        df_selected = df.iloc[:, start_idx:]

        result = []

        for _, row in df_selected.iterrows():
            if format_type == "indexed_dict":
                row_dict = {
                    col_index + 1: value
                    for col_index, value in enumerate(row, start=start_idx)
                }

            elif format_type == "named_dict":
                row_dict = {
                    col_name: value
                    for col_name, value in zip(df_selected.columns, row)
                }

            elif format_type == "mixed_dict":
                row_dict = {
                    f"{col_index + 1}|{col_name}": value
                    for col_index, (col_name, value) in enumerate(zip(df_selected.columns, row), start=start_idx)
                }

            else:
                raise ValueError(f"Unknown format_type: {format_type}")

            result.append(row_dict)

        return result

    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")
