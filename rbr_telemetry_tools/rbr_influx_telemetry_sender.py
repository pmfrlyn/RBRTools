import influxdb_client
import asyncio
import socket
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync


from rbr_telemetry_tools import MESSAGE_LENGTH, FORMAT_FIELDS, process_telemetry_packet


bucket = "rbrtelemetry"
org = "klaw.cloud"
token = "S4PaTHipGiQudzeyh7hMNQTR4t9-fgrsl0gjWATUn2FKf7cFhMsLJJvAjs0rd3jriIfu2ng5lvPH87Dhcl_izw=="
url = "http://telemetry.klaw.cloud:8086"

driver = "spots"

UDP_IP = "10.0.0.30"
UDP_PORT = 6776

async def rbr_telemetry_send(data_queue: asyncio.Queue):
    data = await data_queue.get()
    point = process_telemetry_packet(data, unit="C")

    tag_fields = ("stage.index", "car.index")
    async with InfluxDBClientAsync(url=url, token=token, org=org) as client:
        write_api = client.write_api()
        influx_point = influxdb_client.Point("RBR_RUN")
        influx_point.tag("driver", driver)

        for tag in tag_fields:
            influx_point.tag(tag, point[tag])
        
        for key, val in point.items():
            if key in tag_fields:
                continue
            influx_point.field(key, val)
    
        await write_api.write(bucket="rbrtelemetry", record=influx_point)

async def rbr_telemetry_client(host, port, data_queue: asyncio.Queue):
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    #sock.settimeout(30)
    
    data, address = sock.recvfrom(664)
    await data_queue.put(data)
    sock.close()

async def main():
    data_queue = asyncio.Queue()
    stopped = asyncio.Event()

    loop = asyncio.get_event_loop()
    while not stopped.is_set():
        try:
            await rbr_telemetry_client(UDP_IP, UDP_PORT, data_queue)
            await rbr_telemetry_send(data_queue)
        except KeyboardInterrupt:
            stopped.set()

    loop.stop()

asyncio.run(main())




