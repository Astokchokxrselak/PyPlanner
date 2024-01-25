# Design Philosophy

# Every menu should be able to work independently of each other.

# Menus will base their functionalities off of the current context
# of the entire program.

# TODO: callbacks for input fields
#       submenus
#       assignment editing

from dateparsers import *

from typing import Union, Callable, Sequence

NoneOr = lambda t: Union[t, None]

from msvcrt import getch

import time
from datetime import datetime, timedelta

import alerts

from structs import (BaseAssignment, Group, active_groups, inactive_groups,
                     MultipleProperty as MP)
import structs

import savedata

from helpers.string_helpers import limit_width_smart_break
from helpers.string_helpers import bool_x as x_or_space

def ilerp(i1: int, i2: int, t: float) -> int:
    return int(i1 + (i2 - i1) * t)


def slice_until(array: list, func: Callable):
    res = []
    for i in array:
        if func(i):
            res.append(i)
        else:
            break
    return res


def sslice_until(string: str, func: Callable):
    res = ""
    i = 0
    for i in range(len(string)):
        if func(string[i]):
            res += string[i]
        else:
            break
    return {"string": res, "end": i}


#  datetime parsing

# ANY DELIMITER CAN BE USED TO SEPARATE DATE TIME SYMBOLS AS LONG AS THE SYMBOL IS ONE CHARACTER, NON-ALPHANUMERIC, AND IS USED CONSISTENTLY
# LET (D) REPRESENT THIS DELIMITER
# LET (T) REPRESENT THE ALTERNATIVE DELIMITER FOR TIME (FOR A DATETIME INPUT)
# X REPRESENTS ANY DIGIT (1-9)
# SYMBOLS PROCEEDING X MAY BE ARRANGED IN ANY ORDER
# WHEN SYMBOLS ARE ABSENT THE ORDER OF INPUT MUST BE PRESERVED IN THE ORDER SPECIFIED BY THE SYMBOLS
# WHEN SYMBOLS ARE ABSENT INPUT SEGMENTS [PAIRS OF DIGITS] MUST BE ENTERED AS PAIRS, WITH NUMBERS LESS THAN 10 INCLUDING A LEADING 0


#  Options:
from math import ceil

import os

from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)


def clear():
    if is_trigger(INPCL):
        return os.system('cls')


SPECIAL = b'\xe0'
UP = b'\xe0H'
RIGHT = b'\xe0M'
DOWN = b'\xe0P'
LEFT = b'\xe0K'
DEL = b'\xe0S'
SPACEBAR = b' '
ENTER = b'\r'
COPY = b'\x03'
PASTE = b'\x16'
BACKSPACE = b'\x08'
ANY_KEY = b''


def is_key_special(key):
    return key in (SPECIAL, UP, RIGHT, DOWN, LEFT, SPACEBAR, ENTER, COPY, PASTE, BACKSPACE)


# todo: print warning origin's position
def printwarn(*args):
    if is_trigger(WARNS):
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


class Layer:
    def at(self, y, x):
        return self.grid[y][x]

    def clear_grid(self):
        for x in range(self.w):
            for y in range(self.h):
                self.grid[y + 1][x + 1] = ' '
        self.texts = {}

    # THIS IS NOT A CLEAR GRID FUNCTION
    # THIS REASSEMBLES THE BOX MATRIX
    # TODO: CLEAR_GRID METHOD
    def reset_grid(self):
        self.grid = []
        for i in range(self.true_h):
            self.grid.append([])
            for j in range(self.true_w):
                self.grid[i].append('')

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
        elif len(text) % 2 != self.w % 2 \
                or (break_count + 1) % 2 != self.h % 2:  # + 1 indicates number of lines
            printwarn("Text with unequal parity to dimensions of container cannot be centered")
        offset_y = count_breaks(text) // 2

        line_length = len(text) if not break_count else text.index('\n')
        # TODO: find the longest line instead of the first line
        self.texts[(ceil(self.h / 2) - offset_y, self.w // 2 - line_length // 2 + 1)] = text

    def place_vbar(self, x, *xs, **kwargs):
        self.place_text('|\n' * kwargs.get("length", self.h), (1, x + 1))
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
            is_box = isinstance(t, Box) or isinstance(t, Layer)
            if is_box:
                t = str(t.bake())
            if debug:
                t = '`' + t[1:]
            y, x = yi, xi = p
            for i in range(len(t)):
                ch = t[i]
                if debug and ch == ' ':
                    ch = str(i % 10)
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
            output: str = group.name + "\n" + group.desc + "\nClosest Due Date: " + str(
                group.get_closest_due_date()) + "\nClosest Start Date: " + str(group.get_closest_start_date())

            # desc should be the only multiline element in the box
            # self.h = ceil(len(group.desc) / self.w) + output.count('\n')

            # self.reset_grid()

            self.place_text(output, pn)
        elif isinstance(object, BaseAssignment):
            assignment = object
            name = desc = due = start = inc = ""
            name = assignment.name
            if assignment.has_description:
                max_desc_size = (self.w - 2)
                desc = assignment.desc
                if len(desc) > max_desc_size:  # .h - 1 is for the title (should be one line)
                    # TODO: support for multiline titles and descriptions
                    desc = '\n' + desc[:max_desc_size - 3] + "..."  # ellipsis
                else:
                    desc = '\n' + desc

            if assignment.has_due_date:
                input(type(assignment.due_date))
                due = '\n' + "Due Date: " + str(assignment.due_date)

            if assignment.has_start_date:
                start = '\n' + "Start Date: " + str(assignment.start_date)

            if assignment.is_persistent:
                inc = '\n' + "Interval: " + str(assignment.interval)

            outpt: str = name + desc + due + start + inc
            self.h = outpt.count('\n') + 1

            if not misc.get("noreset", False):
                self.reset_grid()
                self.set_border_default()
            self.place_text(outpt, pn)

    def __repr__(self):
        string = ""
        for r in self.grid:
            string += "".join([s or ' ' for s in r]) + "\n"
        return string

    def __str__(self):
        return self.__repr__()


LAYER_INDEX_KEY = 'layer'


class Box:
    def get_layer(self, index):
        return self._layers[index]

    # THIS IS NOT A CLEAR GRID FUNCTION
    # THIS REASSEMBLES THE BOX MATRIX
    # TODO: CLEAR_GRID METHOD

    def reset_grid(self, index: Union[int, None] = None):
        if index is not None:
            return self._layers[index].reset_grid()
        for grid in self._layers:
            grid.w, grid.h = self.w, self.h
            grid.reset_grid()

    # w - the width of the container, h - the height of the container (empty for square container)
    def __init__(self, w, h=-1, layer_count=1, **kwargs):
        self.w = w

        if h < 0:
            h = w
        self.h = h

        self._layers = []
        for i in range(layer_count):
            self._layers.append(Layer(w, h, **kwargs))

        self._layers[-1].set_border_default()

        self.default_layer = kwargs.get("default_layer", -2)

    def set_border(self, ch):
        self._layers[-1].set_border(ch)

    def set_hborder(self, ch):
        self._layers[-1].set_hborder(ch)

    def set_vborder(self, ch):
        self._layers[-1].set_vborder(ch)

    def set_default_layer(self, new):
        self.default_layer = new

    @property
    def layer_count(self):
        return len(self._layers)

    @property
    def true_h(self):
        return self.h + 2

    @property
    def true_w(self):
        return self.w + 2

    # TODO: place pivot (center, top left, etc.)
    def place(self, obj: 'Box', position: tuple, index=None):
        index = clamp(index or self.default_layer, -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place(obj, position)

    def place_text(self, text: str, position: tuple, index=None):
        index = clamp(index or self.default_layer, -self.layer_count, self.layer_count - 1)
        # self.texts[position] = text
        self.get_layer(index).place_text(text, position)

    def replace_text(self, text: str, position: tuple, index=None):
        index = clamp(index or self.default_layer, -self.layer_count, self.layer_count - 1)
        self.get_layer(index).replace_text(text, position)

    def place_hcenter_text(self, text, y: int = -1, *args: [str, int], **boxargs):
        index = clamp(boxargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_hcenter_text(text, y, *args)

    def place_vcenter_text(self, text, x: int = -1, *args: [str, int], **boxargs):
        index = clamp(boxargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_vcenter_text(text, x, *args)

    def place_center_text(self, text: str, **boxargs):
        index = clamp(boxargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_center_text(text)

    def place_vbar(self, x, *xs, **boxargs):
        index = clamp(boxargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_vbar(x, *xs, **boxargs)

    def place_hbar(self, y: int, *ys: int, **boxargs):
        index = clamp(boxargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_hbar(y, *ys)

    def place_box(self, w: int, h: int, position: tuple, *whps: [int, int, tuple], **boxkwargs) -> Union[
        list['Box'], 'Box']:
        index = clamp(boxkwargs.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        return self.get_layer(index).place_box(w, h, position, *whps, **boxkwargs)

    def bake(self, index: Union[int, None] = None):
        if index is not None:
            return self.get_layer(index).bake()

        # ensure that a line break is inserted in the middle for text
        # whose length is greater than half of the container's width

        debug = is_trigger(DEBUG)
        for i in range(len(self._layers)):
            layer = self._layers[i]
            layer.bake()
        return self

    def loadup(self, object: Union['Group', 'BaseAssignment',], pn: tuple = (1, 2), pd: tuple = (2, 2), **misc):
        index = clamp(misc.get(LAYER_INDEX_KEY, self.default_layer), -self.layer_count, self.layer_count - 1)
        layer = self.get_layer(index)

        # todo: verification of loaded strings based on line breaks
        self.marginx = 1
        if isinstance(object, Group):
            group = object
            max_desc_size = (self.w - 2) * (self.h - 1)
            desc = group.desc
            if len(desc) - desc.count('\n') > max_desc_size:  # .h - 1 is for the title (should be one line)
                # TODO: support for multiline titles
                group.desc = desc[:max_desc_size - 3] + "..."  # ellipsis
            output: str = group.name + "\n" + group.desc + "\nClosest Due Date: " + str(
                group.get_closest_due_date()) + "\nClosest Start Date: " + str(group.get_closest_start_date())

            # desc should be the only multiline element in the box
            # self.h = ceil(len(group.desc) / self.w) + output.count('\n')

            # self.reset_grid()

            layer.place_text(output, pn)
        elif isinstance(object, BaseAssignment):
            assignment = object
            name = desc = due = start = inc = ""
            name = assignment.name
            if len(name) > self.w - 2:
                name = name[:self.w - 2 - 3] + "..."
            if assignment.has_description:
                max_desc_size = (self.w - 2)
                desc = assignment.desc
                if len(desc) > max_desc_size:  # .h - 1 is for the title (should be one line)
                    # TODO: support for multiline titles and descriptions
                    desc = '\n' + desc[:max_desc_size - 3] + "..."  # ellipsis
                else:
                    desc = '\n' + desc

            if assignment.has_due_date:
                due = '\n' + "Due Date: " + str(assignment.due_date)

            if assignment.has_start_date:
                start = '\n' + "Start Date: " + str(assignment.start_date)

            if assignment.is_persistent:
                inc = '\n' + "Interval: " + str(assignment.interval)

            outpt: str = name + desc + due + start + inc
            self.h = outpt.count('\n') + 1

            if not misc.get("noreset", False):
                self.reset_grid()
                self.get_layer(-1).set_border_default()
            layer.place_text(outpt, pn)

    def __repr__(self):
        string = ""
        for i in range(self.true_h):
            for j in range(self.true_w):
                symbol, layer = '', -1
                while not symbol and -layer <= self.layer_count:
                    symbol = self._layers[layer].at(i, j)
                    layer -= 1
                string += symbol or ' '
            string += "\n"
        return string

    def __str__(self):
        return self.__repr__()


# todo: maybe try to have a blinking carat? too much work for now
CARAT = '∣'


# todo: consider inheriting from box
# todo: implement right margins, right now only left

# SINGLE LINE input field
class InputField(Layer):
    FIELD = None

    def __init__(self, w: int, h: int, carat_pos: list[int, int] = (1, 1), **kwargs):
        super().__init__(w, h, **kwargs)
        self.set_border_default()
        self.carat_origin = list(carat_pos)
        self.carat = 0  # the beginning of the string

        self.text = self.displayed_text = ""
        self.displaying = False

    def type(self, char: Union[str, bytes]):
        pos = self.carat
        self.text = self.text[:pos] + (char if isinstance(char, str) else char.decode('ascii')) + self.text[pos:]
        self.shift_carat(len(char))  # move the carat forward

    def margin(self):
        return 0 if self.marginx < 0 else self.marginx

    def delete(self, del_count: int):
        self.text = self.text[:max(self.margin(), self.carat - del_count)] + self.text[self.carat:]
        self.shift_carat(-del_count)

    def clear(self):
        self.back_carat()
        self.text = ""

    def front_carat(self):
        self.shift_carat(len(self.text))

    def back_carat(self):
        self.shift_carat(-len(self.text))

    def shift_carat(self, shift_amount: int):
        self.carat = clamp(self.carat + shift_amount, self.margin(), len(self.text))

    def get(self, vtype: [str, type] = "str"):
        v = self.text

        if vtype == 'd':
            pass
            # v = parse_date_as_date(self.text)
        elif vtype == 't':
            pass
            # v = parse_time_as_time(self.text)
        elif vtype == 'int' or vtype == 'i':
            v = int(self.text)
        elif vtype == 'dt':
            if not self.text:
                v = now()
            elif self.text.strip() == "None":
                v = None
            else:
                v = parse_datetime(self.text)
        elif vtype == 'ts':
            if self.text.strip() == "None":
                v = None
            else:
                if not self.text:
                    v = timedelta()
                else:
                    v = parse_timespan(self.text)
        return v

    def valid_get(self, vtype: str):
        try:
            return self.get(vtype)
        except ValueError:
            return None

    def validate(self, vtype: [str, type]):
        # 's' - string
        # 'd' - date
        # 't' - time
        # 'dt' - datetime

        # if vtype == 's' or vtype is str:
        #    return True
        try:
            v = self.get(vtype)
            self.displayed_text = str(v)
            self.front_carat()
            self.displaying = True
        except ValueError:
            self.clear()
            self.displaying = False
            return ""
        return self.displayed_text

    def bake(self):
        # if the carat is greater than the length of the box, we need to offset the view
        # by the displacement of the carat from the length of the box

        yi, xi = self.carat_origin
        if not self.displaying:
            container_width = self.w - xi
            lentex = min(container_width,
                         len(self.text))  # the amount of characters we are replacing with other characters
            offset = container_width * (
                        self.carat // container_width)  # how many field-widths we offset the text by (incase the carat leaves the box)
            if offset != 0:
                offset -= 1  # leave space for the border?

            for x in range(self.w - xi):
                #  minus one for the border
                if x < lentex and x + offset < len(self.text):
                    self.grid[yi][xi + x] = self.text[x + offset]
                else:
                    self.grid[yi][xi + x] = ' '

            if InputField.FIELD == self:
                index = xi + self.carat % container_width
                if self.carat > container_width:
                    index += 1
                self.grid[yi][index] = CARAT
                # self.grid[yi][xi + min(self.w - xi, self.carat)] = CARAT
        else:
            lentex = min(self.w - xi, len(self.displayed_text))  # the amount of characters we are replacing
            for x in range(self.w - xi):
                if x < lentex:
                    self.grid[yi][xi + x] = self.displayed_text[x]
                else:
                    self.grid[yi][xi + x] = ' '

        """
        # offs = len(self.text) - lentex  # we offset if carat is greater than self.w

        # remove ALL carats
        for x in range(lentex):
            if x - xi < lentex:
                self.grid[yi][x] = self.text[x - xi + offs]
            else:
                self.grid[yi][x] = ' '
            pass
        """

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

MIDX_START = 0
UNUSED_MIDX_START = -1


def reset_menu_selection():
    state(MACT, NO_ACTION)
    state(MSIDE, MSIDE_UNDECIDED)
    state(MIDXA, MIDX_START)
    state(MIDXB, UNUSED_MIDX_START)


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
    def __init__(self, inputs: dict[bytes, Callable], commands: dict[str, Callable], **options):
        self.inputs = inputs
        self.commands = commands
        self.any_key_pre = options.get("any_key_pre", False)  # execute any_key

    def run(self):
        try:
            key = get_input()
            if not key:
                return None
            if isinstance(key, list):
                return self.commands[key[0]](*key[1:])
            else:
                if self.any_key_pre:
                    value = self.inputs[ANY_KEY](key)  # returns a truthy value if overrides behavior of other keys
                    if value is not None:
                        return value
                return self.inputs[key]()
        except KeyError:
            if not self.any_key_pre and isinstance(key, bytes):
                try:
                    return self.inputs[ANY_KEY](key)
                except KeyError:
                    return self.run()


class Menu:
    def get_map(self):
        return InputMap({}, {})

    def __init__(self):
        self.map = self.get_map()

    def menu_display(self):
        bx = get_box(state(WIDTH), state(LNGTH))
        return bx

    def preshow(self):
        #  Useful for menus that override normal show() behavior
        #  returns false if should pop
        global MENU
        MENU = self

        if is_trigger(POP):
            trigger(POP)
            return False
        if self.pop_if():
            return False

        if is_trigger(INPCL):
            clear()
        return True

    def show(self):
        if not self.preshow():
            return

        box = self.menu_display().bake()
        print(box)

        self.map.run()
        self.show()

    def pop_if(self) -> bool:
        return False


class TemplateMenu(Menu):
    def get_map(self):
        return InputMap({}, {})

    def menu_display(self):
        super().menu_display()


class GroupsMenu(Menu):
    def get_map(self):
        def on_space():
            old_idx, old_side = state(MIDXA), state(MSIDE)
            state(FGRPS, int(state(MSIDE) > 0))
            state(FGRP, state(MIDXA))
            FUNCTIONS[ASSGN]()
            state(MIDXA, old_idx)
            state(MSIDE, old_side)

        return InputMap(
            {  # inputs (covered by getch)
                b'x': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED) or state(
                    MIDXA, 0),
                b'n': lambda: state(MSIDE,
                                    MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED) or state(
                    MIDXA, 0),
                SPACEBAR: on_space,
                UP: lambda: state(MIDXA, max(MIDX_START,
                                             state(MIDXA) - 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(
                    MIDXA)),
                DOWN: lambda: state(MIDXA,
                                    min(len(active_groups() if is_state(MSIDE, MSIDE_LEFT) else inactive_groups()) - 1,
                                        state(MIDXA) + 1) if not is_state(MSIDE, MSIDE_UNDECIDED) else state(MIDXA))
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
            "Configure", 1, "(Q)", 2)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Scheduler", 1, "(S)", 2)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Save & Quit Planner", 1, "(:qt)", 2)

        BOTTOM_BUTTON_HEIGHT = 5

        boxes_per_page = int((box.h - BOTTOM_BUTTON_HEIGHT) / BOX_HEIGHT)
        page = state(MIDXA) // boxes_per_page

        y, i = 1, boxes_per_page * page
        bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))

        if len(active_groups()) > i:
            bu.loadup(active_groups()[i])
            if is_state(MSIDE, MSIDE_LEFT) and is_state(MIDXA, i):
                bu.set_border('*')
        bu.place_hcenter_text('Activated-Groups', 0)

        bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))
        if len(inactive_groups()) > i:
            bf.loadup(inactive_groups()[i])
            if is_state(MSIDE, MSIDE_RIGHT) and is_state(MIDXA, i):
                bf.set_border('*')
        bf.place_hcenter_text('Inactivated-Groups', 0)

        while y + BOX_HEIGHT < box.h - BOTTOM_BUTTON_HEIGHT:
            i += 1
            y += BOX_HEIGHT

            bu = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, 1))
            bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))

            if i < len(active_groups()):
                bu.loadup(active_groups()[i])
                if is_state(MSIDE, MSIDE_LEFT) and is_state(MIDXA, i):
                    bu.set_border('*')

            if i < len(inactive_groups()):
                bf.loadup(inactive_groups()[i])
                if is_state(MSIDE, MSIDE_RIGHT) and is_state(MIDXA, i):
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
            select.place_center_text('(X)')
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
            select.place_center_text('(N)')
            select.place_hcenter_text('Through', ceil(select.h // 2) + 2)
        return box


DELETING = 1 << 0
VIEWING = 1 << 1
EDITING = 1 << 2

VIEW_PROPERTY_COUNT = 6
DESCRIPTION_CHARACTER_LIMIT = 150


class AssignmentsMenu(Menu):
    def get_current_assignment(self) -> BaseAssignment:
        return get_focused_group().in_progress_sorted(state(ASTKY))[state(MIDXA)]

    def pop_if(self) -> bool:
        return is_state(FGRP, NO_FOCUSED_GROUP)

    def __init__(self):
        super().__init__()

        self._field_cache = []
        self._field_callbacks = []

    def reset_cache(self):
        self._field_cache = []

    def menu_display(self):
        focused = groups[state(FGRPS)][state(FGRP)]
        in_progress = focused.in_progress_sorted(state(ASTKY))

        if is_trigger(POP):
            trigger(POP)
            return

        BOX_HEIGHT = 5

        w, h = state(WIDTH), state(LNGTH)
        box = Box(w, h, 3)
        box.set_default_layer(0)

        # assignment viewer
        # todo: maybe allow a property viewer where you
        #       scroll from page to page to view different properties in their entirety
        if state(MACT) & VIEWING:  # todo: show this specific key control somewhere (i.e. (V)iew More)
            selected_idx, index = state(MIDXB), 0

            def get_field(length, callback: Callable = None):
                if index >= len(self._field_cache):
                    field = InputField(length, 1, [1, 2])
                    self._field_cache.append(field)
                    self._field_callbacks.append(callback or no_op)
                    return field
                return self._field_cache[index]

            def try_select(field: InputField, text: str = "", displayed_text: Union[str, None] = None):
                nonlocal index

                field.back_carat()
                field.clear_grid()
                field.clear()
                if index == selected_idx:
                    field.set_border('*')
                    if InputField.FIELD == field:
                        field.clear()
                        field.type(text)  # only called once when menudisplay is used in getfield
                    else:
                        field.place_text(displayed_text or text, (1, 2))
                else:
                    field.set_border_default()
                    field.place_text(displayed_text or text, (1, 2))
                index += 1

            viewbox_width = box.w // 2 + padding // 2
            viewbox = box.place_box(viewbox_width, h, (0, box.w // 2 - padding // 2 + 1), layer=1)
            # five boxes between h - 2 and h + 2
            ypos = lambda t: ilerp(6, h - 8, t)

            # 8 character margin from the left
            left_margin = 4

            assignment: BaseAssignment = self.get_current_assignment()

            # one box for name
            name_width, type_width = 45, 30
            halfsum = (name_width + type_width) // 2

            name = get_field(name_width,
                             lambda: self.get_current_assignment().set_name(name.text))
            name_text = assignment.name
            if len(name_text) >= name_width:
                name_text = name_text[:name_width - 3 - 2] + '...'
            try_select(name, name_text)

            viewbox.place(name, (ypos(0), viewbox_width // 2 - halfsum))

            #  todo: support validation for multiline fields

            # one box for assignment type
            type = get_field(type_width,
                             lambda: self.get_current_assignment().set_type(type.text))
            # else:
            #    assignment.name = type.text
            try_select(type, assignment.type.capitalize())

            viewbox.place(type, (ypos(0), viewbox_width // 2 + (name_width - halfsum)))

            # one box for description

            hmargin = 1
            # todo: fix hmargin
            description_line_width = DESCRIPTION_CHARACTER_LIMIT // 2 - hmargin * 2
            description = assignment.desc

            if len(description) >= description_line_width:  # + 2 for the beginning spaces
                description = description[:description_line_width - 3 - 1] + "..."
            # if len(description) > description_line_width:
            #    description = " " * hmargin + description[:DESCRIPTION_CHARACTER_LIMIT // 2] + " " * hmargin \
            #                + " " * hmargin + description[DESCRIPTION_CHARACTER_LIMIT // 2:] + " " * hmargin
            # else:

            """if len(description) < description_line_width:
                description = " " * hmargin + description + " " * hmargin
            else:
                description_half1 = description[:description_line_width]
                description = " " * hmargin + description_half1 + " " * hmargin

                description_half2 = assignment.desc[description_line_width:description_line_width * 2]
                description += "\n" + " " * hmargin + description_half2 + " " * hmargin"""

            desc = get_field(DESCRIPTION_CHARACTER_LIMIT // 2,
                             lambda: self.get_current_assignment().set_desc(desc.text))
            try_select(desc, assignment.desc, description)

            viewbox.place(desc, (ypos(0.5), viewbox.w // 2 - DESCRIPTION_CHARACTER_LIMIT // 4))

            # one box for start date
            date_width = 20
            DATE_COUNT = 3
            halfsum = (date_width * DATE_COUNT) // 2

            sdate = get_field(date_width,
                              lambda: self.get_current_assignment().set_start_date(sdate.valid_get('dt')))
            try_select(sdate, datetime_to_string(assignment.start_date) if assignment.has_start_date else 'None')

            viewbox.place(sdate, (ypos(1) + 2, viewbox_width // 2 - halfsum))
            viewbox.place_text("Start Date", (ypos(1) + 1, viewbox_width // 2 - halfsum + 1))

            # one box for due date
            ddate = get_field(date_width,
                              lambda: self.get_current_assignment().set_due_date(ddate.valid_get('dt')))
            try_select(ddate, datetime_to_string(assignment.due_date) if assignment.has_due_date else 'None')

            viewbox.place(ddate, (ypos(1) + 2, viewbox_width // 2 - halfsum + date_width))
            viewbox.place_text("Due Date", (ypos(1) + 1, viewbox_width // 2 - halfsum + date_width + 1))

            # one box for interval
            interval = get_field(date_width,
                                 lambda: self.get_current_assignment().set_interval(interval.valid_get('ts')))
            try_select(interval, timedelta_to_string(assignment.interval) if assignment.is_persistent else 'None')

            viewbox.place(interval, (ypos(1) + 2, viewbox_width // 2 - halfsum + 2 * date_width))

            caption = "Interval"
            if not assignment.interval_mprop().simple:
                caption += " (" + str(assignment.interval_mprop().get_index() + 1) + ")"
            viewbox.place_text(caption, (ypos(1) + 1, viewbox_width // 2 - halfsum + 2 * date_width + 1))

        if state(MACT) & DELETING:
            # TODO: find a way to center the warning box
            assignment: BaseAssignment = self.get_current_assignment()

            assignment_type = assignment.type
            assignment_name = assignment.name

            confirm_w, confirm_h = 22 + len(assignment_type) + len(assignment_name), 4

            delete_word = "Delete" if state(WIDTH) % 2 != confirm_w % 2 else "Pop"

            confirm = box.place_box(confirm_w, confirm_h, (box.h // 2 - confirm_h // 2, box.w // 2 - confirm_w // 2),
                                    layer=2)
            confirm_text = f"{delete_word} the {assignment_type} \"{assignment_name}\"?"
            confirm.place_hcenter_text(confirm_text, confirm_h // 2)

            instructions = "Yes (Y) | No (N)" if confirm_w % 2 == 0 else "Yes (Y) or No (N)"
            confirm.place_hcenter_text(instructions, confirm_h // 2 + 1)

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
            "Configure (Q)", 1)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Scheduler (S)", 1)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Groups List (G)", 1)
        box.place_box(padding - 5, button_h, (BUTTON_Y_POSITION(), box.w // 2 - (padding - 5) // 2)).place_hcenter_text(
            "Save & Quit Planner (:qt)", 1)
        BOTTOM_BUTTON_HEIGHT = 5

        y, i = 1, state(MIDXA)
        # supporst (description, due date, start date, etc.)
        while y < box.h - BOTTOM_BUTTON_HEIGHT:
            bu = Box(box.w // 2 - padding // 2 - 2, 1)
            if i < len(in_progress):
                bu.loadup(in_progress[i])
                if i == state(MIDXA):
                    bu.set_border('*')

                    sort_mode = state(ASTKY)
                    if sort_mode is not structs.UNSORTED:
                        bu.place_hcenter_text('Sorted by ' + structs.names[sort_mode], bu.true_h - 1)

            if i == 0:
                bu.place_hcenter_text('Unfinished-Assignments', 0)

            box.place(bu, (y, 1))

            i += 1
            y += bu.true_h

        y, i = 1, 0
        while y < box.h - BOTTOM_BUTTON_HEIGHT:
            bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))
            bf.place_hcenter_text('Finished-Assignments', 0)

            if i < len(focused.completed):
                bf.loadup(focused.completed[i])

            i += 1
            y += BOX_HEIGHT

            bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))

        BOX_TO_ARROW_RATIO = 2
        box_width = box.w // 2 - padding // 2 - 2
        if not TRIGGER_COMMANDS['hdnv']:
            arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, 1))
            arrows.place_hcenter_text("Navigate", 0)

            select = arrows.place_box(box_width // BOX_TO_ARROW_RATIO - 1, BOTTOM_BUTTON_HEIGHT - 2,
                                      (1, 1))
            # arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
            select.place_center_text('Choose (X)')

            sort_mode = arrows.place_box(box_width // BOX_TO_ARROW_RATIO - 1, BOTTOM_BUTTON_HEIGHT - 2,
                                         (1, box_width - box_width // BOX_TO_ARROW_RATIO + 1))
            sort_mode.place_center_text("Sort (S)")
            # select.

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

    def get_map(self):
        def edit_assignment(index: int):
            assignment = get_focused_group().in_progress[index]  # TODO: support completed
            FUNCTIONS[ADAED](assignment)

        def remove_assignment():
            state(MACT, state(MACT) | DELETING)

            # change action state

        def confirm_delete():
            if state(MACT) & DELETING:
                state(MACT, state(MACT) ^ DELETING)
                group = get_focused_group()
                index = group.in_progress.index(self.get_current_assignment())
                group.remove_assignment_at(index)
                if index == group.in_progress_count:
                    state(MIDXA, state(MIDXA) - 1)

        def reset_delete():
            if state(MACT) & DELETING:
                state(MACT, state(
                    MACT) ^ DELETING)  # removes deleting instead of setting to normal (may be viewing or doing something else)

        def on_down():
            if is_state(MIDXB, UNUSED_MIDX_START):
                next_idx = min(len(get_focused_group().in_progress) - 1, state(MIDXA) + 1)
                state(MIDXA, next_idx)
            else:
                state(MIDXB, min(state(MIDXB) + 1, VIEW_PROPERTY_COUNT - 1))

        def on_up():
            if is_state(MIDXB, UNUSED_MIDX_START):
                next_idx = max(0, state(MIDXA) - 1)
                state(MIDXA, next_idx)
            else:
                state(MIDXB, max(state(MIDXB) - 1, UNUSED_MIDX_START))

        def on_right():
            if state(MIDXB) < 0 and (state(MACT) & VIEWING):
                state(MIDXB, 0)

        def on_v():
            state(MACT, state(MACT) | VIEWING if not state(MACT) & VIEWING else state(MACT) ^ VIEWING)
            if ~state(MACT) & VIEWING:
                state(MIDXB, UNUSED_MIDX_START)

        def on_spacebar():
            if is_state(MIDXB, UNUSED_MIDX_START):
                on_v()
            else:
                on_any_key(SPACEBAR)

        def on_any_key(key):
            if not (state(MACT) | VIEWING) \
                    or key in (b'=', b'-'):
                return None
            if not is_state(MIDXB, UNUSED_MIDX_START) and (state(MACT) | VIEWING):
                if key not in [BACKSPACE, SPACEBAR]:
                    if is_key_special(key) or key == b'v':
                        return None
                field = self._field_cache[state(MIDXB)]
                get_field(field)  # , on_delete=lambda: ignore_margin or on_change_callback, on_type=on_change_callback)
                self._field_callbacks[state(MIDXB)]()
                return 1
            # returns None

        def on_x():
            state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED)

        def on_s():
            state(ASTKY, (state(ASTKY) + 1) % structs.SORT_COUNT)

        def on_plus():
            if state(MACT) & VIEWING:
                if not is_state(MIDXB, UNUSED_MIDX_START):
                    if state(MIDXB) == 5:
                        self.get_current_assignment().interval_mprop().next()

        def on_minus():
            if state(MACT) & VIEWING:
                if not is_state(MIDXB, UNUSED_MIDX_START):
                    if state(MIDXB) == 5:
                        self.get_current_assignment().interval_mprop().prev()

        return InputMap(
            {  # inputs (covered by getch)
                ANY_KEY: on_any_key,
                b'q': lambda: FUNCTIONS[CNFGA](),
                b's': on_s,
                b'x': on_x,
                b'l': lambda: state(MSIDE, MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED),
                b'g': lambda: trigger(POP) or trigger(REFRS),
                DOWN: on_down,  # if not is_state(MSIDE, MSIDE_UNDECIDED) else MIDXA),
                UP: on_up,  # if not is_state(MSIDE,,  # MSIDE_UNDECIDED) else MIDXA),
                b'c': lambda: FUNCTIONS[ADA]() or reset_menu_selection(),
                BACKSPACE: remove_assignment, b'y': confirm_delete, b'n': reset_delete,
                b'v': on_v,  # todo: show this specific key control somewhere (i.e. (V)iew More)
                SPACEBAR: on_v,
                RIGHT: on_right,
                b'=': on_plus,
                b'-': on_minus
                #    b'e': conditions_menu,
                #    b's': scheduler_menu,
            },
            {  # commands (inputted manually)
                #    'qt': quit_menu,
                #    'cl': clear_all_data,
            }, any_key_pre=True)


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
        bx = box.place_box(w // 2, h // 3, (h // 3, state(WIDTH) // 4))
        bx.set_border('*')
        bx.place_hcenter_text("Are you sure you want to quit?", bx.h // 2 - 1, "Quit (Y)", bx.h // 2, "Return (N)",
                              bx.h // 2 + 1)
        return box


def has_focused_group() -> bool:
    if state(FGRP) == NO_FOCUSED_GROUP:
        return False
    return True


def get_focused_group() -> Group:
    try:
        return groups[state(FGRPS)][state(FGRP)]
    except IndexError:
        return None


BUTTON_COLUMN, FIELD_COLUMN = 1, 2


class Property:
    def __init__(self, caption, width, category, type, next_line=False):
        self.caption = caption
        self.width = width
        self.category = category
        self.type = type
        self.next_line = next_line

    def total_width(self):
        return len(self.caption) + CAPTION_BOX_SPACING + self.width

    @property
    def prebox_spacing(self):
        return self.total_width() - self.width


MAX_BUTTONS_PER_PAGE = 5


class EditorProperty(Property):
    def __init__(self, caption: str, width: int, category: str, type: str, enabled: bool, next_line: Union[bool, None]=False):
        super().__init__(caption, width, category, type, next_line)
        self.enabled = enabled
        self.field: Union[InputField, None] = None

    def build(self):
        self.field = InputField(self.width, 1, [1, 2])

    def get_value(self):
        return self.field.get(self.type)


class AssignmentEditor(Menu):
    def on_space(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MIDXA) < len(self.fields):
            midx = state(MIDXA)
            field = self.fields[midx].field
            get_field(field)
            if field.validate(self.fields[midx].type) and state(MIDXA) != MAX_BUTTONS_PER_PAGE - 1:
                self.find_index(1)
        else:
            self.on_enter()

    def on_enter(self):
        if is_state(MIDXA, len(self.fields)):  # indicates create new assignment button
            # name, description, start_date, due_date, increment, type
            assignment = BaseAssignment(MP(), MP(), MP(), MP(), MP(), MP())
            for i, field in enumerate(self.fields):
                if self.fields[i].enabled is not False:
                    if self.fields[i].caption == "Interval":
                        interval = self.fields[i].field.get('ts')
                        assignment.push_interval(interval)
                    elif self.fields[i].caption == "Name":
                        name = self.fields[i].field.get()
                        assignment.push_name(name)
                    elif self.fields[i].caption == "Description":
                        desc = self.fields[i].field.get()
                        assignment.push_desc(desc)
                    elif self.fields[i].caption == "Due Date":
                        due_date = self.fields[i].field.get('dt')
                        assignment.push_due_date(due_date)
                    elif self.fields[i].caption == "Start Date":
                        start_date = self.fields[i].field.get('dt')
                        assignment.push_start_date(start_date)
                    elif self.fields[i].caption == "Type":
                        type = self.fields[i].field.get()
                        assignment.push_type(type)
                    else:
                        raise NameError("One or more captions in the Property Catalog have an incorrect caption.")
            get_focused_group().add_assignment(assignment)
            poprefrs()
        elif is_state(MSIDE, BUTTON_COLUMN):
            if self.fields[state(MIDXA)].enabled is not None:
                self.fields[state(MIDXA)].enabled = not self.fields[state(MIDXA)].enabled

    def find_index(self, delta: int):
        d = delta // abs(delta)
        i = state(MIDXA)
        if not is_state(MSIDE, MSIDE_UNDECIDED):
            check = False if is_state(MSIDE, FIELD_COLUMN) else None
            while True:
                i += d
                if 0 <= i <= len(self.fields):
                    if i == len(self.fields) or self.fields[i].enabled is not check:
                        state(MIDXA, i)
                        break
                else:
                    break

    def switch_sides(self, side: int):
        if 0 > state(MIDXA) or state(MIDXA) >= len(self.fields):
            return
        state(MSIDE, side)
        if not is_state(MSIDE, MSIDE_UNDECIDED):
            check = None if is_state(MSIDE, BUTTON_COLUMN) else False
            if self.fields[state(MIDXA)].enabled is check:
                i = state(MIDXA)  # we default to the top button
                for n in range(1, len(self.fields)):
                    if 0 <= i + n < len(self.fields):
                        if self.fields[i + n].enabled is not check:
                            state(MIDXA, i + n)
                            return

                    if 0 <= i - n < len(self.fields):
                        if self.fields[i - n].enabled is not check:
                            state(MIDXA, i - n)
                            return

    def on_any_key(self, key):
        if is_state(MSIDE, FIELD_COLUMN) and state(MIDXA) < len(self.fields):
            if key != ENTER:
                field = self.fields[state(MIDXA)].field
                field.front_carat()
                if key != BACKSPACE:
                    field.type(key)
                else:
                    field.delete(len(field.text))
            self.on_space()

    def on_ctrl_c(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MIDXA) < len(self.fields):
            global clipboard
            clipboard = self.fields[state(MIDXA)].field.text

    def on_ctrl_v(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MIDXA) < len(self.fields):
            self.fields[state(MIDXA)].type(clipboard)

    def on_del(self):
        del self.fields[state(MIDXA)]

    def on_p(self):
        midxa = state(MIDXA)
        property = FUNCTIONS[PRCAT]()
        if property:
            eproperty = EditorProperty(property.caption, property.width, property.category, property.type, True)
            state(MIDXA, midxa)
            self.insert_property(midxa, eproperty)

    def get_map(self):
        def default_to_field_column():
            if is_state(MSIDE, MSIDE_UNDECIDED):
                state(MSIDE, FIELD_COLUMN)
                return False
            return True

        return InputMap({
            ANY_KEY: self.on_any_key,
            UP: lambda: default_to_field_column() and self.find_index(-1),
            # state(MIDXA, clamp(state(MIDXA) - 1, 0, len(captions) - 1)),
            DOWN: lambda: default_to_field_column() and self.find_index(1),
            # state(MIDXA, clamp(state(MIDXA) + 1, 0, len(captions) - 1)),
            RIGHT: lambda: self.switch_sides(FIELD_COLUMN),
            LEFT: lambda: self.switch_sides(BUTTON_COLUMN),
            COPY: self.on_ctrl_c,
            PASTE: self.on_ctrl_v,
            ENTER: self.on_enter,
            SPACEBAR: self.on_space,
            DEL: self.on_del,
            b'p': self.on_p,  # TODO: make this open the property catalog instead of adding an interval property
            #  TODO: allow for the deleting of properties once added
        }, {})

    def __init__(self):
        super().__init__()
        self.actives: list[bool] = []

        self.fields: list[EditorProperty] = [
            EditorProperty("Name", NAME_WIDTH, "Name", "str", None),
            EditorProperty("Type", NAME_WIDTH, "Type", "str", None),
            EditorProperty("Description", MAX_PROPERTY_GROUP_WIDTH, "Desc", "str", True),
            EditorProperty("Start Date", DATETIME_WIDTH, "Start Date", "dt", True),
            EditorProperty("Due Date", DATETIME_WIDTH, "Due Date", "dt", True),
            EditorProperty("Interval", TIMEDELTA_WIDTH, "Interval", "ts", False),
        ]

    def insert_property(self, idx, property):
        self.fields.insert(idx, property)
        self.build_field(idx)

    def build_field(self, idx):
        self.fields[idx].build()

    def menu_display(self):
        screen_share = 2 / 3
        box_length = 3
        margin_x = 2

        w, h = state(WIDTH), state(LNGTH)
        bx = Box(w, h)
        bx.place_hbar(0, 19)
        bx.place_vbar(0, 132)

        if has_focused_group():
            focused = get_focused_group()
            bx.place_text(focused.name, (bx.h - 1, bx.w - len(focused.name) - 2))

        BOX_HEIGHT = 3
        OBJECT_SPACEOUT = 1 + margin_x + box_length * 2 + 1

        page = max(0, state(MIDXA)) // MAX_BUTTONS_PER_PAGE
        if state(MIDXA) == len(self.fields) and state(MIDXA) % MAX_BUTTONS_PER_PAGE == 0:
            page -= 1

        page_count = (len(self.fields) - 1) // MAX_BUTTONS_PER_PAGE
        #  TODO: may need to expand the algorithm to support buttons with h > 1
        #  TODO: need to expnad the algorithm to support row-grouping by category

        formatted_page_count = str(page_count + 1) if page_count + 1 > 10 else '0' + str(page_count + 1)
        formatted_page = str(page + 1) if page + 1 > 10 else '0' + str(page + 1)
        bx.place_hcenter_text(f"{formatted_page} / {formatted_page_count}", bx.h)

        for f in range(page * 5, (page + 1) * 5):
            if f >= len(self.fields):
                break
            field: EditorProperty = self.fields[f]
            i = f - page * 5

            caption = field.caption
            if field.enabled is not None:
                active = bx.place_box(box_length, 1, ((i + 1) * BOX_HEIGHT - 1, 1 + margin_x))
                if field.enabled:
                    active.place_center_text('X')
                if is_state(MSIDE, BUTTON_COLUMN) and is_state(MIDXA, f):
                    active.set_border('*')
            elif is_state(MSIDE, BUTTON_COLUMN) and is_state(MIDXA, f):
                state(MIDXA, state(MIDXA) + 1)  # +=1 until reach one that has a trigger

            name = caption + ": "
            bx.place_text(name, ((i + 1) * BOX_HEIGHT, 1 + OBJECT_SPACEOUT))

            if not field.field:
                field.build()
            ifield = field.field
            bx.place(ifield,
                     ((i + 1) * BOX_HEIGHT - 1, 2 + OBJECT_SPACEOUT + len(caption) + 1))  # name

            ifield.set_border_default()
            if is_state(MSIDE, FIELD_COLUMN):
                if f == state(MIDXA):
                    if field.enabled or field.enabled is None:
                        ifield.set_border('*')
                    else:
                        state(MIDXA, state(MIDXA) - 1)
        # Enter Button
        enter_w = w // 3
        enter_h = 1
        enter_center_y = 1  # from the bottom of the screen
        enter = bx.place_box(enter_w, 1, (h - 1 + enter_h - 2 - enter_center_y, enter_w))  # + 2 for borders
        enter.place_center_text("Create New Assignment")
        if is_state(MIDXA, len(self.fields)):  # goes over
            enter.set_border('*')
        return bx


MAX_PROPERTY_GROUP_WIDTH = 90
CAPTION_BOX_SPACING = 2
PROPERTY_GROUP_MEMBER_SPACING = 4
DATETIME_WIDTH = 24
TIMEDELTA_WIDTH = 24
NAME_WIDTH = 30
INTEGER_WIDTH = 6
BOOL_WIDTH = 3


class PropertyCatalog(Menu):
    def __init__(self):
        super().__init__()
        self.properties = [
            # Interval properties
            Property("Interval", TIMEDELTA_WIDTH, "Interval", 'ts'),
            Property("Interval Count", INTEGER_WIDTH, "Interval", 'int'),
            #                      Property("Interval Mode", INTEGER_WIDTH, "Interval"),

            # Due Date properties
            Property("Due Date", DATETIME_WIDTH, "Due Date", 'dt'),
            Property("Due Date Count", INTEGER_WIDTH, "Due Date", 'int'),

            # Start Date properties
            Property("Start Date", DATETIME_WIDTH, "Start Date", 'dt'),
            Property("Start Date Count", INTEGER_WIDTH, "Start Date", 'int'),
        ]

    #  Properties that are similar to each other
    #  May be grouped into a single row under
    #  the following conditions
    #  The sum of all widths and caption character
    #  counts + CAPTION_BOX_SPACING of the properties
    #  is less than MAX_PROPERTY_GROUP_WIDTH

    #  The properties have the same Category

    #  The proceeding property has next_line set to False.
    #  If properties that are not similar to each
    #  other appear next to each other,
    #  they will be placed on an individual row.

    #  Plan: Sort the array of properties by
    #  Category. Place whitespace to differentiate
    #  between prooperties of differing categories.

    #  TODO: Support Properties in the Assignment Editor
    #  TODO: support dropdown menus
    def menu_display(self):
        bx = Box(state(WIDTH), state(LNGTH))

        group = get_focused_group()
        if group is not None:
            bx.place_text(group.name, (bx.h - 1, bx.w - len(group.name) - 1))
        top_margin, bottom_margin = 1, 1
        left_margin = 8
        box_height = 3

        line_idx = 0
        page = 0

        line_width = 0
        line_category = ""
        for i, property in enumerate(self.properties):
            if not line_category:
                line_category = property.category
            y = 1 + top_margin + line_idx * box_height
            if property.next_line or property.category != line_category or line_width + property.total_width() > MAX_PROPERTY_GROUP_WIDTH:
                line_idx += 1
                y = 1 + top_margin + line_idx * box_height
                if y >= bx.h - bottom_margin:
                    #  TODO: next page functionality
                    #  Start off from a different page
                    #  Possibly store the index of the last property of the previous page
                    #       This would complicate the direct changing of pages
                    #  Possibly manually calculate the first index iteratively
                    break
                line_width = 0
                line_category = property.category

            x = left_margin + line_width
            bx.place_text(property.caption, (y + 1, x))
            box = bx.place_box(property.width, 1, (y, x + property.prebox_spacing))
            if state(MIDXB) == i:
                box.set_border('*')
            line_width += property.total_width() + 2 + PROPERTY_GROUP_MEMBER_SPACING  # two is for borders
        page_count = 0

        formatted_page_count = str(page_count + 1) if page_count + 1 > 10 else '0' + str(page_count + 1)
        formatted_page = str(page + 1) if page + 1 > 10 else '0' + str(page + 1)
        bx.place_hcenter_text(f"{formatted_page} / {formatted_page_count}", bx.h - bottom_margin + 1)
        return bx

    def show(self):
        if not self.preshow():
            return

        box = self.menu_display().bake()
        print(box)

        output: Union[None, Property] = self.map.run()
        if isinstance(output, Property):  # if property
            return output
        else:
            return self.show()

    def delta_midxb(self, delta):
        state(MIDXB, state(MIDXB) + delta)
        if not (0 <= state(MIDXB) < len(self.properties)):
            state(MIDXB, clamp(state(MIDXB), 0, len(self.properties) - 1))

    def output(self):
        return self.properties[state(MIDXB)]

    def get_map(self):
        return InputMap({
            UP: lambda: self.delta_midxb(-1),
            DOWN: lambda: self.delta_midxb(1),
            SPACEBAR: self.output
        }, {})


class Configuration(EditorProperty):
    def __init__(self, caption: str, width: int, category: str, type: str, get: Callable, set: Callable,
                 next_line: bool = False):
        super().__init__(caption, width, category, type, None, next_line)
        self.get = get
        self.set = set

    def update(self):
        if InputField.FIELD != self.field:
            self.field.clear()
            self.field.type(self.get())


class ConfigureAssignment(Menu):
    def __init__(self):
        super().__init__()
        CON = Configuration
        self.properties: list[Configuration] = [
            CON("Random Alert Min. Freq", INTEGER_WIDTH, "Random Alert", 'int', lambda: str(alerts.min_rand_interval // 60),
               lambda p: alerts.set_min_rand_interval(p.get_value() * 60)), # desc: "The minimum time in minutes between random alerts."
            CON("Random Alert Max. Freq", INTEGER_WIDTH, "Random Alert", 'int', lambda: str(alerts.max_rand_interval // 60),
               lambda p: alerts.set_max_rand_interval(p.get_value() * 60)), # desc: "The maximum time in minutes between random alerts."
            CON("Normal Alert Voice", INTEGER_WIDTH, "Voices", 'int', lambda: str(state(VALRT)),
               lambda p: state(VALRT, clamp(p.get_value(), 0, 1))),  # desc: The voice heard when a random alert is triggered. 0 for MALE, 1 for FEMALE.
            CON("Random Alert Voice", INTEGER_WIDTH, "Voices", 'int', lambda: str(state(VRALR)),
                lambda p: state(VRALR, clamp(p.get_value(), 0, 1))), # desc: The voice heard when a random alert is triggered. 0 for MALE, 1 for FEMALE.
            CON("Alerts On", BOOL_WIDTH, "Alerts", 'bool', lambda: x_or_space(not is_state(NOTIF, ALROFF)), lambda p: state(NOTIF, ALROFF if not is_state(NOTIF, ALROFF) else ALRON)),
            CON("Voices On", BOOL_WIDTH, "Alerts", 'bool', lambda: x_or_space(state(NOTIF) & VOICES_ONLY), lambda p: state(NOTIF, state(NOTIF) ^ VOICES_ONLY)),
            CON("Popups On", BOOL_WIDTH, "Alerts", 'bool', lambda: x_or_space(state(NOTIF) & POPUPS_ONLY),
                lambda p: state(NOTIF, state(NOTIF) ^ POPUPS_ONLY)),
        ]

    def menu_display(self):
        box = Box(state(WIDTH), state(LNGTH), 3)
        box.set_default_layer(0)

        group = get_focused_group()
        if group is not None:
            box.place_text(group.name, (box.h - 1, box.w - len(group.name) - 1), index=2)

        top_margin, bottom_margin = 1, 1
        left_margin = 8
        box_height = 3

        line_idx = 0
        page = 0

        line_width = 0
        line_category = ""
        for i, config in enumerate(self.properties):
            property = config
            if not line_category:
                line_category = property.category
            y = 1 + top_margin + line_idx * box_height
            if property.next_line or property.category != line_category or line_width + property.total_width() > MAX_PROPERTY_GROUP_WIDTH:
                line_idx += 1
                y = 1 + top_margin + line_idx * box_height
                if y >= box.h - bottom_margin:
                    #  TODO: next page functionality
                    #  Start off from a different page
                    #  Possibly store the index of the last property of the previous page
                    #       This would complicate the direct changing of pages
                    #  Possibly manually calculate the first index iteratively
                    break
                line_width = 0
                line_category = property.category

            x = left_margin + line_width
            box.place_text(property.caption, (y + 1, x))

            if not config.field:
                config.build()
            ifield = config.field
            config.update()
            if state(MIDXA) == i:
                ifield.set_border('*')
            else:
                ifield.set_border_default()

            box.place(ifield, (y, x + property.prebox_spacing))  # name

            # sbx = box.place_box(property.width, 1, (y, x + property.prebox_spacing))
            line_width += property.total_width() + 2 + PROPERTY_GROUP_MEMBER_SPACING  # two is for borders

            # if is_state(MSIDE, FIELD_COLUMN):
            #    if i == state(MIDXA):
            #        if config.enabled or config.enabled is None:
            #            ifield.set_border('*')
            #        else:
            #            state(MIDXA, state(MIDXA) - 1)
        page_count = 0

        formatted_page_count = str(page_count + 1) if page_count + 1 > 10 else '0' + str(page_count + 1)
        formatted_page = str(page + 1) if page + 1 > 10 else '0' + str(page + 1)

        box.place_hcenter_text(f"{formatted_page} / {formatted_page_count}", box.h - bottom_margin + 1)

        if state(MACT) & VIEWING and not is_state(MIDXA, UNUSED_MIDX_START):
            selected = self.properties[state(MIDXA)]
            box.set_default_layer(1)
            bx = box.place_box(box.w // 3, box.h, (0, box.w - box.w // 3))
            bx.place_text(limit_width_smart_break(selected.description, bx.w - 1), (1, 2))
        return box

    def get_map(self):
        def on_varrow(delta):
            state(MIDXA, clamp(state(MIDXA) + delta, UNUSED_MIDX_START, len(self.properties) - 1))

        def on_space():
            field = self.properties[state(MIDXA)]
            if field.type == 'bool':
                pass  # is a trigger, set should be ON and OFF
            elif field.type == 'ddown':
                pass
            else:
                get_field(field.field)
            field.set(field)

        return InputMap(
            {  # inputs (covered by getch)
                b'y': lambda: quit(0),
                b'n': lambda: trigger(POP) or trigger(REFRS),
                b'v': lambda: state(MACT, state(MACT) ^ VIEWING),
                UP: lambda: on_varrow(-1),
                DOWN: lambda: on_varrow(1),
                SPACEBAR: on_space
                #    b'a': actions_menu,
                #    b'e': conditions_menu,
                #    b's': scheduler_menu,
            },
            {  # commands (inputted manually)
                #    'qt': quit_menu,
                #    'cl': clear_all_data,
            })


# class SchedulerMenu(Menu):
#    def get_map(self):

commands = ('cl', 'qt')


def run(output: bool, *cmdss: list[str]):
    out = []
    for cmds in cmdss:
        COMMAND_HISTORY.append(':' + " ".join(cmds))

        cmd = cmds[0]
        if cmd in TRIGGER_COMMANDS:
            TRIGGER_COMMANDS[cmd] = not TRIGGER_COMMANDS[cmd]
            #  trigger(REFRS, True)  # refresh the screen
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
        if output:
            out.append(cmds)
    if out:
        if len(out) > 1:
            return out
        return out[0]


def get_input(init: str = "", **specials) -> Union[bytes, str, None]:
    # if TRIGGER_COMMANDS[REFRS]:
    #    trigger(REFRS)
    #    return None

    block_cmds = specials.get('block_cmds', False)
    print('-:> ', end="")
    key = getch() if not init else init[0].encode('ascii')

    if key == SPECIAL:  # precedes special character; use getch() again
        # todo: check for esc
        spcl = getch()
        if is_trigger(INPCL):
            print('\r', end="")
        return key + spcl
    elif key == b':' and not block_cmds:
        MAX_COMMAND_SIZE: int = 5
        if is_trigger(INPCL):
            print('\r', end="")
        prompt = "-:> :"
        cmds: list[str] = [init[1:]]
        count = 0

        def clearline():
            if is_trigger(INPCL):
                print('\r' + ' ' * 25 + '\r', end="")

        while True:
            print(prompt + " ".join(cmds), end="")

            ch = getch()
            if ch == SPECIAL:  # precedes special character; use getch() again
                # todo: check for esc
                pass
            elif ch == b';':
                run(True, cmds)
                clearline()
                if is_trigger(INPCL):
                    print("\r", end="")
                return get_input()
            elif ch == BACKSPACE:  # backspace
                if cmds:
                    cmds[-1] = cmds[-1][:len(cmds[-1]) - 1]
                    if len(cmds) > 1 and not cmds[-1]:
                        cmds = cmds[:len(cmds) - 1]
            elif ch == ENTER:  # user presses enter
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
        if is_trigger(INPCL):
            print('\r', end="")
        return key  # key.decode('ascii').lower()


HDNV = 'hdnv'  # hide navigation menu
REFRS = 'refrs'  # refresh the current menu
POP = 'pop'  # pop the current menu (can be used to quit from the group menu)
DEBUG = 'debug'  # enter debug mode (counts empty spaces and shows origins for each element)
PMDEF = 'pmdef'  # whether pm is default or not
NOMIN = 'nomin'  # toggles minimizing on due date alert
WARNS = 'warns'  # toggles ui warnings
CFMDE = 'cfmde'  # toggles "confirm delete assignment" popup before removing an assignment
INPCL = 'inpcl'  # toggles whether input clears the terminal
TRIGGER_COMMANDS = {
    'hdnv': False,
    REFRS: False,
    POP: False,
    DEBUG: False,
    PMDEF: True,
    NOMIN: False,
    WARNS: False,
    CFMDE: False,
    INPCL: True,
}


def trigger(s: str, val: bool = None):
    if val is not None:
        TRIGGER_COMMANDS[s] = val
    else:
        TRIGGER_COMMANDS[s] = not TRIGGER_COMMANDS[s]


def is_trigger(s: str):
    return TRIGGER_COMMANDS[s]


def poprefrs():
    trigger(POP)
    trigger(REFRS)


def lit():
    if not InputField.FIELD:
        return
    else:
        input('\'' + InputField.FIELD.text + '\'')


MSIDE = 'mside'  # the side of the menu (left, right, middle, etc.)
MIDXA = 'midxa'  # the 1st index of the menu for the current side (used for lists)
MIDXB = 'midxb'  # the 2nd index of the menu for the current side (used for lists)
WIDTH = 'width'  # the current width of the screen
LNGTH = 'lngth'  # the current height (or length) of the screen
FGRP = 'fgrp'  # the index of the focused group for active or inactive
FGRPS = 'fgrps'  # the type of focused group (active or inactive)
NO_FOCUSED_GROUP = -1
ACTIVE_GROUPS, INACTIVE_GROUPS = range(2)
MACT = 'mact'  # bit field representing the action state of the current menu (deleting, viewing, etc.).
NO_ACTION = 0
VALRT = 'valrt'  # the gender of the tts voice for normal alerts
VRALR = 'vralr'  # the gender of the tts voice for random alerts
ASTKY = 'astky'  # the key used to sort assignments

ALROFF = 0b00
POPUPS_ONLY = 0b01
VOICES_ONLY = 0b10
ALRON = 0b11
NOTIF = 'notif'  # the bit field representing the notification mode (0 for both, 1 for no voice, 2 for no notification, 3 for neither)

STATE_COMMANDS = {
    MSIDE: 0,  # menu side (-1: left, 0: unselected, 1: right)
    MIDXA: 0,  # menu index (0: first tab, n: (n + 1)th tab)
    MIDXB: 0,  # second menu index (0: first tab, n: (n + 1)th tab)
    WIDTH: 0,
    LNGTH: 0,
    FGRP: NO_FOCUSED_GROUP,
    FGRPS: ACTIVE_GROUPS,
    MACT: 0,
    VRALR: 1,  # 0 for male, 1 for female
    VALRT: 0,  # the gender of the tts voice for normal alerts
    ASTKY: structs.UNSORTED,  # keys can be found in structs.py
    NOTIF: ALRON  # by default, both voice and notification are on
}

RMENU = 'rmenu'
GROUP = 'group'
group_menu = GroupsMenu()
ASSGN = 'assgn'
assignments_menu = AssignmentsMenu()
QT = 'qt'
quit_menu = QuitMenu()
ADA = 'ada'
ADAED = 'adaed'
assignment_editor = AssignmentEditor()
OUTPT = 'outpt'
FQT = 'fqt'
TRIGG = 'trigg'
ATRIG = 'atrig'
LIT = 'lit'
SAVE = 'save'
INCRA = 'incra'
property_catalog = PropertyCatalog()
PRCAT = 'prcat'
configure_assignment = ConfigureAssignment()
CNFGA = 'cnfga'
FUNCTIONS: dict[str, Callable] = {
    RMENU: reset_menu_selection,
    GROUP: lambda: reset_menu_selection() or group_menu.show(),
    ASSGN: lambda: reset_menu_selection() or assignments_menu.show(),
    QT: quit_menu.show,
    FQT: lambda: quit(0),
    OUTPT: input,
    TRIGG: lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if is_trigger(i)])),
    ATRIG: lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if not is_trigger(i)])),
    ADA: lambda: reset_menu_selection() or assignment_editor.show(),  # goes to assignment editor
    ADAED: lambda a: reset_menu_selection() or assignment_editor.show(a),
    LIT: lit,
    SAVE: savedata.save_all,
    INCRA: structs.increment_all_persistent,
    PRCAT: lambda: reset_menu_selection() or property_catalog.show(),
    CNFGA: lambda: reset_menu_selection() or configure_assignment.show()
}

if __name__ == "__main__":  # these functions cause a circular dependency when ui.py is the main file
    RCACH = 'rcach'
    FUNCTIONS.update({
        RCACH: alerts.clear_cache
    })


def initial_commands():
    run(False,
        ["lngth", STARTING_DIMENSIONS[0]],
        ["width", STARTING_DIMENSIONS[1]],
        [INCRA],
        [INPCL])


def ui():
    run(False,
        ["lngth", STARTING_DIMENSIONS[0]],
        ["width", STARTING_DIMENSIONS[1]],
        [INCRA])
    while True:
        try:
            group_menu.show()
            print("YEEHEAHHAAHAHAHAHAHAHAHAHAHAHA")
        except Exception as e:
            print(e)
            header = "COMMAND HISTORY"
            print('-' * len(header),
                  header,
                  '-' * len(header),
                  *COMMAND_HISTORY,
                  '-' * len(header), sep="\n")

            inp = get_input(':')
            if inp and inp[0] == "catch":
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
4. The while loop must terminate when getch() == b'\n' (carriage return).

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
    elif ch == b'\n':
        break
    else:
        field.type(ch)

"""

clipboard = ""


# 's' - string
# 'd' - date
# 't' - time
# 'dt' - datetime
def no_op():
    pass


# todo: callback on finish
# assumption: field is a single line input field
def get_field(field: InputField, **callbacks):
    on_delete, on_type = callbacks.get("on_delete", no_op), callbacks.get("on_type", no_op)

    InputField.FIELD = field
    field.displaying = False
    menu = MENU.menu_display()
    while True:
        if is_trigger(POP):
            trigger(POP, False)
            break
        if is_trigger(INPCL):
            clear()
        print(menu.bake())
        ch = get_input(block_cmds=True)
        if isinstance(ch, bytes):
            if ch == ENTER:
                InputField.FIELD = None
                break
            elif ch == BACKSPACE:
                if len(field.text) > 0:
                    field.delete(1)
                    on_delete()
                continue
            elif ch == b'`':
                cmd = get_input(':')
                if not cmd:
                    continue
                if cmd[0] == 'ccase':
                    if len(cmd) == 1 or cmd[1] == 't':  # title case
                        text = list(field.text)
                        ttext = ""
                        for i, ch in enumerate(text):
                            if i == 0 or text[i].isalpha() and not text[i - 1].isalpha():
                                ttext += text[i].upper()
                            else:
                                ttext += text[i]
                        field.clear()
                        field.type(ttext)
                        continue
            elif len(ch) > 0 and ch[0] == ord(SPECIAL):
                if ch in (UP, DOWN):
                    continue  # TODO: Indexing through field, moving carat
                elif ch == RIGHT:
                    field.shift_carat(1)
                elif ch == LEFT:
                    field.shift_carat(-1)
                continue
            char = ch.decode('ascii')
            field.type(char)
            on_type()
    return field.text


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

#  Property Catalog

# Action Menu:
#  At the far left side, the action options
#  At the right side, group and assignment selection options

COMMAND_HISTORY = []

MENU: Menu = None
STARTING_DIMENSIONS = ("20", "133")

if __name__ == "__main__":
    display = Box(1, 3)
    initial_commands()
    configure_assignment.show()

    # button_width = 30
    # w, h = state(WIDTH), state(LNGTH)
    # display = Box(state(WIDTH), state(LNGTH), 2)
    # display.place_hbar(h - h // 6, layer=1)
    #  display.place_vbar(button_width, length=h - h // 6)
    # print(display.bake())

# WORK ON PRIORITY TYPES!
# be able to add priority types
