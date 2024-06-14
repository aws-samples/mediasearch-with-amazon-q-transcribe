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



def create_q_kendraretriever(qKendraRetrieverName, applicationId,amazonQKendraRetrieverroleArn,amazonQKendraIndexID):
    createKendraRetrieverRequest = {
        "applicationId": applicationId, 
        "displayName": qKendraRetrieverName,
        "roleArn": amazonQKendraRetrieverroleArn,
        "type": "KENDRA_INDEX",
        "configuration": {
            "kendraIndexConfiguration": {
                "indexId": amazonQKendraIndexID
            }
            }
    }
    try:
        resp = qbusiness_client.create_retriever(**createKendraRetrieverRequest)
    except Exception as e:
        print(e)
    return resp

def delete_retriever(qbusinessapplicationId,retrieverId):
    deleteRetrieverRequest = {
        "applicationId": qbusinessapplicationId,
        "retrieverId": retrieverId
    }
    try:
        response = qbusiness_client.delete_retriever(**deleteRetrieverRequest)
    except Exception as e:
        print(e)
    return response

def create_nativeIndex(qbusinessapplicationId,qbusinessNativeIndexName):
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
            print('CheckingIndexID status')
            responseGetIndexStatus = qbusiness_client.get_index(
                applicationId=qbusinessapplicationId,
                indexId=nativeIndexId
            )
    except Exception as e:
        print(e)
    return response

  

def create_nativeretriever(qKendraRetrieverName,qbusinessapplicationId,amazonQKendraRetrieverroleArn,indexId):
    createNativeRetrieverRequest = {
        "applicationId": qbusinessapplicationId, 
        "displayName": qKendraRetrieverName,
        "roleArn": amazonQKendraRetrieverroleArn,
        "type": "NATIVE_INDEX",
        "configuration": {
            "nativeIndexConfiguration": {
                "indexId": indexId
            }
        },
    }
    try:
        resp = qbusiness_client.create_retriever(**createNativeRetrieverRequest)

    except Exception as e:
        print(e)
    return resp


qbusinessapplicationId = os.environ.get('AMAZONQ_APPLICATION_ID')
retrieverType = os.environ.get('AMAZONQ_RETRIEVER_TYPE')
indexId = os.environ.get('AMAZONQ_INDEXID')
amazonQKendraRetrieverroleArn = os.environ.get('AMAZONQ_K_RETR_ROLE_ARN')

def lambda_handler(event, context):
    responseData = {}
    if (('RequestType' in event) and (event['RequestType'] == 'Delete')):
        logger.info("Cfn Delete event - Delete QBusiness Retriever created using boto3 APIs - return Success")
        # Delete QBusiness Application
        delete_retriever(qbusinessapplicationId,event['PhysicalResourceId'])
        return exit_status(event, context, cfnresponse.SUCCESS,{})
    
    qKendraRetrieverName='QKendraRetrieverName-'+''.join(random.choice(string.ascii_lowercase) for i in range(4))
    
    try: 
        if (retrieverType == 'Native'):
            response = create_nativeretriever(qKendraRetrieverName,qbusinessapplicationId,amazonQKendraRetrieverroleArn,indexId)
        else:
            # Retriever type if not Native will store the Kendra Index ID (either created by solution or provided by customer)
            amazonQKendraIndexID=indexId
            response = create_q_kendraretriever(qKendraRetrieverName, qbusinessapplicationId,amazonQKendraRetrieverroleArn,amazonQKendraIndexID)
        event['PhysicalResourceId'] = response['retrieverId']
    except Exception as e:
        print(e)
        return exit_status(event, context, cfnresponse.FAILED,responseData)
 
    return exit_status(event, context, cfnresponse.SUCCESS,responseData)