import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import charset_normalizer
import httpx

# Constants
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDU1OTdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.mGtFocaNamOEpoh3Y6WUB-xoAJJzW3EQntzLwbHUSXg"

def load_data(file_path):
    """Load CSV data with encoding detection."""
    with open(file_path, 'rb') as f:
        result = charset_normalizer.detect(f.read())
    encoding = result['encoding']
    return pd.read_csv(file_path, encoding=encoding)

def analyze_data(df):
    """Perform basic data analysis."""
    numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns
    analysis = {
        'summary': df.describe(include='all').to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'correlation': numeric_df.corr().to_dict()  # Compute correlation only on numeric columns
    }
    return analysis

def visualize_data(df, output_dir):
    """
    Generate and save visualizations to the specified output directory.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    sns.set(style="whitegrid")
    numeric_columns = df.select_dtypes(include=['number']).columns
    for column in numeric_columns:
        plt.figure()
        sns.histplot(df[column].dropna(), kde=True)
        plt.title(f'Distribution of {column}')
        plt.savefig(os.path.join(output_dir, f'{column}_distribution.png'))
        plt.close()
    print(f"Visualizations saved to {output_dir}")

def generate_narrative(analysis):
    """Generate narrative using LLM."""
    headers = {
        'Authorization': f'Bearer {AIPROXY_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Summarize the analysis
    summary_text = (
        f"Dataset summary: {analysis['summary']}\n"
        f"Missing values: {analysis['missing_values']}\n"
    )
    prompt = f"Provide a detailed analysis based on the following summary: {summary_text}"
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = httpx.post(API_URL, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return "Narrative generation failed due to an error."

def main():
    dataset_name = "goodreads"  # Replace with dynamic naming if needed
    output_dir = os.path.join("D:\\VS CODE VENV", dataset_name)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory set to: {output_dir}")

    # File path for the input file
    file_path = r"D:\VS CODE VENV\goodreads.csv"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Load data and perform analysis
    df = load_data(file_path)
    if df is None:
        print("Failed to load data. Exiting.")
        return

    analysis = analyze_data(df)
    if analysis is None:
        print("Data analysis failed. Exiting.")
        return

    # Visualize data
    visualize_data(df, output_dir)

    # Generate narrative
    narrative = generate_narrative(analysis)

    # Save narrative to README.md
    readme_path = os.path.join(output_dir, 'README.md')
    try:
        with open(readme_path, 'w') as f:
            f.write(narrative)
        print(f"Narrative saved to {readme_path}")
    except Exception as e:
        print(f"Error saving narrative: {e}")

if __name__ == "__main__":
    main()
