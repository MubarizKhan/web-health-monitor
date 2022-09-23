mport aws_cdk as core
import aws_cdk.assertions as assertions
import requests
import json
import boto3
# import constants as constants
# from constants import *
import constants as cts
# API Endpoint
# url = "https://0vpm0l0jgk.execute-api.us-west-1.amazonaws.com/prod/url"
import aws_cdk as core
import aws_cdk.assertions as assertions
import requests
import json
import boto3
# import constants as constants
# from constants import *
import constants as cts
# API Endpoint
# # url = "https://0vpm0l0jgk.execute-api.us-west-1.amazonaws.com/prod/url"


url_table = "Sprint4MubarizStack-makbuckettotableABA65610-OZZ3E52RK6L2"
payload  = {"url":"www.skipq.com"}
payloadToUpdate = {"url":"www.geeksforgeeks"}


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(cts.url_table)



# """ Test API PUT method action"""

def test_put_action():
    
  api_test = requests.put(cts.url, data=cts.payload["url"]) #requesting api to put 
  # item = table_read(payload["URL_ID"])
  if table:
      response = table.get_item(
                                  Key={       #check if inserted
                                  "url": cts.payload["url"],})
    body = api_test.json()      #convert string to json
    url_ = body['event[body]']  #parse Json to extract url
    if url_ == cts.payload["url"]: #check if url is same
        assert True
    else:
      raise Exception("Table dont exist bruh")
    
    

# test_put_action()

# """ Test API DELETE method action"""

def test_delete_action():
  api_test = requests.delete(cts.url, data=cts.payload)
  response = table.get_item(
                              Key={
                              "url": cts.payload["url"],
                          })
  a = api_test.json() #converts api_test to json object
  r = a['event[body]'] #extracting event body
  c = r.split('=')[1] #parsing to recieve url
  response = table.get_item( Key={"url": cts.payload["url"],}) #search table
  if "Item" not in response:
      assert True
