#!/opt/kwikset/venv/bin/python

"""Tool to watch, log and maybe report to discord
the battery status of a cloud-connected kwikset lock."""

import asyncio
import json
import logging
import time

import aiohttp
import configargparse

from aiokwikset import API


async def main() -> None:
    """Run!"""

    confparse = configargparse.ArgParser(
        default_config_files=["./kwikset.conf", "/etc/kwikset.conf", "~/.kwikset.conf"]
    )
    confparse.add("-u", "--username", required=True)
    confparse.add("-p", "--password", required=True)
    confparse.add("--heartbeaturl", required=False, default=False)
    confparse.add("-d", "--detailstimesecs", required=False, type=int, default=86400 )  # 1 day
    confparse.add("-s", "--sleeptime", required=False, type=int, default=300)  # 5 minutes
    confparse.add("--discordhookurl", required=False, default=False)

    conf = confparse.parse_args()

    # initialize the API
    logging.basicConfig(
        filename="/var/log/kwikset.log",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info(
        "Starting up. User=%s, detailstimesecs=%s, sleeptime=%s",
        conf.username, conf.detailstimesecs, conf.sleeptime
    )

    api = API(conf.username)

    pre_auth = await api.authenticate(conf.password, "phone")

    # MFA verification
    await api.verify_user(pre_auth, input("Code:"))

    # Get user account information:
    # user_info = await api.user.get_info()

    # Get the homes
    homes = await api.user.get_homes()

    # Get the devices for the first home
    devices = await api.device.get_devices(homes[0]["homeid"])

    async with aiohttp.ClientSession() as http:
        details_time = 0
        last_percentage = 100

        while True:
            device_info = await api.device.get_device_info(devices[0]["deviceid"])

            logging.info(
                "%s%% %s",
                device_info['batterypercentage'], device_info['batterystatus']
            )

            if (
                last_percentage != device_info["batterypercentage"]
                or (time.time() > (details_time + conf.detailstimesecs))
            ):
                details_time = time.time()
                logging.info(json.dumps(device_info))
                last_percentage = device_info["batterypercentage"]

                if conf.discordhookurl:
                    discordpayload = {
                        "username": "Kwikset Lock",
                        "content": f"# **Door Status:** _{device_info['doorstatus']}_\n"
                                   f"## **Battery Percent:** _{device_info['batterypercentage']}%_\n"
                                   f"## **Battery Status:** _{device_info['batterystatus']}_\n"
                                   f"### **Last Lock Status Time:** _{time.ctime(device_info['lastLockStatusTime'])}_\n"
                                   f"### **Last Update Status:** _{time.ctime(device_info['lastupdatestatus'])}_\n"
                                   # "```json\n"
                                   # f"{json.dumps(device_info,indent=2)}\n"
                                   # "```\n"
                    }

                    await http.post(conf.discordhookurl, json=discordpayload)

            if conf.heartbeaturl:
                await http.get(conf.heartbeaturl)
            await asyncio.sleep(conf.sleeptime)


asyncio.run(main())
