# train_v3.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.sparse import hstack
import joblib

print("Loading dataset with V3 features...")
df = pd.read_csv('datasets/features_dataset_v3.csv')
df.dropna(inplace=True)

df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# Define our features (X) and target (y)
X_text = df['text']
# ADDED the new domain features
X_numerical = df.drop(columns=['text', 'label'])
y = df['label']

print("Splitting data...")
X_text_train, X_text_test, X_num_train, X_num_test, y_train, y_test = train_test_split(
    X_text, X_numerical, y, test_size=0.2, random_state=42, stratify=y
)

print("Vectorizing text...")
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_text_train_vec = vectorizer.fit_transform(X_text_train)
X_text_test_vec = vectorizer.transform(X_text_test)

print("Combining text and all numerical features...")
X_train_combined = hstack([X_text_train_vec, X_num_train.astype(float)])
X_test_combined = hstack([X_text_test_vec, X_num_test.astype(float)])

print("Training the RandomForestClassifier V3 model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train_combined, y_train)

print("\nEvaluating the V3 model...")
predictions = model.predict(X_test_combined)
print(classification_report(y_test, predictions, target_names=['Safe (Ham)', 'Phishing (Spam)']))

print("Saving the new V3 model and vectorizer...")
joblib.dump(model, 'phishing_model_v3.pkl')
joblib.dump(vectorizer, 'vectorizer_v3.pkl')
print("New model saved as 'phishing_model_v3.pkl' and 'vectorizer_v3.pkl'")