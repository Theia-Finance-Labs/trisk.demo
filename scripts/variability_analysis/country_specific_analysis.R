library(trisk.analysis)

input_path <- file.path("workspace", "trisk_inputs_v2_country_detail")
project_output_path <- file.path("workspace", "india_variability_analysis")
dir.create(project_output_path, showWarnings = FALSE, recursive = TRUE)

run_params <- list(
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_B2DS",
        shock_year=2025,
        scenario_geography="Global"
    ),
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_B2DS",
        shock_year=2030,
        scenario_geography="Global"
    ),
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_NZ2050",
        shock_year=2025,
        scenario_geography="Global"
    ),
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_NZ2050",
        shock_year=2030,
        scenario_geography="Global"
    )
)


sa_outputs <- run_trisk_sa(input_path, run_params, country_iso2="IN", sector="Power")


npv_df <- sa_outputs[["npv"]]
pd_df <- sa_outputs[["pd"]]
params_df <- sa_outputs[["params"]]

npv_df |> readr::write_csv(file.path(project_output_path, "npvs.csv"))
pd_df |> readr::write_csv(file.path(project_output_path, "pds.csv"))
params_df |> readr::write_csv(file.path(project_output_path, "params.csv"))

