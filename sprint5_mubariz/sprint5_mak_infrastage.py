from aws_cdk import (
    Stage,
    )
    
from constructs import Construct
import aws_cdk as cdk
from s3_resources import s3_res
from sprint5_mubariz.sprint5_mubariz_stack import Sprint5MubarizStack

'''
    This stage will instantiate my stack, and this stage will be instantiated in my pipeline,
    so we can instantiate this stage multiple times, beta, gamma, prod etc.

'''


class sprint5MakInfrastage(Stage):
    

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.stage = Sprint5MubarizStack(self, "makStack")