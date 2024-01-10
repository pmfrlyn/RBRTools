import datetime
import asyncio
import async_timeout
import socket

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

import influxdb_client


from rbr_telemetry_tools import (
    MESSAGE_LENGTH, MAPS_INDEX,
    process_telemetry_packet, configure_map_index)

RBR_INSTALL_LOCATION = "D:\\Richard Burns Rally"
RBR_MAPS_INI = RBR_INSTALL_LOCATION + "\\Maps\\tracks.ini"

bucket = "rbrtelemetry"
org = "klaw.cloud"
token = "S4PaTHipGiQudzeyh7hMNQTR4t9-fgrsl0gjWATUn2FKf7cFhMsLJJvAjs0rd3jriIfu2ng5lvPH87Dhcl_izw=="
url = "http://telemetry.klaw.cloud:8086"

driver = "spots"

UDP_IP = "10.0.0.30"
UDP_PORT = 6776

start_time = datetime.datetime.now()
current_stage = None
current_total_steps = None
stage_run = 1
stage_run_attempt = 1

pause_announced = False
paused_stage = None
paused_total_steps = None

session_tag = str(datetime.datetime.now())

configure_map_index(RBR_MAPS_INI)

async def rbr_telemetry_send(data_queue: asyncio.Queue):
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

def read_rbr_telemetry(host, port):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(0.25)

    try:
        data, _ = sock.recvfrom(MESSAGE_LENGTH)
    except socket.timeout:
        data = None
    finally:
        sock.close()
        return data
    

async def rbr_telemetry_client(host, port, data_queue: asyncio.Queue):
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
                print("Stage Restart!")
                new_stage = True
                stage_run_attempt += 1
            elif paused_stage == current_stage and paused_total_steps <= current_total_steps:
                print("Resuming From Pause")
            elif paused_stage != current_stage:
                new_stage = True
                stage_run += 1
                stage_run_attempt = 1

            paused_stage = paused_total_steps = None

        if new_stage:
            print("Starting Stage - SS: {}, Run: {}, Attempt: {}".format("{} ({})".format(
                MAPS_INDEX.get(current_stage, current_stage), current_stage), stage_run, stage_run_attempt))

        await data_queue.put(point)
    else:
        if not(paused_stage and paused_total_steps):
            paused_stage = current_stage
            paused_total_steps = current_total_steps
        else:
            if not pause_announced:
                print("Paused - SS: {}, Steps: {}".format("{} ({})".format(MAPS_INDEX.get(paused_stage, paused_stage), paused_stage), paused_total_steps))
                pause_announced = True


async def main():
    print("RBR Influx Telemetry Sender ({})".format(session_tag))
    data_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    running = loop.create_future()

    try:
        while True:
            await rbr_telemetry_client(UDP_IP, UDP_PORT, data_queue)
            await rbr_telemetry_send(data_queue)
    except KeyboardInterrupt:
        running.set_result(False)

    try:
        await running
    finally:
        loop.stop()


asyncio.run(main())