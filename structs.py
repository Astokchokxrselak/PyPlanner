import datetime


class BaseAssignment:
    def __init__(self, name: str, description: str, start_date: datetime = None, due_date: datetime = None,
                 increment: datetime = None, type: str = None):
        self.name = name
        self.desc = description
        self.start_date = start_date
        self.due_date = due_date
        self.date_increment = increment
        self.type = type or "assignment"

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
        return self.date_increment is not None

    def time_to_due_date(self) -> int:
        return (datetime.datetime.now() - self.due_date).seconds

    def time_to_start_date(self) -> int:
        return (datetime.datetime.now() - self.start_date).seconds

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


class Group:
    def __init__(self, name, description, conditions):
        self.name = name
        self.desc = description
        self.conds = conditions

        self.in_progress = []
        self.completed = []

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
            if not closest or candidate > closest:
                closest = candidate
        return closest

    def get_closest_start_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            candidate = assignment.start_date
            if not closest or candidate > closest:
                closest = candidate
        return closest

    def get_closest_due_date(self):
        closest = None
        for a in self.in_progress:
            assignment: BaseAssignment = a
            candidate = assignment.due_date
            if not closest or candidate > closest:
                closest = candidate
        return closest


groups: list[list['Group'], list['Group']] = [[], []]  # active groups  :  inactive groups


def active_groups():
    return groups[0]


def inactive_groups():
    return groups[1]

