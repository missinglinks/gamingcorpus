import requests
import json
from bs4 import BeautifulSoup
import time
import os

OUT_DIR = "corpus/resetera"

FORUMS = {
    "resetera_etc": "https://www.resetera.com/forums/etcetera.9/page-{page}"
}

MAX_PAGES = 1000


THREAD = "https://www.resetera.com/threads/{id}/page-{page}"

def get_thread_posts(id_,start_post, end_post):
    start_page = int(start_post/50)
    end_page = int(end_post/50)
    
    posts = []
    
    for page in range(start_page+1, end_page+2):
        print("\t\t page {}".format(page))
        rsp = requests.get(THREAD.format(id=id_, page=page))
        soup = BeautifulSoup(rsp.text, "html.parser")

        for article in soup.find_all("article", {"class":"message--post"}):
            post_id = article["data-content"]

            user_details = article.find("h4", {"class": "message-name"})
            user_link = user_details.find("a")
            if user_link:
                user = user_link.text.strip()
                user_id = user_link["data-user-id"]
            else:
                user = user_details.text.strip()
                user_id = None
            
            user_title = article.find("h5", {"class": "userTitle"}).text.strip()

            permalink = article.find("div", {"class": "message-permalink"})
            permalink = permalink.find("a")["href"]

            #print(user_id, user)

            content = article.find("div", {"class": "message-cell--main"})
            date = content.find("time")["title"]

            text_container = content.find("div", {"class": "bbWrapper"})
            text = text_container.text.strip()
            text_html = str(text_container)

            posts.append({
                "post_id": post_id,
                "user": user,
                "user_id": user_id,
                "user_title": user_title,
                "permalink": permalink,
                "text_html": text_html
            })
        
        time.sleep(0.2)
        
        #print(date)
    return posts

def get_thread_list(forum, url):
    thread_list = []

    for page in range(1, MAX_PAGES):
        print("page ",page)
        
        rsp = requests.get(url.format(page=page))
        soup = BeautifulSoup(rsp.text, "html.parser")
        
        current_page = soup.find("a",{"class": "currentPage"})
        if not current_page:
            current_page = soup.find("li", {"class": "pageNav-page--current"})
    
        current_page = int(current_page.text)
        if current_page != page:
            break 
            
        for li in soup.find_all("li", {"class": "discussionListItem"}):
            #skip sticky threads
            if "sticky" not in li["class"]:
                title = li.find("h3")
                thread_url = title.find("a")["href"]
                id_ = thread_url.split(".")[-1][:-1]
                title = title.text.strip()
                
                reply_count = li.find("dl", {"class": "major"}).text.replace("Posts:", "").replace(",","").strip()
                if reply_count.isdigit():
                    reply_count = int(reply_count)
                else:
                    reply_count = 0
                abbr = li.find("abbr", {"class": "DateTime"})
                
                if not abbr:
                    date = li.find("a", {"class" : "faint"}).text
                else:
                    date = abbr["data-datestring"]

                user_a = li.find("a", {"class": "username"})
                user = user_a.text.strip()
                user_id = user_a["href"].split(".")[-1][:-1]

                thread_list.append({
                    "title": title,
                    "id": id_,
                    "user": user,
                    "user_id": user_id,
                    "start_date": date,
                    "reply_count": reply_count     
                })

        time.sleep(0.2)
        
    return thread_list




def main():

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    for forum, url in FORUMS.items():
        
        forum_dir = os.path.join(OUT_DIR, forum)
        if not os.path.exists(forum_dir):
            os.makedirs(forum_dir)

        #get recent thread list
        print("... getting new thread list")
        thread_list = get_thread_list(forum, url)

        #save new thread list
        thread_list_filepath = os.path.join(OUT_DIR, "{}.json".format(forum))
        with open(thread_list_filepath, "w") as f:
            json.dump(thread_list, f)

        """
        #get new threads
        for thread in thread_list:

            print("\t scrape thread '{}'".format(thread["title"]))

            year = thread["start_date"].split(" ")[-1].strip()
            tmp_dir = os.path.join(forum_dir, year)
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            thread_filepath = os.path.join(tmp_dir, "{}.json".format(thread["id"]))
            if not os.path.exists(thread_filepath):
                posts = get_thread_posts(thread["id"], 0, thread["reply_count"]+1)
                thread["posts"] = posts
                
                print("\t {} posts scraped".format(len(posts)))
                print("")

                with open(thread_filepath, "w") as f:
                    json.dump(thread, f)
            time.sleep(0.2)

        """

if __name__ == "__main__":
    main()