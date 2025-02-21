from flask import Flask, request
from google.cloud import datastore
from datetime import datetime

app = Flask(__name__)
client = datastore.Client()

ERROR_RESPONSE = "Invalid Parameter"
MAIN_DATA_KIND = "task2"
COMMAND_HISTORY_KIND = "CommandHistory"
UNDO_HISTORY_KIND = "UndoHistory"

def is_valid_parameter(param):
    return isinstance(param, str) and param.strip() and " " not in param

def set_data(name, value):
    key = client.key(MAIN_DATA_KIND, name)
    entity = datastore.Entity(key=key)
    entity.update({'value': value})
    client.put(entity)

def get_data(name):
    key = client.key(MAIN_DATA_KIND, name)
    return client.get(key)

def delete_data(name):
    key = client.key(MAIN_DATA_KIND, name)
    client.delete(key)

def append_command(command, name, old_value, new_value, kind):
    key = client.key(kind)
    entity = datastore.Entity(key=key)
    entity.update({
        'command': command,
        'name': name,
        'old_value': old_value,
        'new_value': new_value,
        'timestamp': datetime.utcnow()
    })
    client.put(entity)

def pop_command(kind):
    query = client.query(kind=kind)
    query.order = ['-timestamp']
    results = list(query.fetch(limit=1))
    if results:
        entity = results[0]
        client.delete(entity.key)
        return entity['command'], entity['name'], entity['old_value'], entity['new_value']
    return None, None, None, None

@app.route('/set')
def set_variable():
    name = request.args.get('name')
    value = request.args.get('value')
    if is_valid_parameter(name) and is_valid_parameter(value):
        previous_entity = get_data(name)
        old_value = previous_entity['value'] if previous_entity else None
        append_command('SET', name, old_value, value, COMMAND_HISTORY_KIND)
        set_data(name, value)
        return f'{name} = {value}'
    else:
        return ERROR_RESPONSE

@app.route('/get')
def get_variable():
    name = request.args.get('name')
    if is_valid_parameter(name):
        entity = get_data(name)
        return entity['value'] if entity else 'None'
    else:
        return ERROR_RESPONSE

@app.route('/unset')
def unset_variable():
    name = request.args.get('name')
    if is_valid_parameter(name):
        entity = get_data(name)
        if entity:
            append_command('UNSET', name, entity['value'], None, COMMAND_HISTORY_KIND)
            delete_data(name)
            return f'{name} = None'
    else:
        return ERROR_RESPONSE

@app.route('/numequalto')
def numequalto():
    value = request.args.get('value')
    if is_valid_parameter(value):
        query = client.query(kind=MAIN_DATA_KIND)
        query.add_filter('value', '=', value)
        results = list(query.fetch())
        return str(len(results))
    else:
        return ERROR_RESPONSE

@app.route('/undo')
def undo():
    command, name, old_value, new_value = pop_command(COMMAND_HISTORY_KIND)
    if command:
        if command == 'SET':
            if old_value is None:
                delete_data(name)
                append_command('SET', name, old_value, new_value, UNDO_HISTORY_KIND)
                return f'{name} = None'
            else:
                set_data(name, old_value)
                append_command('SET', name, old_value, new_value, UNDO_HISTORY_KIND)
                return f'{name} = {old_value}'
        elif command == 'UNSET':
            set_data(name, old_value)
            append_command('UNSET', name, old_value, new_value, UNDO_HISTORY_KIND)
            return f'{name} = {old_value}'
    else:
        return "NO COMMANDS"

@app.route('/redo')
def redo():
    command, name, old_value, new_value = pop_command(UNDO_HISTORY_KIND)
    if command:
        if command == 'SET':
            set_data(name, new_value)
            append_command('SET', name, old_value, new_value, COMMAND_HISTORY_KIND)
            return f'{name} = {old_value}'
        elif command == 'UNSET':
            delete_data(name)
            append_command('UNSET', name, old_value, new_value, COMMAND_HISTORY_KIND)
            return f'{name} = {old_value}'
    else:
        return "NO COMMANDS"

@app.route('/end')
def end():
    query = client.query(kind=MAIN_DATA_KIND)
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)
    query = client.query(kind=COMMAND_HISTORY_KIND)
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)
    query = client.query(kind=UNDO_HISTORY_KIND)
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)
    return "CLEANED"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)