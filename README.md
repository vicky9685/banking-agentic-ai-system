# ApexBank AI Co-Pilot: Multi-Agent Banking Hub 🏦✨

**ApexBank AI Co-Pilot** is a production-ready, ultra-premium multi-agentic AI system designed to solve critical banking operations workflows. It orchestrates a cooperative swarm of specialized AI agents (Router, Wealth Planner, Security Auditor, Dispute Analyst, Support Desk) behind a stunning glassmorphic single-page dashboard.

---

## 🏗️ Multi-Agent Swarm Architecture

The system coordinates five specialized personas using a **Hierarchical Hybrid Workflow**:

1. **Aegis Coordinator & Router (Aegis):** The command center. Evaluates user input, maps a multi-specialist roadmap, dispatches queries to targeted specialists, and synthesizes the outputs into a clean final response.
2. **Wealth Advisor Agent:** Performs portfolio recommendations and budget suitability assessments under static policy ratios.
3. **Fraud & Audit Specialist:** Scans recent transaction logs for security threats, geolocational velocity anomalies, and geographic impossibility checks.
4. **Dispute Specialist:** Formulates official card dispute resolutions (provisional credits, chargeback dispatch) based on filing timeliness.
5. **Support & Rates Specialist:** Rapidly answers banking FAQs, savings/CD interest yields, and mortgage rates.

---

## 💻 Tech Stack & Design Aesthetics
* **Backend:** FastAPI (Python), Uvicorn server, Pydantic data validation.
* **Frontend:** Vanilla HTML5, premium Vanilla CSS3 (featuring glassmorphism, radial gradient backgrounds, glowing border pulses, custom scrollbars, and card layers), and Vanilla JavaScript state controller.
* **Visuals:** Customized high-fidelity vector-style digital brand asset.
* **AI Orchestration:** Integrated with standard Python SDK and configured with a **Dual-Core Execution Engine** facilitating instant mock simulations or real-time live Google Gemini API execution.

---

## 🚀 Local Run Instructions (Zero-Config Dry Run)

To run the application immediately on your local machine:

### 1. Initialize Python Environment
```powershell
# Create Virtual Environment
py -m venv venv

# Activate Virtual Environment (Windows)
.\venv\Scripts\Activate.ps1

# Activate Virtual Environment (macOS/Linux)
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Launch FastAPI Web Server
```bash
python -m app.main
```
The application will launch on: **`http://localhost:8080`**

### 3. Unlock Live Gemini Mode
* Open the web dashboard in your browser.
* Click **Configure API Key** in the top-right header panel.
* Paste your **Google Gemini API Key** (`AIzaSy...`) and click **Activate**.
* The connection badge will instantly glow green: **Live Gemini Mode** is now fully active with zero reloads!

---

## ☁️ Deploying to Google Cloud Platform (GCP)

We provide two production-grade pathways to deploy this application to **GCP Cloud Run** using serverless containers and secure secret parameters.

### Option A: The Quick Deploy Scripts (Recommended)
This method automates container compiling, registry configurations, Secret Manager bindings, and Cloud Run deployments using a single terminal command. **No local Docker installation required!**

#### On Windows (PowerShell):
```powershell
.\deploy.ps1
```

#### On Linux / macOS (Bash):
```bash
chmod +x deploy.sh
./deploy.sh
```
*The script will prompt you for your target **GCP Project ID** and your **Gemini API Key**, handle API activation, and supply the final public application URL.*

---

### Option B: Deploying via Infrastructure as Code (Terraform)
If your organization prefers declarative deployments:

1. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```
2. Plan & Deploy:
   ```bash
   terraform apply -var="gcp_project_id=YOUR_PROJECT_ID"
   ```
3. Retrieve deployed resource endpoints directly from standard outputs.

---

### Option C: Automated CI/CD (GitHub Actions)
For full continuous deployment automation on every push to your repository's `main` branch, we have pre-configured a GitHub Actions CI/CD workflow:

1. **Locate Workflow:** Find the workflow at `.github/workflows/deploy-gcp.yml`.
2. **Add GitHub Secrets:** In your GitHub Repository, navigate to **Settings > Secrets and variables > Actions** and add the following repository secrets:
   * `GCP_PROJECT_ID`: Your target Google Cloud Project ID.
   * `GCP_SA_KEY`: The JSON Key of a GCP Service Account with permissions for Artifact Registry, Cloud Run, and Cloud Build.
3. **Trigger Pipeline:** Push your code changes to `main` branch. GitHub will automatically trigger the container build on GCP infrastructure, push it, and release it onto Google Cloud Run!

