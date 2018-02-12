import json
from pit.store import Store
import os
import requests
import lxml
from bs4 import BeautifulSoup
import re

CORPUS_DIR = "corpus"

class RssArticleScraper:

    headers={"User-Agent": "gamingcorpus-agent"}

    feeds = []
    articles = []
    origin = ""
    agent = ""
    desc = ""
    directory = ""

    def article_in_corpus(self, article_id):
        article_filepath = os.path.join(self.directory, "{}.json".format(article_id))     
        if os.path.exists(article_filepath):
            return True
        return False

    def __init__(self):

        self.directory = os.path.join(CORPUS_DIR, self.origin)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        self.load()
        self.save()

    def load(self):
        raise NotImplementedError

    def save(self):
        for article in self.articles:
            
            article_filepath = os.path.join(self.directory, "{}.json".format(article["id"]))     
            try:
                article_store = Store(article, origin=self.origin, agent=self.agent, desc=self.desc)
            except:
                print(article)

                article_store = Store(article, origin=self.origin, agent=self.agent, desc=self.desc)
                break
            article_store.save_to(article_filepath)



HTML_REGEX = re.compile('<.*?>')

def remove_html(html_str):
  rv = re.sub(HTML_REGEX, '', html_str)
  return rv