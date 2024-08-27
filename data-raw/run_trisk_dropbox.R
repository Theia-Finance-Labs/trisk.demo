library(r2dii.utils)
library(trisk.model)


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

trisk.model::run_trisk(
  input_path = st_inputs_folder,
  output_path = file.path("workspace", "trisk_standard_outputs"),
  scenario_geography = "Global",
  baseline_scenario = "GECO2023_CurPol",
  target_scenario = "GECO2023_NDC-LTS",
  carbon_price_model = "no_carbon_tax",
  lgd = 0.45,
  risk_free_rate = 0.02,
  discount_rate = 0.07,
  growth_rate = 0.03,
  div_netprofit_prop_coef = 1,
  shock_year = 2030,
  market_passthrough = 0
)
