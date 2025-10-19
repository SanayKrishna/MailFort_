import pandas as pd
import os

def create_master_dataset():
    print("Combining datasets...")

    data_folder = 'datasets'
    
    csv_files = [
        'CEAS_08.csv',
        'Enron.csv',
        'Ling.csv',
        'Nazario.csv',
        'Nigerian_Fraud.csv',
        'phishing_email.csv',
        'SpamAssasin.csv'
    ]

    all_data = []

    for file_name in csv_files:
        file_path = os.path.join(data_folder, file_name)
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found, skipping: {file_path}")
            continue
            
        print(f"Processing {file_path}...")
        try:
            df = pd.read_csv(file_path, encoding='latin1')
            df_clean = None

            if file_name == 'phishing_email.csv':
                text_column_name = 'text_combined'
                label_column_name = 'label'
                
                print(f"  -> Applying special rule for '{file_name}': text='{text_column_name}', label='{label_column_name}'")
                df_clean = df[[text_column_name, label_column_name]].rename(columns={
                    text_column_name: 'text',
                    label_column_name: 'label'
                })
            else:
                text_col, label_col = None, None
                
                possible_text_cols = ['text', 'body', 'message', 'email text']
                possible_label_cols = ['label', 'class', 'target', 'classification', 'type']
                
                for col in df.columns:
                    if col.lower() in possible_text_cols:
                        text_col = col
                    if col.lower() in possible_label_cols:
                        label_col = col
                
                if not text_col or not label_col:
                    print(f"Warning: Could not automatically find text/label columns in {file_name}. Skipping.")
                    continue
                
                df_clean = df[[text_col, label_col]].rename(columns={text_col: 'text', label_col: 'label'})
            
            if df_clean is not None:
                all_data.append(df_clean)

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    master_df = pd.concat(all_data, ignore_index=True)

    master_df.dropna(inplace=True)
    master_df.drop_duplicates(subset=['text'], inplace=True)

    master_df['label'] = master_df['label'].astype(str).str.lower()
    master_df['label'] = master_df['label'].replace({
        'phishing': 'spam', 
        '1': 'spam', 
        '0': 'ham', 
        'benign': 'ham',
        'safe email': 'ham'
    })
    master_df = master_df[master_df['label'].isin(['spam', 'ham'])]

    output_path = os.path.join(data_folder, 'master_dataset.csv')
    master_df.to_csv(output_path, index=False)
    
    print("\n---------------------------------")
    print(f"Successfully created '{output_path}'")
    print(f"Total unique emails in the new dataset: {len(master_df)}")
    print("Final Label distribution:")
    print(master_df['label'].value_counts())
    print("---------------------------------")


if __name__ == '__main__':
    create_master_dataset()