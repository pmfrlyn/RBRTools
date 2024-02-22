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
    read_rbr_telemetry,
    process_telemetry_packet, 
    configure_map_index)

# There are stages that do not return the correct ID when telemetry is sent out
# this is particularly noticeable in the RX Plugin tracks 
# the default return is ID 41 when the system doesn't know about the stage, so we compare
# track len to determine whether or not we are ACTUALLY looking at COTE D ARBROZ
COTE_D_ARBROZ_LEN = 4652
COTE_D_ARBROZ_ID = 41

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
        configure_map_index(configuration['maps_ini_path'])
        
    asyncio.run(main())

async def main():
    click.echo("RBR Influx Telemetry Sender ({})".format(session_tag))

    data_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    running = loop.create_future()
    telemetry_session = RBRTelemetrySession()

    try:
        while True:
            await telemetry_session.get(
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

    tag_fields = ("stage.index", "car.index", "stage.name", "stage.run")  

    del point["general.total_steps"]

    async with InfluxDBClientAsync(url=url, token=token, org=org) as client:
        write_api = client.write_api()
        influx_point = influxdb_client.Point("RBR_RUN")
        influx_point.tag("driver", driver)
        influx_point.tag("session_id", session_tag)

        for tag in tag_fields:
            influx_point.tag(tag, point[tag])
        
        for key, val in point.items():
            if key in tag_fields:
                continue
            influx_point.field(key, val)
    
        await write_api.write(bucket="rbrtelemetry", record=influx_point)

class RBRTelemetrySession(object):
    def __init__(self):
        self.current_stage = None
        self.current_stage_name = None
        self.current_total_steps = None
        self.stage_run = 1
        self.stage_run_attempt = 1

        self.pause_announced = False
        self.paused_stage = None
        self.paused_total_steps = None

        self.apply_stage_collision_fix = False

    async def get(self, host, port, data_queue: asyncio.Queue):
        point = None
        new_stage = self.current_stage is None

        data = await asyncio.get_running_loop().run_in_executor(None, read_rbr_telemetry, host, port)

        if data:
            point = process_telemetry_packet(data, unit="C")

            # stage index fix. remove when there's a proper ID mapping for RX stages plugin :(
            if not self.apply_stage_collision_fix and point["stage.index"] == COTE_D_ARBROZ_ID and int(point["stage.distance_to_end"]) != COTE_D_ARBROZ_LEN:
                print("applying the stage collision fix :(")
                point["stage.name"] = "UNKNOWN-{}".format(int(point["stage.distance_to_end"]))
                point["stage.index"] = int(point["stage.distance_to_end"])
                self.current_stage = point["stage.index"]
                self.current_stage_name = point["stage.name"]
                self.apply_stage_collision_fix = True

            if self.apply_stage_collision_fix is False:
                self.current_stage = point['stage.index']
                self.current_stage_name = point['stage.name']
                
            self.current_total_steps = point['general.total_steps']

            # handle the paused state and resume with the correct data updates
            if self.paused_stage and self.paused_total_steps:
                self.pause_announced = False

                if self.paused_stage == self.current_stage and self.paused_total_steps > self.current_total_steps:
                    click.echo("Stage Restart!")
                    new_stage = True
                    self.stage_run_attempt += 1
                elif self.paused_stage == self.current_stage and self.paused_total_steps <= self.current_total_steps:
                    click.echo("Resuming From Pause")
                elif self.paused_stage != self.current_stage:
                    new_stage = True
                    self.stage_run += 1
                    self.stage_run_attempt = 1
                    self.apply_stage_collision_fix = False

                self.paused_stage = self.paused_total_steps = None
                
            if new_stage:
                click.echo("Starting Stage - SS: {}, Run: {}, Attempt: {}".format("{} ({})".format(
                    self.current_stage_name, self.current_stage), self.stage_run, self.stage_run_attempt))

            # enrich data
            point["stage.run"] = self.stage_run
            point["stage.run_attempt"] = self.stage_run_attempt            
            await data_queue.put(point)
        else:
            if not(self.paused_stage and self.paused_total_steps):
                self.paused_stage = self.current_stage
                self.paused_total_steps = self.current_total_steps
            else:
                if not self.pause_announced:
                    click.echo("Paused - SS: {}, Steps: {}".format("{} ({})".format(
                        self.current_stage_name, self.paused_stage), self.paused_total_steps))
                    self.pause_announced = True


if __name__ == "__main__":
    cli()