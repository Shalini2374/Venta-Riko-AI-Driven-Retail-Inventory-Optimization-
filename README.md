# VentaRiko – Agentic AI Inventory Management System

VentaRiko is an Agentic AI–driven inventory management system designed to reduce food waste and maximize revenue in retail environments.
Instead of static, rule-based discounting, VentaRiko follows an Observe–Orient–Decide–Act (OODA) loop to recommend realistic, gradual, and data-driven discounts for expiring products.

---

## Problem Statement

Supermarkets incur significant losses when products expire unsold.
A common industry practice is last-day panic discounting (for example, 50% off), which reduces profit margins and fails to leverage early selling opportunities.

VentaRiko addresses this problem by identifying the optimal discount “sweet spot,” applying smaller discounts earlier to ensure sales while maximizing overall revenue.

---

## Agentic AI Approach (OODA Loop)

VentaRiko operates as an intelligent agent rather than a static algorithm.

### Observe

* Queries inventory databases
* Analyzes historical sales logs

### Orient

* Engineers critical features:

  * Days_Left
  * Sales_Velocity
  * Stock_Density

### Decide

* Uses a trained RandomForestRegressor (model_v3)
* Predicts the optimal discount percentage for each product

### Act

* Generates a dynamic management dashboard
* Produces a daily actionable task list for store managers

---

## Evolution of Intelligence

The project demonstrates a clear progression in AI decision-making capability.

| Version           | Description                                                                  |
| ----------------- | ---------------------------------------------------------------------------- |
| v1 – Classifier   | Binary yes/no discount decision                                              |
| v2 – Hybrid Model | ML-predicted base discounts combined with rule-based emergency logic         |
| v3 – Full Agent   | Non-linear regression model learning a gradual discount curve from 0% to 50% |

---

## Technology Stack

**Backend**

* Python
* FastAPI

**AI / Machine Learning**

* Scikit-learn
* Pandas
* NumPy
* Joblib

**Database**

* SQLAlchemy
* SQLite (supports multiple managers)

**Frontend**

* HTML5
* Tailwind CSS
* Vanilla JavaScript

**Authentication**

* JSON Web Tokens (JWT)

---

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/your-username/ventariko-ai-agent.git
cd ventariko-ai-agent
```

### Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pandas numpy scikit-learn joblib \
python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Run the Application

```bash
python main.py
```

### Access the User Interface

Open a web browser and navigate to:

```
http://127.0.0.1:8000
```

---

## Key Features

* Agent-based decision-making using the OODA loop
* Revenue-aware discount optimization
* End-to-end system integrating ML, backend services, authentication, and UI
* Designed for realistic retail workflows

---

