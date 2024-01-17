import configparser
import datetime
import math
import os.path
import pathlib
from collections import defaultdict
from dataclasses import dataclass

import click
import influxdb_client
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import colormaps

from rbr_tools import configure_from_file
from rbr_tools import rbr_tools_configuration as configuration

client = None

DEBUG = False

@dataclass
class Run:
    stage_name: str
    stage_time: datetime.timedelta
    dnf: bool
    x_vals: list
    y_vals: list
    z_vals: list
    yaw_vals: list
    speed_vals: list

    @property
    def max_speed(self) -> float:
        return max(self.speed_vals)


@click.group()
@click.option("--time-window",
    help="lookback window for queries")
@click.option("--measurement",
    help="Influx measurement to search under")
@click.option("--bucket",
    envvar="RBR_TELEMETRY_INFLUX_BUCKET",
    help="InfluxDB bucket to search")
@click.option("--org",
    envvar="RBR_TELEMETRY_INFLUX_ORG",
    help="InfluxDB Org to query")
@click.option("--token",
    envvar="RBR_TELEMETRY_INFLUX_TOKEN",
    help="InfluxDB API token")
@click.option("--url",
    envvar="RBR_TELEMETRY_INFLUX_URL",
    help="InfluxDB URL")
@click.option("--config_path",
    envvar="RBR_TELEMETRY_CONFIG",
    default=os.path.join(pathlib.Path.home(), ".rbr_tools.cfg"),
    type=click.Path(exists=False))
def cli(time_window, measurement, bucket, org, token, url, config_path):
    global client

    if os.path.exists(config_path): # aww, yis, configfile
        configure_from_file(config_path)
        
    # override configuration parameters
    if time_window:
        configuration["lookback_window"] = time_window
    if measurement:
        configuration["measurement"] = measurement
    if bucket:
        configuration["bucket"] = bucket
    if org:
        configuration["org"] = org
    if token:
        configuration["token"] = token
    if url:
        configuration["url"] = url

    client = influxdb_client.InfluxDBClient(
        url=configuration["url"],
        token=configuration["token"],
        org=configuration["org"]
    )


@cli.command()
def list_sessions():
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> keyValues(keyColumns: ["session_id"])
        |> group()
        |> unique(column: "_value")""".format(**configuration)

    q_sessions = run_query(query, configuration["org"])[0]

    click.echo("Sessions in the current time window ({})".format(configuration["lookback_window"]))

    for record in q_sessions.records:
        click.echo(record['_value'])


@cli.command()
@click.argument("session_id")
def list_runs(session_id):
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> keyValues(keyColumns: ["stage.run"])
        |> group()
        |> unique(column: "_value")""".format(session_id=session_id,
                                              **configuration)

    q_runs = run_query(query, configuration["org"])[0]

    click.echo("Runs in session {} ({})".format(session_id, configuration["lookback_window"]))

    for record in q_runs.records:
        click.echo("{} -> {}".format(record['_value'], record["stage.name"]))


@cli.command()
@click.argument("session_id")
@click.argument("run_id")
def list_run_attempts(session_id, run_id):
    run_results = process_run_results(get_attempts(session_id, run_id))
    click.echo("Attempts in Run {} ({})".format(run_id, configuration["lookback_window"]))

    for ct, key in enumerate(run_results, 1):
        click.echo("{} -> {} {}".format(ct, run_results[key][-2],
                                        "(DNF)" if run_results[key][-1] else ""))


@cli.command()
@click.argument("session_id")
@click.argument("run_id")
@click.option("--plot-yaw-arrows",
              is_flag=True, default=False,
              help="show yaw arrows on map (WARNING: Can be slow with more than one attempt)")
@click.option("--attempt",
              type=click.INT, multiple=True,
              help="Show only this attempt. Command can be specified more than once")
def plot_attempts(session_id, run_id, plot_yaw_arrows, attempt):
    display_runs(
        process_run_results(get_attempts(session_id, run_id, attempt)),
        plot_yaw_arrows=plot_yaw_arrows
    )


def run_query(query, org):
    query_api = client.query_api()
    return query_api.query(org=org, query=query)


def log_debug(msg):
    if not DEBUG:
        return
    click.echo(msg)


def get_attempts(session_id, run_id, attempts=None):
    query = ""

    query_base = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> filter(fn: (r) => r["stage.run"] == "{run_id}")""".format(
            session_id=session_id,
            run_id=run_id,
            **configuration
        )

    query += query_base

    if attempts:
        attempt_query = " or ".join(['r["stage.run_attempt"] == "{}"'.format(a) for a in attempts])
        query += "\n" + (" " * 8) + "|> filter(fn: (r) => {})".format(attempt_query)

    selected_values = """
        |> filter(fn: (r) => r["_field"] == "car.position_x" or
                             r["_field"] == "car.position_y" or
                             r["_field"] == "car.position_z" or
                             r["_field"] == "stage.distance_to_end" or
                             r["_field"] == "car.speed" or
                             r["_field"] == "stage.name" or
                             r["_field"] == "car.yaw")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> group(columns: ["stage.run_attempt"])"""

    query += selected_values

    return run_query(query, configuration["org"])


def process_run_results(results):
    runs = dict()

    for plot_table in results:
        # positional values
        x_vals = []
        y_vals = []
        z_vals = []
        speed_vals = []
        yaw_vals = []

        #time determination
        start_time = None
        end_time = None
        prev_record = None
        points = 0

        for record in plot_table.records:
            points += 1
            # extract start and end times for the stage
            if prev_record and not start_time and float(record['car.speed']) > 0:
                if float(prev_record['stage.distance_to_end']) > record['stage.distance_to_end']:
                    start_time = prev_record['_time']
                    log_debug("Stage Start Time: {}".format(start_time))
                else:
                    log_debug("Ignoring speed wiggle @ {}".format(record["_time"]))

            if not end_time and int(record['stage.distance_to_end']) <= 0:
                end_time = record['_time']
                log_debug("Stage End Time: {}".format(end_time))

            if start_time or not(len(x_vals) or len(y_vals) or len(z_vals)):
                x_vals.append(record['car.position_x'])
                y_vals.append(record['car.position_y'])
                z_vals.append(record['car.position_z'])
                speed_vals.append(record['car.speed'])

                car_yaw = float(record["car.yaw"])
                yaw_degrees = 360 - (180 + car_yaw)
                yaw_vals.append((yaw_degrees, float(record["car.speed"])))

            prev_record = record

        dnf = False
        if not end_time: # whoa cowboy, we didn't finish that run did we?
            end_time = record["_time"] # nab the last record in the scope
            dnf = True

        if not start_time:
            start_time = end_time
            dnf = True

        stage_time = end_time - start_time
        label = "Attempt {} ({}){}".format(record['stage.run_attempt'], stage_time,
                                           " DNF" if dnf else "")
        
        runs[label] = Run(stage_name= record['stage.name'],
                          x_vals = x_vals,
                          y_vals = y_vals,
                          z_vals = z_vals,
                          yaw_vals = yaw_vals,
                          speed_vals = speed_vals,
                          stage_time = stage_time,
                          dnf = dnf)
        
        log_debug("Retrieved Stage: {}, Attempt: {}, Data Points: {}, Stage Time: {}, Max Speed: {}".format(
                                                                    record['stage.name'],
                                                                    record['stage.run_attempt'],
                                                                    points, stage_time,
                                                                    runs[label].max_speed))
    return runs


def display_runs(runs, plot_yaw_arrows=False):
    plt.style.use('_mpl-gallery')
    # plot
    fig, ax = plt.subplots(figsize=(10, 10))

    click.echo("Plotting Path")
    # plot the paths
    ax.set_prop_cycle(color=colormaps["tab20"].colors)
    ax.set_aspect('equal', adjustable="box")

    for label, run in runs.items():
        # Add the path
        ax.plot(run.x_vals, run.y_vals, linewidth=1.0, label = label)
        # Add begin and end markers
        ax.plot(run.x_vals[0], run.y_vals[0],
                markersize=5, marker="o", markerfacecolor="blue")
        ax.plot(run.x_vals[-1], run.y_vals[-1],
                markersize=5, marker="o", markerfacecolor="red")

    if plot_yaw_arrows:
        x_head = 1
        y_head = 1

        click.echo("Plotting Yaw Arrows")
        #Add some yaw angle arrows
        for label, run in runs.items():
            counter = 0
            max_speed = run.max_speed
            for x, y, yaw_info in zip(run.x_vals, run.y_vals, run.yaw_vals):
                if counter % configuration["arrow_density"] != 0:
                    counter += 1
                    continue
                else:
                    counter += 1

                yaw_degrees, _ = yaw_info
                yaw_radians = (math.pi * yaw_degrees) / 180

                x_head = x + (math.cos(yaw_radians) * configuration["arrow_scale"])
                y_head = y + (math.sin(yaw_radians) * configuration["arrow_scale"])

                arrow = mpatches.FancyArrowPatch((x, y), (x_head, y_head),
                                                 mutation_scale=5,
                                                 arrowstyle="simple")
                ax.add_patch(arrow)

    plt.subplots_adjust(top=0.97, bottom=0.03, left=0.05, right=0.95)
    plt.legend()
    plt.title(run.stage_name)
    plt.show()


if __name__ == "__main__":
    cli()