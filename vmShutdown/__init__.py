#!/usr/bin/env python3

from multiprocessing import dummy
from re import subn
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient,SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime
from json import loads
import json
import requests

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

VMclientid = "VMclientid"
VMcsecretid = "VMcsecretid"
VMtenantid = "VMtenantid"

Tagclientid = "Tagclientid"
Tagcsecretid = "Tagcsecretid"
Tagtenantid = "Tagtenantid"

Tagcredential = ClientSecretCredential(tenant_id=Tagtenantid,client_id=Tagclientid,client_secret=Tagcsecretid)
VMcredential = ClientSecretCredential(tenant_id=VMtenantid,client_id=VMclientid,client_secret=VMcsecretid)

TagClient = SubscriptionClient(Tagcredential)
vmList = []

for sub in TagClient.subscriptions.list():
    subId = sub.as_dict().get('subscription_id')
    client = ResourceManagementClient(Tagcredential, subId)
    for items in client.resource_groups.list():
        rgName = items.as_dict().get('name')
        rgTags = items.as_dict().get('tags')
        if rgTags != None:
            if len(rgTags) == 2:
                if rgTags['EnableShutdown'] == 'True':
                    vmList.append(rgName)

print(vmList)
VMconfig = ComputeManagementClient(VMcredential,subId)

def vm_stop_fun():
	for vm in range(len(vmList)):
		print('stopping '+ vmList[vm] )
		async_vm_stop = VMconfig.virtual_machines.begin_deallocate(vmList[vm],vmList[vm])
		async_vm_stop.wait()
		print(async_vm_stop.result)

print('All VMs Stopped')

if current_time >= '16:29:00' and current_time <= '16:31:00':
	vm_stop_fun()
elif current_time >= '18:29:00' and current_time <= '18:31:00':
	vm_stop_fun()
# if current_time >= '01:29:00' or current_time <= '01:31:00':
else:
	vmWebhookUrl = "Teams Webhook Link"
	message ="""{"type": "message","attachments": [{"contentType": "application/vnd.microsoft.card.adaptive","contentUrl": null,"content": {"$schema": "http://adaptivecards.io/schemas/adaptive-card.json","type": "AdaptiveCard","version": "1.4","body": [{"type": "TextBlock","size": "Large","weight": "Bolder","text": "User VM State Monitor"},{"type": "ColumnSet","columns": [{"type": "Column","items": [{"type": "Image","style": "Person","url": "https://azure.microsoft.com/svghandler/automation/?width=600&height=315","size": "Medium"}],"width": "auto"},{"type": "Column","items": [{"type": "TextBlock","weight": "Bolder","text": "VM-Automation","wrap": true,"size": "Medium"}],"width": "stretch"}]},{"type": "TextBlock","text": "","wrap": true},{"type": "FactSet","facts":[]}]}}]}"""
	payloadData = dict(loads(message))

	json_payload = []
	for j in range(len(vmList)):
	# looping inside the list of virtual machines, to grab the state of each machine
		vm_state = VMconfig.virtual_machines.instance_view(resource_group_name=vmList[j], vm_name=vmList[j])
		json_object = {"Vm Name": "", "Vm_state": ""}
		json_object2 = {"title": "VM Name", "value": ""}
		json_object["Vm Name"] = vmList[j]
		json_object2["value"] = vmList[j]
		json_object["Vm_state"] = vm_state.statuses[1].code
		if json_object["Vm_state"] == 'PowerState/running':
			json_payload.append(json_object2)

	if str(len(json_payload)) != '0':
		json_content = "{0} VM's were ON over night, Below are the List of VM's which were Turned ON.".format(len(json_payload))
	else:
		json_content = "No VM's were on over Night"

	payloadData['attachments'][0]['content']["body"][2]['text'] += json_content
	payloadData['attachments'][0]['content']['body'][3]['facts'] += json_payload

	response = requests.post(
		vmWebhookUrl, data=json.dumps(payloadData),
		headers={'Content-Type': 'application/json'}
	)
	vm_stop_fun()
	print(response)