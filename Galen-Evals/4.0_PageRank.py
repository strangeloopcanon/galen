import numpy as np
import pandas as pd

def load_and_prepare_data_from_excel(excel_file_path):
    """
    Load model evaluation data from an Excel file and prepare the normalized scores matrix.
    """
    # Load the data from an Excel file
    df = pd.read_excel(excel_file_path)

    # Determine the number of models dynamically from the columns
    score_columns = [col for col in df.columns if col.endswith('_Score')]
    num_models = len(score_columns)

    # Initialize an empty matrix based on the number of models
    scores = np.zeros((num_models, num_models))

    # Calculate average scores each model gives to each other
    for i, giver_col in enumerate(score_columns):
        for j in range(num_models):
            receiver = f'Model_{j+1}'
            # Get only rows where receiver is the answered model
            mask = df['AnsweredBy'] == receiver
            filtered_scores = df.loc[mask, giver_col]
            if not filtered_scores.empty:
                scores[j, i] = filtered_scores.mean()

    # Normalize the scores to make each column sum to 1
    score_sums = scores.sum(axis=0)
    normalized_scores = scores / score_sums

    return normalized_scores

def pagerank(scores, damping_factor=0.85, max_iterations=100, tolerance=1e-6):
    """
    Calculate PageRank scores given a normalized scores matrix.
    """
    num_models = scores.shape[0]
    pr = np.ones(num_models) / num_models  # Initial PageRank scores
    iteration = 0
    change = 1

    while change > tolerance and iteration < max_iterations:
        new_pr = np.zeros(num_models)
        for i in range(num_models):
            new_pr[i] = damping_factor * np.dot(scores[:, i], pr) + (1 - damping_factor) / num_models
        change = np.linalg.norm(new_pr - pr, 1)  # L1 norm
        pr = new_pr
        iteration += 1

    return pr

def save_scores_to_excel(scores, model_names, file_path):
    """
    Save the PageRank scores to an Excel file.
    """
    scores_df = pd.DataFrame({'Model': model_names, 'PageRank Score': scores})
    scores_df.to_excel(file_path, index=False)

if __name__ == '__main__':
    # Load data and prepare scores matrix from Excel
    excel_file_path = 'files/model_rankings.xlsx'
    normalized_scores = load_and_prepare_data_from_excel(excel_file_path)

    # Compute PageRank scores
    final_scores = pagerank(normalized_scores)
    print("Final PageRank Scores:", final_scores)

    # Saving the PageRank scores to Excel
    model_names = [f'Model_{i+1}' for i in range(len(final_scores))]
    output_excel_path = 'files/PageRank_Scores.xlsx'
    save_scores_to_excel(final_scores, model_names, output_excel_path)
