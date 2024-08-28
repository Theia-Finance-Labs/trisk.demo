import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import pandas as pd


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


# Function to filter data based on multiple criteria
def filter_data(df, params_df, filter_criteria):
    """
    Filters the dataframe based on the criteria provided in filter_criteria.

    Parameters:
    df (pd.DataFrame): The main dataframe to filter.
    params_df (pd.DataFrame): The parameters dataframe that contains filtering columns.
    filter_criteria (dict): A dictionary where keys are column names in params_df and values are the criteria for filtering.

    Returns:
    pd.DataFrame: The filtered dataframe.
    """
    # Start with the full params_df
    filtered_params_df = params_df.copy()

    # Apply each filtering criterion
    for key, value in filter_criteria.items():
        filtered_params_df = filtered_params_df[filtered_params_df[key] == value]

    # Merge the filtered params_df with the main dataframe
    filtered_df = df.merge(filtered_params_df[["run_id"]], on="run_id", how="inner")

    return filtered_df


# Function to determine common x and y axis limits for all plots
def determine_common_limits(data, column, filter_dict=None):
    """
    Détermine les limites communes pour l'axe x basées sur les données fournies.

    Args:
    data (pd.DataFrame): Le DataFrame contenant les données à analyser.
    column (str): Le nom de la colonne à utiliser pour déterminer les limites.
    filter_dict (dict, optional): Un dictionnaire de filtres à appliquer aux données.

    Returns:
    tuple: Les limites x (x_min, x_max).
    """
    if filter_dict:
        for key, value in filter_dict.items():
            data = data[data[key] == value]

    all_values = data[column].dropna()

    if len(all_values) > 0:
        x_min = all_values.min()
        x_max = all_values.max()
        margin = (x_max - x_min) * 0.1  # 10% de marge
        return (x_min - margin, x_max + margin)
    else:
        print(f"Attention : Aucune donnée valide trouvée pour la colonne {column}")
        return (-1, 1)  # Limites par défaut si aucune donnée n'est trouvée


# Function to plot density distribution for multiple scenarios
def plot_density_distribution(
    data, params_df, title, plots_folder, mode="by_run", specific_run_id=None
):
    print("Données initiales :")
    print(data.head())
    print(f"Nombre total de lignes : {len(data)}")
    print(f"Colonnes : {data.columns}")
    print(f"Mode : {mode}")
    print(f"Specific run ID : {specific_run_id}")
    print("Paramètres :")
    print(params_df)

    mpl.rcParams["font.family"] = "Times New Roman"
    plt.style.use("default")
    plt.figure(figsize=(10, 6), dpi=250)

    colors = plt.colormaps["tab10"]
    max_density_value = 0

    if mode == "by_run":
        xlim = determine_common_limits(data, "net_present_value_change")
        for run_id, run_params in params_df.iterrows():
            filtered_data = data[data["run_id"] == run_params["run_id"]]
            print(
                f"Données filtrées pour run_id {run_params['run_id']} : {len(filtered_data)} lignes"
            )

            if not filtered_data.empty:
                print(f"Traçage pour run_id {run_params['run_id']}")
                label = f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"
                density = filtered_data["net_present_value_change"].plot.density(
                    label=label, color=colors(run_id % 10), ax=plt.gca()
                )
                max_density_value = max(max_density_value, plt.gca().get_ylim()[1])
            else:
                print(f"Pas de données pour run_id {run_params['run_id']}")

    elif mode == "by_technology":
        if specific_run_id is None:
            raise ValueError(
                "specific_run_id doit être fourni lorsque le mode est 'by_technology'"
            )

        filtered_data = data[data["run_id"] == specific_run_id]

        print(
            f"Données filtrées pour run_id {specific_run_id} : {len(filtered_data)} lignes"
        )
        print(f"Technologies uniques : {filtered_data['technology'].unique()}")

        xlim = determine_common_limits(filtered_data, "net_present_value_change")

        for tech_id, technology in enumerate(filtered_data["technology"].unique()):
            tech_data = filtered_data[filtered_data["technology"] == technology]
            print(f"Données pour la technologie {technology} : {len(tech_data)} lignes")
            if not tech_data.empty:
                values = tech_data["net_present_value_change"].values
                print(
                    f"Statistiques pour {technology}: min={values.min()}, max={values.max()}, mean={values.mean()}, std={values.std()}"
                )

                if values.std() > 0:
                    density = tech_data["net_present_value_change"].plot.density(
                        label=technology, color=colors(tech_id), ax=plt.gca()
                    )
                    max_density_value = max(max_density_value, plt.gca().get_ylim()[1])
                else:
                    plt.axvline(values.mean(), color=colors(tech_id), label=technology)
                    max_density_value = 1  # Valeur arbitraire pour l'axe y
            else:
                print(f"Pas de données pour la technologie {technology}")

        run_params = params_df.loc[params_df["run_id"] == specific_run_id].iloc[0]
        title = f"{title} - {run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

    if max_density_value == 0:
        print("Aucune donnée n'a été tracée. Vérifiez vos données et vos filtres.")
        plt.close()
        return

    plt.xlim(xlim)
    plt.ylim(0, max_density_value * 1.1)  # Ajout d'une marge de 10% en haut

    plt.title(title, fontsize=18)
    plt.xlabel("Changement de valorisation", fontsize=14)
    plt.ylabel("Densité", fontsize=14)
    plt.legend(fontsize=10)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))

    plt.tight_layout()

    mode_suffix = "by_run" if mode == "by_run" else f"by_technology_{specific_run_id}"
    imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}_{mode_suffix}.png")

    plt.savefig(imgpath)
    plt.close()
    print(f"Graphique sauvegardé dans {imgpath}")


# Main execution function
def plot_density_distributions(
    npv_df,
    params_df,
    title,
    plots_folder,
):
    plots_folder_by_run = os.path.join(plots_folder, "by_run")
    plots_folder_by_technology = os.path.join(plots_folder, "by_technology")
    os.makedirs(plots_folder_by_run, exist_ok=True)
    os.makedirs(plots_folder_by_technology, exist_ok=True)

    # Tracer le plot global (mode "by_run")
    plot_density_distribution(
        npv_df,
        params_df,
        title=title,
        plots_folder=plots_folder_by_run,
        mode="by_run",
    )

    # Tracer un plot par technologie (toujours en mode "by_run")
    technologies = npv_df["technology"].unique()
    for tech in technologies:
        tech_data = npv_df[npv_df["technology"] == tech]
        plot_density_distribution(
            tech_data,
            params_df,
            title=f"{title} - {tech}",
            plots_folder=plots_folder_by_run,
            mode="by_run",
        )

    # Tracer par technologie pour chaque run (mode "by_technology")
    for run_id in params_df["run_id"]:
        plot_density_distribution(
            npv_df,
            params_df,
            title=title,
            plots_folder=plots_folder_by_technology,
            mode="by_technology",
            specific_run_id=run_id,
        )


if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Le chargement des données a échoué. Arrêt du programme.")
    else:
        # Run the analysis and plot density distribution
        plot_density_distributions(
            npv_df,
            params_df,
            title="Distribution du changement de valorisation à travers les scénarios",
            plots_folder=PLOTS_FOLDER,
        )
