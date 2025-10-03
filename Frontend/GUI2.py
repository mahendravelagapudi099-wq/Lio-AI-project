from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from dotenv import dotenv_values
import sys
import os
import math
import random
from datetime import datetime
import json

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "JARVIS")
old_chat_message = ""

# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# Utility Functions
def ensure_directories():
    os.makedirs(TempDirPath, exist_ok=True)
    os.makedirs(GraphicsDirPath, exist_ok=True)

def SetMicrophoneStatus(Command):
    try:
        with open(rf'{TempDirPath}\Mic.data', 'w', encoding='utf-8') as file:
            file.write(Command)
    except: pass

def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', 'r', encoding='utf-8') as file:
            return file.read().strip()
    except: return "False"

def SetAssistantStatus(Status):
    try:
        with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
            file.write(Status)
    except: pass

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            return file.read()
    except: return "Ready"

def ShowTextToScreen(Text):
    try:
        with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
            file.write(Text)
    except: pass

def SaveConversationHistory(history):
    try:
        with open(rf'{TempDirPath}\history.json', 'w', encoding='utf-8') as file:
            json.dump(history, file, indent=2)
    except: pass

def LoadConversationHistory():
    try:
        with open(rf'{TempDirPath}\history.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except: return []


# ==================== HOLOGRAPHIC AI ORB ====================
class HolographicOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 350)
        
        self._rotation = 0
        self._pulse = 0
        self.state = "idle"
        
        self.particles = []
        for _ in range(40):
            self.particles.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(60, 140),
                'speed': random.uniform(0.3, 1.5),
                'size': random.uniform(2, 5),
                'opacity': random.uniform(100, 255)
            })
        
        self.rotation_anim = QPropertyAnimation(self, b"rotation")
        self.rotation_anim.setDuration(4000)
        self.rotation_anim.setStartValue(0)
        self.rotation_anim.setEndValue(360)
        self.rotation_anim.setLoopCount(-1)
        self.rotation_anim.start()
        
        self.pulse_anim = QPropertyAnimation(self, b"pulse")
        self.pulse_anim.setDuration(2000)
        self.pulse_anim.setStartValue(0)
        self.pulse_anim.setEndValue(15)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.start()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateParticles)
        self.timer.start(30)
        
    @pyqtProperty(float)
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.update()
    
    @pyqtProperty(float)
    def pulse(self):
        return self._pulse
    
    @pulse.setter
    def pulse(self, value):
        self._pulse = value
        self.update()
    
    def setState(self, state):
        self.state = state
        if state == "listening" or state == "speaking":
            self.rotation_anim.setDuration(1500)
        else:
            self.rotation_anim.setDuration(4000)
        self.update()
    
    def updateParticles(self):
        for p in self.particles:
            p['angle'] += p['speed']
            if p['angle'] >= 360:
                p['angle'] -= 360
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        
        if self.state == "listening":
            primary = QColor(0, 217, 255)
            secondary = QColor(168, 85, 247)
        elif self.state == "thinking":
            primary = QColor(168, 85, 247)
            secondary = QColor(251, 191, 36)
        elif self.state == "speaking":
            primary = QColor(16, 185, 129)
            secondary = QColor(0, 217, 255)
        else:
            primary = QColor(0, 217, 255)
            secondary = QColor(100, 116, 139)
        
        for i in range(3):
            radius = 130 + i * 25 + self._pulse
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(primary.red(), primary.green(), primary.blue(), 0))
            gradient.setColorAt(0.7, QColor(primary.red(), primary.green(), primary.blue(), 20 - i * 5))
            gradient.setColorAt(1, QColor(secondary.red(), secondary.green(), secondary.blue(), 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(primary, 1, Qt.SolidLine))
            painter.drawEllipse(center, radius, radius)
        
        hexagon_pts = []
        for i in range(6):
            angle = math.radians(self._rotation + i * 60)
            x = center.x() + 90 * math.cos(angle)
            y = center.y() + 90 * math.sin(angle)
            hexagon_pts.append(QPointF(x, y))
        
        painter.setPen(QPen(secondary, 2, Qt.SolidLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(QPolygonF(hexagon_pts))
        
        triangle_pts = []
        for i in range(3):
            angle = math.radians(-self._rotation * 1.8 + i * 120)
            x = center.x() + 55 * math.cos(angle)
            y = center.y() + 55 * math.sin(angle)
            triangle_pts.append(QPointF(x, y))
        
        painter.setPen(QPen(primary, 2, Qt.SolidLine))
        painter.drawPolygon(QPolygonF(triangle_pts))
        
        for p in self.particles:
            angle = math.radians(p['angle'])
            x = center.x() + p['distance'] * math.cos(angle)
            y = center.y() + p['distance'] * math.sin(angle)
            
            gradient = QRadialGradient(QPointF(x, y), p['size'])
            gradient.setColorAt(0, QColor(primary.red(), primary.green(), primary.blue(), int(p['opacity'])))
            gradient.setColorAt(1, QColor(primary.red(), primary.green(), primary.blue(), 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), p['size'], p['size'])
        
        core_size = 35 + self._pulse / 2
        core_gradient = QRadialGradient(center, core_size)
        
        if self.state == "listening":
            core_gradient.setColorAt(0, QColor(255, 255, 255, 220))
            core_gradient.setColorAt(0.4, primary)
            core_gradient.setColorAt(1, QColor(primary.red(), primary.green(), primary.blue(), 0))
        else:
            core_gradient.setColorAt(0, primary)
            core_gradient.setColorAt(0.6, QColor(primary.red(), primary.green(), primary.blue(), 150))
            core_gradient.setColorAt(1, QColor(primary.red(), primary.green(), primary.blue(), 0))
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, core_size, core_size)


# ==================== VOICE WAVEFORM BUTTON ====================
class VoiceWaveformButton(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self.is_active = False
        self._wave_offset = 0
        self.bars = [random.uniform(0.3, 0.8) for _ in range(32)]
        
        self.wave_anim = QPropertyAnimation(self, b"wave_offset")
        self.wave_anim.setDuration(1200)
        self.wave_anim.setStartValue(0)
        self.wave_anim.setEndValue(360)
        self.wave_anim.setLoopCount(-1)
        
        self.bar_timer = QTimer(self)
        self.bar_timer.timeout.connect(self.updateBars)
        
        self.setCursor(Qt.PointingHandCursor)
    
    @pyqtProperty(float)
    def wave_offset(self):
        return self._wave_offset
    
    @wave_offset.setter
    def wave_offset(self, value):
        self._wave_offset = value
        self.update()
    
    def updateBars(self):
        for i in range(len(self.bars)):
            self.bars[i] = random.uniform(0.2, 1.0)
        self.update()
    
    def mousePressEvent(self, event):
        self.is_active = not self.is_active
        if self.is_active:
            self.wave_anim.start()
            self.bar_timer.start(80)
        else:
            self.wave_anim.stop()
            self.bar_timer.stop()
        self.clicked.emit()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        
        if self.is_active:
            for ring in range(3):
                radius = 70 + ring * 12
                path = QPainterPath()
                points = []
                
                for angle in range(0, 360, 6):
                    rad = math.radians(angle + self._wave_offset + ring * 40)
                    wave = math.sin(rad * 4) * 4
                    r = radius + wave
                    x = center.x() + r * math.cos(rad)
                    y = center.y() + r * math.sin(rad)
                    points.append(QPointF(x, y))
                
                if points:
                    path.moveTo(points[0])
                    for p in points[1:]:
                        path.lineTo(p)
                    path.closeSubpath()
                
                painter.setPen(QPen(QColor(0, 217, 255, 180 - ring * 40), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
            
            bar_width = 3
            total_width = len(self.bars) * (bar_width + 2)
            start_x = center.x() - total_width / 2
            
            for i, height in enumerate(self.bars):
                x = start_x + i * (bar_width + 2)
                bar_height = height * 30
                y = center.y() - bar_height / 2
                
                gradient = QLinearGradient(x, y, x, y + bar_height)
                gradient.setColorAt(0, QColor(0, 217, 255))
                gradient.setColorAt(1, QColor(168, 85, 247))
                
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(QRectF(x, y, bar_width, bar_height), 1, 1)
        else:
            gradient = QRadialGradient(center, 55)
            gradient.setColorAt(0, QColor(30, 41, 59, 220))
            gradient.setColorAt(1, QColor(15, 23, 42, 180))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(100, 116, 139, 200), 2))
            painter.drawEllipse(center, 55, 55)
            
            painter.setPen(QPen(QColor(100, 116, 139), 3))
            painter.drawEllipse(QRectF(center.x() - 12, center.y() - 22, 24, 28))
            painter.drawLine(QPointF(center.x(), center.y() + 6), QPointF(center.x(), center.y() + 20))
            painter.drawLine(QPointF(center.x() - 12, center.y() + 20), QPointF(center.x() + 12, center.y() + 20))


# ==================== CHAT BUBBLE ====================
class ChatBubble(QFrame):
    def __init__(self, message, is_user=False, timestamp=None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.message = message
        self.timestamp = timestamp or datetime.now().strftime("%I:%M %p")
        
        self.setFrameStyle(QFrame.NoFrame)
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        msg_frame = QFrame()
        msg_layout = QVBoxLayout(msg_frame)
        msg_layout.setSpacing(5)
        msg_layout.setContentsMargins(18, 12, 18, 12)
        
        msg_label = QLabel(self.message)
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg_label.setFont(QFont("Segoe UI", 11))
        msg_layout.addWidget(msg_label)
        
        time_label = QLabel(self.timestamp)
        time_label.setFont(QFont("Segoe UI", 8))
        time_label.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        
        if self.is_user:
            msg_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(168, 85, 247, 0.4), stop:1 rgba(139, 92, 246, 0.4));
                    border: 1px solid rgba(168, 85, 247, 0.6);
                    border-radius: 18px;
                    border-top-right-radius: 4px;
                }
            """)
            msg_label.setStyleSheet("color: #e0e7ff;")
            time_label.setAlignment(Qt.AlignRight)
            msg_layout.addWidget(time_label)
            layout.addStretch()
            layout.addWidget(msg_frame)
        else:
            msg_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 217, 255, 0.25), stop:1 rgba(14, 165, 233, 0.25));
                    border: 1px solid rgba(0, 217, 255, 0.5);
                    border-radius: 18px;
                    border-top-left-radius: 4px;
                }
            """)
            msg_label.setStyleSheet("color: #00d9ff;")
            time_label.setAlignment(Qt.AlignLeft)
            msg_layout.addWidget(time_label)
            layout.addWidget(msg_frame)
            layout.addStretch()
        
        self.setStyleSheet("background: transparent;")


# ==================== CIRCULAR GAUGE ====================
class CircularGauge(QWidget):
    def __init__(self, title="", max_value=100, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 140)
        self.title = title
        self.value = 0
        self.max_value = max_value
        
    def setValue(self, value):
        self.value = max(0, min(value, self.max_value))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRectF(20, 20, 100, 100)
        center = QPointF(70, 70)
        
        painter.setPen(QPen(QColor(30, 41, 59), 10))
        painter.drawArc(rect, 0, 360 * 16)
        
        percentage = (self.value / self.max_value) * 100
        angle = int((percentage / 100) * 360 * 16)
        
        if percentage < 50:
            color = QColor(16, 185, 129)
        elif percentage < 80:
            color = QColor(251, 191, 36)
        else:
            color = QColor(239, 68, 68)
        
        painter.setPen(QPen(color, 10, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 90 * 16, -angle)
        
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 20, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(percentage)}%")
        
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(100, 116, 139))
        painter.drawText(QRectF(0, 125, 140, 20), Qt.AlignCenter, self.title)


# ==================== QUICK ACTION CARD ====================
class QuickActionCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, icon_text, title, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.title = title
        self.setFixedSize(150, 150)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 48px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00d9ff; font-size: 13px; font-weight: bold; background: transparent;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        self.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 15px;
            }
            QFrame:hover {
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(0, 217, 255, 0.6);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 217, 255, 80))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ==================== HOME SCREEN ====================
class HomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(100)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)
        
        layout.addStretch()
        
        orb_container = QWidget()
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setContentsMargins(0, 0, 0, 0)
        
        self.orb = HolographicOrb()
        orb_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        layout.addWidget(orb_container)
        
        title = QLabel(Assistantname)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 56px;
                font-weight: bold;
                letter-spacing: 12px;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("◈ ADVANCED AI SYSTEM ◈")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 16px;
                letter-spacing: 4px;
                background: transparent;
            }
        """)
        layout.addWidget(subtitle)
        
        self.status_label = QLabel("● ONLINE")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 18px;
                padding: 12px 30px;
                background: rgba(16, 185, 129, 0.15);
                border: 2px solid rgba(16, 185, 129, 0.4);
                border-radius: 20px;
            }
        """)
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addWidget(status_container)
        
        self.voice_btn = VoiceWaveformButton()
        self.voice_btn.clicked.connect(self.toggleVoice)
        voice_container = QWidget()
        voice_layout = QHBoxLayout(voice_container)
        voice_layout.addStretch()
        voice_layout.addWidget(self.voice_btn)
        voice_layout.addStretch()
        layout.addWidget(voice_container)
        
        instruction = QLabel("◇ TAP TO ACTIVATE VOICE CONTROL ◇")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 12px;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        layout.addWidget(instruction)
        
        layout.addStretch()
        
        self.setStyleSheet("background: transparent;")
    
    def toggleVoice(self):
        if self.voice_btn.is_active:
            SetMicrophoneStatus("True")
            self.orb.setState("listening")
            self.status_label.setText("● LISTENING")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #00d9ff;
                    font-size: 18px;
                    padding: 12px 30px;
                    background: rgba(0, 217, 255, 0.15);
                    border: 2px solid rgba(0, 217, 255, 0.4);
                    border-radius: 20px;
                }
            """)
        else:
            SetMicrophoneStatus("False")
            self.orb.setState("idle")
            self.status_label.setText("● ONLINE")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #10b981;
                    font-size: 18px;
                    padding: 12px 30px;
                    background: rgba(16, 185, 129, 0.15);
                    border: 2px solid rgba(16, 185, 129, 0.4);
                    border-radius: 20px;
                }
            """)
    
    def updateStatus(self):
        status = GetAssistantStatus()
        if status and status != "Ready":
            self.status_label.setText(f"● {status.upper()}")
            self.orb.setState("thinking")


# ==================== CHAT SECTION ====================
class ChatSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.conversation_history = LoadConversationHistory()
        self.initUI()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.checkForNewMessages)
        self.update_timer.start(100)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        header = QHBoxLayout()
        title = QLabel(f"◈ {Assistantname} CHAT INTERFACE ◈")
        title.setStyleSheet("color: #00d9ff; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        header.addWidget(title)
        header.addStretch()
        
        export_btn = QPushButton("📥 Export")
        export_btn.setFixedHeight(35)
        export_btn.clicked.connect(self.exportChat)
        export_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 217, 255, 0.2);
                border: 1px solid rgba(0, 217, 255, 0.5);
                border-radius: 8px;
                color: #00d9ff;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 217, 255, 0.3);
            }
        """)
        export_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(export_btn)
        
        layout.addLayout(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(30, 41, 59, 0.5);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d9ff, stop:1 #a855f7);
                border-radius: 5px;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_widget)
        layout.addWidget(scroll)
        
        for msg in self.conversation_history:
            self.addMessage(msg.get('message', ''), msg.get('is_user', False), msg.get('timestamp', ''))
        
        self.setStyleSheet("background: transparent;")
    
    def addMessage(self, message, is_user=False, timestamp=None):
        bubble = ChatBubble(message, is_user, timestamp)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.messages.append({'message': message, 'is_user': is_user, 'timestamp': timestamp or datetime.now().strftime("%I:%M %p")})
        QTimer.singleShot(50, self.scrollToBottom)
    
    def scrollToBottom(self):
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    
    def checkForNewMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                msg = file.read()
            if msg and msg != old_chat_message:
                self.addMessage(msg, is_user=False)
                old_chat_message = msg
                SaveConversationHistory(self.messages)
        except:
            pass
    
    def exportChat(self):
        filename = f"jarvis_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"JARVIS Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for msg in self.messages:
                    sender = "You" if msg['is_user'] else "JARVIS"
                    f.write(f"[{msg['timestamp']}] {sender}: {msg['message']}\n\n")
            QMessageBox.information(self, "Export Successful", f"Chat exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))


# ==================== SYSTEM MONITOR ====================
class SystemMonitorSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.updateMetrics)
        self.update_timer.start(1000)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        title = QLabel("◈ SYSTEM MONITORING ◈")
        title.setStyleSheet("color: #00d9ff; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(title)
        
        gauges_layout = QGridLayout()
        gauges_layout.setSpacing(20)
        
        self.cpu_gauge = CircularGauge("CPU")
        self.ram_gauge = CircularGauge("RAM")
        self.disk_gauge = CircularGauge("DISK")
        self.network_gauge = CircularGauge("NETWORK")
        
        gauges_layout.addWidget(self.cpu_gauge, 0, 0)
        gauges_layout.addWidget(self.ram_gauge, 0, 1)
        gauges_layout.addWidget(self.disk_gauge, 1, 0)
        gauges_layout.addWidget(self.network_gauge, 1, 1)
        
        layout.addLayout(gauges_layout)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        self.info_label = QLabel("System Status: Online\nUptime: Calculating...\nTemperature: Normal")
        self.info_label.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.6;")
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        layout.addStretch()
        
        self.setStyleSheet("background: transparent;")
    
    def updateMetrics(self):
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_gauge.setValue(cpu_percent)
            
            ram = psutil.virtual_memory()
            self.ram_gauge.setValue(ram.percent)
            
            disk = psutil.disk_usage('/')
            self.disk_gauge.setValue(disk.percent)
            
            net_io = psutil.net_io_counters()
            if hasattr(self, '_last_net_sent'):
                bytes_diff = net_io.bytes_sent - self._last_net_sent
                network_percent = min((bytes_diff / 10485760) * 100, 100)
                self.network_gauge.setValue(network_percent)
            self._last_net_sent = net_io.bytes_sent
            
            cpu_temp = "N/A"
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temp = f"{temps['coretemp'][0].current}°C"
            except:
                pass
            
            uptime_seconds = int(psutil.boot_time())
            uptime = datetime.fromtimestamp(uptime_seconds)
            uptime_str = f"{(datetime.now() - uptime).days}d {(datetime.now() - uptime).seconds // 3600}h"
            
            self.info_label.setText(
                f"System Status: Online\n"
                f"Uptime: {uptime_str}\n"
                f"CPU Temp: {cpu_temp}\n"
                f"Processes: {len(psutil.pids())}"
            )
            
        except ImportError:
            self.cpu_gauge.setValue(random.randint(20, 80))
            self.ram_gauge.setValue(random.randint(30, 70))
            self.disk_gauge.setValue(random.randint(40, 60))
            self.network_gauge.setValue(random.randint(10, 50))
            self.info_label.setText(
                "System Status: Online (Simulated)\n"
                "Install psutil for real metrics:\n"
                "pip install psutil"
            )


# ==================== QUICK ACTIONS ====================
class QuickActionsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        title = QLabel("◈ QUICK ACTIONS ◈")
        title.setStyleSheet("color: #00d9ff; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        header.addWidget(title)
        header.addStretch()
        
        search = QLineEdit()
        search.setPlaceholderText("Search actions...")
        search.setFixedWidth(250)
        search.setFixedHeight(35)
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 8px;
                padding: 8px 15px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 217, 255, 0.6);
            }
        """)
        header.addWidget(search)
        
        layout.addLayout(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        actions_widget = QWidget()
        actions_layout = QGridLayout(actions_widget)
        actions_layout.setSpacing(15)
        
        actions = [
            ("🔍", "Web Search"), ("📁", "File Manager"), ("⚙️", "Settings"), ("📊", "Analytics"),
            ("🎵", "Media Player"), ("📧", "Email"), ("📅", "Calendar"), ("🔒", "Security"),
            ("🌐", "Browser"), ("💬", "Messages"), ("📸", "Camera"), ("🔔", "Notifications")
        ]
        
        row, col = 0, 0
        for icon, title in actions:
            card = QuickActionCard(icon, title)
            card.clicked.connect(lambda t=title: self.actionClicked(t))
            actions_layout.addWidget(card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        scroll.setWidget(actions_widget)
        layout.addWidget(scroll)
        
        self.setStyleSheet("background: transparent;")
    
    def actionClicked(self, title):
        QMessageBox.information(self, "Action", f"Activated: {title}")


# ==================== KNOWLEDGE BASE ====================
class KnowledgeBaseSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        header = QHBoxLayout()
        title = QLabel("◈ KNOWLEDGE BASE ◈")
        title.setStyleSheet("color: #00d9ff; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        header.addWidget(title)
        header.addStretch()
        
        filter_btn = QPushButton("🔽 Filter")
        filter_btn.setFixedHeight(35)
        filter_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 217, 255, 0.2);
                border: 1px solid rgba(0, 217, 255, 0.5);
                border-radius: 8px;
                color: #00d9ff;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(0, 217, 255, 0.3); }
        """)
        filter_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(filter_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setFixedHeight(35)
        clear_btn.clicked.connect(self.clearHistory)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                border-radius: 8px;
                color: #ef4444;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: rgba(239, 68, 68, 0.3); }
        """)
        clear_btn.setCursor(Qt.PointingHandCursor)
        header.addWidget(clear_btn)
        
        layout.addLayout(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: rgba(30, 41, 59, 0.5);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00d9ff, stop:1 #a855f7);
                border-radius: 5px;
            }
        """)
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setSpacing(10)
        
        history = LoadConversationHistory()
        for msg in history[-20:]:
            item = QFrame()
            item.setStyleSheet("""
                QFrame {
                    background: rgba(30, 41, 59, 0.4);
                    border: 1px solid rgba(0, 217, 255, 0.2);
                    border-radius: 10px;
                    padding: 12px;
                }
                QFrame:hover {
                    background: rgba(30, 41, 59, 0.6);
                    border: 1px solid rgba(0, 217, 255, 0.4);
                }
            """)
            item_layout = QVBoxLayout(item)
            
            sender = "You" if msg.get('is_user') else "JARVIS"
            label = QLabel(f"[{msg.get('timestamp', '')}] {sender}")
            label.setStyleSheet("color: #00d9ff; font-weight: bold; font-size: 11px;")
            item_layout.addWidget(label)
            
            content = QLabel(msg.get('message', '')[:100] + "..." if len(msg.get('message', '')) > 100 else msg.get('message', ''))
            content.setStyleSheet("color: #94a3b8; font-size: 10px;")
            content.setWordWrap(True)
            item_layout.addWidget(content)
            
            history_layout.addWidget(item)
        
        history_layout.addStretch()
        scroll.setWidget(history_widget)
        layout.addWidget(scroll)
        
        self.setStyleSheet("background: transparent;")
    
    def clearHistory(self):
        reply = QMessageBox.question(self, "Clear History", 
                                     "Are you sure you want to clear all conversation history?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            SaveConversationHistory([])
            QMessageBox.information(self, "Success", "History cleared successfully!")


# ==================== SETTINGS ====================
class SettingsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        title = QLabel("◈ SETTINGS & CUSTOMIZATION ◈")
        title.setStyleSheet("color: #00d9ff; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(15)
        
        theme_frame = self.createSettingSection("🎨 Appearance", [
            ("Theme", ["Cyber Blue", "Neon Purple", "Matrix Green", "Sunset Orange"]),
            ("Font Size", ["Small", "Medium", "Large"]),
        ])
        settings_layout.addWidget(theme_frame)
        
        voice_frame = self.createSettingSection("🎤 Voice Settings", [
            ("Language", ["English (US)", "English (UK)", "Spanish", "French"]),
            ("Voice Speed", ["0.5x", "1.0x", "1.5x", "2.0x"]),
        ])
        settings_layout.addWidget(voice_frame)
        
        behavior_frame = self.createSettingSection("🧠 Behavior", [
            ("Formality", ["Casual", "Professional", "Technical"]),
            ("Response Length", ["Concise", "Balanced", "Detailed"]),
        ])
        settings_layout.addWidget(behavior_frame)
        
        privacy_frame = QFrame()
        privacy_frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        privacy_layout = QVBoxLayout(privacy_frame)
        
        privacy_title = QLabel("🔒 Privacy & Data")
        privacy_title.setStyleSheet("color: #00d9ff; font-size: 16px; font-weight: bold;")
        privacy_layout.addWidget(privacy_title)
        
        save_history_check = QCheckBox("Save conversation history")
        save_history_check.setChecked(True)
        save_history_check.setStyleSheet("color: white; font-size: 12px;")
        privacy_layout.addWidget(save_history_check)
        
        analytics_check = QCheckBox("Enable usage analytics")
        analytics_check.setStyleSheet("color: white; font-size: 12px;")
        privacy_layout.addWidget(analytics_check)
        
        settings_layout.addWidget(privacy_frame)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setFixedHeight(45)
        save_btn.clicked.connect(self.saveSettings)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d9ff, stop:1 #a855f7);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a855f7, stop:1 #00d9ff);
            }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        settings_layout.addWidget(save_btn)
        
        settings_layout.addStretch()
        scroll.setWidget(settings_widget)
        layout.addWidget(scroll)
        
        self.setStyleSheet("background: transparent;")
    
    def createSettingSection(self, title, options):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00d9ff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        for label, values in options:
            row = QHBoxLayout()
            
            lbl = QLabel(label + ":")
            lbl.setStyleSheet("color: white; font-size: 12px;")
            lbl.setFixedWidth(120)
            row.addWidget(lbl)
            
            combo = QComboBox()
            combo.addItems(values)
            combo.setStyleSheet("""
                QComboBox {
                    background: rgba(15, 23, 42, 0.8);
                    border: 1px solid rgba(0, 217, 255, 0.3);
                    border-radius: 6px;
                    padding: 6px 10px;
                    color: white;
                    font-size: 11px;
                }
                QComboBox:hover { border: 1px solid rgba(0, 217, 255, 0.6); }
            """)
            row.addWidget(combo)
            
            layout.addLayout(row)
        
        return frame
    
    def saveSettings(self):
        QMessageBox.information(self, "Success", "Settings saved successfully!")


# ==================== SIDEBAR ====================
class Sidebar(QFrame):
    navigationChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(80)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(15)
        
        logo = QLabel("⚡")
        logo.setStyleSheet("font-size: 36px; color: #00d9ff;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        layout.addSpacing(20)
        
        nav_items = [
            ("🏠", "Home", 0), ("💬", "Chat", 1), ("📊", "Monitor", 2),
            ("⚡", "Actions", 3), ("📚", "Knowledge", 4), ("⚙️", "Settings", 5)
        ]
        
        for icon, tooltip, index in nav_items:
            btn = QPushButton(icon)
            btn.setFixedSize(50, 50)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, i=index: self.navigationChanged.emit(i))
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(30, 41, 59, 0.5);
                    border: 1px solid rgba(0, 217, 255, 0.3);
                    border-radius: 12px;
                    font-size: 24px;
                    color: #64748b;
                }
                QPushButton:hover {
                    background: rgba(0, 217, 255, 0.2);
                    border: 1px solid rgba(0, 217, 255, 0.6);
                    color: #00d9ff;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 17, 40, 0.95);
                border-right: 1px solid rgba(0, 217, 255, 0.2);
            }
        """)


# ==================== TOP BAR ====================
class TopBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.initUI()
        
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.updateTime)
        self.time_timer.start(1000)
        self.updateTime()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        brand = QLabel(f"◈ {Assistantname}")
        brand.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        layout.addWidget(brand)
        
        layout.addStretch()
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #64748b; font-size: 14px; background: transparent;")
        layout.addWidget(self.time_label)
        
        min_btn = QPushButton("─")
        min_btn.setFixedSize(35, 35)
        min_btn.clicked.connect(lambda: self.parent().parent().showMinimized())
        self.styleControlButton(min_btn, "#64748b")
        layout.addWidget(min_btn)
        
        max_btn = QPushButton("□")
        max_btn.setFixedSize(35, 35)
        max_btn.clicked.connect(self.toggleMaximize)
        self.styleControlButton(max_btn, "#64748b")
        layout.addWidget(max_btn)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(35, 35)
        close_btn.clicked.connect(lambda: self.parent().parent().close())
        self.styleControlButton(close_btn, "#ef4444")
        layout.addWidget(close_btn)
        
        self.setStyleSheet("""
            QFrame {
                background: rgba(10, 17, 40, 0.95);
                border-bottom: 1px solid rgba(0, 217, 255, 0.2);
            }
        """)
    
    def styleControlButton(self, btn, color):
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(100, 116, 139, 0.3);
                border-radius: 17px;
                color: {color};
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid {color};
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
    
    def toggleMaximize(self):
        window = self.parent().parent()
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()
    
    def updateTime(self):
        current_time = datetime.now().strftime("%I:%M %p | %A, %B %d")
        self.time_label.setText(current_time)


# ==================== MAIN WINDOW ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()
    
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        top_bar = TopBar(self)
        main_layout.addWidget(top_bar)
        
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        sidebar = Sidebar()
        content_layout.addWidget(sidebar)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(HomeScreen())
        self.stacked_widget.addWidget(ChatSection())
        self.stacked_widget.addWidget(SystemMonitorSection())
        self.stacked_widget.addWidget(QuickActionsSection())
        self.stacked_widget.addWidget(KnowledgeBaseSection())
        self.stacked_widget.addWidget(SettingsSection())
        
        content_layout.addWidget(self.stacked_widget)
        
        content_container = QWidget()
        content_container.setLayout(content_layout)
        main_layout.addWidget(content_container)
        
        self.setCentralWidget(central_widget)
        self.setGeometry(0, 0, screen_width, screen_height)
        
        sidebar.navigationChanged.connect(self.stacked_widget.setCurrentIndex)
        
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1128, stop:0.3 #1a1f3a, stop:0.6 #0f172a, stop:1 #0a1128);
            }
        """)


# ==================== MAIN ENTRY ====================
def GraphicalUserInterface():
    ensure_directories()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = app.palette()
    palette.setColor(palette.Window, QColor(10, 17, 40))
    palette.setColor(palette.WindowText, QColor(0, 217, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()