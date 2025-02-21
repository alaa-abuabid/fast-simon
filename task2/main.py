from flask import Flask, request
from google.cloud import datastore

app = Flask(__name__)
client = datastore.Client()

ERROR_RESPONSE = "Invalid Parameter"
DATASTORE_KIND_NAME = "task2"

# Stacks to keep track of history and undone commands
command_history_stack = []
undo_history_stack = []

def is_valid_parameter(param):
    return isinstance(param, str) and param.strip() and " " not in param

def set_data(name, value):
    key = client.key(DATASTORE_KIND_NAME, name)
    entity = datastore.Entity(key=key)
    entity.update({'value': value})
    client.put(entity)

def get_data(name):
    key = client.key(DATASTORE_KIND_NAME, name)
    return client.get(key)

def delete_data(name):
    key = client.key(DATASTORE_KIND_NAME, name)
    client.delete(key)


def handle_undo_redo(source_stack, destination_stack):
    if not source_stack:
        return "NO COMMANDS"

    command, name, value = source_stack.pop() # get and remove from source stack
    destination_stack.append(command, name, value) # add the command to the destination stack
    if command == 'SET':
        if value is None:
            delete_data(name)
            return f"{name} = None"
        else:
            set_data(name, value)
            return f"{name} = {value}"
    elif command == 'UNSET':
        set_data(name, value)
        return f"{name} = {value}"

@app.route('/set')
def set_variable():
    name = request.args.get('name')
    value = request.args.get('value')
    if is_valid_parameter(name) and is_valid_parameter(value):
        previous_entity = get_data(name) # we need to get old entity in order to add it to the history stack
        if previous_entity:
            command_history_stack.append(('SET', name, previous_entity['value'])) # set old entity to the command stack before overriding it
        else:
            command_history_stack.append(('SET', name, None)) # set old entity to the command stack before overriding it
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
        entity = get_data(name) # we need to get old entity in order to add it to the history stack
        if entity:
            command_history_stack.append(('UNSET', name, entity['value']))  # set old entity to the command stack before removing it
            delete_data(name)
            return entity['value'] if entity else 'None'
    else:
        return ERROR_RESPONSE

@app.route('/numequalto')
def numequalto():
    value = request.args.get('value')
    if is_valid_parameter(value):
        query = client.query(kind=DATASTORE_KIND_NAME)
        query.add_filter('value', '=', value)
        results = list(query.fetch())
        return str(len(results))
    else:
        return ERROR_RESPONSE

@app.route('/undo')
def undo():
    handle_undo_redo(command_history_stack, undo_history_stack)

@app.route('/redo')
def redo():
    handle_undo_redo(undo_history_stack, command_history_stack)

@app.route('/end')
def end():
    query = client.query(kind=DATASTORE_KIND_NAME)
    keys = [entity.key for entity in query.fetch()]
    client.delete_multi(keys)
    command_history_stack.clear()
    undo_history_stack.clear()
    return "CLEANED"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)