#!/opt/kwikset/venv/bin/python

import aiodns
import aiohttp
import asyncio
import configargparse
import logging
import time

from aiokwikset import API
from pprint import pprint


async def main() -> None:
    """Run!"""

    confparse = configargparse.ArgParser(
        default_config_files=["./kwikset.conf", "/etc/kwikset.conf", "~/.kwikset.conf"]
    )
    confparse.add("-u", "--username", required=True)
    confparse.add("-p", "--password", required=True)
    confparse.add("--heartbeaturl", required=False, default=False)

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
        while True:
            device_info = await api.device.get_device_info(devices[0]["deviceid"])
            # pprint(device_info)
            logging.info(
                f"{device_info['batterypercentage']}% {device_info['batterystatus']}"
            )
            if conf.heartbeaturl:
                await http.get(
                    "https://heartbeat.uptimerobot.com/m798367254-c8f5713329ac5a83ce29a23a97af65c20a902e6e"
                )
            await asyncio.sleep(300)


asyncio.run(main())
