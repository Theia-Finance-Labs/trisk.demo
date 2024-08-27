library(trisk.analysis)
library(dplyr)

# OPEN SOURCE DATA DOWNLOAD
# Download TRISK input data from the specified endpoint
endpoint_url <- "https://crispy-datamodels-bucket.fra1.cdn.digitaloceanspaces.com"
s3_path <- "crispy-datamodels-bucket/trisk_V2/csv"
local_trisk_inputs_folder <- file.path("data-raw", "data", "trisk_inputs")

download_trisk_inputs(endpoint_url, s3_path, local_trisk_inputs_folder)


#


# SENSITIVITY ANALYSIS
# Run sensitivity analysis by varying parameters across multiple TRISK runs
run_params <- list(
  list(
    scenario_geography = "Global",
    baseline_scenario = "Steel_baseline",
    target_scenario = "Steel_NZ",
    shock_year = 2030
  ),
  list(
    scenario_geography = "Global",
    baseline_scenario = "Steel_baseline",
    target_scenario = "Steel_NZ",
    shock_year = 2025
  )
)

sensitivity_analysis_results_on_filtered_assets <- run_trisk_sa(
  input_path = local_trisk_inputs_folder,
  run_params = run_params,
  country_iso2 = c("US", "AR"),
  sector = "Steel",
  technology = c("EAF-DRI", "BOF-BF")
)



# Get sensitivity analysis results for different result types
npvs <- sensitivity_analysis_results_on_filtered_assets[["npv"]]
pds <- sensitivity_analysis_results_on_filtered_assets[["pd"]]
trajectories <- sensitivity_analysis_results_on_filtered_assets[["trajectories"]]
params <- sensitivity_analysis_results_on_filtered_assets[["params"]]


# Load the assets data using readr
assets_data <- readr::read_csv(file.path(local_trisk_inputs_folder, "assets.csv"))

# Merge plant_age_years with npvs and trajectories using dplyr
npvs <- dplyr::left_join(npvs, assets_data%>%dplyr::distinct(asset_id, plant_age_years, country_iso2), by = "asset_id")
trajectories <- dplyr::left_join(trajectories, assets_data%>%dplyr::distinct(asset_id, plant_age_years, country_iso2), by = "asset_id")
