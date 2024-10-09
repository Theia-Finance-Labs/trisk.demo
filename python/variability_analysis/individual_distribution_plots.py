import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
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


def plot_individual_distributions_by_technology(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Plots individual distributions for each technology, with each run plotted in its respective subfolder.

    Args:
    data_df (pd.DataFrame): The dataframe containing the data.
    params_df (pd.DataFrame): The dataframe with run parameters.
    plots_folder (str): The directory where plots will be saved.
    value_type (str): The type of value to plot.
    category_column (str): The category column (e.g., 'technology').
    """
    individual_folder = os.path.join(plots_folder, "individual_distributions")
    os.makedirs(individual_folder, exist_ok=True)

    colors = [
        "blue",
        "orange",
        "red",
        "magenta",
        "gray",
        "cyan",
        "#8B4513",
        "#006400",
        "#4B0082",
        "#FF1493",
        "#00CED1",
        "#FF4500",
        "#2F4F4F",
        "#9ACD32",
        "#FF69B4",
    ]

    technologies = data_df[category_column].unique()
    for tech in technologies:
        tech_folder = os.path.join(individual_folder, tech)
        os.makedirs(tech_folder, exist_ok=True)

        tech_data = data_df[data_df[category_column] == tech]
        for run_id in tech_data["run_id"].unique():
            run_data = tech_data[tech_data["run_id"] == run_id]
            if run_data.empty:
                continue

            plt.figure(figsize=(10, 6), dpi=250)
            ax = plt.gca()

            values = run_data[value_type].values
            label = f"Run ID: {run_id}"
            color = colors[hash(run_id) % len(colors)]

            if len(values) > 1:
                try:
                    run_data[value_type].plot.density(label=label, color=color, ax=ax)
                    print(f"Density curve plotted for {label}")
                except Exception as e:
                    print(f"Error plotting density for {label}: {str(e)}")
                    ax.axvline(values.mean(), color=color, label=label)
            else:
                ax.axvline(values[0], color=color, label=label)

            plt.title(
                f"Distribution of {value_type} - Technology: {tech} - Run: {run_id}",
                fontsize=18,
            )
            plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
            plt.ylabel("Density", fontsize=14)
            plt.legend(fontsize=10)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))
            plt.tight_layout()

            imgpath = os.path.join(tech_folder, f"{tech}_run_{run_id}.png")
            plt.savefig(imgpath)
            plt.close()
            print(f"Graph saved in {imgpath}")


def plot_comparison_between_shock_years(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Plots the distribution for two runs of the same target scenario but different shock years,
    for each technology.

    Args:
    data_df (pd.DataFrame): The dataframe containing the data.
    params_df (pd.DataFrame): The dataframe with run parameters.
    plots_folder (str): The directory where plots will be saved.
    value_type (str): The type of value to plot.
    category_column (str): The category column (e.g., 'technology').
    """
    comparison_folder = os.path.join(plots_folder, "comparison_shock_years")
    os.makedirs(comparison_folder, exist_ok=True)

    # Get all unique target scenarios from the params_df
    target_scenarios = params_df["target_scenario"].unique()
    technologies = data_df[category_column].unique()

    for target_scenario in target_scenarios:
        scenario_runs = params_df[params_df["target_scenario"] == target_scenario]
        shock_years = scenario_runs["shock_year"].unique()

        if len(shock_years) < 2:
            print(
                f"Not enough shock years for target scenario: {target_scenario} to compare."
            )
            continue

        # Select two shock years for comparison
        shock_year_1, shock_year_2 = shock_years[:2]
        run_ids_1 = scenario_runs[scenario_runs["shock_year"] == shock_year_1]["run_id"]
        run_ids_2 = scenario_runs[scenario_runs["shock_year"] == shock_year_2]["run_id"]

        for tech in technologies:
            data_tech = data_df[data_df[category_column] == tech]
            data_1 = data_tech[data_tech["run_id"].isin(run_ids_1)]
            data_2 = data_tech[data_tech["run_id"].isin(run_ids_2)]

            plt.figure(figsize=(10, 6), dpi=250)
            ax = plt.gca()

            colors = ["blue", "orange"]

            if not data_1.empty:
                data_1[value_type].plot.density(
                    label=f"Shock Year: {shock_year_1}", color=colors[0], ax=ax
                )
            if not data_2.empty:
                data_2[value_type].plot.density(
                    label=f"Shock Year: {shock_year_2}", color=colors[1], ax=ax
                )

            plt.title(
                f"Comparison of {value_type} - Target Scenario: {target_scenario} - Technology: {tech}",
                fontsize=18,
            )
            plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
            plt.ylabel("Density", fontsize=14)
            plt.legend(fontsize=10)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))
            plt.tight_layout()

            imgpath = os.path.join(
                comparison_folder, f"comparison_{target_scenario}_{tech}.png"
            )
            plt.savefig(imgpath)
            plt.close()
            print(f"Comparison graph for {tech} saved in {imgpath}")


if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_individual_comparisons")

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting program.")
    else:
        # Plot individual distributions for technologies
        plot_individual_distributions_by_technology(
            npv_df, params_df, PLOTS_FOLDER, "net_present_value_change", "technology"
        )
        # Plot comparison between shock years for all scenarios
        plot_comparison_between_shock_years(
            npv_df,
            params_df,
            PLOTS_FOLDER,
            "net_present_value_change",
            "technology",
        )
