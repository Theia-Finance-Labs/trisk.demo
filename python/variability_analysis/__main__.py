import os
from .distribution_plots import plot_density_distributions
from .quadrant_plots import plot_bivariate_scenarios_quadrants
from .generate_data import run_r_analysis
from .utils import load_data
from .grouped_distrib_plots import plot_grouped_distributions
from .individual_distribution_plots import (
    plot_individual_distributions_by_technology,
    plot_comparison_between_shock_years,
)


if __name__ == "__main__":
    # Constants for all sections
    DATA_SOURCE_FOLDER = R_OUTPUT_PATH = os.path.join(
        "workspace", "india_variability_analysis_INDIA_geo_2"
    )
    DENSITY_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")
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
    run_r_analysis(TRISK_INPUT_PATH, R_OUTPUT_PATH, run_params, country_iso2, sector)
    print("R analysis completed.")

    print("Génération des graphiques de densité...")
    npv_df, pd_df, params_df, trajectories_df = load_data(DATA_SOURCE_FOLDER)

    npv_df[npv_df["technology"] == "HydroCap"].merge(params_df).groupby(
        ["run_id", "target_scenario", "shock_year"]
    ).agg(
        median_npv=("net_present_value_change", "median"),
        mean_npv=("net_present_value_change", "mean"),
        std_npv=("net_present_value_change", "std"),
        unique_company_count=("company_id", "nunique"),
    ).to_csv(
        "workspace/india_variability_analysis_INDIA_geo_2/hydrocap_stats.csv"
    )

    npv_df[npv_df["technology"] == "OilCap"].merge(params_df).groupby(
        ["run_id", "target_scenario", "shock_year"]
    ).agg(
        median_npv=("net_present_value_change", "median"),
        mean_npv=("net_present_value_change", "mean"),
        std_npv=("net_present_value_change", "std"),
        unique_company_count=("company_id", "nunique"),
    ).to_csv(
        "workspace/india_variability_analysis_INDIA_geo_2/oilcap_stats.csv"
    )

    # Section 2: Plot Density Distributions

    plot_density_distributions(
        npv_df=npv_df,
        pd_df=pd_df,
        params_df=params_df,
        plots_folder=DENSITY_PLOTS_FOLDER,
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

    print("All tasks completed successfully.")
