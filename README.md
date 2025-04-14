# Middleware V1


# Setup

## Create .env 

For the demo use:
```
HELMET_ID='1'
DEVICE_TAG='helm'
BASE_URI='https://us-central1-smart-helmet-2c330.cloudfunctions.net'
HELMET_MAC_ADDRESS='F7:98:98:AF:AE:A8'
ROUND_TIME='180'
```



## Install dependencies
This project requires the following libraries installed with pip:
`bluepy, blue-st-sdk, requests, dotenv`





## Optional: add network to pi
Run `sudo nmtui` and fill in SSID.  Most networks use `WPA2 Personal` for the security, but check just in case.

Run `nmcli connection show` to ensure your network is setup.  


## Optional: change refresh rate of sensors in firmware
https://community.st.com/t5/mems-sensors/info-about-sensortile-capabilities/td-p/204776 