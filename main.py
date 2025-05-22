import json
import os
from typing import Any, Dict
import urllib.error
import urllib.request

from dotenv import load_dotenv

import logic
import export


load_dotenv()


BASE_URL = os.getenv('URL')

URL = (
    f"{BASE_URL}/tasks.task.list?"
    "&select[]=ID&select[]=TITLE&select[]=STATUS&select[]=DEADLINE"
    "&select[]=START_DATE_PLAN&select[]=CREATED_DATE&select[]=RESPONSIBLE_ID"
)


def load_data(url: str) -> Dict[str, Any]:
    """Загружает данные по URL."""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        raise ConnectionError(f"Ошибка при загрузке данных: {e}")


def load_settings(filepath: str = 'config.json') -> Dict[str, Any]:
    """Загружает настройки из JSON файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Ошибка загрузки конфига: {e}")

# Загрузка данных по URL


def main():
    data = load_data(URL)
    settings = load_settings()

    output_data = logic.generate_dates(settings["start_date"], settings["end_date"])

    if settings["availability_status"] == 0:
        output_data = logic.tasks_to_df_no_status(
            output_data, data['result']['tasks'])
    elif settings["availability_status"] == 1:
        output_data = logic.tasks_to_df_with_status(
            output_data, data['result']['tasks'])
    else:
        raise ValueError(
                "availability_status должен быть 0 или 1, получено: "
                f"{settings['availability_status']}"
            )

    if settings["export"] == 0:
        output_data.to_json('tasks.json',
                            orient='records',  # Формат записи
                            force_ascii=False,  # Поддержка кириллицы
                            indent=2)
        print("Файл успешно сохранен: tasks.json")
    elif settings["export"] == 1:
        export.export_to_excel(output_data, "tasks_rep.xlsx")
    else:
        raise ValueError(
            "export должен быть 0 или 1, получено: "
            f"{settings['export']}"
        )


if __name__ == "__main__":
    main()
