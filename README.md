# Middleware V1
bluetooth.py is in .gitignore as it is not tested fully yet


# Setup

## Create .env 

For the demo use (unless mac address has changed):
```
HELMET_ID='1'
DEVICE_TAG='helm'
BASE_URI='https://us-central1-smart-helmet-2c330.cloudfunctions.net'
HELMET_MAC_ADDRESS='F7:98:98:AF:AE:A8'
ROUND_TIME='180'
```

optionally you can add to the dotenv, if not it will default to 2000 and 500 respectively
```
IMPACT_THRESHOLD='1000'
GYRO_THRESHOLD='500'
```

## Run tests
To run tests in the [tests](./tests/) you must run them as imports.

## Analytics


## Install dependencies
This project requires the following libraries installed with pip:
`bluepy, blue-st-sdk, requests, dotenv`
Either with sudo or in a venv.

If running either the [performance test](./tests/performance_test.py) or graphing with graph sensor script [analytics](./analytics/graph_sensor.py), also install `matplotlib`.


## Optional: add network to pi
Run `sudo nmtui` and fill in SSID.  Most networks use `WPA2 Personal` for the security, but check just in case.

Run `nmcli connection show` to ensure your network is setup.  


## Optional: change refresh rate of sensors in firmware
https://community.st.com/t5/mems-sensors/info-about-sensortile-capabilities/td-p/204776 