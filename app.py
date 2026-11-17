"""Donation Transparency Ledger - Single-file Python (web3.py) Web UI & Test Runner."""

from __future__ import annotations

import argparse
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import traceback
from typing import Any
import webbrowser

from web3 import Web3
from web3.exceptions import ContractLogicError, Web3RPCError
from web3.logs import DISCARD

RPC_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0x1f90642d8fbCfe29a95528357f0AB300158ffE34"  # Optional: paste deployed contract address from Remix IDE here.

ABI_JSON = """
[
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_cause",
				"type": "string"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "manager",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "cause",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "CauseInitialized",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "donate",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "donationId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "donor",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "DonationReceived",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "expenseId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "recipient",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "purpose",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "ExpenseRecorded",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address payable",
				"name": "_recipient",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_purpose",
				"type": "string"
			}
		],
		"name": "spend",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	},
	{
		"inputs": [],
		"name": "cause",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAllDonations",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "id",
						"type": "uint256"
					},
					{
						"internalType": "address",
						"name": "donor",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct DonationTransparencyLedger.Donation[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getAllExpenses",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "id",
						"type": "uint256"
					},
					{
						"internalType": "address",
						"name": "recipient",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "purpose",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct DonationTransparencyLedger.Expense[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_index",
				"type": "uint256"
			}
		],
		"name": "getDonation",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "id",
						"type": "uint256"
					},
					{
						"internalType": "address",
						"name": "donor",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct DonationTransparencyLedger.Donation",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getDonationsCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_index",
				"type": "uint256"
			}
		],
		"name": "getExpense",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "id",
						"type": "uint256"
					},
					{
						"internalType": "address",
						"name": "recipient",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "purpose",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					}
				],
				"internalType": "struct DonationTransparencyLedger.Expense",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getExpensesCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getSummary",
		"outputs": [
			{
				"internalType": "address",
				"name": "_manager",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_cause",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_balance",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_totalDonated",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_totalSpent",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_donationCount",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_expenseCount",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "manager",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalDonated",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalSpent",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
"""

# Bytecode compiled from DonationTransparencyLedger.sol (Solidity 0.8.24, --evm-version paris --optimize)
CONTRACT_BYTECODE = (
    
    "60a06040523480156200001157600080fd5b506040516200169e3803806200169e833981016040819052"
    "620000349162000125565b60008151116200008a5760405162461bcd60e51b8152602060048201526015"
    "60248201527f43617573652063616e6e6f7420626520656d707479000000000000000000000060448201"
    "5260640160405180910390fd5b3360805260006200009c82826200026e565b50336001600160a01b0316"
    "7fa352fb7c949e0c2d8973923fa7d90306b342ba79ded5e3cfe4ba5de95d1dd8af8242604051620000da"
    "9291906200033a565b60405180910390a25062000377565b634e487b7160e01b60005260416004526024"
    "6000fd5b60005b838110156200011c57818101518382015260200162000102565b50506000910152565b"
    "6000602082840312156200013857600080fd5b81516001600160401b03808211156200015057600080fd"
    "5b818401915084601f8301126200016557600080fd5b8151818111156200017a576200017a620000e956"
    "5b604051601f8201601f19908116603f01168101908382118183101715620001a557620001a5620000e9"
    "565b81604052828152876020848701011115620001bf57600080fd5b620001d283602083016020880162"
    "0000ff565b979650505050505050565b600181811c90821680620001f257607f821691505b6020821081"
    "036200021357634e487b7160e01b600052602260045260246000fd5b50919050565b601f821115620002"
    "69576000816000526020600020601f850160051c81016020861015620002445750805b601f850160051c"
    "820191505b81811015620002655782815560010162000250565b5050505b505050565b815160016001"
    "60401b038111156200028a576200028a620000e9565b620002a2816200029b8454620001dd565b846200"
    "0219565b602080601f831160018114620002da5760008415620002c15750858301515b60001960038690"
    "1b1c1916600185901b17855562000265565b600085815260208120601f198616915b828110156200030b"
    "57888601518255948401946001909101908401620002ea565b50858210156200032a5787850151600019"
    "600388901b60f8161c191681555b5050505050600190811b01905550565b604081526000835180604084"
    "01526200035b816060850160208801620000ff565b602083019390935250601f91909101601f19160160"
    "6001919050565b6080516112fd620003a1600039600081816101a30152818161051101526105f3015261"
    "12fd6000f3fe6080604052600436106100e05760003560e01c8063735e5db61161007f578063dd53ff6c"
    "11610059578063dd53ff6c14610261578063ed88c68e14610283578063ef07a81f1461028b578063fb34"
    "6eab146102b857600080fd5b8063735e5db6146101fd578063878c14841461022a578063c93527d81461"
    "024c57600080fd5b806338a59a07116100bb57806338a59a07146101475780634051ddac146101695780"
    "63481c6a75146101915780636e3f5764146101dd57600080fd5b8062b37044146100f65780630daded95"
    "1461011f57806312065fe01461013457600080fd5b366100f1576100ef33346102ce565b005b600080fd"
    "5b34801561010257600080fd5b5061010c60015481565b6040519081526020015b60405180910390f35b"
    "34801561012b57600080fd5b5060055461010c565b34801561014057600080fd5b504761010c565b3480"
    "1561015357600080fd5b5061015c610479565b6040516101169190610e22565b34801561017557600080"
    "fd5b5061017e610503565b6040516101169796959493929190610edd565b34801561019d57600080fd"
    "5b506101c57f000000000000000000000000000000000000000000000000000000000000000081565b60"
    "40516001600160a01b039091168152602001610116565b3480156101e957600080fd5b506100ef6101f8"
    "366004610f2b565b6105e8565b34801561020957600080fd5b5061021d610218366004610fc0565b6109"
    "e5565b6040516101169190611028565b34801561023657600080fd5b5061023f610b83565b6040516101"
    "169190611042565b34801561025857600080fd5b5060045461010c565b34801561026d57600080fd5b50"
    "610276610c11565b6040516101169190611055565b6100ef610d2e565b34801561029757600080fd5b"
    "506102ab6102a6366004610fc0565b610d3a565b60405161011691906110b9565b3480156102c4576000"
    "80fd5b5061010c60025481565b6000811161032e5760405162461bcd60e51b8152602060048201526022"
    "60248201527f446f6e6174696f6e206d7573742062652067726561746572207468616e207a6560448201"
    "5261726f60f01b60648201526084015b60405180910390fd5b6004546001805483919060009061034690"
    "84906110ef565b9091555050604080516080810182528281526001600160a01b03858116602080840182"
    "8152848601888152426060870181815260048054600181018255600082905298517f8a35acfbc15ff81a"
    "39ae7d344fd709f28e8600b4aa8c65c6b64bfe7fe36bd19b999091029889015592517f8a35acfbc15ff8"
    "1a39ae7d344fd709f28e8600b4aa8c65c6b64bfe7fe36bd19c880180546001600160a01b031916919097"
    "1617909555517f8a35acfbc15ff81a39ae7d344fd709f28e8600b4aa8c65c6b64bfe7fe36bd19d860155"
    "517f8a35acfbc15ff81a39ae7d344fd709f28e8600b4aa8c65c6b64bfe7fe36bd19e9094019390935583"
    "51868152928301919091529183917f3dbea1b4ce5f95137fdcac9b1d685825c3d70ace830df1ca5a181d"
    "3887add410910160405180910390a3505050565b60606004805480602002602001604051908101604052"
    "809291908181526020016000905b828210156104fa576000848152602090819020604080516080810182"
    "5260048602909201805483526001808201546001600160a01b0316848601526002820154928401929092"
    "52600301546060830152908352909201910161049d565b50505050905090565b60006060600080600080"
    "60007f000000000000000000000000000000000000000000000000000000000000000060004760015460"
    "025460048054905060058054905085805461055190611110565b80601f01602080910402602001604051"
    "9081016040528092919081815260200182805461057d90611110565b80156105ca5780601f1061059f57"
    "6101008083540402835291602001916105ca565b820191906000526020600020905b8154815290600101"
    "906020018083116105ad57829003601f168201915b505050505095509650965096509650965096509650"
    "90919293949596565b336001600160a01b037f000000000000000000000000000000000000000000000000"
    "000000000000000016146106595760405162461bcd60e51b815260206004820152601660248201527513"
    "db9b1e481b585b9859d95c8818d85b881cdc195b9960521b6044820152606401610325565b60035460ff"
    "161561069d5760405162461bcd60e51b815260206004820152600e60248201526d1499595b9d1c985b9d"
    "0818d85b1b60921b6044820152606401610325565b6003805460ff191660011790556001600160a01b03"
    "84166107005760405162461bcd60e51b815260206004820152601960248201527f496e76616c696420726563697069656e74206164647265737300000000000000604482015260640161"
    "0325565b600083116107615760405162461bcd60e51b815260206004820152602860248201527f457870"
    "656e736520616d6f756e74206d7573742062652067726561746572207460448201526768616e207a6572"
    "6f60c01b6064820152608401610325565b806107ae5760405162461bcd60e51b81526020600482015260"
    "1f60248201527f457870656e736520707572706f73652063616e6e6f7420626520656d707479006044"
    "820152606401610325565b824710156107fe5760405162461bcd60e51b815260206004820152601d6024"
    "8201527f496e73756666696369656e7420636f6e74726163742062616c616e636500000060448201526064"
    "01610325565b600554600280548591906000906108169084906110ef565b925050819055506005604051"
    "8060a00160405280838152602001876001600160a01b0316815260200186815260200185858080601f01"
    "602080910402602001604051908101604052809392919081815260200183838082843760009201829052"
    "509385525050426020938401525083546001808201865594825290829020835160059092020190815590"
    "82015192810180546001600160a01b0319166001600160a01b0390941693909317909255604081015160"
    "02830155606081015190919060038201906108e590826111b1565b506080820151816004015550508460"
    "01600160a01b0316817fa6bf4a07b4b4310ba944ca044c0c4dca31b776aaa285d40bb3f81a1ce928097c"
    "868686426040516109329493929190611271565b60405180910390a36000856001600160a01b03168560"
    "405160006040518083038185875af1925050503d8060008114610987576040519150601f19603f3d0116"
    "82016040523d82523d6000602084013e61098c565b606091505b50509050806109d35760405162461bcd"
    "60e51b8152602060048201526013602482015272115512081d1c985b9cd9995c8819985a5b1959606a1b"
    "6044820152606401610325565b50506003805460ff1916905550505050565b610a206040518060a00160"
    "4052806000815260200160006001600160a01b0316815260200160008152602001606081526020016000"
    "81525090565b6005548210610a715760405162461bcd60e51b815260206004820152601b60248201527f"
    "457870656e736520696e646578206f7574206f6620626f756e6473000000000060448201526064016103"
    "25565b60058281548110610a8457610a846112b1565b90600052602060002090600502016040518060a0"
    "016040529081600082015481526020016001820160009054906101000a90046001600160a01b03166001"
    "600160a01b03166001600160a01b0316815260200160028201548152602001600382018054610af09061"
    "1110565b80601f0160208091040260200160405190810160405280929190818152602001828054610b1c"
    "90611110565b8015610b695780601f10610b3e57610100808354040283529160200191610b69565b820191"
    "906000526020600020905b815481529060010190602001808311610b4c57829003601f168201915b5050"
    "50505081526020016004820154815250509050919050565b60008054610b9090611110565b80601f0160"
    "208091040260200160405190810160405280929190818152602001828054610bbc90611110565b801561"
    "0c095780601f10610bde57610100808354040283529160200191610c09565b8201919060005260206000"
    "20905b815481529060010190602001808311610bec57829003601f168201915b505050505081565b6060"
    "6005805480602002602001604051908101604052809291908181526020016000905b828210156104fa57"
    "60008481526020908190206040805160a081018252600586029092018054835260018101546001600160"
    "a01b031693830193909352600283015490820152600382018054919291606084019190610c9390611110"
    "565b80601f0160208091040260200160405190810160405280929190818152602001828054610cbf9061"
    "1110565b8015610d0c5780601f10610ce157610100808354040283529160200191610d0c565b82019190"
    "6000526020600020905b815481529060010190602001808311610cef57829003601f168201915b505050"
    "5050815260200160048201548152505081526020019060010190610c35565b610d3833346102ce565b56"
    "5b610d6e60405180608001604052806000815260200160006001600160a01b0316815260200160008152"
    "602001600081525090565b6004548210610dbf5760405162461bcd60e51b815260206004820152601c60"
    "248201527f446f6e6174696f6e20696e646578206f7574206f6620626f756e64730000000060448201"
    "52606401610325565b60048281548110610dd257610dd26112b1565b6000918252602091829020604080"
    "5160808101825260049093029091018054835260018101546001600160a01b0316938301939093526002"
    "83015490820152600390910154606082015292915050565b602080825282518282018190526000919084"
    "8201906040850190845b81811015610e8b57610e78838551805182526020808201516001600160a01b03"
    "169083015260408082015190830152606090810151910152565b9284019260809290920191600101610e"
    "3e565b50909695505050505050565b6000815180845260005b81811015610ebd57602081850181015186"
    "830182015201610ea1565b506000602082860101526020601f19601f8301168501019150509291505056"
    "5b6001600160a01b038816815260e060208201819052600090610f0190830189610e97565b6040830197"
    "909752506060810194909452608084019290925260a083015260c09091015292915050565b6000806000"
    "8060608587031215610f4157600080fd5b84356001600160a01b0381168114610f5857600080fd5b9350"
    "60208501359250604085013567ffffffffffffffff80821115610f7c57600080fd5b818701915087601f"
    "830112610f9057600080fd5b813581811115610f9f57600080fd5b886020828501011115610fb1576000"
    "80fd5b95989497505060200194505050565b600060208284031215610fd257600080fd5b503591905056"
    "5b8051825260018060a01b036020820151166020830152604081015160408301526000606082015160a0"
    "606085015261101460a0850182610e97565b608093840151949093019390935250919050565b60208152"
    "600061103b6020830184610fd9565b9392505050565b60208152600061103b6020830184610e97565b6000"
    "60208083016020845280855180835260408601915060408160051b87010192506020870160005b828110"
    "156110ac57603f1988860301845261109a858351610fd9565b9450928501929085019060010161107e56"
    "5b5092979650505050505050565b815181526020808301516001600160a01b031690820152604080830151"
    "9082015260608083015190820152608081015b92915050565b808201808211156110e957634e487b7160"
    "e01b600052601160045260246000fd5b600181811c9082168061112457607f821691505b602082108103"
    "61114457634e487b7160e01b600052602260045260246000fd5b50919050565b634e487b7160e01b6000"
    "52604160045260246000fd5b601f8211156111ac576000816000526020600020601f850160051c810160"
    "208610156111895750805b601f850160051c820191505b818110156111a857828155600101611195565b"
    "5050505b505050565b815167ffffffffffffffff8111156111cb576111cb61114a565b6111df816111d9"
    "8454611110565b84611160565b602080601f83116001811461121457600084156111fc5750858301515b60"
    "0019600386901b1c1916600185901b1785556111a8565b600085815260208120601f198616915b828110"
    "1561124357888601518255948401946001909101908401611224565b5085821015611261578785015160"
    "0019600388901b60f8161c191681555b5050505050600190811b01905550565b84815260606020820152"
    "8260608201528284608083013760006080848301015260006080601f19601f8601168301019050826040"
    "83015295945050505050565b634e487b7160e01b600052603260045260246000fdfea264697066735822"
    "1220d7ca8937cf13f98f1ed1f02d35110ee49cb47810cacd8c1413b17e8f0f3426c464736f6c63430008"
    "180033"
)


def format_timestamp(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_eth(wei_amount: int) -> str:
    eth_value = Web3.from_wei(wei_amount, "ether")
    return f"{eth_value:.6f}".rstrip("0").rstrip(".") or "0"


def extract_error_reason(exc: Exception) -> str:
    """Return a clean human-readable Solidity revert or RPC error reason."""
    raw = str(exc)
    if isinstance(exc, ContractLogicError):
        raw = str(exc.message or exc)
    elif isinstance(exc, Web3RPCError):
        raw = str(exc)

    cleaned = raw
    for marker in ("VM Exception while processing transaction: revert", "execution reverted:"):
        if marker in cleaned:
            cleaned = cleaned.split(marker, 1)[1].strip()
    for stop in ("', 'data':", '", "data":', "',", '",', "'}", '"}'):
        if stop in cleaned:
            cleaned = cleaned.split(stop, 1)[0].strip()
    return cleaned.strip("'\" ") or "Transaction reverted by contract"


class LedgerService:
    """Thread-safe wrapper around Web3 + Ganache for DonationTransparencyLedger."""

    def __init__(self, rpc_url: str = RPC_URL, contract_address: str = CONTRACT_ADDRESS) -> None:
        self.rpc_url = rpc_url
        self.abi = json.loads(ABI_JSON)
        self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        if not self.w3.is_connected():
            raise ConnectionError(
                f"Cannot connect to Ganache at {rpc_url}. Start Ganache and verify the RPC URL."
            )
        self.lock = threading.Lock()
        self.contract = None
        self.contract_address = ""
        if contract_address.strip():
            self.load_contract(contract_address.strip())

    def accounts_info(self) -> list[dict[str, Any]]:
        accounts = self.w3.eth.accounts
        manager = self.contract.functions.manager().call() if self.contract else None
        result = []
        for idx, addr in enumerate(accounts):
            bal_wei = self.w3.eth.get_balance(addr)
            result.append(
                {
                    "index": idx,
                    "address": addr,
                    "balanceEth": format_eth(bal_wei),
                    "isManager": bool(manager and addr.lower() == manager.lower()),
                }
            )
        return result

    def load_contract(self, address: str) -> str:
        if not Web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        checksum = Web3.to_checksum_address(address)
        code = self.w3.eth.get_code(checksum)
        if not code:
            raise ValueError(
                f"No contract bytecode found at {checksum} on {self.rpc_url}. "
                "Verify the address or deploy a new contract."
            )
        with self.lock:
            self.contract = self.w3.eth.contract(address=checksum, abi=self.abi)
            # Smoke-check expected view call so mismatched contracts fail early.
            self.contract.functions.getSummary().call()
            self.contract_address = checksum
        return checksum

    def deploy_contract(self, from_account: str, cause: str) -> dict[str, Any]:
        cause = cause.strip()
        if not cause:
            raise ValueError("Cause cannot be empty.")
        sender = self._validate_account(from_account)
        with self.lock:
            factory = self.w3.eth.contract(abi=self.abi, bytecode=CONTRACT_BYTECODE)
            try:
                tx_hash = factory.constructor(cause).transact({"from": sender})
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            except (ContractLogicError, Web3RPCError, ValueError) as exc:
                raise RuntimeError(extract_error_reason(exc)) from exc

            contract_addr = Web3.to_checksum_address(receipt["contractAddress"])
            self.contract = self.w3.eth.contract(address=contract_addr, abi=self.abi)
            self.contract_address = contract_addr
            return {
                "contractAddress": contract_addr,
                "manager": sender,
                "cause": cause,
                "txHash": tx_hash.hex(),
                "blockNumber": receipt["blockNumber"],
                "gasUsed": receipt["gasUsed"],
                "events": self._decode_receipt_events(receipt),
            }

    def donate(self, from_account: str, eth_amount: str | float) -> dict[str, Any]:
        contract = self._require_contract()
        sender = self._validate_account(from_account)
        wei_amount = self._parse_eth_to_wei(eth_amount)
        with self.lock:
            try:
                tx_hash = contract.functions.donate().transact(
                    {"from": sender, "value": wei_amount}
                )
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            except (ContractLogicError, Web3RPCError, ValueError) as exc:
                raise RuntimeError(extract_error_reason(exc)) from exc

            return {
                "action": "donate",
                "from": sender,
                "amountEth": format_eth(wei_amount),
                "txHash": tx_hash.hex(),
                "blockNumber": receipt["blockNumber"],
                "gasUsed": receipt["gasUsed"],
                "events": self._decode_receipt_events(receipt),
            }

    def spend(
        self,
        from_account: str,
        recipient: str,
        eth_amount: str | float,
        purpose: str,
    ) -> dict[str, Any]:
        contract = self._require_contract()
        sender = self._validate_account(from_account)
        if not Web3.is_address(recipient):
            raise ValueError(f"Invalid recipient address: {recipient}")
        recipient_checksum = Web3.to_checksum_address(recipient)
        wei_amount = self._parse_eth_to_wei(eth_amount)

        with self.lock:
            try:
                tx_hash = contract.functions.spend(
                    recipient_checksum, wei_amount, purpose.strip()
                ).transact({"from": sender})
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            except (ContractLogicError, Web3RPCError, ValueError) as exc:
                raise RuntimeError(extract_error_reason(exc)) from exc

            return {
                "action": "spend",
                "from": sender,
                "recipient": recipient_checksum,
                "amountEth": format_eth(wei_amount),
                "purpose": purpose.strip(),
                "txHash": tx_hash.hex(),
                "blockNumber": receipt["blockNumber"],
                "gasUsed": receipt["gasUsed"],
                "events": self._decode_receipt_events(receipt),
            }

    def get_state(self) -> dict[str, Any]:
        with self.lock:
            accounts = self.accounts_info()
            base = {
                "connected": True,
                "rpcUrl": self.rpc_url,
                "chainId": self.w3.eth.chain_id,
                "clientVersion": self.w3.client_version,
                "contractLoaded": self.contract is not None,
                "contractAddress": self.contract_address,
                "accounts": accounts,
            }
            if not self.contract:
                return base

            manager, cause, balance, total_donated, total_spent, d_count, e_count = (
                self.contract.functions.getSummary().call()
            )
            donations = [
                {
                    "id": item[0],
                    "donor": item[1],
                    "amountEth": format_eth(item[2]),
                    "timestamp": format_timestamp(item[3]),
                }
                for item in self.contract.functions.getAllDonations().call()
            ]
            expenses = [
                {
                    "id": item[0],
                    "recipient": item[1],
                    "amountEth": format_eth(item[2]),
                    "purpose": item[3],
                    "timestamp": format_timestamp(item[4]),
                }
                for item in self.contract.functions.getAllExpenses().call()
            ]

            base.update(
                {
                    "summary": {
                        "manager": manager,
                        "cause": cause,
                        "balanceEth": format_eth(balance),
                        "totalDonatedEth": format_eth(total_donated),
                        "totalSpentEth": format_eth(total_spent),
                        "donationCount": d_count,
                        "expenseCount": e_count,
                    },
                    "donations": list(reversed(donations)),
                    "expenses": list(reversed(expenses)),
                    "events": self._fetch_all_events(),
                }
            )
            return base

    def _require_contract(self):
        if not self.contract:
            raise RuntimeError("No contract loaded. Deploy a contract or load an address first.")
        return self.contract

    def _validate_account(self, address: str) -> str:
        if not Web3.is_address(address):
            raise ValueError(f"Invalid account address: {address}")
        return Web3.to_checksum_address(address)

    def _parse_eth_to_wei(self, eth_amount: str | float) -> int:
        try:
            value = float(eth_amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amount must be a valid number.") from exc
        if value < 0:
            raise ValueError("Amount cannot be negative.")
        return int(Web3.to_wei(str(eth_amount).strip(), "ether"))

    def _decode_receipt_events(self, receipt: Any) -> list[dict[str, Any]]:
        if not self.contract:
            return []
        decoded: list[dict[str, Any]] = []
        for event_name in ("CauseInitialized", "DonationReceived", "ExpenseRecorded"):
            event_cls = getattr(self.contract.events, event_name)
            for log in event_cls().process_receipt(receipt, errors=DISCARD):
                decoded.append(self._format_event_log(log))
        return decoded

    def _fetch_all_events(self) -> list[dict[str, Any]]:
        if not self.contract:
            return []
        items: list[dict[str, Any]] = []
        for event_name in ("CauseInitialized", "DonationReceived", "ExpenseRecorded"):
            event_cls = getattr(self.contract.events, event_name)
            for log in event_cls().get_logs(from_block=0):
                items.append(self._format_event_log(log))
        items.sort(key=lambda e: (e["blockNumber"], e["logIndex"]), reverse=True)
        return items

    def _format_event_log(self, log: Any) -> dict[str, Any]:
        args = {}
        for key, val in dict(log["args"]).items():
            if key == "amount":
                args["amountEth"] = format_eth(val)
            elif key == "timestamp":
                args["timestamp"] = format_timestamp(val)
            else:
                args[key] = val
        return {
            "event": log["event"],
            "blockNumber": log["blockNumber"],
            "logIndex": log["logIndex"],
            "txHash": log["transactionHash"].hex(),
            "args": args,
        }


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Donation Transparency Ledger</title>
  <style>
    :root {
      --bg: #f4f6f9;
      --card: #ffffff;
      --text: #18212f;
      --muted: #5a6577;
      --border: #dce2ec;
      --primary: #1d4ed8;
      --primary-hover: #1e40af;
      --success-bg: #ecfdf5;
      --success-border: #10b981;
      --success-text: #065f46;
      --error-bg: #fef2f2;
      --error-border: #ef4444;
      --error-text: #991b1b;
      --warn-bg: #fffbeb;
      --warn-border: #f59e0b;
      --warn-text: #92400e;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }
    .container { max-width: 1120px; margin: 24px auto; padding: 0 16px 40px; }
    header {
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
      gap: 12px; margin-bottom: 18px;
    }
    h1 { margin: 0; font-size: 1.65rem; }
    .subtitle { margin: 4px 0 0; color: var(--muted); font-size: 0.95rem; }
    .pill {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 600;
      border: 1px solid var(--border); background: var(--card);
    }
    .pill.ok { border-color: var(--success-border); background: var(--success-bg); color: var(--success-text); }
    .pill.manager { border-color: #6366f1; background: #eef2ff; color: #3730a3; }
    .pill.donor { border-color: var(--warn-border); background: var(--warn-bg); color: var(--warn-text); }
    .card {
      background: var(--card); border: 1px solid var(--border); border-radius: 12px;
      padding: 18px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .card h2 { margin: 0 0 12px; font-size: 1.1rem; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 12px; }
    .stat-box {
      border: 1px solid var(--border); border-radius: 10px; padding: 12px; background: #fafbfd;
    }
    .stat-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.03em; }
    .stat-value { font-size: 1.25rem; font-weight: 700; margin-top: 4px; word-break: break-all; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.86rem; }
    label { display: block; font-size: 0.88rem; font-weight: 600; margin-bottom: 5px; }
    input, select {
      width: 100%; padding: 9px 11px; border: 1px solid var(--border); border-radius: 8px;
      font-size: 0.94rem; margin-bottom: 11px; background: #fff;
    }
    button {
      padding: 9px 15px; border: none; border-radius: 8px; font-size: 0.92rem;
      font-weight: 600; cursor: pointer; background: var(--primary); color: #fff;
    }
    button:hover { background: var(--primary-hover); }
    button.secondary { background: #334155; }
    button.secondary:hover { background: #1e293b; }
    button.danger-test { background: #b45309; }
    button.danger-test:hover { background: #92400e; }
    .row-inline { display: flex; gap: 10px; align-items: end; flex-wrap: wrap; }
    .row-inline > div { flex: 1; min-width: 220px; }
    .alert {
      border-radius: 10px; padding: 12px 14px; margin-bottom: 16px; border: 1px solid;
      display: none;
    }
    .alert.show { display: block; }
    .alert.success { background: var(--success-bg); border-color: var(--success-border); color: var(--success-text); }
    .alert.error { background: var(--error-bg); border-color: var(--error-border); color: var(--error-text); }
    .alert.warn { background: var(--warn-bg); border-color: var(--warn-border); color: var(--warn-text); display: block; margin-bottom: 10px; font-size: 0.88rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th, td { text-align: left; padding: 9px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
    th { color: var(--muted); font-size: 0.8rem; text-transform: uppercase; }
    .empty { color: var(--muted); font-style: italic; padding: 8px 0; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>Donation Transparency Ledger</h1>
        <p class="subtitle">DS 441 A Mini Project &mdash; Ganache Local Blockchain &amp; Python web3.py</p>
      </div>
      <div id="networkBadges"></div>
    </header>

    <div class="card">
      <h2>1. Wallet Account &amp; Contract Connection (Ganache)</h2>
      <div class="row-inline">
        <div>
          <label for="activeAccount">Active Ganache Account (Acting Wallet)</label>
          <select id="activeAccount" onchange="updateRoleUI()"></select>
        </div>
        <div>
          <label for="contractAddressInput">Deployed Contract Address</label>
          <input id="contractAddressInput" class="mono" placeholder="0x... (from Remix or Deploy button)" />
        </div>
        <div style="flex: 0 0 auto; margin-bottom: 11px;">
          <button class="secondary" onclick="loadExistingContract()">Load Contract</button>
        </div>
      </div>
      <div class="row-inline" style="margin-top: 6px; padding-top: 10px; border-top: 1px dashed var(--border);">
        <div>
          <label for="deployCause">Or Deploy New Contract Directly to Ganache (using Active Account as Manager)</label>
          <input id="deployCause" value="Community Flood Relief Fund" placeholder="Enter named cause..." />
        </div>
        <div style="flex: 0 0 auto; margin-bottom: 11px;">
          <button onclick="deployNewContract()">Deploy Contract</button>
        </div>
      </div>
      <div id="accountMeta" class="mono" style="color: var(--muted); margin-top: 4px;"></div>
    </div>

    <div id="txStatusBox" class="alert"></div>

    <div class="card" id="summaryCard" style="display:none;">
      <h2>2. Contract State &amp; Transparency Summary</h2>
      <div class="stats">
        <div class="stat-box">
          <div class="stat-label">Named Cause</div>
          <div class="stat-value" id="sumCause">-</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Contract Balance</div>
          <div class="stat-value" id="sumBalance">0 ETH</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Total Donated</div>
          <div class="stat-value" id="sumDonated">0 ETH</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Total Spent</div>
          <div class="stat-value" id="sumSpent">0 ETH</div>
        </div>
      </div>
      <div class="mono" style="margin-top: 12px; color: var(--muted);">
        Contract: <span id="sumContractAddr">-</span> &nbsp;|&nbsp;
        Manager: <span id="sumManager">-</span>
      </div>
    </div>

    <div class="grid-2" id="actionsGrid" style="display:none;">
      <div class="card">
        <h2>3. Donate Test Ether (Anyone)</h2>
        <label for="donateAmount">Donation Amount (ETH)</label>
        <input id="donateAmount" type="number" step="0.01" min="0" value="2" />
        <button onclick="submitDonation()">Send Donation</button>
      </div>

      <div class="card">
        <h2>4. Record Controlled Expense (Manager Only)</h2>
        <div id="roleNotice" class="alert warn"></div>
        <label for="recipientPreset">Select Recipient Preset (or enter custom address below)</label>
        <select id="recipientPreset" onchange="syncRecipientFromPreset()"></select>
        <label for="spendRecipient">Recipient Address</label>
        <input id="spendRecipient" class="mono" placeholder="0x..." />
        <label for="spendAmount">Expense Amount (ETH)</label>
        <input id="spendAmount" type="number" step="0.01" min="0" value="0.5" />
        <label for="spendPurpose">Expense Purpose</label>
        <input id="spendPurpose" placeholder="e.g., Medical supplies and clean water" value="Medical supplies for flood relief" />
        <button id="spendBtn" onclick="submitSpend()">Record Expense (Spend)</button>
      </div>
    </div>

    <div class="grid-2" id="ledgersGrid" style="display:none;">
      <div class="card">
        <h2>Recorded Expenses (Amount &amp; Purpose)</h2>
        <div id="expensesTable"></div>
      </div>
      <div class="card">
        <h2>Recorded Donations</h2>
        <div id="donationsTable"></div>
      </div>
    </div>

    <div class="card" id="eventsCard" style="display:none;">
      <h2>On-Chain Event Logs</h2>
      <div id="eventsTable"></div>
    </div>
  </div>

  <script>
    let appState = null;

    async function apiCall(path, method = "GET", body = null) {
      const opts = { method, headers: { "Content-Type": "application/json" } };
      if (body !== null) opts.body = JSON.stringify(body);
      const res = await fetch(path, opts);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      return data;
    }

    function showStatus(ok, title, htmlBody) {
      const box = document.getElementById("txStatusBox");
      box.className = "alert show " + (ok ? "success" : "error");
      box.innerHTML = `<strong>${escapeHtml(title)}</strong><div style="margin-top:6px;">${htmlBody}</div>`;
    }

    function escapeHtml(str) {
      return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function shortAddr(addr) {
      if (!addr || addr.length < 12) return addr || "";
      return addr.slice(0, 8) + "..." + addr.slice(-6);
    }

    function syncRecipientFromPreset() {
      const val = document.getElementById("recipientPreset").value;
      if (val) document.getElementById("spendRecipient").value = val;
    }

    function updateRoleUI() {
      if (!appState) return;
      const select = document.getElementById("activeAccount");
      const activeAddr = select.value;
      const acc = appState.accounts.find(a => a.address === activeAddr);
      const summary = appState.summary;

      const meta = document.getElementById("accountMeta");
      if (acc) {
        meta.textContent = `Selected: ${acc.address} | Wallet Balance: ${acc.balanceEth} ETH`;
      }

      const badges = document.getElementById("networkBadges");
      const netBadge = `<span class="pill ok">Ganache Connected &bull; Chain ID ${appState.chainId}</span>`;
      let roleBadge = "";
      if (summary) {
        const isMgr = activeAddr.toLowerCase() === summary.manager.toLowerCase();
        roleBadge = isMgr
          ? `<span class="pill manager">Role: MANAGER (Authorized)</span>`
          : `<span class="pill donor">Role: DONOR / NON-MANAGER</span>`;

        const notice = document.getElementById("roleNotice");
        const spendBtn = document.getElementById("spendBtn");
        if (isMgr) {
          notice.textContent = "Authorized Manager selected. Valid spending transactions will succeed.";
          spendBtn.className = "";
        } else {
          notice.textContent = "Non-Manager selected. Button remains enabled intentionally so you can verify on-chain rejection by the Smart Contract.";
          spendBtn.className = "danger-test";
        }
      }
      badges.innerHTML = netBadge + " " + roleBadge;
    }

    async function refreshState() {
      const prevActive = document.getElementById("activeAccount").value;
      const prevRecipient = document.getElementById("spendRecipient").value;
      appState = await apiCall("/api/state");

      const activeSelect = document.getElementById("activeAccount");
      activeSelect.innerHTML = appState.accounts.map(a => {
        const tag = a.isManager ? " [MANAGER]" : "";
        return `<option value="${a.address}">Account #${a.index}${tag} (${shortAddr(a.address)}) - ${a.balanceEth} ETH</option>`;
      }).join("");
      if (prevActive && appState.accounts.some(a => a.address === prevActive)) {
        activeSelect.value = prevActive;
      } else if (appState.accounts.length > 1 && appState.contractLoaded) {
        activeSelect.value = appState.accounts[1].address;
      }

      const recPreset = document.getElementById("recipientPreset");
      recPreset.innerHTML = `<option value="">-- Custom Address --</option>` + appState.accounts.map(a =>
        `<option value="${a.address}">Account #${a.index} (${shortAddr(a.address)}) - ${a.balanceEth} ETH</option>`
      ).join("");
      if (!prevRecipient && appState.accounts.length > 2) {
        recPreset.value = appState.accounts[2].address;
        document.getElementById("spendRecipient").value = appState.accounts[2].address;
      } else if (prevRecipient) {
        document.getElementById("spendRecipient").value = prevRecipient;
      }

      if (appState.contractAddress) {
        document.getElementById("contractAddressInput").value = appState.contractAddress;
      }

      const show = appState.contractLoaded;
      document.getElementById("summaryCard").style.display = show ? "block" : "none";
      document.getElementById("actionsGrid").style.display = show ? "grid" : "none";
      document.getElementById("ledgersGrid").style.display = show ? "grid" : "none";
      document.getElementById("eventsCard").style.display = show ? "block" : "none";

      if (show && appState.summary) {
        const s = appState.summary;
        document.getElementById("sumCause").textContent = s.cause;
        document.getElementById("sumBalance").textContent = s.balanceEth + " ETH";
        document.getElementById("sumDonated").textContent = s.totalDonatedEth + " ETH";
        document.getElementById("sumSpent").textContent = s.totalSpentEth + " ETH";
        document.getElementById("sumContractAddr").textContent = appState.contractAddress;
        document.getElementById("sumManager").textContent = s.manager;
        renderTables(appState.expenses, appState.donations, appState.events);
      }

      updateRoleUI();
    }

    function renderTables(expenses, donations, events) {
      const expEl = document.getElementById("expensesTable");
      if (!expenses.length) {
        expEl.innerHTML = `<div class="empty">No expenses recorded yet.</div>`;
      } else {
        expEl.innerHTML = `<table><thead><tr><th>ID</th><th>Recipient</th><th>Amount</th><th>Purpose</th><th>Time</th></tr></thead><tbody>` +
          expenses.map(e => `<tr>
            <td>#${e.id}</td>
            <td class="mono" title="${e.recipient}">${shortAddr(e.recipient)}</td>
            <td><strong>${e.amountEth} ETH</strong></td>
            <td>${escapeHtml(e.purpose)}</td>
            <td>${e.timestamp}</td>
          </tr>`).join("") + `</tbody></table>`;
      }

      const donEl = document.getElementById("donationsTable");
      if (!donations.length) {
        donEl.innerHTML = `<div class="empty">No donations recorded yet.</div>`;
      } else {
        donEl.innerHTML = `<table><thead><tr><th>ID</th><th>Donor</th><th>Amount</th><th>Time</th></tr></thead><tbody>` +
          donations.map(d => `<tr>
            <td>#${d.id}</td>
            <td class="mono" title="${d.donor}">${shortAddr(d.donor)}</td>
            <td><strong>${d.amountEth} ETH</strong></td>
            <td>${d.timestamp}</td>
          </tr>`).join("") + `</tbody></table>`;
      }

      const evtEl = document.getElementById("eventsTable");
      if (!events.length) {
        evtEl.innerHTML = `<div class="empty">No contract events emitted yet.</div>`;
      } else {
        evtEl.innerHTML = `<table><thead><tr><th>Block</th><th>Event</th><th>Details</th><th>Tx Hash</th></tr></thead><tbody>` +
          events.map(ev => `<tr>
            <td>#${ev.blockNumber}</td>
            <td><strong>${escapeHtml(ev.event)}</strong></td>
            <td class="mono">${escapeHtml(JSON.stringify(ev.args))}</td>
            <td class="mono" title="${ev.txHash}">${shortAddr(ev.txHash)}</td>
          </tr>`).join("") + `</tbody></table>`;
      }
    }

    async function loadExistingContract() {
      const address = document.getElementById("contractAddressInput").value.trim();
      try {
        const res = await apiCall("/api/load", "POST", { address });
        await refreshState();
        showStatus(true, "Contract Loaded", `Connected to contract <span class="mono">${escapeHtml(res.contractAddress)}</span>.`);
      } catch (err) {
        showStatus(false, "Failed to Load Contract", escapeHtml(err.message));
      }
    }

    async function deployNewContract() {
      const from = document.getElementById("activeAccount").value;
      const cause = document.getElementById("deployCause").value.trim();
      try {
        const res = await apiCall("/api/deploy", "POST", { from, cause });
        await refreshState();
        showStatus(
          true,
          "Contract Deployed Successfully",
          `Address: <span class="mono">${escapeHtml(res.contractAddress)}</span><br/>Manager: <span class="mono">${escapeHtml(res.manager)}</span><br/>Tx Hash: <span class="mono">${escapeHtml(res.txHash)}</span>`
        );
      } catch (err) {
        showStatus(false, "Deployment Failed", escapeHtml(err.message));
      }
    }

    async function submitDonation() {
      const from = document.getElementById("activeAccount").value;
      const amount = document.getElementById("donateAmount").value;
      try {
        const res = await apiCall("/api/donate", "POST", { from, amount });
        await refreshState();
        showStatus(
          true,
          "Donation Transaction Confirmed",
          `Donor: <span class="mono">${escapeHtml(res.from)}</span> donated <strong>${escapeHtml(res.amountEth)} ETH</strong><br/>Tx Hash: <span class="mono">${escapeHtml(res.txHash)}</span> (Block #${res.blockNumber})`
        );
      } catch (err) {
        showStatus(
          false,
          "Donation Transaction Rejected",
          `Sender: <span class="mono">${escapeHtml(from)}</span><br/>Error: <strong>${escapeHtml(err.message)}</strong>`
        );
      }
    }

    async function submitSpend() {
      const from = document.getElementById("activeAccount").value;
      const recipient = document.getElementById("spendRecipient").value.trim();
      const amount = document.getElementById("spendAmount").value;
      const purpose = document.getElementById("spendPurpose").value.trim();
      try {
        const res = await apiCall("/api/spend", "POST", { from, recipient, amount, purpose });
        await refreshState();
        showStatus(
          true,
          "Expense Recorded & Funds Transferred",
          `Manager: <span class="mono">${escapeHtml(res.from)}</span> sent <strong>${escapeHtml(res.amountEth)} ETH</strong> to <span class="mono">${escapeHtml(res.recipient)}</span><br/>Purpose: ${escapeHtml(res.purpose)}<br/>Tx Hash: <span class="mono">${escapeHtml(res.txHash)}</span> (Block #${res.blockNumber})`
        );
      } catch (err) {
        showStatus(
          false,
          "Spending Transaction Rejected by Smart Contract",
          `Caller: <span class="mono">${escapeHtml(from)}</span><br/>Reason: <strong>${escapeHtml(err.message)}</strong><br/>On-chain state and contract balance remain unchanged.`
        );
      }
    }

    refreshState().catch(err => showStatus(false, "Connection Error", escapeHtml(err.message)));
  </script>
</body>
</html>
"""


def make_handler(service: LedgerService) -> type[BaseHTTPRequestHandler]:
    class LedgerHTTPHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

        def do_GET(self) -> None:
            if self.path == "/" or self.path.startswith("/?"):
                body = HTML_PAGE.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if self.path == "/api/state":
                try:
                    self._send_json(HTTPStatus.OK, service.get_state())
                except Exception as exc:
                    self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return

            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})

        def do_POST(self) -> None:
            try:
                data = self._read_json()
                if self.path == "/api/load":
                    addr = service.load_contract(data.get("address", ""))
                    self._send_json(HTTPStatus.OK, {"contractAddress": addr})
                elif self.path == "/api/deploy":
                    res = service.deploy_contract(data.get("from", ""), data.get("cause", ""))
                    self._send_json(HTTPStatus.OK, res)
                elif self.path == "/api/donate":
                    res = service.donate(data.get("from", ""), data.get("amount", ""))
                    self._send_json(HTTPStatus.OK, res)
                elif self.path == "/api/spend":
                    res = service.spend(
                        data.get("from", ""),
                        data.get("recipient", ""),
                        data.get("amount", ""),
                        data.get("purpose", ""),
                    )
                    self._send_json(HTTPStatus.OK, res)
                else:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    return LedgerHTTPHandler


def run_automated_tests(service: LedgerService) -> None:
    """Deploy a fresh contract to Ganache and verify all success and rejection scenarios."""
    accounts = service.w3.eth.accounts
    if len(accounts) < 3:
        raise RuntimeError("Ganache must provide at least 3 unlocked accounts for automated tests.")

    manager_acct = accounts[0]
    donor_acct = accounts[1]
    recipient_acct = accounts[2]
    cause_name = "Disaster Relief Transparency Fund"

    print("=" * 72)
    print("DONATION TRANSPARENCY LEDGER - AUTOMATED GANACHE TEST SUITE")
    print("=" * 72)
    print(f"RPC URL          : {service.rpc_url} (Chain ID: {service.w3.eth.chain_id})")
    print(f"Account #0 (Mgr) : {manager_acct}")
    print(f"Account #1 (Usr) : {donor_acct}")
    print(f"Account #2 (Rec) : {recipient_acct}")
    print("-" * 72)

    # Test 1: Deploy and verify initial contract state
    deploy_info = service.deploy_contract(manager_acct, cause_name)
    state = service.get_state()
    summary = state["summary"]
    assert summary["manager"].lower() == manager_acct.lower()
    assert summary["cause"] == cause_name
    assert summary["balanceEth"] == "0"
    print(f"[PASS] Test 1 - Deploy & Initial State")
    print(f"       Contract: {deploy_info['contractAddress']} | Tx: {deploy_info['txHash']}")
    print(f"       Cause: '{summary['cause']}' | Balance: {summary['balanceEth']} ETH")

    # Test 2: Valid donation from Account #1 (non-manager)
    donate_info = service.donate(donor_acct, "2")
    state = service.get_state()
    assert state["summary"]["balanceEth"] == "2"
    assert state["summary"]["totalDonatedEth"] == "2"
    assert len(donate_info["events"]) == 1
    assert donate_info["events"][0]["event"] == "DonationReceived"
    print(f"[PASS] Test 2 - Donate 2 ETH (Account #1 -> Contract)")
    print(f"       Tx: {donate_info['txHash']} | Event: {donate_info['events'][0]['event']}")
    print(f"       Updated Contract Balance: {state['summary']['balanceEth']} ETH")

    # Test 3: Rejected zero donation
    zero_rejected = False
    try:
        service.donate(donor_acct, "0")
    except RuntimeError as exc:
        zero_rejected = True
        zero_err = str(exc)
    assert zero_rejected, "Expected 0 ETH donation to revert"
    print(f"[PASS] Test 3 - Reject Invalid 0 ETH Donation")
    print(f"       Reverted as expected: {zero_err}")

    # Test 4: Rejected spending attempt by non-manager (Account #1)
    recipient_before = service.w3.eth.get_balance(recipient_acct)
    unauth_rejected = False
    try:
        service.spend(donor_acct, recipient_acct, "0.5", "Unauthorized withdrawal attempt")
    except RuntimeError as exc:
        unauth_rejected = True
        unauth_err = str(exc)
    assert unauth_rejected, "Expected non-manager spend to revert"
    state = service.get_state()
    assert state["summary"]["balanceEth"] == "2"
    assert service.w3.eth.get_balance(recipient_acct) == recipient_before
    assert state["summary"]["expenseCount"] == 0
    print(f"[PASS] Test 4 - Reject Non-Manager Spending Attempt (Account #1)")
    print(f"       Reverted as expected: {unauth_err}")
    print(f"       Contract balance preserved at {state['summary']['balanceEth']} ETH")

    # Test 5: Valid expense recorded by Manager (Account #0)
    spend_purpose = "Emergency medical kits"
    spend_info = service.spend(manager_acct, recipient_acct, "0.5", spend_purpose)
    state = service.get_state()
    recipient_after = service.w3.eth.get_balance(recipient_acct)
    assert recipient_after - recipient_before == Web3.to_wei("0.5", "ether")
    assert state["summary"]["balanceEth"] == "1.5"
    assert state["summary"]["totalSpentEth"] == "0.5"
    assert state["summary"]["expenseCount"] == 1
    assert state["expenses"][0]["amountEth"] == "0.5"
    assert state["expenses"][0]["purpose"] == spend_purpose
    assert spend_info["events"][0]["event"] == "ExpenseRecorded"
    print(f"[PASS] Test 5 - Valid Manager Expense 0.5 ETH (Account #0 -> Account #2)")
    print(f"       Tx: {spend_info['txHash']} | Event: {spend_info['events'][0]['event']}")
    print(f"       Recorded Purpose: '{state['expenses'][0]['purpose']}' | Contract Balance: {state['summary']['balanceEth']} ETH")

    # Test 6: Rejected overspend exceeding contract balance
    overspend_rejected = False
    try:
        service.spend(manager_acct, recipient_acct, "10", "Overspend test")
    except RuntimeError as exc:
        overspend_rejected = True
        overspend_err = str(exc)
    assert overspend_rejected, "Expected overspend to revert"
    assert service.get_state()["summary"]["balanceEth"] == "1.5"
    print(f"[PASS] Test 6 - Reject Overspend (> 1.5 ETH balance)")
    print(f"       Reverted as expected: {overspend_err}")

    print("-" * 72)
    print("ALL 6 TESTS PASSED SUCCESSFULLY")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="Donation Transparency Ledger (Ganache + web3.py)")
    parser.add_argument("--rpc", default=RPC_URL, help=f"Ganache RPC URL (default: {RPC_URL})")
    parser.add_argument("--address", default=CONTRACT_ADDRESS, help="Existing deployed contract address")
    parser.add_argument("--port", type=int, default=8000, help="Local Web UI port (default: 8000)")
    parser.add_argument("--test", action="store_true", help="Run automated Ganache test suite")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser in Web UI mode")
    args = parser.parse_args()

    service = LedgerService(rpc_url=args.rpc, contract_address=args.address)

    if args.test:
        run_automated_tests(service)
        return

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(service))
    url = f"http://127.0.0.1:{args.port}"
    print(f"Connected to Ganache at {args.rpc} (Chain ID: {service.w3.eth.chain_id})")
    print(f"Web3 interface running at {url} (Press Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}")
        traceback.print_exc()
        raise SystemExit(1)
