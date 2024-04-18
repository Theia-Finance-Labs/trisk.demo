#################################################
####### Nature Risk Model Software ##############
#################################################
####### Willingness to Pay (WTP)
####### Effect of Internalizing Nature Risk Costs

#'The model forms part of the LIFE STRESS project.
#'The LIFE STRESS project has received funding from the LIFE Programme of the
#' European Union.‘ The contents of this publication are the sole  responsibility
#' of Theia Finance Labs and  do  not necessarily reflect  the  opinion
#' of the European Union. Project: Project: 101074271 — LIFE21-GIC-DE-Stress.


## Inputs
## Please adjust below the Inputs of the WTP Model

# Total Revenues (tr)
# Net Profit Margin (npm)
# Dependency (d)
# Share of ecosystem cost internalization by producer (int)
# Growth Rate (g)
# Discount rate (r)
# Shock Year (shockyear)

tr <- 100
npm <- 0.04
d <- 0.073
int <- 0.05
g <- 0.03
r <- 0.04
shockyear <- 2028


# If you want to download the output files, please change the output directory below
output_directory <- "C/user/example/Nrisk results/"


## Computation of dataframe

# Create a sequence of years from 2023 to 2050
years <- 2023:2050

# Calculate Revenue for each year
revenue <- tr * (1 + g)^(years - 2023)

# Calculate Discounted Baseline Profits
# Discounting to the year 2023
discounted_baseline_profits <- (revenue * npm) / (1 + r)^(years - 2023)

# Calculate Discounted Shock Profits
# Using the same discounting to the year 2023
discounted_shock_profits <- ifelse(years < shockyear,
                                   discounted_baseline_profits,
                                   (revenue * (npm - d * int)) / (1 + r)^(years - 2023))

# Create the dataframe named valuation_wtp
valuation_wtp <- data.frame(
  Year = years,
  Revenue = revenue,
  Discounted_Baseline_Profit = discounted_baseline_profits,
  Discounted_Shock_Profit = discounted_shock_profits
)

# Print the dataframe to see the first few rows
print(head(valuation_wtp))


## Outputs

# Calculate NPV - Baseline
npv_baseline <- sum(valuation_wtp$Discounted_Baseline_Profit)

# Calculate NPV - Shock (applied on Revenues)
npv_shock <- sum(valuation_wtp$Discounted_Shock_Profit)

# Calculate NPV - Shock (in %)
npv_shock_percent <- (npv_shock / npv_baseline) - 1

# Create the Output dataframe
output_dataframe_wtp <- data.frame(
  NRisk_Model = rep("WTP", 3),
  Variable = c("NPV - Baseline",
               "NPV - Shock (applied on Revenues)",
               "NPV - Shock (in %)"),
  Output = c(npv_baseline,
             npv_shock,
             npv_shock_percent)
)

# Print the dataframe to see the results
print(output_dataframe_wtp)


## Export

# Paths for the output files using the predefined output_directory variable
output_file_path <- file.path(output_directory, "1in1000_Nrisk_WTP_Outputs.csv")
valuation_file_path <- file.path(output_directory, "1in1000_Nrisk_WTP_Valuation.csv")

# Save the dataframes as CSV files
write.csv(output_dataframe_wtp, output_file_path, row.names = FALSE)
write.csv(valuation_wtp, valuation_file_path, row.names = FALSE)
