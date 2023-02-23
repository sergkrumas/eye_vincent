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

# скрипт для переименовывания картинок после рендера
# надо положить его в папку render с отрендеренными картинками и запустить
# картинки нужно затем скопировать в папку images

source_names = (
    r"0001.png",
    r"0002.png",
    r"0003.png",
    r"0004.png",
    r"0005.png",
    r"0006.png",
    r"0007.png",
    r"0008.png",
    r"0009.png",
    r"0010.png",
    r"0011.png",
    r"0012.png",
    r"0013.png",
    r"0014.png",
    r"0015.png",
    r"0016.png",
    r"0017.png",
    r"0018.png",
    r"0019.png",
    r"0020.png"
)

dest_names = (
    r"eyes_default.png",
    r"head_default.png",
    r"head_right.png",
    r"head_left.png",
    r"palming.png",
    r"eyes_closed.png",
    r"eyes_tightly_closed.png",
    r"eyes_down.png",
    r"eyes_up.png",
    r"eyes_right.png",
    r"eyes_left.png",
    r"neck_tilt_left.png",
    r"neck_tilt_right.png",
    r"neck_default.png",
    r"neck_bend_forwards.png",
    r"neck_bend_backwards.png",
    r"neck2_default.png",
    r"neck2_move_forwards.png",
    r"neck2_move_backwards.png",
    r"window.png"
)


import os

for s, d in zip(source_names, dest_names):
    os.rename(s, d)
