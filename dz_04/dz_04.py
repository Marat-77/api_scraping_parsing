from datetime import datetime
from time import sleep
import re
import requests
from lxml import html
from pymongo import errors

import settings

"""
Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0
"""


def insert_data_to_mongodb(input_dict: dict):
    """
    Функция добавляет документ (input_dict) в коллекцию jobs,
    если встречается повторяющийся, то '_id' добавляется в коллекцию duplicates.
    :param input_dict:
    :return:
    """
    try:
        settings.news.insert_one(input_dict)
    except errors.DuplicateKeyError:
        settings.duplicates.insert_one({'dup_id': input_dict['_id']})
    except errors.ServerSelectionTimeoutError:
        print('ServerSelectionTimeoutError - Проверьте настройки соединения с сервером MongoDB')


def get_request(url, referer_url='', params=None):
    """
    Создание подключения и получение данных
    :param url:
    :param referer_url:
    :param params:
    :return:
    """
    if params is None:
        params = {}
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'
    headers = {
        'User-Agent': user_agent,
        'Referer': referer_url,
        'Connection': 'keep-alive',
        'Vary': 'User-Agent'
    }
    sleep(3)
    session = requests.session()

    try:
        response = session.get(url, headers=headers, params=params, timeout=5)
        session.close()
        return response
    except requests.exceptions.ReadTimeout:
        print('The server did not send any data in the allotted amount of time.')


def get_date_news_lenta(news_links, url):

    def _get_date(news_link):
        months = {'января': '01',
                  'февраля': '02',
                  'марта': '03',
                  'апреля': '04',
                  'мая': '05',
                  'июня': '06',
                  'июля': '07',
                  'августа': '08',
                  'сентября': '09',
                  'октября': '10',
                  'ноября': '11',
                  'декабря': '12'}
        # получаем html элемент из запрашиваемой страницы новости:
        news_link_html = html.fromstring(get_request(news_link, url).text)
        # селекторы xpath:
        xpath_time_lenta = '//time[@class="topic-header__item topic-header__time"]/text()'
        xpath_time_moslenta = '//div[@class="_1Lg_CbTX _240YeLMx"]/text()'  # ненадежный селектор
        # получаем список со строкой в которой есть время и дата
        date_html = news_link_html.xpath(f'{xpath_time_lenta} | {xpath_time_moslenta}')
        # Получаем: ['05:44, 14 июля 2022'] или ['Сегодня в 05:44']
        # преобразуем строку в список строк разделителем ', '
        date_html = date_html[0].split(', ')
        # Получаем: ['05:44', '14 июля 2022'] или ['Сегодня в 05:44']
        if len(date_html) == 1:
            # если получили ['Сегодня в 05:44']
            # паттерн регулярного выражения:
            regex = r"(\d{2}-\d{2}-\d{4})"
            # получаем дату "14-07-2022":
            date_html = re.search(regex, news_link)[0]
            # формат даты:
            format_str = '%d-%m-%Y'
        else:
            # ['05:44', '14 июля 2022']
            # Получаем дату в виде строки '14 июля 2022':
            news_date = date_html[-1]
            # Получаем месяц:
            month = news_date.split(' ')[1]
            # Заменяем название месяца на числовой формат
            date_html = news_date.replace(month, months.get(month))
            # формат даты:
            format_str = '%d %m %Y'
        # Получаем дату в формате datetime:
        dateformat_news = datetime.strptime(date_html, format_str).date()
        return dateformat_news

    return map(_get_date, news_links)


def get_lenta_news(response):
    url = response.url
    dom = html.fromstring(response.text)
    # ссылки на новость
    a_topnews = '//a[contains(@class, "_topnews")]'
    news_links = dom.xpath(f'{a_topnews}/@href')

    news_links = tuple(
        map(lambda link: url[:-1] + link if 'https://' not in link else link, news_links)
    )

    # наименование новости
    news_titles = dom.xpath(f'{a_topnews}//h3/text() | {a_topnews}//span/text()')
    news_sources = (news_link.split('/news/')[0] for news_link in news_links)

    print('Пожалуйста, подождите окончания опроса ссылок...')
    news_dates = get_date_news_lenta(news_links, url)
    results = zip(news_links, news_titles, tuple(news_dates), tuple(news_sources))
    for i_res in results:
        res_dict = {'_id': i_res[0],
                    'title': i_res[1],
                    'date': i_res[2].strftime('%Y-%m-%d'),
                    'source': i_res[3]}
        insert_data_to_mongodb(res_dict)


def get_date_news_mail(news_links, url):
    def __get_date(news_link):
        # получаем html элемент из запрашиваемой страницы новости:
        news_link_html = html.fromstring(get_request(news_link, url).text)
        # селектор xpath:
        xpath_time_mail = '//span[@datetime]/@datetime'
        # получаем список со строкой в которой есть время и дата
        date_html = news_link_html.xpath(xpath_time_mail)
        # print(date_html[0])  # 2022-07-14T14:50:06+03:00

        # Получаем дату в формате datetime:
        dateformat_news = datetime.fromisoformat(date_html[0]).date()

        # источник новости:
        xpath_source = '//span[@class="breadcrumbs__item"]/span/a/@href'
        news_source = news_link_html.xpath(xpath_source)[0]
        return dateformat_news, news_source

    # # кортеж дат новостей:
    return map(__get_date, news_links)


def get_mail_news(response):
    url = response.url
    dom = html.fromstring(response.text)
    # контейнер с новостями:
    div_topnews = '//div[contains(@data-logger, "news__MainTopNews")]'
    news_div = dom.xpath(div_topnews)[0]
    a_photo_news = '//a[contains(@class, "topnews__item")]'
    a_list_news = '//a[@class="list__text"]'
    # ссылка на новость:
    news_links = news_div.xpath(f'{a_photo_news}/@href | {a_list_news}/@href')

    # заголовок новости
    span_title = '//span[contains(@class, "photo__title")]'
    news_text = news_div.xpath(f'{a_photo_news}{span_title}/text() | {a_list_news}/text()')

    print('Пожалуйста, подождите окончания опроса ссылок...')

    # получить респонс по ссылке новости и взять xpath.
    # //span[@datetime]/@datetime
    news_dates_sources = get_date_news_mail(news_links, url)
    results = zip(news_links, news_text, news_dates_sources)
    for res in results:
        res_dict = {'_id': res[0],
                    'title': res[1].replace('\xa0', ' '),
                    'date': res[2][0].strftime('%Y-%m-%d'),
                    'source': res[2][1]}
        insert_data_to_mongodb(res_dict)


def get_yandex_news(response):
    print('.' * 55)
    url = response.url
    print(url)
    # вылезает captcha:
    # https://yandex.ru/showcaptcha?cc=1&retpath=....

    dom = html.fromstring(response.text)
    # pprint(dom)
    # //section[@aria-labelledby="top-heading"]
    # контейнер с новостями:
    section_topnews = '//section[@aria-labelledby="top-heading"]'
    # print(section_topnews)
    print('-' * 45)
    # news_div = dom.xpath(section_topnews)[0]
    news_div = dom.xpath('//section[@aria-labelledby="top-heading"]/text()')
    print(news_div)
    print(news_div.text)

    # h2_title = '//h2[@class="mg-card__title"]'
    # # {news_div}{h2_title}/text()
    # news_title = news_div.xpath(f'{h2_title}/text()')
    # print(news_title)
    a_href = ''
    # {news_div}{h2_title}/@href
    # ------------------------------
    # yandex/news
    #
    # title_news:
    # //section[@aria-labelledby="top-heading"]//h2[@class="mg-card__title"]
    # link_news:
    # //section[@aria-labelledby="top-heading"]//h2[@class="mg-card__title"]/a/@href
    #
    # <span class="mg-card-source__time">20:27</span>
    # <span class="mg-card-source__time">12 июля в 16:12</span>
    # date_time_news:
    # //section[@aria-labelledby="top-heading"]//span[@class="mg-card-source__time"]
    #
    # source_news:
    # //a[contains(text(),'string_from_title')]
    # //a[contains(text(),'string_from_title')]/@href


def main():
    news_servers = {'lenta': {'url': 'https://lenta.ru/',
                              'referer_url': 'https://lenta.ru/'},
                    'mail': {'url': 'https://news.mail.ru/',
                             'referer_url': 'https://news.mail.ru/'},
                    'yandex': {'url': 'https://yandex.ru/news/',
                               'referer_url': 'https://yandex.ru/news/'}}

    for news_server, urls in news_servers.items():
        if news_server == 'lenta':
            print('lenta')
            print(urls.get('url'))
            response = get_request(urls.get('url'), urls.get('referer_url'))
            get_lenta_news(response)
        if news_server == 'mail':
            print('mail')
            print(urls.get('url'))
            response = get_request(urls.get('url'), urls.get('referer_url'))
            get_mail_news(response)
        if news_server == 'yandex':
            print('yandex')
            print(urls.get('url'))
            # print(urls.get('referer_url'))
            # response = get_request(urls.get('url'), urls.get('referer_url'))
            # get_yandex_news(response)
            print('мешает captcha')
    print('well done!')


if __name__ == '__main__':
    main()
