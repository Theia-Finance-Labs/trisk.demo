import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Constants
DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
OUTPUT_FOLDER = "./square_quadrants"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Function to load and return the dataset
def load_data(source):
    npv_df = pd.read_csv(os.path.join(source, "npvs.csv"))
    pd_df = pd.read_csv(os.path.join(source, "pds.csv"))
    params_df = pd.read_csv(os.path.join(source, "params.csv"))
    return npv_df, pd_df, params_df


# Function to filter data based on target scenario and shock year
def filter_data(
    npv_df, pd_df, params_df, target_scenario_x, target_scenario_y, shock_year
):
    # Filter params_df based on target_scenario and shock_year
    filtered_params_df = params_df[
        (params_df["target_scenario"].isin([target_scenario_x, target_scenario_y]))
        & (params_df["shock_year"] == shock_year)
    ]

    # Merge the filtered params_df with npv_df and pd_df to get the relevant data
    filtered_npv_df = npv_df.merge(
        filtered_params_df[["run_id", "target_scenario"]], on="run_id", how="inner"
    )
    filtered_pd_df = pd_df.merge(
        filtered_params_df[["run_id", "target_scenario"]], on="run_id", how="inner"
    )

    # Calculate net_present_value_rate_of_change
    filtered_npv_df["net_present_value_rate_of_change"] = (
        filtered_npv_df["net_present_value_shock"]
        - filtered_npv_df["net_present_value_baseline"]
    ) / filtered_npv_df["net_present_value_baseline"]

    return filtered_npv_df, filtered_pd_df


# Function to create a plot with quadrants
def create_quadrant_plot(
    data, xlab_scenario, ylab_scenario, value_column, y_value_column, plot_title
):
    plt.figure(figsize=(10, 10), dpi=250)
    plt.xlabel(xlab_scenario, fontsize=24)
    plt.ylabel(ylab_scenario, fontsize=24)
    plt.xlim(-1, 1)
    plt.ylim(-1, 4)
    plt.hlines(y=0, xmin=-90, xmax=90, linewidth=1, color="grey")
    plt.vlines(x=0, ymin=-90, ymax=180, linewidth=1, color="grey")

    quadrants = [
        ([-1, -1], [-1, 0], [0, 0], [0, -1], "lightcoral"),
        ([-1, 0], [-1, 4], [0, 4], [0, 0], "lightgreen"),
        ([0, 0], [0, 4], [1, 4], [1, 0], "lightblue"),
        ([0, -1], [0, 0], [1, 0], [1, -1], "lightyellow"),
    ]

    ax = plt.gca()
    for coords in quadrants:
        polygon = Polygon(coords[:4], facecolor=coords[4], alpha=0.3)
        ax.add_patch(polygon)

    plt.scatter(data[value_column], data[y_value_column], s=8, c="grey")
    plt.title(plot_title, fontsize=24)
    plt.plot([-1, 1], [-1, 1], linestyle="dashed", color="black", linewidth=2.5)
    plt.tight_layout()
    return plt.gcf(), plt.gca()


# Function to plot density distribution
def plot_density_distribution(
    data, selected_sectors, scenarios, x_limits, xtick_range, title
):
    mpl.rcParams["font.family"] = "Times New Roman"
    plt.style.use("default")
    plt.figure(figsize=(8, 8), dpi=250)
    plt.xlim(*x_limits)
    plt.xticks(
        np.arange(*xtick_range), ["{:,.0%}".format(x) for x in np.arange(*xtick_range)]
    )

    for scenario, color, label in scenarios:
        data[
            (data["target_scenario"] == scenario)
            & (data["sector"].isin(selected_sectors))
        ]["net_present_value_rate_of_change"].plot(
            kind="density", label=label, color=color
        )

    plt.title(title, fontsize=20)
    plt.xlabel("Valuation change", fontsize=16)
    plt.ylabel("Density", fontsize=16)
    plt.legend(fontsize=14)

    ax = plt.gca()
    vals = ax.get_xticks()
    ax.set_xticklabels(["{:,.0%}".format(x) for x in vals])

    plt.show()


# Main function to run the script
def main():
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    # Define your target scenarios and shock year
    target_scenario_x = "Scenario_X_Name"
    target_scenario_y = "Scenario_Y_Name"
    shock_year = 2030  # Example shock year

    # Filter data
    filtered_npv_df, filtered_pd_df = filter_data(
        npv_df, pd_df, params_df, target_scenario_x, target_scenario_y, shock_year
    )

    # Create and save quadrant plots for PD and NPV
    fig, ax = create_quadrant_plot(
        filtered_pd_df,
        target_scenario_x,
        target_scenario_y,
        "pd_baseline",
        "pd_shock",
        "Company PD Difference",
    )
    fig.savefig(
        os.path.join(OUTPUT_FOLDER, f"pd_{target_scenario_x}___{target_scenario_y}.jpg")
    )
    plt.close(fig)

    fig, ax = create_quadrant_plot(
        filtered_npv_df,
        target_scenario_x,
        target_scenario_y,
        "net_present_value_baseline",
        "net_present_value_shock",
        "Company Value Change (%)",
    )
    fig.savefig(
        os.path.join(
            OUTPUT_FOLDER, f"npv_{target_scenario_x}___{target_scenario_y}.jpg"
        )
    )
    plt.close(fig)

    # Define sectors and scenarios for density plots
    selected_sectors = ["Power"]

    scenarios_1 = [
        ("Scenario_X_Name", "blue", "Scenario X"),
        ("NGFS2021_MESSAGE_B2DS", "orange", "MESSAGE B2DS"),
        ("NGFS2021_GCAM_B2DS", "red", "GCAM B2DS"),
        ("NGFS2021_REMIND_B2DS", "magenta", "REMIND B2DS"),
        ("WEO2021_SDS", "gray", "WEO SDS"),
        ("Oxford2021_fast", "cyan", "Oxford"),
    ]
    plot_density_distribution(
        filtered_npv_df,
        selected_sectors,
        scenarios_1,
        x_limits=(-1.5, 2),
        xtick_range=(-1, 2.25, 0.5),
        title="Distribution of Valuation Change",
    )

    scenarios_2 = [
        ("NGFS2021_GCAM_NZ2050", "red", "GCAM NZE"),
        ("IPR2021_RPS", "blue", "IPR RPS"),
        ("NGFS2021_REMIND_NZ2050", "magenta", "REMIND NZE"),
        ("NGFS2021_MESSAGE_NZ2050", "orange", "MESSAGE NZE"),
        ("WEO2021_NZE_2050", "gray", "WEO NZE"),
    ]
    plot_density_distribution(
        filtered_npv_df,
        selected_sectors,
        scenarios_2,
        x_limits=(-1.5, 4),
        xtick_range=(-1, 4.25, 0.5),
        title="Distribution of Valuation Change",
    )


if __name__ == "__main__":
    main()
