// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract Lottery is Ownable, VRFConsumerBaseV2 {
    //ENUMS
    enum LOTTERY_PHASE {
        ACTIVE,
        INACTIVE
    }
    //

    //External interfaces
    AggregatorV3Interface internal priceFeedUSD;
    VRFCoordinatorV2Interface internal coordinator;
    //

    //Fields
    address payable[] public participants;
    uint256 public entryFeeUSD;
    LOTTERY_PHASE public currentPhase;
    uint256 public randomNumber;
    //TODO: Make not hardcoded later
    address vrfCoordinatorAddress;
    bytes32 gasLaneKeyHash;

    //

    constructor(
        uint256 _entryUSD,
        address _feedNetworkAddress,
        address _vrfCoordinator,
        bytes32 _gasLane
    ) VRFConsumerBaseV2(_vrfCoordinatorAddress) {
        priceFeed = AggregatorV3Interface(feeNetworkAddress);
        coordinator = VRFCoordinatorV2Interface(vrfCoordinator);
        currentPhase = LOTTERY_PHASE.INACTIVE;
        vrfCoordinatorAddress = _vrfCoordinator;
        gasLaneKeyHash = _gasLane;
    }

    //I need a function for users to join the lottery and pay the fee
    function join() public payable {
        require(
            currentPhase == LOTTERY_PHASE.ACTIVE,
            "Cannot join the lottery as it has not started yet."
        );
        require(
            msg.value >= getEntryFeeUSD(),
            "Not enough money to participate"
        ); //make sure he paid enough to participate

        participants.push(payable(msg.sender));
    }

    //For nowI will make this callable, later change to clock decision
    function startLottery() public onlyOwner {
        require(
            currentPhase == LOTTERY_PHASE.INACTIVE,
            "Cannot start lottery as it is already ongoing"
        );
        currentPhase = LOTTERY_PHASE.ACTIVE;
    }

    //Close it, also make a clock later
    function endLottery() public onlyOwner {
        require(
            currentPhase == LOTTERY_PHASE.ACTIVE,
            "Cannot end lottery as it is not active"
        );
    }

    //get USD value of entry fee somehow
    //TODO: Add safemath here to avoid production issues, cause my math is garbage ;P
    function getEntryFeeUSD() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 priceInDecimals = ((entryUSD * (10**18)) / (price * (10**10)));
        return priceInDecimals;
    }
}
