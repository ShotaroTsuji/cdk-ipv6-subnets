import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_ipv6_subnets.cdk_ipv6_subnets_stack import CdkIpv6SubnetsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_ipv6_subnets/cdk_ipv6_subnets_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkIpv6SubnetsStack(app, "cdk-ipv6-subnets")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
