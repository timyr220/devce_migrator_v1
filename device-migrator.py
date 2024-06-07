import requests
import os

# Authentication in ThingsBoard
def authenticate(url, username, password):
    auth_url = f"{url}/api/auth/login"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(auth_url, json=payload)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print("Authentication failed:", response.status_code, response.json())
        return None

# Retrieving all devices
def get_all_devices(token, url):
    devices = []
    page_size = 100
    page = 0
    has_next = True

    while has_next:
        search_url = f"{url}/api/tenant/devices?pageSize={page_size}&page={page}"
        headers = {
            'accept': 'application/json',
            'X-Authorization': f'Bearer {token}'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            devices.extend(data['data'])
            has_next = data['hasNext']
            page += 1
        else:
            print("Failed to get devices:", response.status_code, response.json())
            break

    return devices

# Obtaining the device key (DEVICE_KEY)
def get_device_key(token, url, device_id):
    device_key_url = f"{url}/api/device/{device_id}/credentials"
    headers = {
        'accept': 'application/json',
        'X-Authorization': f'Bearer {token}'
    }
    response = requests.get(device_key_url, headers=headers)
    if response.status_code == 200:
        return response.json()['credentialsId']
    else:
        print("Failed to get device key:", response.status_code, response.json())
        return None

# Collecting telemetry from PE
def get_telemetry(token, url, device_id):
    telemetry_url = f"{url}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    headers = {
        'accept': 'application/json',
        'X-Authorization': f'Bearer {token}'
    }
    response = requests.get(telemetry_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get telemetry:", response.status_code, response.json())
        return None

# Sending telemetry to CE
def send_telemetry(url, device_key, telemetry_data):
    telemetry_url = f"{url}/api/v1/{device_key}/telemetry"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(telemetry_url, json=telemetry_data, headers=headers)
    print(f"Send telemetry response status code: {response.status_code}")
    print(f"Send telemetry response text: {response.text}")
    try:
        response_json = response.json()
    except ValueError:
        response_json = None

    if response.status_code == 200:
        print("Telemetry sent successfully")
    else:
        print("Failed to send telemetry:", response.status_code, response_json, response.text)

# Basic programme
tb_pe_url = os.getenv('TB_PE_URL', 'http://localhost:8080')
tb_ce_url = os.getenv('TB_CE_URL', 'http://10.7.2.159:8080')
username = os.getenv('TB_USERNAME', 'tenant@thingsboard.org')
password = os.getenv('TB_PASSWORD', 'tenant')

# Obtaining authentication tokens
pe_token = authenticate(tb_pe_url, username, password)
ce_token = authenticate(tb_ce_url, username, password)

if pe_token and ce_token:
    print(f"PE Token: {pe_token}")
    print(f"CE Token: {ce_token}")

    # Getting a name
    device_name = input("Enter the name of the device to search for (* for all devices): ")

    if device_name == "*":
        pe_devices = get_all_devices(pe_token, tb_pe_url)
        ce_devices = get_all_devices(ce_token, tb_ce_url)
    else:
        device_name_similarity = device_name[:3]

        pe_devices = get_all_devices(pe_token, tb_pe_url)
        ce_devices = get_all_devices(ce_token, tb_ce_url)

        pe_devices = [device for device in pe_devices if
                      device_name in device['name'] or device_name_similarity in device['name']]
        ce_devices = [device for device in ce_devices if
                      device_name in device['name'] or device_name_similarity in device['name']]

    if pe_devices and ce_devices:
        for pe_device in pe_devices:
            pe_device_id = pe_device['id']['id']
            telemetry_data = get_telemetry(pe_token, tb_pe_url, pe_device_id)

            if telemetry_data:
                for key in telemetry_data:
                    telemetry_payload = {
                        "ts": telemetry_data[key][0]["ts"],
                        "values": {
                            key: telemetry_data[key][0]["value"]
                        }
                    }
                    print(f"Telemetry payload для {device_name}: {telemetry_payload}")

                    for ce_device in ce_devices:
                        ce_device_id = ce_device['id']['id']
                        ce_device_key = get_device_key(ce_token, tb_ce_url, ce_device_id)
                        if ce_device_key:
                            send_telemetry(tb_ce_url, ce_device_key, telemetry_payload)
                        else:
                            print(f"Failed to retrieve the key for the device{ce_device_id} in CE.")
    else:
        print("Could not find the device in one or both of the ThingsBoard instances.")
else:
    print("Failed to authenticate to ThingsBoard PE or CE.")
