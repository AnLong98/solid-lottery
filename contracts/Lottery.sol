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
        INACTIVE,
        CHOOSING_WINNER
    }
    //

    //Events
    event RequestedRandomWord(
        uint64 indexed _subscriptionId,
        uint256 _requestID
    );
    event ReceivedRandomWord(uint256 _requestID, uint256 _receivedWord);
    event FundsTransfered(address payable indexed _winnerAddress);
    event RandomWordRetrievalFailiure(string error);
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
    uint64 private vrfSubID;
    uint256 vrfReqID;
    //TODO: Make not hardcoded later
    address vrfCoordinatorAddress;
    bytes32 gasLaneKeyHash;

    //

    constructor(
        uint256 _entryUSD,
        address _feedNetworkAddress,
        address _vrfCoordinator,
        bytes32 _gasLane,
        uint64 _subscriptionID
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        priceFeedUSD = AggregatorV3Interface(_feedNetworkAddress);
        coordinator = VRFCoordinatorV2Interface(_vrfCoordinator);
        currentPhase = LOTTERY_PHASE.INACTIVE;
        vrfCoordinatorAddress = _vrfCoordinator;
        gasLaneKeyHash = _gasLane;
        vrfSubID = _subscriptionID;
        entryFeeUSD = _entryUSD;
    }

    // Assumes the subscription is funded sufficiently.
    function requestRandomWords() private {
        try
            // Will revert if subscription is not set and funded.
            coordinator.requestRandomWords(
                gasLaneKeyHash,
                vrfSubID,
                1, //Request confirmations hardcoded
                100000, //Gas limit hardcoded xD
                1 // Words to request
            )
        returns (uint256 reqId) {
            vrfReqID = reqId;
            emit RequestedRandomWord(vrfSubID, vrfReqID);
        } catch Error(string memory _err) {
            emit RandomWordRetrievalFailiure(_err);
        }
    }

    //Callback function to process chosen random number from VRF
    function fulfillRandomWords(
        uint256 requestID, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        emit ReceivedRandomWord(requestID, randomWords[0]);
        randomNumber = randomWords[0];
        uint256 winnerIndex = randomNumber % participants.length;
        transferFundsToWinner(winnerIndex);
    }

    function transferFundsToWinner(uint256 winnerIndex) private {
        (bool success, bytes memory data) = participants[winnerIndex].call{
            value: address(this).balance
        }("");

        if (success) {
            emit FundsTransfered(participants[winnerIndex]);
            currentPhase = LOTTERY_PHASE.INACTIVE; //How to handle non success scenarios?
            participants = new address payable[](0);
        } else {
            revert("Transfer funds failed");
        }
    }

    //I need a function for users to join the lottery and pay the fee
    function join() public payable {
        require(
            currentPhase == LOTTERY_PHASE.ACTIVE,
            "Cannot join the lottery as it has not started yet."
        );
        require(
            msg.value >= getEntryFeeETH(),
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
        require(
            participants.length > 0,
            "Cannot close lottery untill there is at least one participant."
        ); //may change this later
        currentPhase = LOTTERY_PHASE.CHOOSING_WINNER;
        requestRandomWords();
    }

    //get eth value of entry fee somehow
    //TODO: Add safemath here to avoid production issues, cause my math is garbage ;P
    function getEntryFeeETH() public view returns (uint256) {
        (, int256 price, , , ) = priceFeedUSD.latestRoundData();
        uint256 priceFullDecimals = uint256(price) * 10**10;
        uint256 entryFeeETH = (entryFeeUSD * 10**36) / priceFullDecimals;

        return entryFeeETH;
    }

    function getParticipants() public view returns (address payable[] memory) {
        return participants;
    }

    function getParticipantsNumber() public view returns (uint256) {
        return participants.length;
    }
}
