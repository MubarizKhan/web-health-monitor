import boto3
import os
import json
import string
import random
# import s3_res
import sys

# https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
# 1 datapoints within 1 minute	
# Actions enabled
# This action sends a message to an SNS topic with an endpoint that is pending confirmation. 
# It will not work as expected until the endpoint is confirmed. Look for a subscription confirmation email or review the topic in SNS.
# s3_client = boto3.client('s3')
# cw_obj = cloudWatchPublish()
  # client = boto3.client('cloudwatch')
# s3_client.download_file('mubariz-s3-bucket','s3_res.py', '/tmp/s3_res.py')
# sys.path.insert(1,'/tmp')
    

def db_lambda_handler(event, context):
    
    # import s3_res
    # get alarm table name from environment
    alarmTableName= os.environ["tableName"]
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(alarmTableName)

# parse data from topic subscription to insert it in database 

    table.put_item(
            Item={
                    "Timestamp": event["Records"][0]["Sns"]["Timestamp"],
                    "Subject": event["Records"][0]["Sns"]["Subject"]
                })
    return alarmTableName