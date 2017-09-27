'''
By Oren Root
This is a sample Lambda function that calls VMware Cloud on AWS endpoints to add/remove hosts in a response to an AWS IoT button click.

"SINGLE" and "DOUBLE" clickType payloads trigger add and remove host respectively.

For more documentation, follow the link below.
http://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html
'''

from __future__ import print_function

import boto3
import json
import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
phone_number = '+YOUR PHONE NUMBER'  # change it to your phone number
sddc_id = 'YOUR SDDC ID'#change it to your SDDC ID
org_id = 'YOUR ORG ID' #change it to your ORG ID


def lambda_handler(event, context):
    logger.info('Received event: ' + json.dumps(event))
    '''message = 'Hello from your IoT Button %s. Here is the full event: %s' % (event['serialNumber'], json.dumps(event))'''
    '''sns.publish(PhoneNumber=phone_number, Message=message)'''
    logger.info('SMS has been sent to ' + phone_number)
    access_token = get_access_token()
    logger.info('Access token received:'+access_token)
    orgID = org_id
    sddcID = sddc_id 
    click_type = event['clickType']
    status = ''
    message = 'Click received'
    if click_type == "SINGLE":
        status = add_host(access_token, orgID, sddcID, 1)
        message = 'IoT Button %s was SINGLE clicked. Adding 1 host' % (event['serialNumber'])
    elif click_type == "DOUBLE":
        status = add_host(access_token, orgID, sddcID, 2)
        message = 'IoT Button %s was DOUBLE clicked. Adding 2 hosts' % (event['serialNumber'])
    elif click_type == "LONG":
        status = remove_host(access_token, orgID, sddcID, 1)
        message = 'IoT Button %s was LONG pressed. Removing 1 host' % (event['serialNumber'])
    else:    
        logger.info('unrecognized click type: '+click_type)
        message = 'Hello from your IoT Button %s. Unrecognized click type.' % (event['serialNumber'])
    logger.info('called add_host. Received status: '+str(status))
    sns.publish(PhoneNumber=phone_number, Message=message)

def add_host (access_token, org_id, sddc_id, number_of_host=1):
    body = {'num_hosts': number_of_host}
    headers = {'csp-auth-token': access_token, 'Content-Type': 'application/json'}
    response = requests.post('https://vmc.vmware.com/vmc/api/orgs/'+org_id+'/sddcs/'+sddc_id+'/esxs?action=add', json=body, headers=headers)
    json_response = response.json()
    logger.info('Response JSON'+json.dumps(json_response))
    return response.status_code
    
def remove_host (access_token, org_id, sddc_id, number_of_host=1):
    body = {'num_hosts': number_of_host}
    headers = {'csp-auth-token': access_token, 'Content-Type': 'application/json'}
    response = requests.post('https://vmc.vmware.com/vmc/api/orgs/'+org_id+'/sddcs/'+sddc_id+'/esxs?action=remove', json=body, headers=headers)
    json_response = response.json()
    logger.info('Response JSON'+json.dumps(json_response))
    return response.status_code    
    
def get_access_token ():
    params = {'refresh_token': '''YOUR REFRESH TOKEN GOES HERE'''}
    headers = {'Content-Type': 'application/json'}
    response = requests.post('https://saas.csp.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize', params=params, headers=headers)
    json_response = response.json()
    logger.info('Response JSON'+json.dumps(json_response))
    access_token = json_response['access_token']
    return access_token
