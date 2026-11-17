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


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Donation Transparency Ledger</title>
  <style>
    :root { --bg:#f5f7f5; --card:#fff; --text:#1d3029; --muted:#64766d; --border:#e0e8e2; --primary:#207451; --primary-hover:#155b3d; --success-bg:#edf8f0; --success-border:#b2d9bd; --success-text:#205f36; --error-bg:#fff1ef; --error-border:#edb5ad; --error-text:#9c3024; --warn-bg:#fff8e9; --warn-border:#ebd6a8; --warn-text:#805e21; }
    * { box-sizing:border-box; }
    html { scroll-behavior:smooth; scroll-padding-top:24px; }
    body { margin:0; font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); line-height:1.55; }
    a { color:inherit; text-decoration:none; }
    .skip-link { position:absolute; left:20px; top:-70px; background:white; padding:12px; z-index:10; }
    .skip-link:focus { top:12px; }
    .topbar { background:white; border-bottom:1px solid var(--border); padding:20px max(24px,calc((100vw - 1240px)/2)); display:flex; align-items:center; justify-content:space-between; gap:24px; }
    .brand { display:flex; align-items:center; gap:12px; font-size:19px; font-weight:750; letter-spacing:-.6px; }
    .brand-mark { width:38px; height:38px; display:grid; place-items:center; background:var(--primary); border-radius:12px; color:white; font-size:24px; }
    .brand small { display:block; font-size:10px; letter-spacing:2px; color:var(--muted); text-transform:uppercase; font-weight:600; }
    nav { display:flex; gap:26px; font-size:13px; color:var(--muted); }
    nav a:hover { color:var(--primary); }
    .container { max-width:1240px; margin:36px auto; padding:0 24px 24px; }
    header { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px; margin-bottom:28px; }
    h1 { margin:6px 0; font-size:clamp(26px,4vw,36px); font-weight:650; letter-spacing:-1.2px; }
    .eyebrow { font-size:11px; letter-spacing:2px; text-transform:uppercase; font-weight:700; color:var(--primary); }
    .subtitle,.description { color:var(--muted); font-size:14px; margin:6px 0 20px; }
    .subtitle { margin:0; }
    #networkBadges { display:flex; flex-wrap:wrap; gap:8px; }
    .pill { display:inline-flex; align-items:center; padding:6px 10px; border-radius:6px; font-size:11px; font-weight:600; border:1px solid var(--border); background:white; }
    .pill.ok { background:var(--success-bg); color:var(--success-text); border-color:var(--success-border); }
    .pill.manager { background:#edf3ff; color:#34547f; }
    .pill.donor { color:var(--warn-text); background:var(--warn-bg); }
    .hero { display:grid; grid-template-columns:1fr auto; align-items:center; gap:24px; background:#173f30; color:#fff; border-radius:18px; padding:32px 36px; margin-bottom:24px; position:relative; overflow:hidden; }
    .hero h2 { font-size:clamp(24px,3vw,32px); letter-spacing:-.8px; font-weight:550; margin:8px 0; }
    .hero p { color:#c2d7ca; max-width:590px; font-size:14px; margin:0; }
    .hero .eyebrow { color:#b8d99f; }
    .hero-symbol { width:112px; height:112px; border:1px solid #60826d; border-radius:50%; display:grid; place-items:center; font-size:48px; color:#c9e7ad; box-shadow:0 0 0 16px #ffffff06,0 0 0 32px #ffffff04; margin:0 24px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:24px; margin-bottom:20px; min-width:0; }
    .card h2 { font-size:17px; letter-spacing:-.3px; margin:0 0 18px; font-weight:650; }
    .section-heading { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:18px; }
    .section-heading h2 { margin:0; }
    .grid-2 { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; }
    .stats { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }
    .stat-box { border:1px solid var(--border); border-radius:12px; padding:22px; background:#fafcf9; }
    .stat-box:first-child { background:#eef6ec; border-color:#d2e3cb; }
    .stat-label { font-size:12px; color:var(--muted); }
    .stat-value { font-size:clamp(22px,3vw,30px); font-weight:650; margin-top:10px; letter-spacing:-1px; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
    .mono { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; overflow-wrap:anywhere; }
    label { display:block; font-size:12px; font-weight:600; margin-bottom:7px; }
    input,select { width:100%; min-width:0; padding:12px; border:1px solid #d8e2da; border-radius:8px; font-size:14px; margin-bottom:16px; color:var(--text); background:#fff; min-height:44px; }
    button { padding:11px 18px; border:1px solid transparent; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; background:var(--primary); color:white; min-height:44px; transition:background .15s; }
    button:hover { background:var(--primary-hover); }
    button.secondary { background:white; border-color:var(--border); color:var(--text); }
    button.secondary:hover { background:#edf3ed; }
    button.danger-test { background:#916318; }
    button:disabled { opacity:.55; cursor:wait; }
    :focus-visible { outline:3px solid #7eb69a; outline-offset:3px; }
    .row-inline { display:flex; gap:14px; align-items:end; flex-wrap:wrap; }
    .row-inline > div { flex:1; min-width:200px; }
    .alert { border-radius:10px; padding:14px 18px; margin-bottom:20px; border:1px solid; display:none; overflow-wrap:anywhere; font-size:13px; }
    .alert.show { display:block; }
    .alert.success { background:var(--success-bg); border-color:var(--success-border); color:var(--success-text); }
    .alert.error { background:var(--error-bg); border-color:var(--error-border); color:var(--error-text); }
    .alert.warn { background:var(--warn-bg); border-color:var(--warn-border); color:var(--warn-text); display:block; font-size:12px; }
    .table-scroll { overflow-x:auto; }
    table { width:100%; border-collapse:collapse; font-size:12px; }
    th,td { text-align:left; padding:14px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
    th { color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.6px; background:#f7faf7; white-space:nowrap; }
    td strong { white-space:nowrap; font-weight:600; }
    tbody tr:hover { background:#fafcf9; }
    #eventsTable td:nth-child(3) { min-width:240px; max-width:520px; }
    .empty { color:var(--muted); text-align:center; padding:40px 20px; border:1px dashed var(--border); border-radius:10px; font-size:13px; }
    .quick-amounts { display:flex; gap:8px; margin:0 0 24px; flex-wrap:wrap; }
    .quick-amounts button { flex:1; }
    .donation-card { display:flex; flex-direction:column; }
    .donation-note { margin-top:auto; padding-top:28px; font-size:12px; color:var(--muted); }
    details { border-top:1px solid var(--border); padding-top:16px; margin-top:6px; }
    summary { cursor:pointer; font-size:13px; color:var(--primary); font-weight:600; margin-bottom:12px; }
    .contract-meta { margin-top:18px; color:var(--muted); display:grid; gap:6px; }
    footer { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; font-size:11px; color:var(--muted); padding:12px 0; }
    @media(max-width:800px) { .grid-2 { grid-template-columns:1fr; gap:0; } .topbar { padding:16px 20px; } nav { gap:16px; } .hero-symbol { display:none; } .hero { grid-template-columns:1fr; padding:26px; } .stats { gap:10px; } .stat-box { padding:16px; } }
    @media(max-width:540px) { .container { padding:0 16px; margin-top:24px; } .topbar { align-items:flex-start; } nav { flex-direction:column; gap:4px; font-size:11px; } .card { padding:18px; } .stats { grid-template-columns:1fr; } .stat-box { display:flex; align-items:center; justify-content:space-between; gap:12px; } .stat-value { margin:0; } .row-inline > div { min-width:0; flex-basis:100%; } .row-inline button { width:100%; } .section-heading { flex-wrap:wrap; } }
    .account-meta { font-size:13px; color:var(--muted); margin-bottom:12px; }
    .role-cards { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin:6px 0 18px; }
    .role-cards article { padding:18px; border:1px solid var(--border); border-radius:12px; background:#fafcf9; }
    .role-cards article.selected { border-color:var(--primary); background:#edf8f0; box-shadow:inset 0 0 0 1px var(--primary); }
    .role-cards h3 { font-size:15px; margin:12px 0 6px; }
    .role-cards p { font-size:12px; color:var(--muted); margin:0; }
    input[readonly] { background:#f5f7f5; font-weight:600; }
    @media(max-width:700px) { .role-cards { grid-template-columns:1fr; } }
    .allocation { display:flex; align-items:center; gap:16px; margin-top:20px; font-size:12px; color:var(--muted); }
    .allocation-track { flex:1; height:8px; border-radius:8px; background:#e9eee8; overflow:hidden; }
    #allocationBar { height:100%; background:#36835e; border-radius:8px; }
    .contract-meta { display:flex; justify-content:space-between; flex-wrap:wrap; font-size:13px; }
    #actionsGrid > .card { border-top:3px solid #bad3ad; }
    .card { box-shadow:0 3px 14px #173f3003; }
    .hero { background:radial-gradient(ellipse at top right,#31664a,transparent 65%),#173f30; }
    .table-scroll td { overflow-wrap:anywhere; max-width:240px; }
    .table-scroll td:first-child { color:var(--muted); }
    button:disabled { cursor:not-allowed; }
    .quick-amounts button[aria-pressed="true"] { background:#edf8f0; border-color:var(--primary); color:var(--primary); }
    #connectionSettings { margin-top:20px; }
    #eventsCard details { border:0; padding:0; margin:0; }
    #eventsCard summary { margin:0; }
    #eventsCard details[open] summary { margin-bottom:18px; }
    [hidden] { display:none !important; }
    @media(max-width:540px) { .allocation { flex-direction:column; align-items:stretch; gap:8px; } }
    @media(prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } button { transition:none; } }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="topbar">
    <a class="brand" href="#main"><span class="brand-mark" aria-hidden="true">↗</span><span>ClearFund<small>Donation transparency ledger</small></span></a>
    <nav aria-label="Main navigation"><a href="#connectionCard">Accounts</a><a href="#summaryCard">Overview</a><a href="#ledgersGrid">History</a></nav>
  </div>
  <main class="container" id="main">
    <header>
      <div>
        <div class="eyebrow">Every contribution, accounted for</div><h1>Give with purpose. Follow the impact.</h1>
        <p class="subtitle">Manage contributions and see how funds are used, all in one place.</p>
      </div>
      <div id="networkBadges" aria-live="polite"><span class="pill">Connecting…</span></div>
    </header>

    <section class="hero" aria-label="About the fund">
      <div><div class="eyebrow">CLEARFUND · COMMUNITY FUND</div><h2>Every contribution makes a difference.</h2><p>Support your community with confidence. Every contribution and expense is recorded publicly and can be verified.</p></div>
      <div class="hero-symbol" aria-hidden="true">↗</div>
    </section>
    <div class="card" id="connectionCard">
      <div class="section-heading"><h2>Choose your role</h2><button class="secondary" onclick="refreshDashboard()">↻ Refresh</button></div>
      <div class="row-inline">
        <div>
          <label for="activeAccount">Active account</label>
          <select id="activeAccount" onchange="updateRoleUI()"></select>
          <div id="accountMeta" class="account-meta"></div>
        </div>
      </div>
      <div class="role-cards" aria-label="Fixed account roles">
        <article data-account-role="0"><span class="pill manager">Manager</span><h3>Manage the fund</h3><p>Ganache account #0 · Creates funds and approves expenses.</p></article>
        <article data-account-role="1"><span class="pill ok">Donor</span><h3>Support the cause</h3><p>Ganache account #1 · Makes contributions to the fund.</p></article>
        <article data-account-role="2"><span class="pill donor">Recipient</span><h3>Receive support</h3><p>Ganache account #2 · Receives approved payments.</p></article>
      </div>
      <p class="description">Account identities are fixed. Select a role above to use its available actions.</p>
      <div id="assignmentNotice" class="alert warn" hidden></div>
      <details id="connectionSettings"><summary>Fund settings</summary><p class="description">Connect an existing fund or create a new one to get started.</p><div class="row-inline"><div>
          <label for="contractAddressInput">Fund contract address</label>
          <input id="contractAddressInput" class="mono" placeholder="0x… deployed contract address" />
        </div>
        <div style="flex: 0 0 auto; margin-bottom: 11px;">
          <button class="secondary" onclick="loadExistingContract()">Connect fund</button>
        </div>
      </div>
      <details><summary>Create a new fund</summary><p class="description">Select Manager to create a fund. The fixed Manager account will manage all new funds.</p><div class="row-inline">
        <div>
          <label for="deployCause">Fund name</label>
          <input id="deployCause" value="Community Flood Relief Fund" placeholder="Enter a fund name…" />
        </div>
        <div style="flex: 0 0 auto; margin-bottom: 11px;">
          <button id="deployBtn" onclick="deployNewContract()">Create fund</button>
        </div>
      </div>
      </details>
      </details>
    </div>

    <div id="txStatusBox" class="alert" role="status" aria-live="polite" tabindex="-1"></div>
    <div id="setupNotice" class="empty" style="margin-bottom:20px;">Welcome to ClearFund. Open Fund settings to connect or create your first fund.</div>

    <div class="card" id="summaryCard" style="display:none;">
      <div class="eyebrow">Fund overview</div><h2 id="sumCause" style="font-size:24px; margin-top:6px;">—</h2>
      <div class="stats">
        <div class="stat-box">
          <div class="stat-label">Available balance</div>
          <div class="stat-value" id="sumBalance">0 ETH</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Total contributions</div>
          <div class="stat-value" id="sumDonated">0 ETH</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Funds distributed</div>
          <div class="stat-value" id="sumSpent">0 ETH</div>
        </div>
      </div>
      <div class="contract-meta"><span>Manager: <strong id="sumManager">—</strong></span><span id="activityCount"></span></div><div class="allocation"><div class="allocation-track"><div id="allocationBar"></div></div><span id="allocationLabel"></span></div>
    </div>

    <div class="grid-2" id="actionsGrid" style="display:none;">
      <div class="card donation-card">
        <h2>Make a contribution</h2><p class="description">Choose how much to contribute. Follow your confirmed donation in the history below.</p>
        <p id="donorNotice" class="description"></p><label for="donateAmount">Donation amount (ETH)</label>
        <input id="donateAmount" type="number" step="any" min="0.000000000000000001" inputmode="decimal" value="2" />
        <div class="quick-amounts" aria-label="Suggested amounts"><button class="secondary" onclick="setDonation('0.1')">0.1 ETH</button><button class="secondary" onclick="setDonation('0.5')">0.5 ETH</button><button class="secondary" onclick="setDonation('1')">1 ETH</button><button class="secondary" onclick="setDonation('2')">2 ETH</button></div>
        <button id="donateBtn" onclick="submitDonation()">Donate now ↗</button><p class="donation-note">Local test network · Test Ether only.<br>Transactions are recorded publicly after confirmation.</p>
      </div>

      <div class="card">
        <h2>Record an expense</h2>
        <div id="roleNotice" class="alert warn"></div>
        <label for="recipientName">Payment recipient</label>
        <input id="recipientName" value="Recipient" readonly />
        <p class="description">All payments from this interface go to the fixed Recipient account.</p>
        <label for="spendAmount">Expense amount (ETH)</label>
        <input id="spendAmount" type="number" step="any" min="0.000000000000000001" inputmode="decimal" value="0.5" />
        <label for="spendPurpose">Expense purpose</label>
        <input id="spendPurpose" placeholder="e.g. Medical supplies and clean water" value="" />
        <button id="spendBtn" onclick="submitSpend()">Confirm expense</button>
      </div>
    </div>

    <div class="grid-2" id="ledgersGrid" style="display:none;">
      <div class="card">
        <h2>Expense history</h2>
        <div id="expensesTable" class="table-scroll" tabindex="0" role="region" aria-label="Expense history"></div>
      </div>
      <div class="card">
        <h2>Donation history</h2>
        <div id="donationsTable" class="table-scroll" tabindex="0" role="region" aria-label="Donation history"></div>
      </div>
    </div>

    <div class="card" id="eventsCard" style="display:none;">
      <details><summary>Blockchain confirmation log</summary>
      <div id="eventsTable" class="table-scroll" tabindex="0" role="region" aria-label="Confirmation log"></div></details>
    </div>
    <footer><span>ClearFund · Donation Transparency Ledger</span><span>Local Ganache network · Test Ether only</span></footer>
  </main>

  <script>
    let appState = null;
    let busy = false;
    let online = false;
    const $ = id => document.getElementById(id);
    const same = (a, b) => Boolean(a && b && a.toLowerCase() === b.toLowerCase());
    const escapeHtml = value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
    const roleAccounts = () => (appState?.accounts || []).filter(a => a.index < 3);
    const assignedAccount = index => appState?.accounts.find(a => a.index === index);
    function accountName(address) {
      if (!address) return 'No account selected';
      const account = appState?.accounts.find(a => same(a.address, address));
      if (account) return ['Manager', 'Donor', 'Recipient'][account.index] || `Account ${account.index + 1}`;
      let hash = 2166136261;
      for (const char of address.toLowerCase()) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
      return `Guest ${(hash >>> 0).toString(36).toUpperCase()}`;
    }
    function setDonation(amount) {
      $('donateAmount').value = amount;
      document.querySelectorAll('.quick-amounts button').forEach(button => button.setAttribute('aria-pressed', String(button.textContent === amount + ' ETH')));
    }
    $('donateAmount').addEventListener('input', () => setDonation($('donateAmount').value));
    function updateRoleUI() {
      const address = $('activeAccount').value;
      const account = roleAccounts().find(a => same(a.address, address));
      document.querySelectorAll('[data-account-role]').forEach(card => card.classList.toggle('selected', Number(card.dataset.accountRole) === account?.index));
      const isManager = account?.index === 0;
      const isDonor = account?.index === 1;
      const matchesManager = same(assignedAccount(0)?.address, appState?.summary?.manager);
      const canSpend = isManager && matchesManager && Boolean(assignedAccount(2));
      $('accountMeta').textContent = account ? `${accountName(address)} · Balance: ${account.balanceEth} ETH` : 'No assigned account available';
      $('roleNotice').textContent = canSpend ? 'You are the Manager. Review the amount and purpose before sending funds to the Recipient.' : 'Only the assigned Manager can record expenses. Select Manager to continue.';
      $('roleNotice').className = 'alert ' + (canSpend ? 'show success' : 'warn');
      $('donorNotice').textContent = isDonor ? 'Your contribution will be recorded under Donor.' : 'Select Donor to make a contribution.';
      $('donateBtn').disabled = busy || !online || !isDonor || !appState?.contractLoaded;
      $('donateAmount').disabled = $('donateBtn').disabled;
      document.querySelectorAll('.quick-amounts button').forEach(button => button.disabled = $('donateBtn').disabled);
      $('deployBtn').disabled = busy || !online || !isManager;
      $('spendBtn').disabled = busy || !online || !canSpend;
      for (const id of ['spendAmount', 'spendPurpose']) $(id).disabled = $('spendBtn').disabled;
      const mismatch = appState?.contractLoaded && !matchesManager;
      const missing = appState && roleAccounts().length < 3;
      $('assignmentNotice').hidden = !mismatch && !missing;
      $('assignmentNotice').textContent = missing ? 'This demo needs Ganache accounts #0, #1 and #2. Restore the missing accounts and refresh.' : mismatch ? `This fund is managed by ${accountName(appState.summary.manager)}, not the assigned Manager. Expense payments are disabled. Connect a fund created by Manager or create a new fund with Manager selected.` : '';
      $('networkBadges').innerHTML = online ? '<span class="pill ok">● Connected · Test network</span>' : '<span class="pill donor">Offline · Select Refresh to retry</span>';
    }
    function showStatus(ok, title, body) {
      const box = $('txStatusBox');
      box.className = 'alert show ' + (ok ? 'success' : 'error');
      box.innerHTML = `<strong>${escapeHtml(title)}</strong><div>${body}</div>`;
      box.focus({preventScroll: true});
      box.scrollIntoView({block:'nearest', behavior:'auto'});
    }
    async function apiCall(path, method = 'GET', body = null) {
      const opts = {method, headers:{'Content-Type':'application/json'}};
      if (body !== null) opts.body = JSON.stringify(body);
      const response = await fetch(path, opts);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to complete the request.');
      return data;
    }
    function friendlyError(error) {
      let message = error.message;
      const reasons = {
        'Only manager can spend':'Only the fund manager can record expenses.',
        'Insufficient contract balance':'The fund balance is too low. Enter a smaller amount.',
        'Donation must be greater than zero':'The donation amount must be greater than zero.',
        'Failed to fetch':'Unable to reach the server. Check your connection and refresh.'
      };
      for (const [reason, translation] of Object.entries(reasons)) if (message.includes(reason)) return escapeHtml(translation);
      message = message.replace(/0x[a-fA-F0-9]{40}\b/g, address => accountName(address));
      return escapeHtml(message);
    }
    function renderState() {
      const previous = $('activeAccount').value;
      const options = roleAccounts().map(a => `<option value="${escapeHtml(a.address)}">${escapeHtml(accountName(a.address))}</option>`).join('');
      $('activeAccount').innerHTML = options;
      if (roleAccounts().some(a => same(a.address, previous))) $('activeAccount').value = previous;
      else $('activeAccount').value = (appState.contractLoaded ? assignedAccount(1)?.address : assignedAccount(0)?.address) || '';
      if (appState.contractAddress) $('contractAddressInput').value = appState.contractAddress;
      const loaded = appState.contractLoaded;
      $('setupNotice').style.display = loaded ? 'none' : 'block';
      if (!loaded) $('connectionSettings').open = true;
      for (const id of ['summaryCard','actionsGrid','ledgersGrid','eventsCard']) $(id).style.display = loaded ? (id.endsWith('Grid') ? 'grid' : 'block') : 'none';
      if (loaded) {
        const summary = appState.summary;
        $('sumCause').textContent = summary.cause;
        $('sumBalance').textContent = summary.balanceEth + ' ETH';
        $('sumDonated').textContent = summary.totalDonatedEth + ' ETH';
        $('sumSpent').textContent = summary.totalSpentEth + ' ETH';
        $('sumManager').textContent = accountName(summary.manager);
        $('activityCount').textContent = `${summary.donationCount} contributions · ${summary.expenseCount} expenses`;
        const percent = Number(summary.totalDonatedEth) > 0 ? Math.min(100, Number(summary.totalSpentEth) / Number(summary.totalDonatedEth) * 100) : 0;
        $('allocationBar').style.width = percent + '%';
        $('allocationLabel').textContent = `${percent.toLocaleString('en-US', {maximumFractionDigits:1})}% of contributions distributed`;
        renderTables();
      }
      updateRoleUI();
    }
    function table(id, headings, rows, empty) {
      $(id).innerHTML = rows.length ? `<table><thead><tr>${headings.map(h => `<th scope="col">${h}</th>`).join('')}</tr></thead><tbody>${rows.map(row => '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>').join('')}</tbody></table>` : `<div class="empty">${empty}</div>`;
    }
    function renderTables() {
      table('expensesTable', ['ID','Recipient','Amount','Purpose','Time'], appState.expenses.map(e => [escapeHtml('#'+e.id),escapeHtml(accountName(e.recipient)),`<strong>${escapeHtml(e.amountEth)} ETH</strong>`,escapeHtml(e.purpose),escapeHtml(e.timestamp)]), 'No expenses yet. Confirmed payments will appear here.');
      table('donationsTable', ['ID','Donor','Amount','Time'], appState.donations.map(d => [escapeHtml('#'+d.id),escapeHtml(accountName(d.donor)),`<strong>${escapeHtml(d.amountEth)} ETH</strong>`,escapeHtml(d.timestamp)]), 'No donations yet. Be the first to support this fund.');
      const labels = {CauseInitialized:'Fund created', DonationReceived:'Donation received', ExpenseRecorded:'Expense paid'};
      table('eventsTable', ['Block','Activity','Details','Transaction hash'], appState.events.map(event => {
        const a = event.args;
        const detail = event.event === 'CauseInitialized' ? `${accountName(a.manager)} created ${a.cause}` : event.event === 'DonationReceived' ? `${accountName(a.donor)} contributed ${a.amountEth} ETH` : `${accountName(a.recipient)} received ${a.amountEth} ETH · ${a.purpose}`;
        return [escapeHtml('#'+event.blockNumber), escapeHtml(labels[event.event] || event.event), escapeHtml(detail), `<details><summary>View hash</summary><span class="mono">${escapeHtml(event.txHash)}</span></details>`];
      }), 'No confirmed activity yet.');
    }
    async function refreshState() {
      try { appState = await apiCall('/api/state'); online = true; renderState(); }
      catch (error) { online = false; updateRoleUI(); throw error; }
    }
    async function refreshDashboard() {
      try { await refreshState(); }
      catch (error) { showStatus(false, 'Unable to refresh data', friendlyError(error) + '<br>Displayed data may be out of date.'); }
    }
    function amountValid(id) {
      const input = $(id);
      if (!input.value || !Number.isFinite(Number(input.value)) || Number(input.value) <= 0) {
        showStatus(false, 'Invalid amount', 'Enter an ETH amount greater than zero.');
        return false;
      }
      return true;
    }
    async function transact(path, payload, title, describe) {
      let result;
      try { result = await apiCall(path, 'POST', payload); }
      catch (error) { showStatus(false, 'Request not completed', friendlyError(error)); return; }
      let warning = '';
      try { await refreshState(); }
      catch (_) { warning = '<br>The transaction succeeded, but balances could not be refreshed. Select Refresh to retry; do not submit the transaction again.'; }
      showStatus(true, title, describe(result) + warning);
    }
    async function loadExistingContract() {
      const address = $('contractAddressInput').value.trim();
      if (!/^0x[a-fA-F0-9]{40}$/.test(address)) return showStatus(false, 'Invalid contract address', 'Enter a contract address starting with 0x followed by 40 hexadecimal characters.');
      await transact('/api/load', {address}, 'Fund connected', () => 'You can now view the overview, contribute, and follow the fund history.');
    }
    async function deployNewContract() {
      if (!same($('activeAccount').value, assignedAccount(0)?.address)) return showStatus(false, 'Manager required', 'Select Manager to create a fund.');
      const cause = $('deployCause').value.trim();
      if (!cause) return showStatus(false, 'Fund name required', 'Enter a name that describes the purpose of this fund.');
      await transact('/api/deploy', {from:$('activeAccount').value, cause}, 'Fund created', result => `${escapeHtml(cause)} · Manager: ${escapeHtml(accountName(result.manager))}`);
    }
    async function submitDonation() {
      if (!same($('activeAccount').value, assignedAccount(1)?.address)) return showStatus(false, 'Donor required', 'Select Donor to make a contribution.');
      if (!amountValid('donateAmount')) return;
      await transact('/api/donate', {from:$('activeAccount').value, amount:$('donateAmount').value}, 'Thank you for your contribution!', result => `${escapeHtml(accountName(result.from))} contributed <strong>${escapeHtml(result.amountEth)} ETH</strong>. The transaction is confirmed and recorded in the history.`);
    }
    async function submitSpend() {
      if (!same($('activeAccount').value, assignedAccount(0)?.address) || !same($('activeAccount').value, appState?.summary?.manager)) return showStatus(false, 'Manager required', 'Select the assigned Manager to continue.');
      if (!amountValid('spendAmount')) return;
      const recipient = assignedAccount(2)?.address || '';
      const amount = $('spendAmount').value;
      const purpose = $('spendPurpose').value.trim();
      if (!/^0x[a-fA-F0-9]{40}$/.test(recipient) || /^0x0{40}$/i.test(recipient)) return showStatus(false, 'Recipient unavailable', 'The fixed Recipient account must be available before sending a payment.');
      if (!purpose) return showStatus(false, 'Expense purpose required', 'Describe the expense so contributors can follow how funds are used.');
      if (Number(amount) > Number(appState.summary.balanceEth)) return showStatus(false, 'Insufficient fund balance', 'The expense must not exceed the available balance.');
      await transact('/api/spend', {from:$('activeAccount').value, recipient, amount, purpose}, 'Expense recorded', result => `Sent <strong>${escapeHtml(result.amountEth)} ETH</strong> to ${escapeHtml(accountName(result.recipient))}.<br>Purpose: ${escapeHtml(result.purpose)}`);
    }
    for (const name of ['loadExistingContract','deployNewContract','submitDonation','submitSpend','refreshDashboard']) {
      const action = window[name];
      window[name] = async function() {
        if (busy) return;
        busy = true;
        const controls = [...document.querySelectorAll('button, input, select')];
        controls.forEach(el => el.disabled = true);
        $('main').setAttribute('aria-busy','true');
        const box = $('txStatusBox');
        box.className = 'alert warn';
        box.textContent = 'Processing… Please wait for confirmation.';
        try { await action(); if (box.textContent.startsWith('Processing…')) box.className = 'alert'; }
        finally {
          busy = false;
          controls.forEach(el => el.disabled = false);
          $('main').setAttribute('aria-busy','false');
          updateRoleUI();
        }
      };
    }
    setDonation($('donateAmount').value);
    refreshDashboard();
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
    print(f"       Updated Available balance: {state['summary']['balanceEth']} ETH")

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
    print(f"       Recorded Purpose: '{state['expenses'][0]['purpose']}' | Available balance: {state['summary']['balanceEth']} ETH")

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
