# Методы сбора и обработки данных из сети Интернет


## Урок 3. Парсинг данных. HTML, Beautiful Soap
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет добавлять только новые вакансии/продукты в вашу базу.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты). То есть цифра вводится одна, а запрос проверяет оба поля.

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
db = client['jobs_db']
```

и коллекции (jobs и duplicates):
```python
jobs = db['jobs']  # вакансии
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

```dz_03_insert_data.pydz_03_insert_data.py``` - сбор данных с сайтов hh.ru и superjob.ru и сохранение в базу данных

```dz_03_read_data.py``` - чтение данных из базы
