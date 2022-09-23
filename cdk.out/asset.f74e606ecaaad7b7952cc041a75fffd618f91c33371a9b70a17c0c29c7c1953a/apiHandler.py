from urllib import response
import urllib3
import boto3
import json
# import logging
import os

# from customEncoder import CustomEncoder

import sys

s3_client = boto3.client('s3')
s3_client.download_file(os.environ['bucketName'],'s3_res.py', '/tmp/s3_res.py')
# s3_client.download_file(os.environ['bktTotable'],'s3_res.py', '/tmp/s3_res.py')
sys.path.insert(1,'/tmp')
    
import s3_res

getMethod = 'GET' #READ
putMethod = 'PUT' #CREAT
patchMethod = 'PATCH' #UPDATE
deleteMethod = 'DELETE' 

methodList = [getMethod,putMethod,patchMethod,deleteMethod]

#define paths
healthPath = '/health'

urlPath = "/url"

def api_Handler(event, context):
    
    # logger.info(event)
    httpMethod = event["httpMethod"]
    path = event["path"]
    # requestData = event["queryStringParameters"]

    dynamodb = boto3.resource('dynamodb')
    bucktToTableName =  os.environ['bktTotable']
    table = dynamodb.Table(bucktToTableName)
    
    
    if httpMethod == getMethod and path == healthPath:
        # response = buildResponse(200)
        response =  {
        "statusCode": 200,#"rockstar":'httpMethod == getMethod and path == healthPath is working
        "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "status":"GEt + health", "event['body']":event['body']}),
        "isBase64Encoded": False
        }
        
        return response
        '''
            - Job1:  check condition is being executed.{}
            -Job2:  Data from the event is being parsed as required. let's call the data DP
            -DP:    Dp will be used to query the database, will contain Primary key
                - will be passed as an argument to GEturl function
                -geturl will query the DB
        '''
    
    # Parse url primary key value & pass to function to read from DB
    elif httpMethod == getMethod and path == urlPath:
        print('event:', json.dumps(event))
        
        l = []
        # table = dynamodb.Table('my-table')
        # https://dynobase.dev/dynamodb-python-with-boto3/#:~:text=To%20get%20all%20items%20from,the%20results%20in%20a%20loop
        response = table.scan()
        data = response['Items']
        
        # data is a list of dictionaries
        for i in data:
            l.append(i["url"])
    
        response =  {
        "statusCode": 200,
        "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod,"status":"GEt + url", "event[body":l}),
        "isBase64Encoded": False
        }
        
        return response
        


    elif httpMethod == putMethod and path == urlPath:
        # s3_res.URL_TO_MONITOR.append(event['body'])
 
        l = []
        response = table.scan()
        data = response['Items']
        
        # data is a list of dictionaries
        for i in data:
            l.append(i["url"])
            
        if event['body'] not in data:
            response = table.put_item(TableName=os.environ['bktTotable'],
              Item={'url': event['body']})
              
              
            return {
                "statusCode": 200,
                "body": json.dumps({"statusCode": 200, "event[body]":event['body'],
                                    "status":"put + url Inserted",
                                    "list":"Values have been inserted"}),
                "isBase64Encoded": False
                }
        else:
            return {
                "statusCode": 2030,
                "body": json.dumps({"statusCode": 2030, "event[body]":event['body'],
                                    "status":"already exists",
                                    "list":"Values already exists"}),
                "isBase64Encoded": False
                }
    

    elif httpMethod  == patchMethod and path == urlPath:
        
        old_url=event['body'].split(',')[0]
        new_url=event['body'].split(',')[1]
        
        InsertedResponse = table.put_item(TableName=os.environ['bktTotable'],
          Item={'url': new_url})
          
        delete = table.delete_item(Key={
            'url':old_url
            
        })
          
        # event['body'] = ur1 + "YYY " + ur2
        
        return {
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200, "event[body]":event['body'],
                                "status":"PATCH + url Inserted",
                                "list":new_url + " is added & " +old_url + "is deleted"}),
            "isBase64Encoded": False
            }
 

    elif httpMethod == deleteMethod and path == urlPath:
        response = event['body']
        delete = table.delete_item(Key={
            'url':event['body']
            
        })
        return {
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200, "event[body]":response,
                                "status":"delete + url Inserted",
                                "list":"Values have been deleted"}),
            "isBase64Encoded": False
            }
    else:  
        # response = buildResponse(404, 'Not Found')
        response =  {
        "statusCode": 404,
        "body": json.dumps({"statusCode": 404,"httpMethod": httpMethod, "fail":"failure"}),
        "isBase64Encoded": False
        }
    
    # return 'shoulfder'
    # return response
    
def buildResponse(body, statusCode, httpMethod, current):
    response =  {
        "statusCode": statusCode,
        "body": json.dumps({"statusCode": statusCode,"httpMethod": httpMethod, "fail":current}),
        "isBase64Encoded": False
        }
    return response
    
# def getUrls(table):
#     try:
#         response = table.scan()
#         result = response['Items']
        
#         while 'LastEvaluatedKey' in response:
#             response = table.scan(ExclusiveStartKey = response['LastEvaluatedKey'])
#             result.extend(response['Items'])
            
#         body = {
#             'urls' : result
#         }
        
#         # return buildResponse(200, body)
#         return {
#         "statusCode": 200,
#         "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "getUrls": 'is working'}),
#         "isBase64Encoded": False
#         }
        
#     except:
#         logger.exception('[* ] - Exception Occured, Do custom error handling!!!')
'''
def getUrl(urlId,url_table):
    
        # return        response = table.get_item(Key={'year': year, 'title': title})
    
    response = table.get_item(
            Key = {
                "id_": urlId,
                "url":url_
            }
        )
        
    if urlId in response:
            # return buildResponse(200, response['Item'])
            return {
            "statusCode": 200,
            "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "getUrl": "is working"}),
            "isBase64Encoded": False
                }
            
    else:
            # return buildResponse(404, {'Message': 'UrlId: %s not found' % urlId})
            return {
            "statusCode": 404,
            "body": json.dumps({"statusCode": 404,"httpMethod": httpMethod, "getURL":"coudnt work"}),
            "isBase64Encoded": False
            }
    

def insertUrl(requestBody,table):
    try:
        table.put_item(Item=requestBody)
        # body = {
        #     'Operation': 'SAVE',
        #     'Message': 'SUCCESS',
        #     'Item': requestBody
        # }
        
        return {
        "statusCode": 200,
        "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "saveUrl": "is working"}),
        "isBase64Encoded": False
        }
        
    except:
        return {'statusCode':404,
            'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': '*',
          },
            'body':json.dumps(response)}    
        

def modifyUrl(urlId, updateKey, updateValue,table):
    try:
        response = table.update_item(
            Key = {
                "id_": urlId
            },
            UpdateExpression = 'set %s = :value' % updateKey,
            ExpressionAttributeValues = {
                ':value': updateValue
            },
            ReturnValues = 'UPDATED_NEW'
        )
         
        
        return {
        "statusCode": 200,
        "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "modifyUrl": "is working"}),
        "isBase64Encoded": False
        }
    except:
        return {'statusCode':404,
                'headers': {
                  'Access-Control-Allow-Headers': '*',
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Methods': '*',
                  },
            'body':json.dumps(response)}    
       

def deleteUrl(urlId,table):
    try:
        response = table.delete_item(
            Key = {
                "id_": urlId
            },
            ReturnValues = 'ALL_OLD'
            
        )
        
        return {
        "statusCode": 200,
        "body": json.dumps({"statusCode": 200,"httpMethod": httpMethod, "deleteUrl":urlId}),
        "isBase64Encoded": False
        }
    except:
        return {'statusCode':200,
        'headers': {
              'Access-Control-Allow-Headers': '*',
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': '*',
              },
        'body':json.dumps(response)}    
        # logger.exception('Errorrrr Handling required') 

  '''

# """ buid a response """
# def buildResponse(statusCode, body = None):
#     response = {
#         'statusCode': statusCode,
#         'header': {
#             'Content-Type': 'application/json',
#             'Access-Control-Allow-Origin': '*'
#         }
#     }
    
#     if body is not None:
#         response['body'] = json.dumps(body, cls=CE)
#     return response







# --------------------------------
# ...............................................................
    # For API GET method with urls resource --> READ
    # elif httpMethod == readMethod and path == urlsPath:
#         url_id = requestBody['URL_ID']
#         # To read a URl item from table
#         response = geturl(url_id)
    
# # .........................................................
#     try:
#         response = table.get_item(
#             Key={
#                 "URL_ID": url_id,
#             }
#         )
#         # item=response['Item']

#         if "Item" in response:
#             return buildResponse(200, response['Item'])
#         else:
#             return buildResponse(404, {'Message': "URL %s not find " % url_id})

#     except:
#         logger.exception(
#             'Do your custom error handling here. I am logging out.')