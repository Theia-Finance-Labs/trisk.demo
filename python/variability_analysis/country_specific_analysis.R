# run_trisk_analysis.R
library(trisk.analysis)

run_analysis <- function(input_path, project_output_path, run_params, country_iso2, sector) {
    dir.create(project_output_path, showWarnings = FALSE, recursive = TRUE)
    

    # Read the input CSV files
    assets_data <- readr::read_csv(file.path(input_path, "assets.csv"))
    scenarios_data <- readr::read_csv(file.path(input_path, "scenarios.csv"))
    financial_data <- readr::read_csv(file.path(input_path, "financial_features.csv"))
    carbon_data <- readr::read_csv(file.path(input_path, "ngfs_carbon_price.csv"))
    

    sa_outputs <- run_trisk_sa(assets_data, scenarios_data, financial_data, carbon_data, run_params, country_iso2=country_iso2, sector=sector)
    
    npv_df <- sa_outputs[["npv"]]
    pd_df <- sa_outputs[["pd"]]
    params_df <- sa_outputs[["params"]]
    trajectories_df <- sa_outputs[["trajectories"]]
    
    npv_df |> readr::write_csv(file.path(project_output_path, "npvs.csv"))
    pd_df |> readr::write_csv(file.path(project_output_path, "pds.csv"))
    params_df |> readr::write_csv(file.path(project_output_path, "params.csv"))
    trajectories_df |> readr::write_csv(file.path(project_output_path, "trajectories.csv"))
}


