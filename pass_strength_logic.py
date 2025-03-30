import random
import string
import sqlite3
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
import numpy as np

db_path = os.path.join(os.path.dirname(__file__), 'password_data.db')

def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            length INTEGER,
            uppercase INTEGER,
            digits INTEGER,
            special INTEGER,
            strength FLOAT,
            pattern TEXT
        )
    ''')
    conn.commit()
    conn.close()

def extract_features(password):
    return {
        'length': len(password),
        'uppercase': sum(1 for c in password if c.isupper()),
        'digits': sum(1 for c in password if c.isdigit()),
        'special': sum(1 for c in password if c in string.punctuation),
        'pattern': ''.join('U' if c.isupper() else 'L' if c.islower() else 'D' if c.isdigit() else 'S' for c in password)
    }

def store_password_data(password, strength):
    features = extract_features(password)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO password_patterns (length, uppercase, digits, special, strength, pattern)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (features['length'], features['uppercase'], features['digits'], features['special'], strength, features['pattern']))
    conn.commit()
    conn.close()

def train_model():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM password_patterns", conn)
    conn.close()
    
    if len(df) < 5:
        return None, None
        
    X = df[['length', 'uppercase', 'digits', 'special']]
    y = df['strength']
    
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    
    patterns = df['pattern'].tolist()
    return model, patterns

def check_password_strength(password):
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = sum(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)
    
    strength = 0
    rules_failed = []
    
    if length < 9:
        rules_failed.append("Length should be at least 9 characters")
    else:
        strength += 0.25
        
    if not has_upper:
        rules_failed.append("Should contain uppercase letters")
    else:
        strength += 0.25
        
    if has_digit < 3:
        rules_failed.append("Should contain at least 3 numbers")
    else:
        strength += 0.25
        
    if not has_special:
        rules_failed.append("Should contain special characters")
    else:
        strength += 0.25
        
    if not rules_failed:
        classification = "Strong"
    elif strength >= 0.5:
        classification = "Medium"
    elif strength >= 0.25:
        classification = "Weak"
    else:
        classification = "Very Weak"
        
    return classification, strength, rules_failed

def generate_password_from_pattern(pattern):
    password = []
    for c in pattern:
        if c == 'U':
            password.append(random.choice(string.ascii_uppercase))
        elif c == 'L':
            password.append(random.choice(string.ascii_lowercase))
        elif c == 'D':
            password.append(random.choice(string.digits))
        elif c == 'S':
            password.append(random.choice(string.punctuation))
    return ''.join(password)

def improve_password_ml(password, model, patterns):
    features = extract_features(password)
    base_vector = np.array([[features['length'], features['uppercase'], features['digits'], features['special']]])
    
    if not patterns:
        return improve_password_basic(password)
    
    similar_patterns = random.sample(patterns, min(3, len(patterns)))
    suggestions = []
    
    for pattern in similar_patterns:
        suggested = generate_password_from_pattern(pattern)
        if len(suggested) < len(password):
            suggested = password[:len(suggested)] + suggested
        suggestions.append(suggested)
    
    return suggestions

def improve_password_basic(password):
    improved = list(password)
    special_chars = "!@#$%^&*"
    
    while len(improved) < 9:
        improved.append(str(random.randint(0, 9)))
    
    if not any(c.isupper() for c in improved):
        pos = random.randint(0, len(improved)-1)
        if improved[pos].islower():
            improved[pos] = improved[pos].upper()
        else:
            improved.append(random.choice(string.ascii_uppercase))
    
    digit_count = sum(c.isdigit() for c in improved)
    while digit_count < 3:
        improved.append(str(random.randint(0, 9)))
        digit_count += 1
    
    if not any(c in string.punctuation for c in improved):
        improved.append(random.choice(special_chars))
    
    base = ''.join(improved)
    return [base, base + ''.join(random.choices(string.ascii_letters + string.digits + special_chars, k=2)),
            base + ''.join(random.choices(string.ascii_letters + string.digits + special_chars, k=3))]

def main():
    create_database()
    
    while True:
        password = input("\nEnter your password (or 'exit' to quit): ")
        if password.lower() == 'exit':
            break
            
        classification, strength, rules_failed = check_password_strength(password)
        print(f"\nPassword Strength: {classification}")
        print(f"Score: {strength:.2f}")
        
        store_password_data(password, strength)
        
        if rules_failed:
            print("Missing Requirements:", rules_failed)
            
        if classification in ["Very Weak", "Weak", "Medium"]:
            model, patterns = train_model()
            if model:
                suggestions = improve_password_ml(password, model, patterns)
            else:
                suggestions = improve_password_basic(password)
                
            print("\nHere are some suggested improvements based on your password:")
            for i, suggestion in enumerate(suggestions, 1):
                sugg_class, sugg_strength, _ = check_password_strength(suggestion)
                print(f"\nSuggestion {i}: {suggestion}")
                print(f"New Strength: {sugg_class} (Score: {sugg_strength:.2f})")
        else:
            print("\nYour password is already strong!")

if __name__ == "__main__":
    main()
