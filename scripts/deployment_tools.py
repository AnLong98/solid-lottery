from brownie import (
    Wei,
    accounts,
    config,
    network,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
)
import enum

LOCAL_NETWORKS = ["ganache-local", "development"]
FORKED_NETWORKS = []
TEST_NETWORKS = ["rinkeby"]


class ContractType(enum.Enum):
    chainlink_aggregator = 1
    vrf_coordinator = 2


contract_to_mock_dict = {
    ContractType.chainlink_aggregator: MockV3Aggregator,
    ContractType.vrf_coordinator: VRFCoordinatorV2Mock,
}


def get_user_account(account_id=None, local_test_acc_index=None):
    if network.show_active() not in LOCAL_NETWORKS:
        return accounts.add(config["networks"][network.show_active()]["from_key"])
    if account_id:
        return accounts.load(account_id)

    if local_test_acc_index:
        return accounts[local_test_acc_index]

    if accounts.__len__() > 0:
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_contract_address_or_mock(contract_name, **kwargs):

    if network.show_active() in LOCAL_NETWORKS:
        deploy_mock(contract_name, **kwargs)
        return contract_to_mock_dict[contract_name][-1]

    if network.show_active() in FORKED_NETWORKS:
        # get contract address from config
        pass
    if network.show_active() in TEST_NETWORKS:
        return config["networks"][network.show_active()][contract_name.name]


def deploy_mock(contract_name, **kwargs):
    deployment_account = get_user_account()
    match contract_name:
        case ContractType.chainlink_aggregator:
            deployed_mock = MockV3Aggregator.deploy(
                kwargs["decimals"],
                kwargs["initial_answer"],
                {"from": deployment_account},
            )
            return deployed_mock
        case ContractType.vrf_coordinator:
            deployed_mock = VRFCoordinatorV2Mock.deploy(
                kwargs["base_fee"],
                kwargs["gas_price_link"],
                {"from": deployment_account},
            )
            return deployed_mock


def get_deployed_contracts_num(contract):
    return len(contract)


def get_network_gas_lane():
    return config["networks"][network.show_active()]["gas_lane"]


def create_local_vrf_subscription(account, vrf_mock):
    if network.show_active() in LOCAL_NETWORKS:
        sub_id = vrf_mock.createSubscription({"from": account}).events[
            "SubscriptionCreated"
        ]["subId"]
        vrf_mock.fundSubscription(sub_id, 100000000, {"from": account})
        return sub_id
    else:
        raise Exception(
            "Cannot create subscription locally when on mainnet or forked network."
        )


def get_network_sub_id():
    if network.show_active() in LOCAL_NETWORKS:
        raise Exception(
            "Cannot get subscription id form local network, it has to be created"
        )
    return config["networks"][network.show_active()]["subscription_id"]
