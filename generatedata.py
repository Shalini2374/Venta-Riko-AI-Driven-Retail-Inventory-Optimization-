import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker

# --- 0. Setup ---
fake = Faker()
print("Generating Phase 1 Dataset: supermarket_v1_classification.csv")

# --- 1. Base Product Definitions (Simulates your 'Product Database') ---
products = [
    {'name': 'Fresh Milk', 'category': 'Dairy', 'manufacturer': 'FarmFresh', 'shelf_life': 12},
    {'name': 'Cheddar Cheese', 'category': 'Dairy', 'manufacturer': 'DairyLand', 'shelf_life': 60},
    {'name': 'Chicken Breast', 'category': 'Meat', 'manufacturer': 'Quality Meats', 'shelf_life': 7},
    {'name': 'Ground Beef', 'category': 'Meat', 'manufacturer': 'Quality Meats', 'shelf_life': 5},
    {'name': 'Apples', 'category': 'Produce', 'manufacturer': 'Orchard Gold', 'shelf_life': 25},
    {'name': 'Bananas', 'category': 'Produce', 'manufacturer': 'Tropicana', 'shelf_life': 8},
    {'name': 'Baguette', 'category': 'Bakery', 'manufacturer': 'DailyBread', 'shelf_life': 3},
    {'name': 'Soda (6-pack)', 'category': 'Beverage', 'manufacturer': 'Bubbly Co.', 'shelf_life': 180},
    {'name': 'Frozen Pizza', 'category': 'Frozen', 'manufacturer': 'QuickMeals', 'shelf_life': 365},
    {'name': 'Yogurt', 'category': 'Dairy', 'manufacturer': 'DairyLand', 'shelf_life': 20},
]

sales_trends = ['Low', 'Medium', 'High']
n_rows = 20000
data = []
today = datetime.now().date()

# --- 2. Generate 20,000 Rows ---
for i in range(n_rows):
    if i % 2000 == 0:
        print(f"Generated {i} rows...")
        
    # Pick a base product
    prod = random.choice(products)
    
    # Simulate dates
    shelf_life_days = int(prod['shelf_life'] * np.random.uniform(0.8, 1.2)) # Add variability
    mfg_date = today - timedelta(days=np.random.randint(0, shelf_life_days))
    expiry_date = mfg_date + timedelta(days=shelf_life_days)
    
    # Format dates as requested
    mfg_date_str = mfg_date.strftime('%d/%m/%Y')
    expiry_date_str = expiry_date.strftime('%d/%m/%Y')
    
    # Calculate the MOST important feature
    days_to_expiry = (expiry_date - today).days

    # Simulate inventory and sales
    stock_quantity = np.random.randint(10, 300)
    sales_trend = random.choice(sales_trends)
    
    # --- 3. The Core Classification Logic (Target Column) ---
    # This is what the Decision Tree will learn
    
    discount_band = '0%' # Default
    
    if days_to_expiry <= 3:
        discount_band = '20%' # Urgent
    elif days_to_expiry <= 7 and (sales_trend == 'Low' or prod['category'] in ['Meat', 'Bakery']):
        discount_band = '15%'
    elif days_to_expiry <= 14 and (sales_trend == 'Low' or stock_quantity > 200):
        discount_band = '10%'
    elif days_to_expiry <= 25 and sales_trend == 'Low' and stock_quantity > 250:
        discount_band = '5%'
    elif prod['category'] == 'Dairy' and days_to_expiry <= 10 and sales_trend != 'High':
        discount_band = '5%'

    # Add some noise to prevent 100% perfect rules
    if np.random.rand() > 0.95: 
        discount_band = random.choice(['0%', '5%', '10%', '15%', '20%'])

    # Append data
    data.append([
        prod['name'],
        prod['category'],
        mfg_date_str,
        expiry_date_str,
        prod['manufacturer'],
        stock_quantity,
        sales_trend,
        days_to_expiry,  # We include this for the model
        discount_band    # The target
    ])

# --- 4. Create and Save DataFrame ---
columns = [
    'Product_Name', 'Category', 'Manufacture_Date', 'Expiry_Date', 
    'Manufacturer', 'Stock_Quantity', 'Sales_Trend', 'Days_to_Expiry',
    'Discount_Band' # Our Target
]
df = pd.DataFrame(data, columns=columns)

# Filter out any weird edge cases (e.g., expired items)
df = df[df['Days_to_Expiry'] > 0]

# This is the line that saves the file
df.to_csv('supermarket_v1_classification.csv', index=False)

print(f"\n--- Success! ---")
print(f"Generated {len(df)} rows and saved to 'supermarket_v1_classification.csv'")
print(df.head())