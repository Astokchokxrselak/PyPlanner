import json

import structs

import os

from typing import Union

from datetime import datetime, timedelta

"""
Assignments are saved in a JSON format to be easily readable and editable in any text editor.
"name": {
    "description": string,
    "startdate": {"Y": int, "M": int, "D": int, "h": int, "m": int, "s": int},
    "duedate": {"Y": int, "M": int, "D": int, "h": int, "m": int, "s": int},
    "increment": {"D": int, "h": int, "m": int, "s": int}
}

TODO: live resaving and reloading of saved plans

"""


statedata = {
    "groups": {}
}

if not os.path.exists("plans"):
    os.mkdir("plans")
with open("plans/plan1.json", 'a+') as js:
    js.seek(0)
    jsons = js.read(-1)
    if not jsons:
        js.write(jsons := '{"groups": {}}')
    statedata = json.loads(jsons)


def save_assignment(assignment: structs.BaseAssignment, group: Union[structs.Group, str]):
    assignment_dict = {}
    if assignment.has_description:
        assignment_dict["description"] = assignment.desc
    if assignment.has_start_date:
        assignment_dict["startdate"] = datetime_to_dict(assignment.start_date)
    if assignment.has_due_date:
        assignment_dict["duedate"] = datetime_to_dict(assignment.due_date)
    if assignment.is_persistent:
        assignment_dict["interval"] = timedelta_to_dict(assignment.interval)
    gname = group.name if isinstance(group, structs.Group) else group
    statedata["groups"].setdefault(gname, {})
    statedata["groups"][gname][assignment.name] = assignment_dict

    with open("plans/plan1.json", 'w+') as jsn:
        jsn.write(json.dumps(statedata))


def save_group(group: structs.Group):
    for assignment in group.in_progress:
        save_assignment(assignment, group)

    #  for assignment in group.completed:
    #      save_assignment(assignment, group)


def save_all():
    global statedata
    statedata = {
        "groups": {}
    }

    for group in structs.active_groups():
        save_group(group)

    for group in structs.inactive_groups():
        save_group(group)


def dict_to_datetime(d: dict) -> datetime:
    return datetime(d["Y"], d["M"], d["D"], d["h"], d["m"], d["s"])


def dict_to_timedelta(d: dict) -> timedelta:
    return timedelta(weeks=d["W"], days=d["D"], hours=d["h"], minutes=d["m"], seconds=d["s"])


def datetime_to_dict(dt: datetime):
    return {"Y": dt.year, "M": dt.month, "D": dt.day, "h": dt.hour, "m": dt.minute, "s": dt.second}


def timedelta_to_dict(td: timedelta):
    days = td.days
    weeks = days // 7
    days = days % 7

    seconds = td.seconds
    hours = seconds // 3600
    seconds = seconds % 3600

    minutes = seconds // 60
    seconds = seconds % 60

    return {"W": weeks, "D": days, "h": hours, "m": minutes, "s": seconds}


def load_group(group_name: str, g: dict):
    group = structs.Group(group_name, None, None)
    structs.active_groups().append(group)
    for title, a in g.items():
        a: dict = a

        description = ""
        if "description" in a:
            description = a["description"]

        startdate, duedate = None, None
        if "startdate" in a:
            startdate = dict_to_datetime(a["startdate"])
        if "duedate" in a:
            duedate = dict_to_datetime(a["duedate"])

        increment = None
        if "interval" in a:
            increment = dict_to_timedelta(a["interval"])

        type = ""
        if "type" in a:
            type = a["type"]

        assignment = structs.BaseAssignment(title, description, startdate, duedate, increment, type)
        group.add_assignment(assignment)


def load_all():
    for group_name, group in statedata["groups"].items():
        load_group(group_name, group)
