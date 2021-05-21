import os
import pandas as pd

import config


def process_monthly(df):
    """Reads in the raw Twitter data on central banks + climate change and summarizes by month.
    Counts the occurrences each month of 'central bank' and 'climate change', and computes the ratio between them,
    raw as well as 12 month rolling avg.
    Saves to climate_results_file from config file, and attempts to save to network drive as well."""

    text = [s.lower() for s in df["content"]]
    cb_h = "contains_central_bank"
    cc_h = "contains_climate_change"

    df[cb_h] = ["central bank" in s for s in text]
    df[cc_h] = ["climate change" in s for s in text]

    selected = df[["month", cb_h, cc_h]]
    monthly = selected.groupby("month").agg('sum')
    monthly.sort_values("month", inplace=True)
    monthly["ratio"] = monthly[cc_h] / monthly[cb_h]
    monthly["ratio_rolling_avg_12"] = monthly["ratio"].rolling(window=12).mean()

    return monthly


def save_network(df):
    try:
        if not os.path.exists(config.network_path):
            print(f"Network path missing ({config.network_path}) - attempting to create it")
            os.makedirs(config.network_path)
            print("Success!")
        df.to_excel(config.climate_results_file_network)
        print(f"Successfully saved to network path: {config.climate_results_file_network}")
    except Exception as e:
        print(f"*** Network save failed with exception ***\n{str(e)}.")


def aggregate():
    print("Reading in data.")
    df = pd.read_pickle(config.climate_data_file)

    print("Aggregating by month.")
    monthly = process_monthly(df)

    print("Saving results locally.")
    monthly.to_excel(config.climate_results_file)

    print("Attempting network save")
    save_network(monthly)
    print("...Done!")


def main():
    aggregate()


if __name__ == '__main__':
    main()
