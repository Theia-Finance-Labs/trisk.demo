import os
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


def load_data(source):
    try:
        npv_df = pd.read_csv(os.path.join(source, "npvs.csv"))
        npv_df["net_present_value_change"] = (
            npv_df["net_present_value_shock"] - npv_df["net_present_value_baseline"]
        ) / npv_df["net_present_value_baseline"]

        pd_df = pd.read_csv(os.path.join(source, "pds.csv"))
        pd_df["asset_id"] = pd_df["company_id"]
        pd_df["pd_difference"] = pd_df["pd_shock"] - pd_df["pd_baseline"]
        pd_df = pd_df.loc[pd_df["term"] == 5, :]

        params_df = pd.read_csv(os.path.join(source, "params.csv"))
        return npv_df, pd_df, params_df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None, None, None


def extract_density_for_plot(data, value_type, x_grid=None):
    """
    Computes the density data for a given dataset and value type.
    Returns the density values corresponding to x_grid.
    """
    # Drop NaN values
    values = data[value_type].dropna().values

    # Handle cases with insufficient data
    if len(values) < 2:
        print(f"Insufficient data to compute density for {value_type}.")
        return np.full_like(x_grid, np.nan) if x_grid is not None else np.array([])

    # Define the x-axis grid if not provided
    if x_grid is None:
        x_min, x_max = values.min(), values.max()
        margin = (x_max - x_min) * 0.1
        x_grid = np.linspace(x_min - margin, x_max + margin, 500)

    # Compute density using Gaussian Kernel Density Estimation
    kde = gaussian_kde(values)
    density = kde.evaluate(x_grid)

    return density


def extract_density_data_by_category(data_df, params_df, value_type, category_column):
    """
    Extracts density data for each category as a concatenated DataFrame.
    Returns a dictionary structured as:
    {
        category1: DataFrame with columns ['x', 'density_<label_for_run1>', 'density_<label_for_run2>', ...],
        category2: DataFrame with the same structure,
        ...
    }
    """
    density_data = {}
    categories = data_df[category_column].unique()
    categories = np.append(categories, "All")

    global_min = data_df[value_type].min()
    global_max = data_df[value_type].max()
    global_margin = (global_max - global_min) * 0.1
    global_xlim = (global_min - global_margin, global_max + global_margin)
    x_grid = np.linspace(global_xlim[0], global_xlim[1], 500)

    for cat in categories:
        if cat == "All":
            cat_data = data_df
        else:
            cat_data = data_df[data_df[category_column] == cat]

        density_dfs = []

        for _, run_params in params_df.iterrows():
            # Construct label text similar to legend text
            label = f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

            run_subset = cat_data[cat_data["run_id"] == run_params["run_id"]]

            if not run_subset.empty:
                density_values = extract_density_for_plot(
                    run_subset, value_type, x_grid=x_grid
                )
                density_dfs.append(
                    pd.DataFrame({"x": x_grid, f"density_{label}": density_values})
                )
            else:
                # No data for this run; store NaNs
                density_dfs.append(
                    pd.DataFrame({"x": x_grid, f"density_{label}": np.nan})
                )

        # Concatenate all density columns into one DataFrame for this category
        if density_dfs:
            combined_df = pd.concat(density_dfs, axis=1)
            combined_df = combined_df.loc[
                :, ~combined_df.columns.duplicated()
            ]  # Remove duplicate 'x' columns
            density_data[cat] = combined_df
        else:
            density_data[cat] = pd.DataFrame({"x": x_grid})

    return density_data


if __name__ == "__main__":
    DATA_SOURCE_FOLDER = os.path.join(
        "workspace", "india_variability_analysis_INDIA_geo_2"
    )
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting program.")
    else:
        # Extracting density data as DataFrames per category
        density_by_category = extract_density_data_by_category(
            npv_df, params_df, "net_present_value_change", "technology"
        )

        # Example: Save all density data to Excel files for inspection
        output_base = os.path.join("workspace", "plots_data", "density_data")
        os.makedirs(output_base, exist_ok=True)
        for category, df in density_by_category.items():
            # Use category in file name
            output_file = os.path.join(output_base, f"density_{category}.csv")
            df.to_csv(output_file, index=False)
            print(f"Density data for category '{category}' saved to {output_file}")
