# Методы сбора и обработки данных из сети Интернет


## Урок 4. Система управления базами данных MongoDB в Python
Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath.

Структура данных должна содержать:
- название источника;
- наименование новости;
- ссылку на новость;
- дата публикации.

Сложить собранные новости в БД.

Минимум один сайт, максимум - все три

---

Запустить контейнер с MongoDB:
```commandline
docker run -d --name mongo_scrap -p 27017:27017 -v mongodb_scrap:/data/db mongo
```

В файле ```settings.py``` необходимо указать IP-адрес и порт сервера MongoDB:
```python
HOST = '192.168.2.230'  # укажите IP-адрес
PORT = 27017             # укажиите порт (27017 стандартный порт MongoDB)
```

Так же можно указать базу данных (jobs_db):
```python
db = client['news_db']
```

и коллекции (news и duplicates):
```python
news = db['news']  # новости
duplicates = db['duplicates']  # дубликаты
```

Необходимо установить:
```commandline
pip install requests
pip install beautifulsoup4
pip install lxml
pip install pymongo
```

или
```commandline
pip install -r requirements.txt
или
python -m pip install -r requirements.txt
```

```dz_04.py``` - сбор главных новостей с сайтов lenta.ru и news.mail.ru с помощью XPath и сохранение в базу данных

