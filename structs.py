from datetime import datetime, timedelta
from typing import Callable


class BaseAssignment:
    def __init__(self, name: str, description: str = "", start_date: datetime = None, due_date: datetime = None,
                 interval: timedelta = None, type: str = None):
        self.name = name
        self.desc = description or ""
        self.start_date = start_date
        self.due_date = due_date
        self.interval = interval

        self.type = type or "assignment"

    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.desc = desc

    def set_start_date(self, date):
        self.start_date = date

    def set_due_date(self, date):
        self.due_date = date

    def set_interval(self, interval):
        self.interval = interval

    def set_type(self, type):
        self.type = type

    def __repr__(self):
        return f"Assignment(D:{self.due_date},S:{self.start_date},I:{self.interval})"

    @property
    def due_or_start_date(self):
        return self.due_date or self.start_date

    @property
    def has_description(self) -> bool:
        return bool(self.desc)

    @property
    def has_name(self) -> bool:
        return bool(self.has_name)

    @property
    def has_start_date(self) -> bool:
        return self.start_date is not None

    @property
    def has_due_date(self) -> bool:
        return self.due_date is not None

    @property
    def is_persistent(self) -> bool:
        return self.interval is not None

    def invoke_persistence(self):
        # should never be triggered because of alerts main sloop
        while (self.due_date or self.start_date) < datetime.now():
            if self.has_start_date:
                self.start_date += self.interval
            if self.has_due_date:
                self.due_date += self.interval
        #  TODO: perhaps give the option to have interval be added to the current time instead?

    def time_to_due_date(self) -> int:
        if not self.has_due_date:
            return -1
        if datetime.now() > self.due_date:
            return 0
        return (datetime.now() - self.due_date).seconds

    def time_to_start_date(self) -> int:
        if not self.has_start_date:
            return -1
        if datetime.now() > self.start_date:
            return 0
        return (datetime.now() - self.start_date).seconds

    @property
    def closer_date(self) -> datetime:
        has_dd, has_sd = self.has_due_date, self.has_start_date
        if not has_dd and not has_sd:
            return None
        if has_dd and has_sd:
            if self.time_to_due_date() < self.time_to_start_date():
                return self.start_date
            else:
                return self.due_date
        else:
            return self.due_date or self.start_date

# Sorting Modes
names = ["Dont Sort", "By Name", "By Due Date", "By Start Date", "By Closest Date"]
UNSORTED = 0
BY_NAME = 1
BY_DUE_DATE = 2
BY_START_DATE = 3
BY_CLOSEST_DATE = 4
SORT_COUNT = 5
class Group:
    def __init__(self, name, description, conditions):
        self.name = name
        self.desc = description or ""
        self.conds = conditions

        self.in_progress = []
        self.completed = []

    @property
    def in_progress_count(self):
        return len(self.in_progress)
    @property
    def assignment_count(self):
        return len(self.in_progress) + len(self.completed)

    def add_assignment(self, assignment: BaseAssignment):
        self.in_progress.append(assignment)

    def get_closest_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            candidate = assignment.closer_date
            if not closest or candidate < closest:
                closest = candidate
        return closest

    def get_closest_start_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            if not assignment.has_start_date:
                continue
            candidate = assignment.start_date
            if not closest or candidate > closest:
                closest = candidate
        return closest

    def get_closest_due_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            if not assignment.has_due_date:
                continue
            candidate = assignment.due_date
            if not closest or candidate > closest:
                closest = candidate
        return closest

    def remove_assignment_at(self, index):
        del self.in_progress[index]

    def in_progress_sorted(self, type: int, descending=False):
        if type == UNSORTED:
            return self.in_progress
        key: Callable = None
        if type == BY_NAME:
            key = lambda a: a.name
        elif type == BY_DUE_DATE:
            key = lambda a: a.due_date or -1
        elif type == BY_START_DATE:
            key = lambda a: a.start_date or -1
        elif type == BY_CLOSEST_DATE:
            key = lambda a: a.closer_date or -1
        assignments = self.in_progress[:]
        assignments.sort(key=key, reverse=descending)
        return assignments

    def __repr__(self):
        return "Group<" + self.name + ">"


groups: list[list['Group'], list['Group']] = [[], []]  # active groups  :  inactive groups


def active_groups():
    return groups[0]


def inactive_groups():
    return groups[1]

# todo: make a Menu class
# has a setup function that uses the same stuff, but the other
# things are automatically performed (clear, pop-check, etc.)


def increment_all_persistent():
    for group in active_groups():
        for a in group.in_progress:
            assignment: BaseAssignment = a
            if assignment.is_persistent:
                assignment.invoke_persistence()
