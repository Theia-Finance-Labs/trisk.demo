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
