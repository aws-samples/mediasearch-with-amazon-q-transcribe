import json
import os
import boto3

CLIENT_ID = os.environ["CLIENT_ID"]


def handler(event, context):
    assertion = id_token = event['headers']['Authorization']
    client = boto3.client("sso-oidc") 
    token_response = client.create_token_with_iam(
        clientId=CLIENT_ID,
        grantType="urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion=assertion,
    )
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type':'application/json'
        },
        'body': json.dumps(token_response)
    }
    return response