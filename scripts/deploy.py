from brownie import accounts, Lottery
from scripts.deployment_tools import (
    ContractType,
    create_local_vrf_subscription,
    get_network_gas_lane,
    get_contract_address_or_mock,
    get_user_account,
)


def deploy_contract():
    pass  # Will implement mainnet and fork later


def deploy_lottery_for_testing(
    entry_fee, aggregator_args, vrf_coordinator_args, deployment_account
):
    chainlink_aggregator = get_contract_address_or_mock(
        ContractType.V3Aggregator, **aggregator_args
    )
    vrf_coordinator = get_contract_address_or_mock(
        ContractType.VRFCoordinatorV2, **vrf_coordinator_args
    )
    sub_id = create_local_vrf_subscription(deployment_account, vrf_coordinator)
    deployed_lottery = Lottery.deploy(
        entry_fee,  # Entry fee in USD
        chainlink_aggregator,  # Price feed address
        vrf_coordinator,  # VRF2 Coordinator address
        get_network_gas_lane(),  # gas lane key hash
        sub_id,  # VRF subscription id
        {"from": deployment_account},
    )
    # Below lines are commented out as consumer subscription validation is not working as expected locally

    vrf_coordinator.addConsumer(
        sub_id, deployed_lottery, {"from": deployment_account}
    ).wait(
        1
    )  # Add contract as consumer to local subscription
    return deployed_lottery, vrf_coordinator, chainlink_aggregator


def main():
    deploy_contract()
