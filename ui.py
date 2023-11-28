from typing import Union, Callable

from msvcrt import getwch as inputkey, getch

import time
from datetime import datetime

from math import ceil

import os

from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)


def clear(): return os.system('cls')


UP = b'\xe0H'
RIGHT = b'\xe0M'
DOWN = b'\xe0P'
LEFT = b'\xe0K'
SPACEBAR = b' '
ANY_KEY = b''


# todo: print warning origin's position
def printwarn(*args):
    print("WARNING:", *args)


def put(*args):
    print(*args, end="")


def clamp(vl: int, mn: int, mx: int) -> int:
    return max(min(vl, mx), mn)

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

    def set_border_default(self):
        self.set_vborder('|')
        self.set_hborder('=')

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

    # TODO: place pivot (center, top left, etc.)
    def place(self, obj: 'Box', position: tuple):
        self.texts[position] = obj
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


# todo: maybe try to have a blinking carat? too much work for now
CARAT = '∣'

# single line input field
class InputField(Box):
    FIELD = None
    def __init__(self, w: int, h: int, carat_pos: list[int, int] = (1, 1), **kwargs):
        super().__init__(w, h, **kwargs)
        self.carat_origin = list(carat_pos)
        self.carat = 0 # the beginning of the string

        self.text = ""

    def type(self, char: Union[str, bytes]):
        pos = self.carat
        self.text = self.text[:pos] + (char if isinstance(char, str) else char.decode('ascii')) + self.text[pos:]
        self.carat += 1  # move the carat forward
    def delete(self, del_count: int):
        self.text = self.text[:self.carat - del_count] + self.text[self.carat:]
        self.carat -= del_count
    def bake(self):
        # if the carat is greater than the length of the box, we need to offset the view
        # by the displacement of the carat from the length of the box

        yi, xi = self.carat_origin
        lentex = min(self.w - xi, len(self.text))
        offs = len(self.text) - lentex

        # remove ALL carats
        for x in range(xi, self.true_w - xi + 1):
            if x - xi < lentex:
                self.grid[yi][x] = self.text[x - xi + offs]
            else:
                self.grid[yi][x] = ' '
            pass
        if InputField.FIELD == self:
            self.grid[yi][xi + min(self.w - xi, self.carat)] = CARAT


        # offs = max(len(self.text) - lentex, 0)
        # for i in range(xi, xi + lentex):
        #    # TODO: multiline inputfield
        #    print(lentex)
        #    self.grid[yi][i] = self.text[0: i - xi + 0]  # index from xi to x
        # if InputField.FIELD == self:
        #    self.grid[yi][xi + lentex] = CARAT
        return super().bake()


def get_box(w, h):
    box = Box(w, h)
    return box


# Assignments are modular and customized

# Assignment: Has a Due Date, a Start Date.
# Note: Has no Due Date, has no Start Date.
# Reminder: Has a Start Date
# Persistent: Has a Due Date, a Start Date. Due Date increments by a certain amount.


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
            if isinstance(key, bytes):
                try:
                    return self.inputs[ANY_KEY](key)
                except KeyError:
                    return self.run()
            return self.run()


# todo: make a Menu class
# has a setup function that uses the same stuff, but the other
# things are automatically performed (clear, pop-check, etc.)


example_group = Group("Poppy Seed", "Seed assignments", None)
example_group2 = Group("Pee Group", "We pee here", None)
example_group3 = Group("Do Taxes", "Ewwwwwww", None)
active_groups().append(example_group)
active_groups().append(example_group2)
active_groups().append(example_group3)

example_group_inactive = Group("Mass Destruction Plots", "Plots to muder everyone", None)
inactive_groups().append(example_group_inactive)


class Menu:
    def get_map(self):
        return InputMap({},{})
    def __init__(self):
        self.map = self.get_map()

    def menu_display(self):
        bx = get_box(state(WIDTH), state(LNGTH))
        return bx

    def show(self):
        global MENU
        MENU = self

        if is_trigger(POP):
            trigger(POP)
            return
        if self.pop_if():
            return

        clear()
        box = self.menu_display().bake()
        print(box)

        self.map.run()
        self.show()

    def pop_if(self) -> bool:
        return False

class TemplateMenu(Menu):
    def get_map(self):
        return InputMap({},{})
    def menu_display(self):
        super().menu_display()

class GroupsMenu(Menu):
    def get_map(self):
        return InputMap(
            {  # inputs (covered by getch)
                b's': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED) or state(
                    MINDEX, 0),
                b'l': lambda: state(MSIDE,
                                    MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED) or state(
                    MINDEX, 0),
                b' ': lambda: state(FGRPS, int(state(MSIDE) > 0)) or state(FGRP, state(MINDEX)) or FUNCTIONS[ASSGN](),
                UP: lambda: state(MINDEX, max(MINDEX_START,
                                              state(MINDEX) - 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(
                    MINDEX)),
                DOWN: lambda: state(MINDEX,
                                    min(len(active_groups() if is_state(MSIDE, MSIDE_LEFT) else inactive_groups()) - 1,
                                        state(MINDEX) + 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(MINDEX))
                #    b'a': actions_menu,
                #    b'e': conditions_menu,
                #    b's': scheduler_menu,
            },
            {  # commands (inputted manually)
                #    'qt': quit_menu,
                #    'cl': clear_all_data,
            })
    def menu_display(self):
        box = super().menu_display()
        BOX_HEIGHT = 6

        w, h = state(WIDTH), state(LNGTH)
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

        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Add Group",
            1, "(G)", 2)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Actions", 1, "(A)", 2)

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
            if is_state(MSIDE, MSIDE_LEFT) and is_state(MINDEX, i):
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
                                      (1,
                                       arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
            select.place_hcenter_text('Index', ceil(select.h // 2))
            select.place_center_text('(S)')
            select.place_hcenter_text('Through', ceil(select.h // 2) + 2)
            #    ("(<)" + '-' * (box_width - 10) + "(>)\n") +
            #    ("(<)" + "-Prev Page" + '-' * (box_width - 30) + "-Next Page" + "(>)\n") +
            #    ("(<)" + '-' * (box_width - 10) + "(>)\n"))

            arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT,
                                   (box.h - BOTTOM_BUTTON_HEIGHT, box.w - box_width - 1))
            arrows.place_hcenter_text("Navigate", 0)
            select = arrows.place_box(box_width * 2 // BOX_TO_ARROW_RATIO - 1, BOTTOM_BUTTON_HEIGHT - 2,
                                      (1,
                                       arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
            select.place_hcenter_text('Index', ceil(select.h // 2))
            select.place_center_text('(L)')
            select.place_hcenter_text('Through', ceil(select.h // 2) + 2)
        return box

class AssignmentsMenu(Menu):
    def pop_if(self) -> bool:
        return is_state(FGRP, NO_FOCUSED_GROUP)
    def __init__(self):
        super().__init__()

    def show(self):
        super().show()
    def menu_display(self):
        focused = groups[state(FGRPS)][state(FGRP)]

        if is_trigger(POP):
            trigger(POP)
            return

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

        return box
    def get_map(self):
        return InputMap(
            {  # inputs (covered by getch)
                b's': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED),
                b'l': lambda: state(MSIDE, MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED),
                b'g': lambda: trigger(POP) or trigger(REFRS),
                UP: lambda: state(MINDEX,
                                  min(len(active_groups() if is_state(MSIDE, MSIDE_LEFT) else inactive_groups()),
                                      state(MINDEX) + 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else MINDEX),
                DOWN: lambda: state(MINDEX, max(MINDEX_START, state(MINDEX) - 1) if not is_state(MSIDE,
                                                         MSIDE_UNDECIDED) else MINDEX),
                b'c': lambda: FUNCTIONS[ADA](),
                #    b'e': conditions_menu,
                #    b's': scheduler_menu,
            },
            {  # commands (inputted manually)
                #    'qt': quit_menu,
                #    'cl': clear_all_data,
            })


class QuitMenu(Menu):
    def get_map(self):
        return InputMap(
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
    def __init__(self):
        super().__init__()
    def show(self):
        super().show()

    def menu_display(self):
        w, h = state(WIDTH), state(LNGTH)
        box = get_box(w, h)
        box.set_border('*')
        bx = box.place_box(w // 2, h // 3, (h // 3, state(WIDTH) // 4)).set_border('*')
        bx.place_hcenter_text("Are you sure you want to quit?", bx.h // 2 - 1, "Quit (Y)", bx.h // 2, "Return (N)",
                              bx.h // 2 + 1)
        return box


BUTTON_COLUMN, FIELD_COLUMN = 1, 2
class AssignmentEditor(Menu):
    def on_space(self):
        if is_state(MSIDE, 2):
            get_field(self.caption_fields[state(MINDEX)])
            self.find_index(1)
        elif is_state(MSIDE, 1):
            if self.enabled[state(MINDEX)] is not None:
                self.enabled[state(MINDEX)] = not self.enabled[state(MINDEX)]

    def find_index(self, delta: int):
        d = delta // abs(delta)
        i = state(MINDEX)
        if is_state(MSIDE, BUTTON_COLUMN):
            while True:
                i += d
                if 0 <= i < len(self.enabled):
                    if self.enabled[i] is not None:
                        state(MINDEX, i)
                        return
                else:
                    return
        elif is_state(MSIDE, FIELD_COLUMN):
            while True:
                i += d
                if 0 <= i < len(self.enabled):
                    if self.enabled[i] is not False:
                        state(MINDEX, i)
                        return
                else:
                    return

    def switch_sides(self, side: int):
        state(MSIDE, side)
        if is_state(MSIDE, BUTTON_COLUMN):
            if self.enabled[state(MINDEX)] is None:
                i = state(MINDEX)  # we default to the top button
                for n in range(1, len(self.enabled)):
                    if 0 <= i + n < len(self.enabled):
                        if self.enabled[i + n] is not None:
                            state(MINDEX, i + n)
                            return

                    if 0 <= i - n < len(self.enabled):
                        if self.enabled[i - n] is not None:
                            state(MINDEX, i - n)
                            return

        if is_state(MSIDE, FIELD_COLUMN):
            if self.enabled[state(MINDEX)] is False:
                i = state(MINDEX)  # we default to the top button
                for n in range(1, len(self.enabled)):
                    if 0 <= i + n < len(self.enabled):
                        if self.enabled[i + n] is not False:
                            state(MINDEX, i + n)
                            return

                    if 0 <= i - n < len(self.enabled):
                        if self.enabled[i - n] is not False:
                            state(MINDEX, i - n)
                            return

    def on_any_key(self, key):
        if is_state(MSIDE, FIELD_COLUMN):
            if key != b'\r':
                if key != b'\x08':
                    self.caption_fields[state(MINDEX)].type(key)
                else:
                    self.caption_fields[state(MINDEX)].text = ""
            self.on_space()


    def get_map(self):
        return InputMap({
            ANY_KEY: self.on_any_key,
            UP: lambda: self.find_index(-1),  # state(MINDEX, clamp(state(MINDEX) - 1, 0, len(captions) - 1)),
            DOWN: lambda: self.find_index(1),  # state(MINDEX, clamp(state(MINDEX) + 1, 0, len(captions) - 1)),
            RIGHT: lambda: self.switch_sides(FIELD_COLUMN),
            LEFT: lambda: self.switch_sides(BUTTON_COLUMN),
            b'\r': self.on_space
        }, {})
    def __init__(self):
        super().__init__()
        self.fields: list[InputField] = [
            # Name, Description, Start Date, Due Date, Due Date Postincrement
        ]
        self.actives: list[bool] = []
        self.enabled = [None, True, True, True, False]

        self.captions = {
            "Name": 30,
            "Description": 90,
            "Due Date": 20,  # YY-MM-DD hh:mm:ss (DateTime)
            "Start Date": 20,
            "Date Increment": 20,  # MM-WW-DD-hh-mm-ss (TimeSpan)
        }
        self.caption_fields: list[InputField] = []

        for i, caption in enumerate(self.captions):
            field = InputField(self.captions[caption], 1, [1, 2])
            self.caption_fields.append(field)

    def menu_display(self):
        screen_share = 2 / 3
        box_length = 3
        margin_x = 2

        bx = Box(133, 20)
        bx.place_hbar(0, 19)
        bx.place_vbar(0, 132)

        BUTTON_COLUMN, FIELD_COLUMN = 1, 2

        BOX_HEIGHT = 3
        OBJECT_SPACEOUT = 1 + margin_x + box_length * 2 + 1
        for i, caption in enumerate(self.captions):
            if self.enabled[i] is not None:
                active = bx.place_box(box_length, 1, ((i + 1) * BOX_HEIGHT - 1, 1 + margin_x))
                if self.enabled[i]:
                    active.place_center_text('X')
                if is_state(MSIDE, BUTTON_COLUMN) and is_state(MINDEX, i):
                    active.set_border('*')
            elif is_state(MSIDE, BUTTON_COLUMN) and is_state(MINDEX, i):
                state(MINDEX, state(MINDEX) + 1)  # +=1 until reach one that has a trigger

            name = caption + ": "
            bx.place_text(name, ((i + 1) * BOX_HEIGHT, 1 + OBJECT_SPACEOUT))

            field = self.caption_fields[i]
            bx.place(field,
                     ((i + 1) * BOX_HEIGHT - 1, 2 + OBJECT_SPACEOUT + len(caption) + 1))  # name

            field.set_border_default()
            if is_state(MSIDE, FIELD_COLUMN):
                if i == state(MINDEX):
                    if self.enabled[i] or self.enabled[i] is None:
                        field.set_border('*')
                    else:
                        state(MINDEX, state(MINDEX) - 1)
        return bx


BUTTON_COLUMN, FIELD_COLUMN = 1, 2
class AssignmentEditor(Menu):
    def on_space(self):
        if is_state(MSIDE, 2):
            get_field(self.caption_fields[state(MINDEX)])
            self.find_index(1)
        elif is_state(MSIDE, 1):
            if self.enabled[state(MINDEX)] is not None:
                self.enabled[state(MINDEX)] = not self.enabled[state(MINDEX)]

    def find_index(self, delta: int):
        d = delta // abs(delta)
        i = state(MINDEX)
        if is_state(MSIDE, BUTTON_COLUMN):
            while True:
                i += d
                if 0 <= i < len(self.enabled):
                    if self.enabled[i] is not None:
                        state(MINDEX, i)
                        return
                else:
                    return
        elif is_state(MSIDE, FIELD_COLUMN):
            while True:
                i += d
                if 0 <= i < len(self.enabled):
                    if self.enabled[i] is not False:
                        state(MINDEX, i)
                        return
                else:
                    return

    def switch_sides(self, side: int):
        state(MSIDE, side)
        if is_state(MSIDE, BUTTON_COLUMN):
            if self.enabled[state(MINDEX)] is None:
                i = state(MINDEX)  # we default to the top button
                for n in range(1, len(self.enabled)):
                    if 0 <= i + n < len(self.enabled):
                        if self.enabled[i + n] is not None:
                            state(MINDEX, i + n)
                            return

                    if 0 <= i - n < len(self.enabled):
                        if self.enabled[i - n] is not None:
                            state(MINDEX, i - n)
                            return

        if is_state(MSIDE, FIELD_COLUMN):
            if self.enabled[state(MINDEX)] is False:
                i = state(MINDEX)  # we default to the top button
                for n in range(1, len(self.enabled)):
                    if 0 <= i + n < len(self.enabled):
                        if self.enabled[i + n] is not False:
                            state(MINDEX, i + n)
                            return

                    if 0 <= i - n < len(self.enabled):
                        if self.enabled[i - n] is not False:
                            state(MINDEX, i - n)
                            return

    def on_any_key(self, key):
        if is_state(MSIDE, FIELD_COLUMN):
            if key != b'\r':
                if key != b'\x08':
                    self.caption_fields[state(MINDEX)].type(key)
                else:
                    self.caption_fields[state(MINDEX)].text = ""
            self.on_space()


    def get_map(self):
        return InputMap({
            ANY_KEY: self.on_any_key,
            UP: lambda: self.find_index(-1),  # state(MINDEX, clamp(state(MINDEX) - 1, 0, len(captions) - 1)),
            DOWN: lambda: self.find_index(1),  # state(MINDEX, clamp(state(MINDEX) + 1, 0, len(captions) - 1)),
            RIGHT: lambda: self.switch_sides(FIELD_COLUMN),
            LEFT: lambda: self.switch_sides(BUTTON_COLUMN),
            b'\r': self.on_space
        }, {})
    def __init__(self):
        super().__init__()
        self.fields: list[InputField] = [
            # Name, Description, Start Date, Due Date, Due Date Postincrement
        ]
        self.actives: list[bool] = []
        self.enabled = [None, True, True, True, False]

        self.captions = {
            "Name": 30,
            "Description": 90,
            "Due Date": 20,  # YY-MM-DD hh:mm:ss (DateTime)
            "Start Date": 20,
            "Date Increment": 20,  # MM-WW-DD-hh-mm-ss (TimeSpan)
        }
        self.caption_fields: list[InputField] = []

        for i, caption in enumerate(self.captions):
            field = InputField(self.captions[caption], 1, [1, 2])
            self.caption_fields.append(field)

    def menu_display(self):
        screen_share = 2 / 3
        box_length = 3
        margin_x = 2

        bx = Box(133, 20)
        bx.place_hbar(0, 19)
        bx.place_vbar(0, 132)

        BUTTON_COLUMN, FIELD_COLUMN = 1, 2

        BOX_HEIGHT = 3
        OBJECT_SPACEOUT = 1 + margin_x + box_length * 2 + 1
        for i, caption in enumerate(self.captions):
            if self.enabled[i] is not None:
                active = bx.place_box(box_length, 1, ((i + 1) * BOX_HEIGHT - 1, 1 + margin_x))
                if self.enabled[i]:
                    active.place_center_text('X')
                if is_state(MSIDE, BUTTON_COLUMN) and is_state(MINDEX, i):
                    active.set_border('*')
            elif is_state(MSIDE, BUTTON_COLUMN) and is_state(MINDEX, i):
                state(MINDEX, state(MINDEX) + 1)  # +=1 until reach one that has a trigger

            name = caption + ": "
            bx.place_text(name, ((i + 1) * BOX_HEIGHT, 1 + OBJECT_SPACEOUT))

            field = self.caption_fields[i]
            bx.place(field,
                     ((i + 1) * BOX_HEIGHT - 1, 2 + OBJECT_SPACEOUT + len(caption) + 1))  # name

            field.set_border_default()
            if is_state(MSIDE, FIELD_COLUMN):
                if i == state(MINDEX):
                    if self.enabled[i] or self.enabled[i] is None:
                        field.set_border('*')
                    else:
                        state(MINDEX, state(MINDEX) - 1)
        return bx


commands = ('cl', 'qt')

def run(output: bool, *cmdss: list[str]):
    for cmds in cmdss:
        COMMAND_HISTORY.append(':' + " ".join(cmds))

        cmd = cmds[0]
        if cmd in TRIGGER_COMMANDS:
            TRIGGER_COMMANDS[cmd] = not TRIGGER_COMMANDS[cmd]
            #  trigger(REFRS, True)  # refresh the screen
            return None
        elif cmd in STATE_COMMANDS and len(cmds) > 1:
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


def get_input(init: str = "", **specials) -> Union[bytes, str, None]:
    # if TRIGGER_COMMANDS[REFRS]:
    #    trigger(REFRS)
    #    return None

    block_cmds = specials.get('block_cmds', False)
    print('-:> ', end="")
    key = getch() if not init else init[0].encode('ascii')

    if key == b'\xe0':  # precedes special character; use getch() again
        # todo: check for esc
        spcl = getch()
        print('\r', end="")
        return key + spcl
    elif key == b':' and not block_cmds:
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
group_menu = GroupsMenu()
ASSGN = 'assgn'
assignments_menu = AssignmentsMenu()
QT = 'qt'
quit_menu = QuitMenu()
ADA = 'ada'
assignment_editor = AssignmentEditor()
OUTPT = 'outpt'
FQT = 'fqt'
TRIGG = 'trigg'
ATRIG = 'atrig'
FUNCTIONS = {
    GROUP: group_menu.show,
    ASSGN: assignments_menu.show,
    QT: quit_menu.show,
    FQT: lambda: quit(0),
    OUTPT: input,
    TRIGG : lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if is_trigger(i)])),
    ATRIG : lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if not is_trigger(i)])),
    ADA: assignment_editor.show,  # goes to assignment editor
}


COMMAND_HISTORY = []

MENU: Menu = None
STARTING_DIMENSIONS = ("20", "133")
run(False,
    ["lngth", STARTING_DIMENSIONS[0]],
    ["width", STARTING_DIMENSIONS[1]])


def ui():
    while True:
        try:
            group_menu.show()
        except Exception as e:
            print(e)
            header = "COMMAND HISTORY"
            print('-' * len(header),
                  header,
                  '-' * len(header),
                  *COMMAND_HISTORY,
                  '-' * len(header), sep="\n")
            if get_input(':') == "catch":
                raise e


reset_menu_selection()


"""
What must we do to have an Input Field system?

We need to do the following steps when the user chooses an Input Field (by any
means offered by a menu)

1. We need to assign a Field
2. We need to enable the inputting of that field by the use of getch() (while loop)
3. We need to update the screen based on the characters inputted via step 2

How can we write this algorithm, then?

1. We need to have a function that is called upon selecting an input field.
2. We need to capture our current menu.
3. We need to have a while loop that iterates every time getch() is called successfully.
4. The while loop must terminate when getch() == b'\r' (carriage return).

Say we have the following box bx.
bx = Box(133, 20)

bx has an input field field at the top right corner.
field = InputField(20, 1), (1, 1)
bx.place(field)

The input map of the menu of bx gives the option to select field by pressing the spacebar
key.

When field is selected, the getch() while starts.


while True:
    ch = getch()
    if ch == b'\xe0': # special char
        spec = getch()
    elif ch == b'\r':
        break
    else:
        field.type(ch)

"""


# todo: callback on finish
# assumption: field is a single line input field
def get_field(field: InputField):
    InputField.FIELD = field
    menu = MENU.menu_display()
    while True:
        clear()
        print(menu.bake())
        ch = get_input()
        if isinstance(ch, bytes):
            if ch == b'\r':
                InputField.FIELD = None
                return
            elif ch == b'\x08':
                if len(field.text) > 0:
                    field.delete(1)
                continue
            elif len(ch) > 0 and ch[0] == b'\xe0':
                if ch in (UP, RIGHT, DOWN, LEFT):
                    continue  # TODO: Indexing through field, moving carat
                ch = ch[1]
            char = ch.decode('ascii')
            field.type(char)
            print(ch)


# Template for Menus that use InputFields.
# Fields must be cached in order to preserve their states.
"""
class InputFieldTemplateMenu(Menu):
    def __init__(self):
        super().__init__()
        self.field = InputField(20, 1)
    def get_map(self):
        return InputMap({b' ': lambda: get_field(self.field)}, {})
    def menu_display(self):
        bx = super().menu_display()
        bx.place(self.field, (1, 1))
        return bx
"""

