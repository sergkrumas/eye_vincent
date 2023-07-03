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

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, os, random, string, time, ctypes, subprocess, traceback, locale, itertools

from ctypes import windll, Structure, c_long, byref, wintypes

import math

import win32api
import win32process
import psutil
import datetime
import threading
from collections import namedtuple

ShortBreakInfo = namedtuple('ShortBreakInfo', 'probability name slow_factor images')

from on_windows_startup import is_app_in_startup, add_to_startup, remove_from_startup

# import tracemalloc
# tracemalloc.start()

class Globals():
    LONG_BREAK_INTERVAL = 60.0 * 50.0
    SHORT_BREAK_INTERVAL = 60.0 * 6.0
    LONG_BREAK_DURATION = 60.0 * 10.0
    SHORT_BREAK_DURATION = 10.0
    LONG_DURATION_TRESHOLD = 20.0

    # LONG_BREAK_INTERVAL = 60.0 * 1.0

    DEBUG = True
    DEBUG_DURATION = 30
    # LONG_BREAK_INTERVAL = 31.0

    long_break_tstamp = time.time()
    short_break_tstamp = time.time()

    HOLD_COLOR_PERIOD = 60

    RUN_LED_GARLAND = False

    SHOW_TRAY_NOTIFICATION = False

    SYMBOLS_COUNT = 400

    IMAGES_FOLDERPATH = 'images'

    NUM_REQUEST = None # list index or None

    paused = False

    MEMORY_GUARD = True

    # Целые числа после названия короткого перерыва показывают
    # сколько времени надо держать кадр, чем больше - тем дольше.
    # Целые числа перед названием короткого перерыва показывают
    # вероятность появления напоминания
    # '1' - обычная скорость, '2' - в 2 раза медленее
    SHORT_BREAK_INFOS = (
        # 0
        ShortBreakInfo(50, "глаза влево-вправо", 2,
                ('eyes_left.png', 'eyes_right.png')),
        # 1
        ShortBreakInfo(50, "глаза вверх-вниз", 2,
                ('eyes_down.png', 'eyes_up.png')),
        # 2
        ShortBreakInfo(50, "зажмурить", 3,
                ('eyes_default.png', 'eyes_tightly_closed.png')),
        # 3
        ShortBreakInfo(60, "легко и быстро поморгать", 1,
                ('eyes_default.png', 'eyes_closed.png')),
        # 4
        ShortBreakInfo(10, "посмотреть в окно", 1,
                ('window.png',)),
        # 5
        ShortBreakInfo(40, "закрыть глаза ладонями", 1,
                ("palming.png",)),
        # 6
        ShortBreakInfo(50, 'повороты головы до упора', 3,
                ('head_default.png', 'head_right.png', 'head_default.png', 'head_left.png')),
        # 7
        ShortBreakInfo(50, 'наклоны шеи вперёд и назад', 3,
                ('neck_default.png', 'neck_bend_backwards.png', 'neck_default.png', 'neck_bend_forwards.png')),
        # 8
        ShortBreakInfo(50, 'наклоны шеи влево и вправо', 3,
                ('head_default.png', 'neck_tilt_right.png', 'head_default.png', 'neck_tilt_left.png')),
        # 9
        ShortBreakInfo(50, 'вытягивание шеи вперёд и назад', 3,
                ('neck2_default.png', 'neck2_move_forwards.png', 'neck2_default.png', 'neck2_move_backwards.png')),
        # 10
        ShortBreakInfo(60, 'наклонять голову вверх и вниз смотря на одну и ту же точку в пространстве', 3,
                ('head_default.png', 'head_training1_1.png', 'head_default.png', 'head_training1_2.png')),
        # 11
        ShortBreakInfo(60, 'крутить головой влево и вправо смотря на одну и ту же точку в пространстве', 3,
                ('head_default.png', 'head_training2_1.png', 'head_default.png', 'head_training2_2.png')),

    )

    PIXMAPS = []
    # values at start
    PIXMAPS_INDEX = 0
    COLOR_CHANGE_QUOTA = 0

    # if random.random() > 0.5:
    #     SPAWN_INSIDE_WINDOW = True
    # else:
    #     SPAWN_INSIDE_WINDOW = False
    SPAWN_INSIDE_WINDOW = True

    fw_windows = []

    long_break_last_run_tstamp = None
    short_break_last_run_tstamp = None

    SHORT_BREAK_ARG = "-shortbreak"
    LONG_BREAK_ARG = "-longbreak"

    long_break_running = False
    long_break_soon = False

    is_there_any_fullscreen_window = False

    # для того, чтобы showMessage отработал только один раз
    is_notifications_allowed = True
    info_str = {"short": "", "long": ""}
    block_short_tstamp = None

    last_activity_timestamp = time.time()

    start_timestamp = time.time()

    DURATION = 0.0

    is_odd = False

    WINDOWS_UPDATE_INTERVAL = 30

    dialog_wnds = []

    TITLE = "EyeVincent v0.9"

    auto_close_stamp = time.time()

    @classmethod
    def check_user_activity(cls):
        if (time.time() - cls.last_activity_timestamp) > 30*60:
            return False
        else:
            return True

    @staticmethod
    def get_long_time_info():
        time_passed_1 = time.time() - Globals.long_break_tstamp
        seconds_left_1 = Globals.LONG_BREAK_INTERVAL - time_passed_1
        return time_passed_1, seconds_left_1

    @staticmethod
    def get_short_time_info():
        time_passed_2 = time.time() - Globals.short_break_tstamp
        seconds_left_2 = Globals.SHORT_BREAK_INTERVAL - time_passed_2
        return time_passed_2, seconds_left_2

    @classmethod
    def generate_icons(cls):
        pause_pixmap = QPixmap(32, 32)
        pause_pixmap.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(pause_pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.black))
        r1 = QRect(QPoint(4, 4), QPoint(16-4, 32-4))
        r2 = QRect(QPoint(16+4, 4), QPoint(32-4, 32-4))
        painter.drawRect(r1)
        painter.drawRect(r2)
        painter.end()

        play_pixmap = QPixmap(32, 32)
        play_pixmap.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(play_pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.black))
        points = [
            QPointF(15, 6),
            QPointF(31, 16),
            QPointF(15, 26),
        ]
        poly = QPolygonF(points)
        painter.drawPolygon(poly, fillRule=Qt.WindingFill)
        painter.end()

        cls.pause_icon = QIcon(pause_pixmap)
        cls.play_icon = QIcon(play_pixmap)

        path = os.path.join(
            os.path.dirname(__file__),
            'eyeVincentIcon.png'
            )
        paused_tray_pixmap = QPixmap(path)
        painter = QPainter()
        painter.begin(paused_tray_pixmap)
        painter.setOpacity(0.7)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(paused_tray_pixmap.rect())
        painter.setOpacity(1.0)
        painter.setBrush(QBrush(Qt.red))
        r1 = QRect(QPoint(4, 4), QPoint(16-4, 32-4))
        r2 = QRect(QPoint(16+4, 4), QPoint(32-4, 32-4))
        painter.drawRect(r1)
        painter.drawRect(r2)
        painter.end()

        cls.paused_tray_icon = QIcon(paused_tray_pixmap)

class SymbolInfo():
    pass

def generate_symbols_pixmaps():
    symbols = (
        "あアイウエオカきキくクけケこコさサ"
        "しシすスせセそソたタちチつツてテと"
        "トなナにニぬヌねネのノはハひヒふフ"
        "ヘほホまマみミむムめメもモやヤゆユ"
        "よヨラりリるルれレろロわワをヲんン"
    )
    colors = (
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 0),

        (0, 1, 0),
        (0, 1, 1),
        (1, 0, 0),
        (1, 1, 0),
    )
    for color in colors:
        m_value = int(100 + 155*random.random())
        color_value = list(map(lambda x: x*m_value, color))
        color_slot = list()
        Globals.PIXMAPS.append(color_slot)
        for symbol in symbols:
            pixmap = QPixmap(100, 60)
            pixmap.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(pixmap)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QPainter.Antialiasing, True)
            font = painter.font()
            font.setPixelSize(60)
            painter.setFont(font)
            painter.setPen(QPen(QColor(*color_value)))
            rect = QRect(QPoint(0, 0), QSize(100, 60))
            painter.drawText(rect, Qt.AlignCenter, symbol)
            painter.end()
            color_slot.append(pixmap)
            # pixmap.save(f'{symbol}{color}.jpg')

def format_time(value):
    mins = value // 60
    secs = value - mins*60
    ceil = math.ceil
    if mins:
        return "{:02}:{:02}".format(int(mins), int(secs))
    else:
        return "{}".format(int(secs) if int(secs) else '')

class StylizedUIBase():

    button_style = """QPushButton{
        font-size: 18px;
        color: #303940;
        text-align: center;
        border-radius: 5px;
        background: rgb(220, 220, 220);
        font-family: 'Consolas';
        font-weight: bold;
        border: 3px dashed rgb(30, 30, 30);
        padding: 5px;
        height: 40px;
    }
    QPushButton:hover{
        background-color: rgb(253, 203, 54);
        color: black;
    }
    QPushButton#bottom, QPushButton#quit{
        color: rgb(210, 210, 210);
        background-color: none;
        border: none;
        text-decoration: underline;
    }
    QPushButton#quit{
        color: rgb(200, 70, 70);
    }
    QPushButton#bottom:hover{
        color: rgb(200, 0, 0);
        color: white;
        background-color: rgba(200, 200, 200, 0.1);
    }
    QPushButton#quit:hover{
        color: rgb(220, 0, 0);
        background-color: rgba(220, 50, 50, 0.1);
    }
    """
    title_label_style = """
        font-weight: bold;
        font-size: 18px;
        color: white;
        margin-bottom: 14px;
        text-align: center;
        font-weight: bold;
        width: 100px;
    """
    info_label_style = """
        font-size: 15px;
        color: yellow;
        margin: 2px;
        text-align: center;
    """

    CLOSE_BUTTON_RADIUS = 50

    def mouseMoveEvent(self, event):
        if self.inside_close_button():
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self.update()

    def mouseReleaseEvent(self, event):
        if self.inside_close_button():
            if Globals.DEBUG:
                sys.exit()
            else:
                hide_dialog()

    def get_close_btn_rect(self):
        top_right_corner = self.rect().topRight()
        close_btn_rect = QRect(
            top_right_corner.x() - self.CLOSE_BUTTON_RADIUS,
            top_right_corner.y() - self.CLOSE_BUTTON_RADIUS,
            self.CLOSE_BUTTON_RADIUS * 2,
            self.CLOSE_BUTTON_RADIUS * 2,
        )
        return close_btn_rect

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        painter.setClipping(True)
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.setClipPath(path)
        painter.setPen(Qt.NoPen)
        # color = QColor("#303940")
        color = QColor(48, 57, 64)
        color = QColor(30, 30, 30)
        painter.setBrush(QBrush(color))
        painter.drawPath(path)
        self.draw_close_button(painter)
        # color = QColor(150, 30, 30)
        # color = QColor(48, 57, 64)
        color = QColor(58, 67, 74)
        color = QColor(10, 10, 10)
        painter.setPen(QPen(color, 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        painter.end()

    def mapped_cursor_pos(self):
        return self.mapFromGlobal(QCursor().pos())

    def inside_close_button(self):
        close_btn_rect = self.get_close_btn_rect()
        top_right_corner = self.rect().topRight()
        diff = top_right_corner - self.mapped_cursor_pos()
        distance = math.sqrt(pow(diff.x(), 2) + pow(diff.y(), 2))
        size = close_btn_rect.width()/2
        client_area = QRect(QPoint(close_btn_rect.x(), 0), QSize(int(size), int(size)))
        return distance < self.CLOSE_BUTTON_RADIUS and \
            client_area.contains(self.mapped_cursor_pos())

    def draw_close_button(self, painter):
        if self.inside_close_button():
            painter.setOpacity(.6)
        else:
            painter.setOpacity(.3)
        painter.setBrush(QBrush(QColor(150, 150, 150), Qt.SolidPattern))
        painter.setPen(Qt.NoPen)
        close_btn_rect = self.get_close_btn_rect()
        top_right_corner = self.rect().topRight()
        painter.drawEllipse(close_btn_rect)
        w_ = int(self.CLOSE_BUTTON_RADIUS/2-5)
        cross_pos = top_right_corner + QPoint(-w_, w_)
        painter.setPen(QPen(Qt.white, 4, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.setOpacity(1.0)
        painter.drawLine(
            cross_pos.x()-int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.y()-int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.x()+int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.y()+int(self.CLOSE_BUTTON_RADIUS/8)
        )
        painter.drawLine(
            cross_pos.x()+int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.y()-int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.x()-int(self.CLOSE_BUTTON_RADIUS/8),
            cross_pos.y()+int(self.CLOSE_BUTTON_RADIUS/8)
        )

    def show_at_center(self):
        self.show()
        cp = QDesktopWidget().availableGeometry().center()
        qr = self.frameGeometry()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.activateWindow()

class StylizedDialog(QWidget, StylizedUIBase):
    WIDTH = 500
    STYLE = "color: white; font-size: 18px;"

    STARTUP_CONFIG = (
        'eyeVincentLauncher',
        os.path.join(os.path.dirname(__file__), "eyeVincentLauncher.pyw")
    )

    def __init__(self, *args, notification=True, **kwargs):
        super().__init__( *args, **kwargs)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowModality(Qt.WindowModal)
        main_layout = QVBoxLayout()

        self.label = QLabel()
        self.notification_mode = notification
        if self.notification_mode:
            self.label.setText(f"{Globals.TITLE}\nСкоро большой перерыв")
        else:
            self.label.setText(f'{Globals.TITLE}')
        self.label.setStyleSheet(self.title_label_style)
        self.label.setFixedWidth(self.WIDTH - self.CLOSE_BUTTON_RADIUS*2)
        self.label.setWordWrap(True)
        self.label.setCursor(Qt.ArrowCursor)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_handler)
        self.timer.setInterval(100)
        self.timer.start()
        main_layout.addWidget(self.label)
        hor_layout = QVBoxLayout()


        checkbox_style = """
            QCheckBox {
                font-family: 'Consolas';
                color: white;
                font-size: 18px;
                font-weight: normal;
            }
            QCheckBox::indicator:unchecked {
                background: gray;
            }
            QCheckBox::indicator:checked {
                background: green;
            }
            QCheckBox:checked {
                background-color: rgba(150, 150, 150, 50);
                color: rgb(100, 255, 100);
            }
            QCheckBox:unchecked {
                color: gray;
            }
        """

        if not self.notification_mode:
            self.chbx_ = QCheckBox("Запускать при старте Windows")
            # self.chbx_.setStyleSheet(self.STYLE)
            self.chbx_.setStyleSheet(checkbox_style)
            self.chbx_.setChecked(is_app_in_startup(self.STARTUP_CONFIG[0]))
            self.chbx_.stateChanged.connect(self.settings_checkbox_handler)
            layout_ = QVBoxLayout()
            layout_.setAlignment(Qt.AlignCenter)
            layout_.addSpacing(30)
            layout_.addWidget(self.chbx_)
            layout_.addSpacing(30)
            main_layout.addLayout(layout_)
        else:
            self.chbx_ = None


        if self.notification_mode:
            self.button_pass = QPushButton("Пропустить в этот раз")
            self.button_pass.setCursor(Qt.PointingHandCursor)
            self.button_pass.setStyleSheet(self.button_style)
            self.button_pass.setFocusPolicy(Qt.NoFocus)
            self.button_pass.clicked.connect(self.full_postpone_handler)

            self.button_postpone = QPushButton("Отложить на 10 минут")
            self.button_postpone.setCursor(Qt.PointingHandCursor)
            self.button_postpone.setStyleSheet(self.button_style)
            self.button_postpone.setFocusPolicy(Qt.NoFocus)
            self.button_postpone.clicked.connect(self.postpone_handler)

            self.button_exit = None
            self.button_suspend = None
        else:
            self.button_pass = None
            self.button_postpone = None

            self.button_exit = QPushButton(f'Закрыть {Globals.TITLE}')
            self.button_exit.setCursor(Qt.PointingHandCursor)
            self.button_exit.setStyleSheet(self.button_style)
            self.button_exit.setFocusPolicy(Qt.NoFocus)
            self.button_exit.clicked.connect(self.exit_handler)
            self.button_exit.setObjectName("quit")

            self.button_suspend = QPushButton(f'Приостановить')
            self.button_suspend.setIcon(Globals.pause_icon)
            self.button_suspend.setCursor(Qt.PointingHandCursor)
            self.button_suspend.setStyleSheet(self.button_style)
            self.button_suspend.setFocusPolicy(Qt.NoFocus)
            self.button_suspend.clicked.connect(self.suspend_handler)

        self.button_startnow = QPushButton("Начать большой перерыв прямо сейчас")
        self.button_startnow.setCursor(Qt.PointingHandCursor)
        self.button_startnow.setStyleSheet(self.button_style)
        self.button_startnow.setFocusPolicy(Qt.NoFocus)
        self.button_startnow.clicked.connect(self.startnow_bandler)

        if self.button_postpone:
            hor_layout.addWidget(self.button_postpone)
        hor_layout.addWidget(self.button_startnow)
        if self.button_pass:
            hor_layout.addWidget(self.button_pass)
        if self.button_suspend:
            hor_layout.addSpacing(20)
            hor_layout.addWidget(self.button_suspend)
        if self.button_exit:
            hor_layout.addSpacing(20)
            hor_layout.addWidget(self.button_exit)

            # button = QPushButton(f'Сделать снимок памяти')
            # button.setStyleSheet(self.button_style)
            # button.setCursor(Qt.PointingHandCursor)
            # button.clicked.connect(memory_snapshot)
            # hor_layout.addSpacing(20)
            # hor_layout.addWidget(button)

        main_layout.addLayout(hor_layout)

        self.update_countdown_handler()

        self.setLayout(main_layout)
        self.resize(self.WIDTH, 160)
        self.setMouseTracking(True)

    def settings_checkbox_handler(self):
        self.handle_windows_startup_chbx(self.chbx_)

    def handle_windows_startup_chbx(self, sender):
        if sender.isChecked():
            add_to_startup(*self.STARTUP_CONFIG)
        else:
            remove_from_startup(self.STARTUP_CONFIG[0])

    def suspend_handler(self):
        Globals.paused = not Globals.paused
        app = QApplication.instance()
        default_tray_icon = app.property("keep_ref_to_icon")
        sti = app.property('sti')
        if Globals.paused:
            button_text = "Возобновить"
            icon = Globals.play_icon
            sti.setIcon(Globals.paused_tray_icon)
            Globals.delta_long = time.time() - Globals.long_break_tstamp
            Globals.delta_short = time.time() - Globals.short_break_tstamp
        else:
            button_text = "Приостановить"
            icon = Globals.pause_icon
            sti.setIcon(default_tray_icon)
            Globals.long_break_tstamp = time.time() - Globals.delta_long
            Globals.short_break_tstamp = time.time() - Globals.delta_short
        self.button_suspend.setIcon(icon)
        self.button_suspend.setText(button_text)

    def exit_handler(self):
        self.hide()
        ret = QMessageBox.question(
            None,
            'Подтверждение закрытия',
            "Вы действительно хотите закрыть приложение?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            print('exit from handler')
            app = QApplication.instance()
            Globals.RUN_LED_GARLAND = False
            app.exit()
        else:
            self.show()

    def close(self):
        self.timer.stop()
        self.timer.timeout.disconnect(self.update_handler)
        if self.button_pass:
            self.button_pass.clicked.disconnect(self.full_postpone_handler)
            self.button_pass.deleteLater()
            del self.button_pass
        if self.button_postpone:
            self.button_postpone.clicked.disconnect(self.postpone_handler)
            self.button_postpone.deleteLater()
            del self.button_postpone
        if self.button_exit:
            self.button_exit.clicked.disconnect(self.exit_handler)
            self.button_exit.deleteLater()
            del self.button_exit
        if self.button_suspend:
            self.button_suspend.clicked.disconnect(self.suspend_handler)
            self.button_suspend.deleteLater()
            del self.button_suspend
        if self.button_startnow:
            self.button_startnow.clicked.disconnect(self.startnow_bandler)
            self.button_startnow.deleteLater()
            del self.button_startnow
        if self.chbx_:
            self.chbx_.stateChanged.disconnect(self.settings_checkbox_handler)
            self.chbx_.deleteLater()
            del self.chbx_
        if self.label:
            self.label.deleteLater()
            del self.label
        super().close()

    def startnow_bandler(self):
        Globals.long_break_tstamp = time.time() - Globals.LONG_BREAK_INTERVAL
        interval_handler()
        self.standard_button_handler()

    def postpone_handler(self):
        update_long_tstamp(60*10) # 10 минут
        interval_handler()
        self.standard_button_handler()

    def full_postpone_handler(self):
        update_long_tstamp(60*60, add_remaining_time=False) # 1 час
        Globals.long_break_running = True # чтобы срабатывал перезапуск в случае отмены большого перерыва
        interval_handler()
        self.standard_button_handler()

    def standard_button_handler(self):
        hide_dialog()

    def update_countdown_handler(self):
        print('update_timer', id(self))
        if not self.notification_mode:
            data1 = Globals.info_str['long'][0]
            data2 = Globals.info_str['short']
            if Globals.is_there_any_fullscreen_window:
                fullscreen_info = "Сейчас открыто полноэкранное приложение, и в таком случае напоминания о перерывах не будет"
            else:
                fullscreen_info = ""
            s = f'{Globals.TITLE}\n\n{fullscreen_info}\n\n{data1}\n{data2}'
            self.label.setText(s)
            del s
        data = Globals.info_str['long'][1]
        if data:
            sss = f" ({data})"
        else:
            sss = f""
        s = f"Начать большой перерыв прямо сейчас{sss}"
        self.button_startnow.setText(s)
        del sss
        del s
        if self.notification_mode:
            self.activateWindow()

    def update_handler(self):
        self.update_countdown_handler()
        self.update()

class ForegroundWindow(QWidget):
    def repeat_every_element(self, imgs_list, repeat_count):
        repeat_count = max(1, repeat_count)
        out = []
        for el in imgs_list:
            for n in range(repeat_count):
                out.append(el)
        return out

    def is_long_duration(self):
        return self.duration > Globals.LONG_DURATION_TRESHOLD

    def __init__(self, num, space_rect, remind_data, duration):
        super().__init__()

        # print(remind_data)
        self.remind_info = remind_data.name
        self.remind_images_list = self.repeat_every_element(remind_data.images,
                remind_data.slow_factor)
        # print(self.remind_images_list)
        self.images = []
        if isinstance(self.remind_images_list, str):
            l = list()
            l.append(self.remind_images_list)
            self.remind_images_list = l
        for image_filename in self.remind_images_list:
            path = os.path.join(Globals.IMAGES_FOLDERPATH, image_filename)
            image = QImage(path)
            self.images.append(image)
        self.images_indexes = itertools.cycle(range(len(self.images)))
        if len(self.images) > 1:
            self.current_image_index = next(self.images_indexes)
        else:
            self.current_image_index = 0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowModality(Qt.WindowModal)
        self.num = num
        self.FADE_SECONDS = 1.0
        self.space_rect = space_rect

        self.background_pixmap = QPixmap(space_rect.size())
        self.background_pixmap.fill(Qt.black)
        self.start_time = time.time()
        self.start_time_tick = time.time()
        self.end_time = self.start_time + Globals.DURATION
        self.duration = Globals.DURATION
        self.positions = []

        if self.is_long_duration():
            self.move(space_rect.topLeft())
            self.resize(space_rect.size())
        else:
            r = self.get_short_break_mode_rect(center=self.space_rect.center())
            self.resize(r.size())
            self.move(r.topLeft())


        if self.is_long_duration():
            w = QPlainTextEdit("")
            style = """
            QPlainTextEdit{
                background-color: transparent;
                color: white;
                border: none;
                font-size: 15pt;
            }
            """
            w.setStyleSheet(style)
            w.contextMenuEvent = self.contextMenuEvent
            layout = QVBoxLayout()
            layout.setContentsMargins(200, int(self.rect().height()/2)+100, 200, 0)
            layout.addWidget(w)
            def save_to_disk():
                _if = datetime.datetime.fromtimestamp(Globals.start_timestamp).isoformat()
                filename = _if.replace("T", " ").replace(":", "-").split(".")[0]
                with open(f'memo{filename}.txt', "w+", encoding="utf8") as file:
                    file.write(w.toPlainText())
            w.textChanged.connect(save_to_disk)
            self.setLayout(layout)

        # print(self.frameGeometry(), self.frameGeometry().size())

        self.bkg_color_value = QColor(0, 0, 0, 50)

        # ! раньше с той версией модуля для PyQt5 прога спокойно вывозила 350, а сейчас только 50, лол!
        for i in range(Globals.SYMBOLS_COUNT):
            data = self.init_symbol_data()
            self.positions.append(data)
        self.update_background()
        self.show()

    def init_symbol_data(self):

        w = self.width()
        h = self.height()
        if Globals.SPAWN_INSIDE_WINDOW:
            self.start_pos_y = -h+2*h*random.random()
        else:
            self.start_pos_y = -h*random.random()
        data = SymbolInfo()
        data.pos = QPoint(int(w*random.random()), int(self.start_pos_y))
        if (time.time() - self.start_time) % Globals.HOLD_COLOR_PERIOD < Globals.HOLD_COLOR_PERIOD-3:
            if Globals.COLOR_CHANGE_QUOTA:
                Globals.COLOR_CHANGE_QUOTA -= 1
                indexes = list(range(len(Globals.PIXMAPS)))
                Globals.PIXMAPS_INDEX = random.choice(indexes)
        else:
            Globals.COLOR_CHANGE_QUOTA = 25
        data.symbol_height = 10+50*random.random()
        data.pixmap = random.choice(Globals.PIXMAPS[Globals.PIXMAPS_INDEX])
        data.speed = data.symbol_height
        return data

    def update_background(self):
        if Globals.is_odd:
            painter = QPainter()
            painter.begin(self.background_pixmap)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.fillRect(self.background_pixmap.rect(), self.bkg_color_value)
            for data in self.positions:
                data.pos += QPoint(0, int(data.speed) )
                s_rect = QRect(QPoint(0, 0), QSize(100, 60))
                d_rect = QRect(data.pos, QSize(int(100*(data.symbol_height/60)), int(data.symbol_height)))
                painter.drawPixmap(d_rect, data.pixmap, s_rect)
                if data.pos.y()-100 > self.rect().height():
                    self.positions[self.positions.index(data)] = self.init_symbol_data()
            painter.end()
        self.update()

    def check_time_to_exit(self):
        if time.time() > self.end_time + self.FADE_SECONDS:
            app = QApplication.instance()
            app.exit()

    def get_estimated_time_str(self):
        delta = self.end_time - time.time()
        if self.is_long_duration():
            info = "Время Большого Перерыва\nДелай планку!"
        else:
            # info = self.remind_info
            info = ""
        if delta > 0:
            out = "{}\n{}".format(info, format_time(delta))
        else:
            out =  ""
        return out.strip()

    def update(self):
        super().update()
        self.check_time_to_exit()

    def get_short_break_mode_rect(self, center=None):
        r = QRect(QPoint(0, 0), QSize(320, 180))
        if center is not None:
            r.moveCenter(center)
        return r

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        delta = self.end_time - time.time()

        if delta > 0:
            self.opacity_factor = (time.time() - self.start_time)/self.FADE_SECONDS
            self.opacity_factor = min(1.0, self.opacity_factor)
        else:
            self.opacity_factor = (self.end_time + self.FADE_SECONDS - time.time())/self.FADE_SECONDS
            self.opocity_factor = min(0.0, self.opacity_factor)

        if not self.is_long_duration():
            painter.setClipping(True)
            path = QPainterPath()
            rect = self.get_short_break_mode_rect()
            path.addRoundedRect(QRectF(rect), 20, 20)
            painter.setClipPath(path)
        painter.setOpacity(0.9*self.opacity_factor)

        if self.is_long_duration():
            painter.drawPixmap(QPoint(0, 0), self.background_pixmap)
        else:
            bkg_color = QColor(self.bkg_color_value)
            bkg_color.setAlphaF(1.0)
            painter.fillRect(self.rect(), bkg_color)
        painter.setOpacity(1.0*self.opacity_factor)
        painter.setPen(QPen(QColor(255, 255, 255), 1))

        if not self.is_long_duration():
            image = self.images[self.current_image_index]
            delta = time.time() - self.start_time_tick
            if delta > 0.5:
                self.start_time_tick = time.time()
                if len(self.images) > 1:
                    self.current_image_index = next(self.images_indexes)

            draw_pos_rect = image.rect()
            # draw_pos_rect = QRect(QPoint(0,0), QSize(int(image.width()*1.5), int(image.height()*1.5)))
            draw_pos_rect.moveCenter(self.rect().center())
            painter.drawImage(draw_pos_rect, image, image.rect())

        font = painter.font()
        font.setPixelSize(25)
        # painter.setPen(QPen(QColor(255, 0, 0)))
        painter.setFont(font)
        r = self.get_short_break_mode_rect()
        r.moveCenter(self.rect().center())
        if self.is_long_duration():
            painter.drawText(r, Qt.AlignHCenter | Qt.AlignTop, self.get_estimated_time_str())

        # font.setFamily("Consolas")

        if not self.is_long_duration():
            painter.setClipping(False)


        now = datetime.datetime.now()
        now = str(now).split(".")[0].replace(" ", "\n")
        painter.setPen(QPen(Qt.gray))
        r = self.rect()
        r.setBottom(r.bottom()-500)
        painter.drawText(r, Qt.AlignCenter | Qt.AlignVCenter, now)

        painter.end()

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        contextMenu.setStyleSheet("""
        QMenu{
            padding: 0px;
            font-size: 13pt;
            font-weight: bold;
            font-family: 'Consolas';
        }
        QMenu::item {
            padding: 15px 55px;
            background: #303940;
            color: rgb(230, 230, 230);
        }
        QMenu::item:selected {
            background-color: rgb(253, 203, 54);
            color: rgb(50, 50, 50);
            /* border-left: 2px dashed #303940; */
        }""");
        halt = contextMenu.addAction("Закрыть")
        halt.setIconVisibleInMenu(False)
        # pos = self.mapToGlobal(event.pos())
        pos = QCursor().pos()
        action = contextMenu.exec_(pos)
        if action == halt:
            app = QApplication.instance()
            app.exit()

def show_system_tray(app, icon):
    sti = QSystemTrayIcon(app)
    sti.setIcon(icon)
    @pyqtSlot()
    def on_trayicon_activated(reason):
        if reason in [QSystemTrayIcon.Trigger, QSystemTrayIcon.Context]:
            show_dialog(Globals.long_break_soon)
        return
    sti.activated.connect(on_trayicon_activated)
    sti.setToolTip(Globals.TITLE)
    sti.show()
    return sti

def hide_dialog():
    for dw in Globals.dialog_wnds:
        dw.setParent(None)
        dw.close()
        dw.deleteLater()

    import gc
    gc.collect()

    Globals.dialog_wnds.clear()

def show_dialog(notification):
    hide_dialog()
    # if not is_there_any_fullscreen_window():
    dw = StylizedDialog(notification=notification)
    dw.show_at_center()
    Globals.dialog_wnds.append(dw)

def auto_close_on_fullscreen_window():
    if time.time() - Globals.auto_close_stamp > 2.0:
        Globals.auto_close_stamp = time.time()
        # for window in Globals.fw_windows:
        #     window.hide()
        window = Globals.fw_windows[0]
        offset_value = QPoint(0, -window.rect().height())
        # так как в это время по центру каждого экрана показывается окно с уведомлением,
        # то в таком случае мы немного сдвигаем вверх центральную координату на величину высоты окна уведомления,
        # иначе пришлось бы прятать все окна уведомлений перед проверкой и снова их показывать апосля,
        # а это в свою очередь вызвало бы неприятный эффект мерцания
        if is_there_any_fullscreen_window(offset=offset_value):
            app = QApplication.instance()
            app.exit()
        # for window in Globals.fw_windows:
        #     window.show()

def window_handler():
    auto_close_on_fullscreen_window()
    Globals.is_odd = not Globals.is_odd
    for window in Globals.fw_windows:
        window.update_background()


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class RECT(Structure):
    _fields_ = [
        ('left',   wintypes.ULONG),
        ('top',    wintypes.ULONG),
        ('right',  wintypes.ULONG),
        ('bottom', wintypes.ULONG)
    ]

def range_int_limit(value):
    value = min(value, 2147483647)
    value = max(value, -2147483648)
    return value

POS_ = POINT()
WIN_RECT_ = RECT()

def is_there_any_fullscreen_window(offset=QPoint(0, 0)):

    global POS_, WIN_RECT_

    desktop = QDesktopWidget()
    for i in range(0, desktop.screenCount()):
        screen_rect = desktop.screenGeometry(screen=i)
        screen_center = screen_rect.center()
        POS_.x = c_long(screen_center.x() + offset.x())
        POS_.y = c_long(screen_center.y() + offset.y())
        hwnd = windll.user32.WindowFromPoint(POS_)

        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        not_exception_window = True # for single-monitor systems
        try:
            active_window_path = psutil.Process(pid).exe()
            if active_window_path.lower().endswith("explorer.exe"):
                not_exception_window = False
        except:
            pass

        vlc_window = False
        try:
            active_window_path = psutil.Process(pid).exe()
            if active_window_path.lower().endswith("vlc.exe"):
                vlc_window = True
        except:
            pass

        ret = windll.user32.GetWindowRect(hwnd, byref(WIN_RECT_))
        left_value = 0 if WIN_RECT_.left == 4294967288 else WIN_RECT_.left
        top_value = 0 if WIN_RECT_.top == 4294967288 else WIN_RECT_.top
        win_rect_qt_win10 = QRect(
            range_int_limit(left_value),
            range_int_limit(top_value),
            range_int_limit(WIN_RECT_.right - left_value - 1),
            range_int_limit(WIN_RECT_.bottom - top_value - 1),
        )
        win_rect_qt_win8_1 = QRect(
            range_int_limit(left_value),
            range_int_limit(top_value),
            range_int_limit(WIN_RECT_.right - left_value),
            range_int_limit(WIN_RECT_.bottom - top_value),
        )
        result = not_exception_window and \
                (win_rect_qt_win10 == screen_rect or win_rect_qt_win8_1 == screen_rect or vlc_window)
        # print(result, screen_rect, win_rect_qt_win10, win_rect_qt_win8_1)
        if result:
            desktop.deleteLater()
            del desktop
            return True
    desktop.deleteLater()
    del desktop
    return False

def call_app_with_arg(arg):
    a1 = not is_there_any_fullscreen_window()
    a2 = Globals.check_user_activity()
    if all((a1, a2)):
        if arg == Globals.LONG_BREAK_ARG:
            hide_dialog()
        subprocess.Popen([sys.executable, __file__, arg])

def update_long_tstamp(duration=None, from_now=False, add_remaining_time=True):
    if duration is None:
        Globals.long_break_tstamp = time.time() + Globals.LONG_BREAK_DURATION
        Globals.short_break_tstamp = time.time() + Globals.LONG_BREAK_DURATION
        Globals.block_short_tstamp = time.time()
    else:
        if add_remaining_time:
            no_remaining_time = 0
        else:
            _, no_remaining_time = Globals.get_long_time_info()
        if from_now:
            Globals.long_break_tstamp = time.time() + duration - no_remaining_time
        else:
            Globals.long_break_tstamp += duration - no_remaining_time
    Globals.is_notifications_allowed = True
    Globals.long_break_soon = False

# def memory_snapshot():
#     snapshot = tracemalloc.take_snapshot()
#     # top_stats = snapshot.statistics('lineno')
#     # snapshot = snapshot.filter_traces((
#     #         tracemalloc.Filter(False, r"C:\Python310\lib\tracemalloc.py"),
#     #         tracemalloc.Filter(False, r"C:\Python310\lib\logging"),
#     #         tracemalloc.Filter(False, "<unknown>"),
#     # ))
#     top_stats = snapshot.statistics('lineno')

#     locale.setlocale(locale.LC_ALL, "russian")
#     datetime_string = time.strftime("%A, %d %B %Y %X").capitalize()
#     dt = "{0} {1} {0}".format(" "*15, datetime_string)
#     dt_framed = "{0}\n{1}\n{0}\n".format("-"*len(dt), dt)

#     with open('memory_snapshot.txt', "a+", encoding="utf8") as file:
#         print("\n\n\n", file=file)
#         print(dt_framed, file=file)
#         print("\n", file=file)
#         # print("[ Top 10 ]", file=file)
#         for stat in top_stats:
#             print(stat, file=file)

def show_tray_notification():
    if Globals.SHOW_TRAY_NOTIFICATION:
        app = QApplication.instance()
        sti = app.property('sti')
        icon = app.property('keep_ref_to_icon')
        msg_title = f"Напоминание от {Globals.TITLE}!"
        msg_txt = "Через 30 секунд большой перерыв"
        sti.showMessage(msg_title, msg_txt, icon, 1000)

def rerun_this_app():
    hours_3 = 60*60*3
    if time.time() - Globals.start_timestamp > hours_3:
        time_str = time.strftime("%d %B %Y %X")
        timecode = f"{time_str}"
        set_time_left_args = ()
        if (not Globals.long_break_soon) or (not Globals.long_break_running):
            _, seconds_left_1 = Globals.get_long_time_info()
            set_time_left_args = ("-set_time_left", str(seconds_left_1))
        subprocess.Popen([sys.executable, sys.argv[0], "-rerun", timecode, *set_time_left_args])
        sys.exit()

def interval_handler():

    # memory_snapshot()

    Globals.is_there_any_fullscreen_window = is_there_any_fullscreen_window()
    if Globals.paused:
        return

    time_passed_1, seconds_left_1 = Globals.get_long_time_info()
    if time_passed_1 > Globals.LONG_BREAK_INTERVAL:
        update_long_tstamp()
        hide_dialog()
        call_app_with_arg(Globals.LONG_BREAK_ARG)
        Globals.long_break_last_run_tstamp = time.time()
    elif time_passed_1 > 0 and Globals.is_notifications_allowed:
        if seconds_left_1 < 30:
            Globals.long_break_soon = True
            if Globals.is_there_any_fullscreen_window:
                update_long_tstamp(60*10)
                # переносим на 10 минут
                hide_dialog()
            else:
                if Globals.check_user_activity():
                    show_tray_notification()
                    show_dialog(True)
                    Globals.is_notifications_allowed = False
        else:
            Globals.long_break_soon = False
        if Globals.long_break_running:
            Globals.long_break_running = False
            if Globals.MEMORY_GUARD:
                rerun_this_app()

    lrt = Globals.long_break_last_run_tstamp
    if lrt and (time.time() - lrt) < Globals.LONG_BREAK_DURATION:
        break_seconds_left = Globals.LONG_BREAK_DURATION - (time.time() - lrt)
        msg = "Идёт большой перерыв {}".format(format_time(break_seconds_left))
        Globals.info_str['long'] = (msg, 0)
        Globals.long_break_running = True
    else:
        ft = format_time(seconds_left_1)
        msg = "До большого перерыва осталось {}".format(ft)
        Globals.info_str['long'] = (msg, ft)
        # Globals.long_break_running = False

    time_passed_2, seconds_left_2 = Globals.get_short_time_info()
    bst = Globals.block_short_tstamp
    short_blocked = bst and ((time.time() - bst) < Globals.LONG_BREAK_DURATION)
    if time_passed_2 > Globals.SHORT_BREAK_INTERVAL:
        if not short_blocked:
            Globals.short_break_tstamp = time.time() + Globals.SHORT_BREAK_DURATION
            # для предотвращения одновременного появления вместе
            # с напоминанием большого перерыва
            if seconds_left_1 > (30 + Globals.SHORT_BREAK_DURATION):
                call_app_with_arg(Globals.SHORT_BREAK_ARG)
            Globals.short_break_last_run_tstamp = time.time()
    elif time_passed_2 > 0:
        pass

    lrt = Globals.short_break_last_run_tstamp
    if lrt and (time.time() - lrt) < Globals.SHORT_BREAK_DURATION:
        break_seconds_left = Globals.SHORT_BREAK_DURATION - (time.time() - lrt)
        msg = "Идёт короткий перерыв {}".format(format_time(break_seconds_left))
        Globals.info_str['short'] = msg
    else:
        ft = format_time(seconds_left_2)
        msg = "До короткого перерыва осталось {}".format(ft)
        Globals.info_str['short'] = msg

def is_long_break(args=sys.argv):
    return Globals.LONG_BREAK_ARG in args[1:]

def is_short_break(args=sys.argv):
    return Globals.SHORT_BREAK_ARG in args[1:]

def excepthook(exc_type, exc_value, exc_tb):
    # пишем инфу о краше
    if isinstance(exc_tb, str):
        traceback_lines = exc_tb
    else:
        traceback_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    locale.setlocale(locale.LC_ALL, "russian")
    datetime_string = time.strftime("%A, %d %B %Y %X").capitalize()
    dt = "{0} {1} {0}".format(" "*15, datetime_string)
    dt_framed = "{0}\n{1}\n{0}\n".format("-"*len(dt), dt)
    with open("crush.log", "a+", encoding="utf8") as crush_log:
        crush_log.write("\n"*10)
        crush_log.write(dt_framed)
        crush_log.write("\n")
        crush_log.write(traceback_lines)
    print(traceback_lines)
    app = QApplication.instance()
    sti = app.property('sti')
    if sti:
        sti.hide()
    sys.exit()

def get_from_this_folder(filename):
    return os.path.join(os.path.dirname(__file__), filename)

def get_global_status():
    return Globals.RUN_LED_GARLAND

class BackgroundThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.start_time = time.time()

    def run(self):
        while (time.time() - self.start_time) < Globals.DURATION and get_global_status():
            path = get_from_this_folder("Keyboard_LED_garland.pyw")
            child = subprocess.Popen('pythonw %s' % path, stdout=subprocess.PIPE)
            child.communicate()

def exit_from_main(sti, thread_instance):
    if thread_instance:
        thread_instance.exit()
    app = QApplication.instance()
    sti = app.property('sti')
    if sti:
        sti.hide()
    sys.exit()

def reset_timestamp():
    Globals.last_activity_timestamp = time.time()
    # print("reset timestamp ", time.time())

def listening():
    from pynput import mouse
    from pynput import keyboard
    def keyboard_cb(*args):
        # print("keyboard")
        reset_timestamp()

    def mouse_cb(*args):
        # print("mouse")
        reset_timestamp()
    on_press = on_release = keyboard_cb
    on_move = on_click = on_scroll = mouse_cb
    listener_keyboard = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener_keyboard.start()
    listener_mouse = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    listener_mouse.start()

def main():
    os.chdir(os.path.dirname(__file__))
    sys.excepthook = excepthook

    RERUN_ARG = '-rerun'
    if RERUN_ARG not in sys.argv:
        subprocess.Popen([sys.executable, *sys.argv, RERUN_ARG])
        sys.exit()

    app = QApplication(sys.argv)
    generate_symbols_pixmaps()

    appid = 'sergei_krumas.eye_vincent.client.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    path_icon = "eyeVincentIcon.png"
    icon = None
    icon = QIcon(path_icon)
    app.setProperty("keep_ref_to_icon", icon)
    app.setWindowIcon(icon)
    timer = QTimer()
    sti = None

    thread_instance = None

    if Globals.DEBUG or is_long_break() or is_short_break():
        remind_data = None
        if is_long_break():
            Globals.DURATION = Globals.LONG_BREAK_DURATION
        elif is_short_break():
            Globals.DURATION = Globals.SHORT_BREAK_DURATION
        elif Globals.DEBUG:
            Globals.DURATION = Globals.DEBUG_DURATION
            try:
                remind_data = Globals.SHORT_BREAK_INFOS[Globals.NUM_REQUEST]
            except:
                remind_data = None
        desktop = QDesktopWidget()

        if remind_data is None:
            # remind_data = random.choice(Globals.SHORT_BREAK_INFOS)
            remind_data = random.choices(
              Globals.SHORT_BREAK_INFOS,
              weights=tuple(map(lambda x: x.probability, Globals.SHORT_BREAK_INFOS)),
              k=1)[0]

        for i in range(0, desktop.screenCount()):
            space_for_window = desktop.screenGeometry(screen=i)
            n = i+1
            # print(space_for_window, space_for_window.center())
            fw = ForegroundWindow(n, space_for_window, remind_data, Globals.DURATION)
            Globals.fw_windows.append(fw)
        desktop.deleteLater()
        del desktop

        timer.setInterval(int(Globals.WINDOWS_UPDATE_INTERVAL))
        timer.timeout.connect(window_handler)
        window_handler()

        if not Globals.DEBUG and Globals.DURATION > Globals.LONG_DURATION_TRESHOLD:
            thread_instance = BackgroundThread()
            thread_instance.start()

    else:
        # Требуется создать окно, иначе в QDesktopWidget не попадёт инфа
        # об изменении разрешения экрана при запуске тех же видеоигр;
        # Это окно специально создаётся за пределами видимой области
        w = QWidget()
        w.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        w.resize(100, 100)
        w.move(1000, -200)
        w.show()

        Globals.generate_icons()

        arg_key = "-set_time_left"
        if arg_key in sys.argv:
            arg_pos = sys.argv.index(arg_key)
            try:
                time_left = float(sys.argv[arg_pos+1])
                Globals.long_break_tstamp = time.now() - (Globals.LONG_BREAK_INTERVAL - time_left)
            except:
                pass

        timer.setInterval(400)
        sti = show_system_tray(app, icon)
        timer.timeout.connect(interval_handler)
        interval_handler()
        app.setQuitOnLastWindowClosed(False)

    y = threading.Thread(target=listening)
    y.start()
    timer.start()
    app.setProperty('sti', sti)

    app.exec_()

    exit_from_main(sti, thread_instance)


def _main():
    try:
        main()
    except Exception as e:
        excepthook(type(e), e, traceback.format_exc())

if __name__ == "__main__":
    _main()
