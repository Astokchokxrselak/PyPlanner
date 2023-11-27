from typing import Union, Callable
import win10toast
import win32api

from msvcrt import getwch as inputkey, getch

from datetime import datetime

from math import ceil

import sys, getpass

import os
clear = lambda: os.system('cls')


# todo: print warning origin's position
def printwarn(*args):
    print("WARNING:", *args)

def put(*args):
    print(*args, end="")

"""
win32api.MessageBeep(0x00000040)
win32api.MessageBox(None, "You are to begin the assignment \"{0}\" right now. Change the due date if you believe this is a mistake.".format("Blow up the tristate area"), "Alert", 0)

toaster = win10toast.ToastNotifier()
toaster.show_toast("Random Alert", "This is a random alert reminding you to complete the task \"{0}\" if you are not already in the process of doing so.".format("Blow up the tristate area"),
                   "alert.ico")
"""


def count_breaks(string: str):
    return string.count('\n') - (string[-1] == '\n')


BOX_BORDER_H, BOX_BORDER_V = '=', '|'


class Box:
    # THIS IS NOT A CLEAR GRID FUNCTION
    # THIS REASSEMBLES THE BOX MATRIX
    # TODO: CLEAR_GRID METHOD
    def reset_grid(self):
        for i in range(self.true_h):
            self.grid.append([])
            for j in range(self.true_w):
                self.grid[i].append(' ')
                if i in (0, self.true_h - 1):
                    if j not in (0, self.true_w - 1):
                        self.grid[i][j] = BOX_BORDER_H
                elif j in (0, self.true_w - 1):
                    self.grid[i][j] = BOX_BORDER_V

    def set_vborder(self, ch):
        for y in range(1, self.true_h - 1):
            self.grid[y][0] = self.grid[y][self.true_w - 1] = ch
        return self

    def set_hborder(self, ch):
        for x in range(1, self.true_w - 1):
            self.grid[0][x] = self.grid[self.true_h - 1][x] = ch
        return self

    def set_border(self, ch):
        self.set_vborder(ch)
        self.set_hborder(ch)
        return self

    # w - the width of the container, h - the height of the container (empty for square container)
    def __init__(self, w, h=-1, **kwargs):
        self.grid = []

        if h < 0:
            h = w
        self.w, self.h = w, h

        self.reset_grid()
        self.texts = {}

        self.marginx = kwargs.get('marginx', -1)

    @property
    def true_h(self):
        return self.h + 2

    @property
    def true_w(self):
        return self.w + 2

    def place_text(self, text: str, position: tuple):
        # self.texts[position] = text
        self.replace_text(text, position)
        pass

    def replace_text(self, text: str, position: tuple):
        self.texts[position] = text

    def place_hcenter_text(self, text, y: int = -1, *args: [str, int]):
        if y < 0:
            y = self.h // 2
        pos = (y, self.w // 2 - len(text) // 2 + 1)
        self.texts[pos] = text
        for i in range(0, len(args), 2):
            self.place_hcenter_text(args[i], args[i + 1])
        if not self.w % 2 and len(text) % 2:
            printwarn("Text with odd length cannot be hcentered on a container with even width", pos)
        if not len(text) % 2 and self.w % 2:
            printwarn("Text with even length cannot be hcentered on a container with odd width", pos)
    def place_vcenter_text(self, text, x: int = -1, *args: [str, int]):
        if not self.h % 2 and len(text) % 2:
            printwarn("Text with odd length cannot be vcentered on a container with even height")
        if not len(text) % 2 and self.h % 2:
            printwarn("Text with even length cannot be vcentered on a container with odd height")
        if x < 0:
            x = self.w // 2
        offset_y = count_breaks(text) // 2 * 2
        self.texts[(self.h // 2 - offset_y, x)] = text
        for i in range(0, len(args), 2):
            self.place_vcenter_text(args[i], args[i + 1])

    def place_center_text(self, text: str):
        break_count = count_breaks(text)
        if self.h % 2 != self.w % 2:
            printwarn("Text cannot be centered on a container with dimensions of unequal parity")
        elif len(text) % 2 != self.w % 2\
                or (break_count + 1) % 2 != self.h % 2:  # + 1 indicates number of lines
            printwarn("Text with unequal parity to dimensions of container cannot be centered")
        offset_y = count_breaks(text) // 2

        line_length = len(text) if not break_count else text.index('\n')
        # TODO: find the longest line instead of the first line
        self.texts[(ceil(self.h / 2) - offset_y, self.w // 2 - line_length // 2 + 1)] = text

    def place_vbar(self, x, *xs):
        self.place_text('|\n' * self.h, (1, x + 1))
        for h in xs:
            self.place_vbar(h)

    def place_hbar(self, y: int, *ys: int):
        self.place_text('-' * self.w, (y + 1, 1))
        for v in ys:
            self.place_hbar(v)

    def place_box(self, w: int, h: int, position: tuple, *whps: [int, int, tuple], **boxkwargs) -> Union[
        list['Box'], 'Box']:
        box = Box(w, h, **boxkwargs)
        self.place_text(box, position)

        if not whps:
            return box
        else:
            boxes = [box]
            for i in range(0, len(whps), 3):
                nbox = self.place_box(whps[i], whps[i + 1], whps[i + 2])
                boxes.append(nbox)
            return boxes

    def bake(self):
        # ensure that a line break is inserted in the middle for text
        # whose length is greater than half of the container's width

        debug = is_trigger(DEBUG)
        for p in self.texts:
            t = self.texts[p]
            is_box = isinstance(t, Box)
            if is_box:
                t = str(t.bake())
            if debug:
                t = '*' + t[1:]
            y, x = yi, xi = p
            for i in range(len(t)):
                ch = t[i]
                if debug and ch == ' ':
                    chdex = i % (10 + 25)
                    if chdex < 10:
                        ch = str(chdex % 10)
                    else:
                        ch = chr(chdex - 10 + ord('A'))
                if ch == '\n':
                    x = xi
                    y += 1
                    continue

                # print(t[:i])
                self.grid[y][x] = ch
                # arbitrary wrap logic
                if self.marginx > -1 and not is_box and x >= self.w - self.marginx:
                    x = xi
                    y += 1
                    continue

                # word wrap logic
                """
                if ch == ' ':
                    ni = 1
                    while i + ni < len(t) and t[i + ni] != ' ':
                        ni += 1
                    if x + ni >= self.w - 1:
                        x = xi
                        y += 1
                        continue
                """
                x += 1
        return self

    def loadup(self, object: Union['Group', 'BaseAssignment'], pn: tuple = (1, 2), pd: tuple = (2, 2), **misc):
        # todo: verification of loaded strings based on line breaks
        self.marginx = 1
        if isinstance(object, Group):
            group = object
            max_desc_size = (self.w - 2) * (self.h - 1)
            desc = group.desc
            if len(desc) - desc.count('\n') > max_desc_size:  # .h - 1 is for the title (should be one line)
                # TODO: support for multiline titles
                group.desc = desc[:max_desc_size - 3] + "..."  # ellipsis
            output: str = group.name + "\n" + group.desc + "\nClosest Due Date: " + str(group.get_closest_due_date()) + "\nClosest Start Date: " + str(group.get_closest_start_date())
            # desc should be the only multiline element in the box
            # self.h = ceil(len(group.desc) / self.w) + output.count('\n')

            # self.reset_grid()

            self.place_text(output, pn)
        elif isinstance(object, BaseAssignment):
            assignment = object
            if assignment.has_description:
                max_desc_size = (self.w - 2) * (self.h - 1)
                desc = assignment.desc
                if len(desc) - desc.count('\n') > max_desc_size:  # .h - 1 is for the title (should be one line)
                    # TODO: support for multiline titles
                    assignment.desc = desc[:max_desc_size - 3] + "..."  # ellipsis
            self.place_text(assignment.name + '\n' + assignment.desc, pn)

    def __repr__(self):
        string = ""
        for r in self.grid:
            string += "".join(r) + "\n"
        return string

    def __str__(self):
        return self.__repr__()


def get_box(w, h):
    box = Box(w, h)
    return box


# Assignments are modular and customized

# Assignment: Has a Due Date, a Start Date.
# Note: Has no Due Date, has no Start Date.
# Reminder: Has a Start Date
# Persistent: Has a Due Date, a Start Date. Due Date increments by a certain amount.

class BaseAssignment:
    def __init__(self, name: str, description: str, start_date: datetime = None, due_date: datetime = None,
                 increment: datetime = None):
        self.name = name
        self.desc = description
        self.start_date = start_date
        self.due_date = due_date
        self.date_increment = increment

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

    def time_to_due_date(self):
        return datetime.now() - self.due_date

    def time_to_start_date(self):
        return datetime.now() - self.start_date

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


def state(string: str, val: int = None):
    if val is None:
        return STATE_COMMANDS[string]
    if isinstance(val, int):
        STATE_COMMANDS[string] = val


def is_state(string: str, val: int):
    return STATE_COMMANDS[string] == val


MSIDE_LEFT, MSIDE_RIGHT = -1, 1
MSIDE_UNDECIDED = 0

MINDEX_START = 0
def reset_menu_selection():
    state(MSIDE, MSIDE_UNDECIDED)
    state(MINDEX, MINDEX_START)

# the planner ui
# ui width: 48
# max width of assignment name lines: 20
padding = 36  # space between in progress and completed

# condition keys:
# WKND - weekend
# ^ - and
# v - or
# ~ - not


# Group A
# # of Assignments: 1
# Description: Homework assignments
# Conditions: WKND

# Closest Date: 11:59PM-11/24/23
# Closest Start Date: 11:59PM-11/24/23
# Closest End Date: 11:59PM-11/25/23

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


SCREEN_WIDTH = 133
SCREEN_HEIGHT = 20


BACK_LEFT, NEXT_LEFT = 'Z', 'X'
BACK_RIGHT, NEXT_RIGHT = ',', '.'


class InputMap:
    def __init__(self, inputs: dict[bytes, Callable], commands: dict[str, Callable]):
        self.inputs = inputs
        self.commands = commands
    def run(self):
        try:
            key = get_input()
            if not key:
                return None
            if isinstance(key, str):
                return self.commands[key]()
            else:
                return self.inputs[key]()
        except KeyError:
            return self.run()


# todo: make a Menu class
# has a setup function that uses the same stuff, but the other
# things are automatically performed (clear, pop-check, etc.)

groups: list[list['Group'], list['Group']] = [[], []]  # active groups  :  inactive groups

def active_groups():
    return groups[0]

def inactive_groups():
    return groups[1]

example_group = Group("Poppy Seed", "Seed assignments", None)
example_group2 = Group("Pee Group", "We pee here", None)
example_group3 = Group("Do Taxes", "Ewwwwwww", None)
active_groups().append(example_group)
active_groups().append(example_group2)
active_groups().append(example_group3)

example_group_inactive = Group("Mass Destruction Plots", "Plots to muder everyone", None)
inactive_groups().append(example_group_inactive)

def groups_menu():
    if is_trigger(POP):
        trigger(POP)
        return

    clear()
    BOX_HEIGHT = 6


    w, h = state(WIDTH), state(LNGTH)
    box = get_box(w, h)
    box.place_vbar(box.w // 2 - padding // 2, box.w // 2 + padding // 2)
    box.place_hcenter_text("Groups List", 0)

    button_y = 1
    button_h = 2

    def BUTTON_Y_POSITION():
        nonlocal button_y
        delta = button_h + 2
        y = button_y
        button_y += delta
        return y

    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text("Add Group",
                                                                                               1, "(G)", 2)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text("Actions", 1, "(A)", 2)

    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Clear All", 1, "(:cl)", 2)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Scheduler", 1, "(S)", 2)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Save & Quit Planner", 1, "(:qt)", 2)


    BOTTOM_BUTTON_HEIGHT = 5

    boxes_per_page = int((box.h - BOTTOM_BUTTON_HEIGHT) / BOX_HEIGHT)
    page = state(MINDEX) // boxes_per_page

    y, i = 1, boxes_per_page * page
    bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))
    if len(active_groups()) > i:
        bu.loadup(active_groups()[i])
        if is_state(MSIDE, MSIDE_LEFT) and is_state(MINDEX, i ):
            bu.set_border('*')
    bu.place_hcenter_text('Activated-Groups', 0)

    bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))
    if len(inactive_groups()) > i:
        bf.loadup(inactive_groups()[i])
        if is_state(MSIDE, MSIDE_RIGHT) and is_state(MINDEX, i):
            bf.set_border('*')
    bf.place_hcenter_text('Inactivated-Groups', 0)

    while y + BOX_HEIGHT < box.h - BOTTOM_BUTTON_HEIGHT:
        i += 1
        y += BOX_HEIGHT

        bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))
        bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))

        if i < len(active_groups()):
            bu.loadup(active_groups()[i])
            if is_state(MSIDE, MSIDE_LEFT) and is_state(MINDEX, i):
                bu.set_border('*')

        if i < len(inactive_groups()):
            bf.loadup(inactive_groups()[i])
            if is_state(MSIDE, MSIDE_RIGHT) and is_state(MINDEX, i):
                bf.set_border('*')

    BOX_TO_ARROW_RATIO = 5
    box_width = box.w // 2 - padding // 2 - 2
    if not TRIGGER_COMMANDS['hdnv']:
        arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, 1))
        arrows.place_hcenter_text("Navigate", 0)

        select = arrows.place_box(box_width * 2 // BOX_TO_ARROW_RATIO - 1, BOTTOM_BUTTON_HEIGHT - 2,
                         (1, arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
        select.place_hcenter_text('Index', ceil(select.h // 2))
        select.place_center_text('(S)')
        select.place_hcenter_text('Through', ceil(select.h // 2) + 2)
        #    ("(<)" + '-' * (box_width - 10) + "(>)\n") +
        #    ("(<)" + "-Prev Page" + '-' * (box_width - 30) + "-Next Page" + "(>)\n") +
        #    ("(<)" + '-' * (box_width - 10) + "(>)\n"))

        arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, box.w - box_width - 1))
        arrows.place_hcenter_text("Navigate", 0)
        select = arrows.place_box(box_width * 2 // BOX_TO_ARROW_RATIO - 1, BOTTOM_BUTTON_HEIGHT - 2,
                         (1, arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
        select.place_hcenter_text('Index', ceil(select.h // 2))
        select.place_center_text('(L)')
        select.place_hcenter_text('Through', ceil(select.h // 2) + 2)
    print(box.bake())

    # We want to have it so that each menu has its own input scheme
    # with different effects.

    # We could have a map of inputs that stores functions
    # arranged by input key (bytes objects?).

    # For example, the prototype for the Groups Menu would be the following:

    input_map = InputMap(
    { # inputs (covered by getch)
        b's': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED) or state(MINDEX, 0),
        b'l': lambda: state(MSIDE, MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED) or state(MINDEX, 0),
        b' ': lambda: state(FGRPS, int(state(MSIDE) > 0)) or state(FGRP, state(MINDEX)) or FUNCTIONS[ASSGN](),
        UP: lambda: state(MINDEX, max(MINDEX_START,
                                      state(MINDEX) - 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(MINDEX)),
        DOWN: lambda: state(MINDEX, min(len(active_groups() if is_state(MSIDE, MSIDE_LEFT) else inactive_groups()) - 1,
                                      state(MINDEX) + 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(MINDEX))
    #    b'a': actions_menu,
    #    b'e': conditions_menu,
    #    b's': scheduler_menu,
    },
    { # commands (inputted manually)
    #    'qt': quit_menu,
    #    'cl': clear_all_data,
    })
    input_map.run()

    groups_menu()  # groups_menu is always the starting point of the program



def assignments_menu():
    if is_state(FGRP, NO_FOCUSED_GROUP):
        return  # will return to group menu
    focused = groups[state(FGRPS)][state(FGRP)]

    if is_trigger(POP):
        trigger(POP)
        return

    clear()
    BOX_HEIGHT = 5

    w, h = state(WIDTH), state(LNGTH)
    box = get_box(w, h)
    box.place_hbar(0)
    box.place_vbar(box.w // 2 - padding // 2, box.w // 2 + padding // 2)
    if len(focused.name) % 2 == 0:
        box.place_hcenter_text("Assignments-of-" + focused.name.replace(" ", "-"), 0)
    else:
        box.place_hcenter_text("Assignments-for-" + focused.name.replace(" ", "-"), 0)

    button_y = 1
    button_h = 1

    def BUTTON_Y_POSITION():
        nonlocal button_y
        delta = button_h + 2
        y = button_y
        button_y += delta
        return y + 1

    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Create Assignment (C)", 1)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Actions (A)", 1)

    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Clear All (:cl)", 1)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Scheduler (S)", 1)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Groups List (G)", 1)
    box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
        "Save & Quit Planner (:qt)", 1)
    # todo: : commands prompt normal input instead of getch
    BOTTOM_BUTTON_HEIGHT = 5

    y, i = 1, 0
    bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))
    bu.place_hcenter_text('Unfinished-Assignments', 0)
    bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))
    bf.place_hcenter_text('Finished-Assignments', 0)

    while y < box.h - BOTTOM_BUTTON_HEIGHT:
        if i < len(focused.in_progress):
            bu.loadup(focused.in_progress[i])

        if i < len(focused.completed):
            bf.loadup(focused.completed[i])

        i += 1
        y += BOX_HEIGHT

        bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))
        bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))

    BOX_TO_ARROW_RATIO = 4
    box_width = box.w // 2 - padding // 2 - 2
    arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, 1))
    arrows.place_hcenter_text("Navigate", 0)
    arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2, (1, 1)).place_center_text(
        f'<<<<<\n<({BACK_LEFT})<\n<<<<<')  # .place_center_text(
    arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2,
                     (1, arrows.w - box_width // BOX_TO_ARROW_RATIO - 1)).place_center_text(
        f'>>>>>\n>({NEXT_LEFT})>\n>>>>>')

    #    ("(<)" + '-' * (box_width - 10) + "(>)\n") +
    #    ("(<)" + "-Prev Page" + '-' * (box_width - 30) + "-Next Page" + "(>)\n") +
    #    ("(<)" + '-' * (box_width - 10) + "(>)\n"))

    arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, box.w - box_width - 1))
    arrows.place_hcenter_text("Navigate", 0)
    arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2, (1, 1)).place_center_text(
        f'<<<<<\n<({BACK_RIGHT})<\n<<<<<')  # .place_center_text(
    arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2,
                     (1, arrows.w - box_width // BOX_TO_ARROW_RATIO - 1)).place_center_text(
        f'>>>>>\n>({NEXT_RIGHT})>\n>>>>>')
    print(box.bake())

    # We want to have it so that each menu has its own input scheme
    # with different effects.

    # We could have a map of inputs that stores functions
    # arranged by input key (bytes objects?).

    # For example, the prototype for the Groups Menu would be the following:

    input_map = InputMap(
        {  # inputs (covered by getch)
            b's': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED),
            b'l': lambda: state(MSIDE, MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED),
            b'g': lambda: trigger(POP) or trigger(REFRS),
            UP: lambda: state(MINDEX, min(len(active_groups() if is_state(MSIDE, MSIDE_LEFT) else inactive_groups()), state(MINDEX) + 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else MINDEX),
            DOWN: lambda: state(MINDEX, max(MINDEX_START, state(MINDEX) - 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else MINDEX)
            #    b'a': actions_menu,
            #    b'e': conditions_menu,
            #    b's': scheduler_menu,
        },
        {  # commands (inputted manually)
            #    'qt': quit_menu,
            #    'cl': clear_all_data,
        })

    input_map.run()

    assignments_menu()  # groups_menu is always the starting point of the program


def quit_menu():
    if is_trigger(POP):
        trigger(POP)
        return

    clear()
    BOX_HEIGHT = 5

    w, h = state(WIDTH), state(LNGTH)
    box = get_box(w, h)
    box.set_border('*')
    bx = box.place_box(w // 2, h // 3, (h // 3, state(WIDTH) // 4)).set_border('*')
    bx.place_hcenter_text("Are you sure you want to quit?", bx.h // 2 - 1, "Quit (Y)", bx.h // 2, "Return (N)", bx.h // 2 + 1)
    print(box.bake())

    input_map = InputMap(
        {  # inputs (covered by getch)
            b'y': lambda: quit(0),
            b'n': lambda: trigger(POP) or trigger(REFRS)
            #    b'a': actions_menu,
            #    b'e': conditions_menu,
            #    b's': scheduler_menu,
        },
        {  # commands (inputted manually)
            #    'qt': quit_menu,
            #    'cl': clear_all_data,
        })

    input_map.run()

    quit_menu()


commands = ('cl', 'qt')

def run(output: bool, *cmdss: list[str]):
    for cmds in cmdss:
        COMMAND_HISTORY.append(':' + " ".join(cmds))

        cmd = cmds[0]
        if cmd in TRIGGER_COMMANDS:
            TRIGGER_COMMANDS[cmd] = not TRIGGER_COMMANDS[cmd]
            #  trigger(REFRS, True)  # refresh the screen
            return None
        elif cmd in STATE_COMMANDS:
            STATE_COMMANDS[cmd] = int(cmds[1])
        elif cmd in FUNCTIONS:
            prms = cmds[1:]
            for i in range(0, len(prms)):
                prm = prms[i]
                try:
                    prms[i] = TRIGGER_COMMANDS[prm]
                except KeyError:
                    try:
                        prms[i] = STATE_COMMANDS[prm]
                    except KeyError:
                        pass
            FUNCTIONS[cmd](*prms)
            return None
        if output:
            return cmds[0]


class Direction:
    DIRS = (
        (-1, 0),
        (1, 0),
        (0, 1),
        (0, -1)
    )
    def __init__(self, dir):
        self.dir = Direction.DIRS[dir]


UP = b'\xe0H'
RIGHT = b'\xe0M'
DOWN = b'\xe0P'
LEFT = b'\xe0K'
def get_input(init: str = "") -> Union[bytes, str, Direction, None]:
    # if TRIGGER_COMMANDS[REFRS]:
    #    trigger(REFRS)
    #    return None

    print('-:> ', end="")
    key = getch() if not init else init[0].encode('ascii')

    if key == b'\xe0':  # precedes special character; use getch() again
        # todo: check for esc
        spcl = getch()
        print('\r', end="")
        return key + spcl
    elif key == b':':
        MAX_COMMAND_SIZE: int = 5
        print('\r', end="")
        prompt = "-:> :"
        cmds: list[str] = [init[1:]]
        count = 0

        def clearline():
            print('\r' + ' ' * 25 + '\r', end="")

        while True:
            print(prompt + " ".join(cmds), end="")

            ch = getch()
            if ch == b'\xe0':  # precedes special character; use getch() again
                # todo: check for esc
                pass
            elif ch == b';':
                run(True, cmds)
                clearline()
                print("\r", end="")
                return get_input()
            elif ch == b'\x08':  # backspace
                if cmds:
                    cmds[-1] = cmds[-1][:len(cmds[-1]) - 1]
                    if len(cmds) > 1 and not cmds[-1]:
                        cmds = cmds[:len(cmds) - 1]
            elif ch == b'\r':  # user presses enter
                clearline()
                break
            elif ch == b' ':
                if cmds[-1] != "":
                    cmds.append("")
            elif len(cmds[-1]) < MAX_COMMAND_SIZE:  # any other key
                cmds[-1] += ch.decode('ascii').lower()
            clearline()
        return run(True, cmds)
    else:
        print('\r', end="")
        return key  # key.decode('ascii').lower()


REFRS = 'refrs'
POP = 'pop'
DEBUG = 'debug'
TRIGGER_COMMANDS = {
    'hdnv': False,
    REFRS: False,
    POP: False,
    DEBUG: False
}


def trigger(s: str, val: bool = None):
    if val is not None:
        TRIGGER_COMMANDS[s] = val
    else:
        TRIGGER_COMMANDS[s] = not TRIGGER_COMMANDS[s]


def is_trigger(s: str):
    return TRIGGER_COMMANDS[s]


MSIDE = 'mside'
MINDEX = 'midx'
WIDTH = 'width'
LNGTH = 'lngth'
FGRP = 'fgrp'
FGRPS = 'fgrps'

NO_FOCUSED_GROUP = -1
ACTIVE_GROUPS, INACTIVE_GROUPS = range(2)

STATE_COMMANDS = {
    MSIDE: 0,  # menu side (-1: left, 0: unselected, 1: right)
    MINDEX: 0,  # menu index (0: first tab, n: (n + 1)th tab)
    WIDTH: 0,
    LNGTH: 0,
    FGRP: NO_FOCUSED_GROUP,
    FGRPS: ACTIVE_GROUPS
}


GROUP = 'group'
ASSGN = 'assgn'
QT = 'qt'
ADA = 'ada'
OUTPT = 'outpt'
FQT = 'fqt'
TRIGG = 'trigg'
ATRIG = 'atrig'
FUNCTIONS = {
    GROUP: groups_menu,
    ASSGN: assignments_menu,
    QT: quit_menu,
    FQT: lambda: quit(0),
    OUTPT: input,
    TRIGG : lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if is_trigger(i)])),
    ATRIG : lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if not is_trigger(i)])),
    # ADA: assignment_editor  # goes to assignment editor
}


COMMAND_HISTORY = []

STARTING_DIMENSIONS = ("20", "133")
run(False,
    ["lngth", STARTING_DIMENSIONS[0]],
    ["width", STARTING_DIMENSIONS[1]])
while True:
    try:
        groups_menu()
    except Exception as e:
        print(e)
        header = "COMMAND HISTORY"
        print(header, '-' * len(header), *COMMAND_HISTORY, '-' * len(header), sep="\n")
        if get_input() == "show":
            raise e