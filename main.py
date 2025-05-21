import urllib.request
import json
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from collections import defaultdict

load_dotenv()

URL = os.getenv('URL') + ("/tasks.task.list?&select[]=ID&select[]=TITLE&select["
                          "]=DEADLINE&select[]=START_DATE_PLAN&select[]=CREATED_DATE&select[]=RESPONSIBLE_ID")

# Загрузка данных по URL
with urllib.request.urlopen(URL) as response:
    data = json.loads(response.read().decode('utf-8'))


def generate_dates(start_date, end_date):
    """
    Генерирует DataFrame с датами в указанном диапазоне.

    Параметры:
        start_date (str): Начальная дата в формате "YYYY.MM.DD".
        end_date (str): Конечная дата в формате "YYYY.MM.DD".

    Возвращает:
        pd.DataFrame: DataFrame с колонкой "Дата".
    """
    start = datetime.strptime(start_date, "%Y.%m.%d")
    end = datetime.strptime(end_date, "%Y.%m.%d")

    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime("%Y.%m.%d"))
        current_date += timedelta(days=1)

    return pd.DataFrame({"Дата": date_list})


def add_tasks_to_df(df, tasks_data):
    """
    Добавляет задачи в DataFrame, объединяя их по датам.
    Если на одну дату несколько задач — они добавляются в список.

    Параметры:
        df (pd.DataFrame): Исходный DataFrame с колонкой "Дата"
        tasks_data (list): Список словарей с задачами (каждый в формате task_data)

    Возвращает:
        pd.DataFrame: Модифицированный DataFrame с колонками для каждого работника
    """
    # Создаём временную структуру для хранения задач
    tasks_dict = defaultdict(lambda: defaultdict(list))

    # Обрабатываем все задачи
    for task in tasks_data:
        employee_name = task["responsible"]["name"]
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%dT%H:%M:%S%z")
        created_date = datetime.strptime(task["createdDate"], "%Y-%m-%dT%H:%M:%S%z")

        # Добавляем задачу для каждой даты в диапазоне
        current_date = created_date.date()
        while current_date <= deadline.date():
            date_str = current_date.strftime("%Y.%m.%d")
            tasks_dict[date_str][employee_name].append(task["title"])
            current_date += timedelta(days=1)

    # Добавляем данные в DataFrame
    for employee in set(emp for tasks in tasks_dict.values() for emp in tasks):
        df[employee] = df["Дата"].apply(
            lambda x: tasks_dict[x].get(employee, None)
        )

    return df


if __name__ == "__main__":
    # Генерируем даты
    output_data = generate_dates("2025.05.01", "2025.06.10")

    output_data = add_tasks_to_df(output_data, data['result']['tasks'])

    output_data.to_json('tasks.json',
                        orient='records',  # Формат записи
                        force_ascii=False,  # Поддержка кириллицы
                        indent=2)  # Красивое форматирование
