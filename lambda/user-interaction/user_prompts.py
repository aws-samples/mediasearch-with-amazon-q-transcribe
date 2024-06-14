# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import os
import uuid
import boto3
import datetime 
import jwt
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AMAZONQ_APP_ID = os.environ["AMAZONQ_APP_ID"]
AMAZONQ_REGION = os.environ["AMAZONQ_REGION"]
IAM_ROLE_ARN = os.environ["IAM_ROLE_ARN"] 

# Define a custom function to serialize datetime objects 
def serialize_datetime(obj): 
    if isinstance(obj, datetime.datetime): 
        return obj.isoformat() 
    raise TypeError("Type not serializable") 


def get_amazonq_response(qbusiness_client,prompt, context, attachments):
    logger.info(f"get_amazonq_response: prompt={prompt}, app_id={AMAZONQ_APP_ID}, context={context}")
    input = {
        "applicationId": AMAZONQ_APP_ID,
        "userMessage": prompt,
    }

    if context:
        if context["conversationId"]:
            input["conversationId"] = context["conversationId"]
        if context["parentMessageId"]:
            input["parentMessageId"] = context["parentMessageId"]
    else:
        input["clientToken"] = str(uuid.uuid4())
    
    if attachments:
        input["attachments"] = attachments

    logger.info(f"Amazon Q Input: {json.dumps(input)}")
    try:
        resp = qbusiness_client.chat_sync(**input)
    except Exception as e:
        logger.info(f"Amazon Q Exception: {str(e)}")
        resp = {
            "systemMessage": "Amazon Q Error: " + str(e)
        }
    logger.info(f"Amazon Q Response: {json.dumps(resp, default=serialize_datetime)}")
    return resp

def get_conversations(qbusiness_client,conversation_id, nextToken):
    input = {
        "applicationId": AMAZONQ_APP_ID,
        "conversationId": conversation_id
    }

    if nextToken:
        input["nextToken"] = nextToken

    logger.info(f"Amazon Q Input: {json.dumps(input)}")
    try:
        resp = qbusiness_client.list_messages(**input)
    except Exception as e:
        logger.info(f"Amazon Q Exception: {str(e)}")
        resp = {
            "systemMessage": "Amazon Q Error: " + str(e)
        }
    logger.info(f"Amazon Q Response: {json.dumps(resp, default=serialize_datetime)}")
    return resp

def get_qbusiness_client(idToken):
    identity_center_token_decoded = jwt.decode(idToken, options={"verify_signature": False})
    # Assume the role using the decoded identity context
    sts_client = boto3.client('sts')
    assume_role_response = sts_client.assume_role(
        RoleArn=IAM_ROLE_ARN,
        RoleSessionName='identity-bearer-for-ms-user-conversation',
        ProvidedContexts=[
            {
                'ProviderArn': 'arn:aws:iam::aws:contextProvider/IdentityCenter',
                'ContextAssertion': identity_center_token_decoded['sts:identity_context']
            }
        ]
    )

    # Create an S3 Control client using the assumed role credentials
    identity_bearer_session_credentials = {
        'aws_access_key_id': assume_role_response['Credentials']['AccessKeyId'],
        'aws_secret_access_key': assume_role_response['Credentials']['SecretAccessKey'],
        'aws_session_token': assume_role_response['Credentials']['SessionToken']
    }
    qbusiness_client = boto3.client('qbusiness', **identity_bearer_session_credentials)
    return qbusiness_client

def handler(event, context):
    request_body = json.loads(event["body"])
    logger.info(request_body)
    qbusiness_client=get_qbusiness_client(request_body['idToken'])
   
    if request_body['action'] == 'history':
        amazonq_response = get_conversations(qbusiness_client, request_body['conversationId'], request_body['nextToken'])
        logger.info(amazonq_response)

    if request_body['action'] == 'query':
        amazonq_response = get_amazonq_response(qbusiness_client,request_body['query'],request_body['context'] , '')
        logger.info(amazonq_response)
    
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type':'application/json'
        },
        'body': json.dumps(amazonq_response, default=serialize_datetime)
    }
    return response