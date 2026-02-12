import ast
import io
from PIL import Image

def parse_sensor_info(col_name: str):
    if "observation.images" not in col_name or "cam_" in col_name:
        return None

    is_left = "left" in col_name
    part_name = None
    sensor_type = None

    if "palm" in col_name:
        part_name = "palm"
    elif "thumb" in col_name:
        part_name = "thumb"
    elif "index" in col_name:
        part_name = "index"
    elif "middle_finger" in col_name:
        part_name = "middle"
    elif "ring" in col_name:
        part_name = "ring"
    elif "little" in col_name or "pinky" in col_name:
        part_name = "little"

    if "palm" in col_name:
        sensor_type = "palm"
    elif "tip" in col_name:
        sensor_type = "tip"
    elif "pad" in col_name:
        sensor_type = "pad"
    elif "nail" in col_name:
        sensor_type = "nail"
    elif "middle" in col_name and part_name == "thumb":
        sensor_type = "middle"

    if part_name and sensor_type:
        return part_name, sensor_type, is_left
    
    return None

def decode_image_bytes(raw_val):
    if isinstance(raw_val, dict):
        return raw_val['bytes']
    elif isinstance(raw_val, str):
        return ast.literal_eval(raw_val)['bytes']
    elif isinstance(raw_val, bytes):
        return raw_val
    else:
        raise ValueError(f"Unknown data type for image data: {type(raw_val)}")

def load_image_from_bytes(img_bytes):
    if not img_bytes:
        return None
    return Image.open(io.BytesIO(img_bytes))