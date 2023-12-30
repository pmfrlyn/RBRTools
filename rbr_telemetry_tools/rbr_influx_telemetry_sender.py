import datetime
import asyncio
import async_timeout
import socket

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync

import influxdb_client


from rbr_telemetry_tools import (
    MESSAGE_LENGTH, FORMAT_FIELDS, MAPS_INDEX,
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

current_stage = None
current_total_steps = None
stage_attempt = 1

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
        influx_point.tag("stage.attempt", stage_attempt)

        for tag in tag_fields:
            influx_point.tag(tag, point[tag])
        
        for key, val in point.items():
            if key in tag_fields:
                continue
            influx_point.field(key, val)
    
        await write_api.write(bucket="rbrtelemetry", record=influx_point)

async def rbr_telemetry_client(host, port, data_queue: asyncio.Queue):
    global current_stage
    global current_total_steps
    global paused_stage
    global paused_total_steps
    global stage_attempt

    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    point = None

    sock.settimeout(1)
    try:
        data, _ = sock.recvfrom(664)
        point = process_telemetry_packet(data, unit="C")

        current_stage = point['stage.index']
        current_total_steps = point['general.total_steps']

        # handle the paused state and resume with the correct data updates
        if paused_stage and paused_total_steps:
            if paused_stage == current_stage and paused_total_steps > current_total_steps:
                print("Stage Restart!")
                stage_attempt += 1
            elif paused_stage == current_stage and paused_total_steps <= current_total_steps:
                print("Resuming From Pause")
            elif paused_stage != current_stage:
                print("New Stage!")
                stage_attempt = 1

            paused_stage = paused_total_steps = None

        await data_queue.put(point)
    except socket.timeout:
        if not(paused_stage and paused_total_steps):
            paused_stage = current_stage
            paused_total_steps = current_total_steps
            print("Waiting for telemetry...")
        else:
            print("Paused - SS: {}, Steps: {}".format("{} ({})".format(MAPS_INDEX.get(paused_stage, paused_stage), paused_stage), paused_total_steps))
    finally:
        sock.close()

async def main():
    data_queue = asyncio.Queue()

    loop = asyncio.get_event_loop()
    while True:
        t1 = loop.create_task(
                rbr_telemetry_client(UDP_IP, UDP_PORT, data_queue))
        t2 = loop.create_task(rbr_telemetry_send(data_queue))

        await t1
        await t2
        
    loop.stop()

asyncio.run(main())




