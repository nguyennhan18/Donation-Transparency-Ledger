# Donation Transparency Ledger

**Course:** DS 441 A - Blockchain: Theory & Practices  
**Student:** Nguyễn Văn Nhẫn (`29211135779`)  

## 1. Project Overview
**Donation Transparency Ledger** is a Solidity smart contract and Python (`web3.py`) application running on a local Ganache blockchain. It allows anyone to donate test Ether for a named cause while restricting spending exclusively to the contract manager, recording every expense's recipient, amount, and purpose on-chain.

## 2. Repository Structure
```text
donation-transparency-ledger/
├── DonationTransparencyLedger.sol   # Solidity smart contract (rules, permissions, events)
├── app.py                           # Python web3.py Web UI + automated test suite
├── README.md                        # Setup, deployment, run steps, and test explanations
├── .gitignore
└── screenshots/                     # Evidence screenshots of demo and tests
```

## 3. Prerequisites
- **Ganache** (local Ethereum blockchain running on `http://127.0.0.1:7545`)
- **Python 3.12** (or Python 3.10+) with `web3` (`web3==8.0.0`) installed in `../.venv`
- *(Optional)* **Remix IDE** if deploying `DonationTransparencyLedger.sol` manually to Ganache

## 4. Ganache Network Settings
- **RPC Server URL:** `http://127.0.0.1:7545`
- **Network / Chain ID:** `1337`
- **Accounts used in demo/tests (test Ether only):**
  - **Account #0:** Manager (deploys contract and records valid expenses)
  - **Account #1:** Donor / Non-Manager (donates test Ether and tests unauthorized spending rejection)
  - **Account #2:** Recipient (receives valid expense payouts)

## 5. Smart Contract Design (`DonationTransparencyLedger.sol`)
- **Named Cause & Manager:** Set once in `constructor(string memory _cause)` (`manager = msg.sender`, emits `CauseInitialized`).
- **Open Donations (`donate()` / `receive()`):** Anyone can send `> 0` test Ether; updates `totalDonated`, stores `Donation` record, and emits `DonationReceived`.
- **Manager-Only Spending (`spend()`):** Enforced on-chain via `modifier onlyManager` (`require(msg.sender == manager, "Only manager can spend")`) and `nonReentrant` guard. Validates non-zero recipient, `amount > 0`, non-empty `purpose`, and `address(this).balance >= amount` before storing `Expense`, emitting `ExpenseRecorded`, and transferring Ether.

## 6. Deployment & Run Steps

### Option A: Run the Interactive Web Interface (Deploy or Load Contract)
1. Start **Ganache** (`http://127.0.0.1:7545`, Chain ID `1337`).
2. Start the Python Web UI using the workspace `.venv`:
   ```bash
   cd donation-transparency-ledger
   ../.venv/bin/python app.py
   ```
3. Open `http://127.0.0.1:8000` in your browser:
   - Either select **Account #0**, enter a cause name, and click **Deploy Contract**,
   - **Or** deploy `DonationTransparencyLedger.sol` via **Remix IDE** (*Custom - External Http Provider* `http://127.0.0.1:7545`), paste the deployed address into **Deployed Contract Address**, and click **Load Contract**.
     *(Note for Ganache v7.7.3: in Remix, use Solidity `0.8.19` or set EVM Version to `paris` under Advanced Configurations so `PUSH0` is not emitted.)*
4. Switch between Ganache accounts in the dropdown to demonstrate **Donate** (Account #1), **Unauthorized Spend Rejection** (Account #1), and **Valid Manager Spend** (Account #0 -> Account #2).

### Option B: Run the Automated Test Suite
```bash
cd donation-transparency-ledger
../.venv/bin/python app.py --test
```

## 7. Test Results & Explanation
Running `../.venv/bin/python app.py --test` against local Ganache (`Chain ID: 1337`) passed all 6 test cases:

| # | Scenario | Caller | Expected & Observed Result | On-Chain Explanation |
|---|---|---|---|---|
| 1 | Deploy & Initial State | Account #0 | **PASS** — `cause` set, `balance = 0 ETH` | `constructor` assigns `manager = msg.sender` (`Account #0`) and emits `CauseInitialized`. |
| 2 | Valid Donation (`2 ETH`) | Account #1 | **PASS** — `balance = 2 ETH`, `DonationReceived` emitted | `donate()` is `external payable` with no role restriction; anyone may donate `> 0` ETH. |
| 3 | Zero Donation (`0 ETH`) | Account #1 | **PASS (Rejected)** — Reverted: `Donation must be greater than zero` | `require(_amount > 0)` rejects empty value transfers on-chain. |
| 4 | Unauthorized Spend (`0.5 ETH`) | Account #1 | **PASS (Rejected)** — Reverted: `Only manager can spend`; balance stayed `2 ETH` | `onlyManager` checks `msg.sender == manager` on the EVM; because `Account #1 != Account #0`, state changes revert and no funds move. |
| 5 | Valid Expense (`0.5 ETH`) | Account #0 | **PASS** — `Account #2` received `0.5 ETH`, `balance = 1.5 ETH`, `ExpenseRecorded` emitted, purpose stored | `Account #0` passes `onlyManager`; contract stores `{amount: 0.5 ETH, purpose: "Emergency medical kits"}` before transferring ETH. |
| 6 | Overspend (`10 ETH > 1.5 ETH`) | Account #0 | **PASS (Rejected)** — Reverted: `Insufficient contract balance` | Contract checks `address(this).balance >= _amount` on-chain to prevent overdrawing. |

## 8. Demonstration Screenshots
Place captured screenshots in `screenshots/` (for example):
- `screenshots/01_ganache_accounts.png` — Ganache RPC & test accounts
- `screenshots/02_deploy_contract.png` — Contract deployment by Manager (`Account #0`)
- `screenshots/03_donate_success.png` — Successful donation by `Account #1`
- `screenshots/04_non_manager_rejected.png` — Rejected spending attempt by `Account #1`
- `screenshots/05_manager_spend_success.png` — Valid spending by `Account #0` showing stored amount & purpose
- `screenshots/06_automated_tests.png` — Terminal output of `app.py --test`

## 9. Citations & Assistance
- [Web3.py Documentation](https://web3py.readthedocs.io/) for Python JSON-RPC interaction, contract deployment, receipt event decoding, and transaction handling.
- [Solidity Documentation](https://docs.soliditylang.org/) for Checks-Effects-Interactions pattern, modifiers, and event declarations.
- AI assistance (Antigravity) was used to help structure the smart contract, Python Web3 interface, automated test script, and documentation; all code and tests were verified locally on Ganache.
