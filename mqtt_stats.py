#!/usr/bin/env python3
import asyncio
import json
import logging
import sys

from paho.mqtt.publish import single

from grainfather.grainfather import Grainfather


broker_ip = None


def publish_discovery_info():
    device_topic = {
        "ids": "g30",
        "name": "Grainfather G30",
        "sw": "1.0",
        "mdl": "G30",
        "mf": "Grainfather"
    }

    single(
        'homeassistant/sensor/grainfather/current_temperature/config',
        qos=1, retain=True, hostname=broker_ip,
        payload=json.dumps({
            "dev_cla": "temperature",
            "unit_of_meas": "°C",
            "stat_cla": "measurement",
            "name": "Current Temperature",
            "stat_t": "grainfather/sensor/current_temperature/state",
            "avty_t": "grainfather/status",
            "uniq_id": "grainfather_current_temperature",
            "dev": device_topic
        })
    )
    single(
        'homeassistant/sensor/grainfather/target_temperature/config',
        qos=1, retain=True, hostname=broker_ip,
        payload=json.dumps({
            "dev_cla": "temperature",
            "unit_of_meas": "°C",
            "stat_cla": "measurement",
            "name": "Target Temperature",
            "stat_t": "grainfather/sensor/target_temperature/state",
            "avty_t": "grainfather/status",
            "uniq_id": "grainfather_target_temperature",
            "dev": device_topic
        })
    )
    single(
        'homeassistant/sensor/grainfather/heat_power/config',
        qos=1, retain=True, hostname=broker_ip,
        payload=json.dumps({
            "dev_cla": "power",
            "unit_of_meas": "kW",
            "stat_cla": "measurement",
            "name": "Heat Power",
            "stat_t": "grainfather/sensor/heat_power/state",
            "avty_t": "grainfather/status",
            "uniq_id": "grainfather_heat_power",
            "dev": device_topic
        })
    )


def publish_stats(stats):
    # print(json.dumps(stats.to_dict(), indent=4))
    single('grainfather/status', payload=stats.is_connected, retain=True, hostname=broker_ip)
    single('grainfather/sensor/current_temperature/state', payload=stats.current_temperature, hostname=broker_ip)
    single('grainfather/sensor/target_temperature/state', payload=stats.target_temperature, hostname=broker_ip)
    single('grainfather/sensor/heat_power/state', payload=stats.heat_power, hostname=broker_ip)


async def main():
    publish_discovery_info()

    grain = Grainfather()

    await grain.connect()

    await grain.run(callback=publish_stats)

    while True:
        await asyncio.sleep(5)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    broker_ip = sys.argv[1]
    asyncio.run(main())
