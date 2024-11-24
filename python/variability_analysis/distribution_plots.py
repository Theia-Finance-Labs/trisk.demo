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


def determine_common_limits(data, column):
    """
    Determines common limits for the x-axis based on the provided data.

    Args:
    data (pd.DataFrame): The DataFrame containing the data to analyze.
    column (str): The name of the column to use for determining the limits.

    Returns:
    tuple: The x limits (x_min, x_max).
    """
    all_values = data[column].dropna()

    if len(all_values) > 0:
        x_min = all_values.min()
        x_max = all_values.max()
        margin = (x_max - x_min) * 0.1  # 10% margin
        return (x_min - margin, x_max + margin)
    else:
        print(f"Warning: No valid data found for column {column}")
        return (-1, 1)  # Default limits if no data is found


def plot_density(data, column, ax, label, color):
    """
    Plots a density curve on the given axis.

    Args:
    data (pd.DataFrame): The data to plot.
    column (str): The name of the column to use for density.
    ax (matplotlib.axes.Axes): The axis on which to plot.
    label (str): The label for the legend.
    color (str): The color of the curve.

    Returns:
    float: The maximum density value.
    """
    if data.empty:
        print(f"No data for {label}")
        return 0

    values = data[column].values
    if values.std() > 0:
        density = data[column].plot.density(label=label, color=color, ax=ax)
        return ax.get_ylim()[1]
    else:
        ax.axvline(values.mean(), color=color, label=label)
        return 1  # Arbitrary value for y-axis


def plot_distributions_by_category(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Plots distributions for each category (technology or sector), with a line for each run_id.
    Creates two sets of graphs: one with free x-axis and one with aligned x-axis.
    """
    plots_folder_free = os.path.join(
        plots_folder, f"{value_type}_by_{category_column}_free_x"
    )
    plots_folder_aligned = os.path.join(
        plots_folder, f"{value_type}_by_{category_column}_aligned_x"
    )
    os.makedirs(plots_folder_free, exist_ok=True)
    os.makedirs(plots_folder_aligned, exist_ok=True)

    print(f"Creating distribution graphs by {category_column} for {value_type}")

    categories = data_df[category_column].unique()
    categories = np.append(categories, "All")  # Add "All" for the special case

    # Calculate global limits for the aligned x-axis
    global_min = data_df[value_type].min()
    global_max = data_df[value_type].max()
    global_margin = (global_max - global_min) * 0.1
    global_xlim = (global_min - global_margin, global_max + global_margin)

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

    for cat in categories:
        print(f"\nProcessing {category_column}: {cat}")

        if cat == "All":
            cat_data = data_df
            title = f"Distribution of {value_type} - All {category_column}s"
        else:
            cat_data = data_df[data_df[category_column] == cat]
            title = f"Distribution of {value_type} - {cat}"

        print(f"  Number of rows for this {category_column}: {len(cat_data)}")

        for aligned in [False, True]:
            plt.figure(figsize=(10, 6), dpi=250)
            ax = plt.gca()

            max_density = 0
            min_x, max_x = float("inf"), float("-inf")

            for idx, (run_id, run_params) in enumerate(params_df.iterrows()):
                run_data = cat_data[cat_data["run_id"] == run_params["run_id"]]
                print(f"  Processing run_id: {run_id} ({len(run_data)} rows)")

                if not run_data.empty:
                    values = run_data[value_type].values
                    min_x = min(min_x, values.min())
                    max_x = max(max_x, values.max())

                    label = f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"
                    if len(values) > 1:
                        try:
                            density = run_data[value_type].plot.density(
                                label=label, color=colors[idx % len(colors)], ax=ax
                            )
                            current_max_density = ax.get_ylim()[1]
                            max_density = min(
                                max(max_density, current_max_density), 100
                            )
                            print(f"    Density curve plotted for {label}")
                        except Exception as e:
                            print(f"    Error plotting density for {label}: {str(e)}")
                            ax.axvline(
                                values.mean(),
                                color=colors[idx % len(colors)],
                                label=label,
                            )
                            print(
                                f"    Vertical line plotted for {label} at mean value"
                            )
                    else:
                        ax.axvline(
                            values[0], color=colors[idx % len(colors)], label=label
                        )
                        print(f"    Single vertical line plotted for {label}")

            if min_x == float("inf") or max_x == float("-inf"):
                print(f"  No valid data for {category_column} {cat}")
                plt.close()
                continue

            if aligned:
                plt.xlim(global_xlim)
            else:
                margin = (max_x - min_x) * 0.1
                plt.xlim(min_x - margin, max_x + margin)

            plt.ylim(0, max_density * 1.1)  # Add a 10% margin at the top
            plt.title(title, fontsize=18)
            plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
            plt.ylabel("Density", fontsize=14)
            plt.legend(fontsize=10)
            ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))
            plt.tight_layout()

            folder = plots_folder_aligned if aligned else plots_folder_free
            imgpath = os.path.join(folder, f"{title.replace(' ', '_')}.png")
            plt.savefig(imgpath)
            plt.close()
            print(f"  {'Aligned' if aligned else 'Free'} graph saved in {imgpath}")

        print(f"  X-axis limits: [{min_x:.4f}, {max_x:.4f}]")
        print(f"  Maximum density: {max_density:.4f}")


def plot_distributions_by_run(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Plots distributions for each run_id, with a line for each technology or sector.
    """
    plots_folder = os.path.join(plots_folder, f"{value_type}_by_run_{category_column}")
    os.makedirs(plots_folder, exist_ok=True)

    print(
        f"Creating distribution graphs by run for {value_type} based on {category_column} in {plots_folder}"
    )

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

    for run_id, run_params in params_df.iterrows():
        print(f"\nProcessing run_id: {run_id}")
        plt.figure(figsize=(10, 6), dpi=250)
        ax = plt.gca()

        run_data = data_df[data_df["run_id"] == run_params["run_id"]]
        print(f"  Number of rows for this run: {len(run_data)}")

        title = f"Distribution of {value_type} - {run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

        max_density = 0
        min_x, max_x = float("inf"), float("-inf")

        for idx, category in enumerate(run_data[category_column].unique()):
            cat_data = run_data[run_data[category_column] == category]
            print(f"  Processing {category_column}: {category} ({len(cat_data)} rows)")

            if not cat_data.empty:
                values = cat_data[value_type].values
                min_x = min(min_x, values.min())
                max_x = max(max_x, values.max())

                if len(values) > 1:
                    try:
                        density = cat_data[value_type].plot.density(
                            label=category, color=colors[idx % len(colors)], ax=ax
                        )
                        current_max_density = ax.get_ylim()[1]
                        max_density = min(max(max_density, current_max_density), 100)
                        print(f"    Density curve plotted for {category}")
                    except Exception as e:
                        print(f"    Error plotting density for {category}: {str(e)}")
                        ax.axvline(
                            values.mean(),
                            color=colors[idx % len(colors)],
                            label=category,
                        )
                        print(f"    Vertical line plotted for {category} at mean value")
                else:
                    ax.axvline(
                        values[0], color=colors[idx % len(colors)], label=category
                    )
                    print(f"    Single vertical line plotted for {category}")

        if min_x == float("inf") or max_x == float("-inf"):
            print(f"  No valid data for run_id {run_id}")
            plt.close()
            continue

        print(f"  X-axis limits: [{min_x:.4f}, {max_x:.4f}]")
        print(f"  Maximum density: {max_density:.4f}")

        margin = (max_x - min_x) * 0.1
        plt.xlim(min_x - margin, max_x + margin)
        plt.ylim(0, max_density * 1.1)  # Add a 10% margin at the top
        plt.title(title, fontsize=18)
        plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
        plt.ylabel("Density", fontsize=14)
        plt.legend(fontsize=10)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0%}"))
        plt.tight_layout()

        imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}.png")
        plt.savefig(imgpath)
        plt.close()
        print(f"  Graph saved in {imgpath}")


def plot_density_distributions(npv_df, pd_df, params_df, plots_folder):
    """
    Main function to plot all density distributions.
    """
    mpl.rcParams["font.family"] = "Times New Roman"
    plt.style.use("default")

    # Plot for NPV
    npv_folder = os.path.join(plots_folder, "npv")
    os.makedirs(npv_folder, exist_ok=True)
    plot_distributions_by_category(
        npv_df, params_df, npv_folder, "net_present_value_change", "technology"
    )
    plot_distributions_by_run(
        npv_df, params_df, npv_folder, "net_present_value_change", "technology"
    )

    # Plot for PD
    pd_folder = os.path.join(plots_folder, "pd")
    os.makedirs(pd_folder, exist_ok=True)
    plot_distributions_by_category(
        pd_df, params_df, pd_folder, "pd_difference", "sector"
    )
    plot_distributions_by_run(pd_df, params_df, pd_folder, "pd_difference", "sector")


def plot_barplot_distributions(npv_df, pd_df, params_df, plots_folder):
    """
    Main function to plot all bar plot distributions.
    """
    mpl.rcParams["font.family"] = "Times New Roman"
    plt.style.use("default")

    # Plot for NPV
    npv_folder = os.path.join(plots_folder, "npv_barplot")
    os.makedirs(npv_folder, exist_ok=True)
    plot_barplot_by_category(
        npv_df, params_df, npv_folder, "net_present_value_change", "technology"
    )
    plot_barplot_by_run(
        npv_df, params_df, npv_folder, "net_present_value_change", "technology"
    )

    # Plot for PD
    pd_folder = os.path.join(plots_folder, "pd_barplot")
    os.makedirs(pd_folder, exist_ok=True)
    plot_barplot_by_category(pd_df, params_df, pd_folder, "pd_difference", "sector")
    plot_barplot_by_run(pd_df, params_df, pd_folder, "pd_difference", "sector")


def plot_barplot_by_category(
    data_df, params_df, plots_folder, value_type, category_column
):
    """
    Plots grouped bar plots for each category (technology or sector), showing distributions per run_id.
    """
    plots_folder = os.path.join(plots_folder, f"{value_type}_by_{category_column}")
    os.makedirs(plots_folder, exist_ok=True)

    print(f"Creating grouped bar plots by {category_column} for {value_type}")

    categories = data_df[category_column].unique()
    categories = np.append(categories, "All")  # Add "All" for the special case

    for cat in categories:
        print(f"\nProcessing {category_column}: {cat}")

        if cat == "All":
            cat_data = data_df
            title = f"Grouped Bar Plot of {value_type} - All {category_column}s"
        else:
            cat_data = data_df[data_df[category_column] == cat]
            title = f"Grouped Bar Plot of {value_type} - {cat}"

        print(f"  Number of rows for this {category_column}: {len(cat_data)}")

        plt.figure(figsize=(14, 8), dpi=250)
        ax = plt.gca()

        # Bin calculation based on overall min and max values
        values = cat_data[value_type].values
        min_val = values.min()
        max_val = values.max()
        num_bins = 10
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)
        bar_width = (bin_edges[1] - bin_edges[0]) / (
            len(params_df) + 1
        )  # Width per bar

        for idx, (run_id, run_params) in enumerate(params_df.iterrows()):
            run_data = cat_data[cat_data["run_id"] == run_params["run_id"]]

            if not run_data.empty:
                values = run_data[value_type].values
                counts, _ = np.histogram(values, bins=bin_edges)

                # Calculate positions for the bars
                bar_positions = bin_edges[:-1] + idx * bar_width

                ax.bar(
                    bar_positions,
                    counts,
                    width=bar_width,
                    edgecolor="black",
                    label=f"{run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})",
                    alpha=0.7,
                )
                print(f"    Grouped bar plot distribution plotted for run_id {run_id}")

        plt.title(title, fontsize=18)
        plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
        plt.ylabel("Density", fontsize=14)
        plt.legend(fontsize=10)
        plt.tight_layout()

        imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}.png")
        plt.savefig(imgpath)
        plt.close()
        print(f"  Grouped bar plot saved in {imgpath}")


def plot_barplot_by_run(data_df, params_df, plots_folder, value_type, category_column):
    """
    Plots grouped bar plots for each run_id, showing the distribution for each technology or sector.
    """
    plots_folder = os.path.join(plots_folder, f"{value_type}_by_run_{category_column}")
    os.makedirs(plots_folder, exist_ok=True)

    print(
        f"Creating grouped bar plots by run for {value_type} based on {category_column} in {plots_folder}"
    )

    for run_id, run_params in params_df.iterrows():
        print(f"\nProcessing run_id: {run_id}")
        plt.figure(figsize=(14, 8), dpi=250)
        ax = plt.gca()

        run_data = data_df[data_df["run_id"] == run_params["run_id"]]
        print(f"  Number of rows for this run: {len(run_data)}")

        title = f"Grouped Bar Plot of {value_type} - {run_params['target_scenario']} ({run_params['shock_year']}, {run_params['scenario_geography']})"

        # Bin calculation based on overall min and max values
        values = run_data[value_type].values
        min_val = values.min()
        max_val = values.max()
        num_bins = 10
        bin_edges = np.linspace(min_val, max_val, num_bins + 1)
        bar_width = (bin_edges[1] - bin_edges[0]) / (
            len(run_data[category_column].unique()) + 1
        )

        for idx, category in enumerate(run_data[category_column].unique()):
            cat_data = run_data[run_data[category_column] == category]

            if not cat_data.empty:
                values = cat_data[value_type].values
                counts, _ = np.histogram(values, bins=bin_edges)

                # Calculate positions for the bars
                bar_positions = bin_edges[:-1] + idx * bar_width

                ax.bar(
                    bar_positions,
                    counts,
                    width=bar_width,
                    edgecolor="black",
                    label=category,
                    alpha=0.7,
                )
                print(f"    Grouped bar plot distribution plotted for {category}")

        plt.title(title, fontsize=18)
        plt.xlabel(f"{value_type.replace('_', ' ').title()}", fontsize=14)
        plt.ylabel("Density", fontsize=14)
        plt.legend(fontsize=10)
        plt.tight_layout()

        imgpath = os.path.join(plots_folder, f"{title.replace(' ', '_')}.png")
        plt.savefig(imgpath)
        plt.close()
        print(f"  Grouped bar plot saved in {imgpath}")


if __name__ == "__main__":
    # Constants
    DATA_SOURCE_FOLDER = os.path.join("workspace", "india_variability_analysis")
    PLOTS_FOLDER = os.path.join(DATA_SOURCE_FOLDER, "plots_distributions")
    PLOTS_FOLDER2 = os.path.join(DATA_SOURCE_FOLDER, "plots_histograms")

    # Load data
    npv_df, pd_df, params_df = load_data(DATA_SOURCE_FOLDER)

    if npv_df is None or pd_df is None or params_df is None:
        print("Data loading failed. Exiting program.")
    else:
        # Run the analysis and plot histogram distributions
        plot_barplot_distributions(npv_df, pd_df, params_df, PLOTS_FOLDER2)
        # Run the analysis and plot density distribution
        plot_density_distributions(npv_df, pd_df, params_df, PLOTS_FOLDER)
