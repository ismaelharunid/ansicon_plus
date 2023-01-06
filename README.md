# ansicon_plus
A wrapper for the pip ansicon module that support a few friendly methods to make it easier to use.

Requires ansicon which you can install using `pip install ansicon`.

Known bugs:
 1) the position method may fail on some systems, this is due to my main machine being in the show and my alt machine is running windows.
    so this has not been tested on *-nix, but except for the metioned methods should work fine.
 2) there is no package file yet so installation requirements must be handled manually.  I will fix this when I get my machine back from the shop.
 
 To install, simply download this project and move or copy the ansicon_plus.py to a directory in your python path or project.
 
Usage:
```python
import ansicon_plus

csi = ansicon_plus.ANSI_CSI()
csi.print(csi.clear(2), csi.color((255,0,255)), csi.color((0,127,127), bg=True),
          "The screen is clear and magenta", end="\n", flush=True)
```
 
