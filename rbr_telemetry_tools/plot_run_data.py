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

query_api = client.query_api()

query = """from(bucket: "rbrtelemetry")
  |> range(start: -3h)
  |> filter(fn: (r) => r["_measurement"] == "RBR_RUN")
  |> filter(fn: (r) => r["session_id"] == "2024-01-09 21:30:06.141923")
  |> filter(fn: (r) => r["stage.run"] == "1")
  |> filter(fn: (r) => r["_field"] == "car.position_x" or r["_field"] == "car.position_y" or r["_field"] == "car.position_z")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> group(columns: ["stage.run_attempt"])"""

result = query_api.query(org=org, query=query)


run_vals = defaultdict(list)

for plot_table in result:
    x_vals = []
    y_vals = []
    z_vals = []

    for record in plot_table.records:
        x_vals.append(record['car.position_x'])
        y_vals.append(record['car.position_y'])
        z_vals.append(record['car.position_z'])

    run_vals["attempt {}".format(record['stage.run_attempt'])] = (x_vals, y_vals, z_vals)

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
    ax.plot(vector_vals[0][0], vector_vals[1][0], markersize=5, marker="o", markerfacecolor="blue")
    ax.plot(vector_vals[0][-1], vector_vals[1][-1], markersize=5, marker="o", markerfacecolor="red")


plt.legend()
plt.show()
