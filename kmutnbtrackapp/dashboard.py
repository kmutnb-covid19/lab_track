import datetime
import json
import time
from datetime import timedelta
from kmutnbtrackapp.views.help import tz


def get_data_metadata():
    """Load metadata file as json"""
    try:
        with open('metadata.json') as metadata_json:
            metadata = json.load(metadata_json, object_hook=date_hook)
    except FileNotFoundError:
        metadata = {"latest time": datetime.datetime.fromtimestamp(0),
                    "lab": {}}

    return metadata


def write_metadata(update_data):
    """Write new data into file metadata"""
    with open('metadata.json', 'w') as json_write:
        json.dump(update_data, json_write, indent=4)


def date_hook(json_dict):
    """Check data in json and cast type to datetime"""
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            pass
        except TypeError:
            pass
    return json_dict


def prepare_pie_data(meta_data):
    """Prepare pie chart data before send to template"""
    # ['Task', 'Hours per Day'] เอาไว้ทำอะไรก็ไม่รู้แต่ไม่มีทำกราฟไม่ได้ 55555555
    data = [['Task', 'Hours per Day']]
    for lab_name in meta_data['lab']:
        data.append([lab_name, sum(meta_data['lab'][lab_name].values())])
    return data


def create_empty_date(start, last):
    date_range = []
    start_date = datetime.datetime(int(start.split("/")[0]), int(start.split("/")[1]), int(start.split("/")[2]))
    last_date = datetime.datetime(int(last.split("/")[0]), int(last.split("/")[1]), int(last.split("/")[2]))
    while start_date <= last_date:
        date_range.append(str(start_date.year) + "/" + str(start_date.month) + "/" + str(start_date.day))
        start_date += timedelta(days=1)
    return date_range


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
    date_list = create_empty_date(list(duplicate.keys())[0], list(duplicate.keys())[-1])
    for day in date_list:
        if day in list(duplicate.keys()):
            data.append([int(time.mktime(datetime.datetime(int(day.split("/")[0]), int(day.split("/")[1]),
                                                           int(day.split("/")[2])).timetuple())) * 1000,
                         duplicate[day]])
        else:
            data.append([int(time.mktime(datetime.datetime(int(day.split("/")[0]), int(day.split("/")[1]),
                                                           int(day.split("/")[2])).timetuple())) * 1000,
                         0])
    data.sort()
    return data


def prepare_single_liner_data(meta_data):
    """Prepare liner chart data before send to template"""
    classify_data = {}
    for lab_name in meta_data["lab"]:
        duplicate = {}
        data = []
        for day in meta_data["lab"][lab_name]:
            if day in duplicate:
                duplicate[day] += meta_data['lab'][lab_name][day]
            else:
                duplicate[day] = meta_data['lab'][lab_name][day]
        date_list = create_empty_date(list(duplicate.keys())[0], list(duplicate.keys())[-1])
        for day in date_list:
            if day in list(duplicate.keys()):
                data.append([int(time.mktime(datetime.datetime(int(day.split("/")[0]), int(day.split("/")[1]),
                                                               int(day.split("/")[2])).timetuple())) * 1000,
                             duplicate[day]])
            else:
                data.append([int(time.mktime(datetime.datetime(int(day.split("/")[0]), int(day.split("/")[1]),
                                                               int(day.split("/")[2])).timetuple())) * 1000,
                             0])
        classify_data[lab_name] = data
    return classify_data


def prepare_room_status(lab, user):
    room_status = {}
    for lab_properties in lab:
        room_status[lab_properties['name']] = {}
        room_status[lab_properties['name']]['max'] = lab_properties['max_number_of_people']
        room_status[lab_properties['name']]['use'] = 0

    on_use_user = user.filter(checkin__lte=datetime.datetime.now(tz),
                              checkout__gte=datetime.datetime.now(tz) + datetime.timedelta(minutes=1))

    for room_name in on_use_user:
        room_status[str(room_name)]['use'] += 1
    return room_status
