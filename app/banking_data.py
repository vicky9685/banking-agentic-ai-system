# Mock Database Layer for ApexBank AI Co-Pilot

CUSTOMER_PROFILES = {
    "CUST_8042": {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne.io",
        "account_number": "ACT-9082-1102",
        "checking_balance": 14250.75,
        "savings_balance": 85000.00,
        "credit_score": 782,
        "risk_profile": "Growth-Oriented",
        "monthly_income": 8200.00,
        "monthly_expenses": 3400.00,
        "active_loans": [
            {"loan_id": "LN-2041", "type": "Auto Loan", "amount": 25000.00, "balance": 12400.00, "rate": 4.2}
        ],
        "credit_cards": [
            {"card_id": "CC-9011", "type": "Aegis Infinite", "limit": 20000.00, "balance": 1820.50}
        ]
    },
    "CUST_4011": {
        "name": "Bruce Wayne",
        "email": "bruce@waynecorp.com",
        "account_number": "ACT-1001-9999",
        "checking_balance": 18450000.00,
        "savings_balance": 95000000.00,
        "credit_score": 845,
        "risk_profile": "Aggressive / Venture",
        "monthly_income": 1250000.00,
        "monthly_expenses": 450000.00,
        "active_loans": [],
        "credit_cards": [
            {"card_id": "CC-0007", "type": "Gotham Black Elite", "limit": 10000000.00, "balance": 342000.00}
        ]
    }
}

TRANSACTIONS = {
    "CUST_8042": [
        {"id": "TXN_101", "date": "2026-05-28", "merchant": "Starbucks Coffee", "amount": 7.82, "category": "Food/Dining", "status": "Settled", "location": "Los Angeles, CA"},
        {"id": "TXN_102", "date": "2026-05-29", "merchant": "Chevron Gas Station", "amount": 45.00, "category": "Automotive", "status": "Settled", "location": "Pasadena, CA"},
        {"id": "TXN_103", "date": "2026-05-30", "merchant": "Amazon.com (Online)", "amount": 124.99, "category": "Shopping", "status": "Settled", "location": "Online"},
        # Anomalous fraud-trigger txn (Same day as Pasadena, CA but executed in Bucharest, Romania)
        {"id": "TXN_104", "date": "2026-05-30", "merchant": "Luxury Watch Emporium", "amount": 4200.00, "category": "Shopping", "status": "Pending", "location": "Bucharest, Romania", "flagged": True},
        {"id": "TXN_105", "date": "2026-05-31", "merchant": "Target Store", "amount": 89.20, "category": "Groceries", "status": "Settled", "location": "Los Angeles, CA"}
    ],
    "CUST_4011": [
        {"id": "TXN_201", "date": "2026-05-28", "merchant": "Wayne Enterprises Flight Services", "amount": 85000.00, "category": "Travel", "status": "Settled", "location": "Gotham City"},
        {"id": "TXN_202", "date": "2026-05-29", "merchant": "Fine Art Auction House", "amount": 1250000.00, "category": "Art", "status": "Settled", "location": "Paris, France"},
        # Flagged transaction: unusual high-frequency micropayments
        {"id": "TXN_203", "date": "2026-05-30", "merchant": "CryptoExchange.io", "amount": 25000.00, "category": "Finance", "status": "Pending", "location": "Valletta, Malta", "flagged": True}
    ]
}

DISPUTES = [
    {
        "dispute_id": "DISP_501",
        "customer_id": "CUST_8042",
        "txn_id": "TXN_104",
        "merchant": "Luxury Watch Emporium",
        "amount": 4200.00,
        "date_filed": "2026-05-31",
        "user_reason": "I did not authorize this charge. I was in Los Angeles, California on May 30th shopping on Amazon, and my card was physically in my possession.",
        "status": "Under Review"
    }
]

BANK_RATES = {
    "hysa": {
        "name": "Apex Shield High-Yield Savings",
        "apy": 4.85,
        "minimum_deposit": 1000.00,
        "fees": "Zero monthly maintenance fees"
    },
    "mortgage": {
        "30_year_fixed": 5.99,
        "15_year_fixed": 5.25,
        "5_1_arm": 5.65
    },
    "certificates_of_deposit": {
        "6_month": 5.10,
        "12_month": 4.95,
        "24_month": 4.70
    }
}

POLICIES = """
1. FRAUD DISPUTE POLICY:
   - Customers must file disputes within 60 days of the transaction statement date.
   - Any transaction marked as "flagged" due to simultaneous geolocations (e.g., card physical use in LA and Romania within 2 hours) should be fast-tracked for provisional credit and card freeze.
   
2. LOAN ELIGIBILITY POLICY:
   - Minimum credit score for personal/auto loan: 620. For mortgage: 640.
   - Debt-to-Income (DTI) ratio must not exceed 43%. DTI = (Monthly Debt Commitments + Proposed Loan Payment) / Monthly Income.
   - Max loan amount is capped at 5x the customer's annual income.

3. INVESTMENT STRATEGY SUITABILITY:
   - Growth-Oriented: Recommend 80% equities, 20% fixed income (HYSA, Bonds).
   - Conservative: Recommend 30% equities, 70% fixed income / CDs.
   - Aggressive: Recommend 95% equities, 5% alternative assets (Venture, Crypto).
"""
