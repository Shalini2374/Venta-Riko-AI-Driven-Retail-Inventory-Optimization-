import pandas as pd
import numpy as np

print("Generating new 'supermarket_v3.csv' with realistic discount curves...")

# Number of samples
n_samples = 5000

# Base categories and their perishability (discount multiplier)
categories = {
    "Dairy": 1.2,
    "Bakery": 1.3,
    "Meat": 1.25,
    "Produce": 1.1,
    "Beverage": 0.8,
    "Pantry": 0.9,
    "Frozen": 0.7
}

data = {
    "Category": np.random.choice(list(categories.keys()), n_samples),
    "Days_Left": np.random.randint(1, 90, n_samples),
    "Stock_Available": np.random.randint(10, 200, n_samples),
    "Sales_Last_Week": np.random.randint(0, 100, n_samples)
}

df = pd.DataFrame(data)

# --- This is the new, smart discount logic ---
def calculate_target_discount(row):
    days = row["Days_Left"]
    perish_multiplier = categories[row["Category"]]
    
    # Calculate stock-to-sales ratio (how much "excess" stock there is)
    # Higher ratio means more excess, so higher discount
    stock_ratio = row["Stock_Available"] / (row["Sales_Last_Week"] + 1)
    ratio_multiplier = np.clip(stock_ratio / 10, 0.8, 1.5) # e.g. 70 stock / 7 sales = 10 ratio
    
    # 1. Base discount curve (non-linear)
    if days > 30:
        base_discount = 0
    elif days > 14:
        # Gradual increase from 30 days (0%) to 15 days (5%)
        base_discount = 5 * (1 - (days - 15) / 15) 
    elif days > 7:
        # Steeper increase from 14 days (5%) to 8 days (15%)
        base_discount = 5 + 10 * (1 - (days - 8) / 6)
    elif days > 3:
        # Even steeper from 7 days (15%) to 4 days (35%)
        base_discount = 15 + 20 * (1 - (days - 4) / 3)
    else:
        # Max discount from 3 days (35%) to 1 day (50%)
        base_discount = 35 + 15 * (1 - (days - 1) / 2)
        
    # 2. Apply multipliers
    final_discount = base_discount * perish_multiplier * ratio_multiplier
    
    # 3. Clip to 0-50% range and add noise
    noise = np.random.normal(0, 2) # Add some randomness
    final_discount = np.clip(final_discount + noise, 0, 50)
    
    # 4. Round to 2 decimal places
    return round(final_discount, 2)

df["Target_Discount"] = df.apply(calculate_target_discount, axis=1)

# Save the new dataset
df.to_csv("supermarket_v3.csv", index=False)

print(f"Successfully created 'supermarket_v3.csv' with {n_samples} samples.")
print("\nExample data:")
print(df.sample(5))
