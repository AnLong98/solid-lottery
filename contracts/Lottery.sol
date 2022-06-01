// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] public participants;
    uint256 public entryFeeUSD;
    AggregatorV3Interface internal priceFeedUSD;

    constructor(uint256 _entryUSD, address _feedNetworkAddress) public {
        priceFeed = AggregatorV3Interface(feeNetworkAddress);
    }

    //I need a function for users to join the lottery and pay the fee
    function join() public payable {
        participants.push(payable(msg.sender));
    }

    //For nowI will make this callable, later change to clock decision
    function startLottery() public {}

    //Close it, also make a clock later
    function endLottery() public {}

    //get USD value of entry fee somehow
    //TODO: Add safemath here to avoid production issues, cause my math is garbage ;P
    function getEntryFeeUSD() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 priceInDecimals = ((entryUSD * (10**18)) / (price * (10**10)));
        return priceInDecimals;
    }
}
