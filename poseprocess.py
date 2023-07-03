# -*- coding: utf-8 -*-
import datetime
import hashlib
import re
from bs4 import BeautifulSoup
import tqdm
from models import SourceHTML, Action
from db.mongo import get_mongo_client

DOMAIN_NAME = "http:"


def run():
    db = get_mongo_client()["gymcrawler"]
    unhandled_source_htmls = [
        SourceHTML.from_bson(**i)
        for i in db[SourceHTML.__tablename__].find({}).sort("_id", 1)
    ]
    # 详情页
    for unhandled_source_html in tqdm.tqdm(
        unhandled_source_htmls, desc="processing actions"
    ):
        # for unhandled_source_html in unhandled_source_htmls:
        name = ""
        source = unhandled_source_html.source
        source_hash = unhandled_source_html.source_hash
        difficulty_level = ""
        category = ""
        muscle_type = []
        other_muscle_types = []
        equipment = []
        cover = ""
        action_pictures = []
        muscle_pictures = []
        video = ""
        instruction = ""

        if (
            re.match(
                r"^http://m.elainecroche.com/dongzuo/\d+", unhandled_source_html.source
            )
            is not None
        ):
            html = BeautifulSoup(unhandled_source_html.content, "html.parser")
            html_details_container = html.find("di", class_="o-video-bd")
            # print("source link:", unhandled_source_html.source)
            # get video src
            if html_details_container is not None:
                video = (
                    re.search(
                        r'"video_url"\s*:\s*"(.+?)"', unhandled_source_html.content
                    )
                    .groups()[0]
                    .replace("\/", "/")
                )
                # print("video link:", video)

                video_info_container = html_details_container.find(
                    "div", class_="o-video-info"
                )
                name = video_info_container.find(
                    "h1", class_="video-title"
                ).text.strip()
                # print("name:", name)

                # 类型,级别,主要肌肉群,其他肌肉,器械要求
                action_basic_infos = video_info_container.find(
                    "div", class_="info-main"
                )

                action_basic_infos_list = [
                    re.sub(r"\s", "", action_basic_info.text.strip()).split(":")
                    for action_basic_info in action_basic_infos.find_all("p")
                ]
                # print("info list:", action_basic_infos_list)

                action_basic_infos = {
                    info[0]: info[1] for info in action_basic_infos_list
                }
                difficulty_level = action_basic_infos["级别"]
                # print("difficulty_level:", difficulty_level)

                category = action_basic_infos["类型"]
                # print("category:", category)

                muscle_type = [
                    i.strip() for i in action_basic_infos["主要肌肉群"].split("、")
                ]
                # print("muscle_type:", muscle_type)

                other_muscle_types = [
                    i.strip() for i in action_basic_infos["其他肌肉"].split("、")
                ]
                if other_muscle_types == ["无"]:
                    other_muscle_types = [""]
                # print("other_muscle_types:", other_muscle_types)

                equipment = [i.strip() for i in action_basic_infos["器械要求"].split("、")]
                # print("equipment:", equipment)

                cover = (
                    re.search(r'"pic"\s*:\s*"([^"]+)"', unhandled_source_html.content)
                    .groups()[0]
                    .replace("\/", "/")
                )
                # print("cover:", cover)

                guide_container = html_details_container.find(
                    "div", class_="o-video-guide-pics2"
                )

                if guide_container is not None:
                    action_pictures = [
                        i["src"] for i in guide_container.find_all("img")
                    ]

                    gif_picture = (
                        re.search(r'"gif"\s*:\s*"(.*?)"', unhandled_source_html.content)
                        .groups()[0]
                        .strip()
                        .replace("\/", "/")
                    )
                    if gif_picture is not None and gif_picture:
                        action_pictures.append(gif_picture)
                # print("action_pictures:", action_pictures)

                muscle_pic_container = html_details_container.find(
                    "div", class_="o-video-guide"
                )
                muscle_pictures = [
                    i["src"] for i in muscle_pic_container.find_all("img")
                ]
                # print("muscle_picures:", muscle_pictures)

                instruction = (
                    html_details_container.find("div", class_="guide-text")
                    .find("pre", class_="cont")
                    .text.strip()
                )
                # print("instruction:", instruction)

            html_details_container = html.find("div", class_="bd")
            if html_details_container is not None:
                name = (
                    html_details_container.find("div", class_="info-hd")
                    .find("h4")
                    .text.strip()
                )
                # print("name:", name)

                action_basic_infos = html_details_container.find(
                    "div", class_="info-bd"
                )
                action_basic_info_keys = [
                    re.sub(r"\s", "", i.contents[0])
                    for i in action_basic_infos.find_all("li")
                ]
                action_basic_info_values = [
                    re.sub(r"\s", "", i.text) for i in action_basic_infos.find_all("em")
                ]
                action_basic_infos = dict(
                    zip(action_basic_info_keys, action_basic_info_values)
                )
                # print("info list:", action_basic_info)

                difficulty_level = action_basic_infos["级别"]
                # print("difficulty_level:", difficulty_level)

                category = action_basic_infos["类型"]
                # print("category:", category)

                muscle_type = [
                    i.strip() for i in action_basic_infos["主要肌肉群"].split("、")
                ]
                # print("muscle_type:", muscle_type)

                other_muscle_types = [
                    i.strip() for i in action_basic_infos["训练部位"].split("、")
                ]
                # print("other_muscle_types:", other_muscle_types)

                equipment = [i.strip() for i in action_basic_infos["器械类型"].split("、")]
                # print("equipment:", equipment)

                video_info = html_details_container.find(
                    "div", class_="action-video"
                ).find("video")

                cover = video_info["poster"][0]
                # print("cover: ", cover)

                video = video_info["src"][0]
                # print("video: ", video)

                action_pictures = []

                action_detail_list = html_details_container.find_all(
                    "div", class_="action-detail"
                )

                instruction = action_detail_list[0].text.strip()
                # print("instruction: ", instruction)

                muscle_pictures = [
                    muscle_picture["src"]
                    for muscle_picture in action_detail_list[1].find_all("img")
                ]
                # print("muscle_pictures: ", muscle_pictures)

            if db[Action.__tablename__].find_one({"source": source}) is None:
                db[Action.__tablename__].replace_one(
                    {"source": source},
                    Action(
                        name=name,
                        source=source,
                        source_hash=source_hash,
                        difficulty_level=difficulty_level,
                        category=category,
                        muscle_type=muscle_type,
                        other_muscle_types=other_muscle_types,
                        equipment=equipment,
                        cover=cover,
                        action_pictures=action_pictures,
                        muscle_pictures=muscle_pictures,
                        video=video,
                        instruction=instruction,
                        create_time=datetime.datetime.now(),
                    ).to_bson(),
                    upsert=True,
                )
        else:
            html = BeautifulSoup(unhandled_source_html.content, "html.parser")
            action_list = (
                html.find("div", class_="o-exercise-list").find("ul").find_all("li")
            )
            for action in action_list:
                avatar_container = action.find_all("a", href=re.compile(r"^//.*"))[0]
                source = DOMAIN_NAME + avatar_container["href"]
                source_hash = hashlib.md5(source.encode("utf-8")).hexdigest()

                if (
                    db[SourceHTML.__tablename__].find_one({"source_hash": source_hash})
                    is not None
                ):
                    continue

                if (
                    db[Action.__tablename__].find_one({"source_hash": source_hash})
                    is None
                ):
                    action_content_container = action.find("div", class_="cont")
                    name = (
                        action_content_container.find("a", href=re.compile(r"^//.*"))
                        .find("span", class_="title")
                        .text.strip()
                    )
                    # print("name: ", name)

                    action_basic_info_values = [
                        action_basic_info_value.text.strip()
                        for action_basic_info_value in action_content_container.find(
                            "div", class_="tag"
                        ).find_all("span")
                    ]
                    action_basic_info_keys = ["级别", "器械要求", "主要肌肉群"]
                    action_basic_info = dict(
                        zip(action_basic_info_keys, action_basic_info_values)
                    )

                    difficulty_level = action_basic_info["级别"]
                    # print("difficult level: ", difficulty_level)

                    equipment = [
                        i.strip() for i in action_basic_info["器械要求"].split(",")
                    ]
                    # print("equipment: ", equipment)

                    muscle_type = [
                        i.strip()
                        for i in action_basic_info["主要肌肉群"]
                        .replace("默认,", "")
                        .split(",")
                    ]
                    # print("muscle_type: ", muscle_type)

                    cover = avatar_container.find("div", class_="avatar-pic").find(
                        "img"
                    )["src"]
                    # print("cover: ", cover)

                    action_pictures = [cover]
                    # print("action_pictures: ", action_pictures)

                    db[Action.__tablename__].replace_one(
                        {"source_hash": source_hash},
                        Action(
                            name=name,
                            source=source,
                            source_hash=source_hash,
                            difficulty_level=difficulty_level,
                            category=category,
                            muscle_type=muscle_type,
                            other_muscle_types=other_muscle_types,
                            equipment=equipment,
                            cover=cover,
                            action_pictures=action_pictures,
                            muscle_pictures=muscle_pictures,
                            video=video,
                            instruction=instruction,
                            create_time=datetime.datetime.now()
                        ).to_bson(),
                        upsert=True,
                    )


if __name__ == "__main__":
    run()
