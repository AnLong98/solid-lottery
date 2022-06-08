from brownie import accounts, config, network, MockV3Aggregator, VRFCoordinatorV2Mock
import enum

LOCAL_NETWORKS = ["ganache-local", "development"]
FORKED_NETWORKS = []


class ContractType(enum.Enum):
    V3Aggregator = 1
    VRFCoordinatorV2 = 2


contract_to_mock_dict = {
    ContractType.V3Aggregator: MockV3Aggregator,
    ContractType.VRFCoordinatorV2: VRFCoordinatorV2Mock,
}


def get_user_account(account_id=None, local_test_acc_index=None):
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


def deploy_mock(contract_name, **kwargs):
    deployment_account = get_user_account()
    match contract_name:
        case ContractType.V3Aggregator:
            deployed_mock = MockV3Aggregator.deploy(
                kwargs["decimals"],
                kwargs["initial_answer"],
                {"from": deployment_account},
            )
            return deployed_mock
        case ContractType.VRFCoordinatorV2:
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


def get_network_sub_id():
    return config["networks"][network.show_active()]["subscription_id"]
