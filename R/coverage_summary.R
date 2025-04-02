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


# Define a helper function that creates the Excel file based on the filters provided
create_excel_for_filters <- function(companies_filter = NULL, countries_filter = NULL, file_name, total_ghg, selected_year) {
  
  # --- Process Emissions ---
  filtered_company_emissions <- company_emissions %>% 
    dplyr::filter(
      activity_unit %in% c("tCO2", "tCO2e"),
      year == selected_year
    )
  
  # Apply country filter if provided
  if (!is.null(countries_filter)) {
    filtered_company_emissions <- filtered_company_emissions %>% 
      dplyr::filter(.data$ald_location %in% countries_filter)
  }
  
  # Apply company filter if provided
  if (!is.null(companies_filter)) {
    filtered_company_emissions <- filtered_company_emissions %>% 
      dplyr::filter(company_id %in% companies_filter)
  }
  
  filtered_company_emissions <- filtered_company_emissions %>%
    dplyr::group_by(company_id, company_name, ald_sector, technology, region, ald_location, activity_unit) %>%
    dplyr::summarise(emissions = sum(equity_ownership, na.rm = TRUE), .groups = "drop") %>%
    dplyr::rename(country_iso2 = ald_location, sector = ald_sector) %>%
    dplyr::inner_join(map_countries, by = c("country_iso2" = "country_iso2"))
  
  grouped_company_emissions <- filtered_company_emissions %>%
    dplyr::group_by(.data$country, .data$sector, .data$technology) %>%
    dplyr::summarise(`Emissions (tCO2/tCO2e)` = sum(emissions, na.rm = TRUE), .groups = "drop")
  
  count_companies <- filtered_company_emissions %>%
    dplyr::distinct(company_id, country, country_iso2, sector, technology) %>%
    dplyr::group_by(.data$country, .data$sector, .data$technology) %>%
    dplyr::summarise(`Number of Companies` = dplyr::n(), .groups = "drop") %>%
    dplyr::arrange(dplyr::desc(`Number of Companies`))
  
  summary_companies <- count_companies %>%
    dplyr::left_join(grouped_company_emissions, by = c("country", "sector", "technology"))
  
  summary_companies <- summary_companies %>%
    dplyr::group_by(.data$sector) %>%
    dplyr::mutate(`Percentage of Emissions in Sector` = (`Emissions (tCO2/tCO2e)` / sum(`Emissions (tCO2/tCO2e)`))) %>%
    dplyr::ungroup() %>%
    dplyr::mutate(`Percentage of Total Emissions` = (`Emissions (tCO2/tCO2e)` / sum(`Emissions (tCO2/tCO2e)`))) %>%
    dplyr::rename(`Country` = .data$country, `Technology` = .data$technology) %>%
    dplyr::mutate(Technology = dplyr::case_when(
      grepl("Cap$", .data$Technology) ~ paste0(sub("Cap$", "", .data$Technology), " - Generation"),
      .data$Technology %in% c("Oil", "Gas", "Coal") ~ paste0(.data$Technology, " - Extraction"),
      TRUE ~ .data$Technology
    ))
  
  
  # --- Process Company Activities ---
  unique_companies <- company_activities %>% 
    dplyr::filter(
      activity_unit %in% c("t coal", "t cement", "t steel", "MW", "tkm", "pkm", "# vehicles", "GJ"),
      year == selected_year
    )
  
  # Apply country filter if provided
  if (!is.null(countries_filter)) {
    unique_companies <- unique_companies %>% 
      dplyr::filter(.data$ald_location %in% countries_filter)
  }
  
  # Apply company filter if provided
  if (!is.null(companies_filter)) {
    unique_companies <- unique_companies %>% 
      dplyr::filter(company_id %in% companies_filter)
  }
  
  n_unique_companies <- unique_companies %>% 
    dplyr::distinct(company_id) %>% 
    dplyr::count() %>% 
    dplyr::rename(`Number of Unique Companies` = n)
  
  
  # --- Summary Emissions ---

  total_emissions <- summary_companies %>% 
    dplyr::group_by(sector) %>% 
    dplyr::summarise(`Total Emissions` = sum(`Emissions (tCO2/tCO2e)`)) %>% 
    dplyr::mutate(
      `Total GHG Malaysia` = total_ghg,
      `Share of GHG` = `Total Emissions` / `Total GHG Malaysia`
    )
  
  
  # --- Write Excel Output ---
  openxlsx::write.xlsx(list(
    `Emissions Coverage` = summary_companies,
    `Summary Emissions` = total_emissions,
    `Summary Companies`   = n_unique_companies
  ), file = file_name)
}

# ----------------------
# Define paths and filters
path_ar_data_raw <- r2dii.utils::path_dropbox_2dii(
  "ST INPUTS",
  "ST_INPUTS_PRODUCTION",
  "AR-Company-Indicators_2023Q4.xlsx"
)

outputs_list <- prepare_asset_impact_data(ar_data_path = path_ar_data_raw)
DB_company_activities <- outputs_list[["company_activities"]]
DB_company_emissions  <- outputs_list[["company_emissions"]]

company_activities <- pivot_equity_ownership_columns(DB_company_activities)
company_emissions  <- pivot_equity_ownership_columns(DB_company_emissions)

# For the selected country and company filters:
use_countries <- "MY"
use_countries_vector <- strsplit(use_countries, ",")[[1]]

companies_HQ <- readxl::read_xlsx(path_ar_data_raw, sheet = "Company Information")
use_companies <- companies_HQ %>% 
  dplyr::filter(`Country of Domicile` %in% use_countries_vector) %>% 
  dplyr::pull(`Company ID`)

map_countries <- readr::read_rds("workspace/bench_regions.rds") %>% 
  dplyr::distinct(country_iso, country) %>% 
  dplyr::rename(country_iso2 = country_iso)

selected_year <- 2022
total_ghg <- 325705280 #259326110 #325705280
# ----------------------
# Create Excel files for the three cases

# 1. Case: Filter on both company and country selected
create_excel_for_filters(
  companies_filter = use_companies,
  countries_filter = use_countries_vector,
  file_name = "workspace/coverage_companies_both.xlsx",
  selected_year=selected_year,
  total_ghg=total_ghg
)

# 2. Case: Filter only on country selected (ignore company filter)
create_excel_for_filters(
  companies_filter = NULL,
  countries_filter = use_countries_vector,
  file_name = "workspace/coverage_companies_country_only.xlsx",
  selected_year=selected_year,
  total_ghg=total_ghg
)

# 3. Case: Filter only on company selected (ignore country filter)
create_excel_for_filters(
  companies_filter = use_companies,
  countries_filter = NULL,
  file_name = "workspace/coverage_companies_company_only.xlsx",
  selected_year=selected_year,
  total_ghg=total_ghg
)
