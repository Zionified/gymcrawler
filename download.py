# -*- coding: utf-8 -*-
import datetime
import functools
import hashlib
import re
import time
import requests
import tqdm

from bs4 import BeautifulSoup
from models import SourceHTML
from db.mongo import get_mongo_client


DOMAIN_NAME = "http:"


def delay(seconds=1):
    def wrapper(func):
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=seconds + 1)

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            nonlocal start_time
            try:
                ret = func(*args, **kwargs)
                return ret
            except KeyboardInterrupt:
                raise
            except:
                raise
            finally:
                end_time = datetime.datetime.now()
                time_elapsed = (end_time - start_time).total_seconds()
                if time_elapsed < seconds:
                    time.sleep(seconds - time_elapsed)
                start_time = datetime.datetime.now()

        return _wrapper

    return wrapper


def print_datetime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        try:
            func(*args, **kwargs)
        except:
            raise
        finally:
            end_time = datetime.datetime.now()
            print(
                "start time: {}, end time: {}, time elapsed: {}".format(
                    start_time, end_time, end_time - start_time
                )
            )

    return wrapper


# @print_datetime
@delay(1)
def send_get_request(url, *args, **kwargs):
    resp = requests.get(url, *args, **kwargs)
    resp.raise_for_status()
    return resp


def crawl_actions_by_pages():
    db = get_mongo_client()["gymcrawler"]

    total_pages = range(1, 81)
    # total_pages = [1]

    for page_no in tqdm.tqdm(total_pages):
        page_url = "http://m.elainecroche.com/dongzuo/?page={}".format(page_no)
        page_url_hash = hashlib.md5(page_url.encode("utf-8")).hexdigest()

        if (
            db[SourceHTML.__tablename__].find_one({"source_hash": page_url_hash})
            is not None
        ):
            continue
        try:
            resp = send_get_request(page_url, timeout=1)
        except KeyboardInterrupt:
            return
        except:
            continue

        db[SourceHTML.__tablename__].replace_one(
            {"source_hash": page_url_hash},
            SourceHTML(
                source=page_url,
                source_hash=page_url_hash,
                content=resp.content.decode(),
                create_time=datetime.datetime.now(),
            ).to_bson(),
            upsert=True,
        )
        # print(page_url, resp.content.decode())

        html = BeautifulSoup(resp.content.decode(), "html.parser")
        action_default_urls = list(
            set(
                [
                    DOMAIN_NAME + i["href"]
                    for i in html.find("div", class_="o-exercise-list").find_all(
                        "a", href=re.compile(r"^//m.elainecroche.com/dongzuo/\d+/$")
                    )
                ]
            )
        )
        # print(action_default_urls)

        for action_default_url in action_default_urls:
            action_default_url_hash = hashlib.md5(
                action_default_url.encode("utf-8")
            ).hexdigest()

            if (
                db[SourceHTML.__tablename__].find_one(
                    {"source_hash": action_default_url_hash}
                )
                is not None
            ):
                continue

            try:
                resp = send_get_request(action_default_url, timeout=1)
            except KeyboardInterrupt:
                return
            except:
                continue
            html = BeautifulSoup(resp.content.decode(), "html.parser")

            db[SourceHTML.__tablename__].replace_one(
                {"source_hash": action_default_url_hash},
                SourceHTML(
                    source=action_default_url,
                    source_hash=action_default_url_hash,
                    content=resp.content.decode(),
                    create_time=datetime.datetime.now(),
                ).to_bson(),
                upsert=True,
            )


def run():
    crawl_actions_by_pages()


if __name__ == "__main__":
    run()
