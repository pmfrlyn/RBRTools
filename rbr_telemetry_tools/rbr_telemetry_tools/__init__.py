import configparser
import struct
from .format import FORMAT_STRUCT_PATTERN, MESSAGE_LENGTH, FORMAT_FIELDS

MAPS_INDEX = {}

def configure_map_index(map_ini_file):
    config = configparser.ConfigParser()
    config.read(map_ini_file)

    MAPS_INDEX.update({int(s.replace("Map", "")): config[s]["StageName"].replace("\"", "")
                       for s in config.sections()
                            if "Map" in s and "StageName" in config[s]})
    

def process_telemetry_packet(data, unit=None):
    point = {}
    unpacked_data = struct.unpack_from(FORMAT_STRUCT_PATTERN, data, offset=0)
    for idx, field_name in enumerate(FORMAT_FIELDS):
        value = unpacked_data[idx]
        if "temperature" in field_name:
            if unit == "F":
                value = 1.8 * (value - 273) + 32
            elif unit == "C":
                value = value - 273.15

        point[field_name] = value

    point["stage.name"] = MAPS_INDEX.get(point['stage.index'], "UNKNOWN")

    return point