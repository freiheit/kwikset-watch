#!/opt/kwikset/venv/bin/python

import aiodns
import aiohttp
import asyncio
import configargparse
import logging
import time
import json

from aiokwikset import API
from pprint import pprint, pformat


async def main() -> None:
    """Run!"""

    confparse = configargparse.ArgParser(
        default_config_files=["./kwikset.conf", "/etc/kwikset.conf", "~/.kwikset.conf"]
    )
    confparse.add("-u", "--username", required=True)
    confparse.add("-p", "--password", required=True)
    confparse.add("--heartbeaturl", required=False, default=False)
    confparse.add("-d", "--detailstimesecs", required=False, default=7200)
    confparse.add("-s", "--sleeptime", required=False, default=300)
    confparse.add("--discordhookurl", required=False, default=False)

    conf = confparse.parse_args()

    # initialize the API
    logging.basicConfig(
        filename="/var/log/kwikset.log",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    api = API(conf.username)

    pre_auth = await api.authenticate(conf.password, "phone")

    # MFA verification
    await api.verify_user(pre_auth, input("Code:"))

    # Get user account information:
    user_info = await api.user.get_info()

    # Get the homes
    homes = await api.user.get_homes()

    # Get the devices for the first home
    devices = await api.device.get_devices(homes[0]["homeid"])

    async with aiohttp.ClientSession() as http:
        details_time = 0
        last_percentage = 100
        while True:
            device_info = await api.device.get_device_info(devices[0]["deviceid"])
            # pprint(device_info)
            logging.info(
                f"{device_info['batterypercentage']}% {device_info['batterystatus']}"
            )
            if (
                last_percentage != device_info["batterypercentage"]
                or (details_time + conf.detailstimesecs) < time.time()
            ):
                logging.info(json.dumps(device_info))
                last_percentage = device_info["batterypercentage"]
                if conf.discordhookurl:
                    discordpayload = {
                        "username": "Kwikset Lock",
                        "content": f"# Battery Percent: {device_info['batterypercentage']}\n"
                        f"## Battery Status: {device_info['batterystatus']}\n"
                        f"## Last Lock Status Time: {time.ctime(device_info['lastLockStatusTime'])}\n"
                        f"## Last Update Status: {time.ctime(device_info['lastupdatestatus'])}\n"
                        "```json\n"
                        f"{json.dumps(device_info,indent=2)}\n"
                        "```\n",
                    }
                    await http.post(conf.discordhookurl, json=discordpayload)

            if conf.heartbeaturl:
                await http.get(conf.heartbeaturl)
            await asyncio.sleep(conf.sleeptime)


asyncio.run(main())
