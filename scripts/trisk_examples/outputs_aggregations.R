library(stress.test.plot.report)
library(dplyr)

# INTRO ******************************************************************

# Use this script to aggregate results to a desired index
# Independant crispy outputs can be navigated with the "run_id" column values

# PARAMETERS *************************************************************


trisk_output_folders <- c(
    here::here("workspace", "India Runs", "IndiaAssetsinCountry"),
    here::here("workspace", "India Runs", "IndiaHQandAssetsinCountry"),
    here::here("workspace", "India Runs", "IndiaHQinCountry")
)

output_files_path <- here::here("workspace", "India Runs Aggregate")
fs::dir_create(output_files_path)

use_ald_sectors <- c("Power")

index_cols <- c("run_id", "ald_sector", "ald_business_unit") #"company_id", "company_name"


# ************************************************************************

# I. AGGREGATE CRISPY ====================================================


parameters_cols <- c("roll_up_type", "scenario_geography", "baseline_scenario", "shock_scenario", 
"risk_free_rate", "discount_rate", "div_netprofit_prop_coef", 
"carbon_price_model", "market_passthrough", "financial_stimulus", 
"start_year", "growth_rate", "shock_year")

# index_cols <- c("run_id", "ald_sector", "ald_business_unit") #"company_id", "company_name"

# npv_cols <- c("net_present_value_baseline", "net_present_value_shock")
# pd_cols <- c("term", "pd_baseline", "pd_shock")


for (folder_name in trisk_output_folders){
    multi_crispy <- stress.test.plot.report:::load_multiple_crispy(crispy_outputs_dir = folder_name)

    multi_crispy_agg <- multi_crispy %>%
        dplyr::filter(ald_sector %in% use_ald_sectors) %>%
        dplyr::mutate(
            npv_change = (net_present_value_shock - net_present_value_baseline) / net_present_value_baseline,
            pd_diff = pd_shock - pd_baseline
            ) %>%
        dplyr::group_by_at(c(index_cols, parameters_cols)) %>%
        dplyr::summarise(
            npv_change_weight_avg = stats::weighted.mean(npv_change, w=.data$net_present_value_baseline),
            npv_change_avg = mean(npv_change),
            npv_change_median = median(npv_change),
            pd_diff_weight_avg = stats::weighted.mean(pd_diff, w=.data$net_present_value_baseline),
            pd_diff_avg = mean(pd_diff),
            pd_diff_median = median(pd_diff),

            .groups="drop"
        )

    readr::write_csv(multi_crispy_agg, file.path(output_files_path, paste0(basename(folder_name), "_crispy.csv")))
}


# II. AGGREGATE TRAJECTORIES ===========================================================================

# index_cols <- c("run_id", "ald_sector", "ald_business_unit", "year" ) #"company_name", , "company_id"


# trajectories_cols <- c("production_baseline_scenario", "production_target_scenario", "production_shock_scenario")
# "price_baseline_scenario", "price_shock_scenario", "net_profits_baseline_scenario", 
# "net_profits_shock_scenario", "discounted_net_profits_baseline_scenario", 
# "discounted_net_profits_shock_scenario"

# "production_plan_company_technology", "phase_out"
for (folder_name in trisk_output_folders) {
    multi_trajectory <- stress.test.plot.report:::load_multiple_trajectories(crispy_outputs_dir = folder_name)
    
    multi_trajectory_agg <- multi_trajectory %>%
        dplyr::group_by_at(c(index_cols, "year")) %>%
        dplyr::summarise(
            production_baseline_scenario = sum(production_baseline_scenario),
            production_target_scenario = sum(production_target_scenario),
            production_shock_scenario = sum(production_shock_scenario),
            .groups = "drop"
        ) %>%
        dplyr::group_by_at(index_cols) %>%
        dplyr::mutate(
            production_baseline_scenario_perc = production_baseline_scenario / max(production_baseline_scenario, na.rm = TRUE),
            production_target_scenario_perc = production_target_scenario / max(production_target_scenario, na.rm = TRUE),
            production_shock_scenario_perc = production_shock_scenario / max(production_shock_scenario, na.rm = TRUE)
        ) %>%
        dplyr::ungroup()
    
    readr::write_csv(multi_trajectory_agg, file.path(output_files_path, paste0(basename(folder_name), "_trajectories.csv")))
}