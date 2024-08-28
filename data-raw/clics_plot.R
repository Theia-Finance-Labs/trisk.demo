# Run data-raw/clics_generate_data.R first

library(ggplot2)
library(dplyr)

create_asset_ranking_plot <- function(
  npvs_with_params,
  x_column = "plant_age_years",
  y_column = "net_present_value_shock",
  baseline_column = "net_present_value_baseline",
  threshold_percentage = 0.5,
  title = "Classement des actifs par pourcentage de changement de VAN",
  x_label = "Années cumulées",
  y_label = "Changement de VAN (%)"
) {
  # Calculer le pourcentage de changement
  plot_data <- npvs_with_params %>%
    mutate(npv_change_percent = (!!sym(y_column) - !!sym(baseline_column)) / !!sym(baseline_column) * 100)

  # Trier les données et calculer la position cumulative sur l'axe x
  plot_data <- plot_data %>%
    arrange(desc(npv_change_percent)) %>%
    mutate(cumulative_years = cumsum(!!sym(x_column)))

  # Définir le seuil pour commencer la numérotation
  total_years <- sum(plot_data[[x_column]])
  threshold_years <- total_years * threshold_percentage

  # Ajouter le rang
  plot_data <- plot_data %>%
    mutate(rank = ifelse(cumulative_years > threshold_years, 
                         row_number() - sum(cumulative_years <= threshold_years), 
                         0))%>%
  select(asset_id, cumulative_years, !!sym(x_column), npv_change_percent, rank)

  # Créer le graphique
  plot <- ggplot(plot_data, aes(x = cumulative_years - !!sym(x_column)/2, y = npv_change_percent, width = !!sym(x_column))) +
    geom_bar(stat = "identity", fill = "skyblue", color = "navy", size = 0.5) +
    geom_text(aes(label = ifelse(rank > 0, rank, "")), vjust = -0.5) +
    geom_vline(xintercept = threshold_years, linetype = "dotted", color = "red", size = 1) +
    scale_x_continuous(breaks = seq(0, total_years, by = total_years/10)) +
    labs(title = title, x = x_label, y = y_label) +
    theme_minimal() +
    theme(
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),
      panel.grid = element_blank(),
      axis.line = element_line(color = "black")
    )

  # Retourner le graphique et les données
  return(list(plot = plot, data = plot_data))
}

# Utilisation de la fonction
npvs_with_params <- readr::read_csv(file.path(local_clics_outputs_folder, "npvs_with_params.csv"))

result <- create_asset_ranking_plot(
  npvs_with_params,
  x_column = "plant_age_years",
  y_column = "net_present_value_shock",
  baseline_column = "net_present_value_baseline"
)

# Sauvegarder le graphique
ggsave(file.path("workspace", "asset_ranking_plot_npv_percent.png"), result$plot, width = 12, height = 6, bg = "white")

print(result$data)