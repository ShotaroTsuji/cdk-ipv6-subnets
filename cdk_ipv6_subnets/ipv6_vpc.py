from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Fn,
    RemovalPolicy,
)
from aws_cdk.aws_ec2 import (
    Vpc,
    CfnVPC,
    CfnVPCCidrBlock,
    CfnVPCGatewayAttachment,
    CfnSubnet,
    CfnInternetGateway,
    CfnRoute,
    CfnRouteTable,
    CfnSubnetRouteTableAssociation,
    CfnSecurityGroup,
    SecurityGroup,
)


class Ipv6Vpc(Construct):
    @property
    def vpc(self):
        return self._vpc

    @property
    def sg_default(self):
        return self._sg_default

    @property
    def sg_allow_http(self):
        return self._sg_allow_http

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        cfn_vpc = CfnVPC(self, "Ipv6Vpc", cidr_block="10.0.0.0/24")

        cidr_block = CfnVPCCidrBlock(
            self,
            "Ipv6CidrBlock",
            vpc_id=cfn_vpc.attr_vpc_id,
            amazon_provided_ipv6_cidr_block=True,
        )
        cidr_block.apply_removal_policy(RemovalPolicy.DESTROY)

        public_subnet = CfnSubnet(
            self,
            "PublicSubnet",
            vpc_id=cfn_vpc.attr_vpc_id,
            cidr_block="10.0.0.0/26",
            availability_zone="ap-northeast-1a",
            assign_ipv6_address_on_creation=True,
            ipv6_cidr_block=Fn.select(
                0,
                # CfnのFn::cidrと異なり、最後の引数がなぜかstr
                Fn.cidr(Fn.select(0, cfn_vpc.attr_ipv6_cidr_blocks), 16, "64"),
            ),
        )

        igw = CfnInternetGateway(self, "Igw")
        CfnVPCGatewayAttachment(
            self,
            "VpcPublicIgwAttach",
            vpc_id=cfn_vpc.attr_vpc_id,
            internet_gateway_id=igw.attr_internet_gateway_id,
        )

        public_rtb = CfnRouteTable(
            self,
            "RtbWithDefaultRoutes",
            vpc_id=cfn_vpc.attr_vpc_id,
        )
        CfnRoute(
            self,
            "DefaultRouteIpv4",
            route_table_id=public_rtb.attr_route_table_id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.attr_internet_gateway_id,
        )
        CfnRoute(
            self,
            "DefaultRouteIpv6",
            route_table_id=public_rtb.attr_route_table_id,
            destination_ipv6_cidr_block="::/0",
            gateway_id=igw.attr_internet_gateway_id,
        )
        CfnSubnetRouteTableAssociation(
            self,
            "PublicSubnetRtb",
            subnet_id=public_subnet.attr_subnet_id,
            route_table_id=public_rtb.attr_route_table_id,
        )

        CfnSecurityGroup(
            self,
            "AllowSshAccess",
            group_description="Allow access to SSH via IPv6",
            vpc_id=cfn_vpc.attr_vpc_id,
            security_group_egress=[
                CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ipv6="::/0",
                ),
            ],
            security_group_ingress=[
                CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ipv6="::/0",
                    from_port=22,
                    to_port=22,
                ),
            ],
        )
        sg_allow_http = CfnSecurityGroup(
            self,
            "AllowHttpAccess",
            group_description="Allow access to HTTP via IPv6",
            vpc_id=cfn_vpc.attr_vpc_id,
            security_group_egress=[
                CfnSecurityGroup.EgressProperty(
                    ip_protocol="-1",
                    cidr_ipv6="::/0",
                ),
            ],
            security_group_ingress=[
                CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ipv6="::/0",
                    from_port=80,
                    to_port=80,
                ),
            ],
        )

        self._vpc = Vpc.from_vpc_attributes(
            self,
            "VPC",
            vpc_id=cfn_vpc.attr_vpc_id,
            availability_zones=[public_subnet.attr_availability_zone],
            public_subnet_ids=[public_subnet.attr_subnet_id],
            public_subnet_route_table_ids=[public_rtb.attr_route_table_id],
        )

        self._sg_default = SecurityGroup.from_security_group_id(
            self,
            "SgDefault",
            security_group_id=cfn_vpc.attr_default_security_group,
            allow_all_ipv6_outbound=True,
        )

        self._sg_allow_http = SecurityGroup.from_security_group_id(
            self,
            "SgAllowHTTP",
            security_group_id=sg_allow_http.attr_group_id,
            allow_all_ipv6_outbound=True,
        )

        for index in range(0, len(cfn_vpc.attr_ipv6_cidr_blocks)):
            CfnOutput(
                self,
                f"VpcCidrBlock{index}",
                value=Fn.select(index, cfn_vpc.attr_ipv6_cidr_blocks),
            )

        for index in range(0, len(public_subnet.attr_ipv6_cidr_blocks)):
            CfnOutput(
                self,
                f"PublicSubnetCidrBlock{index}",
                value=Fn.select(index, public_subnet.attr_ipv6_cidr_blocks),
            )
