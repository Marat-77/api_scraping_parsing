"""
Методы сбора и обработки данных из сети Интернет
Урок 1. Основы клиент-серверного взаимодействия. Работа с API.
VK API
"""

# Методы сбора и обработки данных из сети Интернет
# Урок 1. Основы клиент-серверного взаимодействия. Работа с API.
# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.
# Если нет желания заморачиваться с поиском, возьмите API вконтакте (https://vk.com/dev/first_guide).
# Сделайте запрос, чтобы получить список всех сообществ на которые вы подписаны.

import os  # работа с файловой системой
import json  # для кодирования и декодирования данных JSON
from pprint import pprint  # для "красивого вывода данных
from dotenv import load_dotenv  # загрузка информации из ".env"-файла
import requests  # HTTP-библиотека для отправки http-запросов


def config():
    """
    Настройки
    :return:
    """
    # версия API VK
    # https://dev.vk.com/reference/versions
    version = '5.131'

    # загрузка информации из ".env"-файла
    load_dotenv()

    # получение token из файла .env в виде строки TEST_ACCESS_TOKEN="1q2w3e4r5t6y7u8i9oTEST"
    token = os.getenv("VK_TOKEN")

    return token, version


def save_data_to_json(input_data: dict, file_name: str = 'vk_data'):
    """
    Функция сохранения полученных данных в файл json.
    :param input_data:
    :param file_name:
    :return:
    """
    file_name += '.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=2, ensure_ascii=False)


def get_friends(target_id=None):
    """
    Получение данных о друзьях пользователя.
    :return:
    """
    # метод получения данных о друзьях онлайн:
    # method = 'friends.getOnline'

    # метод получения данных о всех друзьях:
    method = 'friends.get'
    params = {
        'order': 'name',
        'count': 15,
        'fields': 'city'
    }
    if target_id:
        params['user_id'] = target_id

    return get_from_vk_api(method, params)


def user_info(target_ids=None):
    """
    Получение информации о пользователе.
    :param target_ids: str
    :return:
    """
    # target_ids - id или короткое имя пользователя
    # users.get
    method = 'users.get'
    params = {
        'fields': 'about'
    }
    if target_ids:
        params['user_ids'] = target_ids
    return get_from_vk_api(method, params)


def user_group(target_id=None):
    """
    Получение информации о группах, в которых состоит пользователь.
    Если не задан target_id, то текущий пользователь (владелец токена).
    :return:
    """
    # groups.get
    method = 'groups.get'
    params = {
        'extended': 1
    }
    # 'extended': 1, - полная информация о группах
    if target_id:
        params['user_id'] = target_id

    return get_from_vk_api(method, params)


def get_from_vk_api(method: str, input_params=None):
    """
    Функция получения данных из API VK
    :param method:
    :param input_params:
    :return:
    """
    token, version = config()
    params = {
        'access_token': token,
        'v': version
    }
    if input_params:
        params.update(input_params)
    json_type = 'application/json'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Content-type': json_type
    }
    url = f'https://api.vk.com/method/{method}'
    response = requests.get(url, headers=headers, params=params, timeout=5)
    return response.json().get('response')


if __name__ == '__main__':
    # получение данных о пользователе
    save_data_to_json(user_info(), 'user_info')

    # # получения данных о друзьях
    user_friends = get_friends()
    # pprint(user_friends)
    save_data_to_json(user_friends, 'user_friends')

    # получение данных о группах
    user_group_data = user_group()
    # pprint(user_group_data)
    save_data_to_json(user_group_data, 'user_groups')
#
