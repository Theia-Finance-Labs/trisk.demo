library(dplyr)
library(ggplot2)
library(stress.test.plot.report)

# Directory where plots will be saved
plots_dir <- "vignettes/paper_lineplots_absval"


granularity <- c("ald_sector", "ald_business_unit")

data_plot <- readr::read_csv("./vignettes/trajectories_paper_agg.csv") %>%
  rename(
    ald_business_unit=technology
  ) %>%
  main_data_load_trajectories_data_from_file(
    crispy_outputs_dir = crispy_outputs_dir,
    granularity = granularity ,
    param_cols = c("scenario_duo_bckp","year")
  )


# Ensure the directory exists
if (!dir.exists(plots_dir)) {
  dir.create(plots_dir, recursive = TRUE)
}

# Loop through each unique scenario duo
for (scenario_duo in unique(data_plot$scenario_duo_bckp)) {
  data_filtered <- data_plot %>%
    filter(scenario_duo_bckp == scenario_duo)

  # Assuming `pipeline_crispy_trisk_line_plot` returns a ggplot object
  trisk_line_plot <- pipeline_crispy_trisk_line_plot(
    trajectories_data = data_filtered,
    facet_var = granularity[-1],
    linecolor = granularity[-1],
    y_in_percent=FALSE
  ) + ggtitle(scenario_duo)

  # Construct the filename for the plot
  plot_filename <- paste0(scenario_duo, ".png") # or .pdf, .svg, etc., as per your requirement
  full_path <- file.path(plots_dir, plot_filename)

  # Save the plot
  # Adjust width, height, and dpi as needed
  ggsave(full_path, trisk_line_plot, width = 6, height = 10, dpi = 300)
}


