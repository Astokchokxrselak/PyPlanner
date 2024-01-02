from structs import BaseAssignment
import datetime

ONE = 0
ALL = 1


class Action:  # lawsuit
    def __init__(self, name, effect, target, func):
        self.name = name
        self.effect = effect
        self.target = target
        self.func = func
        self.parameters = []

    def set_parameters(self, *args):
        self.parameters = args

    def run(self, assignment=None):
        self.func(assignment, *self.parameters)


def delay_assignment(assignment: BaseAssignment, amount: datetime.timedelta):
    assignment.start_date += amount
    assignment.due_date += amount
