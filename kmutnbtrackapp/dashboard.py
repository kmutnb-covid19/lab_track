import datetime
import json


def get_data_metadata():
    """Load metadata file as json"""
    try:
        with open('metadata.json') as metadata_json:
            last_modify = json.load(metadata_json, object_hook=date_hook)
    except:
        last_modify = {}
    return last_modify


def write_metadata(update_data):
    """Write new data into file metadata"""
    with open('metadata.json', 'w') as json_write:
        json.dump(update_data, json_write, indent=4)


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            pass
    return json_dict
