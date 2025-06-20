from flask import Flask, jsonify, request
import json
from typing import Any, Dict
import main
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_settings(filepath: str = 'server_cfg.json') -> Dict[str, Any]:
    """Загружает настройки из JSON файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Ошибка загрузки конфига: {e}")

# Маршрут для получения JSON
@app.route('/api/data', methods=['GET'])
def get_data():
    date_start = request.args.get('dateStart')
    date_end = request.args.get('dateEnd')

    data = main.generate(date_start, date_end)
    json_data = data.to_dict(orient='records')
    return jsonify(json_data)

# Маршрут для получения JSON
@app.route('/api/users', methods=['GET'])
def get_users():
    data = main.generate_users()
    json_data = data
    return jsonify(json_data)

if __name__ == '__main__':
    settings = load_settings()
    app.run(host=settings["host"], port=settings["port"], debug=settings["debug"])