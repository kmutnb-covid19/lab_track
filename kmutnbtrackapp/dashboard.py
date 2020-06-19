import datetime
import json
import time


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
    """Check data in json and cast type to datetime"""
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            pass
    return json_dict


def prepare_pie_data(meta_data):
    """Prepare pie chart data before send to template"""
    # ['Task', 'Hours per Day'] เอาไว้ทำอะไรก็ไม่รู้แต่ไม่มีทำกราฟไม่ได้ 55555555
    data = [['Task', 'Hours per Day']]
    for lab_name in meta_data['lab']:
        data.append([lab_name, sum(meta_data['lab'][lab_name].values())])
    return data


def prepare_liner_data(meta_data):
    """Prepare liner chart data before send to template"""
    # format example [new Date(2015, 0, 1), 5]
    duplicate = {}
    data = []
    for lab_name in meta_data['lab']:
        for day in meta_data['lab'][lab_name]:
            if day in duplicate:
                duplicate[day] += meta_data['lab'][lab_name][day]
            else:
                duplicate[day] = meta_data['lab'][lab_name][day]

    for day in duplicate:
        data.append([int(time.mktime(datetime.datetime(int(day.split("/")[0]), int(day.split("/")[1]),
                                                       int(day.split("/")[2])).timetuple())) * 1000,
                     duplicate[day]])
    return data
