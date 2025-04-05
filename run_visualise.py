import os
import time
import json
import pandas as pd
from openai import OpenAI

def read_json(file_path):
    """
    Read JSON file from the given path and return the data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

dirname = os.getcwd()
config_path = os.path.join(dirname, 'config')
log_path = os.path.join(dirname, 'logs')
output_directory = "output"

info = read_json(os.path.join(config_path, 'info.json'))
GPT_MODEL = info.get('GPT_4')

def visualize(results_df):
    """
    Simple visualization function that ensures it always returns a matplotlib figure.
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server environments
    
    # Debug the input
    print(f"Visualize received data type: {type(results_df)}")
    
    # Create a figure for any result type
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Handle error case - string input
    if isinstance(results_df, str):
        ax.text(0.5, 0.5, "Cannot visualize string input", fontsize=14, ha='center', va='center')
        ax.text(0.5, 0.4, results_df[:100] + "..." if len(results_df) > 100 else results_df, 
                fontsize=10, ha='center', va='center', wrap=True)
        ax.axis('off')
        return fig
        
    # Handle non-DataFrame input
    if not isinstance(results_df, pd.DataFrame):
        ax.text(0.5, 0.5, f"Cannot visualize {type(results_df).__name__}", 
                fontsize=14, ha='center', va='center')
        ax.axis('off')
        return fig
    
    # Check for empty DataFrame
    if results_df.empty:
        ax.text(0.5, 0.5, "No data to visualize (empty DataFrame)", 
                fontsize=14, ha='center', va='center')
        ax.axis('off')
        return fig
    
    print(f"Visualizing DataFrame with columns: {results_df.columns.tolist()}")
    
    # For simplicity, create a basic bar chart for any data with numeric columns
    numeric_cols = results_df.select_dtypes(include=['number']).columns.tolist()
    string_cols = results_df.select_dtypes(include=['object']).columns.tolist()
    
    # Choose what to plot based on available columns
    if numeric_cols:
        # We have numeric data to plot
        value_col = numeric_cols[0]  # Use first numeric column
        
        if string_cols:
            # We have a string column to use as categories
            category_col = string_cols[0]
            # Limit to 20 rows for readability and sort by value
            plot_df = results_df.sort_values(by=value_col, ascending=False).head(20)
            plot_df.plot(kind='bar', x=category_col, y=value_col, ax=ax, color='skyblue')
            plt.xticks(rotation=45, ha='right')
            ax.set_xlabel(category_col)
        else:
            # No string columns, plot numeric column against index
            plot_df = results_df.head(20)
            plot_df.plot(kind='bar', y=value_col, ax=ax, color='skyblue')
            ax.set_xlabel("Index")
        
        # Set title and labels
        ax.set_title(f"Data Visualization: {value_col}")
        ax.set_ylabel(value_col)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        # No numeric data, create a text display
        ax.text(0.5, 0.8, "Data Preview (no numeric columns to plot)", 
                fontsize=14, ha='center', va='center')
        
        # Display the first few rows as text
        if string_cols:
            col = string_cols[0]
            for i, val in enumerate(results_df[col].head(8)):
                ax.text(0.5, 0.7 - i*0.07, str(val)[:50], 
                       fontsize=10, ha='center')
        
        ax.axis('off')
    
    plt.tight_layout()
    
    # Save the figure with a timestamp to avoid conflicts
    try:
        os.makedirs(output_directory, exist_ok=True)
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = os.path.join(output_directory, f"Chart_{timestamp}.png")
        plt.savefig(output_file_name)
        print(f"Figure saved as {output_file_name}")
    except Exception as e:
        print(f"Warning: Could not save figure: {e}")
    
    # Always return the figure object
    return fig

if __name__ == "__main__":
    # Example DataFrame
    results_df = pd.DataFrame({
        'protein1': ['GAPDH', 'ACTB', 'TP53', 'AKT1', 'MYC'],
        'frequency': [9357, 7773, 7443, 7179, 7147]
    })
    visualize(results_df)