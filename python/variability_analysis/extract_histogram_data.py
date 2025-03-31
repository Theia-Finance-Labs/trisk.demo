import os
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


def load_data(source):
    """
    Loads the NPV, PD, and parameters datasets from the specified source directory.

    Parameters:
    source (str): The directory containing the CSV files.

    Returns:
    tuple: A tuple containing the NPV dataframe, PD dataframe, and parameters dataframe.
    """
    try:
        npv_df = pd.read_csv(os.path.join(source, "npvs.csv"))
        # Calculate net_present_value_change
        npv_df["net_present_value_change"] = (
            npv_df["net_present_value_shock"] - npv_df["net_present_value_baseline"]
        ) / npv_df["net_present_value_baseline"]

        pd_df = pd.read_csv(os.path.join(source, "pds.csv"))
        pd_df["asset_id"] = pd_df["company_id"]
        # Calculate pd_difference
        pd_df["pd_difference"] = pd_df["pd_shock"] - pd_df["pd_baseline"]
        pd_df = pd_df.loc[pd_df["term"] == 5, :]  # Filter for term == 5

        params_df = pd.read_csv(os.path.join(source, "params.csv"))

        return npv_df, pd_df, params_df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None, None, None


def extract_histogram_for_plot(data, value_type, bin_edges):
    """
    Computes histogram counts for a given dataset and value type.

    Parameters:
    data (pd.DataFrame): The input data containing the values to histogram.
    value_type (str): The column name for which histogram is computed.
    bin_edges (np.ndarray): The edges of the bins.

    Returns:
    np.ndarray: Array of histogram counts.
    """
    values = data[value_type].dropna().values
    counts, _ = np.histogram(values, bins=bin_edges)
    return counts


def extract_histogram_data_by_category(
    data_df, params_df, value_type, category_column, num_bins=10
):
    """
    Extracts histogram data for each category as a concatenated DataFrame.

    Returns a dictionary structured as:
    {
        category1: DataFrame with columns ['bin_start', 'bin_end', 'count_<label_for_run1>', 'count_<label_for_run2>', ...],
        category2: DataFrame with the same structure,
        ...
    }
    """
    histogram_data = {}
    categories = data_df[category_column].unique()
    categories = np.append(categories, "All")  # Add "All" for the special case

    for cat in categories:
        print(f"\nProcessing {category_column}: {cat}")

        if cat == "All":
            cat_data = data_df
        else:
            cat_data = data_df[data_df[category_column] == cat]

        histogram_dfs = []

        # Determine common bin edges for this category across all runs
        values_all = cat_data[value_type].dropna().values
        if values_all.size == 0:
            print(f"  No data to compute histogram for category '{cat}'. Skipping.")
            continue
        min_val = values_all.min()
        max_val = values_all.max()
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)

        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Optional: for reference

        for _, run_params in params_df.iterrows():
            # Construct label text similar to legend text
            label = f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

            run_subset = cat_data[cat_data["run_id"] == run_params["run_id"]]

            if not run_subset.empty:
                counts = extract_histogram_for_plot(run_subset, value_type, bin_edges)
                histogram_dfs.append(
                    pd.DataFrame(
                        {
                            "bin_start": bin_edges[:-1],
                            "bin_end": bin_edges[1:],
                            f"count_{label}": counts,
                        }
                    )
                )
                print(
                    f"  - Histogram counts extracted for run_id {run_params['run_id']} with label '{label}'"
                )
            else:
                # No data for this run; store NaNs
                histogram_dfs.append(
                    pd.DataFrame(
                        {
                            "bin_start": bin_edges[:-1],
                            "bin_end": bin_edges[1:],
                            f"count_{label}": np.nan,
                        }
                    )
                )
                print(
                    f"  - No data for run_id {run_params['run_id']} with label '{label}'. Filled with NaNs."
                )

        # Concatenate all count columns into one DataFrame for this category
        if histogram_dfs:
            combined_df = pd.concat(histogram_dfs, axis=1)
            # Remove duplicate 'bin_start' and 'bin_end' columns
            combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
            histogram_data[cat] = combined_df
            print(f"  - Histogram data combined for category '{cat}'")
        else:
            histogram_data[cat] = pd.DataFrame(
                {"bin_start": bin_edges[:-1], "bin_end": bin_edges[1:]}
            )
            print(f"  - Empty histogram data for category '{cat}'")

    return histogram_data


def extract_histogram_data_by_run(
    data_df, params_df, value_type, category_column, num_bins=10
):
    """
    Extracts histogram data grouped by run_id as concatenated DataFrames.

    Returns a dictionary structured as:
    {
        run_id1: DataFrame with columns ['bin_start', 'bin_end', 'count_<category1>', 'count_<category2>', ...],
        run_id2: DataFrame with the same structure,
        ...
    }
    """
    histogram_data = {}
    for _, run_params in params_df.iterrows():
        run_id = run_params["run_id"]
        print(f"\nProcessing run_id: {run_id}")

        run_data = data_df[data_df["run_id"] == run_id]
        if run_data.empty:
            print(f"  - No data found for run_id {run_id}. Skipping.")
            continue

        categories = run_data[category_column].unique()
        histogram_dfs = []

        # Determine common bin edges for this run across all categories
        values_all = run_data[value_type].dropna().values
        if values_all.size == 0:
            print(f"  - No data to compute histogram for run_id {run_id}. Skipping.")
            continue
        min_val = values_all.min()
        max_val = values_all.max()
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)

        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Optional: for reference

        for category in categories:
            cat_data = run_data[run_data[category_column] == category]
            if not cat_data.empty:
                counts = extract_histogram_for_plot(cat_data, value_type, bin_edges)
                histogram_dfs.append(
                    pd.DataFrame(
                        {
                            "bin_start": bin_edges[:-1],
                            "bin_end": bin_edges[1:],
                            f"count_{category}": counts,
                        }
                    )
                )
                print(
                    f"  - Histogram counts extracted for category '{category}' in run_id {run_id}"
                )
            else:
                # No data for this category; store NaNs
                histogram_dfs.append(
                    pd.DataFrame(
                        {
                            "bin_start": bin_edges[:-1],
                            "bin_end": bin_edges[1:],
                            f"count_{category}": np.nan,
                        }
                    )
                )
                print(
                    f"  - No data for category '{category}' in run_id {run_id}. Filled with NaNs."
                )

        # Concatenate all count columns into one DataFrame for this run_id
        if histogram_dfs:
            combined_df = pd.concat(histogram_dfs, axis=1)
            # Remove duplicate 'bin_start' and 'bin_end' columns
            combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
            histogram_data[run_id] = combined_df
            print(f"  - Histogram data combined for run_id '{run_id}'")
        else:
            histogram_data[run_id] = pd.DataFrame(
                {"bin_start": bin_edges[:-1], "bin_end": bin_edges[1:]}
            )
            print(f"  - Empty histogram data for run_id '{run_id}'")

    return histogram_data


def save_histogram_data(histogram_data, output_base_folder, data_type="category"):
    """
    Saves the extracted histogram data to Excel files.

    Parameters:
    histogram_data (dict): Dictionary containing histogram DataFrames.
    output_base_folder (str): Base folder to save the Excel files.
    data_type (str): Type of data ('category' or 'run') to organize folders.
    """
    for key, df in histogram_data.items():
        # Construct descriptive file names
        if data_type == "category":
            filename = f"histogram_{key.replace(' ', '_')}.csv"
        elif data_type == "run":
            filename = f"histogram_run_{key}.csv"
        else:
            filename = f"histogram_{key}.csv"

        output_path = os.path.join(output_base_folder, filename)
        df.to_csv(output_path, index=False)
        print(f"  - Histogram data for '{key}' saved to {output_path}")


if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join(
        "workspace", "india_variability_analysis_INDIA_geo_2"
    )
    HISTOGRAM_DATA_FOLDER = os.path.join("workspace", "plots_data", "histogram_data")

    # Create output directories
    histogram_data_by_category_folder = os.path.join(
        HISTOGRAM_DATA_FOLDER, "by_category"
    )
    histogram_data_by_run_folder = os.path.join(HISTOGRAM_DATA_FOLDER, "by_run")
    os.makedirs(histogram_data_by_category_folder, exist_ok=True)
    os.makedirs(histogram_data_by_run_folder, exist_ok=True)

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting program.")
    else:
        # ===========================
        # Extract Histogram Data by Category
        # ===========================
        print("\n--- Extracting Histogram Data by Category ---")
        # Example for NPV
        histogram_by_category_npv = extract_histogram_data_by_category(
            data_df=npv_df,
            params_df=params_df,
            value_type="net_present_value_change",
            category_column="technology",
            num_bins=10,
        )
        save_histogram_data(
            histogram_data=histogram_by_category_npv,
            output_base_folder=histogram_data_by_category_folder,
            data_type="category",
        )

        # Example for PD
        histogram_by_category_pd = extract_histogram_data_by_category(
            data_df=pd_df,
            params_df=params_df,
            value_type="pd_difference",
            category_column="sector",
            num_bins=10,
        )
        save_histogram_data(
            histogram_data=histogram_by_category_pd,
            output_base_folder=histogram_data_by_category_folder,
            data_type="category",
        )

        # ===========================
        # Extract Histogram Data by Run
        # ===========================
        print("\n--- Extracting Histogram Data by Run ---")
        # Example for NPV
        histogram_by_run_npv = extract_histogram_data_by_run(
            data_df=npv_df,
            params_df=params_df,
            value_type="net_present_value_change",
            category_column="technology",
            num_bins=10,
        )
        save_histogram_data(
            histogram_data=histogram_by_run_npv,
            output_base_folder=histogram_data_by_run_folder,
            data_type="run",
        )

        # Example for PD
        histogram_by_run_pd = extract_histogram_data_by_run(
            data_df=pd_df,
            params_df=params_df,
            value_type="pd_difference",
            category_column="sector",
            num_bins=10,
        )
        save_histogram_data(
            histogram_data=histogram_by_run_pd,
            output_base_folder=histogram_data_by_run_folder,
            data_type="run",
        )

        print("\nHistogram data extraction and saving complete.")
