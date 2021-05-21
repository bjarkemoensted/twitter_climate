import pandas as pd

import config
import scraping

QUERY = "'central bank'"
EARLIEST_DATE = "2010-01-01"
LATEST_DATE = None
FILENAME = config.climate_data_file
SAVE_EVERY = 5000

_date_format = "%Y-%m-%d"
_month_format = "%Y-%m"


def parse_tweet(tweet):
    res = {}
    res["date"] = tweet.date.strftime(_date_format)
    res["month"] = tweet.date.strftime(_month_format)
    res["tweet_id"] = tweet.id
    res["content"] = tweet.content

    return res


def read_existing():
    """Reads in any data that's already been downloaded. Returns None if none is found."""
    res = None
    try:
        res = pd.read_pickle(FILENAME)
    except FileNotFoundError:
        pass
    return res


def determine_start_stop_dates(data):
    """Determines the periods in which we need to look for new data."""
    a = EARLIEST_DATE
    b = LATEST_DATE
    periods = []
    if data is None:
        periods = [(a, b)]
    else:
        a_data = min(data["date"])
        b_data = max(data["date"])
        missing_early_data = a != a_data
        periods.append((b_data, None))
        if missing_early_data:
            periods.append((a, a_data))
    return periods


def uninterruptible_pickle(df, filename):
    """Pickle input dataframe to target filename, but catches keyboard interrupts momentarily until saving is,
    completed so no data is lost from killing the script."""

    done = False
    interrupted = False
    while not done:
        try:
            df.to_pickle(filename)
            done = True
        except KeyboardInterrupt:
            print("Saving in progress... Interrupting after save is complete.")
            interrupted = True
        #
    if interrupted:
        print("fDone saving to {filename}. Re-raising exception.")
        raise KeyboardInterrupt


def sync():
    running = read_existing()

    periods = determine_start_stop_dates(running)
    print(f"Querying {len(periods)} periods: {str(periods)}.")

    def update_data_and_save(new_tweets):
        nonlocal running
        parsed = [parse_tweet(tweet) for tweet in new_tweets]
        reached = parsed[-1]["date"]
        new_df = pd.DataFrame(data=parsed)
        if running is None:
            running = new_df
        else:
            running = running.append(new_df, ignore_index=True)

        n_tweets_with_duplicates = len(running)
        running.drop_duplicates(subset="tweet_id", inplace=True)
        n_tweets = len(running)
        dropped = n_tweets_with_duplicates - n_tweets
        if dropped:
            print(f"Dropped {dropped} duplicate Tweet IDs.")

        msg = f"Reached date: {reached}. Downloaded {n_tweets} tweets total."
        print(msg)

        uninterruptible_pickle(df=running, filename=FILENAME)

    for startat, stopat in periods:
        scraping.scrape_between(
            base_query=QUERY,
            startat=startat,
            stopat=stopat,
            callback=update_data_and_save,
            buffer_length=SAVE_EVERY,
            verbose=False)

    print("Done syncing!")
    return


def main():
    sync()


if __name__ == '__main__':
    main()
