# -*- coding: utf-8 -*-
import hashlib
import re
import requests
import tqdm

from bs4 import BeautifulSoup
from sqlalchemy import select, text

from db.engine import get_engine, get_session
from db.models.sourcehtml import SourceHTML


DOMAIN_NAME = "http:"

def delay():
    pass

# def crawl_action_default():
#     resp = requests.get("http://m.elainecroche.com/dongzuo/?page=1")
#     resp.raise_for_status()
#     html = BeautifulSoup(resp.content.decode(), "html.parser")
#     container = html.body.find("div", class_="o-exercise-main")
#     print(container)


def crawl_actions_by_pages():
    total_pages = range(1, 81)
    # total_pages = [1]

    for page_no in total_pages:
        page_url = "http://m.elainecroche.com/dongzuo/?page={}".format(page_no)
        try:
            resp = requests.get(page_url, timeout=1)
            resp.raise_for_status()
        except:
            print("Invalid link...skipping page {}".format(page_no))
            continue

        page_url_hash = hashlib.md5(page_url.encode("utf-8")).hexdigest()

        with get_session() as session:
            if (
                session.scalars(
                    select(SourceHTML).where(SourceHTML.source_hash == page_url_hash)
                ).first()
                is not None
            ):
                continue

            session.add(
                SourceHTML(
                    source=page_url,
                    source_hash=page_url_hash,
                    content=resp.content.decode(),
                )
            )
            session.commit()
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

        for action_default_url in tqdm.tqdm(
            action_default_urls,
            desc="page={}".format(page_no),
        ):
            # for action_default_url in tqdm.tqdm(
            #     ["http://m.elainecroche.com/dongzuo/1/"],
            #     desc="page={}".format(page_no),
            # ):
            try:
                resp = requests.get(action_default_url, timeout=1)
                resp.raise_for_status()
            except:
                print("Invalid link...skipping {}".format(action_default_urls))
                continue

            html = BeautifulSoup(resp.content.decode(), "html.parser")

            action_default_url_hash = hashlib.md5(
                action_default_url.encode("utf-8")
            ).hexdigest()

            # print("inserting ", action_default_url)
            with get_session() as session:
                if (
                    session.scalars(
                        select(SourceHTML).where(
                            SourceHTML.source_hash == action_default_url_hash
                        )
                    ).first()
                    is not None
                ):
                    continue

                session.add(
                    SourceHTML(
                        source=action_default_url,
                        source_hash=action_default_url_hash,
                        content=resp.content.decode(),
                    )
                )
                session.commit()


def run():
    crawl_actions_by_pages()


if __name__ == "__main__":
    run()
