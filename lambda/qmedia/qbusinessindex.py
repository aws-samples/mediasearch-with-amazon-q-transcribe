# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import boto3
import string
import random
import logging
import cfnresponse
from botocore.exceptions import ClientError

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
AMAZONQ_REGION = os.environ.get("AMAZONQ_REGION") or os.environ["AWS_REGION"]
AMAZONQ_ENDPOINT_URL = os.environ.get("AMAZONQ_ENDPOINT_URL") or f'https://qbusiness.{AMAZONQ_REGION}.api.aws'  
qbusinessapplicationId = os.environ.get('AMAZONQ_APPLICATION_ID')
retrieverType = os.environ.get('AMAZONQ_RETRIEVER_TYPE')
responseData = {}

qbusiness_client = boto3.client(
    service_name="qbusiness", 
    region_name=AMAZONQ_REGION,
    endpoint_url=AMAZONQ_ENDPOINT_URL
)

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


def create_qbusiness_nativeIndex(qbusinessapplicationId,qbusinessNativeIndexName):
    
    createIndexRequest = {
        "applicationId": qbusinessapplicationId,
        "capacityConfiguration": {
            'units': 1
        },
        "displayName": qbusinessNativeIndexName
    }
    try:
        
        response = qbusiness_client.create_index(**createIndexRequest)
        nativeIndexId=response['indexId']
        # Check and proceed only after the IndexId is ACTIVE
        responseGetIndexStatus = {
            'status': 'CREATING'
        }
        while responseGetIndexStatus['status'] != 'ACTIVE':
            logger.info('Checking Index creation status')
            responseGetIndexStatus = qbusiness_client.get_index(
                applicationId=qbusinessapplicationId,
                indexId=nativeIndexId
            )
    except Exception as e:
        logger.info(str(e))
    return response


def delete_qbusiness_index(qbusinessapplicationId,indexId):
    try:
        response=qbusiness_client.delete_index(
            applicationId=qbusinessapplicationId,
            indexId=indexId
        )

        responseGetIndexStatus = {
            'status': 'DELETING'
        }
        while responseGetIndexStatus['status'] == 'DELETING':
            logger.info('Checking Index deletion status')
            responseGetIndexStatus = qbusiness_client.get_index(
                applicationId=qbusinessapplicationId,
                indexId=indexId
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("Deletion of Index "+indexId+" successful")
            return cfnresponse.SUCCESS
    except Exception as e:
        logger.info("Exception:"+str(e))
        return cfnresponse.FAILED


def lambda_handler(event, context):
    if (('RequestType' in event) and (event['RequestType'] == 'Delete')):
        logger.info("Cfn Delete event - Delete QBusiness Index created using boto3 APIs - return Success")
        # Delete QBusiness Index
        returnVal=delete_qbusiness_index(qbusinessapplicationId,event['PhysicalResourceId'])
        return exit_status(event, context, returnVal,{})

    try: 
        if (retrieverType == 'Native'):
            amazonQBusinessIndexDisplayname='QBusinessMediasearchIndex-'+''.join(random.choice(string.ascii_lowercase) for i in range(4))
            response = create_qbusiness_nativeIndex(qbusinessapplicationId,amazonQBusinessIndexDisplayname)
            indexId=response['indexId']
            event['PhysicalResourceId'] = indexId
            responseData = {'QBusinessIndexId': indexId, 'QBusinessIndexARN': response['indexArn']}
        else:
            logger.info("Do nothing")
        
    except Exception as e:
        return exit_status(event, context, cfnresponse.FAILED,{})
 
    return exit_status(event, context, cfnresponse.SUCCESS,responseData)
