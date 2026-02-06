import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

print("--- Phase 2: Generating 60,000-row regression dataset ---")
print("Filename: supermarket_v2.csv")

# --- 1. Base Product Definitions ---
products = {
    101: {'name': 'Fresh Milk', 'category': 'Dairy', 'base_mrp': 3.00},
    102: {'name': 'Cheddar Cheese', 'category': 'Dairy', 'base_mrp': 5.50},
    103: {'name': 'Yogurt', 'category': 'Dairy', 'base_mrp': 1.50},
    201: {'name': 'Chicken Breast', 'category': 'Meat', 'base_mrp': 7.00},
    202: {'name': 'Ground Beef', 'category': 'Meat', 'base_mrp': 6.00},
    301: {'name': 'Apples', 'category': 'Produce', 'base_mrp': 0.50},
    302: {'name': 'Bananas', 'category': 'Produce', 'base_mrp': 0.30},
    401: {'name': 'Baguette', 'category': 'Bakery', 'base_mrp': 2.50},
    402: {'name': 'Croissant', 'category': 'Bakery', 'base_mrp': 1.20},
    501: {'name': 'Soda (6-pack)', 'category': 'Beverage', 'base_mrp': 8.00},
    601: {'name': 'Frozen Pizza', 'category': 'Frozen', 'base_mrp': 6.50},
}

seasons = ['Normal', 'Festive', 'Off']
n_rows = 60000
data = []

# --- 2. Generate 60,000 Rows ---
for i in range(n_rows):
    if i % 5000 == 0:
        print(f"Generated {i} rows...")
        
    # --- Basic Attributes ---
    prod_id = random.choice(list(products.keys()))
    product = products[prod_id]
    
    product_name = product['name']
    category = product['category']
    mrp = round(product['base_mrp'] * np.random.uniform(0.95, 1.05), 2)
    
    # --- Core Predictive Attributes ---
    expiry_days = np.random.randint(1, 45) # Wider range for regression
    stock_available = np.random.randint(10, 500)
    units_sold_last_week = np.random.randint(5, 700)
    
    # Create a 'demand_trend'
    demand_trend = (units_sold_last_week / (stock_available + 1))
    demand_trend_normalized = min(1.0, demand_trend / 5.0) # Normalize to 0-1
    
    customer_rating = round(np.random.uniform(2.5, 5.0), 1)
    season = random.choice(seasons)

    # --- 3. Target Column: The "Perfect" Discount (Regression) ---
    # This is the complex logic our model will learn
    discount = 0.0
    
    if expiry_days <= 3:
        discount = 0.30  # Base 30%
    elif expiry_days <= 7:
        discount = 0.15  # Base 15%
    elif expiry_days <= 14:
        discount = 0.05  # Base 5%

    # High stock / low demand increases discount
    if stock_available > 300 and demand_trend_normalized < 0.3:
        discount += 0.10
        
    # Low stock / high demand REDUCES discount
    if stock_available < 50 and demand_trend_normalized > 0.7:
        discount -= 0.05 
        
    # Seasonal impact
    if season == 'Festive' and demand_trend_normalized > 0.5:
        discount -= 0.05 # Sells anyway
    if season == 'Off' and demand_trend_normalized < 0.3:
        discount += 0.10 # Needs extra push

    # Perishable categories are more sensitive
    if category in ['Bakery', 'Meat']:
        discount += 0.05
        
    # Final cleanup & noise
    discount = np.clip(discount, 0.0, 0.5) # Clamp between 0% and 50%
    discount = round(discount + np.random.uniform(-0.02, 0.02), 3) # Add noise
    discount = np.clip(discount, 0.0, 0.5) # Re-clamp

    data.append([
        prod_id, product_name, category, expiry_days, units_sold_last_week,
        stock_available, demand_trend_normalized, customer_rating, season, mrp,
        discount # This is our continuous target
    ])

# --- 4. Create and Save DataFrame ---
columns = [
    'Product_ID', 'Product_Name', 'Category', 'Expiry_Days', 'Units_Sold_Last_Week',
    'Stock_Available', 'Demand_Trend', 'Customer_Rating', 'Season', 'MRP', 'Discount_Pct'
]
df = pd.DataFrame(data, columns=columns)

df.to_csv('supermarket_v2.csv', index=False)
print(f"--- ✅ Success! Generated supermarket_v2.csv with {len(df)} rows. ---")