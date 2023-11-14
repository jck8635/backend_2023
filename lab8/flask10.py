#!/usr/bin/python3

from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

def calculate(arg1, op, arg2):
    if op == '+':
        return arg1 + arg2
    elif op == '-':
        return arg1 - arg2
    elif op == '*':
        return arg1 * arg2
    else:
        return None

@app.route('/<int:arg1>/<string:op>/<int:arg2>', methods=['GET'])
def calculate_get(arg1, op, arg2):
    result = calculate(arg1, op, arg2)
    if result is not None:
        return jsonify({'result': result}), 200
    else:
        return jsonify({'error': '비정상적 입력'}), 400

@app.route('/', methods=['POST'])
def calculate_post():
    data = request.get_json()
    arg1 = data.get('arg1', 0)
    op = data.get('op', '')
    arg2 = data.get('arg2', 0)
    
    result = calculate(arg1, op, arg2)
    if result is not None:
        return jsonify({'result': result}), 200
    else:
        return jsonify({'error': '비정상적 입력'}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=19171)