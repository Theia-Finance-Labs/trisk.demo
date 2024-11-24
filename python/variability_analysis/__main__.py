import os
import pandas as pd
from .distribution_plots import plot_density_distributions, plot_barplot_distributions
from .quadrant_plots import plot_bivariate_scenarios_quadrants
from .generate_data import run_r_analysis
from .utils import load_data
from .grouped_distrib_plots import plot_grouped_distributions
from .individual_distribution_plots import (
    plot_individual_distributions_by_technology,
    plot_comparison_between_shock_years,
    plot_comparison_between_shock_years_barplot,
)


def generate_technology_stats(npv_df, params_df, output_file):
    """
    Generates statistics for each technology and saves them into one Excel file.
    Adds a "Technology" column to differentiate between the technologies.

    Parameters:
    - npv_df: DataFrame containing the net present value (NPV) data.
    - params_df: DataFrame containing parameter data.
    - output_file: The file path where the Excel file will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Get unique technologies in the npv_df
    technologies = npv_df["technology"].unique()

    # List to collect all DataFrames for concatenation
    all_tech_stats = []

    # Loop through each technology and collect their stats
    for tech in technologies:
        tech_df = npv_df[npv_df["technology"] == tech].merge(params_df)

        # Group by without 'run_id' and compute aggregations
        stats_df = tech_df.groupby(["target_scenario", "shock_year"]).agg(
            median_npv_change=("net_present_value_change", "median"),
            mean_npv_change=("net_present_value_change", "mean"),
            std_npv_change=("net_present_value_change", "std"),
            unique_company_count=("company_id", "nunique"),
            min_npv_change=("net_present_value_change", "min"),
            max_npv_change=("net_present_value_change", "max"),
            q1_npv_change=("net_present_value_change", lambda x: x.quantile(0.25)),
            q3_npv_change=("net_present_value_change", lambda x: x.quantile(0.75)),
            count_observations=("net_present_value_change", "count"),
        )

        # Prettify the numeric values by rounding them to 2 decimal places
        stats_df = stats_df.round(4)

        # Add a "Technology" column
        stats_df["Technology"] = tech

        # Reset index and rename columns
        stats_df = stats_df.reset_index().rename(
            columns={
                "target_scenario": "Target Scenario",
                "shock_year": "Shock Year",
                "median_npv_change": "Median NPV Change",
                "mean_npv_change": "Mean NPV Change",
                "std_npv_change": "Standard Deviation NPV Change",
                "unique_company_count": "Unique Company Count",
                "min_npv_change": "Minimum NPV Change",
                "max_npv_change": "Maximum NPV Change",
                "q1_npv_change": "First Quartile NPV Change (Q1)",
                "q3_npv_change": "Third Quartile NPV Change (Q3)",
                "count_observations": "Number of Observations",
            }
        )

        # Append the dataframe to the list
        all_tech_stats.append(stats_df)

    # Concatenate all dataframes into one
    final_df = pd.concat(all_tech_stats, ignore_index=True)

    # Save the concatenated DataFrame to a single Excel file
    final_df.to_excel(output_file, index=False)


if __name__ == "__main__":
    # Constants for all sections
    DATA_SOURCE_FOLDER = R_OUTPUT_PATH = os.path.join(
        "workspace", "india_variability_analysis_INDIA_geo_2"
    )
    DENSITY_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")
    HISTOGRAM_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_histograms")
    QUADRANT_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_quadrants")
    GROUPED_PLOTS_FOLDER = os.path.join(
        DATA_SOURCE_FOLDER, "plots_distributions_grouped"
    )
    TRISK_INPUT_PATH = os.path.join("workspace", "ST_INPUTS_AI_COUNTRIES")

    # Create output folders if they don't exist
    os.makedirs(DENSITY_PLOTS_FOLDER, exist_ok=True)
    os.makedirs(QUADRANT_PLOTS_FOLDER, exist_ok=True)
    os.makedirs(GROUPED_PLOTS_FOLDER, exist_ok=True)

    # Define run parameters for scenarios
    # Define the parameters
    run_params = [
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2025,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2030,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2025,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2030,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_NZ2050",
            "shock_year": 2025,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_NZ2050",
            "shock_year": 2030,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_B2DS",
            "shock_year": 2025,
            "scenario_geography": "India",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_B2DS",
            "shock_year": 2030,
            "scenario_geography": "India",
        },
    ]

    # Section 1: Run R Analysis
    print("Running R analysis...")
    country_iso2 = "IN"
    sector = "Power"
    # run_r_analysis(TRISK_INPUT_PATH, R_OUTPUT_PATH, run_params, country_iso2, sector)
    print("R analysis completed.")

    print("Génération des graphiques de densité...")
    npv_df, pd_df, params_df, trajectories_df = load_data(DATA_SOURCE_FOLDER)

    # Call the function to generate and save technology stats
    generate_technology_stats(
        npv_df, params_df, os.path.join(DATA_SOURCE_FOLDER, "statdesc.xlsx")
    )

    # Section 2: Plot Density Distributions

    plot_density_distributions(
        npv_df=npv_df,
        pd_df=pd_df,
        params_df=params_df,
        plots_folder=DENSITY_PLOTS_FOLDER,
    )

    plot_barplot_distributions(
        npv_df=npv_df,
        pd_df=pd_df,
        params_df=params_df,
        plots_folder=HISTOGRAM_PLOTS_FOLDER,
    )
    print("Graphiques de densité générés.")

    # # Section 3: Plot Bivariate Scenario Quadrants
    # print("Generating quadrant plots...")

    # for i, params1 in enumerate(run_params):
    #     for j, params2 in enumerate(run_params):
    #         if i >= j:
    #             continue  # Skip if indices are the same or if params1 has already been compared with params2
    #         plot_bivariate_scenarios_quadrants(
    #             npv_df=npv_df,
    #             pd_df=pd_df,
    #             params_df=params_df,
    #             params1=params1,
    #             params2=params2,
    #             save_folder_path=QUADRANT_PLOTS_FOLDER,
    #         )
    print("Quadrant plots generated.")

    # Section 4: Plot Grouped Distributions
    print("Generating grouped distribution plots...")
    plot_grouped_distributions(
        npv_df,
        params_df,
        GROUPED_PLOTS_FOLDER,
        "net_present_value_change",
        "technology",
    )
    plot_grouped_distributions(
        pd_df, params_df, GROUPED_PLOTS_FOLDER, "pd_difference", "sector"
    )
    print("Grouped distribution plots generated.")

    print("Generating individual distribution plots...")

    individual_distrib_plots_folder = os.path.join(
        DATA_SOURCE_FOLDER, "plots_individual_comparisons"
    )
    individual_distrib_plots_folder2 = os.path.join(
        DATA_SOURCE_FOLDER, "plots_individual_comparisons_bar"
    )

    plot_individual_distributions_by_technology(
        npv_df,
        params_df,
        individual_distrib_plots_folder,
        "net_present_value_change",
        "technology",
    )
    # Plot comparison between shock years for all scenarios
    plot_comparison_between_shock_years(
        npv_df,
        params_df,
        individual_distrib_plots_folder,
        "net_present_value_change",
        "technology",
    )

    plot_comparison_between_shock_years_barplot(
        npv_df,
        params_df,
        individual_distrib_plots_folder2,
        "net_present_value_change",
        "technology",
    )

    print("All tasks completed successfully.")
