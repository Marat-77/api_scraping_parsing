"""
Методы сбора и обработки данных из сети Интернет
Урок 1. Основы клиент-серверного взаимодействия. Работа с API.
API GitHub
"""

# Методы сбора и обработки данных из сети Интернет
# Урок 1. Основы клиент-серверного взаимодействия. Работа с API.
# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

from typing import Any
import json
import requests


def get_user_repos(user_name: str) -> list[dict[str, Any]] | None:
    """
    Получение списка репозиториев пользователя user_name
    :param user_name: str - имя пользователя сервиса ГитХаб
    :return: list | None - список репозиториев или None
    """
    url = f'https://api.github.com/users/{user_name}/repos'
    json_type = 'application/json'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Content-type': json_type
    }
    response = requests.get(url, headers=headers, timeout=5)
    if response.ok:
        response_json = response.json()
        # print(type(response_json))
        # print(len(response_json))
        list_repos = []
        for i in response_json:
            i_dict = {
                'name': i.get('name'),
                'full_name': i.get('full_name'),
                'description': i.get('description'),
                'html_url': i.get('html_url'),
                'language': i.get('language'),
                'allow_forking': i.get('allow_forking'),
                'visibility': i.get('visibility')
            }
            list_repos.append(i_dict)

        result = list_repos
    else:
        result = None

    return result


def save_list_to_json(input_data):
    """
    Функция сохранения полученных данных в файл json.
    :param input_data:
    :return:
    """
    print()
    with open('git_data.json', 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=2, ensure_ascii=False)


def main():
    """
    main function
    :return:
    """
    user_name = 'kubernetes'
    data = get_user_repos(user_name)
    save_list_to_json(data)


if __name__ == '__main__':
    main()
