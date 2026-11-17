// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Donation Transparency Ledger
/// @notice Collects test Ether donations and records manager-controlled spending for a named cause.
contract DonationTransparencyLedger {
    struct Donation {
        uint256 id;
        address donor;
        uint256 amount;
        uint256 timestamp;
    }

    struct Expense {
        uint256 id;
        address recipient;
        uint256 amount;
        string purpose;
        uint256 timestamp;
    }

    address public immutable manager;
    string public cause;
    uint256 public totalDonated;
    uint256 public totalSpent;

    bool private _locked;
    Donation[] private donations;
    Expense[] private expenses;

    event CauseInitialized(address indexed manager, string cause, uint256 timestamp);
    event DonationReceived(
        uint256 indexed donationId,
        address indexed donor,
        uint256 amount,
        uint256 timestamp
    );
    event ExpenseRecorded(
        uint256 indexed expenseId,
        address indexed recipient,
        uint256 amount,
        string purpose,
        uint256 timestamp
    );

    modifier onlyManager() {
        require(msg.sender == manager, "Only manager can spend");
        _;
    }

    modifier nonReentrant() {
        require(!_locked, "Reentrant call");
        _locked = true;
        _;
        _locked = false;
    }

    constructor(string memory _cause) {
        require(bytes(_cause).length > 0, "Cause cannot be empty");
        manager = msg.sender;
        cause = _cause;
        emit CauseInitialized(msg.sender, _cause, block.timestamp);
    }

    /// @notice Donate test Ether to the named cause. Anyone may call this function.
    function donate() external payable {
        _recordDonation(msg.sender, msg.value);
    }

    /// @notice Fallback for direct Ether transfers so every donation is tracked.
    receive() external payable {
        _recordDonation(msg.sender, msg.value);
    }

    /// @notice Record an expense and transfer Ether to a recipient. Restricted to manager.
    function spend(
        address payable _recipient,
        uint256 _amount,
        string calldata _purpose
    ) external onlyManager nonReentrant {
        require(_recipient != address(0), "Invalid recipient address");
        require(_amount > 0, "Expense amount must be greater than zero");
        require(bytes(_purpose).length > 0, "Expense purpose cannot be empty");
        require(address(this).balance >= _amount, "Insufficient contract balance");

        uint256 expenseId = expenses.length;
        totalSpent += _amount;
        expenses.push(
            Expense({
                id: expenseId,
                recipient: _recipient,
                amount: _amount,
                purpose: _purpose,
                timestamp: block.timestamp
            })
        );

        emit ExpenseRecorded(expenseId, _recipient, _amount, _purpose, block.timestamp);

        (bool sent, ) = _recipient.call{value: _amount}("");
        require(sent, "ETH transfer failed");
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getDonationsCount() external view returns (uint256) {
        return donations.length;
    }

    function getExpensesCount() external view returns (uint256) {
        return expenses.length;
    }

    function getDonation(uint256 _index) external view returns (Donation memory) {
        require(_index < donations.length, "Donation index out of bounds");
        return donations[_index];
    }

    function getExpense(uint256 _index) external view returns (Expense memory) {
        require(_index < expenses.length, "Expense index out of bounds");
        return expenses[_index];
    }

    function getAllDonations() external view returns (Donation[] memory) {
        return donations;
    }

    function getAllExpenses() external view returns (Expense[] memory) {
        return expenses;
    }

    function getSummary()
        external
        view
        returns (
            address _manager,
            string memory _cause,
            uint256 _balance,
            uint256 _totalDonated,
            uint256 _totalSpent,
            uint256 _donationCount,
            uint256 _expenseCount
        )
    {
        return (
            manager,
            cause,
            address(this).balance,
            totalDonated,
            totalSpent,
            donations.length,
            expenses.length
        );
    }

    function _recordDonation(address _donor, uint256 _amount) internal {
        require(_amount > 0, "Donation must be greater than zero");
        uint256 donationId = donations.length;
        totalDonated += _amount;
        donations.push(
            Donation({
                id: donationId,
                donor: _donor,
                amount: _amount,
                timestamp: block.timestamp
            })
        );
        emit DonationReceived(donationId, _donor, _amount, block.timestamp);
    }
}
