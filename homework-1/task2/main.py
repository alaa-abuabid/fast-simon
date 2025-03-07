from flask import Flask, request
from google.cloud import datastore
from datetime import datetime

app = Flask(__name__)
client = datastore.Client()

ERROR_RESPONSE = "Invalid Parameter"
MAIN_DATA_KIND = "task2"
UNDO_STACK_KIND = "undoStack"
REDO_STACK_KIND = "redoStack"
VARIABLE_HISTORY_KIND = "VariableHistory"

def is_valid_parameter(param):
    return isinstance(param, str) and param.strip() and " " not in param

def set_data(name, value):
    key = client.key(MAIN_DATA_KIND, name)
    entity = datastore.Entity(key=key)
    entity.update({'value': value})
    client.put(entity)
    append_variable_history(name, value)

def get_data(name):
    key = client.key(MAIN_DATA_KIND, name)
    return client.get(key)

def delete_data(name):
    key = client.key(MAIN_DATA_KIND, name)
    client.delete(key)
    append_variable_history(name, None)

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

def append_variable_history(name, value):
    key = client.key(VARIABLE_HISTORY_KIND)
    entity = datastore.Entity(key=key)
    entity.update({
        'name': name,
        'value': value,
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

def discard_data_by_kind(kind):
    query = client.query(kind=kind)
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)

@app.route('/set')
def set_variable():
    name = request.args.get('name')
    value = request.args.get('value')
    if is_valid_parameter(name) and is_valid_parameter(value):
        discard_data_by_kind(REDO_STACK_KIND) # discard redo stack
        previous_entity = get_data(name)
        old_value = previous_entity['value'] if previous_entity else None
        append_command('SET', name, old_value, value, UNDO_STACK_KIND)
        set_data(name, value)
        return f'{name} = {value}'
    else:
        return ERROR_RESPONSE

@app.route('/get')
def get_variable():
    name = request.args.get('name')
    if is_valid_parameter(name):
        # discard_data_by_kind(REDO_STACK_KIND)  # discard redo stack - based on the test this should not remove the redo history
        entity = get_data(name)
        return entity['value'] if entity else 'None'
    else:
        return ERROR_RESPONSE

@app.route('/unset')
def unset_variable():
    name = request.args.get('name')
    if is_valid_parameter(name):
        discard_data_by_kind(REDO_STACK_KIND)  # discard redo stack
        entity = get_data(name)
        if entity:
            append_command('UNSET', name, entity['value'], None, UNDO_STACK_KIND)
            delete_data(name)
            return f'{name} = None'
        else:
            return "not found"
    else:
        return ERROR_RESPONSE

@app.route('/numequalto')
def numequalto():
    value = request.args.get('value')
    if is_valid_parameter(value):
        # discard_data_by_kind(REDO_STACK_KIND)  # discard redo stack - based on the test this should not remove the redo history
        query = client.query(kind=MAIN_DATA_KIND)
        query.add_filter('value', '=', value)
        results = list(query.fetch())
        return str(len(results))
    else:
        return ERROR_RESPONSE

@app.route('/undo')
def undo():
    command, name, old_value, new_value = pop_command(UNDO_STACK_KIND)
    if command:
        if command == 'SET':
            if old_value is None:
                delete_data(name)
                append_command('SET', name, old_value, new_value, REDO_STACK_KIND)
                return f'{name} = None'
            else:
                set_data(name, old_value)
                append_command('SET', name, old_value, new_value, REDO_STACK_KIND)
                return f'{name} = {old_value}'
        elif command == 'UNSET':
            set_data(name, old_value)
            append_command('UNSET', name, old_value, new_value, REDO_STACK_KIND)
            return f'{name} = {old_value}'
    else:
        return "NO COMMANDS"

# The official documentation states that if more than one consecutive REDO command is issued, the original commands should
# be redone in the original order of execution. Additionally, it specifies that if another command is executed after an
# UNDO, the REDO command should do nothing.
# However, after testing with the provided sequences, I found that the REDO command should still work even if GET or
# NUMEQUALTO commands were issued after an UNDO. This is the behavior implemented in the app.
@app.route('/redo')
def redo():
    command, name, old_value, new_value = pop_command(REDO_STACK_KIND)
    if command:
        if command == 'SET':
            set_data(name, new_value)
            append_command('SET', name, old_value, new_value, UNDO_STACK_KIND)
            return f'{name} = {new_value}'
        elif command == 'UNSET':
            delete_data(name)
            append_command('UNSET', name, old_value, new_value, UNDO_STACK_KIND)
            return f'{name} = None'
    else:
        return "NO COMMANDS"

@app.route('/audit')
def variable_history():
    name = request.args.get('name')
    if is_valid_parameter(name):
        query = client.query(kind=VARIABLE_HISTORY_KIND)
        query.add_filter('name', '=', name)
        query.order = ['-timestamp']
        results = list(query.fetch())

        if results:
            history = [f"timestamp | value"]
            history += [
                f"{datetime.utcfromtimestamp(entity['timestamp'].timestamp()).strftime('%Y-%m-%d %H:%M')} | {entity['value'] if entity['value'] is not None else 'None'}"
                for entity in results
            ]
            return f"variable {name} audit\n" + "\n".join(history)
        else:
            return f"variable {name} audit\nNo history found"
    else:
        return ERROR_RESPONSE

@app.route('/end')
def end():
    discard_data_by_kind(MAIN_DATA_KIND)
    discard_data_by_kind(UNDO_STACK_KIND)
    discard_data_by_kind(REDO_STACK_KIND)
    discard_data_by_kind(VARIABLE_HISTORY_KIND)
    return "CLEANED"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)