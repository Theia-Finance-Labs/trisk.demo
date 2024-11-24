library(dplyr)
assets_data <- readr::read_csv("workspace/trisk_inputs_v2_legacy_countries2/assets.csv")

filtered_assets <- assets_data %>% 
    filter(
        ((country_iso2 %in% c("NG", "GH")) & (technology=="GasCap") ) |
        ( (country_iso2 %in% c("AO", "KE")) & (technology=="OilCap") ) |
        ( (country_iso2 %in% c("ZA")) & (technology=="CoalCap") ) |
        ( (country_iso2 %in% c("ZA", "KE", "ML", "MZ")) & (technology=="RenewablesCap") ) |
        ( (country_iso2 %in% c("GA", "NG", "AO")) & (technology=="Oil") ) |
        ( (country_iso2 %in% c("GH", "NG", "AO")) & (technology=="Gas") ) |
        ( (country_iso2 %in% c("MZ", "NG")) & (technology=="Coal") ))
        
selection <- filtered_assets %>% distinct(company_name, country_iso2, sector, technology) %>% 
    group_by(technology) %>% sample_n(2) %>% arrange(sector, technology) %>% ungroup(

    )
selection <- selection %>%
  dplyr::mutate(
    exposure_value = runif(n = n(), min = 100000, max = 10000000),
    loss_given_default = runif(n = n(), min = 0, max = 1),
    term = sample(1:5, size = n(), replace = TRUE)
  )

selection %>% writexl::write_xlsx("ifc_portfolio.xlsx")
