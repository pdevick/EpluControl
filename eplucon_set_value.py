# Author: Patrick Devick
# Goal: changing a value of the heatpump using the Eplucon site by replaying the requests

import aiohttp
import re


@service(supports_response="optional")
async def eplucon_set_value(
    url_base: str = "https://portaal.eplucon.nl",
    username=None,
    password=None,
    command=None,
    value=None,
    module_index=None,
    return_response=True,
):
    """yaml
    name: Eplucon Set Value
    description: Set a value of the Eplucon Heatpump.
    fields:
      url_base:
         description: the url to the eplucon portal
         example: https://portaal.eplucon.nl
                  https://portaal.eplucon.be
         required: false
      username:
         description: The username used to logon the portal
         example: username@domain.com
         required: true
      password:
         description: The password used to logon the portal
         example: password
         required: true
      command:
         description: The command to update a control on the heatpump
         example: indoor_temperature - the temperature to achieve when heating or cooling\n
                   heating_active - enable or disable heating\n
                   stop_heating_above - heating stops when outside temperature is above this value\n
                   heating_curve_correction - adjust the heat curve (quicker/slower heating)\n
                   warm_water_active - enable or disable production of warm water\n
                   boiler_temperature - the max temperature of the warm water in the boiler\n
                   boiler_temperature_delta - the delta determines when production warm water starts again\n
                   heatpump_active - enable or disable heatpump or put it in Emergency or APX state\n
                   heatpump_operation_mode - operation mode like only heating, only cooling, or automatic determined by th-Touch or Heatpump\n
                   cooling_active - enable or disable cooling\n
                   stop_passive_cooling_below - stop cooling when outside temperatue below this value
         required: true
      value:
         description: The value to be set.
         example: indoor_temperature = 21.4 (min 10.0, max 30.0)\n
                  heating_active = 1 (1 is enabled, 0 is disabled)\n
                  stop_heating_above = 19.3 (min 0.0, max 30.0)\n
                  heating_curve_correction = 2 (0 degrees correction) (min = 0 (-4 degrees), max = 4 (+4 degrees))\n
                  warm_water_active = 1 (1 is enabled, 0 is disabled)\n
                  boiler_temperature = 56 (min 10, max 65)\n
                  boiler_temperature_delta = 14.1 (min 5.0, max 65.0)\n
                  heatpump_active = 0 (0 = disabled, 1 = enabled, 2 = Emergency, 3 is APX)\n
                  heatpump_operation_mode = 1 (1 is Cooling, 2 is Heating, 3 is Auto th-TOUCH, 4 is Auto Wp, 5 is Fireplace )\n
                  cooling_active = 0 (0 is disable, 1 is enabled)\n
                  stop_passive_cooling_below = 23.5 (min 0.0, max 35.0)\n
         required: true
      module_index:
         description: The index of the module referring to the heatpump
         example: x1a11b1234bc987f0123a1e1a2ab1d89
         required: true
    """

    log.info("Verifying the input arguments")
    if username is None:
        return return_message("error", "Argument Username is mandatory")
    if password is None:
        return return_message("error", "Argument Password is mandatory")
    if command is None:
        return return_message("error", "Argument Command is mandatory")
    if value is None:
        return return_message("error", "Argument Value is mandatory")
    if module_index is None:
        return return_message("error", "Argument Module_index is mandatory")
    log.info("Verifying the input arguments passed")

    # the possible commands and its metadata
    command_type = {
        "indoor_temperature": {
            "code": "5704",
            "type": "float",
            "min": "10.0",
            "max": "30.0",
        },
        "boiler_temperature": {
            "code": "5700",
            "type": "integer",
            "min": "0",
            "max": "65",
        },
        "boiler_temperature_delta": {
            "code": "5804",
            "type": "float",
            "min": "5.00",
            "max": "65.0",
        },
        "warm_water_active": {
            "code": "5711",
            "type": "boolean",
            "min": "0",
            "max": "1",
        },
        "heatpump_active": {"code": "5715", "type": "enum", "min": "0", "max": "3"},
        "heatpump_operation_mode": {
            "code": "5712",
            "type": "enum",
            "min": "1",
            "max": "5",
        },
        "heating_active": {"code": "5813", "type": "boolean", "min": "0", "max": "1"},
        "stop_heating_above": {
            "code": "5814",
            "type": "float",
            "min": "0.0",
            "max": "30.0",
        },
        "heating_curve_correction": {
            "code": "5886",
            "type": "enum",
            "min": "0",
            "max": "4",
        },
        "cooling_active": {"code": "5817", "type": "boolean", "min": "0", "max": "1"},
        "stop_passive_cooling_below": {
            "code": "5901",
            "type": "float",
            "min": "0.0",
            "max": "35.0",
        },
        "stop_active_cooling_below": {
            "code": "5818",
            "type": "float",
            "min": "0.0",
            "max": "35.0",
        },
    }

    # check if command is known and the value is valid (type, min and maximum if enum then it is only the integer)
    command_item = command_type.get(command)
    if command_item is None:
        return return_message("error", "The command " + str(command) + " is invalid")

    if command_item["type"] == "float":
        if not isinstance(value, (float, int)) or (
            float(value) < float(command_item["min"])
            or float(value) > float(command_item["max"])
        ):
            return return_message(
                "error",
                "The value "
                + str(value)
                + " is invalid for command, it expects a number with 1 decimal "
                + command,
            )

    elif command_item["type"] == "integer":
        if not isinstance(value, int) or (
            int(value) < int(command_item["min"])
            or int(value) > int(command_item["max"])
        ):
            return return_message(
                "error",
                "The value "
                + str(value)
                + " is invalid for command, only whole numbers are expected for the command "
                + command,
            )

    elif command_item["type"] == "enum":
        if not isinstance(value, int) or (
            int(value) < int(command_item["min"])
            or int(value) > int(command_item["max"])
        ):
            return return_message(
                "error",
                "The value " + str(value) + " is invalid for command " + command,
            )

    elif command_item["type"] == "boolean":
        if not isinstance(value, int) or (int(value) < 0 or int(value) > 1):
            return return_message(
                "error",
                "The value "
                + str(value)
                + " is invalid for command, a 0 or 1 is expected "
                + command,
            )

    # setting the urls

    url_authentication = url_base + "/login"
    url_getcontrol_postfix = "?blockType=module&account_module_index=" + module_index
    url_sendcontrol = (
        url_base
        + "/e-control/ajax/send_control_data?account_module_index="
        + module_index
    )
    url_getcontrol = (
        url_base
        + "/e-control/ajax/modal/"
        + command_item["code"]
        + url_getcontrol_postfix
    )

    #
    # Access the portal to log in and then to the additional requests
    #
    async with aiohttp.ClientSession() as session:
        log.info("Accessing the portal: %s", url_authentication)
        async with session.get(url_authentication) as response:
            log.info("Accessing the portal: Status %s", response.status)
            html = response.text()

        #
        # find the input elements of the form to fill in the credentials
        #
        input_elements = re.findall(r"<input[^>]*>", html)
        form_data = {
            re.search(r'name="([^"]*)"', input_tag)
            .group(0)
            .replace("name=", "")
            .replace('"', ""): re.search(r'value="([^"]*)"', input_tag)
            .group(0)
            .replace("value=", "")
            .replace('"', "")
            for input_tag in input_elements
        }
        form_data["username"] = username
        form_data["password"] = password

        #
        # Log in using the given credentials
        #
        log.info("Authenticating on the portal: %s", url_authentication)
        async with session.post(url_authentication, data=form_data) as response:
            log.info("Authenticating on the portal: Status %s", response.status)
            html = response.text()

        # need to check if logon is successfull, as it got 200 and not directed
        if len(re.findall(r"inloggegevens is niet", html)) > 0:
            return return_message("error", "Authenticating on the portal failed")

        # get the details of the form to change the control
        log.info("Accessing the form: %s", url_getcontrol)
        async with session.get(url_getcontrol) as response:
            log.info("Accessing the form: Status %s", response.status)
            html = response.text()
            if response.status != 200:
                return return_message(
                    "error",
                    "Accessing the form failed. Maybe wrong module_index is used",
                )

        input_elements = re.findall(r"<input[^>]*>", html)
        form_data = {
            re.search(r'name=\\"([^"]*)"', input_tag)
            .group(0)
            .replace("name=", "")
            .replace('"', "")
            .replace("\\", ""): re.search(r'value=\\"([^"]*)"', input_tag)
            .group(0)
            .replace("value=", "")
            .replace('"', "")
            .replace("\\", "")
            for input_tag in input_elements
        }

        # based on type of control use the template json
        json = ""
        if command_item["type"] == "float":
            json = '[{"name":"format","value":"2"},{"name":"type","value":"2"},{"name":"menutype","value":"MU"},{"name":"blockType","value":"menu"},{"name":"tile_value","value":"placeholder_value"},{"name":"ido","value":"placeholder_command"}]'
        elif command_item["type"] == "integer":
            json = '[{"name":"format","value":"1"},{"name":"type","value":"1"},{"name":"menutype","value":"MU"},{"name":"blockType","value":"module"},{"name":"tile_value","value":"placeholder_value"},{"name":"ido","value":"placeholder_command"}]'
        elif command_item["type"] == "boolean":
            json = '[{"name":"format","value":"0"},{"name":"type","value":"10"},{"name":"menutype","value":"MU"},{"name":"blockType","value":"menu"},{"name":"tile_value","value":"placeholder_value"},{"name":"ido","value":"placeholder_command"}]'
        elif command_item["type"] == "enum":
            json = '[{"name":"format","value":"0"},{"name":"type","value":"11"},{"name":"menutype","value":"MU"},{"name":"blockType","value":"menu"},{"name":"tile_value","value":"placeholder_value"},{"name":"ido","value":"placeholder_command"}]'

        #
        # set the code and value for the control in the json template string
        #
        json = json.replace("placeholder_command", command_item["code"])
        json = json.replace("placeholder_value", str(value))

        # add the json to the form so it can be submitted
        form_data["data"] = json
        log.info(json)

        #
        # Post the data to change the control
        #
        log.info("Posting the form: %s, value set to %s", url_sendcontrol, str(value))
        async with session.post(url_sendcontrol, data=form_data) as response:
            log.info("Posting the form: Status %s", response.status)
            html = response.text()
            log.info("Reponse to posting the form: %s", html)
        return return_message("sucess", "OK")


#
# helper for return message
#
def return_message(status, description):
    log.error("%s", description)

    return_dict = {"status": "", "description": ""}
    return_dict["status"] = status
    return_dict["description"] = description

    return return_dict


if __name__ == "__main__":
    import asyncio
    import os
    import logging as log
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        eplucon_set_value(
            url_base=os.getenv("url_base"),
            username=os.getenv("username"),
            password=os.getenv("password"),
            command="warm_water_active",
            value=1,
            module_index=os.getenv("module_index"),
        )
    )