# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import boto3
import uuid
import os
import logging
logger = logging.getLogger()
import cfnresponse
logger.setLevel(logging.INFO)


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

def find_ssoins_index(instance_arn):
    ssoins_index = instance_arn.find("ssoins-")
    # Extract the substring starting from "ssoins-" and get the part after it
    if ssoins_index != -1:
        extracted_string = instance_arn[ssoins_index + len("ssoins-"):]
        print(extracted_string)
    else:
        print("ssoins- not found in the ARN")
    return extracted_string

def find_apl_index(apl_arn):
    apl_index = apl_arn.find("apl-")
    # Extract the substring starting from "ssoins-" and get the part after it
    if apl_index != -1:
        extracted_string = apl_arn[apl_index + len("apl-"):]
        print(extracted_string)
    else:
        print("apl- not found in the ARN")
    return extracted_string


def handler(event, context):
    responseData = {}
    if (('RequestType' in event) and (event['RequestType'] == 'Delete')):
        logger.info("Cfn Delete event - no action - return Success")
        return exit_status(event, context, cfnresponse.SUCCESS,responseData)
    if (('RequestType' in event) and (event['RequestType'] == 'Update')):
        logger.info("Cfn Update event - Nothing to do - return Success")
        return exit_status(event, context, cfnresponse.SUCCESS,responseData)

    # Create an AWS SSO admin client
    sso_admin_client = boto3.client('sso-admin')
    # Define the parameters
    instance_arn = os.environ['IDC_INSTANCE_ARN']
    #"arn:aws:sso:::instance/ssoins-7223ab890c573fa4"
    application_provider_arn = "arn:aws:sso::aws:applicationProvider/custom"
    idc_app_name = os.environ['IDC_APP_NAME']

    ssoins_index=find_ssoins_index(instance_arn)

    try: 
        # Call the create_application method
        response = sso_admin_client.create_application(
            InstanceArn=instance_arn,
            ApplicationProviderArn=application_provider_arn,
            Name=idc_app_name,
            PortalOptions={
                "Visibility":"DISABLED"
            }
        )
        
        # Print the response
        applicationArn=response['ApplicationArn']
        apl_index=find_apl_index(applicationArn)
        assignment_required = True

        # Call the put_application_assignment_configuration method
        response = sso_admin_client.put_application_assignment_configuration(
            ApplicationArn=applicationArn,
            AssignmentRequired=assignment_required
        )

        # Define the parameters
        idc_trustedissuer_name = os.environ['IDC_TRUSTEDISSUER_NAME']
        issuer_url = os.environ['IDC_ISSUER_URL']
        #'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_JVTSf96MX'
        aud = os.environ['IDC_AUD']
        #'4pg60bli08ef2u4q9sg6j72is2'
        
        # Call the create_trusted_issuer method

        response = sso_admin_client.create_trusted_token_issuer(
        ClientToken=str(uuid.uuid4()),
        InstanceArn=instance_arn,
        Name=idc_trustedissuer_name,
        TrustedTokenIssuerConfiguration={
            'OidcJwtConfiguration': {
                'ClaimAttributePath': 'email',
                'IdentityStoreAttributePath': 'emails.value',
                'IssuerUrl': issuer_url,
                'JwksRetrievalOption': 'OPEN_ID_DISCOVERY'
            }
        },
        TrustedTokenIssuerType='OIDC_JWT'
    )
        
        trustedTokenIssuerArn = response['TrustedTokenIssuerArn']


        response = sso_admin_client.put_application_grant(
        ApplicationArn=applicationArn,
        Grant={
            'JwtBearer': {
                'AuthorizedTokenIssuers': [
                    {
                        'AuthorizedAudiences': [
                            aud,
                        ],
                        'TrustedTokenIssuerArn': trustedTokenIssuerArn
                    },
                ]
            }

        },
        GrantType='urn:ietf:params:oauth:grant-type:jwt-bearer'
        )
        
        
        scopes = ['qbusiness:conversations:access','qbusiness:conversations:read_write','qbusiness:messages:access','qbusiness:messages:read_write','qbusiness:qapps:access']

        for scope in scopes:
            response = sso_admin_client.put_application_access_scope(
                ApplicationArn=applicationArn,
                Scope=scope
            )
        
        authentication_method_type = 'IAM'
        authentication_method = {
            'Iam': {
                'ActorPolicy':  {
            'Version': '2012-10-17',
            'Statement': [
                {
                'Effect': 'Allow',
                'Principal': {
                    'Service': 'lambda.amazonaws.com'
                },
                'Action': [
                    'sso-oauth:CreateTokenWithIAM'
                ],
                'Resource': [
                    '*'
                ]
                }
            ]
            }}}
        response=sso_admin_client.put_application_authentication_method(
                ApplicationArn=applicationArn,
                AuthenticationMethodType=authentication_method_type,
                AuthenticationMethod=authentication_method
            )
        
        responseData = {'ApplicationArn': applicationArn, 'ApplicationConsoleURL':f'https://console.aws.amazon.com/singlesignon/applications/home?#/instances/{ssoins_index}/ins-{apl_index}'}
        event['PhysicalResourceId'] = applicationArn

        lambda_response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type':'application/json'
        },
        'ApplicationArn': applicationArn
        }
        logger.info(lambda_response)

    except Exception as e:
        logger.error(e)
        return exit_status(event, context, cfnresponse.FAILED,responseData)
    
    return exit_status(event, context, cfnresponse.SUCCESS,responseData)




