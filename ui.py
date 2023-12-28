# Design Philosophy

# Every menu should be able to work independently of each other.

# Menus will base their functionalities off of the current context
# of the entire program.

# TODO: callbacks for input fields
#       submenus
#       assignment editing

from typing import Union, Callable, Sequence

from msvcrt import getch

import time
from datetime import datetime, timedelta

import alerts

from structs import BaseAssignment, Group, active_groups, inactive_groups

import savedata

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

def now(**replacements) -> datetime: 
    replacements.setdefault('second', 0)
    replacements.setdefault('microsecond', 0)
    return datetime.now().replace(**replacements)


#  Options:

MONTH_MAX = 12
def parse_date(string: str) -> datetime:
    delimiter = ''
    for ch in string:
        if not ch.isalnum():
            delimiter = ch
            break
    if delimiter:
        tokens = string.split(delimiter)
    else: # no delimiter => tokens are packed together => divisible by either 2 or 3
        tokens = []
        i = 0
        if len(string) % 3 == 0:
            if string[2].isalpha():
                token_size = 3
            else:
                token_size = 2
        elif len(string) % 2 == 0:
            token_size = 2
        else:
            raise ValueError("Parameter is in an invalid format.")
        while i < len(string):
            tokens.append(string[i:i + token_size])
            i += token_size
        print("DATES: ", tokens)

    start = tokens[0] # the start must be consistent for the rest of the tokens
    if len(start) == 2: # inferred date path
        if len(tokens) == 2: # month-day path
            month, day = int(tokens[0]), int(tokens[1])
            return now(month=month, day=day)
        elif len(tokens) == 3: # year-month-day path
            month, day, year = map(lambda t: int(t), tokens)
            print(month)
            return now(year=2000 + year, month=month, day=day)
    elif len(start) == 3: # noninferred date path; symbols are specified
        datetkns = {'D':now().day, 'Y':now().year - 2000, 'M':now().month} # day, year, month
        for token in tokens:
            if token[-1] in datetkns:
                tk = token[-1]
                datetkns[tk] = int(token[:len(token) - 1])
        return now(year=2000 + datetkns['Y'], month=datetkns['M'], day=datetkns['D'])

# DATES
# CONTEXT OF ANNOTATIONS: WHEN USED AS A START/DUE DATE
#  XXXXXX OR XX(D)XX(D)XX OR XXMXXDXXY (given day of the given month of the given year)
parse_date("120423")
parse_date("04-12-12")
parse_date("11M24D23Y")
parse_date("03D21Y10M")
#  XXY(D)XXM (end of the given month of the current year)
parse_date("23Y04M")
parse_date("03M06Y")
#  XXY(D)XXD (day of the same month in the current year)
parse_date("12D23Y")
parse_date("42Y04D")
#  XXXX OR XXD(D)XXM OR XX(D)XX OR XXDXXM (given day in the given month in the current year)
parse_date("0830")
parse_date("13D/06M")
parse_date("12M/25D")
parse_date("04M12D")
#  XXY (current day and month of the given year)
parse_date("23Y")
#  XXM (current day of the given month of the current year)
parse_date("12M")
#  XXD (given day of the current month of the current year)
parse_date("24D")


def parse_time(string: str) -> datetime:
    ending_chars = string[len(string) - 2:]
    is_pm = True  # trigger(PMDEF)
    if ending_chars.isalpha():
        is_pm = ending_chars.upper() == 'PM'
        string = string[:len(string) - 2]

    delimiter = ''
    hour, minute = now().hour, now().minute
    for ch in string:
        if not ch.isalnum():
            delimiter = ch
            break
    if delimiter:
        tokens = string.split(delimiter)
    else: # no delimiter => tokens are packed together => divisible by either 2 or 3
        tokens = []
        i = 0
        if len(string) % 3 == 0:
            if string[2].isalpha():
                token_size = 3
            else:
                token_size = 2
        elif len(string) % 2 == 0:
            token_size = 2
        else:
            raise ValueError("Parameter is in an invalid format.")
        while i < len(string):
            tokens.append(string[i:i + token_size])
            i += token_size
        print("DATES: ", tokens)

    if string.isnumeric() or delimiter:
        if len(tokens) == 1:
            hour = int(tokens[0])
            minute = 59
        if len(tokens) == 2: # hour-minute path
            hour, minute = int(tokens[0]), int(tokens[1])
    else: # noninferred time path; symbols are specified
        timetkns = {'H':now().hour, 'M':59} # hour, minute
        for token in tokens:
            if token[-1] in timetkns:
                tk = token[-1]
                timetkns[tk] = int(token[:len(token) - 1])
        hour, minute = timetkns['H'], timetkns['M']
    if is_pm:
        if hour < 12:  # PM hours
            hour += 12
    return now(hour=hour, minute=minute)

# TIMES
#  XX(T)XX OR XXHXXM (hour)
parse_time('1159')
parse_time('11H59M')
#  XXM (minute of the current hour)
parse_time('59M')
#  XX OR XXH (last minute of the given hour) 
parse_time('11')
parse_time('11H')
# input()


# DATETIMES
# [valid date](D)[valid time](T) (self explanatory)
# D[valid date] (11:59PM of the given date)
# T[valid time] (given time of the current day)
# +[valid timespan] (the current datetime plus the timespan)
# +[valid timespan]T[valid time] (the current datetime plus the timespan with time T)

def get_datetime(alphstr: str, plus_count: int = 0) -> datetime:
    current_time = now()
    options = {
        "Monday": current_time + timedelta(((-current_time.weekday() - 1) % 7 + 1 + plus_count * 7)),
        "Tuesday": current_time + timedelta(((-current_time.weekday()) % 7 + 1 + plus_count * 7)),
        "Wednesday": current_time + timedelta(((-current_time.weekday() + 1) % 7 + 1 + plus_count * 7)),
        "Thursday": current_time + timedelta(((-current_time.weekday() + 2) % 7 + 1 + plus_count * 7)),
        "Friday": current_time + timedelta(((-current_time.weekday() + 3) % 7 + 1 + plus_count * 7)),
        "Saturday": current_time + timedelta(((-current_time.weekday() + 4) % 7 + 1 + plus_count * 7)),
        "Sunday": current_time + timedelta(((-current_time.weekday() + 5) % 7 + 1 + plus_count * 7)),
    }
    return options[alphstr]


def parse_datetime(string):
    if not string:
        raise ValueError("Parameter is in an invalid format.")
    string = string.strip(' ')

    # SPECIAL CASES #

    if string == 'N':
        return now()

    # RELATIVE #

    if string[0] == 'A':
        sid, i = '', 1

        while i < len(string):
            if string[i].isnumeric():
                sid += string[i]
            else:
                break
            i += 1
        if not sid:
            input(sid)
            raise ValueError
        id = int(sid)

        assignment: BaseAssignment = get_focused_group().in_progress[id]  # TODO: support completed assignments
        date_type = string[i]  # last char before break
        relative = None
        if date_type == 'D':
            if assignment.has_due_date:
                relative = assignment.due_date
        elif date_type == 'S':
            if assignment.has_start_date:
                relative = assignment.start_date
        if not relative:
            raise ValueError

        i += 1
        if i >= len(string):
            return relative
        elif string[i] != '+':
            raise ValueError

        i += 1
        timespan = sslice_until(string[i:], lambda ch: ch != '+')
        delta = parse_timespan(timespan["string"])

        i = timespan["end"]
        if string[i] == '@':
            at_time = parse_time(string[i + 1:])
            relative.replace(hour=at_time.hour, minute=at_time.minute, second=at_time.second)

        return relative + delta

    # STRING/WEEKDAY #

    i = 0
    word = ""
    while i < len(string) and string[i].isalpha():
        word += string[i]
        i += 1
    try:
        date = get_datetime(word, string.count('+') - string.count('-'))
        if '@' in string:
            time = parse_time(string[string.index('@') + 1:])
            date = date.replace(hour=time.hour, minute=time.minute)
        return date
    except KeyError:
        pass

    # NORMAL CASES #

    leading_char = string[0]  # the leading character will either be a character
    # or a digit.
    if not leading_char.isnumeric():
        if leading_char == 'T':
            return parse_time(string[1:])
        if leading_char == 'D':
            next_char = string[1]
            if next_char == 'T':
                return parse_datetime(string[2:])
            return parse_date(string[1:])
        if leading_char == '+':
            spanstr = ""
            for ch in string[1:]:
                if ch.isalnum():
                    spanstr += ch
                else:
                    break
            print("ASPAN", spanstr)
            date = now() + parse_timespan(spanstr)
            if '@' in string:  # sets exact time
                time = parse_time(string[string.index('@') + 1:])
                date = date.replace(hour=time.hour, minute=time.minute)
                print("CHANGED DATE: ", time)
            return date

    delis = set()
    delimiters = []
    for ch in string:
        if not ch.isalnum() and ch not in delis:
            delimiters.append(ch)
            delis.add(ch)
    del delis

    if len(delimiters) == 3:
        tokens = string.split(delimiters[1])
        time = parse_time(tokens[1])
        date = parse_date(tokens[0])
        datetime = date.replace(hour=time.hour, minute=time.minute)
        return datetime
    if len(delimiters) == 1: # inferred datetime path
        tokens = string.split(delimiters[0])
        # inferred datetime path has exactly 5 tokens; MM(D)DD(D)YY(D)HH(D)MM
        month, day, year, hour, minute = map(lambda t: int(t), tokens)
        datetime = now(month=month, day=day, year=year, hour=hour, minute=minute)
        return datetime
    if len(delimiters) == 0:  # labeled path
        tokens = []
        # the inferred path MUST use two digits per token

        iterstring = string
        if string[len(string) - 2 - 1:].isalpha():
            iterstring = string[len(string) - 2 - 1:]

        alpha = False
        for i in iterstring:
            if i.isalpha():
                alpha = True
                break

        if alpha:
            token = ''
            for ch in string:
                token += ch
                if ch.isalpha():
                    tokens.append(token)
                    token = ""

            tkns = {'D': now().day, 'Y': now().year - 2000, 'M': now().month, 'h': now().hour, 'm': now().minute}  # hour, minute
            month_assigned = False
            for token in tokens:
                if token[-1] in tkns:
                    tk = token[-1]
                    if tk == 'M':
                        if not month_assigned:
                            tkns['M'] = int(token[:len(token) - 1])
                        else:
                            tkns['m'] = int(token[:len(token) - 1])  # change to minute
                        month_assigned = not month_assigned  # alternate
                    else:
                        tkns[tk] = int(token[:len(token) - 1])
        else:
            # 1130 - 11:30PM today
            # 113023 - 11:59PM 11/30/23
            # 1130231130 - 11:30PM 11/30/23
            # 11302311 - 11:59PM 11/30/23
            token, i = '', 0
            while i < len(string):
                token += string[i]
                i += 1
                if i % 2 == 0:
                    tokens.append(token)
                    token = ''

            if len(tokens) == 2:
                return parse_time(string)
            elif len(tokens) == 3:
                print(string[:6])
                print(parse_date(string[:6]))
                return parse_date(string[:6]).replace(hour=11, minute=59)
            elif len(tokens) >= 4:
                date = parse_date(string[:6]) # first three pairs of characters represent date
                time = parse_time(string[6:]) # last two pairs of characters represent time
                return date.replace(hour=time.hour, minute=time.minute)
            else:
                raise ValueError("Parameter is in an invalid format.")

        return now(day=tkns['D'], year=tkns['Y'] + 2000, month=tkns['M'], hour=tkns['h'], minute=tkns['m'])

# print("1A0A: ", parse_datetime("11M28D23Y10H00M"))
print("------------------")
print(parse_datetime("Monday"))
print(parse_datetime("Monday@1:02PM"))
print("--------------")
print("2B0B: ", parse_datetime("11-28-23/10:00"))
print(parse_datetime("11-28-23-10-00"))
print(parse_datetime("T1159"))
print(parse_datetime("D1230"))
# if datetime begins with A, followed by a string of numbers and a character in the set {D, S}
# then followed by a plus, then a valid timespan, we set the datetime relative to another assignment

def datetime_to_string(date: datetime):
    return f"{date.year - 2000}Y{date.month}M{date.day}D{date.hour}H{date.minute}M{date.second}S"

def timedelta_to_string(td: timedelta):
    days = td.days
    weeks = days // 7
    days = days % 7

    seconds = td.seconds
    hours = seconds // 3600
    seconds = seconds % 3600

    minutes = seconds // 60
    seconds = seconds % 60

    return f"{weeks}W{days}D{hours}h{minutes}m{seconds}s"

# input()
# TIMEDELTA
#  DDHHMM - day, hour, minute timespan (inferred path)
# + - next day, same minute
# +(T) for token T (Y, W, D, M, H, OR m) - next T (T's value + 1)
# + - next day
# +++ - in 3 days
# any number of +'s can be used to separate digits, i.e.

# 11++20 (in 11 days, 2 hours from this current hour, and 20 minutes)
# limitation: +'s cannot be used for multiple tokens in a row, they must be separated

# +++

# -(T) for token T (Y, W, D, M, H OR m) - last T (T's value - 1)
# XXYXXMXXWXXDXXHXXM (Year, month, week, day, hour, minute)
# DT[valid datetime] - difference between current datetime and valid datetime.


def parse_timespan(string: str) -> timedelta:
    string = string.strip()
    if not string:
        raise ValueError("Parameter is in an invalid format.")
    leading_chars = string[:2]
    if leading_chars == 'DT':
        # if string[2] != '[' or string[-1] != ']':
        #     raise ValueError("Parameter is in an invalid format.")
        datetime = parse_datetime(string[3:len(string)])
        return datetime - now()
    else:
        leading_char = leading_chars[0]
        if leading_char.isalpha(): # and leading_chars[1] == '[':
            # if string[-1] != ']':
            #    raise ValueError("Parameter is in an invalid format.")
            if leading_char == 'D':
                datetime = parse_date(string[2:len(string) - 1])
                return datetime - now()
            elif leading_char == 'T':
                datetime = parse_time(string[2:len(string) - 1])
                return datetime - now()
    tokens = []

    delimiter = ''
    alpha = False
    for i in string:
        if i.isalpha():
            alpha = True

    if alpha:
        token = ''
        for ch in string:
            token += ch
            if ch.isalpha():
                tokens.append(token)
                token = ""

        month_assigned = False
        tkns = {tk: 0 for tk in ('Y', 'W', 'D', 'H', 'm')}
        for tkn in tokens:
            tk = tkn[-1]
            if tk == 'M':
                if month_assigned:
                    tkns['M'] = int(tkn[:len(tkn) - 1])
                else:
                    tkns['m'] = int(tkn[:len(tkn) - 1])
                month_assigned = not month_assigned
            else:
                tkns[tk] = int(tkn[:len(tkn) - 1])
        return timedelta(days=tkns['Y'] * 365 + tkns['W'] * 7 + tkns['D'], hours=tkns['H'], minutes=tkns['m'],
                         seconds=0, microseconds=0)
    else:
        i = 0
        if len(string) == 3:  # another very special inferred case
            tokens.append(string[0])  # hour
            tokens.append(string[1:])  # minute
            return timedelta(hours=int(tokens[0]), minutes=int(tokens[1]))
        elif len(string) == 5:  # very special inferred case
            tokens.append(string[0])  # day
            tokens.append(string[1:3])  # hour
            tokens.append(string[3:])  # minute
            return timedelta(days=int(tokens[0]), hours=int(tokens[1]), minutes=int(tokens[2]))
        while i < len(string):
            tokens.append(string[i:i + 2])
            i += 2
        print(tokens)
        if len(tokens) == 1:
            return timedelta(hours=int(tokens[0]))
        if len(tokens) == 2:
            return timedelta(hours=int(tokens[0]), minutes=int(tokens[1]))
        if len(tokens) == 3: # for three token inferred path,
            return timedelta(days=int(tokens[0]), hours=int(tokens[1]), minutes=int(tokens[2]))
        if len(tokens) == 4:
            return timedelta(weeks=int(tokens[0]), days=int(tokens[1]), hours=int(tokens[2]), minutes=int(tokens[3]))


print(parse_datetime("+1D@3H"))
"""
print(parse_timespan('DT[1159]'))
print(parse_timespan('DT[12M1D]'))
print(parse_timespan('D[11M30D]'))
print(parse_timespan('T[11H59M]'))
print(parse_timespan(''))
"""
print(parse_timespan('11'))
print(parse_timespan('1'))
print(parse_timespan('1120'))
print(parse_timespan('11030'))
print(parse_timespan('130'))
print(parse_timespan('11H'))
# input()

from math import ceil

import os

from structs import (BaseAssignment, Group,
                     groups, active_groups, inactive_groups)


def clear(): return os.system('cls')


SPECIAL = b'\xe0'
UP = b'\xe0H'
RIGHT = b'\xe0M'
DOWN = b'\xe0P'
LEFT = b'\xe0K'
SPACEBAR = b' '
ENTER = b'\r'
COPY = b'\x03'
PASTE = b'\x16'
BACKSPACE = b'\x08'
ANY_KEY = b''


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

    # THIS IS NOT A CLEAR GRID FUNCTION
    # THIS REASSEMBLES THE BOX MATRIX
    # TODO: CLEAR_GRID METHOD
    def reset_grid(self):
        self.grid = []
        for i in range(self.true_h):
            self.grid.append([])
            for j in range(self.true_w):
                self.grid[i].append(' ')

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
                due = '\n' + "Due Date: " + str(assignment.due_date)

            if assignment.has_start_date:
                start = '\n' + "Start Date: " + str(assignment.start_date)

            if assignment.is_persistent:
                inc = '\n' + "Interval: " + str(assignment.interval)

            outpt: str = name + desc + due + start + inc
            self.h = outpt.count('\n') + 1

            if not misc.get("noreset", False):
                self.reset_grid()
            self.place_text(outpt, pn)

    def __repr__(self):
        string = ""
        for r in self.grid:
            string += "".join(r) + "\n"
        return string

    def __str__(self):
        return self.__repr__()


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
        index = clamp(boxargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_hcenter_text(text, y, *args)

    def place_vcenter_text(self, text, x: int = -1, *args: [str, int], **boxargs):
        index = clamp(boxargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_vcenter_text(text, x, *args)

    def place_center_text(self, text: str, **boxargs):
        index = clamp(boxargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_center_text(text)

    def place_vbar(self, x, *xs, **boxargs):
        index = clamp(boxargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_vbar(x, *xs)

    def place_hbar(self, y: int, *ys: int, **boxargs):
        index = clamp(boxargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).place_hbar(y, *ys)

    def place_box(self, w: int, h: int, position: tuple, *whps: [int, int, tuple], **boxkwargs) -> Union[
        list['Box'], 'Box']:
        index = clamp(boxkwargs.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
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

    def loadup(self, object: Union['Group', 'BaseAssignment'], pn: tuple = (1, 2), pd: tuple = (2, 2), **misc):
        index = clamp(misc.get('index', self.default_layer), -self.layer_count, self.layer_count - 1)
        self.get_layer(index).loadup(object, pn, pd, **misc)

        return

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
                due = '\n' + "Due Date: " + str(assignment.due_date)

            if assignment.has_start_date:
                start = '\n' + "Start Date: " + str(assignment.start_date)

            if assignment.is_persistent:
                inc = '\n' + "Interval: " + str(assignment.interval)

            outpt: str = name + desc + due + start + inc
            self.h = outpt.count('\n') + 1

            if not misc.get("noreset", False):
                self.reset_grid()
            self.place_text(outpt, pn)

    def __repr__(self):
        string = ""
        for i in range(self.true_h):
            for j in range(self.true_w):
                symbol, layer = ' ', -1
                while not symbol.strip() and -layer <= self.layer_count:
                    symbol = self._layers[layer].at(i, j)
                    layer -= 1
                string += symbol
            string += "\n"
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
        self.carat = 0  # the beginning of the string

        self.text = self.displayed_text = ""
        self.displaying = False

    def type(self, char: Union[str, bytes]):
        pos = self.carat
        self.text = self.text[:pos] + (char if isinstance(char, str) else char.decode('ascii')) + self.text[pos:]
        self.shift_carat(len(char))  # move the carat forward
    def delete(self, del_count: int):
        self.text = self.text[:max(0, self.carat - del_count)] + self.text[self.carat:]
        self.shift_carat(-del_count)
    def clear(self):
        self.back_carat()
        self.text = ""
    def front_carat(self):
        self.shift_carat(len(self.text))

    def back_carat(self):
        self.shift_carat(-len(self.text))

    def shift_carat(self, shift_amount: int):
        self.carat = clamp(self.carat + shift_amount, 0, len(self.text))

    def get(self, vtype: [str, type]):
        v = self.text
        if vtype == 'd':
            pass
            # v = parse_date_as_date(self.text)
        elif vtype == 't':
            pass
            # v = parse_time_as_time(self.text)
        elif vtype == 'dt':
            if not self.text:
                v = now()
            else:
                v = parse_datetime(self.text)
        elif vtype == 'ts':
            if not self.text:
                v = timedelta()
            v = parse_timespan(self.text)
        return v
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
            lentex = min(container_width, len(self.text))  # the amount of characters we are replacing
            offset = container_width * (self.carat // container_width)
            if offset != 0:
                offset -= 1

            for x in range(self.w - xi):
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
            if isinstance(key, list):
                return self.commands[key[0]](*key[1:])
            else:
                return self.inputs[key]()
        except KeyError:
            if isinstance(key, bytes):
                try:
                    return self.inputs[ANY_KEY](key)
                except KeyError:
                    return self.run()
            return self.run()


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
        def on_space():
            state(FGRPS, int(state(MSIDE) > 0))
            state(FGRP, state(MINDEX))
            FUNCTIONS[ASSGN]()
        return InputMap(
            {  # inputs (covered by getch)
                b's': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED) or state(
                    MINDEX, 0),
                b'l': lambda: state(MSIDE,
                                    MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED) or state(
                    MINDEX, 0),
                SPACEBAR: on_space,
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
        BOTTOM_BUTTON_HEIGHT = 5

        y, i = 1, state(MINDEX)
        # supporst (description, due date, start date, etc.)
        while y < box.h - BOTTOM_BUTTON_HEIGHT:
            bu = Box(box.w // 2 - padding // 2 - 2,1)
            if i == 0:
                bu.place_hcenter_text('Unfinished-Assignments', 0)

            if i < len(focused.in_progress):
                bu.loadup(focused.in_progress[i])
            #    if i == state(MINDEX):
            #        bu.set_border('*')

            box.place(bu, (y, 1))
            i += 1
            y += bu.true_h
            return box

        y, i = 1, 0
        while y < box.h - BOTTOM_BUTTON_HEIGHT:
            bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))
            bf.place_hcenter_text('Finished-Assignments', 0)

            if i < len(focused.completed):
                bf.loadup(focused.completed[i])

            i += 1
            y += BOX_HEIGHT

            bf = box.place_box(box.w // 2 - padding // 2 - 2, BOX_HEIGHT - 2, (y, box.w // 2 + padding // 2 + 2))

        BOX_TO_ARROW_RATIO = 4
        box_width = box.w // 2 - padding // 2 - 2
        if not TRIGGER_COMMANDS['hdnv']:
            arrows = box.place_box(box_width, BOTTOM_BUTTON_HEIGHT, (box.h - BOTTOM_BUTTON_HEIGHT, 1))
            arrows.place_hcenter_text("Navigate", 0)

            select = arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2,
                                      (1, 1))
                                       # arrows.w - 3 * box_width // BOX_TO_ARROW_RATIO - box_width // 2 // BOX_TO_ARROW_RATIO - 1))
            select.place_center_text('Choose (X)')


            sort_mode = arrows.place_box(box_width // BOX_TO_ARROW_RATIO, BOTTOM_BUTTON_HEIGHT - 2,
                                      (1, box_width - box_width // BOX_TO_ARROW_RATIO))
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
            group = get_focused_group()
            index = state(MINDEX)
            group.remove_assignment_at(index)
            if index == group.in_progress_count:
                state(MINDEX, state(MINDEX) - 1)

        return InputMap(
            {  # inputs (covered by getch)
                b'x': lambda: state(MSIDE, MSIDE_LEFT if not is_state(MSIDE, MSIDE_LEFT) else MSIDE_UNDECIDED),
                b'l': lambda: state(MSIDE, MSIDE_RIGHT if not is_state(MSIDE, MSIDE_RIGHT) else MSIDE_UNDECIDED),
                b'g': lambda: trigger(POP) or trigger(REFRS),
                DOWN: lambda: state(MINDEX,
                                  min(len(get_focused_group().in_progress) - 1,
                                      state(MINDEX) + 1)), # if not is_state(MSIDE, MSIDE_UNDECIDED) else MINDEX),
                UP: lambda: state(MINDEX, max(MINDEX_START, state(MINDEX) - 1)), # if not is_state(MSIDE,
                SPACEBAR: lambda: edit_assignment(state(MINDEX)),                                         # MSIDE_UNDECIDED) else MINDEX),
                b'c': lambda: FUNCTIONS[ADA](),
                BACKSPACE: remove_assignment
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


def has_focused_group() -> bool:
    if state(FGRP) == NO_FOCUSED_GROUP:
        return False
    return True

def get_focused_group() -> Group:
    return groups[state(FGRPS)][state(FGRP)]


BUTTON_COLUMN, FIELD_COLUMN = 1, 2
class AssignmentEditor(Menu):
    def on_space(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MINDEX) < len(self.caption_fields):
            midx = state(MINDEX)
            field = self.caption_fields[midx]
            get_field(field)
            if field.validate(self.field_types[midx]):
                self.find_index(1)
        else:
            self.on_enter()

    def show(self, assignment=None):
        if assignment:
            name, desc, sdat, ddat, incr = range(5)
            self.caption_fields[name].text = assignment.name
            if assignment.has_description:
                self.enabled[desc] = True
                self.caption_fields[desc].text = assignment.desc
            else:
                self.enabled[desc] = False
                self.caption_fields[desc].text = ""

            if assignment.has_start_date:
                self.enabled[sdat] = True
                self.caption_fields[sdat].text = datetime_to_string(assignment.start_date)
            else:
                self.enabled[sdat] = False
                self.caption_fields[sdat].text = ""

            if assignment.has_due_date:
                self.enabled[ddat] = True
                self.caption_fields[ddat].text = datetime_to_string(assignment.due_date)
            else:
                self.enabled[ddat] = False
                self.caption_fields[ddat].text = ""

            if assignment.is_persistent:
                self.enabled[incr] = True
                self.caption_fields[incr].text = timedelta_to_string(assignment.interval)
            else:
                self.enabled[incr] = False
                self.caption_fields[incr].text = ""

        super().show()


    def on_enter(self):
        if is_state(MINDEX, len(self.captions)):  # indicates create new assignment button
            assignment_params = ["", "", None, None, None, ""]
            # name, description, start_date, due_date, increment, type
            for i, field in enumerate(self.caption_fields):
                if self.enabled[i] is not False:
                    assignment_params[i] = field.get(self.field_types[i])
            get_focused_group().add_assignment(BaseAssignment(*assignment_params))
            poprefrs()
        elif is_state(MSIDE, BUTTON_COLUMN):
            if self.enabled[state(MINDEX)] is not None:
                self.enabled[state(MINDEX)] = not self.enabled[state(MINDEX)]

    def find_index(self, delta: int):
        d = delta // abs(delta)
        i = state(MINDEX)
        if not is_state(MSIDE, MSIDE_UNDECIDED):
            check = False if is_state(MSIDE, FIELD_COLUMN) else None
            while True:
                i += d
                if 0 <= i <= len(self.enabled):
                    if i == len(self.enabled) or self.enabled[i] is not check:
                        state(MINDEX, i)
                        break
                else:
                    break

    def switch_sides(self, side: int):
        if 0 > state(MINDEX) or state(MINDEX) >= len(self.captions):
            return
        state(MSIDE, side)
        if not is_state(MSIDE, MSIDE_UNDECIDED):
            check = None if is_state(MSIDE, BUTTON_COLUMN) else False
            if self.enabled[state(MINDEX)] is check:
                i = state(MINDEX)  # we default to the top button
                for n in range(1, len(self.enabled)):
                    if 0 <= i + n < len(self.enabled):
                        if self.enabled[i + n] is not check:
                            state(MINDEX, i + n)
                            return

                    if 0 <= i - n < len(self.enabled):
                        if self.enabled[i - n] is not check:
                            state(MINDEX, i - n)
                            return

    def on_any_key(self, key):
        if is_state(MSIDE, FIELD_COLUMN) and state(MINDEX) < len(self.caption_fields):
            if key != ENTER:
                field = self.caption_fields[state(MINDEX)]
                field.front_carat()
                if key != BACKSPACE:
                    field.type(key)
                else:
                    field.delete(len(field.text))
            self.on_space()

    def on_ctrl_c(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MINDEX) < len(self.caption_fields):
            global clipboard
            clipboard = self.caption_fields[state(MINDEX)].text

    def on_ctrl_v(self):
        if is_state(MSIDE, FIELD_COLUMN) and state(MINDEX) < len(self.caption_fields):
            self.caption_fields[state(MINDEX)].type(clipboard)

    def get_map(self):
        def default_to_field_column():
            if is_state(MSIDE, MSIDE_UNDECIDED):
                state(MSIDE, FIELD_COLUMN)
                return False
            return True
        return InputMap({
            ANY_KEY: self.on_any_key,
            UP: lambda: default_to_field_column() and self.find_index(-1),  # state(MINDEX, clamp(state(MINDEX) - 1, 0, len(captions) - 1)),
            DOWN: lambda: default_to_field_column() and self.find_index(1),  # state(MINDEX, clamp(state(MINDEX) + 1, 0, len(captions) - 1)),
            RIGHT: lambda: self.switch_sides(FIELD_COLUMN),
            LEFT: lambda: self.switch_sides(BUTTON_COLUMN),
            COPY: self.on_ctrl_c,
            PASTE: self.on_ctrl_v,
            ENTER: self.on_enter,
            SPACEBAR: self.on_space
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
            "Start Date": 24,
            "Due Date": 24,  # YY-MM-DD hh:mm:ss (DateTime)
            "Date Increment": 24,  # MM-WW-DD-hh-mm-ss (TimeSpan)
        }
        self.field_types = ['s', 's', 'dt', 'dt', 'ts']
        self.caption_fields: list[InputField] = []

        for i, caption in enumerate(self.captions):
            field = InputField(self.captions[caption], 1, [1, 2])
            self.caption_fields.append(field)

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
        # Enter Button
        enter_w = w // 3
        enter_h = 1
        enter_center_y = 1  # from the bottom of the screen
        enter = bx.place_box(enter_w, 1, (h - 1 + enter_h - 2 - enter_center_y, enter_w)) # + 2 for borders
        enter.place_center_text("Create New Assignment");
        if is_state(MINDEX, len(self.captions)): # goes over
            enter.set_border('*')
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
            return cmds


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
            if ch == SPECIAL:  # precedes special character; use getch() again
                # todo: check for esc
                pass
            elif ch == b';':
                run(True, cmds)
                clearline()
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
        print('\r', end="")
        return key  # key.decode('ascii').lower()


HDNV = 'hdnv'  # hide navigation menu
REFRS = 'refrs'  # refresh the current menu
POP = 'pop'  # pop the current menu (can be used to quit from the group menu)
DEBUG = 'debug'  # enter debug mode (counts empty spaces and shows origins for each element)
PMDEF = 'pmdef'  # whether pm is default or not
ALRON = 'alron'  # turns alerts on or off
NOMIN = 'nomin'  # toggles minimizing on due date alert
WARNS = 'warns'  # toggles ui warnings
CFMDE = 'cfmde'  # toggles "confirm delete assignment" popup before removing an assignment
TRIGGER_COMMANDS = {
    'hdnv': False,
    REFRS: False,
    POP: False,
    DEBUG: False,
    PMDEF: True,
    ALRON: True,
    NOMIN: False,
    WARNS: False,
    CFMDE: False
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
ADAED = 'adaed'
assignment_editor = AssignmentEditor()
OUTPT = 'outpt'
FQT = 'fqt'
TRIGG = 'trigg'
ATRIG = 'atrig'
LIT = 'lit'
SAVE = 'save'
# RCACH = 'rcach'
FUNCTIONS: dict[str, Callable] = {
    GROUP: group_menu.show,
    ASSGN: assignments_menu.show,
    QT: quit_menu.show,
    FQT: lambda: quit(0),
    OUTPT: input,
    TRIGG: lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if is_trigger(i)])),
    ATRIG: lambda: input("".join(['(' + i + ')' for i in TRIGGER_COMMANDS if not is_trigger(i)])),
    ADA: lambda: reset_menu_selection() or assignment_editor.show(),  # goes to assignment editor
    ADAED: lambda a: reset_menu_selection() or assignment_editor.show(a),
    LIT: lit,
    SAVE: savedata.save_all,
    # RCACH: alerts.clear_cache
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


# todo: callback on finish
# assumption: field is a single line input field
clipboard = ""


# 's' - string
# 'd' - date
# 't' - time
# 'dt' - datetime
def get_field(field: InputField):
    InputField.FIELD = field
    field.displaying = False
    menu = MENU.menu_display()
    while True:
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
            print(ch)
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

if __name__ == "__main__":
    ui()
