# AI Multi-Agent Core Engine for ApexBank AI Co-Pilot
import os
import time
import json
from .banking_data import CUSTOMER_PROFILES, TRANSACTIONS, DISPUTES, BANK_RATES, POLICIES

# Check for Gemini API key and try to import official SDK
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        GEMINI_AVAILABLE = True
except ImportError:
    pass

class AgentResponse:
    def __init__(self, agent_name: str, thought: str, action: str, response: str):
        self.agent_name = agent_name
        self.thought = thought
        self.action = action
        self.response = response

    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "thought": self.thought,
            "action": self.action,
            "response": self.response
        }

# ==========================================
# Specialist Agents Monologue & Mock Logic
# ==========================================

def run_live_gemini(system_prompt: str, user_prompt: str) -> str:
    """Helper to query the Gemini API directly."""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        return f"Error executing Gemini live API: {str(e)}"

# 1. WEALTH ADVISOR AGENT
SYSTEM_WEALTH = f"""You are the ApexBank Wealth Advisor Agent.
You analyze customer financial profiles (checking/savings balances, DTI, monthly cashflow, active loans) and policies to provide tailored financial planning, budgeting strategies, and suitable asset allocation.
Adhere strictly to SUITABILITY policies:
{POLICIES}
Format responses professionally with clear financial recommendations, projections, or budget targets."""

def run_wealth_advisor(customer_id: str, query: str) -> AgentResponse:
    profile = CUSTOMER_PROFILES.get(customer_id)
    if not profile:
        return AgentResponse(
            "Wealth Advisor Agent",
            "Customer ID not found in database. Aborting audit.",
            "Lookup customer profile",
            "Error: Customer record not found."
        )

    thought = (
        f"Analyzing customer profile for {profile['name']} ({customer_id}). "
        f"Balances: Checking = ${profile['checking_balance']:,}, Savings = ${profile['savings_balance']:,}. "
        f"Risk Profile: {profile['risk_profile']}. "
        f"Analyzing suitability and cashflow options for the query: '{query}'."
    )
    action = f"Calculate asset allocation based on {profile['risk_profile']} profile."

    if GEMINI_AVAILABLE:
        user_prompt = f"Customer Profile:\n{json.dumps(profile, indent=2)}\n\nQuery:\n{query}"
        response_text = run_live_gemini(SYSTEM_WEALTH, user_prompt)
    else:
        # Dry-run simulation mode
        if profile["risk_profile"] == "Growth-Oriented":
            response_text = (
                f"### Personalized Portfolio Proposal for **{profile['name']}**\n\n"
                f"Based on your **{profile['risk_profile']}** risk profile, your total assets of "
                f"**${profile['checking_balance'] + profile['savings_balance']:,}** are highly suitable for a growth strategy.\n\n"
                f"#### Recommended Asset Allocation:\n"
                f"- **80% Equities / Growth Funds:** ($80,000) target allocation into diversified ETFs.\n"
                f"- **20% Cash / HYSA:** ($20,000) target allocation in our *Apex Shield HYSA* (currently earning a highly competitive **4.85% APY**).\n\n"
                f"#### Strategic Action Plan:\n"
                f"1. **Emergency Reserve:** Keep $15,000 in your checking/savings as liquid cash.\n"
                f"2. **Excess Capital Deployment:** We recommend setting up an automatic monthly transfer of **$1,500** from checking into our Growth Funds to dollar-cost average into the market.\n"
                f"3. **Debt Optimization:** Your auto loan (LN-2041) at **4.2%** is reasonably priced; it is more mathematically sound to invest excess cash rather than aggressively paying off this low-interest debt."
            )
        elif profile["risk_profile"] == "Aggressive / Venture":
            response_text = (
                f"### Ultra-High-Net-Worth Portfolio Proposal for **{profile['name']}**\n\n"
                f"Based on your **{profile['risk_profile']}** profile and substantial liquidity "
                f"(${profile['savings_balance'] + profile['checking_balance']:,}), we recommend a tactical alternative allocation.\n\n"
                f"#### Recommended Asset Allocation:\n"
                f"- **95% High-Beta Equities / Tech Ventures:** ($107,777,500) deployed into Wayne Corp private shares and global equities.\n"
                f"- **5% Alternative Asset Hedge:** ($5,672,500) in digital assets or real estate.\n\n"
                f"#### Strategic Cashflow Actions:\n"
                f"- **Liquidity Pools:** Transition $10,000,000 into institutional yield accounts to capture interest while retaining transactional flexibility.\n"
                f"- **Venture Capital Allocation:** Leverage current Wayne Ventures funds to access early-stage deeptech opportunities."
            )
        else:
            response_text = "Suitability review complete. Profile indicates a standard conservative allocation."

    return AgentResponse("Wealth Advisor Agent", thought, action, response_text)


# 2. FRAUD & AUDIT SPECIALIST
SYSTEM_FRAUD = f"""You are the ApexBank Fraud & Audit Specialist Agent.
You review customer transaction lists to audit security, flag geographical/velocity anomalies, double-charge events, or suspicious merchant behavior.
Use the policies defined here:
{POLICIES}
Explain precisely why a transaction was flagged, audit the security factors, and propose safe resolution paths."""

def run_fraud_auditor(customer_id: str, query: str) -> AgentResponse:
    profile = CUSTOMER_PROFILES.get(customer_id)
    txns = TRANSACTIONS.get(customer_id, [])
    
    thought = (
        f"Retrieving recent transactions for {customer_id}. "
        f"Scanning {len(txns)} transactions for anomalous signals, velocity checks, and geo-discrepancies."
    )
    action = "Search transaction list for geolocational velocity issues and flagged states."

    flagged_txns = [t for t in txns if t.get("flagged")]
    
    if GEMINI_AVAILABLE:
        user_prompt = f"Customer Profile:\n{json.dumps(profile, indent=2)}\n\nTransactions:\n{json.dumps(txns, indent=2)}\n\nQuery:\n{query}"
        response_text = run_live_gemini(SYSTEM_FRAUD, user_prompt)
    else:
        # Dry-run simulation mode
        if flagged_txns:
            ft = flagged_txns[0]
            response_text = (
                f"### 🛡️ Transaction Security Audit Report\n\n"
                f"**System Flag Triggered:** **Velocity/Geographic Anomaly Detected**\n\n"
                f"Our systems have flagged transaction **{ft['id']}** at **{ft['merchant']}** (${ft['amount']:,}) "
                f"originating from **{ft['location']}** on **{ft['date']}**.\n\n"
                f"#### 🔍 Why was this flagged?\n"
                f"- **Geographical Velocity Anomaly:** On the same day, you made a physical purchase at Target or Chevron in **Los Angeles, CA**. It is physically impossible to execute an in-person transaction in **Bucharest, Romania** within that timeframe.\n"
                f"- **Category Deviation:** A high-value purchase of **${ft['amount']:,}** deviates significantly from your standard grocery/dining transaction envelope.\n\n"
                f"#### 🛡️ Required Security Actions:\n"
                f"1. **Provisional Hold:** The transaction is currently marked as **Pending** and funds have been frozen to prevent settlement.\n"
                f"2. **Card Lock:** We recommend freezing your active credit card (**CC-9011**) immediately through your dashboard.\n"
                f"3. **Re-issuance:** A new card will be dispatched via express shipping. No fraud liabilities will be incurred."
            )
        else:
            response_text = "### 🛡️ Transaction Security Audit Report\n\nAll audited transactions are within standard operational parameters. No fraud indicators detected."

    return AgentResponse("Fraud & Audit Agent", thought, action, response_text)


# 3. DISPUTE SPECIALIST
SYSTEM_DISPUTE = f"""You are the ApexBank Dispute Specialist Agent.
You process official customer card disputes. You review the date filed, amount, customer claim statement, and verify against standard bank guidelines:
{POLICIES}
Formulate a formal resolution decision (Approve provisional credit, Deny, request documentation) and provide clear reasoning."""

def run_dispute_specialist(customer_id: str, query: str) -> AgentResponse:
    disputes = [d for d in DISPUTES if d["customer_id"] == customer_id]
    thought = f"Locating filed disputes for {customer_id}. Processing merchant chargeback claims against dispute policies."
    action = "Check policies on fast-tracking geo-anomalous pending claims."

    if GEMINI_AVAILABLE:
        user_prompt = f"Customer Disputes:\n{json.dumps(disputes, indent=2)}\n\nQuery:\n{query}"
        response_text = run_live_gemini(SYSTEM_DISPUTE, user_prompt)
    else:
        if disputes:
            disp = disputes[0]
            response_text = (
                f"### ⚖️ Formal Dispute Resolution Case: **{disp['dispute_id']}**\n\n"
                f"**Disputed Transaction:** {disp['merchant']} (${disp['amount']:,})\n"
                f"**Status:** **Approved (Provisional Credit Issued)**\n\n"
                f"#### 📝 Case Assessment:\n"
                f"- **Timeliness Check:** Dispute filed on **{disp['date_filed']}** for a transaction on **2026-05-30**. This easily satisfies the mandatory **60-day filing window**.\n"
                f"- **Evidence Review:** Customer claims physical card possession in Los Angeles while transaction was routed in Romania. The concurrent transaction logs in Pasadena, CA validate the impossibility of customer physical presence at the foreign location.\n\n"
                f"#### ⚖️ Final Decision & Actions:\n"
                f"1. **Provisional Credit:** A credit of **${disp['amount']:,}** has been applied to your credit card account, neutralizing the charge.\n"
                f"2. **Chargeback Initiated:** We have initiated a formal dispute recovery file against the merchant's acquiring bank."
            )
        else:
            response_text = "### case status\n\nNo active disputes filed for this customer. If you wish to file a dispute, select a flagged transaction from your history panel."

    return AgentResponse("Dispute Analyst Agent", thought, action, response_text)


# 4. SUPPORT & RATES SPECIALIST
SYSTEM_SUPPORT = f"""You are the ApexBank Support & Rates Specialist Agent.
You answer FAQs, explain products, details account minimums, fees, and current rates:
{BANK_RATES}
Provide courteous, helpful answers with structured comparisons or calculations."""

def run_support_specialist(customer_id: str, query: str) -> AgentResponse:
    thought = f"Processing customer FAQ regarding current product terms and deposit minimums for: '{query}'."
    action = "Fetch current deposit product rates from banking rate sheets."

    if GEMINI_AVAILABLE:
        user_prompt = f"Bank Rates Sheet:\n{json.dumps(BANK_RATES, indent=2)}\n\nQuery:\n{query}"
        response_text = run_live_gemini(SYSTEM_SUPPORT, user_prompt)
    else:
        response_text = (
            f"### 🏦 ApexBank Product & Current Rates Sheet\n\n"
            f"Thank you for inquiring about our modern savings and credit products! Here is a summary of our top yields:\n\n"
            f"#### 📈 Savings Accounts\n"
            f"- **{BANK_RATES['hysa']['name']}**\n"
            f"  - **APY:** **{BANK_RATES['hysa']['apy']}%**\n"
            f"  - **Minimum Opening Balance:** ${BANK_RATES['hysa']['minimum_deposit']:,}\n"
            f"  - **Fees:** {BANK_RATES['hysa']['fees']}\n\n"
            f"#### 📅 Certificates of Deposit (CDs)\n"
            f"- **6-Month Fixed Term:** **{BANK_RATES['certificates_of_deposit']['6_month']}% APY**\n"
            f"- **12-Month Fixed Term:** **{BANK_RATES['certificates_of_deposit']['12_month']}% APY**\n"
            f"- **24-Month Fixed Term:** **{BANK_RATES['certificates_of_deposit']['24_month']}% APY**\n\n"
            f"#### 🏠 Home Mortgages\n"
            f"- **15-Year Fixed:** **{BANK_RATES['mortgage']['15_year_fixed']}% Interest Rate**\n"
            f"- **30-Year Fixed:** **{BANK_RATES['mortgage']['30_year_fixed']}% Interest Rate**\n\n"
            f"Would you like me to help you pre-calculate your interest yield based on a specific initial deposit?"
        )

    return AgentResponse("Support Specialist Agent", thought, action, response_text)


# ==========================================
# Coordinator & Router Agent
# ==========================================

SYSTEM_COORDINATOR = """You are the ApexBank Aegis Coordinator & Router Agent.
Your job is to orchestrate a team of specialized banking AI agents.
Given a user query and a customer profile, you determine which specialist agent is the most appropriate to handle the request.
Specialists:
1. "wealth": Wealth Advisor (advisory, investments, budgeting, savings suitability).
2. "fraud": Fraud & Audit Specialist (suspicious activities, geographic velocity checks, transaction verification).
3. "dispute": Dispute Specialist (chargebacks, provisional credit, policy compliance).
4. "support": Support & Rates Specialist (FAQ, savings yields, CD rates, mortgage percentages).

You must write a final, beautifully synthesized summary integrating the specialized agents' reports. Always present a unified front to the customer."""

def coordinate_agents(customer_id: str, query: str) -> dict:
    """Orchestrator that routes, executes, and synthesizes multi-agent conversations."""
    profile = CUSTOMER_PROFILES.get(customer_id)
    if not profile:
        return {
            "synthesized_response": "Error: Customer record not found.",
            "thought_logs": []
        }

    # 1. Routing Decision
    lower_query = query.lower()
    routes = []
    
    # Simple routing heuristic (fallback or guide for LLM)
    if any(k in lower_query for k in ["invest", "portfolio", "budget", "allocation", "planning", "wealth"]):
        routes.append("wealth")
    if any(k in lower_query for k in ["fraud", "suspicious", "flagged", "security", "anomalous"]):
        routes.append("fraud")
    if any(k in lower_query for k in ["dispute", "chargeback", "charge dispute", "refund"]):
        routes.append("dispute")
    if any(k in lower_query for k in ["rate", "apy", "hysa", "cd", "mortgage", "fee", "faq"]):
        routes.append("support")

    # If no specific route matched, default to general support + routing
    if not routes:
        routes = ["support"]

    thought_logs = []
    
    # 2. Execution phase: Invoke selected specialists
    specialist_reports = {}
    for r in routes:
        if r == "wealth":
            res = run_wealth_advisor(customer_id, query)
            specialist_reports["wealth"] = res.response
            thought_logs.append(res.to_dict())
        elif r == "fraud":
            res = run_fraud_auditor(customer_id, query)
            specialist_reports["fraud"] = res.response
            thought_logs.append(res.to_dict())
        elif r == "dispute":
            res = run_dispute_specialist(customer_id, query)
            specialist_reports["dispute"] = res.response
            thought_logs.append(res.to_dict())
        elif r == "support":
            res = run_support_specialist(customer_id, query)
            specialist_reports["support"] = res.response
            thought_logs.append(res.to_dict())

    # 3. Compilation/Synthesis
    coordinator_thought = f"Synthesizing results from specialists: {', '.join(routes)} into a unified presentation."
    coordinator_action = "Synthesize final response report for user."
    
    if GEMINI_AVAILABLE:
        user_prompt = f"Customer Profile:\n{json.dumps(profile, indent=2)}\n\nSpecialist Reports:\n{json.dumps(specialist_reports, indent=2)}\n\nQuery:\n{query}"
        synthesized_response = run_live_gemini(SYSTEM_COORDINATOR, user_prompt)
    else:
        # Dry-run compilation logic
        synthesized_response = "### 🏦 ApexBank AI Co-Pilot Unified Report\n\n"
        if "fraud" in routes:
            synthesized_response += (
                f"Hello {profile['name']},\n\n"
                f"We detected a critical security alert regarding transaction **TXN_104** at **Luxury Watch Emporium** ($4,200.00).\n\n"
                f"Our **Fraud & Audit Team** confirmed that this transaction constitutes an geolocational impossibility based on your activity in Pasadena, CA. "
                f"As a result, your card has been temporarily locked to prevent further issues, and a new one is being dispatched.\n\n"
            )
        if "dispute" in routes:
            synthesized_response += (
                f"#### ⚖️ Card Dispute Resolution:\n"
                f"Our **Dispute Specialist** has fast-tracked Case **DISP_501**. A **provisional credit of $4,200.00** has already been applied "
                f"to your credit balance so you will not carry any liability while our recovery teams proceed.\n\n"
            )
        if "wealth" in routes:
            synthesized_response += (
                f"#### 📈 Wealth Management & Growth Options:\n"
                f"Additionally, based on your active cache of checking/savings assets, our **Wealth Advisor** recommends optimizing your yield: "
                f"keeping $15,000 for emergency purposes and sweeping extra cash flow into standard ETFs (80%) and our top-tier **4.85% APY** HYSA (20%).\n\n"
            )
        if "support" in routes and len(routes) == 1:
            synthesized_response += (
                f"Hello {profile['name']},\n\n"
                f"I've fetched the latest savings and credit rates for your review:\n\n"
                f"{specialist_reports['support']}\n\n"
                f"Please let me know if you would like me to pre-calculate interest gains on a specific balance!"
            )
            
        synthesized_response += "\n\nIs there anything else our multi-agent team can assist you with today?"

    coordinator_log = AgentResponse("Aegis Coordinator & Router", coordinator_thought, coordinator_action, synthesized_response)
    thought_logs.insert(0, coordinator_log.to_dict())

    return {
        "synthesized_response": synthesized_response,
        "thought_logs": thought_logs
    }
