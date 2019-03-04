import logging

from bs4 import BeautifulSoup

from mills import get_request
from mills import strip_n
from mills import parse_sec_today_url
from mills import d2sql
from mills import get_title
from mills import get_redirect_url
from mills import SQLiteOper


def scraw(so, proxy=None):
    """

    :param so:
    :param proxy:
    :return:
    """
    url = "https://sec.today/pulses/"
    r = get_request(url)
    if r:
        try:
            soup = BeautifulSoup(r.content, 'lxml')

        except Exception as e:
            logging.error("GET %s  failed : %s" % (url, repr(e)))
            return
        if soup:
            rows = soup.find_all("div", class_='row')

            if rows:

                for row in rows:

                    if row:
                        overview = {}

                        card_title = row.find("h5", class_="card-title")
                        if card_title:
                            card_title_text = strip_n(card_title.get_text())
                            card_title_url = card_title.find("a", class_="text-dark").get("href")
                            overview["title_english"] = card_title_text
                            sec_url = "https://sec.today%s" % card_title_url

                            url_details = get_redirect_url(sec_url, root_dir="data/sec_url",
                                                           issql=False, proxy=proxy)
                            if url_details:
                                overview["url"] = url_details.get("url")
                                overview["domain"] = url_details.get("domain")
                            else:
                                overview["url"] = sec_url

                        card_text = row.find("div", class_="card-text")
                        if card_text:
                            card_text_type = card_text.find("span", class_="badge badge-light")
                            if card_text_type:
                                card_text_type = strip_n(card_text_type.get_text())
                                overview["tag"] = card_text_type

                            card_text_source_day = card_text.find("small", class_="text-muted")
                            if card_text_source_day:
                                card_text_source_day = strip_n(card_text_source_day.get_text())

                                domain_ts = parse_sec_today_url(card_text_source_day)
                                if domain_ts:
                                    domain, ts = domain_ts
                                    overview["domain"] = domain
                                    overview["domain_name"] = str(get_title(overview["domain"], proxy=proxy))
                                    overview["ts"] = ts

                        card_text_chinese = row.find("p", class_="card-text my-1")
                        if card_text_chinese:
                            card_text_chinese = strip_n(card_text_chinese.find("q").get_text())
                            overview["title"] = card_text_chinese

                        if overview:
                            sql = d2sql(overview, table="xuanwu_detail_new")

                            if sql:
                                try:
                                    so.execute(sql)
                                except Exception as e:
                                    logging.error("[sec_total_sql]: sql(%s) error(%s)" % (sql, str(e)))

                            st = "{ts}\t{tag}\t{url}" \
                                 "\t{title}\t{title_english}\t{domain}\t{domain_name}".format(
                                ts=overview.get("ts"),
                                tag=overview.get("tag"),
                                domain=overview.get("domain"),
                                title=overview.get("title"),
                                title_english=overview.get("title_english"),
                                domain_name=overview.get("domain_name"),
                                url=overview.get("url")
                            )
                            print st


if __name__ == "__main__":
    """
    """
    proxy = None
    so = SQLiteOper("data/scrap.db")
    scraw(so, proxy=proxy)