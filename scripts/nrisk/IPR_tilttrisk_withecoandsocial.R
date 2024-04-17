library(dplyr)


### FOR IPR because of longer time horizon

trajectories_data_bu <-
  readr::read_csv(here::here("workspace/tiltrisk/trajectories_data_bu.csv")) %>%
  dplyr::filter(run_id == "32a7d72b-480d-4de3-8522-6bfb40cfe2a8")
trajectories_data_sector <-
  readr::read_csv(here::here("workspace/tiltrisk/trajectories_data_sector.csv")) %>%
  dplyr::filter(run_id == "32a7d72b-480d-4de3-8522-6bfb40cfe2a8")


items <- list(
  list(
    data = trajectories_data_bu,
    group_cols = c("run_id", "ald_sector", "ald_business_unit", "country")
  )
  ,
  list(
    data = trajectories_data_sector,
    group_cols = c("run_id", "ald_sector", "country")
  )
)

npv_changes_df <- NULL
for (item in items) {
  data = item$data
  group_cols = item$group_cols

  ##normal trajectory data, but without Terminal Value!

  # Defining the factors
  ecofactor <- -0.0293
  socfactor <- -0.1493
  growth_rate <- 0.03
  discount_rate <- 0.07


  # Perform the adjustments and calculations grouped by 'ald_business_unit'
  data_grouped <- data %>%
    group_by_at(group_cols) %>% ##here we would need to group also for country? and scenaro run if we want to, but IPR is until 2050
    mutate(# Create initial 'eco' and 'soc' columns
      eco = net_profits_shock_scenario,
      soc = net_profits_shock_scenario) %>%
    mutate(# Adjust 'eco' for the year 2050
      eco = ifelse(year == 2048, eco * (1 + ecofactor), eco),
      # Adjust 'soc' for the year 2050
      soc = ifelse(year == 2048, soc * (1 + socfactor), soc)) %>%
    mutate(
      # Adjust 'eco' for the years 2030-2049
      eco = ifelse(
        year >= 2030 & year < 2048,
        eco + (eco[year == 2048] - net_profits_shock_scenario[year == 2048]) / 19 * (year - 2029),
        eco
      ),
      # Adjust 'soc' for the years 2030-2049
      soc = ifelse(
        year >= 2030 & year < 2048,
        soc + (soc[year == 2048] - net_profits_shock_scenario[year == 2048]) / 19 * (year - 2029),
        soc
      )
    ) %>%
    mutate(# Calculate 'disc_eco'
      disc_eco = eco / ((1 + discount_rate) ^ (year - 2022)),
      # Calculate 'disc_soc'
      disc_soc = soc / ((1 + discount_rate) ^ (year - 2022))) %>%
    mutate(
      # Calculate Terminal Values and discount them
      TV_net_profits_baseline = ifelse(
        year == 2048,
        net_profits_baseline_scenario * (1 + growth_rate) / (discount_rate - growth_rate),
        0
      ),
      TV_net_profits_shock = ifelse(
        year == 2048,
        net_profits_shock_scenario * (1 + growth_rate) / (discount_rate - growth_rate),
        0
      ),
      TV_eco = ifelse(
        year == 2048,
        eco * (1 + growth_rate) / (discount_rate - growth_rate),
        0
      ),
      TV_soc = ifelse(
        year == 2048,
        soc * (1 + growth_rate) / (discount_rate - growth_rate),
        0
      )
    ) %>%
    mutate(
      # Discount Terminal Values
      disc_TV_net_profits_baseline = TV_net_profits_baseline / ((1 + discount_rate) ^
                                                                  (2049 - 2022)),
      disc_TV_net_profits_shock = TV_net_profits_shock / ((1 + discount_rate) ^
                                                            (2049 - 2022)),
      disc_TV_eco = TV_eco / ((1 + discount_rate) ^ (2049 - 2022)),
      disc_TV_soc = TV_soc / ((1 + discount_rate) ^ (2049 - 2022))
    )

  # Calculate NPVs including Terminal Values for each business unit
  npv_calculations <- data_grouped %>%
    summarise(
      NPV_baseline = sum(
        ifelse(year >= 2030, discounted_net_profits_baseline_scenario, 0)
      ) + sum(disc_TV_net_profits_baseline),
      NPV_shock = sum(
        ifelse(year >= 2030, discounted_net_profits_shock_scenario, 0)
      ) + sum(disc_TV_net_profits_shock),
      NPV_disc_eco = sum(ifelse(year >= 2030, disc_eco, 0)) + sum(disc_TV_eco),
      NPV_disc_soc = sum(ifelse(year >= 2030, disc_soc, 0)) + sum(disc_TV_soc)
    )


  # Output the table
  print(npv_calculations)

  # Calculating the change in NPV relative to the NPV baseline
  npv_changes <- npv_calculations %>%
    mutate(
      Change_NPV_shock = (NPV_shock / NPV_baseline) - 1,
      Change_NPV_disc_eco = (NPV_disc_eco / NPV_baseline) - 1,
      Change_NPV_disc_soc = (NPV_disc_soc / NPV_baseline) - 1
    ) %>%
    select_at(c(
      group_cols,
      "Change_NPV_shock",
      "Change_NPV_disc_eco",
      "Change_NPV_disc_soc"
    ))

  npv_changes_df <- bind_rows(npv_changes_df, npv_changes)
}

npv_changes_df %>% readr::write_csv(here::here("workspace/tiltrisk/npv_changes_IPR.csv"))

