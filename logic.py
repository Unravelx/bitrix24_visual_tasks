from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List

import pandas as pd


def generate_dates(start_date: str, end_date: str) -> pd.DataFrame:
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


def tasks_to_df_no_status(df :pd.DataFrame, tasks_data: List[Dict]) -> pd.DataFrame:
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


def tasks_to_df_with_status(df: pd.DataFrame, tasks_data: [List[Dict]]) -> pd.DataFrame:
    """
    Добавляет задачи в формате словаря {"Название": "Статус"} в DataFrame

    Параметры:
        df (pd.DataFrame): Исходный DataFrame с колонкой "Дата"
        tasks_data (list): Список задач с полями:
            - title (название)
            - status (код статуса)
            - deadline, createdDate (даты)
            - responsoble (ответственный)
    """
    # Словарь для хранения: дата -> сотрудник -> {задача: статус}
    tasks_dict = defaultdict(lambda: defaultdict(dict))

    for task in tasks_data:
        employee = task["responsible"]["name"]
        task_name = task["title"]
        status = task["status"]

        # Обработка временного диапазона
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%dT%H:%M:%S%z")
        created = datetime.strptime(task["createdDate"], "%Y-%m-%dT%H:%M:%S%z")

        current_date = created.date()
        while current_date <= deadline.date():
            date_str = current_date.strftime("%Y.%m.%d")
            tasks_dict[date_str][employee][task_name] = status
            current_date += timedelta(days=1)

    # Добавляем данные в DataFrame
    for employee in {emp for tasks in tasks_dict.values() for emp in tasks}:
        df[employee] = df["Дата"].apply(
            lambda x: tasks_dict[x].get(employee, {})
        )

    return df
