from scripts.deploy import deploy_lottery_for_testing
from scripts.deployment_tools import get_user_account
from brownie import Lottery


def test__getEntryFeeUSD__mocked_price__assert_returned_value():
    # deploy contract
    initial_price = 200000000000
    entry_fee = 20
    aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
    vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
    contract = deploy_lottery_for_testing(
        entry_fee, aggregator_args_dict, vrf_coordinator_args_dict
    )

    lottery = Lottery[-1]
    entry_fee = lottery.getEntryFeeETH()
    expected_eth = 20 / (
        initial_price / 100000000
    )  # Converting intial price back to normal units
    assert entry_fee == expected_eth
