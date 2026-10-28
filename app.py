# app.py (V3 - FINAL PRODUCTION VERSION with Whitelist)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import joblib
import re
import pandas as pd
from scipy.sparse import hstack
from urlextract import URLExtract
from email_fetcher import fetch_latest_emails

app = Flask(__name__)
CORS(app)

# --- LOAD V3 MODEL, VECTORIZER, AND CONSTANTS ---
model = joblib.load('phishing_model_v3.pkl')
vectorizer = joblib.load('vectorizer_v3.pkl')
extractor = URLExtract()

with open('public_suffix_list.dat', 'r', encoding='utf-8', errors='ignore') as f:
    common_tlds = {line.strip() for line in f if not line.startswith('//') and '.' not in line}

# --- THE WHITELIST: THE SENIOR ANALYST'S RULEBOOK ---
WHITELISTED_DOMAINS = {
    'google.com', 'reddit.com', 'microsoft.com', 'github.com',
    'amazon.com', 'apple.com', 'paypal.com', 'youtube.com',
    'substack.com', 'mcafee.com' # Added based on your screenshot
}

def is_allowlisted(domain):
    """
    True if domain is a trusted domain or a subdomain of one.
    Matches on a dot boundary, so accounts.google.com passes but evilgoogle.com does not.
    """
    domain = (domain or "").lower().rstrip(".")
    return any(domain == d or domain.endswith("." + d) for d in WHITELISTED_DOMAINS)


# --- THE DEFINITIVE V3 ANALYSIS FUNCTION ---
def analyze_email_details(full_email_text, from_address=None):
    """
    Analyzes email text using a hybrid approach: Whitelist first, then the V3 AI model.
    """
    domain_str = 'unknown.domain'
    if from_address:
        match = re.search(r'@([\w.-]+)', from_address)
        if match:
            domain_str = match.group(1).lower()

    # --- STEP 1: THE WHITELIST OVERRIDE ---
    # Trusted sender domain (or subdomain) skips the model.
    if is_allowlisted(domain_str):
        return {
            'result': 'SAFE',
            'confidence': '100.00%',
            'url_count': len(extractor.find_urls(full_email_text)),
            'keywords_str': 'WHITELIST_OVERRIDE',
            'override': True
        }

    # --- STEP 2: IF NOT WHITELISTED, PROCEED WITH AI ANALYSIS ---
    domain_length = len(domain_str)
    subdomain_count = domain_str.count('.')
    has_hyphen = 1 if '-' in domain_str else 0
    is_common_tld = 1 if domain_str.split('.')[-1] in common_tlds else 0
    url_count = len(extractor.find_urls(full_email_text))
    suspicious_keywords_list = [
        'verify', 'urgent', 'password', 'suspended', 'account', 'login', 'bank',
        'invoice', 'payment', 'confirm', 'unusual activity', 'secure', 'support',
        'alert', 'important', 'congratulations', 'winner', 'free', 'prize'
    ]
    keyword_count = sum(keyword in full_email_text.lower() for keyword in suspicious_keywords_list)
    text_length = len(full_email_text)
    uppercase_ratio = sum(1 for c in full_email_text if c.isupper()) / (text_length + 1)
    
    text_vec = vectorizer.transform([full_email_text])
    numerical_features = pd.DataFrame([[
        url_count, keyword_count, text_length, uppercase_ratio,
        domain_length, subdomain_count, has_hyphen, is_common_tld
    ]])
    combined_features = hstack([text_vec, numerical_features.astype(float)])

    prediction = model.predict(combined_features)[0]
    probability = model.predict_proba(combined_features)[0]

    result = "PHISHING" if prediction == 1 else "SAFE"
    confidence = f"{probability[prediction]:.2%}"
    
    return {
        'result': result, 'confidence': confidence, 'url_count': url_count,
        'keywords_str': ' '.join([kw for kw in suspicious_keywords_list if kw in full_email_text.lower()]) or 'NONE_FOUND',
        'override': False
    }

# --- FLASK ROUTES (No changes from here) ---
@app.route('/')
def home():
    return render_template('index.html', active_tab='inbox')

@app.route('/analyze_manual', methods=['POST'])
def analyze_manual():
    email_text = request.form.get('email_text')
    details = None
    if email_text:
        from_in_text = re.search(r'From:.*', email_text, re.IGNORECASE)
        sender = from_in_text.group(0) if from_in_text else None
        details = analyze_email_details(email_text, from_address=sender)
    return render_template('index.html', details=details, email_text=email_text, active_tab='manual')

@app.route('/fetch_emails_api', methods=['GET'])
def fetch_emails_api():
    try:
        num_to_fetch = request.args.get('count', default=10, type=int)
        emails = fetch_latest_emails(num_emails=num_to_fetch)
        analyzed_emails = []
        for email in emails:
            full_content = email.get('subject', '') + " " + email.get('body', '')
            sender = email.get('from', 'N/A')
            details = analyze_email_details(full_content, from_address=sender)
            email_data = {
                'from': sender, 'subject': email.get('subject', 'N/A'),
                'body': email.get('body', ''), 'analysis': details 
            }
            analyzed_emails.append(email_data)
        return jsonify({'status': 'success', 'emails': analyzed_emails})
    except Exception as e:
        print(f"An error occurred in fetch_emails_api: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)