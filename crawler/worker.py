from threading import Thread

from inspect import getsource
from collections import defaultdict
from utils.download import download
from utils import get_logger
import scraper
import time
import nltk
from nltk.corpus import stopwords


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        word_count = {}
        word_frequency = defaultdict(int)
        
        # nltk has a set of stopwords that can be imported
        nltk.download('stopwords')
        # stops is a set containing english stop words
        stops = set(stopwords.words('english'))
        # remove words from nltk stopwords set that aren't included in the rank.nl stopwords list
        remove_from_nltk = {"ma", "mustn", "haven", "shouldn", "can", "mightn", "aren", "doesn",
                            "weren", "hasn", "needn't",	"ain", "o",	"needn", "s", "ll", "that'll",
                            "don", "m", "will",	"didn",	"wasn",	"re",	"isn", "ve", "should've",
                            "y", "wouldn", "mightn't", "just", "hadn", "shan", "couldn", "d", "won",
                            "t", "now"}
        stops = stops-remove_from_nltk
        # add missing words from rank.nl to nltk stopwords set
        add_to_nltk = {"they're", "i'd", "how's", 'ought', "he'd", "can't", "when's", "he'll", "he's", 
                       'cannot', "we've", "i'll", "she'd", "where's", "they'd", "here's", "they'll", 
                       "why's", 'would', "i've", 'could', "who's", "there's", "we're", "that's", "let's", 
                       "we'd", "i'm", "she'll", "we'll", "they've", "what's"}
        stops = stops.union(add_to_nltk)

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, word_count, word_frequency, stops)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            # time delay/politeness:
            time.sleep(self.config.time_delay)
        
        # find the largest int length in the word_count dict
        longest_page_length = max(word_count.keys())
        # find the url that corresponds with the largest length
        longest_page = word_count[longest_page_length]
        # print out results
        print(f'Longest Page: {longest_page}')
        print(f'Longest Page Length: {longest_page_length}')
        
        sort_by_frequency = sorted(word_frequency.items(), key=lambda x: x[1], reversed=True)
        # print(sort_by_frequency)
        most_common_words = [key for key in sort_by_frequency.keys()[:51]]
        print("MOST COMMON WORDS:")
        print(most_common_words)
