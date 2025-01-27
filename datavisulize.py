import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the dataset (you can replace this with your own file path or database query)
def load_data(file_path):
    return pd.read_csv(file_path)

# Clean data by handling missing values
def clean_data(df):
    # Filling missing values with the median of the respective column
    df.fillna(df.median(), inplace=True)
    
    # Handling outliers by capping the values to the 1st and 99th percentiles
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        lower_percentile = df[column].quantile(0.01)
        upper_percentile = df[column].quantile(0.99)
        df[column] = df[column].clip(lower=lower_percentile, upper=upper_percentile)
    
    return df

# Perform unique data analysis: calculate basic statistics
def analyze_data(df):
    # Display summary statistics
    print("Summary Statistics:")
    print(df.describe())
    
    # Get unique counts for categorical data
    print("\nUnique Value Counts:")
    print(df.nunique())
    
    # Correlation between numeric columns
    print("\nCorrelation Matrix:")
    print(df.corr())

# Visualize data: Plot various types of graphs
def visualize_data(df):
    # Set style
    sns.set(style="whitegrid")
    
    # Histogram of temperature and humidity
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(df['Temperature'], kde=True, color='blue', bins=20)
    plt.title('Temperature Distribution')
    
    plt.subplot(1, 2, 2)
    sns.histplot(df['Humidity'], kde=True, color='green', bins=20)
    plt.title('Humidity Distribution')
    plt.tight_layout()
    plt.show()

    # Scatter plot for Temperature vs Humidity
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x='Temperature', y='Humidity', hue='Motion Detected', palette='coolwarm')
    plt.title('Temperature vs Humidity (Colored by Motion Detection)')
    plt.show()

    # Box plot for Temperature distribution by Motion Detected
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='Motion Detected', y='Temperature', palette='Set2')
    plt.title('Temperature Distribution by Motion Detected')
    plt.show()

# Main function to orchestrate the data analysis and visualization
def main(file_path):
    # Load data
    df = load_data(file_path)
    
    # Clean data
    df = clean_data(df)
    
    # Perform data analysis
    analyze_data(df)
    
    # Visualize data
    visualize_data(df)

# Run the analysis (replace 'your_data.csv' with the actual path to your dataset)
if __name__ == "__main__":
    main('your_data.csv')
