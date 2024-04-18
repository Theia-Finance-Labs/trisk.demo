#################################################
####### Nature Risk Model Software ##############
#################################################
####### Planetary Boundaries Model
####### Effect of Ecosystem Cost on Fishing Profitability

#'The model forms part of the LIFE STRESS project.
#'The LIFE STRESS project has received funding from the LIFE Programme of the
#' European Union.‘ The contents of this publication are the sole  responsibility
#' of Theia Finance Labs and  do  not necessarily reflect  the  opinion
#' of the European Union. Project: Project: 101074271 — LIFE21-GIC-DE-Stress.


## Inputs
## Please adjust below the Inputs of the Planetary Boundaries Model

# Baseline Fishing Revenue (bfr)
# Net Profit Margin (npm)
# Baseline Growth Rate (g)
# Alternative Growth Rate ()
# discount rate (r)
# Shock Year (shockyear)

bfr <- 100
npm <- 0.04
g <- 0.04
ag <- -0.01
r <- 0.00
shockyear <- 2025


# If you want to download the output files, please change the output directory below
output_directory <- "C/user/example/Nrisk results/"


## Computation of dataframe
# Create a sequence of years from 2022 to 2050
years <- 2022:2050

# Calculate Revenue for each year
revenue <- bfr * (1 + g)^(years - 2022)

# Calculate Alternative Revenue Pathway
alternative_revenue <- rep(0, length(years))
alternative_revenue[1] <- revenue[1]  # First year is the same as baseline revenue
for (i in 2:length(years)) {
  if (years[i] < shockyear) {
    alternative_revenue[i] <- revenue[i]
  } else {
    alternative_revenue[i] <- alternative_revenue[i - 1] * (1 + ag)
  }
}

# Calculate Discounted Baseline Profit
discounted_baseline_profit <- revenue * npm / (1 + r)^(years - 2023)

# Calculate Discounted Shock Profit using Alternative Revenue Pathway
discounted_shock_profit <- alternative_revenue * npm / (1 + r)^(years - 2023)

# Create the dataframe
valuation_fishing <- data.frame(
  Year = years,
  Revenue = revenue,
  Alternative_Revenue_Pathway = alternative_revenue,
  Discounted_Baseline_Profit = discounted_baseline_profit,
  Discounted_Shock_Profit = discounted_shock_profit
)

# Print the dataframe to see the first few rows
print(head(valuation_fishing))


## Outputs

# Access the last (2050) value for Revenue and Alternative Revenue Pathway
production_2050_baseline <- valuation_fishing$Revenue[valuation_fishing$Year == 2050]
production_2050_alternative <- valuation_fishing$Alternative_Revenue_Pathway[valuation_fishing$Year == 2050]

# Calculate Production in 2050 relative to Baseline
production_relative_to_baseline <- round(production_2050_alternative / production_2050_baseline,4)

# Calculate NPV - Baseline
npv_baseline <- sum(valuation_fishing$Discounted_Baseline_Profit)

# Calculate NPV - Shock (applied on Revenues)
npv_shock <- sum(valuation_fishing$Discounted_Shock_Profit)

# Calculate NPV - Shock (in %)
npv_shock_percent <- round((npv_shock / npv_baseline) - 1,4)

# Create the Output dataframe
output_fishing <- data.frame(
  NRisk_Model = rep("Planet. Boundaries", 4),
  Variable = c("Production in 2050 relative to Baseline",
               "NPV - Baseline",
               "NPV - Shock (applied on Revenues)",
               "NPV - Shock (in %)"),
  Output = c(production_relative_to_baseline,
             npv_baseline,
             npv_shock,
             npv_shock_percent)
)

# Print the dataframe to see the results
print(output_fishing)

## Export

# Paths for the output files using the predefined output_directory variable
output_file_path <- file.path(output_directory, "1in1000_Nrisk_PlanetBoundaries_Outputs.csv")
valuation_file_path <- file.path(output_directory, "1in1000_Nrisk_PlanetBoundaries_Valuation_Fishing.csv")

# Save the dataframes as CSV files
write.csv(output_fishing, output_file_path, row.names = FALSE)
write.csv(valuation_fishing, valuation_file_path, row.names = FALSE)
