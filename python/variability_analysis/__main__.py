import os
from .distribution_plots import plot_density_distributions
from .quadrant_plots import plot_bivariate_scenarios_quadrants
from .generate_data import run_r_analysis
from .utils import load_data


if __name__ == "__main__":
    # Constants for all sections
    DATA_SOURCE_FOLDER = R_OUTPUT_PATH = os.path.join(
        "workspace", "india_variability_analysis"
    )
    DENSITY_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")
    QUADRANT_PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_quadrants")
    R_INPUT_PATH = os.path.join("workspace", "trisk_inputs_v2_legacy_countries")

    # Create output folders if they don't exist
    os.makedirs(DENSITY_PLOTS_FOLDER, exist_ok=True)
    os.makedirs(QUADRANT_PLOTS_FOLDER, exist_ok=True)

    # Define run parameters for scenarios
    # Define the parameters
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
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_NZ2050",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_NZ2050",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_B2DS",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023REMIND_CP",
            "target_scenario": "NGFS2023REMIND_B2DS",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
    ]

    # Section 1: Run R Analysis
    print("Running R analysis...")
    country_iso2 = "IN"
    sector = "Power"
    run_r_analysis(R_INPUT_PATH, R_OUTPUT_PATH, run_params, country_iso2, sector)
    print("R analysis completed.")

    # Section 2: Plot Density Distributions
    print("Génération des graphiques de densité...")
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)
    plot_density_distributions(
        npv_df=npv_df, params_df=params_df, plots_folder=DENSITY_PLOTS_FOLDER
    )
    print("Graphiques de densité générés.")

    # Section 3: Plot Bivariate Scenario Quadrants
    print("Generating quadrant plots...")
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    for i, params1 in enumerate(run_params):
        for j, params2 in enumerate(run_params):
            if i >= j:
                continue  # Skip if indices are the same or if params1 has already been compared with params2
            plot_bivariate_scenarios_quadrants(
                npv_df=npv_df,
                pd_df=pd_df,
                params_df=params_df,
                params1=params1,
                params2=params2,
                save_folder_path=QUADRANT_PLOTS_FOLDER,
            )
    print("Quadrant plots generated.")

    print("All tasks completed successfully.")
