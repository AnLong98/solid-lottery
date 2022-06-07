from brownie import accounts, Lottery
from scripts.deployment_tools import (
    ContractType,
    get_network_gas_lane,
    get_network_sub_id,
    get_contract_address_or_mock,
    get_user_account,
)


def deploy_contract():
    aggregator_args_dict = {"decimals": 8, "initial_answer": 200000000000}
    vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}

    deployment_account = get_user_account()
    deployed_lottery = Lottery.deploy(
        20,  # Entry fee in USD
        get_contract_address_or_mock(
            ContractType.V3Aggregator, **aggregator_args_dict
        ),  # Price feed address
        get_contract_address_or_mock(
            ContractType.VRFCoordinatorV2, **vrf_coordinator_args_dict
        ),  # VRF2 Coordinator address
        get_network_gas_lane(),  # gas lane key hash
        get_network_sub_id(),  # VRF subscription id
        {"from": deployment_account},
    )


def deploy_lottery_for_testing(aggregator_args, vrf_coordinator_args):
    deployed_lottery = Lottery.deploy(
        20,  # Entry fee in USD
        get_contract_address_or_mock(
            ContractType.V3Aggregator, aggregator_args
        ),  # Price feed address
        get_contract_address_or_mock(
            ContractType.VRFCoordinatorV2, vrf_coordinator_args
        ),  # VRF2 Coordinator address
        get_network_gas_lane(),  # gas lane key hash
        get_network_sub_id(),  # VRF subscription id
    )


def main():
    deploy_contract()
