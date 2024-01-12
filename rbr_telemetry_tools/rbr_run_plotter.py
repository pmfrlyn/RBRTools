import configparser
import math
import os.path
import pathlib

import click
import influxdb_client
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.patches as mpatches

from collections import defaultdict

client = None

DEBUG = False

configuration = {
    "org": "example.com",
    "token": "",
    "url": "http://localhost:8086",
    "measurement": "RBR_RUN",
    "bucket": "rbrtelemetry",
    "lookback_window": "-7d",
    "arrow_scale": 1
}

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
    default=os.path.join(pathlib.Path.home(), ".rbr_telemetry.cfg"),
    type=click.Path(exists=False))
def cli(time_window, measurement, bucket, org, token, url, config_path):
    global client

    if os.path.exists(config_path): # aww, yis, configfile
        config = configparser.ConfigParser()
        config.read(config_path)
        for section in ["influx", "search"]:
            for key, val in config[section].items():
                if key in configuration:
                    configuration[key] = val

    # use or override configuration parameters
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
    click.echo("Runs in session {} ({})".format(session_id, configuration["lookback_window"]))

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
def plot_runs(session_id, run_id, plot_yaw_arrows, attempt):
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
    run_vals = defaultdict(list)

    for plot_table in results:
        # positional values
        x_vals = []
        y_vals = []
        z_vals = []
        yaw_vals = []

        #time determination
        start_time = None
        end_time = None
        prev_record = None
        points = 0
        max_speed = 0

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

                car_yaw = float(record["car.yaw"])
                yaw_degrees = 360 - (180 + car_yaw)
                yaw_vals.append((yaw_degrees, float(record["car.speed"])))

                if float(record['car.speed']) > max_speed:
                    max_speed = float(record['car.speed'])

            prev_record = record

        dnf = False
        if not end_time: # whoa cowboy, we didn't finish that run did we?
            end_time = record["_time"] # nab the last record in the scope
            dnf = True

        stage_time = end_time - start_time
        label = "Attempt {} ({}){}".format(record['stage.run_attempt'], stage_time,
                                           " DNF" if dnf else "")
        run_vals[label] = (x_vals, y_vals, z_vals, yaw_vals, record['stage.name'],
                           max_speed, stage_time, dnf)

        log_debug("Retrieved Stage: {}, Attempt: {}, Data Points: {}, Stage Time: {}, Max Speed: {}".format(
                                                                    record['stage.name'],
                                                                    record['stage.run_attempt'],
                                                                    points, stage_time,
                                                                    max_speed))
    return run_vals

def display_runs(run_vals, plot_yaw_arrows=False):
    plt.style.use('_mpl-gallery')
    # plot
    fig, ax = plt.subplots(figsize=(10, 10))

    click.echo("Plotting Path")
    # plot the paths
    ax.set_prop_cycle(color=colormaps["tab20"].colors)
    ax.set_aspect('equal', adjustable="box")

    for label, vector_vals in run_vals.items():
        # Add the path
        ax.plot(vector_vals[0], vector_vals[1], linewidth=1.0, label = label)
        # Add begin and end markers
        ax.plot(vector_vals[0][0], vector_vals[1][0],
                markersize=5, marker="o", markerfacecolor="blue")
        ax.plot(vector_vals[0][-1], vector_vals[1][-1],
                markersize=5, marker="o", markerfacecolor="red")

    if plot_yaw_arrows:
        x_tail = 0
        y_tail = 0
        x_head = 1
        y_head = 1
        dx = x_head - x_tail
        dy = y_head - y_tail

        click.echo("Plotting Yaw Arrows")
        #Add some yaw angle arrows
        for label, vector_vals in run_vals.items():
            counter = 0
            max_speed = vector_vals[5]
            for x, y, yaw_info in zip(vector_vals[0], vector_vals[1], vector_vals[3]):
                if counter % 10 != 0:
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
    plt.title(vector_vals[4])
    plt.show()


if __name__ == "__main__":
    cli()