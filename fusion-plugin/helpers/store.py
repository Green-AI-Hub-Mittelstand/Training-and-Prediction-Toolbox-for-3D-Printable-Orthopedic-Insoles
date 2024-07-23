import json
import os

from ..config import ROOT_DIR
from ..lib import fusion360utils as futil


def loadVariable(variable_name, default_value = None, filename = 'user-config.json'):
    PATH = os.path.join(ROOT_DIR, filename)
    futil.log("loading config from: %s" % PATH )
    try:
        with open(PATH, 'r') as file:
            data = json.load(file)
            return data.get(variable_name, default_value)
    except FileNotFoundError:
        return default_value

def storeVariable(variable_name, variable_value,  filename = 'user-config.json'):
    PATH = os.path.join(ROOT_DIR, filename)
    try:
        with open(PATH, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[variable_name] = variable_value

    with open(PATH, 'w') as file:
        json.dump(data, file, indent=2)