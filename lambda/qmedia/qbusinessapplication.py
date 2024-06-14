# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
import string
import random
import logging
import cfnresponse

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
AMAZONQ_REGION = os.environ.get("AMAZONQ_REGION") or os.environ["AWS_REGION"]
AMAZONQ_ENDPOINT_URL = os.environ.get("AMAZONQ_ENDPOINT_URL") or f'https://qbusiness.{AMAZONQ_REGION}.api.aws'  

qbusiness_client = boto3.client(
    service_name="qbusiness", 
    region_name=AMAZONQ_REGION,
    endpoint_url=AMAZONQ_ENDPOINT_URL
)

def create_q_application(amazonQApplicationDisplayname,amazonQApplicationroleArn,amazonQApplicationDescription):
    
    createApplicationRequest = {
        "displayName": amazonQApplicationDisplayname,
        "roleArn": amazonQApplicationroleArn,
        "description": amazonQApplicationDescription
    }
    try:
        response = qbusiness_client.create_application(**createApplicationRequest)
    except Exception as e:
        print(e)
    return response

   
def delete_qbusiness_application(qbusinessapplicationId):
    delete_applicationRequest = {
        "applicationId": qbusinessapplicationId
    }
    try:
        response = qbusiness_client.delete_application(**delete_applicationRequest)
    except Exception as e:
        print(e)
    return response

def exit_status(event, context, status,responseData):
    logger.info(f"exit_status({status})")
    if ('ResourceType' in event):
        if (event['ResourceType'].find('CustomResource') > 0):
            logger.info("cfnresponse:" + status)
            if ('PhysicalResourceId' in event):
                resid=event['PhysicalResourceId']
                cfnresponse.send(event, context, status,responseData, resid)
            else:
               cfnresponse.send(event, context, status, responseData, None)
    return status


def lambda_handler(event, context):
    responseData = {}

    if (('RequestType' in event) and (event['RequestType'] == 'Delete')):
        logger.info("Cfn Delete event - Delete QBusiness Application created using boto3 APIs - return Success")
        # Delete QBusiness Application
        delete_qbusiness_application(event['PhysicalResourceId'])
        return exit_status(event, context, cfnresponse.SUCCESS,responseData)

    if (('RequestType' in event) and (event['RequestType'] == 'Update')):
        logger.info("Cfn Update event - Nothing to do - return Success")
        return exit_status(event, context, cfnresponse.SUCCESS,responseData)

    amazonQApplicationroleArn = os.environ.get('AMAZONQ_APP_ROLE_ARN')
    amazonQApplicationDescription="Amazon QBusiness MediaSearch"
    amazonQApplicationDisplayname='QBusinessMediasearch-'+''.join(random.choice(string.ascii_lowercase) for i in range(4))

    try:
        amazonqcreate_response = create_q_application(amazonQApplicationDisplayname,amazonQApplicationroleArn,amazonQApplicationDescription)

        responseData = {'QApplicationId': amazonqcreate_response['applicationId']}
        event['PhysicalResourceId'] = amazonqcreate_response['applicationId']

    except Exception as e:
        logger.error('ERROR: Could not create QBusiness Application with Kendra retriever ->'+str(e))
        return exit_status(event, context, cfnresponse.FAILED,responseData)

    return exit_status(event, context, cfnresponse.SUCCESS,responseData)