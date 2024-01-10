import influxdb_client

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

MEASUREMENT = "RBR_RUN"
BUCKET = "rbrtelemetry"

SESSION_ID = "2024-01-09 21:30:06.141923"
RUN_ID = 1

def main():
    plot_runs(
        query_from_influx(SESSION_ID, RUN_ID, BUCKET, MEASUREMENT)
    )

def query_from_influx(session_id, run_id, bucket="rbrtelemetry", measurement="RBR_RUN", lookback_window="-1w"):
    query = """from(bucket: "{bucket}")
        |> range(start: {lookback_window})
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> filter(fn: (r) => r["session_id"] == "{session_id}")
        |> filter(fn: (r) => r["stage.run"] == "{run_id}")
        |> filter(fn: (r) => r["_field"] == "car.position_x" or 
                             r["_field"] == "car.position_y" or 
                             r["_field"] == "car.position_z" or
                             r["_field"] == "stage.distance_to_end" or 
                             r["_field"] == "car.speed" or 
                             r["_field"] == "stage.name")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> group(columns: ["stage.run_attempt"])""".format(
            bucket=bucket,
            lookback_window=lookback_window,
            measurement=measurement,
            session_id=session_id,
            run_id=run_id,
        )

    query_api = client.query_api()
    return query_api.query(org=org, query=query)

def plot_runs(results):
    run_vals = defaultdict(list)

    for plot_table in results:
        # positional values
        x_vals = []
        y_vals = []
        z_vals = []

        #time determination
        start_time = None
        end_time = None
        prev_record = None


        for record in plot_table.records:
            # extract start and end times for the stage
            if prev_record and not start_time and float(record['car.speed']) > 0:
                if float(prev_record['stage.distance_to_end']) > record['stage.distance_to_end']:
                    start_time = prev_record['_time']
                #    print("Stage Start Time: {}".format(start_time))
                #else:
                #    print("Ignoring speed wiggle")
            
            if not end_time and int(record['stage.distance_to_end']) <= 0:
                end_time = record['_time']
                #print("Stage End Time: {}".format(end_time))
            
            #print(record['stage.distance_to_end'])
            x_vals.append(record['car.position_x'])
            y_vals.append(record['car.position_y'])
            z_vals.append(record['car.position_z'])

            prev_record = record

        stage_time = end_time - start_time
        label = "Attempt {} ({})".format(record['stage.run_attempt'], stage_time)
        run_vals[label] = (x_vals, y_vals, z_vals, record['stage.name'])

        print("Stage Time: {}".format(stage_time))

    import matplotlib.pyplot as plt
    from matplotlib import colormaps

    plt.style.use('_mpl-gallery')

    # plot
    fig, ax = plt.subplots()

    ax.set_prop_cycle(color=colormaps["tab20"].colors)

    for label, vector_vals in run_vals.items():
        # Add the path
        ax.plot(vector_vals[0], vector_vals[1], linewidth=1.0, label = label)
        # Add begin and end markers
        ax.plot(vector_vals[0][0], vector_vals[1][0], 
                markersize=5, marker="o", markerfacecolor="blue")
        ax.plot(vector_vals[0][-1], vector_vals[1][-1], 
                markersize=5, marker="o", markerfacecolor="red")

    ax.set_aspect('equal', adjustable="box")

    plt.subplots_adjust(top=0.97, bottom=0.03)
    plt.legend()
    plt.title(vector_vals[3])
    plt.show()

if __name__ == "__main__":
    main()