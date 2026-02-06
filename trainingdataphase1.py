import pandas as pd
import numpy as np
import joblib  # This is the library for saving your model
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.tree import export_text # To show the tree logic

print("--- Phase 1: Training the v1 Classification Model ---")

# 1. Load Data
try:
    data = pd.read_csv('supermarket_v1_classification.csv')
    print(f"Loaded {len(data)} rows from supermarket_v1_classification.csv\n")
except FileNotFoundError:
    print("Error: 'supermarket_v1_classification.csv' not found.")
    print("Please run 'generate_data_v1.py' first.")
    exit()

# 2. Feature Engineering
# This simulates your live app calculating 'Days_to_Expiry'
data['Expiry_Date'] = pd.to_datetime(data['Expiry_Date'], format='%d/%m/%Y')
data['Days_to_Expiry'] = (data['Expiry_Date'] - datetime.now()).dt.days

# Filter out any items that are already expired
data = data[data['Days_to_Expiry'] > 0].copy()
print("Refreshed 'Days_to_Expiry' feature.")

# 3. Define Features (X) and Target (y)
# These are the columns the model will learn from
feature_columns = [
    'Category', 
    'Stock_Quantity', 
    'Sales_Trend', 
    'Days_to_Expiry'
]
target_column = 'Discount_Band' # This is what we want to predict

X = data[feature_columns]
y = data[target_column]

# 4. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Training with {len(X_train)} samples, testing with {len(X_test)} samples.\n")

# 5. Define Preprocessing
# We must convert text (like 'Dairy') into numbers (like [1,0,0])
categorical_features = ['Category', 'Sales_Trend']
numeric_features = ['Stock_Quantity', 'Days_to_Expiry']

# 'passthrough' means numeric features don't need changes for a Decision Tree
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('num', 'passthrough', numeric_features)
    ])

# 6. Create the Full Model Pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', DecisionTreeClassifier(max_depth=10, random_state=42))
])

# 7. Train the Model
print("Training Decision Tree Classifier...")
model_pipeline.fit(X_train, y_train)
print("Model training complete.")

# 8. Evaluate the Model
print("\n--- Model Evaluation ---")
y_pred = model_pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 9. SAVE THE MODEL
# This is the important part!
model_filename = 'model_v1.pkl'
joblib.dump(model_pipeline, model_filename)
print(f"\n--- ✅ Successfully saved the trained model as '{model_filename}' ---")

# 10. Show the "Explainable Logic" (The Goal of Phase 1)
print("\n--- Model's Learned Logic (Decision Tree Rules Sample) ---")
try:
    # Get feature names after one-hot encoding
    feature_names = list(model_pipeline.named_steps['preprocessor']
                         .named_transformers_['cat']
                         .get_feature_names_out(categorical_features))
    feature_names.extend(numeric_features) # Add the numeric features

    # Export the rules
    tree_rules = export_text(model_pipeline.named_steps['classifier'], 
                             feature_names=feature_names, 
                             max_depth=5) # Show top 5 levels for brevity
    print(tree_rules)
except Exception as e:
    print(f"Could not export tree rules: {e}")