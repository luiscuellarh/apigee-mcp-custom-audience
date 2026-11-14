import os
import uuid
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

# Initialize stateless Streamable HTTP MCP Server for Cloud Run
mcp = FastMCP(
    "SimpleBank-MCP",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8080)),
    stateless_http=True,
    json_response=True,
)

# ==============================================================================
# Mock Banking Data (In-Memory, Easy to Understand & Test)
# ==============================================================================

CUSTOMERS = {
    "CUST-101": {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "segment": "Premier Banking",
        "credit_score": 785,
        "kyc_status": "VERIFIED",
    },
    "CUST-102": {
        "name": "Carlos Ruiz",
        "email": "carlos.ruiz@example.com",
        "segment": "Personal Banking",
        "credit_score": 720,
        "kyc_status": "VERIFIED",
    },
    "CUST-103": {
        "name": "Emma Smith",
        "email": "emma.smith@acme-corp.example.com",
        "segment": "Business Banking",
        "credit_score": 810,
        "kyc_status": "VERIFIED",
    },
}

ACCOUNTS = {
    "ACC-001": {
        "customer_id": "CUST-101",
        "holder": "Alice Johnson",
        "type": "CHECKING",
        "iban": "GB29NWBK60161331926819",
        "balance": 15400.50,
        "currency": "USD",
        "status": "ACTIVE",
    },
    "ACC-002": {
        "customer_id": "CUST-101",
        "holder": "Alice Johnson",
        "type": "HIGH_YIELD_SAVINGS",
        "iban": "GB29NWBK60161331926820",
        "balance": 48000.00,
        "currency": "USD",
        "status": "ACTIVE",
    },
    "ACC-003": {
        "customer_id": "CUST-102",
        "holder": "Carlos Ruiz",
        "type": "CHECKING",
        "iban": "GB29NWBK60161331926821",
        "balance": 3200.00,
        "currency": "USD",
        "status": "ACTIVE",
    },
    "ACC-004": {
        "customer_id": "CUST-103",
        "holder": "Emma Smith (Acme Corp)",
        "type": "BUSINESS_CHECKING",
        "iban": "GB29NWBK60161331926822",
        "balance": 125000.00,
        "currency": "USD",
        "status": "ACTIVE",
    },
}

TRANSACTIONS = {
    "ACC-001": [
        {
            "tx_id": "TX-9001",
            "date": "2026-11-12",
            "type": "DEBIT",
            "category": "Dining",
            "merchant": "Blue Bottle Coffee",
            "amount": -14.75,
            "description": "Morning coffee & pastry",
        },
        {
            "tx_id": "TX-9002",
            "date": "2026-11-11",
            "type": "DEBIT",
            "category": "Utilities",
            "merchant": "City Power & Light",
            "amount": -120.50,
            "description": "Monthly Electricity Bill",
        },
        {
            "tx_id": "TX-9003",
            "date": "2026-11-10",
            "type": "CREDIT",
            "category": "Payroll",
            "merchant": "TechCorp Inc.",
            "amount": 4200.00,
            "description": "Bi-weekly Salary Deposit",
        },
        {
            "tx_id": "TX-9004",
            "date": "2026-11-08",
            "type": "DEBIT",
            "category": "Shopping",
            "merchant": "Amazon Marketplace",
            "amount": -89.99,
            "description": "Wireless Headphones",
        },
    ],
    "ACC-002": [
        {
            "tx_id": "TX-9005",
            "date": "2026-11-01",
            "type": "CREDIT",
            "category": "Interest",
            "merchant": "SimpleBank Savings",
            "amount": 165.00,
            "description": "Monthly APY Interest Payout (4.25%)",
        },
    ],
    "ACC-003": [
        {
            "tx_id": "TX-9006",
            "date": "2026-11-09",
            "type": "CREDIT",
            "category": "Transfer",
            "merchant": "External Bank Transfer",
            "amount": 500.00,
            "description": "Initial Account Funding",
        },
        {
            "tx_id": "TX-9007",
            "date": "2026-11-11",
            "type": "DEBIT",
            "category": "Transport",
            "merchant": "Uber Trip",
            "amount": -28.40,
            "description": "Airport ride",
        },
    ],
    "ACC-004": [
        {
            "tx_id": "TX-9008",
            "date": "2026-11-12",
            "type": "CREDIT",
            "category": "Invoice",
            "merchant": "Global Logistics Ltd.",
            "amount": 18500.00,
            "description": "Invoice #INV-2026-88 Settlement",
        },
    ],
}

CARDS = {
    "CARD-4501": {
        "customer_id": "CUST-101",
        "account_id": "ACC-001",
        "holder": "Alice Johnson",
        "type": "VISA_INFINITE_CREDIT",
        "masked_number": "****-****-****-4501",
        "status": "ACTIVE",
        "credit_limit": 25000.00,
        "current_balance": 1420.30,
        "available_credit": 23579.70,
    },
    "CARD-8820": {
        "customer_id": "CUST-101",
        "account_id": "ACC-001",
        "holder": "Alice Johnson",
        "type": "VISA_DEBIT",
        "masked_number": "****-****-****-8820",
        "status": "ACTIVE",
        "daily_limit": 3000.00,
    },
    "CARD-9912": {
        "customer_id": "CUST-102",
        "account_id": "ACC-003",
        "holder": "Carlos Ruiz",
        "type": "MASTERCARD_GOLD_CREDIT",
        "masked_number": "****-****-****-9912",
        "status": "FROZEN",
        "credit_limit": 8000.00,
        "current_balance": 650.00,
        "available_credit": 7350.00,
    },
}

BILLERS = {
    "BILL-ELECTRIC": {"name": "City Power & Light", "category": "Electricity"},
    "BILL-INTERNET": {"name": "FiberNet Gigabit ISP", "category": "Telecommunications"},
    "BILL-WATER": {"name": "Metro Water Authority", "category": "Water & Sewer"},
    "BILL-CLOUD": {"name": "Google Cloud Platform", "category": "Cloud Infrastructure"},
}

LOAN_PRODUCTS = {
    "PERSONAL": {"name": "Personal Unsecured Loan", "annual_rate_pct": 8.9, "min_months": 6, "max_months": 60},
    "AUTO": {"name": "Green Vehicle Auto Loan", "annual_rate_pct": 5.4, "min_months": 12, "max_months": 84},
    "MORTGAGE": {"name": "Fixed-Rate Home Mortgage", "annual_rate_pct": 6.2, "min_months": 60, "max_months": 360},
}

# Precomputed O(1) secondary indexes by customer_id
CUSTOMER_ACCOUNTS: dict[str, list[str]] = {}
for _acc_id, _acc in ACCOUNTS.items():
    CUSTOMER_ACCOUNTS.setdefault(_acc["customer_id"], []).append(_acc_id)

CUSTOMER_CARDS: dict[str, list[str]] = {}
for _card_id, _card in CARDS.items():
    CUSTOMER_CARDS.setdefault(_card["customer_id"], []).append(_card_id)


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


# ==============================================================================
# Async MCP Banking Tools (Zero Thread-Pool Overhead on Uvicorn Event Loop)
# ==============================================================================


@mcp.tool()
async def get_customer_profile(customer_id: str) -> dict:
    """Retrieve a customer's profile, banking tier, KYC status, and linked accounts (e.g., CUST-101, CUST-102, CUST-103)."""
    cid = customer_id.strip().upper()
    customer = CUSTOMERS.get(cid)
    if not customer:
        return {"error": f"Customer '{customer_id}' not found. Valid IDs: {', '.join(CUSTOMERS.keys())}"}
    linked_accounts = [
        {
            "account_id": acc_id,
            "type": ACCOUNTS[acc_id]["type"],
            "balance": ACCOUNTS[acc_id]["balance"],
            "currency": ACCOUNTS[acc_id]["currency"],
        }
        for acc_id in CUSTOMER_ACCOUNTS.get(cid, [])
    ]
    return {"customer_id": cid, **customer, "accounts": linked_accounts}


@mcp.tool()
async def list_accounts(customer_id: str = "") -> dict:
    """List all bank accounts, optionally filtered by customer_id (e.g., CUST-101)."""
    cid = customer_id.strip().upper()
    if cid:
        acc_ids = CUSTOMER_ACCOUNTS.get(cid, [])
        results = [{"account_id": acc_id, **ACCOUNTS[acc_id]} for acc_id in acc_ids]
    else:
        results = [{"account_id": acc_id, **acc} for acc_id, acc in ACCOUNTS.items()]
    return {"total_accounts": len(results), "accounts": results}


@mcp.tool()
async def get_account_balance(account_id: str) -> dict:
    """Retrieve the available balance and details for a specific bank account (e.g., ACC-001, ACC-002, ACC-003, ACC-004)."""
    acc_key = account_id.strip().upper()
    account = ACCOUNTS.get(acc_key)
    if not account:
        return {"error": f"Account '{account_id}' not found. Valid IDs: {', '.join(ACCOUNTS.keys())}"}
    return {"account_id": acc_key, **account}


@mcp.tool()
async def list_transactions(account_id: str, limit: int = 5, category: str = "") -> dict:
    """List recent transactions for a bank account (ACC-001..ACC-004), optionally filtered by category (e.g., Dining, Utilities, Payroll)."""
    acc_key = account_id.strip().upper()
    if acc_key not in ACCOUNTS:
        return {"error": f"Account '{account_id}' not found. Valid IDs: {', '.join(ACCOUNTS.keys())}"}
    safe_limit = max(1, min(limit, 100))
    tx_list = TRANSACTIONS.get(acc_key, [])
    cat_filter = category.strip().lower()
    if cat_filter:
        tx_list = [tx for tx in tx_list if tx.get("category", "").lower() == cat_filter]
    return {
        "account_id": acc_key,
        "holder": ACCOUNTS[acc_key]["holder"],
        "current_balance": ACCOUNTS[acc_key]["balance"],
        "transactions": tx_list[:safe_limit],
    }


@mcp.tool()
async def transfer_funds(
    source_account: str,
    destination_account: str,
    amount: float,
    description: str = "Internal bank transfer",
) -> dict:
    """Transfer money between two bank accounts (e.g., from ACC-001 to ACC-003)."""
    src = source_account.strip().upper()
    dst = destination_account.strip().upper()
    if src not in ACCOUNTS or dst not in ACCOUNTS:
        return {"error": f"Invalid source or destination account. Valid IDs: {', '.join(ACCOUNTS.keys())}"}
    if src == dst:
        return {"error": "Source and destination accounts must be different."}
    if amount <= 0:
        return {"error": "Transfer amount must be greater than zero."}
    if ACCOUNTS[src]["balance"] < amount:
        return {"error": f"Insufficient funds in {src} (Available: {ACCOUNTS[src]['balance']} USD)."}

    ACCOUNTS[src]["balance"] = round(ACCOUNTS[src]["balance"] - amount, 2)
    ACCOUNTS[dst]["balance"] = round(ACCOUNTS[dst]["balance"] + amount, 2)

    timestamp = _utc_now_str()
    tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
    TRANSACTIONS.setdefault(src, []).insert(
        0,
        {
            "tx_id": f"{tx_id}-D",
            "date": timestamp,
            "type": "DEBIT",
            "category": "Transfer",
            "merchant": ACCOUNTS[dst]["holder"],
            "amount": -amount,
            "description": f"Transfer to {dst}: {description}",
        },
    )
    TRANSACTIONS.setdefault(dst, []).insert(
        0,
        {
            "tx_id": f"{tx_id}-C",
            "date": timestamp,
            "type": "CREDIT",
            "category": "Transfer",
            "merchant": ACCOUNTS[src]["holder"],
            "amount": amount,
            "description": f"Transfer from {src}: {description}",
        },
    )

    return {
        "status": "COMPLETED",
        "transaction_id": tx_id,
        "timestamp": timestamp,
        "source_account": src,
        "new_source_balance": ACCOUNTS[src]["balance"],
        "destination_account": dst,
        "new_destination_balance": ACCOUNTS[dst]["balance"],
        "transferred_amount": amount,
        "currency": "USD",
        "description": description,
    }


@mcp.tool()
async def list_cards(customer_id: str = "") -> dict:
    """List debit and credit cards, optionally filtered by customer_id (e.g., CUST-101, CUST-102)."""
    cid = customer_id.strip().upper()
    if cid:
        card_ids = CUSTOMER_CARDS.get(cid, [])
        cards = [{"card_id": card_id, **CARDS[card_id]} for card_id in card_ids]
    else:
        cards = [{"card_id": card_id, **card} for card_id, card in CARDS.items()]
    return {"total_cards": len(cards), "cards": cards}


@mcp.tool()
async def toggle_card_lock(card_id: str, action: str = "FREEZE") -> dict:
    """Freeze or unfreeze a credit/debit card (card_id: CARD-4501, CARD-8820, CARD-9912; action: FREEZE or UNFREEZE)."""
    cid = card_id.strip().upper()
    act = action.strip().upper()
    if cid not in CARDS:
        return {"error": f"Card '{card_id}' not found. Valid IDs: {', '.join(CARDS.keys())}"}
    if act not in ("FREEZE", "UNFREEZE"):
        return {"error": "Invalid action. Use 'FREEZE' or 'UNFREEZE'."}

    new_status = "FROZEN" if act == "FREEZE" else "ACTIVE"
    CARDS[cid]["status"] = new_status
    return {
        "card_id": cid,
        "masked_number": CARDS[cid]["masked_number"],
        "holder": CARDS[cid]["holder"],
        "previous_action": act,
        "new_status": new_status,
        "updated_at": _utc_now_str(),
    }


@mcp.tool()
async def pay_utility_bill(account_id: str, biller_id: str, amount: float, invoice_ref: str = "INV-2026") -> dict:
    """Pay a registered utility or service biller (biller_id: BILL-ELECTRIC, BILL-INTERNET, BILL-WATER, BILL-CLOUD) from a bank account."""
    acc = account_id.strip().upper()
    bil = biller_id.strip().upper()
    if acc not in ACCOUNTS:
        return {"error": f"Account '{account_id}' not found. Valid IDs: {', '.join(ACCOUNTS.keys())}"}
    if bil not in BILLERS:
        return {"error": f"Biller '{biller_id}' not found. Valid billers: {', '.join(BILLERS.keys())}"}
    if amount <= 0:
        return {"error": "Payment amount must be greater than zero."}
    if ACCOUNTS[acc]["balance"] < amount:
        return {"error": f"Insufficient funds in {acc}."}

    ACCOUNTS[acc]["balance"] = round(ACCOUNTS[acc]["balance"] - amount, 2)
    biller = BILLERS[bil]
    timestamp = _utc_now_str()
    payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"

    TRANSACTIONS.setdefault(acc, []).insert(
        0,
        {
            "tx_id": payment_id,
            "date": timestamp,
            "type": "DEBIT",
            "category": biller["category"],
            "merchant": biller["name"],
            "amount": -amount,
            "description": f"Bill Payment ({invoice_ref})",
        },
    )

    return {
        "status": "PAID",
        "payment_id": payment_id,
        "timestamp": timestamp,
        "account_id": acc,
        "remaining_balance": ACCOUNTS[acc]["balance"],
        "biller_id": bil,
        "biller_name": biller["name"],
        "amount_paid": amount,
        "invoice_ref": invoice_ref,
    }


@mcp.tool()
async def simulate_loan(loan_type: str = "PERSONAL", principal_amount: float = 10000.0, term_months: int = 24) -> dict:
    """Simulate monthly payments and total interest for a loan (loan_type: PERSONAL, AUTO, MORTGAGE)."""
    ltype = loan_type.strip().upper()
    if ltype not in LOAN_PRODUCTS:
        return {"error": f"Unknown loan_type '{loan_type}'. Valid types: {', '.join(LOAN_PRODUCTS.keys())}"}
    product = LOAN_PRODUCTS[ltype]
    if principal_amount <= 0:
        return {"error": "principal_amount must be greater than zero."}
    if not (product["min_months"] <= term_months <= product["max_months"]):
        return {
            "error": f"term_months for {ltype} must be between {product['min_months']} and {product['max_months']} months."
        }

    monthly_rate = (product["annual_rate_pct"] / 100.0) / 12.0
    monthly_payment = principal_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / (
        (1 + monthly_rate) ** term_months - 1
    )
    total_payment = monthly_payment * term_months
    total_interest = total_payment - principal_amount

    return {
        "loan_type": ltype,
        "product_name": product["name"],
        "principal_amount": round(principal_amount, 2),
        "term_months": term_months,
        "annual_apr_pct": product["annual_rate_pct"],
        "estimated_monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_payment, 2),
        "currency": "USD",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
