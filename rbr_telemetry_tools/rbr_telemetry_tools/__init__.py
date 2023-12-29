import struct
from .format import FORMAT_STRUCT_PATTERN, MESSAGE_LENGTH, FORMAT_FIELDS

# F = 1.8*(K-273) + 32

def process_telemetry_packet(data, unit="C"):
    point = {}
    unpacked_data = struct.unpack_from(FORMAT_STRUCT_PATTERN, data, offset=0)
    for idx, field_name in enumerate(FORMAT_FIELDS):
        value = unpacked_data[idx]
        if "temperature" in field_name:
            if unit == "F":
                value = 1.8 * (value - 273) + 32
            elif unit == "C":
                value = value - 273.15
            elif unit == "K":
                pass #cheeky

        point[field_name] = value

    return point
    