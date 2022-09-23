
import aws_cdk as core
import aws_cdk.assertions as assertions
import requests
import json
import boto3
# import constants as constants
# from constants import *
import constants as cts


# API Endpoint
# url = "https://0vpm0l0jgk.execute-api.us-west-1.amazonaws.com/prod/url"
# # https://ziv1yma9sh.execute-api.us-west-1.amazonaws.com/prod"
# url_table = "Sprint4MubarizStack-makbuckettotableABA65610-1N2B07Z4RT5MW"
# payload  = {"url":"www.skipq.com"}
# payloadToUpdate = {"url":"www.geeksforgeeks"}





""" Test to check API Endpoint health"""

def test_api_health():
    response = requests.get(cts.url) #params
    print(response, response.status_code)
    statusCode = response.status_code
    assert statusCode == 200
    
    # print(constants.tableNameList)
    
    if statusCode == 200:
        print ("passed " + str(statusCode))

# test_api_health()



#  Test to check API PUT method
def test_api_put_method():
    
    
    r = requests.put(cts.url, data=cts.payload)
    a = r.json()
    b = a['event[body]']
    c = b.split('=')[1]

    if c == cts.payload["url"]:
    #     print("url has been added to the table")
        assert True
        

# #  Test to check API GET method

def test_api_get_method():
    
    # api_test = requests.put(url, params = payload)
    r = requests.get(cts.url)
    a = r.json()
    if a['event[body']:

        assert True
        


# #  Test to check API DELETE method

def test_api_delete_method():
    
    api_test = requests.delete(cts.url, data=cts.payload) #requesting api to delete
    a = api_test.json() #convert string to json fotmat
    r = a['event[body]'] #extracting url from request
    c = r.split('=')[1]
    if c == cts.payload["url"]:
    #     print("url has been added to the table")
        assert True
    

# test_api_delete_method()

# def test_api_patch_method():
#     r = requests.delete(url, data=payload)
#     api_test = requests.patch(url, params = payload)
#   
#         assert True
# test_api_patch_method()
