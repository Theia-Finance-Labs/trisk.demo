#################################################
####### Nature Risk Model Software ##############
#################################################
####### Land use Model
####### Effect of Ecosystem Cost on Profits per Hectare

#'The model forms part of the LIFE STRESS project.
#'The LIFE STRESS project has received funding from the LIFE Programme of the
#' European Union.‘ The contents of this publication are the sole  responsibility
#' of Theia Finance Labs and  do  not necessarily reflect  the  opinion
#' of the European Union. Project: Project: 101074271 — LIFE21-GIC-DE-Stress.


## Inputs
## Please adjust below the Inputs of the Land Model

# Revenue per Hectare (rph)
# Net Profit Margin (npm)
# Ecosystem Cost (ecocost)
# Ecosystem Cost Internalization Factor (int)
# growth rate (g)
# discount rate (r)
# Shock Year (shockyear)
# Profit Adjustment (profadj)
rph <- 130
npm <- 0.44
ecocost <- 88
int <- 0.5
g <- 0.04
r <- 0.00
shockyear <- 2025
profadj <- 0.8

# If you want to download the output files, please change the output directory below
output_directory <- "C/user/example/Nrisk results/"


## Computation of dataframe

# Create a sequence of years from 2022 to 2050
years <- 2022:2050

# Calculate Revenue for each year
# Revenue in the first year is `rph` and grows by `g` each year
revenue <- rph * (1 + g)^(years - 2022)

# Calculate Discounted Baseline Profits
# Revenue * npm, discounted to the year 2023
discounted_baseline_profits <- revenue * npm / (1 + r)^(years - 2023)

# Calculate Discounted Shock Profit
discounted_shock_profits <- ifelse(years < shockyear,
                                   discounted_baseline_profits,
                                   ((revenue - ecocost * int) * npm * profadj) / (1 + r)^(years - 2023))

# Create the dataframe
Valuation_per_Hectare <- data.frame(Year = years,
                                    Revenue = revenue,
                                    Discounted_Baseline_Profits = discounted_baseline_profits,
                                    Discounted_Shock_Profits = discounted_shock_profits)

# Print the dataframe to see the first few rows
print(head(Valuation_per_Hectare))


## Output Results

# Calculations for output values
profit_baseline <- rph * npm
profit_shock <- (rph - ecocost * int) * npm
profit_shock_percent <- round((profit_shock / profit_baseline) - 1, 4)

# Sum of discounted profits for NPV calculations
npv_baseline <- sum(discounted_baseline_profits)
npv_shock <- sum(discounted_shock_profits)
npv_shock_percent <- round((npv_shock / npv_baseline) - 1, 4)

# Create the Output dataframe
output_dataframe_land <- data.frame(
  NRisk_Model = rep("Land", 6),
  Variable = c("Profit per Hectare - Baseline (€)",
               "Profit per Hectare - Shock (€)",
               "Profit per Hectare - Shock (in%)",
               "NPV per Hectare - Baseline (€)",
               "NPV per Hectare - Shock (applied on Revenues) (€)",
               "NPV per Hectare - Shock (in %)"),
  Output = c(profit_baseline,
             profit_shock,
             profit_shock_percent,
             npv_baseline,
             npv_shock,
             npv_shock_percent)
)

# Print the dataframe to see the results
print(output_dataframe_land)

## Export

# Paths for the output files using the predefined output_directory variable
output_file_path <- file.path(output_directory, "1in1000_Nrisk_Land_Outputs.csv")
valuation_file_path <- file.path(output_directory, "1in1000_Nrisk_Land_ValuationperHectare.csv")

# Save the dataframes as CSV files
write.csv(output_dataframe_land, output_file_path, row.names = FALSE)
write.csv(Valuation_per_Hectare, valuation_file_path, row.names = FALSE)

