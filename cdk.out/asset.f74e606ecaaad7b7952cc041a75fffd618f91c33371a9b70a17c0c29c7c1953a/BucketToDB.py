import boto3
import os
import json
import string
import random
# import s3_res
import sys

s3_client = boto3.client('s3')
s3_client.download_file(os.environ['bucketName'],'s3_res.py', '/tmp/s3_res.py')
# s3_client.download_file(os.environ['bktTotable'],'s3_res.py', '/tmp/s3_res.py')
sys.path.insert(1,'/tmp')
    
import s3_res


def bucket_to_dbHandler(event, context):

    dynamodb = boto3.resource('dynamodb')
    bucktToTableName =  os.environ['bktTotable']
    table = dynamodb.Table(bucktToTableName)
    
    for url in s3_res.URL_TO_MONITOR:
        response = table.put_item(TableName=os.environ['bktTotable'],
           Item={
                'url': str(url)
            }
        )
    
        