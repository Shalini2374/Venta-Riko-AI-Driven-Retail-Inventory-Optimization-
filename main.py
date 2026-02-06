import joblib
import os
import csv
import io
import pandas as pd
import numpy as np
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel, ConfigDict # Updated Pydantic import
from datetime import date, datetime, timedelta
from typing import List
from pathlib import Path

# --- Database Imports ---
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, Session, relationship, joinedload
from sqlalchemy.orm import declarative_base # Updated import
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
# --- END Imports ---

# --- Security Imports ---
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# --- END Security Imports ---

# --- Define Base Directory ---
BASE_DIR = Path(__file__).resolve().parent

print("--- Starting the VentaRiko AI Agent Server (v3) ---")

# --- 1. DATABASE SETUP ---
DATABASE_URL = f"sqlite:///{BASE_DIR / 'store.db'}"
Base = declarative_base() # Updated function call

# --- Define User table ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    user_stock_batches = relationship("StockBatch", back_populates="owner")
    user_sales_logs = relationship("DailySalesLog", back_populates="owner")
    created_products = relationship("Product", back_populates="creator")


# --- Define StockBatch table ---
class StockBatch(Base):
    __tablename__ = "stock_batches"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    expiry_date = Column(Date)
    product_id = Column(Integer, ForeignKey("products.id"))
    owner_id = Column(Integer, ForeignKey("users.id")) 
    owner = relationship("User", back_populates="user_stock_batches")
    product = relationship("Product", back_populates="stock_batches")

# --- Define Product table ---
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True)
    category = Column(String)
    manufacturer = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id")) 
    creator = relationship("User", back_populates="created_products")
    stock_batches = relationship("StockBatch", back_populates="product")
    sales_logs = relationship("DailySalesLog", back_populates="product")

# --- Define DailySalesLog table ---
class DailySalesLog(Base):
    __tablename__ = "daily_sales_logs"
    id = Column(Integer, primary_key=True, index=True)
    quantity_sold = Column(Integer)
    sale_date = Column(DateTime, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey("products.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="user_sales_logs")
    product = relationship("Product", back_populates="sales_logs")

# Create engine and tables
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB Dependency
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

print(f"--- Database setup complete. Using: {DATABASE_URL} ---")
# --- END DATABASE SETUP ---

# --- Security Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
ALGORITHM = "HS256" # Using the standard HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic Models for User Auth
class UserCreate(BaseModel): username: str; password: str
class UserResponse(BaseModel):
    id: int; username: str
    class Config: # Use Config instead of ConfigDict for compatibility
        from_attributes = True
class Token(BaseModel): access_token: str; token_type: str
class TokenData(BaseModel): username: str | None = None

# Security Utility Functions
def verify_password(plain_password, hashed_password): return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password): return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency to Get Current User
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None: raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError: raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None: raise credentials_exception
    return user
# --- END Security Setup ---

# --- Initialize FastAPI app ---
app = FastAPI(
    title="Venta Riko - AI Agent (v3)", # Updated title
    description="A smart AI agent that predicts realistic, gradual discounts based on a learned model."
)

# --- Load ML Model ---
# *** CRITICAL CHANGE: Load the new v3 model ***
model_filename = BASE_DIR / 'model_v3.pkl' 
model = None
try:
    if model_filename.exists():
        model = joblib.load(model_filename)
        print(f"--- Successfully loaded SMART model: {model_filename.name} ---")
    else:
        print(f"--- FATAL ERROR: Model file not found: {model_filename} ---")
        print("--- Please run 'training_v3.py' to create the model. ---")
except Exception as e:
    print(f"--- FATAL ERROR: Error loading model: {e} ---")
# --- END Load ML Model ---

# --- Pydantic Models for Stock ---
class StockBatchCreate(BaseModel): product_id: int; quantity: int; expiry_date: date

# --- API Endpoints ---

# Mount static files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# --- User Authentication Endpoints (No changes needed) ---

@app.post("/register/", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user: raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    try:
        db.add(db_user); db.commit(); db.refresh(db_user)
        print(f"--- Successfully registered user: {user.username} (ID: {db_user.id}) ---")
        return db_user
    except IntegrityError: db.rollback(); raise HTTPException(status_code=400, detail="Username already registered (concurrent request)")
    except Exception as e: db.rollback(); print(f"--- ERROR during registration: {e} ---"); raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    print(f"--- User '{form_data.username}' logged in successfully. Token issued. ---")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- END User Authentication Endpoints ---


@app.get("/")
async def read_root_html():
    index_path = BASE_DIR / 'index.html'
    if index_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    else:
        return {"message": "Welcome to Venta Riko API. Frontend file 'index.html' not found."}


# --- Data Management Endpoints (Multi-Manager logic is already correct) ---

@app.post("/setup/upload-inventory/")
async def upload_inventory(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # This logic is correct - it skips existing global products
    if not file or not file.filename.endswith('.csv'): raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .csv file.")
    try:
        contents = await file.read(); file_text = io.StringIO(contents.decode('utf-8-sig'))
        reader = csv.DictReader(file_text); products_added = 0; products_skipped = 0
        required_columns = {'id', 'name', 'category', 'manufacturer'}
        header = set(map(str.lower, reader.fieldnames or []))
        if not required_columns.issubset(header): missing = required_columns - header; raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {', '.join(missing)}")
        
        for row_raw in reader:
            row = {str(k).lower().strip(): str(v).strip() if v is not None else '' for k, v in row_raw.items()}
            try:
                product_id_str = row.get('id', '')
                if not product_id_str: continue # Skip empty rows
                product_id = int(product_id_str)
                existing_product = db.query(Product).filter(Product.id == product_id).first()
                if not existing_product:
                    new_product = Product(id=product_id, name=row.get('name'), category=row.get('category'), manufacturer=row.get('manufacturer'), creator_id=current_user.id)
                    db.add(new_product); products_added += 1
                else: products_skipped += 1
            except (ValueError, TypeError): continue
        db.commit()
        print(f"--- User '{current_user.username}' inventory upload: {products_added} new products added, {products_skipped} existing products skipped. ---")
        return {"status": "success", "filename": file.filename, "products_added": products_added, "products_skipped": products_skipped}
    except Exception as e: db.rollback(); print(f"--- ERROR [User: {current_user.username}] processing inventory file: {e} ---"); raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/stock/add_batch/", response_model=StockBatchCreate)
async def add_stock_batch(batch: StockBatchCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # This logic is correct - it tags the batch with owner_id
    if batch.quantity < 0: raise HTTPException(status_code=400, detail="Quantity cannot be negative.")
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    if not product: raise HTTPException(status_code=404, detail=f"Product {batch.product_id} not found. Please upload it via the inventory setup first.")
    try:
        new_batch = StockBatch(product_id=batch.product_id, quantity=batch.quantity, expiry_date=batch.expiry_date, owner_id=current_user.id)
        db.add(new_batch); db.commit(); db.refresh(new_batch)
        print(f"--- User '{current_user.username}' successfully added batch (ID: {new_batch.id}) for '{product.name}' ---")
        return new_batch
    except Exception as e: db.rollback(); print(f"--- ERROR [User: {current_user.username}] adding stock batch: {e} ---"); raise HTTPException(status_code=500, detail=f"Error adding stock batch: {e}")


@app.post("/stock/add_batch_bulk/", response_model=dict)
async def add_stock_batch_bulk(batches: List[StockBatchCreate], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # This logic is correct - it tags all batches with owner_id
    batches_added_count = 0; product_names = set()
    product_ids = {batch.product_id for batch in batches}
    valid_products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    valid_product_map = {product.id: product.name for product in valid_products}

    try:
        for i, batch in enumerate(batches):
            if batch.quantity < 0: raise HTTPException(status_code=400, detail=f"Item {i} has negative quantity.")
            product_name = valid_product_map.get(batch.product_id)
            if not product_name: raise HTTPException(status_code=404, detail=f"Item {i} (product_id: {batch.product_id}) not found in global catalog. Transaction rolled back.")
            
            new_batch = StockBatch(product_id=batch.product_id, quantity=batch.quantity, expiry_date=batch.expiry_date, owner_id=current_user.id)
            db.add(new_batch); product_names.add(product_name); batches_added_count += 1
            
        db.commit()
        print(f"--- User '{current_user.username}' successfully added {batches_added_count} bulk batches. ---")
        return {"status": "success", "batches_added": batches_added_count, "products_updated": sorted(list(product_names))}
    except Exception as e: db.rollback(); print(f"--- ERROR [User: {current_user.username}] adding bulk stock: {e} ---"); raise HTTPException(status_code=500, detail=f"Error adding bulk stock: {e}")


@app.post("/sales/upload-daily/")
async def upload_daily_sales(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # This logic is correct - it only sells from the user's own stock
    if not file or not file.filename.endswith('.csv'): raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        contents = await file.read(); file_text = io.StringIO(contents.decode('utf-8-sig'))
        reader = csv.DictReader(file_text); required_columns = {'product_id', 'quantity_sold'}; header = set(map(lambda h: str(h).lower().strip(), reader.fieldnames or []))
        if not required_columns.issubset(header): missing = required_columns - header; raise HTTPException(status_code=400, detail=f"Sales CSV missing columns: {', '.join(missing)}")

        sales_logged = 0; updated_products = set(); rows = [row for row in reader]
        
        product_ids_from_csv = set()
        for r in rows:
            try:
                pid_str = str(r.get('product_id', '')).strip()
                if pid_str.isdigit():
                    product_ids_from_csv.add(int(pid_str))
            except Exception:
                continue # Skip malformed rows

        valid_products_q = db.query(Product).filter(Product.id.in_(product_ids_from_csv)).all()
        valid_product_map = {p.id: p.name for p in valid_products_q}

        for row_raw in rows:
            row = {str(k).lower().strip(): str(v).strip() if v is not None else '' for k, v in row_raw.items()}
            try:
                product_id_str = row.get('product_id', '')
                quantity_sold_str = row.get('quantity_sold', '')
                if not product_id_str or not quantity_sold_str: continue

                product_id = int(product_id_str)
                quantity_to_sell = int(quantity_sold_str)
                if quantity_to_sell <= 0: continue
            except (ValueError, TypeError): continue

            product_name = valid_product_map.get(product_id)
            if not product_name: continue

            new_sale_log = DailySalesLog(product_id=product_id, quantity_sold=quantity_to_sell, owner_id=current_user.id)
            db.add(new_sale_log); sales_logged += 1

            available_batches = db.query(StockBatch).filter(
                StockBatch.product_id == product_id, 
                StockBatch.quantity > 0,
                StockBatch.owner_id == current_user.id # <-- Correctly scoped
            ).order_by(StockBatch.expiry_date.asc()).all()
            
            quantity_remaining_to_sell = quantity_to_sell; stock_updated_this_product = False
            for batch in available_batches:
                if quantity_remaining_to_sell <= 0: break
                sell_from_this_batch = min(batch.quantity, quantity_remaining_to_sell)
                if sell_from_this_batch > 0: batch.quantity -= sell_from_this_batch; quantity_remaining_to_sell -= sell_from_this_batch; stock_updated_this_product = True
            if stock_updated_this_product: updated_products.add(product_name)
            if quantity_remaining_to_sell > 0: print(f"--- WARNING [User: {current_user.username}]: Sale ({quantity_to_sell}) exceeded stock for '{product_name}'. Short by {quantity_remaining_to_sell}. ---")
        
        db.commit()
        return {"status": "success", "filename": file.filename, "sales_transactions_logged": sales_logged, "stock_updated_for_products": sorted(list(updated_products))}
    except Exception as e: db.rollback(); print(f"--- ERROR [User: {current_user.username}] processing sales file: {e} ---"); raise HTTPException(status_code=500, detail=f"Error processing sales file: {str(e)}")


@app.get("/dashboard/")
async def get_dashboard_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(f"\n--- SMART AGENT (v3) [User: {current_user.username}]: Received request for Dashboard Report ---")
    
    try:
        # This query correctly gets all global products but only joins *this user's* stock and sales
        products = db.query(Product).options(
            joinedload(Product.stock_batches.and_(StockBatch.owner_id == current_user.id)),
            joinedload(Product.sales_logs.and_(DailySalesLog.owner_id == current_user.id))
        ).all()
        print(f"--- AGENT (Observe): Found {len(products)} total products. Filtering for user '{current_user.username}'. ---")
    except Exception as e: print(f"--- ERROR [User: {current_user.username}] querying database: {e} ---"); raise HTTPException(status_code=500, detail=f"Database query error: {e}")

    today = date.today(); one_week_ago = datetime.utcnow() - timedelta(days=7)
    features_list = []; report_list = []
    if not model: raise HTTPException(status_code=500, detail="Model (model_v3.pkl) is not loaded.")

    print(f"--- AGENT (Orient): Processing products for user '{current_user.username}'... ---")
    
    for product in products:
        # Get *this user's* total stock for this product
        total_stock = sum(batch.quantity for batch in product.stock_batches if batch.quantity > 0)
        
        # Only process products this user actually has in stock
        if total_stock > 0:
            # Get *this user's* nearest expiry date
            nearest_expiry_date = min((batch.expiry_date for batch in product.stock_batches if batch.quantity > 0 and batch.expiry_date), default=None)
            days_to_expiry = (nearest_expiry_date - today).days if nearest_expiry_date else 9999
            
            # Get *this user's* sales
            sales_last_week = sum(log.quantity_sold for log in product.sales_logs if log.sale_date >= one_week_ago)

            # *** THIS IS THE CRITICAL FIX: Build the feature dictionary ***
            # This must match the features in training_v3.py
            model_features = {
                "Category": product.category or "Unknown", 
                "Days_Left": days_to_expiry, 
                "Sales_Last_Week": sales_last_week, 
                "Stock_Available": total_stock
            }
            features_list.append(model_features)
            
            # Also add to the report_list for final display
            report_list.append({
                "product_id": product.id, "name": product.name, 
                "total_stock": total_stock, 
                "nearest_expiry": nearest_expiry_date.isoformat() if nearest_expiry_date else None, 
                "days_to_expiry": days_to_expiry if nearest_expiry_date else None, 
                "sales_last_week": sales_last_week
            })

    if not features_list: 
        print(f"--- AGENT [User: {current_user.username}]: No products with stock found for this user. ---")
        return []

    print(f"--- AGENT (Decide): Getting smart predictions for {len(features_list)} items... ---")
    predicted_discounts_raw = []
    try:
        # *** THIS IS THE CRITICAL FIX: Create the DataFrame ***
        # Create the DataFrame *from the list of dictionaries*
        features_df = pd.DataFrame(features_list)
        
        # Ensure the columns are in the order the model expects
        # (This is the most robust way to do it)
        required_model_cols = ["Category", "Days_Left", "Stock_Available", "Sales_Last_Week"]
        features_df = features_df[required_model_cols]
        
        if not features_df.empty: 
            predicted_discounts_raw = model.predict(features_df)
    except Exception as e: 
        print(f"--- ERROR [User: {current_user.username}] during model prediction: {e} ---")
        print("--- Features sent to model: ---")
        print(features_df.head())
        print("--- Make sure this matches the training script! ---")
        raise HTTPException(status_code=500, detail=f"Model prediction error: {e}")

    print(f"--- AGENT (Act): Applying smart discounts for user '{current_user.username}'... ---")
    final_report = []
    
    for i, report_item in enumerate(report_list):
        status = "OK"
        days_left = report_item["days_to_expiry"]
        
        if days_left is not None and days_left <= 0: 
            status = "Wasted / Remove"
            discount_pct = None # No discount on wasted items
        else:
            # --- *** THIS IS THE "FULL AI" LOGIC (NO HARD RULES) *** ---
            
            # 1. Get the AI's prediction
            raw_prediction = predicted_discounts_raw[i] if i < len(predicted_discounts_raw) else 0.0
            
            # 2. Clean and clip the AI's answer
            discount_pct = 0.0 if pd.isna(raw_prediction) else round(np.clip(raw_prediction, 0, 50), 2)
            
            # 3. Determine the STATUS based on urgency and the AI's decision
            # (We removed the 50% hard rule)
            if days_left is not None and days_left <= 3:
                status = "Urgent Discount!"
            elif days_left is not None and days_left <= 10: # Check up to 10 days
                status = "Expiring Soon"
            elif discount_pct > 0.1: # If AI suggests a discount for non-expiring
                status = "AI Discount"
        
        # Show all items that this user has in stock, regardless of status
        # This is a change to show a "full" report
        report_item["status"] = status
        report_item["predicted_discount_percent"] = discount_pct
        final_report.append(report_item)

    final_report_sorted = sorted(final_report, key=lambda x: x['days_to_expiry'] if x['days_to_expiry'] is not None else 9999)
    print(f"--- AGENT [User: {current_user.username}]: Smart report generated with {len(final_report_sorted)} items. ---")
    return final_report_sorted

# --- Allow running directly ---
if __name__ == "__main__":
    import uvicorn
    print("--- Starting server in __main__ block ---")
    # This mount is for running directly, it duplicates the one above but is fine
    if not any(route.path == '/static' for route in app.routes if hasattr(route, 'path')):
         app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static_run")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

