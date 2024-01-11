import click
import influxdb_client
import matplotlib.pyplot as plt
from matplotlib import colormaps
import matplotlib.patches as mpatches
import math

from collections import defaultdict

bucket = "rbrtelemetry"
org = "klaw.cloud"
token = "S4PaTHipGiQudzeyh7hMNQTR4t9-fgrsl0gjWATUn2FKf7cFhMsLJJvAjs0rd3jriIfu2ng5lvPH87Dhcl_izw=="
url = "http://telemetry.klaw.cloud:8086"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

measurement_ = "RBR_RUN"
bucket = "rbrtelemetry"
lookback_window = "-7d"

DEBUG = False
INFO = True
  

@click.group()
@click.option("--time-window", default="-7d", help="lookback window for queries")
@click.option("--measurement", default=measurement_, help="Influx measurement to search under")
def cli(time_window, measurement):
    global lookback_window
    global measurement_

    measurement_ = measurement
    lookback_window = time_window

@cli.command()
def list_sessions():
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> keyValues(keyColumns: ["session_id"])
        |> group()
        |> unique(column: "_value")""".format(bucket=bucket,
                                              lookback_window=lookback_window)

    q_sessions = run_query(query, org)[0]

    click.echo("Sessions in the current time window ({})".format(lookback_window))

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
        |> unique(column: "_value")""".format(bucket=bucket, 
                                             lookback_window=lookback_window,
                                             measurement=measurement_,
                                             session_id=session_id)

    q_runs = run_query(query, org)[0]

    click.echo("Runs in session {} ({})".format(session_id, lookback_window))

    for record in q_runs.records:
        click.echo("{} -> {}".format(record['_value'], record["stage.name"]))

@cli.command()
@click.argument("session_id")
@click.argument("run_id") 
def list_run_attempts(session_id, run_id):
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> filter(fn: (r) => r["stage.run"] == "{run_id}")
        |> keyValues(keyColumns: ["stage.run_attempt"])
        |> group()
        |> unique(column: "_value")""".format(bucket=bucket, 
                                             lookback_window=lookback_window,
                                             measurement=measurement_,
                                             session_id=session_id,
                                             run_id=run_id)

    q_attempts = run_query(query, org)[0]

    click.echo("Runs in session {} ({})".format(session_id, lookback_window))

    for record in q_attempts.records:
        click.echo(record['_value'])

@cli.command()
@click.argument("session_id")
@click.argument("run_id")
@click.option("--plot-yaw-arrows", 
              is_flag=True, default=False, 
              help="show yaw arrows on map (WARNING: Can be slow with more than one attempt)")
@click.option("--attempt",
              type=click.INT, multiple=True,
              help="Show only this attempt. Command can be specified more than once")
def plot_run(session_id, run_id, plot_yaw_arrows, attempt):
    query = ""

    query_base = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> filter(fn: (r) => r["stage.run"] == "{run_id}")""".format(
            bucket=bucket,
            lookback_window=lookback_window,
            measurement=measurement_,
            session_id=session_id,
            run_id=run_id,
        )
    
    query += query_base

    if attempt:
        attempt_query = " or ".join(['r["stage.run_attempt"] == "{}"'.format(a) for a in attempt])
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

    plot_runs(
        process_run_results(run_query(query, org)),
        plot_yaw_arrows=plot_yaw_arrows
    )

def run_query(query, org):
    query_api = client.query_api()
    return query_api.query(org=org, query=query)

def log_debug(msg):
    if not DEBUG:
        return
    click.echo(msg)

def log_info(msg):
    if not INFO:
        return
    click.echo(msg)

def query_from_influx(session_id, run_id, bucket="rbrtelemetry", measurement="RBR_RUN", lookback_window="-1w"):
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> filter(fn: (r) => r["stage.run"] == "{run_id}")
        |> filter(fn: (r) => r["stage.run_attempt"] == "2")
        |> filter(fn: (r) => r["_field"] == "car.position_x" or
                             r["_field"] == "car.position_y" or
                             r["_field"] == "car.position_z" or
                             r["_field"] == "stage.distance_to_end" or
                             r["_field"] == "car.speed" or
                             r["_field"] == "stage.name" or
                             r["_field"] == "car.yaw")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> group(columns: ["stage.run_attempt"])""".format(
            bucket=bucket,
            lookback_window=lookback_window,
            measurement=measurement,
            session_id=session_id,
            run_id=run_id,
        )

    return run_query(query, org)

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

        stage_time = end_time - start_time
        label = "Attempt {} ({})".format(record['stage.run_attempt'], stage_time)
        run_vals[label] = (x_vals, y_vals, z_vals, yaw_vals, record['stage.name'], max_speed)

        log_info("Retrieved Stage: {}, Attempt: {}, Data Points: {}, Stage Time: {}, Max Speed: {}".format(
                                                                    record['stage.name'],
                                                                    record['stage.run_attempt'],
                                                                    points, stage_time,
                                                                    max_speed))
    return run_vals

def plot_runs(run_vals, plot_yaw_arrows=False):
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

                x_head = x + (math.cos(yaw_radians) * 1)
                y_head = y + (math.sin(yaw_radians) * 1)

                arrow = mpatches.FancyArrowPatch((x, y), (x_head, y_head),
                                                 mutation_scale=5,
                                                 arrowstyle="simple")
                ax.add_patch(arrow)


    plt.subplots_adjust(top=0.97, bottom=0.03)
    plt.legend()
    plt.title(vector_vals[4])
    plt.show()


if __name__ == "__main__":
    cli()