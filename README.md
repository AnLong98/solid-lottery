# Introduction

Implementation of decentralized lottery with smart contracts built using Solidity on Ethereum network. Lottery is time limited.
Users can enter lottery when it opens by paying a fee in Ether, when lottery is over a random winner is chosen and reward distributed to his wallet address. ETH/USD conversion rate and random numbers are acquired using Chainlink.

## Technologies

 - Solidity
 - Eth brownie
 - Python
 - Ganache CLI

## How to run this?

 - Install Eth brownie, ganache CLI, Pipx and Python 3.10
 - Compile with ```brownie compile```
 - Run tests with ```brownie test --capture=no```
 - Create .env file 
 - Create and fund Chainlink subscription on https://vrf.chain.link/
 - Add your Rinkeby private key to RINKEBY_PRIVATE_KEY variable in .env
 - Add your local ganache CLI private key to .env variable ACCOUNT_PRIVATE_KEY
 - Add your VRF subscription ID to VRF_SUB_ID in .env file
 - Create Infura project and add project id to .env file variable WEB3_INFURA_PROJECT_ID
 - Run ``` brownie run scripts/deploy.py --network=rinkeby ``` to deploy to rinkeby testnet
 - Copy deployed contract address from console or Infura, and add it to consumers list on Chainlink VRF

## Authors
Predrag Glavas 

## License
[MIT](https://choosealicense.com/licenses/mit/)
