library(r2dii.utils)
library(trisk.analysis)
library(magrittr)
library(stringdist)

# Créer le répertoire si nécessaire
dir.create("data-raw/data/opendata_steel_assets", recursive = TRUE, showWarnings = FALSE)


# download gem steel plants
download.file(
  "https://scenarios-repository.fra1.cdn.digitaloceanspaces.com/opendata_steel_assets/gem_steel_april_2024_steel_plants.csv",
  destfile = "data-raw/data/opendata_steel_assets/gem_steel_april_2024_steel_plants.csv"
)

# Load CSV files

gem_assets <- readr::read_csv("data-raw/data/opendata_steel_assets/gem_steel_april_2024_steel_plants.csv") %>%
  dplyr::select(plant_id, owner, workforce_size) %>%
  dplyr::mutate(workforce_size = as.numeric(workforce_size))


# RUN TRISK

# Trisk runs on AI data
run_with_aggregated_countries_on_global_geography <- TRUE
if (run_with_aggregated_countries_on_global_geography) {
  st_inputs_folder <-
    r2dii.utils::path_dropbox_2dii(
    "ST INPUTS",
    "ST_INPUTS_AI_GEOGRAPHIES"
  )
} else { 
  st_inputs_folder <-
    r2dii.utils::path_dropbox_2dii(
    "ST INPUTS",
    "ST_INPUTS_AI_COUNTRIES"
  )
}

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
  input_path = st_inputs_folder,
  run_params = run_params,
)


# Print sensitivity analysis results for different result types
npvs <- sensitivity_analysis_results_on_filtered_assets[["npv"]]
pds <- sensitivity_analysis_results_on_filtered_assets[["pd"]]
trajectories <- sensitivity_analysis_results_on_filtered_assets[["trajectories"]]
params <- sensitivity_analysis_results_on_filtered_assets[["params"]]

# MERGE TRISK OUTPUTS TO GEM/SFI DATA 

# Perform fuzzy matching between npv results and assets dataset in batches
batch_size <- 100
num_batches <- ceiling(nrow(npvs) / batch_size)

merged_results <- data.frame()

pb <- progress::progress_bar$new(total = num_batches)

for (i in 1:num_batches) {
  start <- (i-1) * batch_size + 1
  end <- min(i * batch_size, nrow(npvs))
  
  npvs_batch <- npvs[start:end, ]
  
  batch_results <- npvs_batch %>%
    dplyr::mutate(match = stringdist::amatch(company_name, gem_assets$owner, method = "lv", maxDist = 0.2)) %>%
    dplyr::left_join(gem_assets %>% dplyr::mutate(row = dplyr::row_number()), by = c("match" = "row")) %>%
    dplyr::mutate(confidence = 1 - stringdist::stringdist(company_name, owner, method = "lv") / pmax(nchar(company_name), nchar(owner))) %>%
    dplyr::select(-match)
  
  merged_results <- dplyr::bind_rows(merged_results, batch_results)
  
  pb$tick()
}

merged_results <- tibble::as_tibble(merged_results)

