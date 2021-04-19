import os
import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#setando os valores com variáveis de ambiente
server   = os.getenv('VCENTER_HOST')
#administrator@vsphere.local
username = os.getenv('VCENTER_USERNAME')
password = os.getenv('VCENTER_PASSWORD')

#variável global
ENDPOINT_SESSION = f'https://{server}/rest/com/vmware/cis/session'

def login_vmware():
    url = ENDPOINT_SESSION
    response = requests.post(url, auth=(username, password), verify=False)
    if response.status_code == 200:
        content = response.json()
        token   = content['value']
        return token

def list_vms(token):
    url = f'https://{server}/rest/vcenter/vm'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        vms     = []
        content = response.json()
        for vm in content['value']:
            temp_dict         = {}
            vm_id             = vm['vm']
            vm_name           = vm['name']
            vm_power_state    = vm['power_state']
            vm_cpu_count      = vm['cpu_count']
            vm_memory_size_mb = vm ['memory_size_MiB']
            #print(f'ID: {vm_id} - Name: {vm_name} - State: {vm_power_state} - CPU: {vm_cpu_count} - Memory: {vm_memory_size_mb}')
            temp_dict['vm_id']             = vm_id
            temp_dict['vm_name']           = vm_name
            temp_dict['vm_power_state']    = vm_power_state
            temp_dict['vm_cpu_count']      = vm_cpu_count
            temp_dict['vm_memory_size_mb'] = vm_memory_size_mb
            vms.append(temp_dict)
        return vms

def poweroff_vm(token, vmid):
    url = f'https://{server}/rest/vcenter/vm/{vmid}/power/stop'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        message = f'VM {vmid} was stopped.'
        return message
    elif response.status_code == 400:
        content = response.json()
        result  = content['value']['messages'][0]['default_message']
        message = f'[{vmid}]: {result}'
        return message

def poweron_vm(token, vmid):
    url = f'https://{server}/rest/vcenter/vm/{vmid}/power/start'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        message = f'VM {vmid} was started.'
        return message
    elif response.status_code == 400:
        content = response.json()
        result  = content['value']['messages'][0]['default_message']
        message = f'[{vmid}]: {result}'
        return message

def update_cpu(token, vmid, cpu):
    url = f'https://{server}/rest/vcenter/vm/{vmid}/hardware/cpu'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    data = {
        "spec": {
            "cores_per_socket": cpu,
            "count": cpu
        }
    }
    response = requests.patch(url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        message = f'VM {vmid} was updated.'
        return message
    elif response.status_code == 400:
        content = response.json()
        result  = content['value']['messages'][0]['default_message']
        message = f'[{vmid}]: {result}'
        return message

def get_datastores(token):
    url = f'https://{server}/rest/vcenter/datastore'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        datastores = []
        content    = response.json()
        for datastore in content['value']:
            datastore_id                            = datastore['datastore']
            datastore_name                          = datastore['name']
            datastore_type                          = datastore['type']
            datastore_free_space                    = datastore['free_space']
            datastore_capacity                      = datastore['capacity']
            datastore_utilization_perc              = (datastore_free_space*100)/datastore_capacity
            print(f'{datastore_name} - {datastore_utilization_perc:.2f}%')
            temp_dict                               = {}
            temp_dict['datastore_id']               = datastore_id
            temp_dict['datastore_name']             = datastore_name
            temp_dict['datastore_type']             = datastore_type
            temp_dict['datastore_free_space']       = datastore_free_space
            temp_dict['datastore_capacity']         = datastore_capacity
            temp_dict['datastore_utilization_perc'] = datastore_utilization_perc
            datastores.append(temp_dict)
        return datastores

def get_cluster_id(token):
    url = f'https://{server}/rest/vcenter/cluster'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        content    = response.json()
        cluster_id = content['value'][0]['cluster']
        return cluster_id

def get_datastore_id(token, datastore_name):
    url = f'https://{server}/rest/vcenter/datastore'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    query_string = {'filter.names.1': datastore_name}
    response = requests.get(url, headers=headers, params=query_string, verify=False)
    if response.status_code == 200:
        content = response.json()
        datastore_id = content['value'][0]['datastore']
        return datastore_id

def get_folder_id(token, folder_name):
    url = f'https://{server}/rest/vcenter/folder'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    query_string = {'filter.names.1': folder_name}
    response = requests.get(url, headers=headers, params=query_string, verify=False)
    if response.status_code == 200:
        content   = response.json()
        folder_id = content['value'][0]['folder']
        return folder_id

#criando vm
def create_vm_default(token, vm_name, cluster_id, datastore_id, folder_id):
    token        = token
    cluster_id   = get_cluster_id(token)
    datastore_id = get_datastore_id(token, datastore_name)
    folder_id    = get_folder_id(token, folder_name) 
    vm_name      = 'test_1'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }

    data = {
        "spec": {
            "name": vm_name,
            "guest_OS": 'RHEL_8_64',
            "placement": {
                "cluster": cluster_id,
                "datastore": datastore_id,
                "folder": folder_id,
            },
        }
    }

    url = f'https://{server}/rest/vcenter/vm'
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 200:
        content = response.json()
        result = content['value']
        message = f'VM {vm_name} was created with id {result}.'
        return message
    elif response.status_code == 400:
        content = response.json()
        result = content['value']['messages'][0]['default_message']
        message = result
        return message

def delete_vm(token, vmid):
    url = f'https://{server}/rest/vcenter/vm/{vmid}'
    headers = {
        'Content-Type': 'application/json',
        'vmware-api-session-id': token
    }
    response = requests.delete(url, headers=headers, verify=False)
    if response.status_code == 200:
        message = f'VM {vmid} was deleted.'
        return message
    elif response.status_code == 404:
        content = response.json()
        message = content['value']['messages'][0]['default_message']
        return message
#vms = list_vms(token)
#for vm in vms:
#    print(vm)