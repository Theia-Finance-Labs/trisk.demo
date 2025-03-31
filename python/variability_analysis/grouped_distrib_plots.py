import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from scipy import stats


# Function to load and return the dataset
def load_data(source):
    """
    Loads the NPV, PD, and parameters datasets from the specified source directory.

    Parameters:
    source (str): The directory containing the CSV files.

    Returns:
    tuple: A tuple containing the NPV dataframe, PD dataframe, and parameters dataframe.
    """
    try:
        npv_df = pd.read_csv(os.path.join(source, "npvs.csv"))
        # Calculate net_present_value_rate_of_change
        npv_df["net_present_value_change"] = (
            npv_df["net_present_value_shock"] - npv_df["net_present_value_baseline"]
        ) / npv_df["net_present_value_baseline"]

        pd_df = pd.read_csv(os.path.join(source, "pds.csv"))
        pd_df["asset_id"] = pd_df["company_id"]
        # Calculate pd_difference
        pd_df["pd_difference"] = pd_df["pd_shock"] - pd_df["pd_baseline"]
        pd_df = pd_df.loc[pd_df["term"] == 5, :]

        params_df = pd.read_csv(os.path.join(source, "params.csv"))

        return npv_df, pd_df, params_df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None, None, None


def plot_grouped_distributions(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Trace des distributions groupées pour chaque scénario cible, avec une ligne pour chaque catégorie.
    La couleur de la ligne est déterminée par la catégorie (technologie ou secteur).
    Le type de ligne est déterminée par l'année de choc.
    Utilise une échelle linéaire pour les axes x et y, avec chaque distribution normalisée à un maximum de 1.
    """
    plots_folder = os.path.join(plots_folder, f"{value_type}_grouped_by_scenario")
    os.makedirs(plots_folder, exist_ok=True)

    print(
        f"Création de graphiques de distribution groupés pour {value_type} basés sur les scénarios dans {plots_folder}"
    )

    plt.style.use("default")

    colors = [
        "blue",
        "orange",
        "red",
        "magenta",
        "gray",
        "cyan",
        "#8B4513",
        "#006400",
        "#4B0082",
        "#FF1493",
        "#00CED1",
        "#FF4500",
        "#2F4F4F",
        "#9ACD32",
        "#FF69B4",
    ]

    # Sort categories and create a color dictionary
    categories = sorted(data_df[category_column].unique())
    color_dict = dict(zip(categories, colors[: len(categories)]))

    line_styles = ["-", "--", ":", "-."]

    target_scenarios = params_df["target_scenario"].unique()
    shock_years = params_df["shock_year"].unique()

    for target_scenario in target_scenarios:
        plt.figure(figsize=(12, 8), dpi=250)
        ax = plt.gca()

        scenario_data = data_df[
            data_df["run_id"].isin(
                params_df[params_df["target_scenario"] == target_scenario]["run_id"]
            )
        ]
        print(
            f"\nTraitement du scénario cible: {target_scenario} ({len(scenario_data)} lignes)"
        )

        for category in categories:
            for jdx, shock_year in enumerate(shock_years):
                cat_data = scenario_data[
                    (scenario_data[category_column] == category)
                    & (
                        scenario_data["run_id"].isin(
                            params_df[
                                (params_df["target_scenario"] == target_scenario)
                                & (params_df["shock_year"] == shock_year)
                            ]["run_id"]
                        )
                    )
                ]

                if not cat_data.empty:
                    label = f"{category} ({shock_year})"
                    color = color_dict[category]
                    linestyle = line_styles[jdx % len(line_styles)]

                    try:
                        data = cat_data[value_type].dropna().values
                        if len(data) > 1:
                            kde = stats.gaussian_kde(data)
                            x_range = np.linspace(data.min(), data.max(), 500)
                            density = kde(x_range)
                            # Normalize the density to have a maximum of 1
                            normalized_density = density / np.max(density)
                            ax.plot(
                                x_range,
                                normalized_density,
                                label=label,
                                color=color,
                                linestyle=linestyle,
                            )
                        else:
                            ax.axvline(
                                data[0], color=color, linestyle=linestyle, label=label
                            )
                        print(f"  Courbe de densité tracée pour {label}")
                    except Exception as e:
                        print(
                            f"  Erreur lors du tracé de la densité pour {label}: {str(e)}"
                        )
                        ax.axvline(
                            cat_data[value_type].mean(),
                            color=color,
                            linestyle=linestyle,
                            label=label,
                        )
                        print(
                            f"  Ligne verticale tracée pour {label} à la valeur moyenne"
                        )

        # Set y-axis limits from 0 to 1.1 for a bit of headroom
        ax.set_ylim(0, 1.1)

        title = f"Distribution de {value_type} - Scénario {target_scenario}"
        plt.title(title, fontsize=18)
        plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
        plt.ylabel("Densité normalisée", fontsize=14)
        plt.legend(
            fontsize=10,
            title=f"{category_column.capitalize()} (Année de choc)",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )

        # Format x-axis labels as percentages
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))

        plt.tight_layout()

        imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}.png")
        plt.savefig(imgpath, bbox_inches="tight")
        plt.close()
        print(f"  Graphique sauvegardé dans {imgpath}")


# Vous devrez ajouter cette fonction à votre flux de travail principal, par exemple :
if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions_grouped")

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    # Ajoutez cet appel après avoir chargé vos données
    plot_grouped_distributions(
        npv_df, params_df, PLOTS_FOLDER, "net_present_value_change", "technology"
    )
    plot_grouped_distributions(
        pd_df, params_df, PLOTS_FOLDER, "pd_difference", "sector"
    )
