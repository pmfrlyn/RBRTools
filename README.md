# Spots' RBR Tools 
 
This package contains a few tools that I have written for the Richard Burns Rally simulator software. The package contains three main tools: 
 
* rbr_setup_compare: This tool allows you to compare to setup (lsp) files and show what is different between them. Useful when you're trying to understand setups and trying to merge them 
* rbr_influx_telemetry_sender: This tool connects to the RBR UDP telemetry endpoint and repeats all telemetry information to an InfluxDB bucket, tagging it with extra information such as: grouping runs into sessions, driver, runs (and how many attempts,) as well as decoding the stage name from the stage id provided by RBR 
* rbr_run_plotter: A for-fun tool that will let you retrieve a run within a session as well as all attempts and then overlay their paths in an X/Y plot. The tool also has the ability to overlay yaw (car facing) arrows to let you see how sideways you got 
 
The rbr_tools python package itself contains libraries to let you compare setups, retrive telemetry data, as well as process the telemetry packets. 
 
## Installation 
 
This package is not available through PyPI, but can be easily installed by downloading the package and then using setuptools. 
 
Below is an example of how to install it into a new virtual environment. 
 
 
$ cd path\to\RBRTools 
$ python -m venv ENV 
$ pip install . 
 
 
## Configuration 
 
The rbr_tools package can be configured via an ini file, by default located in $HOMEDIR/.rbr_tools.cfg and makes using the telemetry related tools much more pleasant. An example file is shown below, and one is also included in the samples/ directory. 
 
```
[general] 
driver = H. Helperton 
measurement = RBR_RUN 
maps_ini_path = C:\Richard Burns Rally\Maps\Tracks.ini 
 
[telemetry] 
rbr_telemetry_host = localhost 
rbr_telemetry_port = 6776 
 
[influx] 
bucket = rbrtelemetry 
org = example.com 
url = http://example.com:8086 
token = ohyouthoughtiwasgonnagiveyouarealtoken== 
 
[search] 
lookback_window = -3d ;change this value to widen or narrow your search window (bigger is slower) 
```
 
I recommend you create a config file to save you from typing out a bunch of command line options every single time. 
 
## Usage 
I'm going to assume the tools are installed in Windows
 
### rbr_setup_compare 

``` 
$ rbr_setup_compare.exe
Usage rbr_setup_compare.py file1 file2 
```

### rbr_influx_telemetry_sender

There's a few prerequisites:
* A configuredf and running InfluxDB endpoint
* A bucket, a token, and org in Influx

```
> rbr_influx_telemetry_sender.exe --help
Usage: rbr_influx_telemetry_sender [OPTIONS]

Options:
  --driver TEXT         Driver to tag this telemetry under
  --measurement TEXT    Influx measurement to search under
  --bucket TEXT         InfluxDB bucket to search
  --org TEXT            InfluxDB Org to query
  --token TEXT          InfluxDB API token
  --url TEXT            InfluxDB URL
  --host TEXT           Telemetry host
  --port TEXT           Telemetry port
  --config_path PATH    Configuration file for the rbr_tools package
  --maps_ini_path PATH  Location of your Tracks.ini file
  --help                Show this message and exit.
```
### rbr_run_plotter

This tool uses matplotlib to display the path a run has taken through the course. It can be useful to look at line differences between attempts at a particular stage.

This tool has a few commandlets. Below is a sample session with the tool

```
> rbr_run_plotter.exe --help
Usage: rbr_run_plotter [OPTIONS] COMMAND [ARGS]...

Options:
  --time-window TEXT  lookback window for queries
  --measurement TEXT  Influx measurement to search under
  --bucket TEXT       InfluxDB bucket to search
  --org TEXT          InfluxDB Org to query
  --token TEXT        InfluxDB API token
  --url TEXT          InfluxDB URL
  --config_path PATH
  --help              Show this message and exit.

Commands:
  list-run-attempts
  list-runs
  list-sessions
  plot-attempts
```

`list-sessions` sessions shows you all the session IDs in the current search window.

```
> rbr_run_plotter list-sessions
Sessions in the current time window (-2d)
2024-01-10 13:57:20.903919
2024-01-11 15:03:35.115940
2024-01-11 15:24:43.355697
2024-01-12 11:50:22.618175
```
`list-runs` shows you how many different runs you did during the selected session. The number before the stage name is the ID for that set of attempts.

```
> rbr_run_plotter list-runs "2024-01-10 13:57:20.903919"          
Runs in session 2024-01-10 13:57:20.903919 (-2d)
1 -> Harwood Forest
```

You can check how many attempts you made with the `list-run-attempts` commandlet and see your attempt time and whether you completed the stage.

```
> rbr_run_plotter list-run-attempts "2024-01-10 13:57:20.903919" 1
Attempts in Run 1 (-2d)
1 -> 0:04:33.136102 
2 -> 0:04:21.676847 
3 -> 0:04:07.367272 
4 -> 0:04:12.142860 
5 -> 0:04:07.648289 
6 -> 0:04:02.615259 
```

Now to show a pretty picture with some yaw arrows that compares the slowest attempt to the fastest one. Keep in mind that adding yaw arrows can make the display really slow if there's a lot of attempts overlayed on each other.

```
rbr_run_plotter plot-attempts -3d --attempt 1 --attempt 6 --plot-yaw-arrows "2024-01-10 13:57:20.903919" 1
```
![](samples/sample_plotted_run.png?raw=true)