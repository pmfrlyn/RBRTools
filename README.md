# RBR Tools

This package contains a few tools that I have written for the Richard Burns Rally simulator software. The package contains three main tools:

* `rbr_setup_compare`: This tool allows you to compare to setup (lsp) files and show what is different between them. Useful when you're trying to understand setups and trying to merge them
* `rbr_influx_telemetry_sender`: This tool connects to the RBR UDP telemetry endpoint and repeats all telemetry information to an InfluxDB bucket, tagging it with extra information such as: grouping runs into sessions, driver, runs (and how many attempts,) as well as decoding the stage name from the stage id provided by RBR
* `rbr_run_plotter`: A for-fun tool that will let you retrieve a run within a session as well as all attempts and then overlay their paths in an X/Y plot. The tool also has the ability to overlay yaw (car facing) arrows to let you see how sideways you got

The `rbr_tools` python package itself contains libraries to let you compare setups, retrive telemetry data, as well as process the telemetry packets.

## Installation

This package is not available through PyPI, but can be easily installed by downloading the package and then using `setuptools`.

Below is an example of how to install it into a new virtual environment.

```
$ cd path\to\RBRTools
$ python -m venv ENV
$ pip install .
```

## Configuration

The `rbr_tools` package can be configured via an ini file, by default located in `$HOMEDIR/.rbr_tools.cfg` and makes using the telemetry related tools much more pleasant. An example file is shown below, and one is also included in the `samples/` directory.

```
[general]
driver = H. Helperton
measurement = RBR_RUN
maps_ini_path = C:\Richard Burns Rally\Maps\Tracks.ini

[telemetry]
rbr_telemetry_host = localhost
rbr_telemetry_port = 6776

[influx]
org = example.com
url = http://example.com:8086
token = ohyouthoughtiwasgonnagiveyouarealtoken==

[search]
bucket = rbrtelemetry
lookback_window = -3d
```