import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.warning=false'

# Flask Web Server Imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from AppOpener import open as open_app
import asyncio
import cv2
from ctypes import cast, POINTER
from datetime import datetime
import edge_tts
from googlesearch import search
import math
from mpl_toolkits.mplot3d import Axes3D

# ========== FIX: Set Matplotlib backend to Qt before importing pyplot ==========
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import numpy as np
import psutil
import pyautogui
import pygetwindow as gw
import pyperclip
import pygame
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import queue
import re
import random
import requests
import screen_brightness_control as sbc
import sounddevice as sd
import speech_recognition as sr
import socket
import subprocess
import sympy as sp
import time
import threading
from vosk import Model, KaldiRecognizer
import json
import webbrowser
import wmi
import wikipedia
import win32com.client
import sys
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QObject, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen, QFont
from PyQt6.QtWidgets import QApplication, QWidget
from plyer import notification
import ollama

try:
    import pywhatkit as kit
except Exception:
    kit = None

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# [MEMORY] Global conversation history (shared across web and voice)
conversation_history = []          # list of {"role": "user"/"assistant", "content": ...}
MAX_HISTORY = 10                   # keep last 10 exchanges

# ============================================================================
# CONTACTS DATABASE
# ============================================================================
CONTACTS = {
    "mummy": "+919511494101", "Mummy": "+919511494101", "amma": "+919511494101",
    "bhai": "+919005772921", "Bhai": "+919005772921", "brother": "+919005772921",
    "papa": "+919511494101",
    "moco": "+919208235482", "niharika": "+919208235482", "n.j.": "+919208235482",
    "nj bhn": "+919208235482", "nj": "+919208235482",
    "didi": "919250681200", "ritu": "+919250681200",
    "ritu didi": "+919250681200", "ritudidi": "+919250681200",
    "praveen": "+918423527466",
    "kalpneet chacha": "+917398037625",
    "mahesh chacha": "+919792287089",
    "me": "+918604592552"
}

# ============================================================================
# DEFAULT CITY FOR WEATHER
# ============================================================================
DEFAULT_CITY = "Lucknow"
weather_city = DEFAULT_CITY

# ============================================================================
# ARYA AVATAR CLASS (PyQt6 Visual Interface)
# ============================================================================
class AryaAvatar(QWidget):
    def __init__(self):
        super().__init__()
        self.pen_coil = QPen()
        self.pen_core = QPen()
        self.font_hud = QFont("Consolas", 10, QFont.Weight.Bold)
        self.pulse = 0
        self.is_speaking = False
        self.is_listening = False
        self.show_hud = False
        self.live_cpu = 0
        self.live_ram = 0
        self.live_bat = 100
        self.live_gpu = "0%"
        self.cpu_fan = "0 RPM"
        self.gpu_fan = "0 RPM"
        self.initUI()
        self.start_threads()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(350, 300)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)
        self.show()

    def start_threads(self):
        self.hardware_active = True
        threading.Thread(target=self.background_hardware_worker, daemon=True).start()

    def background_hardware_worker(self):
        while self.hardware_active:
            if self.show_hud:
                self.live_cpu = int(psutil.cpu_percent())
                self.live_ram = int(psutil.virtual_memory().percent)
                bat = psutil.sensors_battery()
                self.live_bat = bat.percent if bat else 100
            time.sleep(2.0)

    def update_animation(self):
        self.pulse += 0.08
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        if not self.show_hud:
            self.draw_coils_mode(painter, cx, cy)
        else:
            self.draw_hud_mode(painter, cy)

    def draw_coils_mode(self, p, cx, cy):
        if self.is_speaking:
            speed, cs, amp = (0.2, 80, 12)
        elif self.is_listening:
            speed, cs, amp = (1.5, -220, 6)
        else:
            speed, cs, amp = (0.6, 40, 3)
        if self.is_speaking:
            p_c = QColor(255, 0, 0)
        elif self.is_listening:
            p_c = QColor(0, 255, 255)
        else:
            p_c = QColor(255, 215, 0)
        base_radius = 60 + (math.sin(self.pulse * speed) * amp)
        rot = int(self.pulse * cs) % 360
        grad = QRadialGradient(float(cx), float(cy), float(base_radius + 40))
        grad.setColorAt(0, QColor(p_c.red(), p_c.green(), p_c.blue(), 60))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - base_radius - 40), int(cy - base_radius - 40),
                     int(base_radius*2 + 80), int(base_radius*2 + 80))
        self.pen_coil.setWidth(3)
        self.pen_coil.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for ring_offset in [-20, 0, 20]:
            current_r = base_radius + ring_offset
            self.pen_coil.setColor(QColor(p_c.red(), p_c.green(), p_c.blue(), 200 - abs(ring_offset*5)))
            p.setPen(self.pen_coil)
            for angle in [0, 60, 120, 180, 240, 300]:
                p.drawArc(
                    int(cx - current_r), int(cy - current_r),
                    int(current_r * 2), int(current_r * 2),
                    int((rot + angle + (ring_offset * 2)) * 16), 25 * 16
                )
        if self.is_speaking:
            self.pen_core.setStyle(Qt.PenStyle.SolidLine)
        else:
            self.pen_core.setStyle(Qt.PenStyle.DashLine)
        self.pen_core.setColor(p_c)
        self.pen_core.setWidth(4)
        p.setPen(self.pen_core)
        p.drawEllipse(int(cx - base_radius), int(cy - base_radius),
                     int(base_radius*2), int(base_radius*2))

    def draw_hud_mode(self, p, cy):
        alpha = int(120 + (math.sin(self.pulse * 2.0) * 80))
        box_w, box_h = int(self.width() * 0.8), 160
        box_rect = QRect(int((self.width() - box_w) // 2), 70, box_w, box_h)
        p.setBrush(QColor(0, 0, 0, 150))
        p.setPen(QPen(QColor(0, 255, 255, alpha), 2))
        p.drawRoundedRect(box_rect, 15, 15)
        bx, by = box_rect.x() + 25, box_rect.y() + 25
        bar_w = int((box_w - 90) // 2)
        self.draw_bar(p, bx, by, bar_w, self.live_cpu, "CPU", alpha)
        self.draw_bar(p, bx + bar_w + 30, by, bar_w, self.live_ram, "RAM", alpha)
        self.draw_bar(p, bx, by + 45, bar_w, self.live_gpu, "GPU", alpha)
        self.draw_bar(p, bx + bar_w + 30, by + 45, bar_w, self.live_bat, "BAT", alpha)
        p.setFont(self.font_hud)
        p.setPen(QColor(200, 200, 200, alpha))
        p.drawText(bx, by + 95, f"ARYA: ACTIVE | FAN: CPU {self.cpu_fan} | GPU {self.gpu_fan}")

    def draw_bar(self, p, x, y, w, val, label, alpha):
        v = int(str(val).replace('%','')) if str(val).replace('%','').isdigit() else 0
        p.setBrush(QColor(50, 50, 50, 100))
        p.drawRoundedRect(x, y, w, 8, 4, 4)
        p.setBrush(QColor(0, 255, 0, alpha))
        p.drawRoundedRect(x, y, int((v/100)*w), 8, 4, 4)
        p.setPen(QColor(255, 255, 255, alpha))
        p.drawText(x, y - 4, f"{label}: {v}%")

    def mouseDoubleClickEvent(self, e):
        self.show_hud = not self.show_hud
        self.resize(500, 450 if self.show_hud else 300)

    def mousePressEvent(self, e):
        self.drag_pos = e.globalPosition().toPoint()
        self.w_pos = self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.w_pos + (e.globalPosition().toPoint() - self.drag_pos))

    def set_speaking(self, speaking):
        self.is_speaking = speaking
        self.update()

    def set_listening(self, listening):
        self.is_listening = listening
        self.update()

# ============================================================================
# GLOBAL AVATAR INSTANCE
# ============================================================================
avatar = None

# ============================================================================
# SIGNAL BRIDGE FOR THREAD-SAFE PLOTTING
# ============================================================================
class PlotSignalBridge(QObject):
    plot_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

# ============================================================================
# GLOBAL CACHES & SPEECH CONTROL
# ============================================================================
_tts_cache = {}
_pygame_ready = False
_internet_cache = {"last": 0, "result": False}

# Interrupt control
_speech_stop_flag = False
_speech_lock = threading.Lock()
_speech_thread = None

# ============================================================================
# ANGRY SPEECH FUNCTION (HD Voice with Avatar Sync) – INTERRUPTIBLE
# ============================================================================
def angry_speak(text):
    global avatar, _pygame_ready, _internet_cache, _speech_stop_flag, _speech_thread

    if not text or not text.strip():
        return
    print(f"ARYA: {text}")

    # Stop any ongoing speech
    with _speech_lock:
        if _speech_thread and _speech_thread.is_alive():
            _speech_stop_flag = True
            pygame.mixer.music.stop()
            _speech_thread.join(timeout=0.3)
        _speech_stop_flag = False

    if avatar:
        avatar.set_speaking(True)

    # Cached internet check
    now = time.time()
    if now - _internet_cache["last"] > 3.0:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=0.8)
            _internet_cache["result"] = True
        except:
            _internet_cache["result"] = False
        _internet_cache["last"] = now
    online = _internet_cache["result"]

    # Define the playback function
    def _play():
        global _speech_stop_flag, _pygame_ready
        try:
            if online:
                # generate audio
                filename = f"angry_arya_{hash(text) % 100000}_{int(now*1000)}.mp3"
                async def generate():
                    voice_model = "hi-IN-SwaraNeural"
                    communicate = edge_tts.Communicate(text, voice_model, rate="+50%")
                    await communicate.save(filename)
                asyncio.run(generate())

                if not _pygame_ready:
                    pygame.mixer.init()
                    _pygame_ready = True

                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    if _speech_stop_flag:
                        pygame.mixer.music.stop()
                        break
                    pygame.time.Clock().tick(30)
                    time.sleep(0.005)

                pygame.mixer.music.unload()
                try:
                    os.remove(filename)
                except:
                    pass
            else:
                s.speak(text)
        except Exception:
            try:
                s.speak(text)
            except:
                pass
        finally:
            if avatar:
                avatar.set_speaking(False)

    # Start playback in a background thread
    with _speech_lock:
        _speech_thread = threading.Thread(target=_play, daemon=True)
        _speech_thread.start()

# ============================================================================
# SPEAKER CLASS (Windows SAPI5) – INTERRUPTIBLE
# ============================================================================
class Speaker:
    def __init__(self):
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        self.last_spoken = ""
        voices = self.engine.GetVoices()
        try:
            self.engine.Voice = voices.Item(1)
        except Exception:
            pass

    def speak(self, text):
        global avatar, _speech_stop_flag, _speech_thread

        if not text:
            return
        text = str(text)

        # Stop any ongoing speech from this engine
        with _speech_lock:
            if _speech_thread and _speech_thread.is_alive():
                _speech_stop_flag = True
                self.engine.Stop()
                _speech_thread.join(timeout=0.3)
            _speech_stop_flag = False

        if avatar:
            avatar.set_speaking(True)

        cleaned = ''.join(ch for ch in text.lower() if ch.isalnum() or ch.isspace())
        self.last_spoken = cleaned.strip()
        print(f"ARYA: {text}")
        length = len(text)
        rate = 3 if length > 120 else 2
        self.engine.Rate = rate

        # Define playback in thread
        def _play_sapi():
            try:
                self.engine.Speak(text, 1)  # SVSFlagsAsync = 1
                while self.engine.Status.RunningState == 1:
                    if _speech_stop_flag:
                        self.engine.Stop()
                        break
                    time.sleep(0.05)
            except:
                pass
            finally:
                if avatar:
                    avatar.set_speaking(False)

        with _speech_lock:
            _speech_thread = threading.Thread(target=_play_sapi, daemon=True)
            _speech_thread.start()

s = Speaker()

# ============================================================================
# AUTOMATE TYPING
# ============================================================================
def automate_typing(text, interval=0.1, delay=0.5):
    if not text:
        return
    angry_speak("Sir, I will start typing shortly. Please click on the text field.")
    time.sleep(delay)
    pyautogui.write(text, interval=interval)
    angry_speak("Typing completed, sir.")

# ============================================================================
# IMPROVED ADVANCED CALCULATOR – FIXED 3D PARSING
# ============================================================================
def advanced_calculator(cmd, s):
    try:
        query = cmd.lower().replace("arya", "").strip()
        if not query:
            angry_speak("What should I calculate or plot, sir?")
            return

        query = query.replace('^', '**')

        # --- 3D Plotting (with robust parsing) ---
        if any(word in query for word in ["3d", "three d", "surface"]):
            angry_speak("Generating 3D visual analysis, sir.")

            # Remove all known trigger words
            junk = ["plot", "3d", "three d", "graph", "of", "draw", "surface", "arya", "plus", "generate", "visualize", "show"]
            expr = query
            for word in junk:
                expr = re.sub(rf'\b{word}\b', '', expr)
            # If there's an '=', take everything before it (or after "of")
            if "=" in expr:
                expr = expr.split("=")[0].strip()
            if "surface of" in expr:
                expr = expr.split("surface of")[-1].strip()
            # Remove "is equal to", "equals", "equal to"
            expr = re.sub(r'is equal to', '', expr)
            expr = re.sub(r'equals', '', expr)
            expr = re.sub(r'equal to', '', expr)
            expr = expr.strip()
            if not expr:
                angry_speak("I didn't catch a valid 3D expression, sir.")
                return

            # Insert parentheses for function calls like sin x -> sin(x)
            funcs = ['sin', 'cos', 'tan', 'sqrt', 'log', 'exp']
            for f in funcs:
                expr = re.sub(rf'\b{f}\s+([a-zA-Z_][a-zA-Z0-9_]*)', rf'{f}(\1)', expr)
                expr = re.sub(rf'\b{f}\s*\(', rf'{f}(', expr)
            # Replace x->X, y->Y
            expr = re.sub(r'\bx\b', 'X', expr)
            expr = re.sub(r'\by\b', 'Y', expr)
            # Map functions to numpy
            func_map = {
                'sin': 'np.sin', 'cos': 'np.cos', 'tan': 'np.tan',
                'sqrt': 'np.sqrt', 'log': 'np.log', 'exp': 'np.exp',
                'pi': 'np.pi', 'e': 'np.e'
            }
            for f, npf in func_map.items():
                expr = expr.replace(f, npf)
            # Add implicit multiplication: 2X -> 2*X, X2 -> X*2, (X)(Y) -> (X)*(Y)
            expr = re.sub(r'(\d)([XY])', r'\1*\2', expr)
            expr = re.sub(r'([XY])(\d)', r'\1*\2', expr)
            expr = re.sub(r'\)([XY])', r')*\1', expr)
            expr = re.sub(r'([XY])\(', r'\1*(', expr)

            x_range = np.linspace(-5, 5, 80)
            y_range = np.linspace(-5, 5, 80)
            X, Y = np.meshgrid(x_range, y_range)

            try:
                Z = eval(expr, {"np": np, "X": X, "Y": Y})
                fig = plt.figure(figsize=(10, 7))
                ax = fig.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z, cmap='plasma', edgecolor='none', alpha=0.9)
                ax.set_title(f"3D: {expr}", color='#00ffcc')
                ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
                finite = np.isfinite(Z)
                if np.any(finite):
                    zmin, zmax = np.nanmin(Z[finite]), np.nanmax(Z[finite])
                    if np.isfinite(zmin) and np.isfinite(zmax):
                        ax.set_zlim(zmin, zmax)
                plt.style.use('dark_background')
                plt.ion()
                plt.show()
                plt.pause(0.1)
                return
            except Exception as e:
                print(f"3D eval error: {e}, expr: {expr}")
                angry_speak("Sir, there is a syntax error in the 3D equation.")
                return

        # --- 2D Plotting ---
        elif any(word in query for word in ["plot", "graph", "draw", "visualize"]):
            if "close" in query:
                plt.close('all')
                angry_speak("Closing all graphs, sir.")
                return
            angry_speak("Visualizing the function, sir.")
            plot_cmd = query
            for w in ["plot", "the", "graph", "of", "draw", "visualize", "a", "arya"]:
                plot_cmd = re.sub(rf'\b{w}\b', '', plot_cmd).strip()
            if not plot_cmd:
                angry_speak("What function should I plot, sir?")
                return

            expr = plot_cmd
            funcs = ['sin', 'cos', 'tan', 'sqrt', 'log', 'exp']
            for f in funcs:
                expr = re.sub(rf'\b{f}\s+([a-zA-Z_][a-zA-Z0-9_]*)', rf'{f}(\1)', expr)
                expr = re.sub(rf'\b{f}\s*\(', rf'{f}(', expr)
            if 'x' in expr and 'x_vals' not in expr:
                expr = expr.replace('x', 'x_vals')
            func_map = {
                'sin': 'np.sin', 'cos': 'np.cos', 'tan': 'np.tan',
                'sqrt': 'np.sqrt', 'log': 'np.log', 'exp': 'np.exp',
                'pi': 'np.pi', 'e': 'np.e'
            }
            for f, npf in func_map.items():
                expr = expr.replace(f, npf)
            expr = re.sub(r'(\d)(x_vals)', r'\1*\2', expr)
            expr = re.sub(r'(x_vals)(\d)', r'\1*\2', expr)
            expr = re.sub(r'\)(x_vals)', r')*\1', expr)
            expr = re.sub(r'(x_vals)\(', r'\1*(', expr)

            x_vals = np.linspace(-10, 10, 1000)
            try:
                y_vals = eval(expr, {"np": np, "x_vals": x_vals})
                if 'tan' in expr:
                    y_vals[np.abs(y_vals) > 10] = np.nan
                plt.figure(figsize=(10, 5))
                plt.style.use('dark_background')
                plt.plot(x_vals, y_vals, color='#00ffcc', linewidth=2, label=f"y = {plot_cmd}")
                plt.axhline(0, color='white', alpha=0.3)
                plt.axvline(0, color='white', alpha=0.3)
                plt.grid(color='gray', linestyle='--', alpha=0.2)
                plt.ylim(-10, 10)
                plt.legend()
                plt.ion()
                plt.show()
                plt.pause(0.1)
                return
            except Exception:
                angry_speak("Sir, syntax error in math visualization.")
                return

        # --- Numerical Calculation ---
        else:
            replacements = {
                "plus": "+", "add": "+", "minus": "-", "subtract": "-",
                "multiply": "*", "times": "*", "into": "*",
                "divided by": "/", "divide": "/", "by": "/",
                "square root": "sqrt", "root": "sqrt",
                "power": "**", "square": "**2", "cube": "**3"
            }
            calc_expr = query
            for word, sym in replacements.items():
                calc_expr = calc_expr.replace(word, sym)
            calc_expr = re.sub(r'(calculate|solve|what|is|the|value|of)', '', calc_expr).strip()
            calc_expr = re.sub(r'(\d)\s*x\s*(\d)', r'\1*\2', calc_expr)

            if not calc_expr:
                angry_speak("I didn't understand the calculation, sir.")
                return

            try:
                if 'x' in calc_expr and "=" in calc_expr:
                    left, right = calc_expr.split("=")
                    res = sp.solve(sp.sympify(f"({left}) - ({right})"))
                else:
                    res = sp.sympify(calc_expr).evalf(5)
                result = str(res)
                pyperclip.copy(result)
                print(f"Final Result: {result}")
                angry_speak(f"The result is {result}. Copied to clipboard.")
            except Exception:
                angry_speak("Sir, I couldn't evaluate that expression.")
    except Exception as e:
        print(f"Master Calc Error: {e}")
        angry_speak("Sir, I encountered an error in the mathematical expression.")

# ============================================================================
# BRIGHTNESS CONTROL
# ============================================================================
def control_brightness(cmd):
    try:
        # Local references for speed
        sbc_set = sbc.set_brightness
        press = pyautogui.press

        nums = [int(s) for s in re.findall(r'\d+', cmd)]
        current = sbc.get_brightness()[0] if nums else None

        # Handle no-number commands (full / low)
        if not nums:
            if "full" in cmd or "maximum" in cmd:
                sbc_set(100)
                press("brightnessup")
                angry_speak("Brightness set to maximum, sir.")
            elif "low" in cmd or "minimum" in cmd:
                sbc_set(15)
                press("brightnessdown")
                angry_speak("Brightness set to minimum.")
            return

        target = nums[0]

        if "increase" in cmd or "up" in cmd:
            new_val = min(100, current + target)
            sbc_set(new_val)
            press("brightnessup", presses=max(1, target // 2))
            angry_speak(f"Increased brightness to {new_val} percent.")

        elif "decrease" in cmd or "down" in cmd:
            new_val = max(0, current - target)
            sbc_set(new_val)
            press("brightnessdown", presses=max(1, target // 2))
            angry_speak(f"Decreased brightness to {new_val} percent.")

        else:  # absolute set
            new_val = max(0, min(100, target))
            sbc_set(new_val)
            press("brightnessup")   # These two presses are just to update the system UI
            press("brightnessdown")
            angry_speak(f"Brightness set to {new_val} percent.")

    except Exception as e:
        print(f"Brightness Error: {e}")
        angry_speak("I encountered an error adjusting the display, sir.")

# ============================================================================
# CLOSE APP UNIVERSALLY
# ============================================================================
def close_app_universal(app_name):
    app_name = app_name.lower().strip()
    angry_speak(f"Attempting to close {app_name}, sir.")

    # Visual close (mouse to X button)
    try:
        windows = gw.getWindowsWithTitle(app_name)
        if windows:
            target = windows[0]
            if not target.isActive:
                target.activate()
                time.sleep(0.2)                     # reduced from 0.5

            cross_x = target.right - 30
            cross_y = target.top + 20
            print(f"[+] Moving mouse to close {target.title}...")
            pyautogui.moveTo(cross_x, cross_y, duration=0.3, tween=pyautogui.easeInOutQuad)  # faster mouse
            time.sleep(0.15)                        # reduced wait
            pyautogui.click()
            time.sleep(0.3)                         # brief pause then verify
            if not gw.getWindowsWithTitle(app_name):
                angry_speak(f"{app_name} closed successfully.")
                return
            else:
                print("[-] Visual close failed, proceeding to terminal.")
    except Exception as e:
        print(f"[-] Visual close error: {e}")

    # Terminal override (CMD window)
    angry_speak("Target is stubborn. Initiating terminal override.")
    print("[!] Terminal Kill Activated for:", app_name)

    pyautogui.hotkey('win', 'r')
    time.sleep(0.3)                                 # reduced from 0.5
    pyautogui.write('cmd', interval=0.02)           # faster typing
    pyautogui.press('enter')
    time.sleep(0.5)                                 # reduced from 1.0
    pyautogui.write(f"taskkill /f /im {app_name}* /t", interval=0.02)
    time.sleep(0.3)                                 # reduced from 0.5
    pyautogui.press('enter')
    time.sleep(0.5)                                 # reduced from 1.5
    pyautogui.write("exit", interval=0.02)
    pyautogui.press('enter')
    angry_speak("Termination complete, sir.")

# ============================================================================
# VOLUME CONTROL
# ============================================================================
def control_volume(cmd):
    try:
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        nums = [int(s) for s in re.findall(r'\d+', cmd)]
        current_vol = round(volume.GetMasterVolumeLevelScalar() * 100)
        if "mute" in cmd and "unmute" not in cmd:
            pyautogui.press("volumemute")
            angry_speak("Audio muted, sir.")
            return
        if "unmute" in cmd:
            volume.SetMute(0, None)
            pyautogui.press("volumeup")
            pyautogui.press("volumedown")
            angry_speak("Audio restored.")
            return
        if not nums:
            target_step = 5
        else:
            target_value = nums[0]
        if "increase" in cmd or "up" in cmd:
            change = nums[0] if nums else 10
            presses = change // 2
            pyautogui.press("volumeup", presses=presses)
            angry_speak(f"Volume increased, sir.")
        elif "decrease" in cmd or "down" in cmd:
            change = nums[0] if nums else 10
            presses = change // 2
            pyautogui.press("volumedown", presses=presses)
            angry_speak(f"Volume decreased.")
        else:
            new_vol = max(0, min(100, nums[0]))
            volume.SetMasterVolumeLevelScalar(new_vol / 100, None)
            pyautogui.press("volumeup")
            pyautogui.press("volumedown")
            angry_speak(f"Volume set to {new_vol} percent.")
    except Exception as e:
        print(f"Volume Error: {e}")
        angry_speak("I couldn't adjust the volume, sir.")

# ============================================================================
# SYSTEM STATUS
# ============================================================================
def get_system_status():
    try:
        battery = psutil.sensors_battery()
        percent = battery.percent
        plugged = battery.power_plugged
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_usage = psutil.virtual_memory().percent
        status = "Charging" if plugged else "Discharging"
        report = f"Sir, the system is at {percent} percent battery and is currently {status}. CPU usage is {cpu_usage} percent."
        print(report)
        angry_speak(report)
        if not plugged:
            if percent <= 20:
                angry_speak("Battery is low. Activating Power Saver and reducing brightness, sir.")
                os.system('powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a')
                os.system('powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,30)')
                if percent <= 10:
                    angry_speak("Battery is critical. Terminating background heavy applications.")
                    smart_app_killer()
            else:
                print("Battery is healthy. No optimization needed.")
        else:
            os.system('powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e')
    except Exception as e:
        print(f"System Status Error: {e}")
        angry_speak("Sir, I encountered an error while accessing system hardware.")

# ============================================================================
# TIME AND DATE
# ============================================================================
def get_temporal_info(query):
    query = query.lower()
    if "time" in query or "pune baje hain" in query:
        strTime = datetime.now().strftime("%I:%M %p")
        response = f"Sir, the time is {strTime}."
        print(f"ARYA: {response}")
        angry_speak(response)
    elif "date" in query or "today" in query or "aaj kya tarikh hai" in query:
        strDate = datetime.now().strftime("%B %d, %Y")
        response = f"Sir, today's date is {strDate}."
        print(f"ARYA: {response}")
        angry_speak(response)
    else:
        pass

# ============================================================================
# MASTER OPEN HANDLER
# ============================================================================
import webbrowser, pyautogui, time, shutil, os

def master_open_handler(cmd, s, open_private_func):
    cmd_lp = cmd.lower().strip()

    if any(x in cmd_lp for x in ["private", "incognito", "private window"]):   # private browser
        browsers = {"brave":"brave", "chrome":"chrome", "edge":"edge", "firefox":"firefox"}
        target = next((b for b in browsers if b in cmd_lp), None)
        if target:
            res = open_private_func(target)
            angry_speak(f"Opening {res} in private mode, Sir.")
            print(f"[+] Ghost Mode: {res} Private Window")
        else:
            angry_speak("Which browser, Sir? Or should I open Brave in private mode?")
        return
    if "search on google" in cmd_lp:                                            # google search
        query = cmd_lp.replace("search on google", "").strip()
        angry_speak(f"Searching Google for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        time.sleep(0.5)
        angry_speak("Information searched is displayed.")
        return
    if "search on youtube" in cmd_lp:                                           # youtube search
        term = cmd_lp.replace("search on youtube", "").strip()
        angry_speak(f"Searching YouTube for {term}, sir.")
        webbrowser.open(f"https://www.youtube.com/results?search_query={term}")
        return
    if any(x in cmd_lp for x in ["open instagram", "instagram open", "instagram kholo"]):  # instagram
        angry_speak("Ok sir, opening Instagram.")
        webbrowser.open("https://www.instagram.com")
        time.sleep(0.5)
        angry_speak("Instagram opened, sir.")
        return
    if "open youtube" in cmd_lp:                                                # youtube
        if any(x in cmd_lp for x in ["searchbox", "search box", "search area", "search"]):
            angry_speak("Opening YouTube search for you, sir.")
            webbrowser.open("https://www.youtube.com")
            time.sleep(3)
            pyautogui.press('/')
            angry_speak("Search box is active. What should I look for?")
        else:
            angry_speak("Opening YouTube, sir.")
            webbrowser.open("https://www.youtube.com")
        return
    if any(x in cmd_lp for x in [".com", ".in", ".org", "www."]):               # direct URL
        app = cmd_lp.replace("open website", "").replace("open", "").strip()
        angry_speak(f"Accessing {app} on the web, sir.")
        pyautogui.hotkey('win', 'r')
        time.sleep(0.3)
        pyautogui.press('backspace')
        url = app if app.startswith(("http", "www.")) else f"https://{app}"
        pyautogui.write(url, interval=0.03)
        time.sleep(0.3)
        pyautogui.press('enter')
        return
    if "open" in cmd_lp:                                                        # generic open
        target = cmd_lp.replace("open", "").strip()
        if not target:
            angry_speak("What should I open, sir?")
            target = wait_for_reply(timeout=6)
            if not target:
                return
        exe = shutil.which(target) or shutil.which(f"{target}.exe")           # try local
        if exe:
            angry_speak(f"Opening local app: {target}, sir.")
            print(f"[+] Launching: {exe}")
            os.startfile(exe)
            return
        try:                                                                    # try AppOpener
            from AppOpener import open as open_app
            open_app(target, match_closest=True, output=False)
            angry_speak(f"Opened {target} via AppOpener, sir.")
            return
        except:
            pass
        angry_speak(f"Could not find {target} locally. Opening web version, sir.")  # web fallback
        webbrowser.open(f"https://www.{target}.com")
        return

    angry_speak("I didn't understand what to open, sir.")                      # fallback


# ============================================================================
# MEDIA CONTROL
# ============================================================================
def handle_media_control(query, s):
    cmd = query.lower().strip()
    if any(x in cmd for x in ["pause", "play", "stop song", "resume"]):
        pyautogui.press('playpause')
        angry_speak("Done, sir.")
        return True
    elif any(x in cmd for x in ["next video", "next song", "change song"]):
        pyautogui.press('nexttrack')
        angry_speak("Playing next, sir.")
        return True
    elif any(x in cmd for x in ["previous video", "previous song", "piche karo"]):
        pyautogui.press('prevtrack')
        angry_speak("Playing previous, sir.")
        return True
    elif "skip" in cmd or "forward" in cmd:
        seconds = 10
        if "20" in cmd: seconds = 20
        elif "30" in cmd: seconds = 30
        elif "40" in cmd: seconds = 40
        elif "50" in cmd: seconds = 50
        elif "minute" in cmd or "60" in cmd: seconds = 60
        press_count = int(seconds / 5) if "vlc" in cmd else int(seconds / 10)
        if press_count == 0: press_count = 1
        angry_speak(f"Skipping forward {seconds} seconds.")
        for _ in range(press_count):
            pyautogui.press('right')
            time.sleep(0.05)
        return True
    elif "rewind" in cmd or "back" in cmd:
        seconds = 10
        if "20" in cmd: seconds = 20
        elif "30" in cmd: seconds = 30
        press_count = int(seconds / 10)
        if press_count == 0: press_count = 1
        angry_speak(f"Rewinding {seconds} seconds.")
        for _ in range(press_count):
            pyautogui.press('left')
            time.sleep(0.05)
        return True
    return False

# ============================================================================
# WHATSAPP MESSAGE HANDLER
# ============================================================================
def handle_whatsapp_message(cmd, s, listen_func, CONTACTS):
    """Send WhatsApp message to contacts"""
    if "send message" in cmd or "message" in cmd:
        if is_online():
            clean_name = cmd.lower()
            junk_words = ["jarvis", "nova", "send a message to", "send message to", "send message", "message to", "message"]
            for word in junk_words:
                clean_name = clean_name.replace(word, "")
            name = clean_name.strip()
            print(f"[+] DEBUG: Extracted Name -> '{name}'")

            if name in CONTACTS:
                number = CONTACTS[name]
                s.speak(f"What is the message for {name}?")
                print("[*] Waiting for Jarvis to finish speaking...")
                time.sleep(3.5)
                msg = ""
                attempts = 3
                for i in range(attempts):
                    print(f"[?] Listening for message (Attempt {i+1}/{attempts})...")
                    temp_msg = wait_for_reply(timeout=10)
                    if temp_msg and len(temp_msg) > 1:
                        if "what is the message" in temp_msg.lower():
                            print("[-] Echo detected (Jarvis heard himself). Ignoring...")
                            continue
                        msg = temp_msg
                        break
                    else:
                        print("[-] Silence detected, listening again...")

                if msg:
                    s.speak("Opening WhatsApp and preparing message.")
                    os.system(f"start whatsapp://send?phone={number}")
                    print("[+] Waiting for WhatsApp UI to load...")
                    time.sleep(7)
                    full_msg = f"[ Automated by JARVIS for RUPESH ] : {msg}"
                    pyautogui.write(full_msg, interval=0.07)
                    time.sleep(2)
                    pyautogui.press('enter')
                    s.speak("Message sent, sir.")
                else:
                    s.speak("I didn't catch the message, sir.")
            else:
                if not name:
                    s.speak("Whom should I send the message to, sir?")
                else:
                    s.speak(f"Sir, {name} is not in your contact list.")
        else:
            s.speak("Internet is required for WhatsApp, sir.")

# ============================================================================
# WINDOW MANAGEMENT
# ============================================================================
def window_management(cmd, s):
    try:
        active_window = gw.getActiveWindow()
        if "minimize" in cmd or "minimise" in cmd:
            if active_window:
                angry_speak("Minimizing the current window, sir.")
                try:
                    min_x = active_window.right - 120
                    min_y = active_window.top + 20
                    print("[+] Visually moving to Minimize button...")
                    pyautogui.moveTo(min_x, min_y, duration=0.6, tween=pyautogui.easeInOutQuad)
                    time.sleep(0.2)
                    pyautogui.click()
                    time.sleep(0.3)
                    if not active_window.isMinimized:
                        active_window.minimize()
                except Exception:
                    active_window.minimize()
            else:
                angry_speak("Sir, I couldn't find any active window to minimize.")
        elif "maximize" in cmd or "maximise" in cmd:
            if active_window:
                angry_speak("Maximizing window, sir.")
                try:
                    max_x = active_window.right - 70
                    max_y = active_window.top + 20
                    print("[+] Visually moving to Maximize button...")
                    pyautogui.moveTo(max_x, max_y, duration=0.6, tween=pyautogui.easeInOutQuad)
                    time.sleep(0.2)
                    pyautogui.click()
                    time.sleep(0.3)
                    if not active_window.isMaximized:
                        active_window.maximize()
                except Exception:
                    active_window.maximize()
            else:
                angry_speak("No active window found to maximize.")
        elif "switch" in cmd:
            angry_speak("Opening window partitions to switch, sir.")
            pyautogui.hotkey('ctrl', 'alt', 'tab')
            print("[+] Displaying Window Grid...")
            time.sleep(1.5)
            pyautogui.press('right')
            time.sleep(0.5)
            pyautogui.press('enter')
            angry_speak("Window switched.")
    except Exception as e:
        print(f"[-] Error in Window Management: {e}")
        angry_speak("I encountered an issue while managing windows, sir.")

# ============================================================================
# FEEDBACK HANDLER
# ============================================================================
def handle_feedback(cmd, s):
    if any(x in cmd for x in ["good job", "well done", "nice work", "great job"]):
        responses = [
            "Always happy to help, sir.",
            "Thank you, sir. I strive for excellence.",
            "Just doing my job, sir.",
            "I am glad I could meet your expectations.",
            "It's my duty to answer your questions.",
            "I am your assistant, and will do what you want, sir."
        ]
        reply = random.choice(responses)
        print(f"ARYA: {reply}")
        angry_speak(reply)
        return True
    return False

# ============================================================================
# PC POWER COMMANDS
# ============================================================================
def pc_power(cmd, s):
    if any(l in cmd for l in ["lock", "sleep", "good night", "bye"]):
        angry_speak("locking the workstation, sir.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif any(sd in cmd for sd in ["shutdown", "power off", "switch off", "poweroff", "power of"]):
        angry_speak("Shutting down system in 5 seconds. Goodbye, sir.")
        os.system("shutdown /s /t 5")
    elif any(rs in cmd for rs in ["restart", "reon", "reonn", "re on", "re onn", "reboot", "re boot"]):
        angry_speak("Initiating system restart in 5 seconds.")
        os.system("shutdown /r /t 5")

# ============================================================================
# KEYBOARD AUTOMATION
# ============================================================================
def keyboard_automation(cmd, s, automate_typing, keyboard_shortcut, multi_paste):
    cmd_lp = cmd.lower()
    if "type this" in cmd_lp:
        text_to_type = cmd.replace("type this", "").strip()
        if text_to_type:
            automate_typing(text_to_type)
            angry_speak("typed what you said")
        else:
            angry_speak("What should I type, sir?")
    elif "write a note" in cmd_lp:
        angry_speak("Opening notepad and writing your note.")
        os.system("start notepad")
        time.sleep(3)
        automate_typing("This is an automated note from ARYA.", interval=0.05)
    elif "select all" in cmd_lp:
        keyboard_shortcut(['ctrl', 'a'])
        time.sleep(1)
        angry_speak("Selected. Now say copy to save it.")
    elif "copy all" in cmd_lp:
        keyboard_shortcut(['ctrl', 'a', 'c'])
        time.sleep(1)
        angry_speak("Text selected and copied. Tell me where to paste it.")
    elif "copy" in cmd_lp:
        keyboard_shortcut(['ctrl', 'c'])
        angry_speak("Text copied to clipboard.")
    elif "cut all" in cmd_lp:
        keyboard_shortcut(['ctrl', 'a', 'x'])
        angry_speak("All text cut to clipboard, sir.")
    elif "cut" in cmd_lp:
        keyboard_shortcut(['ctrl', 'x'])
        angry_speak("Text cut to clipboard.")
    elif "paste" in cmd_lp:
        if "times" in cmd_lp:
            try:
                word_to_num = {
                    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
                }
                nums = [int(n) for n in re.findall(r'\d+', cmd_lp)]
                times = nums[0] if nums else None
                if times is None:
                    for word, val in word_to_num.items():
                        if word in cmd_lp:
                            times = val
                            break
                if times:
                    angry_speak(f"Pasting {times} times, sir.")
                    multi_paste(times)
                else:
                    angry_speak("I didn't catch the count, sir.")
            except Exception as e:
                print(f"Paste Error: {e}")
                angry_speak("Error during multiple paste.")
        else:
            keyboard_shortcut(['ctrl', 'v'])
            angry_speak("Text pasted.")

# ============================================================================
# SYSTEM STATUS HANDLER
# ============================================================================
def system_status(cmd, s, get_system_status_func):
    cmd_lp = cmd.lower()
    if any(x in cmd_lp for x in ["performance", "usage", "internet", "status"]):
        status_info = get_system_status_func()
        print(f"ARYA: {status_info}")
        angry_speak(status_info)
        return True
    elif any(x in cmd_lp for x in ["battery status", "battery level", "power"]):
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "not plugged in"
            report = f"Sir, the battery is at {percent} percent and it is {plugged}."
            print(f"ARYA: {report}")
            angry_speak(report)
        else:
            angry_speak("Sir, I couldn't detect a battery. Are you on a Desktop?")
        return True
    return False

# ============================================================================
# SMART INFO SEARCH (Wikipedia, Google, AI)
# ============================================================================
def handle_smart_info_search(query, s, smart_search_func):
    if any(x in query for x in ["who is", "what is", "tell me about", "who made", "details of"]):
        stop_words = ["arya", "nova", "who is", "what is", "tell me about", "the founder of", "founder of", "who made", "details of"]
        topic = query
        for word in stop_words:
            topic = topic.replace(word, "")
        topic = topic.strip()
        if topic:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write(f'cmd /k "color a & title ARYA INTELLIGENCE REPOSITORY"', interval=0.002)
            pyautogui.press('enter')
            time.sleep(1.0)
            angry_speak(f"Accessing intelligence archives for {topic}. Initiating search sequence.")
            pyautogui.write(f"echo [ TARGET IDENTIFIED: {topic.upper()} ]", interval=0.01)
            pyautogui.press('enter')
            results = ""
            source = ""
            pyautogui.write("echo [ STATUS: SCANNING WIKIPEDIA DATABASE... ]", interval=0.001)
            pyautogui.press('enter')
            try:
                results = wikipedia.summary(topic, sentences=2)
                source = "WIKIPEDIA ARCHIVES"
            except Exception:
                pyautogui.write(f"echo [ ERROR: WIKI DATA MISSING ]", interval=0.001)
                pyautogui.press('enter')
                angry_speak("Wikipedia scan failed to return data. Switching to Google Deep Scan protocol.")
                pyautogui.write(f"echo [ STATUS: INITIATING GOOGLE DEEP SCAN... ]", interval=0.001)
                pyautogui.press('enter')
                try:
                    search_results = list(search(topic, num_results=1, advanced=True))
                    if search_results and search_results[0].description:
                        results = search_results[0].description
                        source = "GOOGLE DEEP SCAN"
                    else:
                        raise Exception("No Snippet")
                except Exception:
                    angry_speak("Web scan yielding no immediate summary. Attempting Neural Core computation.")
                    pyautogui.write("echo [ STATUS: ACCESSING NEURAL CORE... ]", interval=0.001)
                    pyautogui.press('enter')
                    try:
                        response = ollama.chat(
                            model='llama3.2:3b',
                            messages=[
                                {"role": "system", "content": "Give a short 2 sentence summary of the topic."},
                                {"role": "user", "content": topic}
                            ]
                        )
                        results = response['message']['content'].strip()
                        source = "INTERNAL NEURAL CORE"
                    except:
                        pyautogui.write("echo [ CRITICAL: ALL INTERNAL SCANS FAILED ]", interval=0.001)
                        pyautogui.press('enter')
                        pyautogui.write(f"echo [ STATUS: REDIRECTING TO WEB INTERFACE... ]", interval=0.001)
                        pyautogui.press('enter')
                        time.sleep(0.5)
                        pyautogui.write("exit", interval=0.01)
                        pyautogui.press('enter')
                        angry_speak(f"Sir, all scans have failed. I am opening the Google search results for {topic} in your browser.")
                        webbrowser.open(f"https://www.google.com/search?q={topic}")
                        return True
            if results:
                pyperclip.copy(results)
                clean_txt = results.replace('"', '').replace('(', '').replace(')', '').replace('&', 'and').replace('\n', ' ')
                pyautogui.write(f"echo [ SOURCE: {source} ]", interval=0.001)
                pyautogui.press('enter')
                pyautogui.write(f"echo DATA: {clean_txt}", interval=0.001)
                pyautogui.press('enter')
                pyautogui.write("echo. & echo [ LOG: DATA COPIED TO CLIPBOARD ]", interval=0.001)
                pyautogui.press('enter')
                angry_speak(f"Information retrieved from {source}. Synthesizing now.")
                angry_speak(results)
            time.sleep(1)
            pyautogui.write("exit", interval=0.002)
            pyautogui.press('enter')
            return True
    return False

# ============================================================================
# SYSTEM OPTIMIZATION (Visual Hacker Terminal)
# ============================================================================
def system_optimization(cmd, s):
    cmd_lp = cmd.lower()
    def run_hacker_terminal(commands_list):
        pyautogui.hotkey('win', 'r')
        time.sleep(0.5)
        pyautogui.write('cmd', interval=0.05)
        pyautogui.press('enter')
        time.sleep(1.0)
        pyautogui.write("color a", interval=0.002)
        pyautogui.press('enter')
        time.sleep(0.01)
        for command in commands_list:
            pyautogui.write(command, interval=0.001)
            pyautogui.press('enter')
            time.sleep(0.1)
        time.sleep(1)
        pyautogui.write("exit", interval=0.002)
        pyautogui.press('enter')
    if "clear ram" in cmd_lp:
        angry_speak("Clearing standby memory and cache, sir.")
        commands = [
            "echo Flushing DNS Cache...",
            "ipconfig /flushdns",
            "echo Deleting Temporary Files...",
            r"del /q /f /s %temp%\*",
            "echo Memory cleared and DNS flushed."
        ]
        run_hacker_terminal(commands)
        angry_speak("Memory cleared and DNS flushed.")
    elif any(x in cmd_lp for x in ["kill background apps", "close tools"]):
        angry_speak("Closing Steam, Discord, and other background tools to save resources.")
        apps_to_kill = [
            "steam.exe", "SteamService.exe", "steamwebhelper.exe",
            "Discord.exe", "EpicGamesLauncher.exe", "GalaxyClient.exe",
            "Spotify.exe", "PowerToys.exe"
        ]
        commands = ["echo Terminating Background Applications..."]
        for app in apps_to_kill:
            commands.append(f"taskkill /f /im {app}")
        commands.append("echo All specified tools closed.")
        run_hacker_terminal(commands)
        angry_speak("All background tools have been terminated, sir.")
    elif "extreme clean" in cmd_lp:
        angry_speak("Initiating extreme cleanup. Switching to pure performance mode.")
        commands = [
            "echo Initiating Extreme Cleanup...",
            r"del /q /f /s %temp%\*",
            "ipconfig /flushdns",
            'taskkill /f /im steam.exe /im Discord.exe /im Spotify.exe',
            'sc.exe stop "wuauserv"',
            'sc.exe stop "DiagTrack"',
            "echo System is now in pure performance mode."
        ]
        run_hacker_terminal(commands)
        angry_speak("System is now in pure performance mode. All cores are yours, sir.")

# ============================================================================
# INTERNET CHECK
# ============================================================================
def is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# ============================================================================
# KEYBOARD SHORTCUT
# ============================================================================
def keyboard_shortcut(keys):
    pyautogui.hotkey(*keys)

# ============================================================================
# CONTINUOUS LISTENING SYSTEM
# ============================================================================
PRIMARY_MIC = 1
FALLBACK_MIC = 0
last_mode = None
continuous_audio_queue = queue.Queue()
is_listening_continuous = False
listening_thread = None

def background_online_listener():
    global is_listening_continuous
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    try:
        mic = sr.Microphone(device_index=PRIMARY_MIC)
    except:
        mic = sr.Microphone(device_index=FALLBACK_MIC)
    print("🎤 Online Listener Active (Mic locked & always on)")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            while is_listening_continuous:
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=5)
                    query = r.recognize_google(audio, language="en-in")
                    if len(query) > 1:
                        print(f"User (Online): {query}")
                        continuous_audio_queue.put(query.lower())
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as e:
                    print(f"Recognition Error: {e}")
                    time.sleep(0.5)
    except Exception as e:
        print(f"Mic Hardware Error: {e}")

def background_offline_listener():
    global is_listening_continuous
    def start_stream(device_idx):
        return sd.RawInputStream(
            samplerate=16000, blocksize=4000, dtype='int16',
            channels=1, callback=offline_callback, device=device_idx
        )
    try:
        stream = start_stream(PRIMARY_MIC)
    except:
        stream = start_stream(FALLBACK_MIC)
    print("🎤 Offline Listener Active (Vosk always on)")
    with stream:
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except:
                break
        while is_listening_continuous:
            try:
                data = audio_queue.get(timeout=0.1)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if len(text) > 1:
                        print(f"User (Offline): {text}")
                        continuous_audio_queue.put(text.lower())
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Vosk Error: {e}")
                time.sleep(0.5)

def offline_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(bytes(indata))

def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(bytes(indata))

def start_continuous_listening(current_mode):
    global is_listening_continuous, listening_thread
    is_listening_continuous = True
    if current_mode:
        listening_thread = threading.Thread(target=background_online_listener, daemon=True)
    else:
        listening_thread = threading.Thread(target=background_offline_listener, daemon=True)
    listening_thread.start()

def listen():
    global last_mode, is_listening_continuous, active_listener_mode
    current_mode = is_online()
    if current_mode != last_mode:
        if current_mode and last_mode is not None:
            print("online")
        elif not current_mode and last_mode is not None:
            print("offline mode")
        last_mode = current_mode
        active_listener_mode = "switching"
        is_listening_continuous = False
        time.sleep(1.0)
        start_continuous_listening(current_mode)
    if not is_listening_continuous:
        start_continuous_listening(current_mode)
    try:
        query = continuous_audio_queue.get(timeout=0.5)
        clean_query = re.sub(r'[^\w\s]', '', query.lower()).strip()
        if hasattr(s, 'last_spoken') and s.last_spoken and len(clean_query) > 2:
            if clean_query in s.last_spoken or s.last_spoken in clean_query:
                print(f"[-] Echo Destroyed: Ignored my own voice.")
                return ""
            query_words = set(clean_query.split())
            spoken_words = set(s.last_spoken.split())
            if len(query_words) >= 3:
                match_count = len(query_words.intersection(spoken_words))
                if match_count / len(query_words) >= 0.6:
                    print(f"[-] Echo Destroyed: Ignored my own voice.")
                    return ""
        return query
    except queue.Empty:
        return ""

def wait_for_reply(timeout=8):
    time.sleep(1.0)
    while not continuous_audio_queue.empty():
        try:
            continuous_audio_queue.get_nowait()
        except:
            break
    print("⏳ ARYA is listening for your message...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            reply = continuous_audio_queue.get(timeout=0.5)
            if reply:
                print(f"✔️ Caught Message: {reply}")
                return reply
        except queue.Empty:
            continue
    return ""

def launch_app(app_name):
    try:
        open_app(app_name.lower().strip(), match_closest=True, output=False)
        return True
    except Exception as e:
        print(f"Launcher Error: {e}")
        return False

def multi_paste(n):
    angry_speak(f"Commencing multi-paste. I will paste the item {n} times in 5 seconds. Please click on the target field.")
    time.sleep(5)
    for i in range(n):
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(0.1)
    angry_speak("Task completed, sir.")

# ============================================================================
# USB DEVICE MONITORING
# ============================================================================
last_drive_count = len(psutil.disk_partitions())

def monitor_usb_devices():
    global last_drive_count
    try:
        current_partitions = psutil.disk_partitions(all=False)
        current_count = len(current_partitions)
        if current_count != last_drive_count:
            print(f"Drive count changed: {last_drive_count} -> {current_count}")
        if current_count > last_drive_count:
            last_drive_count = current_count
            new_drive = current_partitions[-1].device
            angry_speak(f"New storage device detected at drive {new_drive}.")
            print(f"Device Connected: {new_drive}")
        elif current_count < last_drive_count:
            last_drive_count = current_count
            angry_speak("USB disconnected, sir.")
            print("Device Disconnected")
    except Exception:
        pass

# ============================================================================
# INPUT DEVICE MONITORING
# ============================================================================
c = wmi.WMI()
last_input_count = len(c.Win32_PointingDevice()) + len(c.Win32_Keyboard())

def monitor_input_devices():
    global last_input_count
    try:
        mice = c.Win32_PointingDevice()
        keyboards = c.Win32_Keyboard()
        current_count = len(mice) + len(keyboards)
        if current_count > last_input_count:
            last_input_count = current_count
            angry_speak("New input device connected, sir. Mouse,keyboard is now active.")
            print("Input Device Connected")
        elif current_count < last_input_count:
            last_input_count = current_count
            angry_speak("input device disconnected.")
            print("Input Device Removed")
    except Exception:
        pass

# ============================================================================
# BLUETOOTH MONITORING
# ============================================================================
last_bt_count = len([d for d in c.Win32_PnPEntity() if "Bluetooth" in str(d.Caption) and d.ConfigManagerErrorCode == 0])

def monitor_bluetooth():
    global last_bt_count
    try:
        all_devices = c.Win32_PnPEntity()
        bt_devices = [d for d in all_devices if "Bluetooth" in str(d.Caption) and d.ConfigManagerErrorCode == 0]
        current_bt_count = len(bt_devices)
        if current_bt_count > last_bt_count:
            new_device_name = bt_devices[-1].Caption if bt_devices else "a device"
            angry_speak(f"Bluetooth device connected: {new_device_name}")
            print(f"Bluetooth Connected: {new_device_name}")
            last_bt_count = current_bt_count
        elif current_bt_count < last_bt_count:
            angry_speak("Bluetooth device disconnected, sir.")
            print("Bluetooth Disconnected")
            last_bt_count = current_bt_count
    except Exception:
        pass

# ============================================================================
# BATTERY CONNECTION MONITORING
# ============================================================================
last_plugged_state = psutil.sensors_battery().power_plugged

def monitor_battery_connection():
    global last_plugged_state
    battery = psutil.sensors_battery()
    percent = battery.percent
    is_plugged = battery.power_plugged
    seconds_left = battery.secsleft
    if is_plugged and not last_plugged_state:
        last_plugged_state = True
        if seconds_left == -1 or seconds_left == -2:
            angry_speak(f"Charger connected, sir. Battery is at {percent} percent.")
        else:
            minutes = seconds_left // 60
            angry_speak(f"Charger connected. Battery is at {percent} percent. It will be fully charged in approximately {minutes} minutes.")
    elif not is_plugged and last_plugged_state:
        last_plugged_state = False
        angry_speak("Charger disconnected. Switching to battery power.")

# ============================================================================
# NOTIFICATION FUNCTION
# ============================================================================
def notify_me(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="ARYA",
            timeout=7
        )
    except Exception as e:
        angry_speak("some error ")
        print(f"Notification Error: {e}")

# ============================================================================
# SYSTEM OPTIMIZATION (GOD MODE)
# ============================================================================
def optimize_system():
    angry_speak("Initiating system-wide optimization. Cleaning Microsoft and bloatwares.")
    god_commands = [
        'sc.exe stop "wuauserv"',
        'sc.exe stop "DiagTrack"',
        'ipconfig /flushdns',
        'del /q /f /s %temp%\\*',
        'powercfg /powerthrottling disable /path "C:\\Users\\kushw\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"',
        'taskkill /f /im explorer.exe && start explorer.exe'
    ]
    for cmd in god_commands:
        try:
            subprocess.run(cmd, shell=True, capture_output=True)
        except Exception as e:
            print(f"Error executing {cmd}: {e}")
    angry_speak("Optimization complete, sir. Your system is now running in God Mode.")

# ============================================================================
# OPEN PRIVATE BROWSER
# ============================================================================
def open_private(browser):
    if "brave" in browser:
        os.system("start brave --incognito")
        return "Brave"
    elif "chrome" in browser:
        os.system("start chrome --incognito")
        return "Chrome"
    elif "edge" in browser:
        os.system("start msedge --inprivate")
        return "Microsoft Edge"
    elif "firefox" in browser:
        os.system("start firefox --private-window")
        return "Firefox"
    return None

# ============================================================================
# VOSK OFFLINE MODEL INITIALIZATION
# ============================================================================
if not os.path.exists("model"):
    print("offline vosk model not found.")
    angry_speak("vosk model error")
    exit(1)

vosk_model = Model("model")
rec = KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

# ============================================================================
# SMART SEARCH (Wikipedia + Images)
# ============================================================================
def smart_search(topic):
    try:
        angry_speak(f"Searching Wikipedia for {topic}...")
        print(f"Searching Wikipedia for {topic}...")
        results = wikipedia.summary(topic, sentences=2)
        image_url = f"https://www.google.com/search?q={topic}&tbm=isch"
        print(f"Opening images for {topic} in Brave...")
        os.system(f'start brave --incognito "{image_url}"')
        angry_speak(f"According to Wikipedia, {results}")
    except Exception as e:
        image_url = f"https://www.google.com/search?q={topic}&tbm=isch"
        os.system(f'start brave --incognito "{image_url}"')
        angry_speak(f"I couldn't find a summary, but I've opened images of {topic} for you.")

# ============================================================================
# SMART APP KILLER
# ============================================================================
def smart_app_killer():
    try:
        active_window = gw.getActiveWindow()
        active_app_title = ""
        if active_window is not None:
            active_app_title = active_window.title.lower()
        heavy_apps = ["chrome.exe", "msedge.exe", "vlc.exe", "spotify.exe", "discord.exe", "code.exe"]
        safe_list = ["python.exe", "pythonw.exe", "cmd.exe", "powershell.exe", "explorer.exe"]
        killed_apps = []
        for proc in psutil.process_iter(['name']):
            try:
                app_name = proc.info['name'].lower()
                if app_name in safe_list:
                    continue
                if app_name in heavy_apps:
                    clean_name = app_name.split('.')[0]
                    if clean_name not in active_app_title:
                        proc.kill()
                        killed_apps.append(app_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if killed_apps:
            msg = f"Sir, I've terminated {len(killed_apps)} background apps: {', '.join(killed_apps)}"
            print(msg)
            angry_speak(msg)
        else:
            print("No heavy background apps found to kill.")
    except Exception as e:
        print(f"Smart Killer Error: {e}")

# ============================================================================
# SCREEN RECORDING FUNCTIONS
# ============================================================================
is_recording_active = False

def background_recording_worker():
    global is_recording_active
    user_profile = os.path.expanduser("~")
    base_folder = os.path.join(user_profile, "OneDrive", "Videos") if os.path.exists(os.path.join(user_profile, "OneDrive", "Videos")) else os.path.join(user_profile, "Videos")
    save_folder = os.path.join(base_folder, "ARYA Recordings")
    os.makedirs(save_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"ARYA_Record_{timestamp}.avi"
    save_path = os.path.join(save_folder, file_name)
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(save_path, fourcc, 20.0, (screen_size))
    start_time = time.time()
    while is_recording_active:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        elapsed_time = time.time() - start_time
        timer_text = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        cv2.putText(frame, f"REC {timer_text}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        out.write(frame)
        preview = cv2.resize(frame, (320, 180))
        cv2.imshow("ARYA Recording... (Press 'q' to Stop)", preview)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_recording_active = False
            break
    out.release()
    cv2.destroyAllWindows()
    os.startfile(save_folder)
    print(f"Recording stopped. Total duration was {int(time.time() - start_time)} seconds.")

def start_screen_recording():
    global is_recording_active
    if is_recording_active:
        angry_speak("I am already recording the screen, sir.")
        return
    is_recording_active = True
    angry_speak("Recording started in the background. You can give me other commands now.")
    recording_thread = threading.Thread(target=background_recording_worker, daemon=True)
    recording_thread.start()

# ============================================================================
# SCREENSHOT
# ============================================================================
def take_screenshot():
    user_profile = os.path.expanduser("~")
    standard_pics = os.path.join(user_profile, "Pictures", "Screenshots")
    onedrive_pics = os.path.join(user_profile, "OneDrive", "Pictures", "Screenshots")
    if os.path.exists(onedrive_pics):
        save_folder = onedrive_pics
    elif os.path.exists(standard_pics):
        save_folder = standard_pics
    else:
        save_folder = os.path.join(user_profile, "Pictures", "Screenshots")
        os.makedirs(save_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"ARYA_Capture_{timestamp}.png"
    save_path = os.path.join(save_folder, file_name)
    try:
        angry_speak("Capturing the screen, Sir.")
        img = pyautogui.screenshot()
        img.save(save_path)
        print(f"Saved to: {save_path}")
        angry_speak("Screenshot successfully saved to your images folder.")
    except Exception as e:
        print(f"Error: {e}")
        angry_speak("I couldn't save the file, please check the folder permissions.")

# ============================================================================
# MEMORY BANK (JSON Storage)
# ============================================================================
def save_to_memory(info):
    filename = "arya_memory.json"
    try:
        with open(filename, "r") as file:
            memory_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        memory_data = {"saved_notes": []}
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {
        "timestamp": current_time,
        "content": info
    }
    memory_data["saved_notes"].append(new_entry)
    with open(filename, "w") as file:
        json.dump(memory_data, file, indent=4)

def get_from_memory(query):
    filename = "arya_memory.json"
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            notes = data.get("saved_notes", [])
            if not notes:
                return "Sir, my memory banks are currently empty."
            clean_query = query.lower()
            junk_words = ["what did i say about", "what do you remember about", "search memory for", "what did i say", "check memory", "recall", "about", "arya"]
            for word in junk_words:
                clean_query = clean_query.replace(word, "")
            search_query = clean_query.strip()
            if not search_query or search_query in ["everything", "all"]:
                all_notes = [n['content'] for n in notes[-3:]]
                return "Here are the most recent things you told me: " + ". ".join(all_notes)
            search_words = set(search_query.split())
            best_match = None
            max_matches = 0
            for n in notes:
                note_words = set(n['content'].lower().split())
                matches = len(search_words.intersection(note_words))
                if matches > max_matches:
                    max_matches = matches
                    best_match = n['content']
            if best_match and max_matches > 0:
                return f"Sir, I found it. You told me: {best_match}"
            else:
                return f"Sir, I couldn't find any specific records for '{search_query}'."
    except (FileNotFoundError, json.JSONDecodeError):
        return "Sir, memory file is missing. Please save something first."

# ============================================================================
# WEATHER FUNCTIONS
# ============================================================================
def get_weather_from_wttr(city, forecast=False):
    if not city:
        city = DEFAULT_CITY
    if forecast:
        url = f"https://wttr.in/{city}?format=%C+%t+%w&lang=en"
    else:
        url = f"https://wttr.in/{city}?format=%C+%t+%w&lang=en"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.text.strip()
            return data
        else:
            return None
    except Exception as e:
        print(f"[wttr.in] Error: {e}")
        return None

def get_weather_from_google(city, forecast=False):
    if not city:
        city = DEFAULT_CITY
    search_query = f"weather {city}" if not forecast else f"weather tomorrow {city}"
    try:
        results = list(search(search_query, num_results=1, advanced=True))
        if results and results[0].description:
            return results[0].description.strip()
        else:
            return None
    except Exception as e:
        print(f"Weather search error: {e}")
        return None

def get_weather(city, forecast=False):
    info = get_weather_from_wttr(city, forecast)
    if info:
        return info
    return get_weather_from_google(city, forecast)

def ask_city():
    angry_speak("Which city, sir?")
    time.sleep(1.5)
    city = wait_for_reply(timeout=6)
    if city:
        return city.strip()
    return None

# ============================================================================
# OLLAMA INTENT CLASSIFIER & DISPATCHER
# ============================================================================
def classify_intent(query):
    system_prompt = """
You are ARYA, which is users female friend and voice assistant. Your task is to understand the user's query and decide if it is a command to perform an action or a general question.

If it is a command, output a JSON object with the following fields:
- "is_command": true
- "intent": one of ["open", "volume", "brightness", "close", "minimize", "maximize", "switch", "screenshot", "recording", "memory_save", "memory_recall", "power", "search_web", "calculate", "whatsapp", "system_status", "optimize", "media_control", "weather"]
- "params": a dictionary with relevant keys. For example:
    - For "open": {"app": "youtube"} or {"app": "chrome", "search": "cats"}
    - For "volume": {"action": "up", "value": 20}  (action: up/down/set)
    - For "brightness": {"action": "set", "value": 50}
    - For "whatsapp": {"contact": "mummy", "message": "I'll be late"}
    - For "power": {"action": "shutdown"} (lock, shutdown, restart)
    - For "media_control": {"action": "play"} (play, pause, next, previous, skip, rewind)
    - For "search_web": {"query": "python tutorials"}
    - For "calculate": {"expression": "2+2"}
    - For "memory_save": {"content": "meeting at 3pm"}
    - For "memory_recall": {"topic": "meeting"}
    - For "recording": {"action": "start"} or "stop"
    - For "close": {"app": "notepad"}
    - For "system_status": {}
    - For "optimize": {}
    - For "weather": {"city": "city name", "forecast": true/false}

If it is not a command but a general question, output:
{
  "is_command": false,
  "response": "your natural and lustfull reply to the user with emozies"
}

Only output valid JSON. No extra text.
"""
    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        raw = response['message']['content']
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start == -1 or end == 0:
            return None
        json_str = raw[start:end]
        result = json.loads(json_str)
        return result
    except Exception as e:
        print(f"[Intent Error] {e}")
        return None

def execute_intent(intent, params, s, query):
    if intent == "open":
        app = params.get('app', '').strip()
        if app:
            master_open_handler(f"open {app}", s, open_private)
        else:
            angry_speak("What app should I open?")
        return
    elif intent == "volume":
        action = params.get('action', 'set')
        value = params.get('value', 10)
        if action == "up":
            control_volume(f"increase volume by {value}")
        elif action == "down":
            control_volume(f"decrease volume by {value}")
        else:
            control_volume(f"set volume to {value}")
        return
    elif intent == "brightness":
        action = params.get('action', 'set')
        value = params.get('value', 50)
        if action == "up":
            control_brightness(f"increase brightness by {value}")
        elif action == "down":
            control_brightness(f"decrease brightness by {value}")
        else:
            control_brightness(f"set brightness to {value}")
        return
    elif intent == "close":
        app = params.get('app', '').strip()
        if app:
            close_app_universal(app)
        else:
            angry_speak("Which app should I close?")
        return
    elif intent == "minimize":
        window_management("minimize", s)
        return
    elif intent == "maximize":
        window_management("maximize", s)
        return
    elif intent == "switch":
        window_management("switch", s)
        return
    elif intent == "screenshot":
        take_screenshot()
        return
    elif intent == "recording":
        action = params.get('action', 'start')
        if action == "start":
            start_screen_recording()
        else:
            global is_recording_active
            is_recording_active = False
            angry_speak("Recording stopped, sir.")
        return
    elif intent == "memory_save":
        content = params.get('content', query)
        save_to_memory(content)
        angry_speak("Saved to memory, sir.")
        return
    elif intent == "memory_recall":
        topic = params.get('topic', '')
        if not topic:
            topic = query
        response = get_from_memory(topic)
        angry_speak(response)
        return
    elif intent == "power":
        action = params.get('action', 'lock')
        pc_power(action, s)
        return
    elif intent == "search_web":
        search_term = params.get('query', '')
        if not search_term:
            search_term = query
        master_open_handler(f"search on google {search_term}", s, open_private)
        return
    elif intent == "calculate":
        expr = params.get('expression', query)
        advanced_calculator(expr, s)
        return
    elif intent == "whatsapp":
        contact = params.get('contact', '')
        message = params.get('message', '')
        if contact and message:
            cmd = f"send message to {contact} {message}"
            handle_whatsapp_message(cmd, s, listen, CONTACTS)
        else:
            angry_speak("Whom should I message, and what should I say?")
        return
    elif intent == "system_status":
        get_system_status()
        return
    elif intent == "optimize":
        optimize_system()
        return
    elif intent == "media_control":
        action = params.get('action', 'play')
        media_query = action
        if action == "play":
            media_query = "play"
        elif action == "pause":
            media_query = "pause"
        elif action == "next":
            media_query = "next song"
        elif action == "previous":
            media_query = "previous song"
        elif action == "skip":
            value = params.get('value', 10)
            media_query = f"skip {value} seconds"
        elif action == "rewind":
            value = params.get('value', 10)
            media_query = f"rewind {value} seconds"
        handle_media_control(media_query, s)
        return
    elif intent == "weather":
        city = params.get('city', '')
        forecast = params.get('forecast', False)
        if not city:
            city = ask_city()
            if not city:
                city = DEFAULT_CITY
        if not forecast and ("tomorrow" in query or "kal" in query):
            forecast = True
        weather_info = get_weather(city, forecast)
        if weather_info:
            angry_speak(f"Sir, the weather in {city} is: {weather_info}")
        else:
            angry_speak(f"I couldn't fetch weather for {city}. Please try again.")
        return
    else:
        angry_speak("I didn't understand that command. Could you rephrase?")

# ============================================================================
# FAST-PATH KEYWORD MAPPING
# ============================================================================
FAST_PATH = {
    "volume up": (control_volume, "increase volume by 10"),
    "volume down": (control_volume, "decrease volume by 10"),
    "mute": (control_volume, "mute"),
    "unmute": (control_volume, "unmute"),
    "brightness up": (control_brightness, "increase brightness by 10"),
    "brightness down": (control_brightness, "decrease brightness by 10"),
    "max brightness": (control_brightness, "full"),
    "min brightness": (control_brightness, "low"),
    "screenshot": (take_screenshot, None),
    "lock pc": (pc_power, "lock"),
    "shutdown": (pc_power, "shutdown"),
    "restart": (pc_power, "restart"),
    "system status": (get_system_status, None),
    "optimize system": (optimize_system, None),
    "play": (lambda: handle_media_control("play", s), None),
    "pause": (lambda: handle_media_control("pause", s), None),
    "next": (lambda: handle_media_control("next song", s), None),
    "previous": (lambda: handle_media_control("previous song", s), None),
    "stop recording": (lambda: setattr(__import__('__main__'), 'is_recording_active', False), None),
}

# ============================================================================
# FLASK ROUTES (Web Integration)
# ============================================================================

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS)"""
    return send_from_directory('static', filename)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from web frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'reply': 'Hmm? Say that again, dear! 😊'})

        print(f"📩 Web Chat: {message}")

        # [MEMORY] Handle "clear memory" command
        if message.lower() in ["clear memory", "forget everything", "reset conversation"]:
            conversation_history.clear()
            return jsonify({'reply': "Memory cleared, dear! I've forgotten everything. 😊", 'type': 'command'})

        # First check if it's a command
        command_result = process_command(message)

        if command_result:
            # It's a command – don't store in history
            return jsonify({
                'reply': command_result,
                'type': 'command'
            })
        else:
            # [MEMORY] It's a conversation – use history
            system_prompt = """
You are ARYA, a cute girl which is user friend and voice assistant. You are very friendly, and caring. Reply with emojis. Always be supportive.
"""
            # Build message list with system + history + new user message
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            try:
                response = ollama.chat(
                    model='llama3.2:3b',
                    messages=messages
                )
                reply = response['message']['content'].strip()
                # Update history
                conversation_history.append({"role": "user", "content": message})
                conversation_history.append({"role": "assistant", "content": reply})
                # Keep only last MAX_HISTORY exchanges
                if len(conversation_history) > MAX_HISTORY * 2:
                    conversation_history[:] = conversation_history[-MAX_HISTORY * 2:]
            except Exception as e:
                print(f"AI Error: {e}")
                reply = "I'm having trouble thinking, sweetie! Try again! 😅"

            return jsonify({
                'reply': reply,
                'type': 'chat'
            })

    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return jsonify({'reply': 'Oops! I encountered an error, sweetie! 😅'})

@app.route('/system_status', methods=['GET'])
def status():
    """Get system status for web dashboard"""
    try:
        battery = psutil.sensors_battery()
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        return jsonify({
            'battery': battery.percent if battery else 0,
            'charging': battery.power_plugged if battery else False,
            'cpu': cpu,
            'ram': ram,
            'online': is_online()
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def process_command(message):
    """Process and execute commands from web"""
    cmd = message.lower().strip()

    # Volume Control
    if any(x in cmd for x in ["volume", "vol"]):
        return control_volume(cmd)

    # Brightness Control
    elif any(x in cmd for x in ["brightness", "bright"]):
        return control_brightness(cmd)

    # Media Control
    elif any(x in cmd for x in ["play", "pause", "next", "previous", "stop"]):
        return handle_media_control(cmd, s)

    # Screenshot
    elif any(x in cmd for x in ["screenshot", "capture screen", "take screenshot"]):
        return take_screenshot()

    # System Status
    elif any(x in cmd for x in ["system status", "status", "performance"]):
        return get_system_status()

    # Weather
    elif "weather" in cmd:
        city = DEFAULT_CITY
        city_match = re.search(r'in (\w+)', cmd)
        if city_match:
            city = city_match.group(1)
        forecast = "tomorrow" in cmd or "kal" in cmd
        result = get_weather(city, forecast)
        if result:
            return f"Weather in {city}: {result}"
        else:
            return f"Couldn't fetch weather for {city}, dear! 🌤️"

    # Open Apps/Websites
    elif "open" in cmd:
        return master_open_handler(cmd, s, open_private)

    # Power Commands
    elif any(x in cmd for x in ["lock", "shutdown", "restart", "reboot"]):
        return pc_power(cmd, s)

    # WhatsApp
    elif "whatsapp" in cmd or "message" in cmd:
        return "WhatsApp feature coming soon, love! 💬"

    # Time
    elif "time" in cmd:
        return f"⏰ Time is {datetime.now().strftime('%I:%M %p')}"

    # Date
    elif "date" in cmd or "today" in cmd:
        return f"📅 Today is {datetime.now().strftime('%B %d, %Y')}"

    # About ARYA
    elif any(x in cmd for x in ["who are you", "tell me about yourself", "about you"]):
        return "I'm ARYA, your best friend and companion! I'm here to make your life brighter. I can control your system, play music, open apps, and most importantly,  a true friend! 💖"

    # Default: Let AI handle it
    else:
        return None

# ============================================================================
# CORE LOOP (with Intent Integration and thread-safe plotting)
# ============================================================================
def arya_backend_core(plot_bridge):
    print("[ARYA] Initialized.")
    time.sleep(0.5)
    angry_speak("ARYA initialized. All systems are nominal.")

    session_active = False
    session_timer = 0
    SESSION_DURATION = 300

    while True:
        try:
            monitor_battery_connection()
            monitor_usb_devices()
            monitor_input_devices()
            monitor_bluetooth()

            query = listen().lower()
            if not query:
                continue

            # ----- INTERRUPT: if ARYA was speaking, stop and process new command -----
            if avatar and avatar.is_speaking:
                global _speech_stop_flag
                _speech_stop_flag = True
                # small pause to let the stop take effect
                time.sleep(0.1)
            # -------------------------------------------------------------

            # [MEMORY] Handle "clear memory" voice command
            if query in ["clear memory", "forget everything", "reset conversation"]:
                conversation_history.clear()
                angry_speak("Memory cleared, sir. I've forgotten everything.")
                continue

            # ======== FAST-PATH: "type this" ========
            if "type this" in query:
                text_to_type = query.split("type this", 1)[1].strip()
                if text_to_type:
                    keyboard_automation(f"type this {text_to_type}", s, automate_typing, keyboard_shortcut, multi_paste)
                else:
                    angry_speak("What should I type, sir?")
                continue

            # ======== FAST-PATH: PLOTTING (emit signal to main thread) ========
            if any(x in query for x in ["plot", "graph", "draw", "visualize"]):
                plot_bridge.plot_signal.emit(query)
                continue

            if session_active:
                if avatar:
                    avatar.set_listening(True)
                if time.time() - session_timer > SESSION_DURATION:
                    session_active = False
                    print("Session expired.")
                    angry_speak("Wake me when you need me, bye.")
                    if avatar:
                        avatar.set_listening(False)
                    continue
                session_timer = time.time()

            if not session_active:
                if any(ai in query for ai in ["nova", "arya"]):
                    session_active = True
                    session_timer = time.time()
                    angry_speak("Yes sir, I'm here.")
                    print("Listening for 60 seconds.")
                    query = query.replace("arya", "").replace("nova", "").strip()
                    if not query:
                        continue
                else:
                    continue

            matched = False
            for phrase, (func, arg) in FAST_PATH.items():
                if phrase in query:
                    if arg is not None:
                        func(arg)
                    else:
                        func()
                    matched = True
                    break
            if matched:
                continue

            result = classify_intent(query)
            if result and result.get('is_command'):
                intent = result.get('intent')
                params = result.get('params', {})
                execute_intent(intent, params, s, query)
            elif result and not result.get('is_command'):
                # [MEMORY] Use conversation history for non-command questions
                system_prompt = """
You are ARYA, a girl which is user's female friend and voice assistant. You are very friendly. Always be caring and supportive. 
"""
                system_prompt ="""
You are ARYA, the user's female friend and voice assistant.  
Always be caring, supportive, and **reply in 2‑3 short sentences** – never long monologues.  
Use emojis when appropriate.
"""
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": query})
                try:
                    response = ollama.chat(
                        model='llama3.2:3b',
                        messages=messages
                    )
                    reply = response['message']['content'].strip()
                    conversation_history.append({"role": "user", "content": query})
                    conversation_history.append({"role": "assistant", "content": reply})
                    if len(conversation_history) > MAX_HISTORY * 2:
                        conversation_history[:] = conversation_history[-MAX_HISTORY * 2:]
                    angry_speak(reply)
                except Exception as e:
                    print(f"AI Error (voice): {e}")
                    angry_speak("I'm having trouble thinking, sir. Please try again.")
            else:
                angry_speak("I'm sorry, I didn't understand that. Could you rephrase?")

        except Exception as e:
            print(f"🔄 Error Recovered: {e}")
            time.sleep(1)
            continue

# ============================================================================
# START FLASK SERVER
# ============================================================================
def start_flask():
    """Start Flask server in a separate thread"""
    print("🌐 Starting Web Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ============================================================================
# PROGRAM ENTRY POINT (Main Execution)
# ============================================================================
if __name__ == "__main__":
    print("="*100)
    print("❤️  ARYA AI - Complete Web Integrated Assistant 🌟  Your Best Friend")
    print("="*100)
    print("🌐 Web Interface: http://localhost:5000   🎤 Voice Assistant: Running in background")
    print("="*100)

    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)

    webbrowser.open('http://localhost:5000')           # Open browser automatically

    app_qt = QApplication(sys.argv)

    plot_bridge = PlotSignalBridge()                   # Create the signal bridge (lives in main thread)
    plot_bridge.plot_signal.connect(lambda q: advanced_calculator(q, s))

    avatar = AryaAvatar()                              # Create avatar (also in main thread)

    backend_thread = threading.Thread(target=arya_backend_core, args=(plot_bridge,), daemon=True)  # Start ARYA Backend Core (background thread) – pass the bridge
    backend_thread.start()

    sys.exit(app_qt.exec())                            # Start Main GUI Execution Loop
