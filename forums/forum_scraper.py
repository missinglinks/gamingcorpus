import json
from pit.store import Store, load_json
import os
import requests
import lxml
from bs4 import BeautifulSoup
import re
import time
from copy import deepcopy

CORPUS_DIR = "corpus"

class ForumScraper:
    forums = {}
    max_pages = 100

    origin = ""
    agent = ""
    desc = ""
    directory = ""

    def __init__(self, max_pages):
        self.directory = os.path.join(CORPUS_DIR, self.origin)
        self.max_pages = max_pages
        #self.load()

    def get_thread_list(self, forum, url):
        raise NotImplementedError

    def get_thread_posts(self, id_, start_post, end_post):
        raise NotImplementedError


    def update(self):
        for forum, url in self.forums.items():
            trhead_list = []
            forum_dir = os.path.join(self.directory, forum)

            #load thread list from last update and build index with thread reply counts
            thread_list_filepath = os.path.join(self.directory, "{}.json".format(forum))
            if os.path.exists(thread_list_filepath):
                store = load_json(thread_list_filepath)
                last_thread_list = store.data()
                last_thread_index = { x["id"]: x["reply_count"] for x in last_thread_list  }
            else:
                last_thread_index = {}


            #get recent thread list
            print("... getting new thread list")
            thread_list = self.get_thread_list(forum, url)
            new_thread_list = deepcopy(thread_list)

            #get new threads
            for thread in thread_list:

                print("\t scrape thread '{}'".format(thread["title"]))

                if thread["id"] not in last_thread_index or thread["reply_count"] != last_thread_index[thread["id"]]:

                    year = thread["start_date"].split(" ")[-1].strip()
                    tmp_dir = os.path.join(forum_dir, year)
                    if not os.path.exists(tmp_dir):
                        os.makedirs(tmp_dir)

                    thread_filepath = os.path.join(tmp_dir, "{}.json".format(thread["id"]))

                    posts = self.get_thread_posts(thread["id"], 0, thread["reply_count"]+1)
                    thread["posts"] = posts
                    
                    print("\t {} posts scraped".format(len(posts)))
                    print("")
                    thread_store = Store(thread, origin=self.origin, agent=self.agent, desc=self.desc)
                    thread_store.save_to(thread_filepath)
                    #time.sleep(0.2)

            #save new thread list
            thread_list_store = Store(new_thread_list, origin=self.origin, agent=self.agent, desc=self.desc)
            thread_list_store.save_to(thread_list_filepath)            


    def init(self):
        for forum, url in self.forums.items():
            thread_list = []
            forum_dir = os.path.join(self.directory, forum)
            if not os.path.exists(forum_dir):
                os.makedirs(forum_dir)

            #get recent thread list
            print("... getting new thread list")
            thread_list = self.get_thread_list(forum, url)

            #save new thread list
            thread_list_filepath = os.path.join(self.directory, "{}.json".format(forum))
            thread_list_store = Store(thread_list, origin=self.origin, agent=self.agent, desc=self.desc)
            thread_list_store.save_to(thread_list_filepath)

            #get new threads
            for thread in thread_list:

                print("\t scrape thread '{}'".format(thread["title"]))

                year = thread["start_date"].split(" ")[-1].strip()
                tmp_dir = os.path.join(forum_dir, year)
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)

                thread_filepath = os.path.join(tmp_dir, "{}.json".format(thread["id"]))
                if not os.path.exists(thread_filepath):

                    posts = self.get_thread_posts(thread["id"], 0, thread["reply_count"]+1)
                    thread["posts"] = posts
                    
                    print("\t {} posts scraped".format(len(posts)))
                    print("")
                    thread_store = Store(thread, origin=self.origin, agent=self.agent, desc=self.desc)
                    thread_store.save_to(thread_filepath)
                #time.sleep(0.2)