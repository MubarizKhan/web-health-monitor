import aws_cdk as core
import aws_cdk.assertions as assertions
# import requests
import json
import boto3
# import constants as constants
import pytest


from sprint5_mubariz.sprint5_mubariz_stack import Sprint5MubarizStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sprint5_mubariz/sprint5_mubariz_stack.py
# def test_sqs_queue_created():
#     app = core.App()
#     stack = Sprint5MubarizStack(app, "sprint5-mubariz")
#     template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

        
''' 

    These are our tests which are going to be exected right before our beta pipeline is deployed'''

@pytest.fixture(scope="module")
def imp_template():
    app = core.App()
    stack = Sprint5MubarizStack(app, "sprint5-mubariz")
    template = assertions.Template.from_stack(stack)
    yield template
    
# https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.assertions/Template.html
def test_s3BucketsCreated(imp_template):
    imp_template.resource_count_is("AWS::S3::Bucket",1)
    

def test_lambdaCreated(imp_template):
    imp_template.resource_count_is("AWS::Lambda::Function", 6)
    
    
def test_snsInvocation(imp_template):
    imp_template.has_resource_properties("AWS::SNS::Subscription",props={"Protocol": "lambda"})