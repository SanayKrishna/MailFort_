# feature_extractor.py (V3 - with FINAL encoding fix)
import pandas as pd
from urlextract import URLExtract
from tqdm import tqdm
import re

tqdm.pandas()

# --- THIS IS THE DEFINITIVE FIX ---
# We tell Python to use 'utf-8', and if it finds any invalid characters,
# simply ignore them and move on. This is safe for this file.
with open('public_suffix_list.dat', 'r', encoding='utf-8', errors='ignore') as f:
    common_tlds = {line.strip() for line in f if not line.startswith('//') and '.' not in line}

def get_domain_from_text(text):
    # Simple regex to find the first 'From: ... <email@domain.com>'
    match = re.search(r'From:.*?@([\w.-]+)', text, re.IGNORECASE)
    return match.group(1) if match else None

def extract_all_features(df):
    extractor = URLExtract()
    
    print("Extracting text-based features...")
    df['url_count'] = df['text'].progress_apply(lambda x: len(extractor.find_urls(x)))
    suspicious_keywords = [
        'verify', 'urgent', 'password', 'suspended', 'account', 'login', 'bank',
        'invoice', 'payment', 'confirm', 'unusual activity', 'secure', 'support',
        'alert', 'important', 'congratulations', 'winner', 'free', 'prize'
    ]
    df['keyword_count'] = df['text'].progress_apply(lambda x: sum(keyword in x.lower() for keyword in suspicious_keywords))
    df['text_length'] = df['text'].progress_apply(len)
    df['uppercase_ratio'] = df['text'].progress_apply(lambda x: sum(1 for c in x if c.isupper()) / (len(x) + 1))
    
    print("Extracting domain features from email text...")
    df['domain'] = df['text'].progress_apply(get_domain_from_text)
    
    df['domain'].fillna('unknown.domain', inplace=True)

    print("Calculating domain reputation features...")
    df['domain_length'] = df['domain'].progress_apply(len)
    df['subdomain_count'] = df['domain'].progress_apply(lambda x: x.count('.'))
    df['has_hyphen'] = df['domain'].progress_apply(lambda x: 1 if '-' in x else 0)
    
    df['is_common_tld'] = df['domain'].progress_apply(
        lambda x: 1 if x.split('.')[-1] in common_tlds else 0
    )
    
    return df

if __name__ == '__main__':
    print("Loading the master dataset...")
    df = pd.read_csv('datasets/master_dataset.csv')
    df.dropna(subset=['text'], inplace=True)
    
    df_features = extract_all_features(df)
    
    final_columns = [
        'text', 'label', 'url_count', 'keyword_count', 'text_length', 
        'uppercase_ratio', 'domain_length', 'subdomain_count', 
        'has_hyphen', 'is_common_tld'
    ]
    df_final = df_features[final_columns]
    
    output_path = 'datasets/features_dataset_v3.csv'
    df_final.to_csv(output_path, index=False)
    
    print(f"\nFeature extraction V3 complete! New dataset saved to: {output_path}")