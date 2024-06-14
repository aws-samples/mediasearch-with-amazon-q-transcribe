# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import boto3
import os
from botocore.exceptions import ClientError

def handler(event, context):
    print(event)
    # Get the bucket name and object key from the event
    body = json.loads(event["body"])
    bucket_name = body["Bucket"]
    object_key = body["Key"]
    expiration = 3600  # Default expiration time is 1 hour

    # Validate inputs
    if not bucket_name or not object_key:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type':'application/json'
            },
            'body': json.dumps({'error': 'bucket_name and object_key are required'})
        }

    # Create S3 client
    s3_client = boto3.client('s3')

    try:
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
    except ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type':'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type':'application/json'
        },
        'body': json.dumps({'presigned_url': presigned_url})
    }
