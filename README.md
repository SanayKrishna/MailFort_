# MailFort

A phishing email classifier with a small Flask front end. You can paste an email in by hand or pull the latest messages from an inbox over IMAP, and each one comes back labelled SAFE or PHISHING with a confidence score and the suspicious keywords it contained.

## How it works

Classification is a two-step check:

1. **Sender allowlist.** If the sender's domain ends in one of a short list of trusted domains (google.com, microsoft.com, github.com and a few others), the email is marked SAFE and the model is skipped.
2. **Model.** Everything else goes through a Random Forest (100 trees) trained on two kinds of features combined into one matrix:
   - TF-IDF over the email text (top 5,000 terms, English stop words removed)
   - eight hand-built features: URL count, suspicious keyword count, text length, uppercase ratio, sender domain length, subdomain count, hyphen in the domain, and whether the TLD is a common one

The training data is seven public email corpora merged into one labelled set: CEAS-08, Enron, Ling, Nazario, Nigerian Fraud, SpamAssassin and a phishing email set. `train_v3.py` holds out 20% (stratified) and prints a classification report before saving the model.

## Run it

Python 3.10 or newer.

```bash
git clone https://github.com/SanayKrishna/MailFort_.git
cd MailFort_
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The datasets and the trained model are not in the repo (they are too large). To build them:

1. Put the seven CSVs listed in `combine_datasets.py` into `datasets/`.
2. Download Mozilla's `public_suffix_list.dat` into the repo root. Both the feature extractor and the app read it.
3. Build the dataset and train:

```bash
python combine_datasets.py      # writes datasets/master_dataset.csv
python feature_extractor.py     # writes datasets/features_dataset_v3.csv
python train_v3.py              # writes phishing_model_v3.pkl and vectorizer_v3.pkl
```

For inbox scanning, create a `.env` file in the root:

```env
EMAIL_USER=you@example.com
EMAIL_PASS=your-app-password
IMAP_SERVER=imap.gmail.com
```

Use an app password, not your main account password. Then start the app:

```bash
python app.py
```

Open http://127.0.0.1:5000. The Inbox tab fetches and scores recent emails, and the Manual tab scores whatever you paste in.

## Project layout

```text
app.py                Flask routes and the allowlist + model check
email_fetcher.py      IMAP fetch over SSL
combine_datasets.py   merges the seven source corpora
feature_extractor.py  builds the numeric features
train_v3.py           trains and evaluates the model
templates/, static/   the web UI
```

## Known limitations

- The allowlist uses a plain suffix match, so a lookalike domain such as `evilgoogle.com` passes as `google.com`. It should match on a dot boundary (`== d` or `.endswith("." + d)`).
- Labels are binary. Spam and phishing are treated as the same class, so a marketing email can be flagged as phishing.
- The model only sees text and sender features. It does not inspect attachments, headers such as SPF or DKIM results, or where the links actually point.
