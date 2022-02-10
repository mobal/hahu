from bs4 import BeautifulSoup
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import make_msgid

import chevron
import io
import json
import logging
import math
import os
import requests
import smtplib
import sys
import traceback



BASE_URL = "https://www.hasznaltauto.hu"
PAGE_SIZE = 20

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

payload = {
    "HirdetesSzemelyautoSearch[evjarat_min]": os.getenv("CAR_MIN_YEAR"),
    "HirdetesSzemelyautoSearch[futottkm_min]": os.getenv("CAR_DISTANCE_MIN"),
    "HirdetesSzemelyautoSearch[futottkm_max]": os.getenv("CAR_DISTANCE_MAX"),
    "HirdetesSzemelyautoSearch[kivitel][]": os.getenv("CAR_BODY_TYPE"),
    "HirdetesSzemelyautoSearch[marka_id]": os.getenv("CAR_MAKE"),
    "HirdetesSzemelyautoSearch[modell_id]": os.getenv("CAR_MODEL"),
    "HirdetesSzemelyautoSearch[vetelar_max]": os.getenv("CAR_MAX_PRICE"),
    "HirdetesSzemelyautoSearch[vetelar_min]": os.getenv("CAR_MIN_PRICE"),
    "HirdetesSzemelyautoSearch[uzemanyag][]": os.getenv("CAR_FUEL_TYPE"),
}


def _crawl(url):
    divs = BeautifulSoup(_get(url).content, "html.parser").find_all(
        "div", {"class": "talalati-sor"}
    )
    if len(divs) > 0:
        return _parse(divs)
    return []


def _create_message(car):
    msg = EmailMessage()
    msg["From"] = "Putt-Putt <{}>".format(os.getenv("SMTP_FROM"))
    msg["Subject"] = "[{0}] {1}".format(car.get("id"), car.get("title"))
    msg["To"] = os.getenv("SMTP_TO")
    msg["X-Priority"] = "2"
    with io.open(
        os.path.join(os.path.dirname(__file__), "templates/mail.mustache"),
        "r",
        encoding="utf-8",
    ) as f:
        if car["image"]:
            img_id = make_msgid()
            car["img_id"] = img_id[1:-1]
            msg.add_alternative(chevron.render(f, car), subtype="html")
            msg.get_payload()[0].add_related(
                car.get("image").read(), "image", "jpeg", cid=img_id
            )
        else:
            msg.add_alternative(chevron.render(f, car), subtype="html")
    return msg


def _get(url, stream=False):
    res = requests.get(
        url, headers={"User-Agent": os.getenv("USER_AGENT")}, stream=stream
    )
    if res.ok:
        return res
    else:
        logger.error(res.status_code)
        sys.exit(res.status_code)


def _get_image(url):
    res = _get(url, True)
    if res.ok:
        res.raw.decode_content = True
        return res.raw
    else:
        logger.error(res.status_code)
        sys.exit(res.status_code)


def _get_search_key():
    headers = {
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": os.getenv("USER_AGENT"),
        "Content-Type": "Application/X-WWW-Form-URLEncoded; Charset=UTF-8",
    }
    return json.loads(
        _post(
            BASE_URL + "/egyszeru/szemelyauto", dict(payload, getSearchUrl=1), headers
        ).content
    )["formUrl"].rsplit("/", 1)[-1]


def _get_total():
    headers = {
        "Accept": "application/json, text/javascript, */*, q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": os.getenv("USER_AGENT"),
        "Content-Type": "Application/X-WWW-Form-URLEncoded; Charset=UTF-8",
    }
    return json.loads(
        _post(BASE_URL + "/egyszeru/szemelyauto", payload, headers).content
    )["totalCount"]


def _parse(divs):
    cars = []
    for div in divs:
        a = div.find("h3").find("a", href=True)
        cars.append(
            {
                "details": div.find("div", {"class": "talalatisor-info adatok"}).text,
                "id": div.find("div", {"class": "talalatisor-hirkod"}).text.split()[1][
                    :-1
                ],
                "image": _get_image(
                    div.find("img", {"class": "img-responsive"})[
                        "data-lazyurl"
                    ].replace("_1t", "")
                )
                if div.find("img", {"class": "img-responsive"}).has_attr("data-lazyurl")
                else None,
                "price": div.find("div", {"class": "vetelar"}).text,
                "title": a.text,
                "url": a["href"],
            }
        )
    return cars


def _post(url, payload, headers={"User-Agent": os.getenv("USER_AGENT")}):
    res = requests.post(url, data=payload, headers=headers)
    if res.ok:
        return res
    else:
        logger.error(res.status_code)
        sys.exit(res.status_code)


def _load_database():
    if os.path.exists(os.getenv("DB_PATH")):
        with open(os.getenv("DB_PATH"), "r") as f:
            try:
                return json.load(f)
            except:
                logger.error(traceback.format_exc())
    else:
        logger.error(
            'The given path "{}" is not a valid path'.format(os.getenv("DB_PATH"))
        )
    return []


def _save_database(data):
    with open(os.getenv("DB_PATH"), "w") as f:
        try:
            json.dump(data, f)
        except:
            logger.error(traceback.format_exc())
            sys.exit(1)


def _update_database(cars):
    diff = []
    database = _load_database()
    for car in cars:
        temp = car.copy()
        temp.pop("image")
        if temp not in database:
            database.append(temp)
            diff.append(car)
    if len(diff) > 0:
        _save_database(database)
    return diff


def _send_mails(cars):
    logger.info("Sending email(s)...")
    try:
        server = smtplib.SMTP(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"))
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        for car in cars:
            server.sendmail(
                os.getenv("SMTP_FROM"),
                os.getenv("SMTP_TO"),
                _create_message(car).as_string(),
            )
        server.close()
    except:
        logger.error(traceback.format_exc())
        sys.exit(1)


def main():
    cars = []
    curr = 0
    last = math.ceil(_get_total() / PAGE_SIZE)
    search_key = _get_search_key()
    while curr < last:
        cars += _crawl(
            "{}/talalatilista/{}/page{}".format(BASE_URL, search_key, str(curr + 1))
        )
        curr += 1
    if len(cars) > 0:
        diff = _update_database(cars)
        logger.info('Found "{}" new car(s)'.format(len(diff)))
        if len(diff) > 0:
            _send_mails(diff)
    else:
        logger.info("The search returned no results")


if __name__ == "__main__":
    main()
