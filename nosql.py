"""NoSQL database written in Python."""
from __future__ import print_function

# Standard library imports
import socket

TYPE_CONVERSION = {
    'INT': int,
    'STRING': str,
    'LIST': list,
    }

HOST = 'localhost'
PORT = 50505
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
STATS = {
    'PUT': {'success': 0, 'error': 0},
    'GET': {'success': 0, 'error': 0},
    'GETLIST': {'success': 0, 'error': 0},
    'PUTLIST': {'success': 0, 'error': 0},
    'INCREMENT': {'success': 0, 'error': 0},
    'APPEND': {'success': 0, 'error': 0},
    'DELETE': {'success': 0, 'error': 0},
    'STATS': {'success': 0, 'error': 0},
    }


def update_stats(command, success):
    """Update the STATS dict with info about if executing
    *command* was a *success*."""
    if success:
        STATS[command]['success'] += 1
    else:
        STATS[command]['error'] += 1


def handle_put(key, value):
    """Return a tuple containing True and the message
    to send back to the client."""
    DATA[key] = value
    return (True, 'Key [{}] set to [{}]'.format(key, value))


def handle_get(key):
    """Return a tuple containing True if the key exists and the message
    to send back to the client."""
    if key not in DATA:
        return(False, 'ERROR: Key [{}] not found'.format(key))
    else:
        return(True, DATA[key])


def handle_putlist(key, value):
    """Return a tuple containing True if the command succeeded and the message
    to send back to the client."""
    return handle_put(key, value)


def handle_getlist(key):
    """Return a tuple containing True if the key contained a list and
    the message to send back to the client."""
    return_value = exists, value = handle_get(key)
    if not exists:
        return return_value
    elif not isinstance(value, list):
        return (
            False,
            'ERROR: Key [{}] contains non-list value ([{}])'.format(key, value)
            )
    else:
        return return_value


def handle_increment(key):
    """Return a tuple containing True if the key's value could be incremented
    and the message to send back to the client."""
    return_value = exists, value = handle_get(key)
    if not exists:
        return return_value
    elif not isinstance(value, int):
        return (
            False,
            'ERROR: Key [{}] contains non-int value ([{}])'.format(key, value)
            )
    else:
        DATA[key] = value + 1
        return (True, 'Key [{}] incremented'.format(key))


def handle_append(key, value):
    """Return a tuple containing True if the key's value could be appended to
    and the message to send back to the client."""
    return_value = exists, value = handle_get(key)
    if not exists:
        return return_value
    elif not isinstance(value, list):
        return (
            False,
            'ERROR: Key [{}] contains non-list value ([{}])'.format(key, value)
            )
    else:
        DATA[key].append(value)
        return (True, 'Key [{}] had value [{}] appended'.format(key, value))


def handle_delete(key):
    """Return a tuple containing True if the key could be deleted and
    the message to send back to the client."""
    if key not in DATA:
        return (
            False,
            'ERROR: Key [{}] not found and could not be deleted'.format(key)
            )
    else:
        del DATA[key]


def handle_stats():
    """Return a tuple containing True and the contents of the STATS dict."""
    return (True, str(STATS))

COMMAND_HANDLERS = {
    'PUT': handle_put,
    'GET': handle_get,
    'GETLIST': handle_getlist,
    'PUTLIST': handle_putlist,
    'INCREMENT': handle_increment,
    'APPEND': handle_append,
    'DELETE': handle_delete,
    'STATS': handle_stats,
    }
DATA = {}


def parse_message(data):
    """Return a tuple contianing the command, the key, and (optionally) the
    value cast to the appropriate type."""
    command, key, value, value_type = data.strip().split(';')
    if value:
        if value_type == 'LIST':
            value = value.split(',')
        else:
            value = TYPE_CONVERSION[value_type](value)
    else:
        value = None
    return command, key, value


def main():
    """Main entry point for script."""
    SOCKET.bind((HOST, PORT))
    SOCKET.listen(1)
    while 1:
        connection, address = SOCKET.accept()
        print('New connection from [{}]'.format(address))
        data = connection.recv(4096).decode()
        command, key, value = parse_message(data)
        if command == 'STATS':
            response = handle_stats()
        elif command in (
            'GET',
            'GETLIST',
            'INCREMENT',
            'DELETE'
                ):
            response = COMMAND_HANDLERS[command](key)
        elif command in (
            'PUT',
            'PUTLIST',
                ):
            response = COMMAND_HANDLERS[command](key, value)
        else:
            response = (False, 'Unknown command type [{}]'.format(command))
        update_stats(command, response[0])
        connection.sendall('{};{}'.format(response[0], response[1]))
        connection.close()


if __name__ == '__main__':
    main()
