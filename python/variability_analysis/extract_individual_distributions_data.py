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


def compute_density(values, x_grid):
    """
    Computes density values using Gaussian Kernel Density Estimation.

    Parameters:
    values (np.ndarray): The data points for which density is computed.
    x_grid (np.ndarray): The grid over which density is evaluated.

    Returns:
    np.ndarray: Density values corresponding to x_grid.
    """
    kde = gaussian_kde(values)
    return kde.evaluate(x_grid)


def extract_density_individual_distributions(
    data_df, params_df, value_type, category_column, output_base_folder, num_points=500
):
    """
    Extracts density data for each technology and run_id and saves them as Excel files.

    Parameters:
    data_df (pd.DataFrame): The dataframe containing the data.
    params_df (pd.DataFrame): The dataframe with run parameters.
    value_type (str): The type of value to compute density for.
    category_column (str): The category column (e.g., 'technology').
    output_base_folder (str): The base directory to save density data.
    num_points (int): Number of points in the x_grid for density computation.
    """
    # Create the base folder for individual distributions
    individual_folder = os.path.join(
        output_base_folder, "individual_distributions_data"
    )
    os.makedirs(individual_folder, exist_ok=True)

    # Get unique technologies
    technologies = data_df[category_column].unique()
    print(f"Found {len(technologies)} technologies.")

    for tech in technologies:
        print(f"\nProcessing Technology: {tech}")
        tech_folder = os.path.join(individual_folder, tech)
        os.makedirs(tech_folder, exist_ok=True)

        tech_data = data_df[data_df[category_column] == tech]
        unique_run_ids = tech_data["run_id"].unique()
        print(f"  Found {len(unique_run_ids)} runs for Technology '{tech}'.")

        for run_id in unique_run_ids:
            run_data = tech_data[tech_data["run_id"] == run_id]
            if run_data.empty:
                print(f"    - No data for Run ID: {run_id}. Skipping.")
                continue

            values = run_data[value_type].dropna().values
            if len(values) < 2:
                print(
                    f"    - Insufficient data for Run ID: {run_id}. Skipping density computation."
                )
                continue

            # Define x_grid based on the data range with 10% margin
            x_min, x_max = values.min(), values.max()
            margin = (x_max - x_min) * 0.1
            x_grid = np.linspace(x_min - margin, x_max + margin, num_points)

            # Compute density
            density = compute_density(values, x_grid)

            # Construct descriptive label
            run_params = params_df[params_df["run_id"] == run_id]
            if run_params.empty:
                label = f"Run_{run_id}"
                print(
                    f"    - No parameters found for Run ID: {run_id}. Using default label '{label}'."
                )
            else:
                run_params = run_params.iloc[0]
                label = f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

            # Create DataFrame for density data
            density_df = pd.DataFrame({"x": x_grid, "density": density})

            # Define output file path
            sanitized_label = (
                label.replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
                .replace(",", "_")
            )
            output_file = os.path.join(
                tech_folder, f"density_run_{run_id}_{sanitized_label}.csv"
            )

            # Save to Excel
            density_df.to_csv(output_file, index=False)
            print(f"    - Density data saved to {output_file}")


def extract_comparison_density(
    data_df, params_df, value_type, category_column, output_base_folder, num_points=500
):
    """
    Extracts density data for comparisons between shock years and saves them as Excel files.

    Parameters:
    data_df (pd.DataFrame): The dataframe containing the data.
    params_df (pd.DataFrame): The dataframe with run parameters.
    value_type (str): The type of value to compute density for.
    category_column (str): The category column (e.g., 'technology').
    output_base_folder (str): The base directory to save comparison density data.
    num_points (int): Number of points in the x_grid for density computation.
    """
    comparison_folder = os.path.join(output_base_folder, "comparison_shock_years_data")
    os.makedirs(comparison_folder, exist_ok=True)

    # Get all unique target scenarios
    target_scenarios = params_df["target_scenario"].unique()
    technologies = data_df[category_column].unique()
    print(f"Found {len(target_scenarios)} target scenarios.")

    for target_scenario in target_scenarios:
        print(f"\nProcessing Target Scenario: {target_scenario}")
        scenario_runs = params_df[params_df["target_scenario"] == target_scenario]
        shock_years = scenario_runs["shock_year"].unique()

        if len(shock_years) < 2:
            print(
                f"  - Not enough shock years for Target Scenario '{target_scenario}'. Skipping."
            )
            continue

        # Select first two shock years for comparison
        shock_year_1, shock_year_2 = shock_years[:2]
        run_ids_1 = scenario_runs[scenario_runs["shock_year"] == shock_year_1][
            "run_id"
        ].values
        run_ids_2 = scenario_runs[scenario_runs["shock_year"] == shock_year_2][
            "run_id"
        ].values
        print(f"  - Comparing Shock Years: {shock_year_1} vs {shock_year_2}")

        for tech in technologies:
            print(f"  Processing Technology: {tech}")
            data_tech = data_df[data_df[category_column] == tech]

            # Aggregate data for shock_year_1
            data_1 = data_tech[data_tech["run_id"].isin(run_ids_1)]
            values_1 = data_1[value_type].dropna().values

            # Aggregate data for shock_year_2
            data_2 = data_tech[data_tech["run_id"].isin(run_ids_2)]
            values_2 = data_2[value_type].dropna().values

            if len(values_1) < 2 or len(values_2) < 2:
                print(
                    f"    - Insufficient data for Technology '{tech}' in one of the shock years. Skipping."
                )
                continue

            # Define common x_grid based on combined data
            combined_values = np.concatenate([values_1, values_2])
            x_min, x_max = combined_values.min(), combined_values.max()
            margin = (x_max - x_min) * 0.1
            x_grid = np.linspace(x_min - margin, x_max + margin, num_points)

            # Compute densities
            density_1 = compute_density(values_1, x_grid)
            density_2 = compute_density(values_2, x_grid)

            # Create DataFrame for comparison
            comparison_df = pd.DataFrame(
                {
                    "x": x_grid,
                    f"density_{shock_year_1}": density_1,
                    f"density_{shock_year_2}": density_2,
                }
            )

            # Define output file path
            output_file = os.path.join(
                comparison_folder,
                f"comparison_{target_scenario}_{tech}_shock_years_{shock_year_1}_vs_{shock_year_2}.csv",
            )

            # Save to Excel
            comparison_df.to_csv(output_file, index=False)
            print(f"    - Comparison density data saved to {output_file}")


def plot_individual_distributions_by_technology(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Placeholder for plotting function. This function is now deprecated in favor of data extraction.
    """
    print("Plotting function is deprecated. Use data extraction functions instead.")


if __name__ == "__main__":

    # Constants
    DATA_SOURCE_FOLDER = os.path.join(
        "workspace", "india_variability_analysis_INDIA_geo_2"
    )
    OUTPUT_BASE_FOLDER = os.path.join("workspace", "plots_data")

    # Create output directories
    density_output_folder = os.path.join(OUTPUT_BASE_FOLDER, "individual_density_data")
    comparison_density_output_folder = os.path.join(
        OUTPUT_BASE_FOLDER, "comparison_density_data"
    )
    os.makedirs(density_output_folder, exist_ok=True)
    os.makedirs(comparison_density_output_folder, exist_ok=True)

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting program.")
        raise

    # ===========================
    # Extract Density Data for Individual Distributions by Technology
    # ===========================
    print(
        "\n--- Extracting Density Data for Individual Distributions by Technology ---"
    )
    extract_density_individual_distributions(
        data_df=npv_df,
        params_df=params_df,
        value_type="net_present_value_change",
        category_column="technology",
        output_base_folder=density_output_folder,
    )
    extract_density_individual_distributions(
        data_df=pd_df,
        params_df=params_df,
        value_type="pd_difference",
        category_column="sector",
        output_base_folder=density_output_folder,
    )

    # ===========================
    # Extract Density Data for Comparison Between Shock Years
    # ===========================
    print("\n--- Extracting Density Data for Comparison Between Shock Years ---")
    extract_comparison_density(
        data_df=npv_df,
        params_df=params_df,
        value_type="net_present_value_change",
        category_column="technology",
        output_base_folder=comparison_density_output_folder,
    )
    extract_comparison_density(
        data_df=pd_df,
        params_df=params_df,
        value_type="pd_difference",
        category_column="sector",
        output_base_folder=comparison_density_output_folder,
    )

    print("\nDensity data extraction and saving complete.")
