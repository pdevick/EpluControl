# EpluControl (your heatpump)
Control Heatpump via pythonscript (re)using capabilities of the Eplucon website

## Introduction

I am a big fan of using Home Assistant and was quite disappointed about the possibilities to integrate the Ecoforest Heatpump which I own. It is the provider to blame, not Home Assistant.
Of course you could say you should have done your due dilligence before buying it. And I did during the procurement when i asked about the possiblities, it was told that you could control temperature with for example Google. In the end yes there was a possiblity to integrate the seperate room controllers, but sadly not the main controller "Th-Touch" which is actually controlling the heatpump.

## Background
First I started with scraping the eplucon website - using the nice multiscrape integration - to read information and present it in Home Assistant. This enabled that I could ask Google about the current temperature and if the heating was on. For each item I found the html representation on the website and defined a sensor scraping it. Luckily they made an API available which provides the actual information of the heatpump in a more structured way. It was a big improvement and more stable as I experienced in the beginning issues when they overhauled the website and then I could startover again finding out the html representation of the values to read. However there was and is still no possbility to control for example the indoor temperature or the mode of the heatpump using the API. I asked for it but without any usable reaction.

The App and the website as offered by the provider can be used to control and that is it. So not fully integrated within my home automation and always in the need to use another app as well without opportunity to do some automations. It should be possible!!!

I looked around and identified two possible solutions (1) adding an additional card in the pump yourself to read and control it locally using modbus etc. or (2) scrape it from the site. For now I did not want to open the heatpump and add an additional card to prevent any guarantee issues. I just wanted to stay away from any possible discussion about it in case of a mallfunction. 

Sadly the th-touch controller connected to the heatpump does not provide capabilities to connect locally from Home Assistant. Even not for reading while itself is sending all data from the heatpump to the service provider. I sniffed the network for traffic and thought about some interception but without any luck. So in the end I choose to experiment with discovering which requests are being sent from the website to read and update data of the heatpump. I was in the believe that it should be possible to replay this with some creativity and tools which are currently available. I accept for now that it is not local and having a dependency with the cloud. When the service provider is maintaining the heatpump I will aks if he can add the additional card.

The current solution I have is assuming that you have (1) an account on the eplucon website and you're able to control your heatpump from there and (2) you are already able to read data and have sensors within Home Assistant. You need at least to have the indoor temperature and the configured indoor temperature available for the thermostat in Home Assistant. You can use the Ecoforest integration from Koen Hendriks (https://github.com/koenhendriks/ha-eplucon) or use your own implementation of invoking the API as provided by Eplucon (https://portaal.eplucon.nl/docs/api). You can use the multiscrape or rest integration to invoke the API. I am still using my own invocation of the API as the Ecoforest integration was not available at that time and it has currently a sync issue. Also I wanted to be able to pause the integration as the API has a service window which then provides 0 as values for a minute or 15 which makes the diagrams unreadable.

So I am now able to read the data in a nice structured way. The next idea, make an native integration for it, however Koen Hendriks already started this (https://github.com/koenhendriks/ha-eplucon) so no need to work on that.

## Controlling the heatpump
However I still wanted to be able to control the temperature from my Home Assistant.

Why? Just because it can and should be possible without the use of multiple apps/websites and do repetitive things manually. Also I experienced that the heatpump finished heating my house in the morning just before waking up. When woke up the floor was already cooling down. I just wanted to the delay the moment that starts heating during the night and then still runs when waking up. Just because it is possible and the floor is then still nice comfortly warmer.  I also use it for other things like lowering the room temperature when in holiday mode. It turns down production of domestic water and starts again just before returning from holiday. 

Using the developer tools from the browesr, I discovered what is sent/received when using the website to control the heatpump. I created a Python script to reproduce the same steps to control the heatpump. By having it in a script it is possible to use within automations in Home Assistant. It is the first attempt and there is still plenty room for improvement and to get it more robust, however for me currently it does the job for now. Lets hope that they do not change the implementation to frequently. As mentiones before I experienced some changes in the past 18 months when they overhauled the website twice.

Altough the script is written in Python is is pending on the Pyscript Python scripting integration (https://github.com/custom-components/pyscript) to be installed in Home Assistant. In that way you could use the script as an action within an automation and do not have to start bash session. Also it enables some opportunities to write to the log of Home Assisant and provide responses to the automations in Home Assistant. So the script does not run in a bash session on its own.

# What can be controlled currently

+ "indoor_temperature", the indoor temperature to achieve when cooling or heating

+ "heating_active", enable or disable heating
+ "stop_heating_above", stop heating when outside temperature above
+ "heating_curve_correction", adjustment of the heat curve (quicker or slower heating)
 
+ "warm_water_active", enable or disable production of warm water
+ "boiler_temperature", the max temperature of domestic water in the boiler
+ "boiler_temperature_delta", the delta which determines when the production of domestic water starts again

+ "heatpump_mode", in which mode the heatpump is like cooling or heating
+ "heatpump_operation", in which operation mode the heatpump is like off, 

+ "cooling_active": enable or disable cooling
+ "stop_passive_cooling_below": stop passive cooling when outside temperature below

# Get it running
1. Install Pyscript
See https://github.com/custom-components/pyscript. After installation it should be available as an integration.

![image](https://github.com/user-attachments/assets/67ed64f6-82cc-40a9-a910-211a14eefe08)

2. Place the script in the pyscript folder
You can use SSH, Samba integration or just create the file via Studio Code server integration and copy/paste the code into that file.

![image](https://github.com/user-attachments/assets/77a20283-870f-4645-9262-793df895cb6e)

3. Go to Developer Tools in Home Assistant

If all went OK the script is available as an Action within Home Assisstant and can be used accordingly in automations etc.

![image](https://github.com/user-attachments/assets/37ef6b16-1a98-49f3-9d7d-aff8b54f9dc9)

When selecting the action in the Developer Tools it shows which parameters are expected. Sadly I could not find a easy way to add username, password and index as a secret from YAML. So for now they are expected as parameters. Of course you can add them as default in the python script. Or define helpers in Home Assistant and use them in your automations.

To be able to run the script and control your heatpump you need to use the same account which you use to login on the eplucon site and also know the module_index which repesennts the heatpump. 

![image](https://github.com/user-attachments/assets/3a53d9fb-4dde-4471-995b-3c66d8d9ccc9)

5. Determine the module_index of the heatpump
The quickest way is to open the Developer Tools (F12 in Edge) and have a look which requests are sent from the website when the Warmtepomp is selected

Login the Eplucon Site and select Heatpump/Warmtepomp in the menu. Something like below should be shown.

![image](https://github.com/user-attachments/assets/9ab5c8b8-872d-4186-942c-a6e47b348baf)

Open the Developer Tools using F12 and click on the OpenDev button to continue. 
Select the Network Tab which will show the requests sent from this page to the webserver. 

![image](https://github.com/user-attachments/assets/a2ba6fdb-0733-4d5d-a2d3-d6625a8a5265)

Make sure that the networkconsole is opened and active (a red circle in the toplef should be shown) in the Developer Tools to see which requests are sent.

![image](https://github.com/user-attachments/assets/75e82242-47a9-4539-a9f0-d49bb05cbc09)

Just wait for a couple of seconds and some rows will appear in the list. The string after the = is the value to use as module_index

![image](https://github.com/user-attachments/assets/fbb1bb7a-beca-4b86-a1ac-63d86d83aa0e)

7. Now you can go to he developer tools using all the information to actually change a setting of the heatpump
Fill in the loginname, password, and module_index. And lets use the command "indoor_temperature" to change the temperature to the selected value.
Press the perfom Action, when all is OK the button wil flash green and in the Response is stated that everything went OK.

![image](https://github.com/user-attachments/assets/fe51e2a4-5eec-4851-9d1f-e4c8eb8d6ac2)

After a short while you should see the temperature also updated in the Eplucon Website or the App to the selected value.

Congratulations. Now the heatpump can be controlled from Home Assistant and used within automations and dashboards.

9. Create a thermostat (if needed)
I've created a thermostat so i can control it in the same way as I can control the temperature for all my other rooms. Also because when it is defined as a thermostat it can be easier exposed to for example Google Home. I now can ask what is the temperature, but also say to increase or decrease the temperature.

![image](https://github.com/user-attachments/assets/67cc7db6-d6f4-4d32-b8fb-2c7fad17db83)

In Home Assistant you can create a generic thermostat which requires a sensor measuring the temperature and a switch to control the device to turn it on or off. 
The latter we will not use and therefore just create a dummy switch as a helper. The sensor is used to show the current temperature and can be the indoor_temperature from the Ecoforest integration or in my case my own sensor. 

So just create a helper defining an input_boolean, give it a name (dummy_thermostat_switch) and use that one in the thermostat yaml as listed below. You can create your unique_id which enables that some things can be changed from Home Assistant UI.

```
climate:
  - platform: generic_thermostat
    name: Woonkamer
    unique_id: 328e6af41-123a-12b3-a123-b12345bf1b11
    heater: input_boolean.dummy_thermostat_switch
    target_sensor: sensor.indoor_temperature
    min_temp: 18
    max_temp: 30
    target_temp_step: 0.1
    initial_hvac_mode: "heat"
    ac_mode: false
```

If you restart you have a thermostat which you can now use on a dashboard showing the actual, also the temperature can be changed on the thermostat. However nothing will happen at this moment. Well it wil turn on/off the switch, but that is dummy. To enable that the configured temperature is passed to the heatpump an automation is needed listening to state changes of the thermostat. In that automation the action is defined to invoke the python script as an action and sent the temperature as set in the thermostat.

```

alias: Controlling the Heatpump
description: Controlling the heatpump.
triggers:
  - trigger: state
    entity_id:
      - climate.woonkamer
    attribute: temperature
    for:
      hours: 0
      minutes: 0
      seconds: 5
    id: Temeperature set via thermostat in HA
  - trigger: state
    entity_id:
      - sensor.configured_indoor_temperature
    id: Temperature set via Eplucon website or App
conditions: []
actions:
  - if:
      - condition: trigger
        id:
          - Temeperature set via thermostat in HA
    then:
      - action: pyscript.eplucon_set_value
        data:
          username: username@domain.com
          password: password
          command: indoor_temperature
          value: "{{ state_attr('climate.woonkamer','temperature') | float(18.0) }}"
          module_index: x1a11b1234bc987f0123a1e1a2ab1d89
        enabled: true
    alias: Sent command to heatpump
  - if:
      - condition: trigger
        id:
          - Temperature set via Eplucon website or App
    then:
      - action: climate.set_temperature
        metadata: {}
        data:
          temperature: "{{ states('sensor.configured_indoor_temperature')  }}"
        target:
          entity_id: climate.woonkamer
    alias: Update thermostat (change from external)
mode: single
```
## Other usages 
Above I described the road which I took to be able to control the heatpump from Home Assistant and provided an example to control the temperature using the thermostat in Home Assistant dahboards. It does not stop there and I continued with some other automations

+ Having Holiday mode, turning off domestic water heating and lowering room temperatures and a a day before returning from holiday enabling it again
+ Delay starting time during the night to ensure that it is still running early in the morning. Just to increase comfort.
+ Starting heatpump earlier to use overcapcity of solar energy and when nearing the temperature where the heatpump would start otherwise to produce heat
+ Joker protection, when the temperature is set to a very high temperature it lowers it to a maximum. Some friends think they are funny by putting the temperature to 30 degrees.
+ When overcapacity of electricity and the heatpump is allready running then increase temperature a bit for a while in the rooms which are lesser used like like garage, chillroom etc. just for comfort.

# Ideas for improvements
+ Better validation on input and the supported domains
+ Better checking on exceptions and results from the requests to the webserver
+ Having it as a native integration (combined with the reading)
+ Adding the other commands (currently focused on the ones which I need)
+ Cleaner code as i am not a python expert. I did it with some youtube and google.

# Disclaimer
I created this to enable a customer journey using one app/website which is is my Home Assistant. Also it enabled me to make smarter use of the heatpump to create more comfort and/or use the energy more efficient. For me it works for now. 
By sharing this I hope that others can enjoy it as well. It is without warranty and the use of it is your own responsibilty. 

Have fun with it and if you have improvements for the script or ideas how to make smarter use of the heatpump and Home Assisstant, please share it and/or improve te script.
And I appreciate if you leave a star at this repository.
