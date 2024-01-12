import configparser
import os.path
import pathlib

rbr_tools_configuration = {
    "driver": "helpy_helperton",
    "org": "example.com",
    "token": "",
    "url": "http://localhost:8086",
    "measurement": "RBR_RUN",
    "bucket": "rbrtelemetry",
    "lookback_window": "-1d",
    "arrow_scale": 1,
    "arrow_density": 10,
    "maps_ini_path": "",
    "config_path": os.path.join(pathlib.Path.home(), ".rbr_tools.cfg"),
    "rbr_telemetry_host": "127.0.0.1",
    "rbr_telemetry_port": 6776
}

def configure_from_file(config_path=os.path.join(pathlib.Path.home(), ".rbr_tools.cfg")):
    config = configparser.ConfigParser()
    config.read(config_path)
    for section in ["influx", "search", "general", "telemetry"]:
        for key, val in config[section].items():
            if key in rbr_tools_configuration:
                rbr_tools_configuration[key] = val