import os
from rpy2 import robjects
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector, ListVector

# Enable the conversion between Pandas DataFrame and R DataFrame
pandas2ri.activate()


def run_r_analysis(input_path, project_output_path, run_params, country_iso2, sector):
    """
    Runs the R analysis by calling the R function from the provided script.

    Parameters:
    - input_path (str): Path to the input directory for trisk analysis.
    - project_output_path (str): Path where output files will be saved.
    - run_params (list of dicts): List of run parameters.
    - country (str): Country ISO code.
    - sector (str): Sector to analyze.
    """

    # Get the current directory of this Python script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the R script
    r_script_path = os.path.join(current_directory, "country_specific_analysis.R")
    # Import the R script using the full path
    r.source(r_script_path)

    # Convert each dictionary in the list to an R ListVector
    run_params_r = ListVector(
        {str(i): ListVector(params) for i, params in enumerate(run_params)}
    )

    # Assign parameters to the R environment
    robjects.globalenv["input_path"] = input_path
    robjects.globalenv["project_output_path"] = project_output_path
    robjects.globalenv["run_params"] = run_params_r
    robjects.globalenv["country_iso2"] = country_iso2
    robjects.globalenv["sector"] = sector

    # Define the R function to run
    run_analysis_r = robjects.r["run_analysis"]

    # Call the R function with parameters
    run_analysis_r(input_path, project_output_path, run_params_r, country_iso2, sector)


if __name__ == "__main__":
    # Define the paths
    input_path = os.path.join("workspace", "trisk_inputs_v2_country_detail")
    project_output_path = os.path.join("workspace", "india_variability_analysis")

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
    ]

    country_iso2 = "IN"
    sector = "Power"

    # Run the R analysis with the defined parameters
    run_r_analysis(input_path, project_output_path, run_params, country_iso2, sector)
