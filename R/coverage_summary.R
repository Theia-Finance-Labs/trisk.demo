library(dplyr)
library(readr)



# RAW

#' read Asset Resolution data
#'
#' @param path_ar_data_raw path to AR excel input
#'
#' @param sheet_name name of excel sheet
#'
read_asset_resolution <- function(path_ar_data_raw, sheet_name) {
  if (sheet_name %in% c("Company Activities", "Company Emissions")) {
    
  
  ar_data <- readxl::read_xlsx(path_ar_data_raw,
                               sheet = sheet_name) %>%
    dplyr::select(-dplyr::starts_with("Direct Ownership")) %>%
    dplyr::rename(
      company_id = .data$`Company ID`,
      company_name = .data$`Company Name`,
      ald_sector = .data$`Asset Sector`,
      technology = .data$`Asset Technology`,
      technology_type = .data$`Asset Technology Type`,
      region = .data$`Asset Region`,
      ald_location = .data$`Asset Country`,
      activity_unit = .data$`Activity Unit`
    )

    
  } else if (sheet_name == "Company Information") {
    ar_data <- readxl::read_xlsx(path_ar_data_raw,
                                 sheet = sheet_name) %>%
      dplyr::rename(
        company_id = .data$`Company ID`,
        company_name = .data$`Company Name`,
        is_ultimate_parent = .data$`Is Ultimate Parent`,
        ald_location = .data$`Country of Domicile`,
        lei = .data$`LEI`
      )
  } else {
    stop("Sheet name not recognized")
  }

  return(ar_data)
}


#' rename technology column according to some rules
#' @param ar_data ar_data
#'
rename_technology <- function(ar_data) {
  ar_data <- ar_data %>%
    dplyr::mutate(
      technology = dplyr::case_when(
        .data$ald_sector == "Coal" ~ "Coal",
        .data$technology %in% c("Gas", "Natural Gas Liquids") ~ "Gas",
        .data$technology == "Oil and Condensate" ~ "Oil",
        .data$technology == "ICE Diesel" ~ "ICE",
        .data$technology == "ICE Gasoline" ~ "ICE",
        .data$technology == "ICE CNG" ~ "ICE",
        .data$technology == "ICE Propane" ~ "ICE",
        .data$technology == "ICE E85+" ~ "ICE",
        .data$technology == "Hybrid No-Plug" ~ "Hybrid",
        .data$technology == "Hybrid Plug-In" ~ "Hybrid",
        .data$technology == "Fuel Cell" ~ "FuelCell",
        TRUE ~ .data$technology
      )
    ) |>
      # hardcoded renaming for Steel sector
      dplyr::mutate(technology = dplyr::case_when(
        technology == 'Basic Oxygen Furnace' & technology_type == 'Integrated Blast Furnace' ~ 'BOF-BF',
        technology == 'Basic Oxygen Furnace' & technology_type == 'Integrated DRI Furnace' ~ 'BOF-DRI',
        technology == 'Electric Arc Furnace' & technology_type == 'Integrated Blast Furnace' ~ 'EAF-BF',
        technology == 'Electric Arc Furnace' & technology_type == 'Integrated DRI Furnace' ~ 'EAF-DRI',
        technology == 'Electric Arc Furnace' & technology_type == 'Integrated Open Hearth Furnace' ~ 'EAF-OHF',
        technology == 'Electric Arc Furnace' & technology_type == 'Mini-Mill' ~ 'EAF-MM',
        TRUE ~ technology  # Default case to keep existing value
      ))
  return(ar_data)
}
#' rename ald_sector column according to some rules
#' @param ar_data ar_data
#'
rename_ald_sector <- function(ar_data) {
  ar_data <- ar_data %>%
    dplyr::mutate(ald_sector = dplyr::if_else(.data$ald_sector == "LDV", "Automotive", .data$ald_sector)) %>%
    dplyr::mutate(
      ald_sector = dplyr::case_when(
        .data$technology == "Coal" ~ "Coal",
        .data$technology %in% c("Gas", "Oil") ~ "Oil&Gas",
        TRUE ~ .data$ald_sector
      )
    )
  return(ar_data)
}

#' Prepare Asset Impact data before transformation to abcd
#' @param ar_data_path file path to the source Asset Resolution xlsx
#'
#' @export
prepare_asset_impact_data <- function(ar_data_path) {
  
  # Asset Impact specific data preparation
  
  company_activities <-
    read_asset_resolution(ar_data_path,
                          sheet_name = "Company Activities")
  company_emissions <-
    read_asset_resolution(ar_data_path,
                          sheet_name = "Company Emissions")

  company_activities <- rename_technology(company_activities)
  company_emissions <- rename_technology(company_emissions)


  company_activities <- rename_ald_sector(company_activities)
  company_emissions <- rename_ald_sector(company_emissions)

  
  return(
    list(
      company_activities = company_activities,
      company_emissions = company_emissions
    )
  )

}

#' pivot values of Equity Ownership, to be used as yearly production/emissions
#' TODO when Direct Ownership is not nan, use it when Equity Ownership is nan ?
#'
#' @param ar_data ar_data
#'
pivot_equity_ownership_columns <- function(ar_data) {
  ar_data <- ar_data %>%
    tidyr::pivot_longer(
      cols = dplyr::starts_with("Equity Ownership "),
      names_to = "year",
      values_to = "equity_ownership"
    ) %>%
    dplyr::mutate(year = stringr::str_extract(.data$year, stringr::regex("\\d+")))

  return(ar_data)
}


options(r2dii_dropbox=r2dii_dropbox)


# parameters ========================================

path_ar_data_raw <-
  r2dii.utils::path_dropbox_2dii(
    "ST INPUTS",
    "ST_INPUTS_PRODUCTION",
    "AR-Company-Indicators_2023Q4.xlsx"
  )

outputs_list <- prepare_asset_impact_data(ar_data_path = path_ar_data_raw)
DB_company_activities <- outputs_list[["company_activities"]]
DB_company_emissions <- outputs_list[["company_emissions"]]

company_activities <-
  pivot_equity_ownership_columns(DB_company_activities)
company_emissions <-
  pivot_equity_ownership_columns(DB_company_emissions)


# use_countries <- geo_countries %>% filter(scenario_geography=="MiddleEastAndAfrica") %>% pull(country_iso2_list)
# use_countries <- "AO,BJ,BW,BF,BI,CV,CM,CF,TD,KM,CD,CG,CI,DJ,GQ,ER,ET,GA,GM,GH,GN,GW,KE,LS,LR,MG,MW,ML,MR,MU,MZ,NA,NE,NG,RW,ST,SN,SC,SL,SO,ZA,SS,SD,TZ,TG,UG,ZM,ZW"
use_countries <- "MY"
# Step 1: Split the string into a vector
use_countries_vector <- strsplit(use_countries, ",")[[1]]


map_countries <- readr::read_rds("workspace/bench_regions.rds") %>% distinct(country_iso, country) %>% rename(country_iso2=country_iso)
selected_year <- 2022
# ==================================================
# EMISIONS PER TECHNOLOGY , AT THE LAST FORECAST YEAR
# ==================================================

# Filter and summarize emissions
filtered_company_emissions <- company_emissions %>% 
  filter(activity_unit %in% c("tCO2", "tCO2e"), year==selected_year, .data$ald_location %in% use_countries_vector) %>%
  group_by(company_id, company_name, ald_sector, technology, region, ald_location, activity_unit) %>%
  summarise(emissions = sum(equity_ownership, na.rm = TRUE), .groups = "drop") %>%
  rename(country_iso2 = ald_location, sector=ald_sector)  %>%
  inner_join(map_countries)
  #  %>% inner_join(filtered_assets %>% distinct(company_id, country_iso2, sector, technology), 
  #            by = c("company_id", "technology", "country_iso2")) 
    
    
grouped_company_emissions <-  filtered_company_emissions %>%
    group_by(.data$country, .data$sector, .data$technology) %>%
    summarise(`Emissions (tCO2/tCO2e)` = sum(emissions, na.rm = TRUE), .groups = "drop")

# Aggregate and summarize the data
count_companies <- filtered_company_emissions %>%
  distinct(company_id, country, country_iso2, sector, technology) %>%
  group_by(.data$country, .data$sector, .data$technology) %>%
  summarise(`Number of Companies` = n(), .groups = "drop") %>%
  arrange(desc(`Number of Companies`))

# Join emissions data to count_companies
summary_companies <- count_companies %>%
  left_join(grouped_company_emissions , 
            by = c("country", "sector", "technology"))

# Calculate the percentage of total emissions per sector
summary_companies <- summary_companies %>%
  group_by(.data$sector) %>%
  mutate(`Percentage of Emissions in Sector` = (`Emissions (tCO2/tCO2e)` / sum(`Emissions (tCO2/tCO2e)`))) %>%
  ungroup()

summary_companies <- summary_companies %>%
  mutate(`Percentage of Total Emissions` = (`Emissions (tCO2/tCO2e)` / sum(`Emissions (tCO2/tCO2e)`)))

# Rename columns
summary_companies <- summary_companies %>%
  rename(`Country` = .data$country, `Technology` = .data$technology) 

# Rename technologies based on the rules and remove "Cap"
summary_companies <- summary_companies %>%
  mutate(Technology = case_when(
    grepl("Cap$", .data$Technology) ~ paste(sub("Cap$", "", .data$Technology), "- Generation"),
    .data$Technology %in% c("Oil", "Gas", "Coal") ~ paste(.data$Technology, "- Extraction"),
    TRUE ~ .data$Technology
  )) 



# # Save the filtered datasets to variables based on the updated technology names
# power_nonrenewable <- dplyr::filter(summary_companies, .data$sector == "Power", !(.data$Technology %in%  c("Renewables - Generation", "Hydro - Generation")))
# power_renewable <- dplyr::filter(summary_companies, .data$sector == "Power", (.data$Technology %in%  c("Renewables - Generation", "Hydro - Generation")))
# coal <- dplyr::filter(summary_companies, .data$sector == "Coal")
# oil_and_gas <- dplyr::filter(summary_companies, .data$sector == "Oil&Gas")
# steel <- dplyr::filter(summary_companies, .data$sector == "Steel")
# shipping <- dplyr::filter(summary_companies, .data$sector == "Shipping")
# cement <- dplyr::filter(summary_companies, .data$sector == "Cement")


# # Write the datasets to an Excel file
# openxlsx::write.xlsx(list(
#   `All data`= summary_companies,
#   `Power NonRenewable` = power_nonrenewable,
#   `Power Renewable` = power_renewable,
#   Coal = coal,
#   `Oil And Gas` = oil_and_gas,
#   Steel = steel,
#   Shipping = shipping,
#   Cement = cement
# ), file = "workspace/coverage_companies.xlsx")

# ==================================================
# OVERALL STATS
# ==================================================


n_unique_companies  <-  company_activities %>% 
  filter(activity_unit %in% c("t coal", "t cement",  "t steel","MW", "tkm", "pkm","# vehicles", "GJ"), 
    year==selected_year, 
    .data$ald_location %in% use_countries_vector) %>%
  distinct(company_id) %>% count() %>% rename(`Number of Unique Companies`=`n`)


total_ghg <- 259326110 #325705280
total_emissions <- summary_companies %>% 
  group_by(sector) %>% 
  summarise(`Total Emissions` = sum(`Emissions (tCO2/tCO2e)`)) %>% 
  mutate(
    `Total GHG Malaysia` = total_ghg,
    `Share of GHG` = `Total Emissions`/`Total GHG Malaysia`)


# Write the datasets to an Excel file
openxlsx::write.xlsx(list(
  `Emissions Coverage`= summary_companies,
  `Summary Emissions`= total_emissions,
  `Summary Companies` = n_unique_companies
), file = "workspace/coverage_companies.xlsx")
