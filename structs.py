import datetime as dt
from datetime import datetime, timedelta
from typing import Callable, Union, Any



# MultiplePropertyModes are: Linear, Pingpong, and Loop
# MultiplePropertyValue
    # get()  - gets the value. option to decrease times if True
    # getTimes()  - gets the number of times this value should be accessed before moving on
    # isDone()  - returns whether multipleproperty should move on (times > number)
    # times  - the number of times this value has been used
    # reset()  - sets times to 0


class MultiplePropertyValue:
    def __init__(self, value, count=1):
        self.times = 0
        self.value = value
        self.count = count

    def set(self, value):
        self.value = value

    def get(self, decrement=False):
        if decrement:
            self.times += 1
        return self.value

    def get_times(self):
        return self.times

    def is_done(self):
        return self.times >= self.count

    def reset(self):
        self.times = 0

    def __repr__(self):
        return "P{" + str(self.value) + "}"


# MultipleProperty
    # get()  - the current value of the property
    # next()  - moves the current value of the property based on mode
    # getMode()  - gets the current mode
    # getList()  - gets the array of possible property values
    # add()  - adds a new property value to the array of possible property values
    # setMode()  - sets the current mode
    # getIndex()  - gets the index of the current property
    # direction
class MultipleProperty:
    def __init__(self, *values: Union[MultiplePropertyValue, Any]):
        self.properties: list[MultiplePropertyValue] = list(values)
        for i, value in enumerate(self.properties):
            if not isinstance(value, MultiplePropertyValue):
                self.properties[i] = MultiplePropertyValue(value)
        self.index = 0
        self.direction = 1

    @property
    def count(self):
        return len(self.properties)

    def get(self):
        try:
            return self.properties[self.index].get()
        except IndexError:
            return None

    def get_prop(self):
        return self.properties[self.index]

    def next(self):
        self.index = (self.index + 1) % len(self.properties)  # TODO: modes

    def prev(self):
        self.index = (self.index - 1) % len(self.properties)  # TODO: modes

    def get_mode(self):
        pass

    def get_prop_list(self):
        return self.properties

    def get_list(self) -> list[MultiplePropertyValue]:
        return [property.value for property in self.properties]

    def add(self, value):
        self.properties.append(MultiplePropertyValue(value, 1))

    def set(self, value):
        self.properties[self.index].set(value)

    def set_mode(self):
        pass

    def get_index(self):
        return self.index

    @property
    def simple(self):
        return len(self.properties) <= 1

    def __repr__(self):
        return "MultipleProperty" + str(self.get_prop_list())

    def __str__(self):
        return "MultipleProperty" + str(self.get_list())

# list of advanced properties to add to assignments:
    # multiple intervals
    # interval modes
    # multiple due dates
    # due date modes
    # multiple start dates
    # start date modes
    # messages on alert due
    # messages on alert start
    # message alert on due modes
    # message alert on start modes
    # random alert priority index
    # multiple descriptions
    # description modes
    # when to minimize all tabs
    # if should be autoincremented on restart
    # delete when past due
    # add interval to current time when due
    # disable interval when marked as done

#  Suggestion: store properties and have them be called.
#   This would allow for the certain ordering of properties having significance, which could be very powerful (Due Dates --> Due Dates --> Interval --> Due Date --> Interval)

# TODO: make name, desc, etc. protected fields and make getter properties
class BaseAssignment:
    # TODO: add miscellaneous properties and support simple detection for them
    def __init__(self, name: MultipleProperty, description: MultipleProperty = "", start_date: MultipleProperty = None, due_date: MultipleProperty = None,
                 interval: MultipleProperty = None, type: MultipleProperty = "assignment"):
        def try_create_property(obj: Any) -> MultipleProperty:
            return MultipleProperty(obj) if not isinstance(obj, MultipleProperty) else obj

        self._name: MultipleProperty = try_create_property(name)
        self._desc: MultipleProperty = try_create_property(description)
        self._start_date: MultipleProperty = try_create_property(start_date)
        self._due_date: MultipleProperty = try_create_property(due_date)
        self._interval: MultipleProperty = try_create_property(interval)
        self._type: MultipleProperty = try_create_property(type)

    def interval_mprop(self):
        return self._interval

    def push_name(self, name: str):
        self._name.add(name)

    def push_desc(self, desc: str):
        self._desc.add(desc)

    def push_due_date(self, due_date: datetime):
        self._due_date.add(due_date)

    def push_start_date(self, start_date: datetime):
        self._start_date.add(start_date)

    def push_type(self, type: str):
        self._type.add(type)

    def push_interval(self, interval: timedelta):
        self._interval.add(interval)

    @property
    def name(self) -> str:
        return self._name.get()

    @property
    def desc(self) -> str:
        return self._desc.get()

    @property
    def start_date(self) -> Union[datetime, None]:
        return self._start_date.get()

    @start_date.setter
    def start_date(self, value):
        self._start_date.set(value)

    @property
    def due_date(self) -> Union[datetime, None]:
        return self._due_date.get()

    @due_date.setter
    def due_date(self, value):
        self._due_date.set(value)

    @property
    def interval(self) -> Union[timedelta, None]:
        return self._interval.get()

    @interval.setter
    def interval(self, value):
        self._interval.set(value)

    @property
    def type(self) -> str:
        return self._type.get()

    def set_name(self, name: str, index=0):
        self._name.get_prop_list()[index].set(name)

    def set_desc(self, desc, index=0):
        self._desc.get_prop_list()[index].set(desc)

    def set_start_date(self, date, index=0):
        self._start_date.get_prop_list()[index].set(date)

    def set_due_date(self, date, index=0):
        self._due_date.get_prop_list()[index].set(date)

    def set_interval(self, interval, index=0):
        self._interval.get_prop_list()[index].set(interval)

    def set_type(self, type, index=0):
        self._type.get_prop_list()[index].set(type)

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

    # Simple assignments have only one value for each of their properties.
    def is_simple(self) -> bool:
        return self._name.simple \
           and self._desc.simple \
           and self._start_date.simple \
           and self._due_date.simple \
           and self._interval.simple \
           and self._type.simple


    @property
    def is_persistent(self) -> bool:
        return self.interval is not None or not self.is_simple()

    def invoke_persistence(self):
        # should never be triggered because of alerts main sloop
        while (self.due_date or self.start_date) < datetime.now():
            if self.has_start_date:
                self.start_date += self.interval
            if self.has_due_date:
                self.due_date += self.interval
            self._interval.next()
        self._desc.next()
        self._name.next()
        self._start_date.next()
        self._due_date.next()
        self._type.next()
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

    def current(self):
        if self.has_start_date:
            if self.has_due_date:
                return self.start_date < datetime.now() < self.due_date
            return self.start_date < datetime.now()
        elif self.has_due_date:
            return datetime.now() < self.start_date
        return False


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

        self.in_progress: list[BaseAssignment] = []
        self.completed = []

    def get_current_assignments(self) -> list[BaseAssignment]:
        current = []
        for assignment in self.in_progress:
            if assignment.current():
                current.append(assignment)
        return current

    def any_current_assignments(self):
        for assignment in self.in_progress:
            if assignment.current():
                return True
        return False

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
            if candidate > datetime.now() and (not closest or candidate < closest):
                closest = candidate
        return closest

    def get_closest_start_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            if not assignment.has_start_date:
                continue
            candidate = assignment.start_date
            if candidate > datetime.now() and (not closest or candidate < closest):
                closest = candidate
        return closest

    def get_closest_due_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            if not assignment.has_due_date:
                continue
            candidate = assignment.due_date
            if candidate > datetime.now() and (not closest or candidate < closest):
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
            key = lambda a: a.due_date or datetime(1970, 1, 1)
        elif type == BY_START_DATE:
            key = lambda a: a.start_date or datetime(1970, 1, 1)
        elif type == BY_CLOSEST_DATE:
            key = lambda a: a.closer_date or datetime(1970, 1, 1)
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

#  subtasks
#  option to merge assignments into a single assignment containing two or more subtasks (action)
