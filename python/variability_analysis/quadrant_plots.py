import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from .utils import load_data, filter_data


# Function to filter and merge data
def filter_and_merge_data(npv_df, pd_df, params_df, filter_criteria1, filter_criteria2):
    # Filter both datasets
    filtered_npv_x = filter_data(npv_df, params_df, filter_criteria1)
    filtered_npv_y = filter_data(npv_df, params_df, filter_criteria2)

    filtered_pd_x = filter_data(pd_df, params_df, filter_criteria1)
    filtered_pd_y = filter_data(pd_df, params_df, filter_criteria2)

    # Merge on common keys (company_id and asset_id)
    merged_npv_df = pd.merge(
        filtered_npv_x[
            [
                "company_id",
                "asset_id",
                "net_present_value_baseline",
                "net_present_value_shock",
                "net_present_value_change",
            ]
        ],
        filtered_npv_y[
            [
                "company_id",
                "asset_id",
                "net_present_value_baseline",
                "net_present_value_shock",
                "net_present_value_change",
            ]
        ],
        on=["company_id", "asset_id"],
        suffixes=("_x", "_y"),
    )

    merged_pd_df = pd.merge(
        filtered_pd_x[
            ["company_id", "asset_id", "pd_baseline", "pd_shock", "pd_difference"]
        ],
        filtered_pd_y[
            ["company_id", "asset_id", "pd_baseline", "pd_shock", "pd_difference"]
        ],
        on=["company_id", "asset_id"],
        suffixes=("_x", "_y"),
    )

    return merged_npv_df, merged_pd_df


# Function to create a plot with quadrants
def create_quadrant_plot(data, xlab_scenario, ylab_scenario, value_column, plot_title):

    # Calculate the min and max values for x and y axes
    x_min = min(data[value_column + "_x"].min(), -1)
    x_max = max(data[value_column + "_x"].max(), 1)
    y_min = min(data[value_column + "_y"].min(), -1)
    y_max = max(data[value_column + "_y"].max(), 1)

    plt.figure(figsize=(10, 10), dpi=250)
    plt.xlabel(xlab_scenario, fontsize=24)
    plt.ylabel(ylab_scenario, fontsize=24)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.hlines(y=0, xmin=x_min, xmax=x_max, linewidth=1, color="grey")
    plt.vlines(x=0, ymin=y_min, ymax=y_max, linewidth=1, color="grey")

    quadrants = [
        ([x_min, y_min], [x_min, 0], [0, 0], [0, y_min], "lightcoral"),
        ([x_min, 0], [x_min, y_max], [0, y_max], [0, 0], "lightgreen"),
        ([0, 0], [0, y_max], [x_max, y_max], [x_max, 0], "lightblue"),
        ([0, y_min], [0, 0], [x_max, 0], [x_max, y_min], "lightyellow"),
    ]

    ax = plt.gca()
    for coords in quadrants:
        polygon = Polygon(coords[:4], facecolor=coords[4], alpha=0.3)
        ax.add_patch(polygon)

    plt.scatter(data[value_column + "_x"], data[value_column + "_y"], s=12, c="grey")
    plt.title(plot_title, fontsize=24)
    plt.plot(
        [min(x_min, y_min), max(x_max, y_max)],
        [min(x_min, y_min), max(x_max, y_max)],
        linestyle="dashed",
        color="black",
        linewidth=2.5,
    )
    plt.tight_layout()
    return plt.gcf(), plt.gca()


# Main function to run the script
def plot_bivariate_scenarios_quadrants(
    npv_df, pd_df, params_df, params1, params2, save_folder_path
):
    filter_criteria1, filter_criteria2 = params1, params2
    # Filter and merge data
    merged_npv_df, merged_pd_df = filter_and_merge_data(
        npv_df, pd_df, params_df, filter_criteria1, filter_criteria2
    )

    # Create and save quadrant plot for PD
    fig, ax = create_quadrant_plot(
        merged_pd_df,
        params1["target_scenario"],
        params2["target_scenario"],
        "pd_difference",
        f"Company PD Difference ({params1['shock_year']} vs {params2['shock_year']})",
    )
    fig.savefig(
        os.path.join(
            save_folder_path,
            f"pd_{params1['target_scenario']}___{params2['target_scenario']}_{params1['shock_year']}_vs_{params2['shock_year']}.jpg",
        )
    )
    plt.close(fig)

    # Create and save quadrant plot for NPV
    fig, ax = create_quadrant_plot(
        merged_npv_df,
        params1["target_scenario"],
        params2["target_scenario"],
        "net_present_value_change",
        f"Company NPV Difference ({params1['shock_year']} vs {params2['shock_year']})",
    )
    fig.savefig(
        os.path.join(
            save_folder_path,
            f"npv_{params1['target_scenario']}___{params2['target_scenario']}_{params1['shock_year']}_vs_{params2['shock_year']}.jpg",
        )
    )
    plt.close(fig)


if __name__ == "__main__":
    from .utils import load_data, filter_data

    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    save_folder_path = os.path.join(DATA_SOURCE_FOLDER, "plots_quadrants")

    # Create output folder if it doesn't exist
    os.makedirs(save_folder_path, exist_ok=True)

    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    # Define your run parameters
    run_params = [
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_B2DS",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2025,
            "scenario_geography": "Global",
        },
        {
            "baseline_scenario": "NGFS2023GCAM_CP",
            "target_scenario": "NGFS2023GCAM_NZ2050",
            "shock_year": 2030,
            "scenario_geography": "Global",
        },
    ]

    # Loop over each pair of parameters and run the main function, skipping pairs with the same indices
    for i, params1 in enumerate(run_params):
        for j, params2 in enumerate(run_params):
            if i >= j:
                continue  # Skip if indices are the same or if params1 has already been compared with params2
            plot_bivariate_scenarios_quadrants(
                npv_df=npv_df,
                pd_df=pd_df,
                params_df=params_df,
                params1=params1,
                params2=params2,
                save_folder_path=save_folder_path,
            )
