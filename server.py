from flask import Flask, jsonify, request
import json
import main

app = Flask(__name__)


JSON_FILE = "tasks.json"

def load_data():
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"error": "File not found"}, 404
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}, 500


# Маршрут для получения JSON
@app.route('/api/data', methods=['GET'])
def get_data():
    date_start = request.args.get('dateStart')
    date_end = request.args.get('dateEnd')
    print(date_end)
    data = main.generate(date_start, date_end)
    json_data = data.to_dict(orient='records')
    return jsonify(json_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)