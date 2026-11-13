import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize stateless Streamable HTTP MCP Server for Cloud Run
mcp = FastMCP(
    "SimpleBank-MCP",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    stateless_http=True,
    json_response=True,
)

# In-memory mock banking database
ACCOUNTS = {
    "ACC-001": {"holder": "Alice Johnson", "balance": 15400.50, "currency": "USD"},
    "ACC-002": {"holder": "Carlos Ruiz", "balance": 3200.00, "currency": "USD"},
}

TRANSACTIONS = {
    "ACC-001": [
        {"date": "2026-11-10", "type": "CREDIT", "amount": 2500.00, "description": "Payroll Deposit"},
        {"date": "2026-11-11", "type": "DEBIT", "amount": -120.50, "description": "Utility Bill Payment"},
    ],
    "ACC-002": [
        {"date": "2026-11-09", "type": "CREDIT", "amount": 500.00, "description": "Initial Deposit"},
    ],
}


@mcp.tool()
def get_account_balance(account_id: str) -> dict:
    """Retrieve the available balance for a bank account (e.g., ACC-001, ACC-002)."""
    account = ACCOUNTS.get(account_id)
    if not account:
        return {"error": f"Account {account_id} not found."}
    return {"account_id": account_id, **account}


@mcp.tool()
def list_transactions(account_id: str, limit: int = 5) -> dict:
    """List the most recent transactions for a bank account."""
    if account_id not in ACCOUNTS:
        return {"error": f"Account {account_id} not found."}
    return {"account_id": account_id, "transactions": TRANSACTIONS.get(account_id, [])[:limit]}


@mcp.tool()
def transfer_funds(
    source_account: str,
    destination_account: str,
    amount: float,
    description: str = "Bank transfer",
) -> dict:
    """Transfer funds between two bank accounts."""
    if source_account not in ACCOUNTS or destination_account not in ACCOUNTS:
        return {"error": "Invalid source or destination account."}
    if amount <= 0:
        return {"error": "Transfer amount must be greater than zero."}
    if ACCOUNTS[source_account]["balance"] < amount:
        return {"error": "Insufficient funds in source account."}

    ACCOUNTS[source_account]["balance"] = round(ACCOUNTS[source_account]["balance"] - amount, 2)
    ACCOUNTS[destination_account]["balance"] = round(ACCOUNTS[destination_account]["balance"] + amount, 2)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    TRANSACTIONS[source_account].insert(
        0, {"date": timestamp, "type": "DEBIT", "amount": -amount, "description": f"To {destination_account}: {description}"}
    )
    TRANSACTIONS[destination_account].insert(
        0, {"date": timestamp, "type": "CREDIT", "amount": amount, "description": f"From {source_account}: {description}"}
    )

    return {
        "status": "COMPLETED",
        "timestamp": timestamp,
        "source_account": source_account,
        "new_source_balance": ACCOUNTS[source_account]["balance"],
        "destination_account": destination_account,
        "transferred_amount": amount,
        "description": description,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
