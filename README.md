VentaRiko: An Agentic AI Inventory Management System

VentaRiko is an intelligent "Agentic AI" platform designed to solve the massive problem of food waste in retail. Instead of relying on static, hard-coded rules, VentaRiko follows an OODA Loop (Observe-Orient-Decide-Act) to provide store managers with a realistic, gradual, and data-driven discount strategy for expiring goods.

🚀 The Core Problem

Supermarkets lose billions every year due to products reaching their expiry date. Most managers use "panic discounting" (e.g., 50% off on the last day), which loses profit. VentaRiko uses Machine Learning to find the "sweet spot"—applying smaller, gradual discounts earlier to ensure the product sells while maximizing revenue.

🧠 The Agentic AI (OODA Loop)

Unlike a simple algorithm, VentaRiko behaves as an Agent:

Observe: It queries the inventory database and sales logs.

Orient: It calculates key features like Days_Left, Sales_Velocity, and Stock_Density.

Decide: It feeds these features into a RandomForestRegressor (model_v3) to predict the optimal discount.

Act: It generates a dynamic dashboard and a "Daily To-Do List" for the manager.

📈 Evolution of the Intelligence

This project demonstrates the evolution of AI decision-making:

v1 (The Classifier): Simple Yes/No prediction for discounts.

v2 (The Hybrid): AI-predicted base discounts with hard-coded emergency rules.

v3 (The Full Agent): A realistic, non-linear model that learned the "gradual curve" from 0% to 50% through custom data engineering.

🛠 Tech Stack

Backend: Python, FastAPI

AI/ML: Scikit-Learn, Pandas, NumPy, Joblib

Database: SQLAlchemy, SQLite (Multi-Manager Support)

Frontend: HTML5, Tailwind CSS, JavaScript (Vanilla)

Authentication: JWT (JSON Web Tokens)

🔧 Installation & Setup

Clone the repository:

git clone [https://github.com/your-username/ventariko-ai-agent.git](https://github.com/your-username/ventariko-ai-agent.git)
cd ventariko-ai-agent


Install dependencies:

pip install fastapi uvicorn sqlalchemy pandas numpy scikit-learn joblib python-jose[cryptography] passlib[bcrypt] python-multipart


Run the server:

python main.py


Access the UI:
Open http://127.0.0.1:8000 in your browser.

