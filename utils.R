convert_colnames_legacy_to_new <- function(data_source, data_target) {
  # List all files in the source directory
  scenario_data_fps <- list.files(data_source, full.names = TRUE)
  companies_data_fps <- list.files(data_target, full.names = TRUE)
  
  # Define renaming rules for each file pattern
  # file_pattern2 = list(oldCol1 = "newCol1")
  renaming_rules <- list(
    ngfs_carbon_price = list(), # no change
    prewrangled_capacity_factors = list(technology = "ald_business_unit"),
    Scenarios_AnalysisInput = list(technology = "ald_business_unit"),
    price_data_long = list(sector="ald_sector", technology="ald_business_unit"),
    abcd_stress_test_input = list(id="company_id", technology="ald_business_unit")
    )
  
  # Loop through each file
  for(file_path in c(scenario_data_fps, companies_data_fps)) {
    file_name <- basename(file_path)
    
    # Determine which renaming rule to apply based on file name
    applicable_rule <- NULL
    for(pattern in names(renaming_rules)) {
      if(grepl(pattern, file_name)) {
        applicable_rule <- renaming_rules[[pattern]]
        break
      }
    }
    
    # If a renaming rule is applicable, proceed with renaming
    if(!is.null(applicable_rule)) {
      # Read the file (assuming CSV, adjust if different)
      data <- readr::read_csv(file_path)
      
      # Adds column scenario_type to Scenarios_AnalysisInput table
      if (grepl("Scenarios_AnalysisInput",file_path)){
        if (! "scenario_type" %in% colnames(data)){
          scenario_types <- tibble::tribble(
                          ~scenario, ~scenario_type,
                      "WEO2021_APS",     "baseline",
                      "WEO2021_SDS",        "shock",
                    "WEO2021_STEPS",     "baseline",
               "GECO2021_1.5C-Unif",        "shock",
                  "GECO2021_CurPol",     "baseline",
                 "GECO2021_NDC-LTS",        "shock",
                 "WEO2021_NZE_2050",        "shock",
               "NGFS2021_GCAM_B2DS",        "shock",
                 "NGFS2021_GCAM_CP",     "baseline",
                "NGFS2021_GCAM_DN0",        "shock",
                 "NGFS2021_GCAM_DT",        "shock",
                "NGFS2021_GCAM_NDC",     "baseline",
             "NGFS2021_GCAM_NZ2050",        "shock",
            "NGFS2021_MESSAGE_B2DS",        "shock",
              "NGFS2021_MESSAGE_CP",     "baseline",
             "NGFS2021_MESSAGE_DN0",        "shock",
              "NGFS2021_MESSAGE_DT",        "shock",
             "NGFS2021_MESSAGE_NDC",     "baseline",
          "NGFS2021_MESSAGE_NZ2050",        "shock",
             "NGFS2021_REMIND_B2DS",        "shock",
               "NGFS2021_REMIND_CP",     "baseline",
              "NGFS2021_REMIND_DN0",        "shock",
               "NGFS2021_REMIND_DT",        "shock",
              "NGFS2021_REMIND_NDC",     "baseline",
           "NGFS2021_REMIND_NZ2050",        "shock",
                      "IPR2021_FPS",        "shock",
                      "IPR2021_RPS",        "shock",
                 "IPR2021_baseline",     "baseline",
                  "Oxford2021_base",     "baseline",
                  "Oxford2021_fast",        "shock"
          )
          
          data <- data |>
            dplyr::inner_join(scenario_types, by=c("scenario"))

        }
      }
      
      if (grepl("price_data_long",file_path)){
        if ("scenario_geography" %in% colnames(data)){
          data <- data |>
            dplyr::filter(scenario_geography=="Global") 
        }
      }
      
      # Rename columns based on the applicable rule
      new_colnames <- sapply(colnames(data), function(col) {
        if(col %in% names(applicable_rule)) {
          return(applicable_rule[[col]])
        } else {
          return(col)
        }
      })
      colnames(data) <- new_colnames
      
      # Save the file to the target directory with the same name
      readr::write_csv(data, file.path(data_target, file_name))
    }
  }
}
