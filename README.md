<h1 align="center">Hi there, I'm <a href="https://github.com/timyr220" target="_blank">Timur</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>

# Device Migrator

Device Migrator is a Python script designed to migrate telemetry data from a ThingsBoard Professional Edition (PE) instance to a ThingsBoard Community Edition (CE) instance. This script automates the process of collecting telemetry data from devices in PE and sending it to corresponding devices in CE.
Features

Authenticate with both ThingsBoard PE and CE instances.
Retrieve a list of all devices from both instances.
Filter devices by name or partial match.
Collect telemetry data from specified devices in PE.
Send collected telemetry data to corresponding devices in CE.

### Prerequisites

+ Python 3.x
+ requests library (install via pip install requests)
+ ThingsBoard PE and CE instances

#### Environment Variables

Set the following environment variables to configure the script:

    TB_PE_URL: URL of the ThingsBoard PE instance (e.g., http://localhost:8080)
    TB_CE_URL: URL of the ThingsBoard CE instance (e.g., http://0.0.0.000:8080)
    TB_USERNAME: Username for authentication (e.g., tenant@thingsboard.org)
    TB_PASSWORD: Password for authentication (e.g., tenant)

## Usage

##### Clone the repository and navigate to the script directory.

    git clone https://github.com/timyr220/device_migrator_v1.git

###### Install the required Python packages.



    pip install requests

Set the required environment variables. For example:



    export TB_PE_URL="http://localhost:8080"
    export TB_CE_URL="http://0.0.0.000:8080"
    export TB_USERNAME="tenant@thingsboard.org"
    export TB_PASSWORD="tenant"

# Run the script.

#### python device-migrator.py

When prompted, enter the name of the device you want to migrate telemetry for. You can enter:
 A specific device name (e.g., Device123).
A partial device name to match multiple devices (e.g., Device will match Device123, Device456, etc.).
An asterisk (*) to select all devices.

#### Script Workflow

Authentication: The script authenticates with both the PE and CE instances using the provided credentials.
Device Retrieval: It retrieves the list of all devices from both instances.
Device Filtering: Based on user input, it filters devices by exact match, partial match (first three characters), or selects all devices if an asterisk (*) is entered.
Telemetry Collection: For each matching device in PE, it collects telemetry data.
Telemetry Transmission: The collected telemetry data is sent to the corresponding devices in CE.

Example

Here is an example of how the script operates:

Set the environment variables:

```
export TB_PE_URL="http://localhost:8080"
export TB_CE_URL="http://0.0.0.000:8080"
export TB_USERNAME="tenant@thingsboard.org"
export TB_PASSWORD="tenant"
```
### Run the script:

    python device_migrator.py

When prompted, enter a device name or a pattern:



+ Enter the name of the device to search for (* for all devices): Device

 +   This will match all devices whose names contain Device.

  +  The script will then collect telemetry data from the matching devices in PE and send it to the corresponding devices in CE.

### Troubleshooting

Authentication Failed: Ensure that the URLs, username, and password are correct and the ThingsBoard instances are running.
Failed to Get Devices: Check the network connection and ensure the ThingsBoard instances are accessible.
Failed to Send Telemetry: Verify the device keys and network connectivity to the CE instance.

## Contribution

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
