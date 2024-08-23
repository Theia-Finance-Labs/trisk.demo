import os
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
