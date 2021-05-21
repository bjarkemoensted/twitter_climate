import snscrape.modules
import warnings


class NoSSLVerificationScraper(snscrape.modules.twitter.TwitterSearchScraper):
    """Ugly hack to disable SSL verification and silence warnings from snscrapes Twitter module."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session.verify = False

    def _request(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            return super()._request(*args, **kwargs)


def add_time_window_to_query(base_query, startat, stopat=None):
    """Takes a query such as '"central bank" OR "central banks"' and adds optional flags controlling the time window
    to search in.."""

    parts = [base_query]
    if stopat is not None:
        parts.append("until:" + stopat)
    parts.append("since:" + startat)
    query = " ".join(parts)
    return query


def build_query_from_search_terms(search_terms, startat, stopat=None, danish_only=False):
    """Builds a query from list of search terms, such as ['money', 'finance', 'etc...']."""
    if isinstance(search_terms, str):
        search_terms = [search_terms]

    term_string = " OR ".join(search_terms)
    base_query = "(%s)" % term_string
    if danish_only:
        base_query += " lang:da"

    query = add_time_window_to_query(base_query=base_query, startat=startat, stopat=stopat)
    return query


def scrape_between(
        base_query,
        callback,
        startat,
        stopat=None,
        buffer_length=100,
        max_tweets=None,
        verbose=True):
    """Takes a Twitter query string containing everything except start and stop dates, and scrapes tweets matching
    the query between the input time delimiters.
    Every time buffer_length tweets have been scraped, the tweets are sent to the callback method."""

    if any(bad in base_query for bad in ("until:", "since:")):
        raise ValueError("base query must not contain temporal info.")

    if max_tweets is None:
        max_tweets = float('inf')

    query = add_time_window_to_query(base_query=base_query, startat=startat, stopat=stopat)
    scraper = NoSSLVerificationScraper(query=query)

    tweets = []
    n_hits = 0
    for tweet in scraper.get_items():
        tweets.append(tweet)
        n_hits += 1
        if n_hits >= max_tweets:
            callback(tweets)
            print(f"Exceeded max of {max_tweets} tweets!")
            return True

        if len(tweets) >= buffer_length:
            callback(tweets)
            tweets = []
            if verbose:
                print("Processed %d tweets!" % buffer_length)
        #

    if tweets:
        callback(tweets)
    if verbose:
        print("Done scraping!")
    return True
