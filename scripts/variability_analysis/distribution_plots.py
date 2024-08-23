import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


# Function to load and return the dataset
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
        # Calculate net_present_value_rate_of_change
        npv_df["net_present_value_change"] = (
            npv_df["net_present_value_shock"] - npv_df["net_present_value_baseline"]
        ) / npv_df["net_present_value_baseline"]

        pd_df = pd.read_csv(os.path.join(source, "pds.csv"))
        pd_df["asset_id"] = pd_df["company_id"]
        # Calculate pd_difference
        pd_df["pd_difference"] = pd_df["pd_shock"] - pd_df["pd_baseline"]
        pd_df = pd_df.loc[pd_df["term"] == 5, :]

        params_df = pd.read_csv(os.path.join(source, "params.csv"))

        return npv_df, pd_df, params_df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None, None, None


# Function to filter data based on multiple criteria
def filter_data(df, params_df, filter_criteria):
    """
    Filters the dataframe based on the criteria provided in filter_criteria.

    Parameters:
    df (pd.DataFrame): The main dataframe to filter.
    params_df (pd.DataFrame): The parameters dataframe that contains filtering columns.
    filter_criteria (dict): A dictionary where keys are column names in params_df and values are the criteria for filtering.

    Returns:
    pd.DataFrame: The filtered dataframe.
    """
    # Start with the full params_df
    filtered_params_df = params_df.copy()

    # Apply each filtering criterion
    for key, value in filter_criteria.items():
        filtered_params_df = filtered_params_df[filtered_params_df[key] == value]

    # Merge the filtered params_df with the main dataframe
    filtered_df = df.merge(filtered_params_df[["run_id"]], on="run_id", how="inner")

    return filtered_df


# Function to plot density distribution for multiple scenarios
def plot_density_distribution(
    data, params_df, run_params, selected_sectors, title, plots_folder
):
    """
    Plots the density distribution for multiple runs on the same plot.

    Parameters:
    data (pd.DataFrame): The NPV dataframe containing data to plot.
    params_df (pd.DataFrame): The parameters dataframe for filtering runs.
    run_params (list): A list of dictionaries, each containing run parameters for plotting.
    selected_sectors (list): Sectors to include in the plot.
    title (str): Title of the plot.
    plots_folder (str): Path to the folder where plots will be saved.
    """
    mpl.rcParams["font.family"] = "Times New Roman"
    plt.style.use("default")
    plt.figure(figsize=(8, 8), dpi=250)

    all_changes = []

    # Predefined set of colors for the plots
    colors = ["blue", "orange", "red", "magenta", "gray", "cyan"]

    # Loop through each run's parameters and plot its density
    for idx, params in enumerate(run_params):
        # Assign a color from the predefined list
        color = colors[idx % len(colors)]

        # Filter the data based on the current parameters
        filtered_data = filter_data(
            data,
            params_df,
            params,
        )

        # Filter further by the selected sectors
        filtered_data = filtered_data[filtered_data["sector"].isin(selected_sectors)]

        # Generate a label based on the parameters
        label = f"{params['target_scenario']} ({params['shock_year']}, {params['scenario_geography']})"

        # Plot the density distribution
        if not filtered_data.empty:
            all_changes.extend(filtered_data["net_present_value_change"].values)
            filtered_data["net_present_value_change"].plot(
                kind="density", label=label, color=color
            )

    # Automatically set x-axis limits and ticks based on data range
    if all_changes:
        x_min = min(all_changes) - 0.5
        x_max = max(all_changes) + 0.5
        x_limits = (x_min, x_max)
        x_ticks = np.arange(x_min, x_max + 0.5, 0.5)
        plt.xlim(x_limits)
        plt.xticks(x_ticks, ["{:,.0%}".format(x) for x in x_ticks])

    plt.title(title, fontsize=20)
    plt.xlabel("Valuation change", fontsize=16)
    plt.ylabel("Density", fontsize=16)
    plt.legend(fontsize=14)

    ax = plt.gca()
    vals = ax.get_xticks()
    ax.set_xticklabels(["{:,.0%}".format(x) for x in vals])

    # Save the plot
    imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}.png")
    plt.savefig(imgpath)
    print(f"Plot saved to {imgpath}")


def plot_density_distributions(
    data_source_folder,
    plots_folder,
    selected_sectors,
    run_params,
    title="Distribution of Valuation Change across Scenarios",
):
    """
    Runs the analysis by loading data, filtering it based on provided sectors,
    and plotting the density distribution of valuation changes.

    Parameters:
    - data_source_folder (str): Path to the folder containing input data files.
    - plots_folder (str): Path to the folder where plots will be saved.
    - selected_sectors (list): List of sectors to include in the density plot.
    - run_params (list of dicts): List of run parameters for each scenario.
    - title (str): Title of the plot (default is "Distribution of Valuation Change across Scenarios").
    """
    npv_df, pd_df, params_df = load_data(data_source_folder)

    # Check if data loading was successful
    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting.")
        return

    # Create output folder if it doesn't exist
    os.makedirs(plots_folder, exist_ok=True)

    # Plot density distributions for all runs on the same plot
    plot_density_distribution(
        npv_df,
        params_df,
        run_params,
        selected_sectors,
        title=title,
        plots_folder=plots_folder,
    )


if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")

    # Define sectors for density plots
    selected_sectors = ["Power"]

    # Define run parameters (color is not needed here)
    run_params = [
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "WEO2021_SDS",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "Oxford",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
    ]

    # Run the analysis and plot density distribution
    plot_density_distributions(
        data_source_folder=DATA_SOURCE_FOLDER,
        plots_folder=PLOTS_FOLDER,
        selected_sectors=selected_sectors,
        run_params=run_params,
    )
