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
    "0001.png",
    "0002.png",
    "0003.png",
    "0004.png",
    "0005.png",
    "0006.png",
    "0007.png",
    "0008.png",
    "0009.png",
    "0010.png",
    "0011.png",
    "0012.png",
    "0013.png",
    "0014.png",
    "0015.png",
    "0016.png",
    "0017.png",
    "0018.png",
    "0019.png",
    "0020.png",

    "0021.png",
    "0022.png",
    "0023.png",
    "0024.png",
)

dest_names = (
    "eyes_default.png",
    "head_default.png",
    "head_right.png",
    "head_left.png",
    "palming.png",
    "eyes_closed.png",
    "eyes_tightly_closed.png",
    "eyes_down.png",
    "eyes_up.png",
    "eyes_right.png",
    "eyes_left.png",
    "neck_tilt_left.png",
    "neck_tilt_right.png",
    "neck_default.png",
    "neck_bend_forwards.png",
    "neck_bend_backwards.png",
    "neck2_default.png",
    "neck2_move_forwards.png",
    "neck2_move_backwards.png",
    "window.png",

    "head_training1_1.png",
    "head_training1_2.png",
    "head_training2_1.png",
    "head_training2_2.png",
)


import os

for s, d in zip(source_names, dest_names):
    os.rename(s, d)
