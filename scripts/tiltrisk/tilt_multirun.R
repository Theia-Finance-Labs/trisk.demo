library(trisk.model)


input_path <- r2dii.utils::path_dropbox_2dii(fs::path("ST Inputs","ST_INPUTS_MASTER"))

trisk_output_path <- here::here("workspace", "tiltrisk", "trisk_runs")
fs::dir_create(trisk_output_path)

run_params = list(
  list(
    scenario_geography="Global",
    baseline_scenario="IPR2023_baseline",
    shock_scenario="IPR2023_FPS",
    shock_year=2030
  ),
  list(
    scenario_geography="Europe",
    baseline_scenario="WEO2021_APS",
    shock_scenario="WEO2021_SDS",
    shock_year=2030
  )
)


for (run_param in run_params){
  do.call(run_trisk, c(list(output_path = trisk_output_path, input_path = input_path), run_param))
}
