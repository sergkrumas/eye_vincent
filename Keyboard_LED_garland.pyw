# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#  Author: Sergei Krumas (github.com/sergkrumas)
#
# ##### END GPL LICENSE BLOCK #####



from ctypes import windll
from win32con import VK_CAPITAL, VK_NUMLOCK, VK_SCROLL
import time

locks = (VK_NUMLOCK, VK_CAPITAL, VK_SCROLL)
KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP = 2

WAIT_VALUE = 0.2

state = [False, False, False]

order = True

def _wait():
    time.sleep(WAIT_VALUE)

def get_lock_button_state(lock_id):
    return windll.user32.GetKeyState(lock_id)

def toogle_lock_button(lock_id):
    windll.user32.keybd_event(lock_id, 69, KEYEVENTF_EXTENDEDKEY, 0)
    windll.user32.keybd_event(lock_id, 69, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def save_state():
    for n, lock_id in enumerate(locks):
        state[n] = get_lock_button_state(lock_id)

def load_state():
    for n, lock_id in enumerate(locks):
        if state[n]:
            toogle_lock_button(lock_id)

def reset():
    for lock_id in locks:
        is_on = get_lock_button_state(lock_id)
        if is_on:
            toogle_lock_button(lock_id)

def toogle_NUM_LOCK(wait=True):
    toogle_lock_button(VK_NUMLOCK)
    if wait:
        _wait()

def toogle_CAPS_LOCK(wait=True):
    toogle_lock_button(VK_CAPITAL)
    if wait:
        _wait()

def toogle_SCROLL_LOCK(wait=True):
    toogle_lock_button(VK_SCROLL)
    if wait:
        _wait()

def program_1_0():

    toogle_NUM_LOCK()
    toogle_NUM_LOCK()

    toogle_CAPS_LOCK()
    toogle_CAPS_LOCK()

    toogle_SCROLL_LOCK()
    toogle_SCROLL_LOCK()

def program_1_1():

    toogle_SCROLL_LOCK()
    toogle_SCROLL_LOCK()

    toogle_CAPS_LOCK()
    toogle_CAPS_LOCK()

    toogle_NUM_LOCK()
    toogle_NUM_LOCK()

def program_1():
    if order:
        program_1_0()
        program_1_1()
    else:
        program_1_1()
        program_1_0()

def program_2_0():

    toogle_NUM_LOCK()
    toogle_CAPS_LOCK()
    toogle_SCROLL_LOCK()

    toogle_NUM_LOCK()
    toogle_CAPS_LOCK()
    toogle_SCROLL_LOCK()

def program_2_1():

    toogle_SCROLL_LOCK()
    toogle_CAPS_LOCK()
    toogle_NUM_LOCK()

    toogle_SCROLL_LOCK()
    toogle_CAPS_LOCK()
    toogle_NUM_LOCK()

def program_2():

    if order:
        program_2_0()
        program_2_1()
    else:
        program_2_1()
        program_2_0()



def program_3():

    toogle_NUM_LOCK(wait=False)
    toogle_CAPS_LOCK(wait=False)
    toogle_SCROLL_LOCK(wait=False)

    _wait()

    toogle_NUM_LOCK(wait=False)
    toogle_CAPS_LOCK(wait=False)
    toogle_SCROLL_LOCK(wait=False)

def repeat(func, times=1):
    for n in range(times):
        _wait()
        func()

if __name__ == '__main__':

    save_state()

    order = True
    reset()
    program_1()
    reset()
    program_2()
    reset()
    repeat(program_3, times=10)

    order = False
    reset()
    program_2()
    reset()
    program_1()
    reset()
    repeat(program_3, times=10)

    load_state()
