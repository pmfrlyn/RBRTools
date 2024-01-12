import asyncio
import async_timeout
import datetime
import os.path

import click
import influxdb_client
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

from rbr_tools import configure_from_file
from rbr_tools import rbr_tools_configuration as configuration
from rbr_tools.telemetry import (
    MAPS_INDEX,
    read_rbr_telemetry,
    process_telemetry_packet, 
    configure_map_index)

current_stage = None
current_total_steps = None
stage_run = 1
stage_run_attempt = 1

pause_announced = False
paused_stage = None
paused_total_steps = None

session_tag = str(datetime.datetime.now())

@click.command()
@click.option("--driver",
    help="Driver to tag this telemetry under")
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
@click.option("--host",
    envvar="RBR_TELEMETRY_HOST",
    help="Telemetry host")
@click.option("--port",
    envvar="RBR_TELEMETRY_PORT",
    help="Telemetry port")
@click.option("--config_path",
    envvar="RBR_TELEMETRY_CONFIG",
    default=configuration["config_path"],
    type=click.Path(exists=False),
    help="Configuration file for the rbr_tools package")
@click.option("--maps_ini_path",
    envvar="RBR_TELEMETRY_TRACKS_INI",
    default=configuration["maps_ini_path"],
    type=click.Path(exists=False),
    help="Location of your Tracks.ini file")
def cli(driver, measurement, bucket, org, token, url, host, port, config_path, maps_ini_path):
    global client

    if os.path.exists(config_path): # aww, yis, configfile
        click.echo("Loading Configuration: {}".format(config_path))
        configure_from_file(config_path)

    # override configuration parameters
    if maps_ini_path:
        configuration["maps_ini_path"] = maps_ini_path
    if driver:
        configuration["driver"] = driver
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
    if host:
        configuration["rbr_telemetry_host"] = host
    if port:
        configuration["rbr_telemetry_port"] = port

    if os.path.exists(configuration['maps_ini_path']):
        click.echo("Loading Maps Configuration: {}".format(configuration['maps_ini_path']))
        configure_map_index(maps_ini_path)

    asyncio.run(main())

async def main():
    click.echo("RBR Influx Telemetry Sender ({})".format(session_tag))
    data_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    running = loop.create_future()

    try:
        while True:
            await rbr_telemetry_get(
                configuration['rbr_telemetry_host'],
                int(configuration['rbr_telemetry_port']),
                data_queue)
            await rbr_telemetry_send(data_queue)
    except KeyboardInterrupt:
        running.set_result(False)

    try:
        await running
    finally:
        loop.stop()


async def rbr_telemetry_send(data_queue: asyncio.Queue):
    url = configuration["url"]
    token = configuration["token"]
    org = configuration["org"]
    driver = configuration["driver"]

    try:
        async with async_timeout.timeout(1):
            point = await data_queue.get()
    except asyncio.exceptions.TimeoutError:
        return

    tag_fields = ("stage.index", "car.index", "stage.name")

    del point["general.total_steps"]

    async with InfluxDBClientAsync(url=url, token=token, org=org) as client:
        write_api = client.write_api()
        influx_point = influxdb_client.Point("RBR_RUN")
        influx_point.tag("driver", driver)
        influx_point.tag("session_id", session_tag)
        influx_point.tag("stage.run", stage_run)
        influx_point.tag("stage.run_attempt", stage_run_attempt)

        for tag in tag_fields:
            influx_point.tag(tag, point[tag])
        
        for key, val in point.items():
            if key in tag_fields:
                continue
            influx_point.field(key, val)
    
        await write_api.write(bucket="rbrtelemetry", record=influx_point)


async def rbr_telemetry_get(host, port, data_queue: asyncio.Queue):
    global current_stage
    global current_total_steps
    global paused_stage
    global paused_total_steps
    global stage_run
    global stage_run_attempt
    global pause_announced

    point = None
    new_stage = current_stage is None

    data = await asyncio.get_running_loop().run_in_executor(None, read_rbr_telemetry, host, port)

    if data:
        point = process_telemetry_packet(data, unit="C")

        current_stage = point['stage.index']
        current_total_steps = point['general.total_steps']

        # handle the paused state and resume with the correct data updates
        if paused_stage and paused_total_steps:
            pause_announced = False

            if paused_stage == current_stage and paused_total_steps > current_total_steps:
                click.echo("Stage Restart!")
                new_stage = True
                stage_run_attempt += 1
            elif paused_stage == current_stage and paused_total_steps <= current_total_steps:
                click.echo("Resuming From Pause")
            elif paused_stage != current_stage:
                new_stage = True
                stage_run += 1
                stage_run_attempt = 1

            paused_stage = paused_total_steps = None

        if new_stage:
            click.echo("Starting Stage - SS: {}, Run: {}, Attempt: {}".format("{} ({})".format(
                MAPS_INDEX.get(current_stage, current_stage), current_stage), stage_run, stage_run_attempt))

        await data_queue.put(point)
    else:
        if not(paused_stage and paused_total_steps):
            paused_stage = current_stage
            paused_total_steps = current_total_steps
        else:
            if not pause_announced:
                click.echo("Paused - SS: {}, Steps: {}".format("{} ({})".format(MAPS_INDEX.get(paused_stage, paused_stage), paused_stage), paused_total_steps))
                pause_announced = True

if __name__ == "__main__":
    cli()