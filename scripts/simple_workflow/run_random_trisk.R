library(trisk.model)

# Function to get the latest timestamped folder
get_latest_timestamped_folder <- function(directory) {
  dirs <- list.dirs(directory, full.names = TRUE, recursive = FALSE)
  latest_dir <- dirs[which.max(file.info(dirs)$mtime)]
  return(latest_dir)
}

input_path = get_latest_timestamped_folder(fs::path("workspace","st_inputs"))

params_list <- get_scenario_geography_x_ald_sector(input_path = input_path)
random_row <- params_list[sample(nrow(params_list), 1), ]
# Extract each column value into a variable named like the column
scenario_geography <- random_row$scenario_geography
baseline_scenario <- random_row$baseline_scenario
shock_scenario <- random_row$shock_scenario

run_trisk(
    input_path = input_path,
    output_path = fs::path("workspace","st_outputs"),
    baseline_scenario=baseline_scenario,
    shock_scenario=shock_scenario,
    scenario_geography=scenario_geography
    )
