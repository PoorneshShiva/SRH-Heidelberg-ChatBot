from flask import Flask, request, jsonify, render_template, redirect
from srh_model import query_engine
from jinja2 import Environment
import queue
import json

app = Flask(__name__)
result_queue = queue.Queue()

conversation_history = []
env = Environment()
env.globals.update(enumerate=enumerate)


@app.route('/')
def index():
    print(conversation_history)
    return render_template('index.html', conversation=conversation_history, enumerate=enumerate)


@app.route('/check', methods=['GET'])
def data():
    json_data = list()
    for index, item in enumerate(conversation_history):
        if index % 2 == 0 or index == 0:
            key = 'sender'
        else:
            key = 'ChatBot'
        json_data.append({key: item})
    return json_data


@app.route('/clear', methods=['POST'])
def clear_the_conversation():
    global conversation_history
    conversation_history = []
    return redirect('/')


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.form
    # if request.form:
    #     request.form['message']
    message = data['message'].lower()  # Convert message to lowercase for case-insensitive matching
    conversation_history.append({'message': str(message)})
    response = query_engine.query(message)
    try:
        print(response['response'])
    except:
        pass
    conversation_history.append({'message': response})
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
