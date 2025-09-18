import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("--- Model Training Script Started ---")
try:
    data_path = os.path.join('data', 'dropout.csv')
    df = pd.read_csv(data_path, sep=',')
    print("Successfully loaded data file.")
except FileNotFoundError:
    print("Error: Could not find 'data/dropout.csv'.")
    exit()

df['Target'] = df['Target'].map({'Enrolled': 0, 'Graduate': 0, 'Dropout': 1})
X = df.drop('Target', axis=1)
y = df['Target']
for col in X.select_dtypes(include=['object']).columns:
    X[col] = X[col].astype('category').cat.codes

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("Training the AI model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, 'dropout_model.joblib')
print("--- SUCCESS: AI Model saved as 'dropout_model.joblib' ---")