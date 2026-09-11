<div align="center"><img src="logoo.webp"></div>


# Pattern Guard — Autonomous Dark Pattern Prosecution Platform

> **"We don't just detect dark patterns. We prosecute them."**

Pattern Guard is an autonomous agent that navigates real e-commerce and SaaS funnels (signup, checkout, cancellation, cookie consent walls), detects manipulative UX in real-time, captures forensic DOM proofs and annotated screenshots, and computes a regulatory **Manipulation Index** (0–100) per site. It outputs an editorial **"Hall of Shame"** leaderboard and comprehensive evidence drill-downs citing FTC and EU Digital Services Act violations.

---

## ⚡ Multi-Model Flexibility: Local Python or Any API Key

Pattern Guard gives users total choice between running **100% free / local** or attaching **any LLM API key** for enhanced precision:

| Engine / Mode | API Key Required? | Cost | Description |
|---|---|---|---|
| ⚡ **Local Python Engine (Default)** | **None** | **No inference fees** | Deterministic DOM parsing, WCAG contrast math, price drift tracking, and local regex heuristics. |
| 🧠 **xAI / Grok** | `xai-...` | Optional | Advanced psychological coercion analysis via `grok-beta` / `grok-2`. |
| 🤖 **OpenAI** | `sk-...` | Optional | Detailed cognitive bias analysis via `gpt-4o-mini` / `gpt-4o`. |
| ⚙️ **Custom LLMs / Ollama / DeepSeek** | Any | Optional | Custom OpenAI-compatible endpoint support (e.g. `http://localhost:11434/v1` or `https://api.deepseek.com/v1`). |

*Keys and optional OpenAI-compatible endpoint/model overrides can be configured in the UI (saved locally in your browser) or passed as server environment variables (`GROQ_API_KEY`, `GROK_API_KEY`, `OPENAI_API_KEY`). Treat browser-stored keys as development convenience; use server-side secrets for shared deployments.*

---

## 🚢 Single-Command Cloud & Container Hosting

Pattern Guard is packaged as a complete full-stack single-port container containing Node.js, Python 3.11, Playwright Headless Chromium, FastAPI, and the compiled React UI.

### Option 1: Docker / Docker Compose (Deploy Anywhere)
```bash
# Run with Docker Compose
docker compose up --build -d
```
Open **`http://localhost:8000`**.

### Option 2: Render.com (1-Click Cloud Blueprint)
1. Push this repository to GitHub.
2. Go to [Render.com](https://render.com) $\to$ **New Blueprint Instance**.
3. Select your repo — Render will automatically read `render.yaml` and `Dockerfile` and spin up the live backend + frontend container on a public URL.

### Option 3: Railway / Fly.io / VPS
```bash
# Build and run with standard Docker
docker build -t pattern-guard .
docker run -p 8000:8000 -e PORT=8000 pattern-guard
```

---

## 🚀 Running Locally (Under 2 Minutes)

### Single Port (Fullstack Mode)
```bash
# Build the frontend once before starting the single-port server
cd frontend
npm ci
npm run build
cd ..

# Start FastAPI backend (serves both API and compiled React UI on port 8000)
python -m uvicorn backend.main:app --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser.

### Local Development Mode
```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```
Open **`http://localhost:5173`**.

---

## 📋 Detection Rubric & Regulatory Taxonomy

| Dark Pattern Category | Forensic Algorithmic Trigger | Severity & Score Weight | Applicable Legal Grounding | Psychological Mechanism |
|---|---|---|---|---|
| **Sneaking / Pre-checked Opt-in** | Checkbox `checked=true` for non-essential add-ons (warranty, insurance, recurring club membership) or auto-added line items. | **Critical** (+25 to +30 pts) | FTC Act § 5 (15 U.S.C. § 45); EU DSA Art. 25; Cal. AB 390 | **Default Effect / Inertia Bias** |
| **Hidden Costs / Drip Pricing** | Price escalation between Step 1 and checkout due to unannounced mandatory platform fees, convenience fees, or studio surcharges. | **Critical** (+22 to +28 pts) | FTC 16 CFR Part 464 (Deceptive Fees Rule); Cal. SB 478 | **Sunk Cost Fallacy & Bait-and-Switch** |
| **Confirmshaming** | Decline button framed with guilt-tripping language (e.g. *"No thanks, I don't want to save money and prefer paying full price"*). | **High** (+24 pts) | FTC Policy Statement on Dark Patterns; EU DSA Art. 25(1) | **Emotional Guilt Induction** |
| **Fake Urgency & Resetting Timers** | Countdown clocks that reset upon page refresh; artificial scarcity warnings (*"Only 1 left in stock!"*) without backend inventory depletion. | **Critical** (+28 pts) | FTC Urgency Enforcement; EU UCPD Directive 2005/29/EC | **FOMO & Urgency Heuristic** |
| **Roach Motel / Asymmetrical Friction** | 1-click instant enrollment vs multi-step cancellation labyrinth (>= 3 screens, exit interviews, guilt prompts) or mandatory phone-call walls. | **Critical** (+30 to +35 pts) | FTC Click-to-Cancel Rule (16 CFR § 425.6); Cal. SB 313 | **Sludge & Cognitive Friction** |
| **Visual Deception / Low Contrast** | Mandatory terms, fee disclaimers, or cancellation links rendered with < 3.0:1 contrast ratio or font-size < 11px. | **High** (+18 to +26 pts) | FTC Conspicuousness Standards (16 CFR § 425.4); WCAG 2.1 AA | **Visual Suppression & Concealment** |

---

## 🧪 Built-in Zero-Fail Offline Sandboxes

- **ShopSneak E-Commerce Funnel** (`http://127.0.0.1:8000/mock/shopsneak`):
  - Pre-checked 2-year accidental warranty (+$18.99)
  - Fake 5-minute countdown clock that resets on refresh
  - Drip platform regulatory fee ($7.50) and handling fee ($4.85)
- **GymTrap SaaS Roach Motel Funnel** (`http://127.0.0.1:8000/mock/gymtrap`):
  - 1-click free trial signup
  - 4-page cancellation obstacle course with catastrophic loss framing
  - Offline phone-call cancellation mandate (*"Call 1-800-555-0199"*)

---

## 🎨 Editorial Design

The interface uses a dark editorial dashboard, compact forensic typography, restrained blue accents, and high-density evidence views.

---

## Security and interpretation notes

- Public scan targets must resolve to globally routable addresses. Loopback access is limited to Pattern Guard's built-in `/mock` routes.
- Scan concurrency and step counts are bounded. Configure `MAX_CONCURRENT_SCANS` and `CORS_ALLOWED_ORIGINS` for your deployment.
- Bright Data URLs supplied through the UI are restricted to `brd.superproxy.io` WebSocket endpoints.
- Results are automated evidence leads, not legal determinations. Verify findings and citations with qualified reviewers before enforcement or publication.
