library(trisk.analysis)

input_path=file.path("workspace", "trisk_inputs_v2_country_detail")

run_params <- list(
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_B2DS",
        shock_year=2025,
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
        target_scenario="NGFS2023GCAM_B2DS",
        shock_year=2030,
        scenario_geography="Global"
    ),
    list(
        baseline_scenario="NGFS2023GCAM_CP",
        target_scenario="NGFS2023GCAM_NZ2050",
        shock_year=2030,
        scenario_geography="Global"
    )
)


agg_outputs <- run_trisk_sa(input_path, run_params, country_iso2="IN", sector="Power")


npv_df <- agg_outputs[["npv"]]
pd_df <- agg_outputs[["pd"]]


