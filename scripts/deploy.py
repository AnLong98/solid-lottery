from brownie import accounts, Lottery
from deployment_tools import get_contract_address_or_mock, get_user_account
from scripts.deployment_tools import (
    ContractType,
    get_network_gas_lane,
    get_network_sub_id,
)


def deploy_contract():
    deployed_lottery = Lottery.deploy(
        100,  # Entry fee in USD
        get_contract_address_or_mock(
            ContractType.MockV3Aggregator
        ),  # Price feed address
        get_contract_address_or_mock(
            ContractType.MockVRFCoordinatorV2
        ),  # VRF2 Coordinator address
        get_network_gas_lane(),  # gas lane key hash
        get_network_sub_id(),  # VRF subscription id
    )


def main():
    deploy_contract()
