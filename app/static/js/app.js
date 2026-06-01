// JavaScript Controller for ApexBank AI Co-Pilot Dashboard

let activeCustomerId = "CUST_8042"; // Default Active Profile
let currentProfileData = null;
let activeAgentLogs = [];

// Initialize Dashboard
window.addEventListener("DOMContentLoaded", () => {
    selectCustomer(activeCustomerId);
});

// 1. Fetch & Select Customer Profile Data
async function selectCustomer(customerId) {
    activeCustomerId = customerId;
    
    // Highlight Card
    document.querySelectorAll(".customer-card").forEach(card => {
        card.classList.remove("active");
    });
    const activeCard = document.getElementById(`card-${customerId}`);
    if (activeCard) {
        activeCard.classList.add("active");
    }

    try {
        const response = await fetch(`/api/customer/${customerId}`);
        if (!response.ok) throw new Error("Failed to load customer profile");
        
        const data = await response.json();
        currentProfileData = data;
        renderLedger(data);
    } catch (err) {
        console.error("Error loading customer data:", err);
    }
}

// 2. Render Profile Ledger (Right Panel)
function renderLedger(data) {
    const profile = data.profile;
    const txns = data.transactions;

    // Set Balances
    document.getElementById("ledger-checking-amt").innerText = `$${profile.checking_balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    document.getElementById("ledger-savings-amt").innerText = `$${profile.savings_balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;

    // Render Credit Card
    const card = profile.credit_cards && profile.credit_cards.length > 0 ? profile.credit_cards[0] : null;
    const lockBtn = document.getElementById("card-lock-action-btn");
    
    if (card) {
        document.getElementById("ledger-cc-type").innerText = card.type;
        document.getElementById("ledger-cc-num").innerText = `•••• •••• •••• ${card.card_id.split('-')[1] || '9011'}`;
        document.getElementById("ledger-cc-limit").innerText = `Limit: $${card.limit.toLocaleString()}`;
        document.getElementById("ledger-cc-bal").innerText = `Balance: $${card.balance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        
        const statusEl = document.getElementById("ledger-cc-status");
        if (card.status === "Locked") {
            statusEl.innerText = "LOCKED";
            statusEl.className = "cc-status locked";
            lockBtn.innerText = "🔓 Unlock Credit Card";
            lockBtn.style.background = "rgba(16, 185, 129, 0.1)";
            lockBtn.style.color = "var(--accent-green)";
            lockBtn.style.borderColor = "rgba(16, 185, 129, 0.2)";
        } else {
            statusEl.innerText = "ACTIVE";
            statusEl.className = "cc-status";
            lockBtn.innerText = "🔒 Lock Credit Card";
            lockBtn.style.background = "rgba(239, 68, 68, 0.1)";
            lockBtn.style.color = "var(--accent-red)";
            lockBtn.style.borderColor = "rgba(239, 68, 68, 0.2)";
        }
        lockBtn.style.display = "flex";
    } else {
        document.getElementById("ledger-cc-type").innerText = "No Active Cards";
        document.getElementById("ledger-cc-num").innerText = "•••• •••• •••• ••••";
        document.getElementById("ledger-cc-limit").innerText = "Limit: $0";
        document.getElementById("ledger-cc-bal").innerText = "Balance: $0";
        document.getElementById("ledger-cc-status").innerText = "INACTIVE";
        lockBtn.style.display = "none";
    }

    // Render Recent Transactions
    const listEl = document.getElementById("ledger-txn-list");
    listEl.innerHTML = "";
    
    txns.forEach(txn => {
        const item = document.createElement("div");
        item.className = "txn-item";
        
        let flagSpan = "";
        if (txn.flagged) {
            flagSpan = `<span class="txn-flag">FLAGGED</span>`;
        }

        item.innerHTML = `
            <div class="txn-left">
                <span class="txn-merchant">${txn.merchant}</span>
                <span class="txn-meta">${txn.date} • ${txn.location}</span>
            </div>
            <div class="txn-right">
                <span class="txn-amt" style="color: ${txn.flagged ? 'var(--accent-red)' : 'var(--text-primary)'}">
                    $${txn.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}
                </span>
                ${flagSpan}
            </div>
        `;
        listEl.appendChild(item);
    });
}

// 3. Lock Active Card Interface Link
async function lockActiveCard() {
    if (!currentProfileData || !currentProfileData.profile.credit_cards.length) return;
    const card = currentProfileData.profile.credit_cards[0];
    
    const targetStatus = card.status === "Locked" ? "Active" : "Locked";
    
    try {
        // Toggle Locally
        card.status = targetStatus;
        renderLedger(currentProfileData);
        
        // If locked, send secure log to chat
        const chatMessages = document.getElementById("chat-messages-container");
        const sysMsg = document.createElement("div");
        sysMsg.className = "chat-bubble system";
        sysMsg.style.borderColor = targetStatus === "Locked" ? "var(--accent-red)" : "var(--accent-green)";
        sysMsg.innerHTML = `
            <h3>🛡️ Security Account Audit Notification</h3>
            <p>A secure signal was dispatched to host networks. Credit card <strong>${card.card_id}</strong> is now <strong>${targetStatus.toUpperCase()}</strong>.</p>
        `;
        chatMessages.appendChild(sysMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Sync with API
        await fetch("/api/lock_card", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                customer_id: activeCustomerId,
                card_id: card.card_id
            })
        });
    } catch (err) {
        console.error("Error setting card status:", err);
    }
}

// 4. Interactive Scenarios Pre-loader
function loadScenario(type) {
    const input = document.getElementById("chat-user-textbox");
    if (type === "wealth_advisory") {
        input.value = "Suggest a wealth investment portfolio recommendation based on my risk profile and active account assets.";
    } else if (type === "fraud_alert") {
        input.value = "Audit my recent transactions for suspicious charges. Are there any anomalies?";
    } else if (type === "card_dispute") {
        input.value = "Evaluate my pending card dispute for the Luxury Watch purchase. What is the status?";
    } else if (type === "product_rates") {
        input.value = "Show me the current interest rates for home mortgages and High Yield Savings Accounts.";
    }
    input.focus();
}

// 5. Send Message & Orchestrate Thoughts
async function sendMessage() {
    const textBox = document.getElementById("chat-user-textbox");
    const prompt = textBox.value.trim();
    if (!prompt) return;

    // Append User Bubble
    const container = document.getElementById("chat-messages-container");
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user";
    userBubble.innerText = prompt;
    container.appendChild(userBubble);
    
    textBox.value = "";
    container.scrollTop = container.scrollHeight;

    // Append Temporary Thinking Wave
    const thinkingBubble = document.createElement("div");
    thinkingBubble.className = "chat-bubble system";
    thinkingBubble.id = "agent-thinking-bubble";
    thinkingBubble.innerHTML = `
        <div class="thinking-wave">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    container.appendChild(thinkingBubble);
    container.scrollTop = container.scrollHeight;

    // Reset Agent Thought Nodes visually
    resetAgentNodes();
    setNodeState("coordinator", "thinking");
    document.getElementById("thought-status-label").innerText = "Analyzing query...";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                customer_id: activeCustomerId,
                message: prompt
            })
        });

        if (!response.ok) throw new Error("Orchestration network failed");
        const data = await response.json();
        
        // Remove thinking animation bubble
        const anim = document.getElementById("agent-thinking-bubble");
        if (anim) anim.remove();

        // Render Synthesized Response
        const sysBubble = document.createElement("div");
        sysBubble.className = "chat-bubble system";
        sysBubble.innerHTML = formatMarkdown(data.synthesized_response);
        container.appendChild(sysBubble);
        container.scrollTop = container.scrollHeight;

        // Process Agent Logs & Highlight Path
        activeAgentLogs = data.thought_logs;
        animateAgentThoughts(activeAgentLogs);

    } catch (err) {
        console.error(err);
        const anim = document.getElementById("agent-thinking-bubble");
        if (anim) anim.remove();
        
        const errBubble = document.createElement("div");
        errBubble.className = "chat-bubble system";
        errBubble.style.borderColor = "var(--accent-red)";
        errBubble.innerHTML = `<p style="color:var(--accent-red);">System connection error. Please configure API keys or verify backend.</p>`;
        container.appendChild(errBubble);
    }
}

function checkEnterKey(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// 6. Visual Multi-Agent Node Animations
function resetAgentNodes() {
    document.querySelectorAll(".agent-node").forEach(node => {
        node.className = "agent-node";
    });
    document.getElementById("active-thought-details-card").classList.remove("active");
}

function setNodeState(agentKey, state) {
    const node = document.getElementById(`node-${agentKey}`);
    if (!node) return;
    
    node.className = "agent-node active";
    if (state === "thinking") {
        node.classList.add("thinking");
    }
}

function animateAgentThoughts(logs) {
    resetAgentNodes();
    document.getElementById("thought-status-label").innerText = "Synthesis Complete";
    
    // Determine which specialized agents were consulted
    logs.forEach(log => {
        const name = log.agent_name.toLowerCase();
        
        let key = "";
        if (name.includes("coordinator")) key = "coordinator";
        else if (name.includes("wealth") || name.includes("advisor")) key = "wealth";
        else if (name.includes("fraud") || name.includes("auditor") || name.includes("security")) key = "fraud";
        else if (name.includes("dispute") || name.includes("analyst")) key = "dispute";
        else if (name.includes("support") || name.includes("specialist")) key = "support";

        if (key) {
            setNodeState(key, "active");
            // Add click listener to show specific thoughts in the log box
            const node = document.getElementById(`node-${key}`);
            node.onclick = () => showAgentLogCard(log);
        }
    });

    // Auto-display coordinator log
    const coordLog = logs.find(l => l.agent_name.includes("Coordinator"));
    if (coordLog) {
        showAgentLogCard(coordLog);
    }
}

function showAgentLogCard(log) {
    document.querySelectorAll(".agent-node").forEach(node => {
        node.classList.remove("thinking"); // stop flashing when reviewing
    });
    
    // Highlight matching node
    const name = log.agent_name.toLowerCase();
    let key = "";
    if (name.includes("coordinator")) key = "coordinator";
    else if (name.includes("wealth") || name.includes("advisor")) key = "wealth";
    else if (name.includes("fraud") || name.includes("auditor")) key = "fraud";
    else if (name.includes("dispute") || name.includes("analyst")) key = "dispute";
    else if (name.includes("support") || name.includes("specialist")) key = "support";
    
    if (key) {
        document.getElementById(`node-${key}`).classList.add("thinking");
    }

    document.getElementById("active-thought-agent-name").innerText = log.agent_name;
    document.getElementById("active-thought-reasoning").innerText = log.thought;
    document.getElementById("active-thought-tool").innerText = log.action;
    
    document.getElementById("active-thought-details-card").classList.add("active");
}

// 7. Dynamic API Key Modal Workflows
function openApiKeyModal() {
    document.getElementById("api-modal-overlay").classList.add("active");
}

function closeApiKeyModal() {
    document.getElementById("api-modal-overlay").classList.remove("active");
}

async function submitApiKey() {
    const key = document.getElementById("gemini-key-input").value.trim();
    if (!key) return;

    try {
        const response = await fetch("/api/api_key", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ api_key: key })
        });

        if (!response.ok) throw new Error("Invalid API key configured");
        
        closeApiKeyModal();
        
        // Update connection status dynamically
        const badge = document.getElementById("connection-mode-badge");
        badge.className = "mode-badge live";
        document.getElementById("connection-mode-text").innerText = "Live Gemini Mode";
        
        alert("Success! Live Google Gemini Engine has been unlocked.");
    } catch (err) {
        alert("Error configuring API Key: " + err.message);
    }
}

// Simple Custom Markdown Formatter (replaces bold and list markers)
function formatMarkdown(text) {
    if (!text) return "";
    let html = text
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/#### (.*)/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*)/g, '<li>$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    return html;
}
