
import atexit
from sys import stderr, stdin, stdout

try:
    from ansicon import *
except:
    print("Module ansicon is not installed or accessable.")
    print("This module(ansicon_plus) requires ansicon to work. Try:")
    print("    pip install ansicon")
    print("from the command line to install ansicon.")
    exit(-1)


try:
    import msvcrt
except:
    nonblock_read = None
else:
    def nonblock_read():
        result = []
        while msvcrt.kbhit():
            c = msvcrt.getch()
            result.append(c.decode("ascii"))
        return ''.join(result)

if nonblock_read is None:
    print("Method 'position' is not supported because there")
    print("no good support for non-blocking reads.  This problem")
    print("should be fixed soon.  Check for new versions to solve")
    print("this problem, or try installing module 'msvcrt'.")


def raiseValueError(value):
    raise ValueError("unexpected value {!r}".format(value))


ESC = '\x1b'
CSI = ESC + '['
STANDARDS = ("DEC", "SCO")
MODES = dict(# name = (set. reset)
             bold=(1, 22),
             dim=(2, 22),
             faint=(2, 22),
             italic=(3, 23),
             underline=(4, 24),
             blink=(5, 25),
             inverse=(7, 27),
             hidden=(8, 28),
             linethrough=(9, 29),
             strikethrough=(9, 29))
COLORS = dict(# name = (foreground, background)
              black=(30, 40),
              red=(31, 41),
              green=(32, 42),
              yellow=(33, 43),
              blue=(34, 44),
              magenta=(35, 45),
              cyan=(36, 46),
              white=(37, 47),
              default=(39, 49),
              brightblack=(90, 100),
              brightred=(91, 101),
              brightgreen=(92, 102),
              brightyellow=(93, 103),
              brightblue=(94, 104),
              brightmagenta=(95, 105),
              brightcyan=(96, 106),
              brightwhite=(97, 107),
              reset=(0, 0))

# None of the following screen modes actually work.
SCREENS = { # name = screen_mode
           "mono-text-40x25": 0,
           "color-text-40x25": 1,
           "mono-text-80x25": 2,
           "color-text-80x25": 3,
           "CGA": 4,
           "4color-graphic-320x200": 4,
           "mono-graphic-320x200": 5,
           "mono-graphic-640x200": 6,
           "linewrap": 7,
           "color-graphic-320x200": 13,
           "16color-graphic-640x200": 14,
           "mono-graphic-640x350": 15,
           "16color-graphic-640x350": 16,
           "mono-graphic-640x480": 17,
           "16color-graphic-640x480": 18,
           "MCGA": 19,
           "256color-graphic-320x200": 19}

class ANSI_CSI:

    def __new__(cls, standard=None,
                initialize=True, setup=None, teardown=None):
        if standard and standard not in STANDARDS:
            raise ValueError("standard expects one of {} but found {!r}"
                             .format(', '.join(standard), standard))
        if setup and not callable(setup):
            raise ValueError("setup expects a callable but found {!r}"
                             .format(setup))
        if teardown and not callable(teardown):
            raise ValueError("teardown expects a callable"
                             " but found {!r}".format(teardown))
        self = super().__new__(cls)
        self._standard = standard or None
        self._setup = setup or None
        self._teardown = teardown or None
        atexit.register(self.teardown)
        if initialize:
            self.setup()
        return self

    _standard = None

    @property
    def standard(self):
        return self._standard

    _setup = None
    _teardown = None

    def __del__(self):
        self.teardown()

    def setup(self):
        if not loaded():
            load()
            if self._setup:
                self._setup()

    def teardown(self):
        if loaded():
            if self._teardown:
                self._teardown()
            unload()

    def csi(self, code, *args):
        "returns a formatted csi code as CSI{args}{code}."
        if not (type(code) is str and len(code) == 1):
            unload()
            raise ValueError("code expects a csi code character"
                             " but found {!r}".format(code))
        if not all(type(a) is int for a in args):
            unload()
            raise ValueError("*args expects integers but found {!r}"
                             .format(args))
        return "{}{}{}".format(CSI,
                               ';'.join(str(a) for a in args),
                               code)
    def position(self):
        "Return cursor position as line, column."
        if not loaded():
            raise NotImplementedError("ansicon is not loaded")
        self.print(self.csi("n", 6), flush=True)
        result = nonblock_read()
        if result and result.startswith(CSI) and result.endswith("R"):
            return tuple(int(i)
                         for i in result[len(CSI):-1]
                         .split(";"))
        return None

    def resetmodes(self):
        "Reset all color or graphic modes."
        return self.csi("m", 0)

    def color(self, *colors, bg=False):
        "Set color modes, uses color name, color int or rgb-tuple."
        i = int(bool(bg))
        values = sum((((COLORS[name][i],)
                      if type(name) is str else
                      ((38,48)[i], 5, name)
                      if type(name) is int and 0 <= name <= 255 else
                      ((38,48)[i], 2, *name)
                      if isinstance(name, tuple) and len(name) == 3
                      and all(type(n) is int
                              and 0 <= n <= 255
                              for n in name) else
                      raiseValueError(name))
                  for name in colors), ())
        return self.csi("m", *values)

    def mode(self, *modes, clear=False):
        "Set graphic modes, used mode names or mode int."
        i = int(bool(clear))
        values = ((MODES[name][i]
                   if type(name) is str else
                   name
                   if type(name) is int else
                   raiseValueError(name))
                  for name in modes)
        return self.csi("m", *values)

    def screen(self, *modes, clear=False):
        "Set screen modes."
        raise NotImplementedError("screen modes don't actually work!")
        i = int(bool(clear))
        return ''.join(self.csi("hl"[i], SCREENS[name])
                       for name in modes)

    def save(self):
        "Save cursor position."
        return self.csi("s" if self._standard == "SCO" else "7")

    def restore(self):
        "Restore cursor position."
        return self.csi("u" if self._standard == "SCO" else "8")

    def print(self, *values,
              sep=' ', end='', file=stdout, flush=False):
        if not loaded():
            raise NotImplementedError("ansicon is not loaded")
        print(*values, sep=sep, end=end, file=file, flush=flush)


def _def_ansi_csi_method(name, code, desc=None):
    def ansi_csi_method(self, *args):
        return self.csi(code, *args)
    ansi_csi_method.__name__ = name
    if desc:
        ansi_csi_method.__doc__ = desc
    setattr(ANSI_CSI, name, ansi_csi_method)

setattr(ANSI_CSI, "Modes", tuple(MODES.keys()))
setattr(ANSI_CSI, "Colors", tuple(COLORS.keys()))
for name, code, doc in (("up", "A", "Moves cursor up n lines."),
                        ("down", "B", "Move cursor down n lines."),
                        ("right", "C", "Move cursor right n lines."),
                        ("left", "D", "Move cursor left n lines."),
                        ("next", "E", "Go to start, n lines down."),
                        ("prev", "F", "Go to start, n lines up."),
                        ("column", "G", "Go to column n."),
                        ("move", "H", "Go to line n, column m."),
                        ("clear", "J", "Clear display (0, 1, or 2)."),
                        ("erase", "K", "Clear line (0, 1, or 2)."),
                        ("up1", "M", "Up 1 line, scroll if needed.")):
    _def_ansi_csi_method(name, code, doc)




