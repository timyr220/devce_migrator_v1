import requests
import os

# Аутентификация в ThingsBoard
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

# Получение всех устройств
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

# Получение ключа устройства (DEVICE_KEY)
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
        print("Failed to obtain device key:", response.status_code, response.json())
        return None

# Сбор телеметрии
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
        print("Failed to receive telemetry:", response.status_code, response.json())
        return None

# Отправка телеметрии
def send_telemetry(url, device_key, telemetry_data):
    telemetry_url = f"{url}/api/v1/{device_key}/telemetry"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(telemetry_url, json=telemetry_data, headers=headers)
    print(f"Telemetry sending response code status: {response.status_code}")
    print(f"Telemetry sending response text: {response.text}")
    try:
        response_json = response.json()
    except ValueError:
        response_json = None

    if response.status_code == 200:
        print("Telemetry sent successfully")
    else:
        print("Failed to send telemetry:", response.status_code, response_json, response.text)

# Основная программа
tb_pe_url = os.getenv('TB_PE_URL', 'http://localhost:8080')
tb_ce_url = os.getenv('TB_CE_URL', 'http://0.0.0.000:8080')
username = os.getenv('TB_USERNAME', 'tenant@thingsboard.org')
password = os.getenv('TB_PASSWORD', 'tenant')

# Получение токенов аутентификации
pe_token = authenticate(tb_pe_url, username, password)
ce_token = authenticate(tb_ce_url, username, password)

if pe_token and ce_token:
    print(f"PE Token: {pe_token}")
    print(f"CE Token: {ce_token}")

    # Выбор направления переноса данных
    direction = input("Enter the direction of data transfer (1 for PE -> CE, 2 for CE -> PE):")

    if direction == "1":
        source_token = pe_token
        source_url = tb_pe_url
        target_token = ce_token
        target_url = tb_ce_url
    elif direction == "2":
        source_token = ce_token
        source_url = tb_ce_url
        target_token = pe_token
        target_url = tb_pe_url
    else:
        print("Incorrect transfer direction")
        exit(1)

    # Ввод имени устройства
    device_name = input("Enter the device name to search (* for all devices): ")

    if device_name == "*":
        source_devices = get_all_devices(source_token, source_url)
        target_devices = get_all_devices(target_token, target_url)
    else:
        device_name_similarity = device_name[:4]

        source_devices = get_all_devices(source_token, source_url)
        target_devices = get_all_devices(target_token, target_url)

        source_devices = [device for device in source_devices if
                          device_name in device['name'] or device_name_similarity in device['name']]
        target_devices = [device for device in target_devices if
                          device_name in device['name'] or device_name_similarity in device['name']]

    if source_devices and target_devices:
        for source_device in source_devices:
            source_device_id = source_device['id']['id']
            telemetry_data = get_telemetry(source_token, source_url, source_device_id)

            if telemetry_data:
                for key in telemetry_data:
                    telemetry_payload = {
                        "ts": telemetry_data[key][0]["ts"],
                        "values": {
                            key: telemetry_data[key][0]["value"]
                        }
                    }
                    print(f" payload for {source_device['name']}: {telemetry_payload}")

                    for target_device in target_devices:
                        target_device_id = target_device['id']['id']
                        target_device_key = get_device_key(target_token, target_url, target_device_id)
                        if target_device_key:
                            send_telemetry(target_url, target_device_key, telemetry_payload)
                        else:
                            print(f"Failed to obtain a key for the device {target_device_id} in the target ThingsBoard.")
    else:
        print("The device could not be found in one or both ThingsBoard instances.")
else:
    print("Failed to authenticate to ThingsBoard PE or CE.")
