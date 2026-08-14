# VentaRiko – AI-Driven Retail Inventory Optimization

VentaRiko is an AI-driven retail inventory optimization application that helps store managers monitor inventory, analyze recent sales activity, identify products approaching expiration, and receive machine-learning-based discount recommendations.

The application combines **FastAPI, JWT authentication, SQLAlchemy, SQLite, Pandas, Scikit-learn, and a Random Forest regression model** with a web-based dashboard.

> **Note:** The current machine-learning model is trained using synthetic retail data. The project is a portfolio prototype demonstrating an end-to-end AI-assisted inventory decision-support workflow.

---

## Application Screenshots

### AI Dashboard

The dashboard combines inventory information, recent sales activity, remaining shelf life, inventory status, and AI-generated discount recommendations.

![VentaRiko AI Dashboard](screenshots/dashboard.png)

### Data Upload Center

The Data Upload Center allows users to upload product catalogs and daily sales data and add inventory batches individually or in bulk.

![VentaRiko Data Upload Center](screenshots/data-upload.png)

### Authentication

The application provides a login interface protected by JWT-based authentication.

![VentaRiko Login](screenshots/login.png)

---

## Problem

Retail businesses need to manage inventory efficiently, especially for products with limited shelf life.

When products approach expiration or inventory levels become high relative to recent demand, store managers need to determine:

* Which products require immediate attention
* Which products may benefit from markdowns
* What discount level should be considered
* Which products are approaching expiration
* How recent sales activity should influence inventory decisions

Handling these decisions manually can become difficult as the number of products and transactions increases.

---

## Solution

VentaRiko provides an end-to-end inventory decision-support workflow.

```text
                    ┌───────────────────┐
                    │   Store Manager   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   Web Interface   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      FastAPI      │
                    │    REST APIs      │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ SQLite +        │       │ Inventory &     │
        │ SQLAlchemy      │       │ Sales Features │
        └─────────────────┘       └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Random Forest   │
                                  │   Regressor     │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ Discount        │
                                  │ Recommendation  │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │   Dashboard     │
                                  └─────────────────┘
```

---

## Key Features

### AI-Based Discount Recommendation

A **Random Forest Regressor** predicts a recommended discount percentage based on inventory and recent sales information.

### Inventory Management

The application supports:

* Adding individual stock batches
* Adding multiple stock batches in bulk
* Uploading inventory data
* Monitoring remaining shelf life

### Sales Data Management

Daily sales information can be uploaded and incorporated into the inventory analysis workflow.

### JWT Authentication

The backend provides user registration and JWT-based authentication for protected application functionality.

### User-Level Data Association

Inventory and sales records are associated with authenticated users, allowing the dashboard to retrieve data relevant to the current user.

### Inventory Status

The dashboard categorizes inventory conditions and highlights products that may require attention.

### Web Dashboard

The dashboard displays:

* Product
* Inventory status
* Available stock
* Recent sales
* Remaining days
* AI-recommended discount

---

## How It Works

### 1. Authenticate

A user registers and logs into the application.

The backend generates a JWT token for authenticated requests.

### 2. Upload Inventory

The user uploads or adds inventory information through the Data Upload Center.

### 3. Upload Sales Data

Daily sales information is uploaded through the application.

### 4. Prepare Features

The application uses inventory and sales information to prepare the features required by the machine-learning model.

### 5. Generate Prediction

The Random Forest regression model predicts a recommended discount percentage.

### 6. Display Recommendation

The dashboard presents the inventory status and AI-generated recommendation to the user.

---

## Machine Learning

### Model

The application uses:

**Random Forest Regressor**

The model performs a regression task where the target is a recommended discount percentage.

### Model Features

The current prediction pipeline uses:

| Feature           | Description           |
| ----------------- | --------------------- |
| `Category`        | Product category      |
| `Days_Left`       | Remaining shelf life  |
| `Stock_Available` | Available inventory   |
| `Sales_Last_Week` | Recent sales activity |

### Prediction Target

The model predicts:

```text
Target_Discount
```

The application limits the final recommendation to:

```text
0% – 50%
```

---

## Machine Learning Pipeline

```text
Synthetic Retail Dataset
          │
          ▼
    Data Preparation
          │
          ▼
   Feature Engineering
          │
          ▼
    Train/Test Split
          │
          ▼
 Random Forest Regressor
          │
          ▼
      Evaluation
          │
          ▼
   Saved ML Model
          │
          ▼
    FastAPI Backend
          │
          ▼
 Discount Recommendation
          │
          ▼
       Dashboard
```

---

## Training Data

The project uses a **synthetic supermarket dataset** for model development.

The dataset contains retail inventory and sales-related information used to demonstrate the machine-learning workflow.

The synthetic target is based on inventory-related conditions such as:

* Remaining shelf life
* Product category
* Available stock
* Recent sales activity
* Stock-to-sales relationships

Because the training data is synthetic, the model should be considered a prototype and should not be interpreted as a production retail pricing model.

---

## Model Training

The repository includes scripts for generating synthetic data and training the model.

### Generate the dataset

```bash
python generatedata_v3.py
```

### Train the model

```bash
python training_v3.py
```

The training pipeline uses a train/test split and evaluates the regression model using **Root Mean Squared Error (RMSE)**.

The trained model is serialized and used by the FastAPI application.

---

## API Endpoints

| Endpoint                   | Method | Description                                          |
| -------------------------- | ------ | ---------------------------------------------------- |
| `/register/`               | POST   | Register a new user                                  |
| `/token`                   | POST   | Authenticate and obtain a JWT token                  |
| `/users/me/`               | GET    | Retrieve authenticated user information              |
| `/setup/upload-inventory/` | POST   | Upload inventory data                                |
| `/stock/add_batch/`        | POST   | Add an inventory batch                               |
| `/stock/add_batch_bulk/`   | POST   | Add multiple inventory batches                       |
| `/sales/upload-daily/`     | POST   | Upload daily sales data                              |
| `/dashboard/`              | GET    | Retrieve dashboard inventory and recommendation data |

---

## Authentication Flow

```text
User Registration
       │
       ▼
Password Hashing
       │
       ▼
User Login
       │
       ▼
JWT Token
       │
       ▼
Authenticated Request
       │
       ▼
Protected API Endpoint
```

The application uses JWT-based authentication and password hashing for user authentication.

---

## Database

VentaRiko uses:

* **SQLite** for local database storage
* **SQLAlchemy** as the ORM

The application stores information related to:

* Users
* Products
* Stock batches
* Daily sales

Inventory and sales records are associated with users to support user-level data separation.

For a production deployment, a database such as PostgreSQL would be more suitable.

---

## OODA-Inspired Workflow

The application follows an OODA-inspired decision workflow.

### Observe

Collect inventory and sales information:

* Stock availability
* Remaining shelf life
* Product category
* Recent sales

### Orient

Prepare relevant features and identify inventory conditions that may require attention.

### Decide

Use the Random Forest regression model to generate a discount recommendation.

### Act

Present the recommendation through the dashboard so that a store manager can use it as a decision-support signal.

> The OODA terminology describes the workflow design. The current implementation is an ML-backed decision-support application, not a fully autonomous AI agent.

---

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* REST APIs
* SQLAlchemy

### Authentication

* JWT
* Python-JOSE
* Passlib
* bcrypt

### Machine Learning

* Scikit-learn
* Random Forest Regression
* Pandas
* NumPy
* Joblib

### Data Generation

* Pandas
* NumPy
* Faker

### Database

* SQLite
* SQLAlchemy ORM

### Frontend

* HTML
* JavaScript
* CSS
* Tailwind CSS

### Development

* Git
* GitHub
* VS Code
* Postman

---

## Project Structure

```text
Venta-Riko-AI-Driven-Retail-Inventory-Optimization/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│
├── screenshots/
│   ├── dashboard.png
│   ├── data-upload.png
│   └── login.png
│
├── model_v3.pkl
├── supermarket_v3.csv
├── generatedata_v3.py
├── training_v3.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Shalini2374/Venta-Riko-AI-Driven-Retail-Inventory-Optimization-.git
```

### 2. Navigate to the project

```bash
cd Venta-Riko-AI-Driven-Retail-Inventory-Optimization-
```

### 3. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Requirements

The project uses the following Python packages:

```text
fastapi==0.119.1
uvicorn==0.38.0
SQLAlchemy==2.0.44
pydantic==2.12.3
python-jose==3.5.0
passlib==1.7.4
bcrypt==3.2.0
python-multipart==0.0.20
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
joblib==1.4.2
Faker==37.11.0
```

---

## Environment Configuration

The application uses a secret key for authentication.

For local development, configure a secret key through an environment variable:

```env
SECRET_KEY=your-secret-key
```

Do not commit real secrets, passwords, API keys, or credentials to the repository.

---

## Running the Application

Start the FastAPI application:

```bash
python main.py
```

Alternatively:

```bash
uvicorn main:app --reload
```

The application runs locally at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Application Workflow

```text
1. Register
      ↓
2. Login
      ↓
3. Authenticate with JWT
      ↓
4. Upload inventory
      ↓
5. Upload daily sales
      ↓
6. Open dashboard
      ↓
7. Review inventory status
      ↓
8. Review AI discount recommendations
```

---

## Data Flow

```text
Inventory Data
      │
      ▼
Inventory API
      │
      ▼
Database
      │
      ├──────────────┐
      │              │
      ▼              ▼
Inventory Data   Sales Data
      │              │
      └──────┬───────┘
             ▼
      Feature Preparation
             │
             ▼
     Random Forest Model
             │
             ▼
  Discount Recommendation
             │
             ▼
         Dashboard
```

---

## Project Evolution

The project evolved through multiple machine-learning approaches:

| Version | Approach                                                            |
| ------- | ------------------------------------------------------------------- |
| **v1**  | Classification-based discount decision                              |
| **v2**  | Regression with inventory and demand-related features               |
| **v3**  | Random Forest regression with a nonlinear synthetic discount target |

The latest version focuses on predicting a continuous discount percentage rather than making a binary discount/no-discount decision.

---

## Security

The current application includes:

* JWT-based authentication
* Password hashing
* Protected API endpoints
* User-level data association

For production deployment, additional security measures would be appropriate, including:

* HTTPS
* Secure secret management
* Token expiration and refresh mechanisms
* Rate limiting
* Strong password policies
* Secure CORS configuration
* Input validation
* Production database configuration
* Logging and monitoring

---

## Limitations

The current version has several limitations:

* The training dataset is synthetic.
* The model predicts discount recommendations rather than directly optimizing revenue or profit.
* Recommendation quality depends on the quality of inventory and sales data.
* SQLite is currently used for local development.
* The model has not been validated against a large real-world retail transaction dataset.
* The application is a decision-support prototype rather than a fully autonomous inventory management system.
* Recommendations should be reviewed by a human decision-maker before being applied to real retail operations.

---

## Future Improvements

Potential improvements include:

* Training on real retail transaction data
* Adding historical demand forecasting
* Incorporating price elasticity
* Adding product profit margins
* Using time-series models for demand prediction
* Automated model retraining
* Model monitoring and drift detection
* PostgreSQL integration for production deployments
* Docker-based deployment
* Cloud deployment
* Role-based access control
* Automated inventory alerts
* Discount effectiveness tracking
* Inventory turnover analytics

---

## What This Project Demonstrates

This project demonstrates an end-to-end software engineering and machine-learning workflow involving:

* REST API development with FastAPI
* JWT authentication
* Password hashing
* SQLAlchemy ORM
* SQLite database management
* CSV and tabular data processing
* Feature preparation
* Random Forest regression
* Machine-learning model serialization
* ML model integration with a backend API
* Frontend dashboard development
* User-level data association
* AI-assisted decision support

---

## Disclaimer

VentaRiko is an educational and portfolio project demonstrating an AI-assisted retail inventory optimization workflow.

The current machine-learning model is trained on synthetic data and has not been validated for production retail pricing decisions.

The recommendations generated by the system should therefore be treated as **decision-support suggestions rather than guaranteed optimal pricing decisions**.

---

## Author

**G. S. Shalini**

Integrated M.Tech – Computer Science and Engineering
VIT Vellore

**GitHub:**
https://github.com/Shalini2374

**LinkedIn:**
https://www.linkedin.com/in/shalini-saravanan-8a3519268/

---

## License

This project is licensed under the **MIT License**.
