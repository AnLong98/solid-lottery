from multiprocessing.sharedctypes import Value
import time
import unittest
import pytest
from scripts.deploy import deploy_lottery_for_testing
from scripts.deployment_tools import get_user_account
from brownie import Lottery, Wei, accounts, exceptions


class LotteryUnitTests(unittest.TestCase):

    contract_owner_acc = None
    lottery_player_acc_1 = None
    lottery_player_acc_2 = None
    lottery_player_acc_3 = None
    contract = None

    @classmethod
    def setUpClass(cls):
        cls.contract_owner_acc = get_user_account()
        cls.lottery_player_acc_1 = get_user_account(local_test_acc_index=1)
        cls.lottery_player_acc_2 = get_user_account(local_test_acc_index=2)
        cls.lottery_player_acc_3 = get_user_account(local_test_acc_index=3)
        return super().setUpClass()

    def setUp(self):
        # deploy sample contract where deployment arguments are fixed across multiple tests
        initial_price = 200000000000
        entry_fee = 50
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        self.contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

    def test__getEntryFeeETH__mocked_price__assert_returned_value(self):
        # deploy contract specifically because I need to set price
        initial_price = 200000000000
        entry_fee = 30
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

        calculated_eth = contract.getEntryFeeETH()
        assert calculated_eth == Wei("0.015 ether")

    def test__startLottery__owner_starting__assert_started(self):
        transaction = self.contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        assert self.contract.currentPhase() == 0  # Assert started

    def test__startLottery__non_owner_starting__assert_throws_exception(self):
        with pytest.raises(exceptions.VirtualMachineError):
            self.contract.startLottery({"from": self.lottery_player_acc_3})

    def test__startLottery__already_started__assert_throws_exception(self):
        # start it twice
        transaction = self.contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        with pytest.raises(exceptions.VirtualMachineError):
            self.contract.startLottery({"from": self.contract_owner_acc})

    def test__joinLottery__enough_money__assert_joined(self):
        # start lottery
        transaction = self.contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        transaction = self.contract.join(
            {"from": self.lottery_player_acc_1, "value": self.contract.getEntryFeeETH()}
        )
        assert self.contract.getParticipantsNumber() == 1
        assert (self.contract.getParticipants())[0] == self.lottery_player_acc_1

    def test__joinLottery__more_than_enough_money__assert_joined(self):
        # start lottery
        transaction = self.contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        transaction = self.contract.join(
            {
                "from": self.lottery_player_acc_1,
                "value": self.contract.getEntryFeeETH() + 0.5,
            }
        )
        assert self.contract.getParticipantsNumber() == 1
        assert (self.contract.getParticipants())[0] == self.lottery_player_acc_1

    def test__joinLottery__not_enough_money__assert_throws_exception(self):
        # deploy contract specifically because I need to set price
        initial_price = 200000000000
        entry_fee = 100
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

        fee_eth = contract.getEntryFeeETH()
        # start lottery
        transaction = contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        with pytest.raises(exceptions.VirtualMachineError):
            contract.join(
                {
                    "from": self.lottery_player_acc_1,
                    "value": fee_eth - Wei("0.0001  ether"),
                }
            )

    def test__joinLottery__not_started__assert_throws_exception(self):
        with pytest.raises(exceptions.VirtualMachineError):
            self.contract.join(
                {
                    "from": self.lottery_player_acc_1,
                    "value": Wei("1 ether"),
                }
            )

    def test__endLottery__not_owner__assert_throws_exception(self):
        with pytest.raises(exceptions.VirtualMachineError):
            self.contract.endLottery(
                {
                    "from": self.lottery_player_acc_1,
                }
            )

    def test__endLottery__not_started__assert_throws_exception(self):
        # deploy contract specifically because I need it not to be started
        initial_price = 200000000000
        entry_fee = 80
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

        with pytest.raises(exceptions.VirtualMachineError):
            contract.endLottery(
                {
                    "from": self.contract_owner_acc,
                }
            )

    def test__endLottery__active_lottery__assert_ended(self):
        # deploy contract specifically because I need it not to be started
        initial_price = 200000000000
        entry_fee = 80
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

        # start lottery
        transaction = contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        # join
        transaction = contract.join(
            {
                "from": self.lottery_player_acc_1,
                "value": contract.getEntryFeeETH(),
            }
        )

        # end it
        contract.endLottery(
            {
                "from": self.contract_owner_acc,
            }
        )

        assert contract.currentPhase() == 2

    def test__endLottery__active_lottery_one_participant__assert_funds_received(self):
        # deploy contract specifically because I need it not to be started
        initial_price = 200000000000
        entry_fee = 100
        aggregator_args_dict = {"decimals": 8, "initial_answer": initial_price}
        vrf_coordinator_args_dict = {"base_fee": 100000, "gas_price_link": 100000}
        contract = deploy_lottery_for_testing(
            entry_fee,
            aggregator_args_dict,
            vrf_coordinator_args_dict,
            self.contract_owner_acc,
        )

        # start lottery
        transaction = contract.startLottery({"from": self.contract_owner_acc})
        transaction.wait(1)

        balance_before_joining = self.lottery_player_acc_1.balance()
        # join
        transaction = contract.join(
            {
                "from": self.lottery_player_acc_1,
                "value": contract.getEntryFeeETH(),
            }
        )
        balance_after_joining = self.lottery_player_acc_1.balance()
        assert contract.balance() > 0

        # end it
        contract.endLottery(
            {
                "from": self.contract_owner_acc,
            }
        )
        time.sleep(2)
        assert balance_before_joining > balance_after_joining
        assert contract.balance() == 0
        assert self.lottery_player_acc_1.balance() > balance_after_joining
