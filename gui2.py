from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, 
                             QSizePolicy, QGraphicsDropShadowEffect, QScrollArea, QGridLayout)
from PyQt5.QtGui import (QIcon, QPainter, QColor, QTextCharFormat, QFont, 
                        QPixmap, QTextBlockFormat, QPainterPath, QLinearGradient, 
                        QPen, QBrush, QRadialGradient, QPolygonF)
from PyQt5.QtCore import (Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, 
                          QRect, QPoint, pyqtProperty, QPointF, QRectF)
from dotenv import dotenv_values
import sys
import os
import math
import random

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "JARVIS")
old_chat_message = ""

# Directory paths
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 
                     'can you', "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf'{TempDirPath}\Mic.data', 'w', encoding='utf-8') as file:
            file.write(Command)
    except:
        pass

def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', 'r', encoding='utf-8') as file:
            Status = file.read().strip()
        return Status
    except:
        return "False"

def SetAsssistantStatus(Status):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
            file.write(Status)
    except:
        pass

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
            Status = file.read()
        return Status
    except:
        return ""

def MicButtonInitiated():
    SetMicrophoneStatus("True")

def MicButtonClosed():
    SetMicrophoneStatus("False")

def ShowTextToScreen(Text):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
            file.write(Text)
    except:
        pass


class HolographicOrb(QWidget):
    """Animated holographic orb - main AI visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 400)
        
        self._rotation = 0
        self._pulse = 0
        self._is_active = False
        self.particles = []
        
        # Initialize particles
        for _ in range(30):
            self.particles.append({
                'angle': random.uniform(0, 360),
                'distance': random.uniform(50, 150),
                'speed': random.uniform(0.5, 2),
                'size': random.uniform(2, 6)
            })
        
        # Rotation animation
        self.rotation_anim = QPropertyAnimation(self, b"rotation")
        self.rotation_anim.setDuration(3000)
        self.rotation_anim.setStartValue(0)
        self.rotation_anim.setEndValue(360)
        self.rotation_anim.setLoopCount(-1)
        self.rotation_anim.start()
        
        # Pulse animation
        self.pulse_anim = QPropertyAnimation(self, b"pulse")
        self.pulse_anim.setDuration(2000)
        self.pulse_anim.setStartValue(0)
        self.pulse_anim.setEndValue(20)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.start()
        
        # Update timer for particles
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
    
    def setActive(self, active):
        self._is_active = active
        if active:
            self.rotation_anim.setDuration(1000)
        else:
            self.rotation_anim.setDuration(3000)
    
    def updateParticles(self):
        for particle in self.particles:
            particle['angle'] += particle['speed']
            if particle['angle'] >= 360:
                particle['angle'] -= 360
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        
        # Draw outer rings
        for i in range(3):
            radius = 120 + i * 20 + self._pulse
            
            gradient = QRadialGradient(center, radius)
            if self._is_active:
                gradient.setColorAt(0, QColor(0, 217, 255, 0))
                gradient.setColorAt(0.8, QColor(0, 217, 255, 30 - i * 10))
                gradient.setColorAt(1, QColor(168, 85, 247, 0))
            else:
                gradient.setColorAt(0, QColor(0, 217, 255, 0))
                gradient.setColorAt(0.8, QColor(0, 217, 255, 15 - i * 5))
                gradient.setColorAt(1, QColor(0, 217, 255, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(0, 217, 255, 50), 2))
            painter.drawEllipse(center, radius, radius)
        
        # Draw rotating hexagon
        hexagon_points = []
        for i in range(6):
            angle = math.radians(self._rotation + i * 60)
            x = center.x() + 80 * math.cos(angle)
            y = center.y() + 80 * math.sin(angle)
            hexagon_points.append(QPointF(x, y))
        
        painter.setPen(QPen(QColor(168, 85, 247, 150), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawPolygon(QPolygonF(hexagon_points))
        
        # Draw inner rotating triangle
        triangle_points = []
        for i in range(3):
            angle = math.radians(-self._rotation * 1.5 + i * 120)
            x = center.x() + 50 * math.cos(angle)
            y = center.y() + 50 * math.sin(angle)
            triangle_points.append(QPointF(x, y))
        
        painter.setPen(QPen(QColor(0, 217, 255, 200), 2))
        painter.drawPolygon(QPolygonF(triangle_points))
        
        # Draw particles
        for particle in self.particles:
            angle = math.radians(particle['angle'])
            x = center.x() + particle['distance'] * math.cos(angle)
            y = center.y() + particle['distance'] * math.sin(angle)
            
            gradient = QRadialGradient(QPointF(x, y), particle['size'])
            gradient.setColorAt(0, QColor(0, 217, 255, 200))
            gradient.setColorAt(1, QColor(0, 217, 255, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), particle['size'], particle['size'])
        
        # Draw core
        core_gradient = QRadialGradient(center, 30 + self._pulse / 2)
        if self._is_active:
            core_gradient.setColorAt(0, QColor(255, 255, 255, 255))
            core_gradient.setColorAt(0.3, QColor(0, 217, 255, 200))
            core_gradient.setColorAt(1, QColor(168, 85, 247, 0))
        else:
            core_gradient.setColorAt(0, QColor(0, 217, 255, 150))
            core_gradient.setColorAt(0.5, QColor(0, 217, 255, 100))
            core_gradient.setColorAt(1, QColor(0, 217, 255, 0))
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, 30 + self._pulse / 2, 30 + self._pulse / 2)


class HolographicButton(QPushButton):
    """Modern holographic button"""
    def __init__(self, text="", icon_text="", parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.button_text = text
        self._glow = 0
        
        self.setFixedHeight(60)
        self.setMinimumWidth(150)
        self.setCursor(Qt.PointingHandCursor)
        
        self.glow_anim = QPropertyAnimation(self, b"glow")
        self.glow_anim.setDuration(1000)
        self.glow_anim.setStartValue(0)
        self.glow_anim.setEndValue(15)
        self.glow_anim.setEasingCurve(QEasingCurve.InOutQuad)
    
    @pyqtProperty(int)
    def glow(self):
        return self._glow
    
    @glow.setter
    def glow(self, value):
        self._glow = value
        self.update()
    
    def enterEvent(self, event):
        self.glow_anim.setDirection(QPropertyAnimation.Forward)
        self.glow_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.glow_anim.setDirection(QPropertyAnimation.Backward)
        self.glow_anim.start()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        
        # Glow effect
        if self._glow > 0:
            glow_rect = rect.adjusted(-self._glow, -self._glow, self._glow, self._glow)
            gradient = QRadialGradient(rect.center(), rect.width())
            gradient.setColorAt(0, QColor(0, 217, 255, 50))
            gradient.setColorAt(1, QColor(0, 217, 255, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(glow_rect, 15, 15)
        
        # Button background
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor(30, 41, 59, 180))
        gradient.setColorAt(1, QColor(15, 23, 42, 180))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 217, 255, 100), 2))
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 15, 15)
        
        # Draw icon and text
        painter.setPen(QColor(0, 217, 255))
        font = QFont("Arial", 12, QFont.Bold)
        painter.setFont(font)
        
        text = f"{self.icon_text}  {self.button_text}"
        painter.drawText(rect, Qt.AlignCenter, text)


class VoiceControlButton(QWidget):
    """Advanced voice control button with waveform"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.is_active = False
        self._wave_offset = 0
        
        self.wave_anim = QPropertyAnimation(self, b"wave_offset")
        self.wave_anim.setDuration(1500)
        self.wave_anim.setStartValue(0)
        self.wave_anim.setEndValue(360)
        self.wave_anim.setLoopCount(-1)
        
        self.setCursor(Qt.PointingHandCursor)
    
    @pyqtProperty(float)
    def wave_offset(self):
        return self._wave_offset
    
    @wave_offset.setter
    def wave_offset(self, value):
        self._wave_offset = value
        self.update()
    
    def mousePressEvent(self, event):
        self.is_active = not self.is_active
        if self.is_active:
            self.wave_anim.start()
            MicButtonInitiated()
        else:
            self.wave_anim.stop()
            MicButtonClosed()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        
        if self.is_active:
            # Animated waveform rings
            for i in range(3):
                radius = 60 + i * 15
                
                path = QPainterPath()
                points = []
                for angle in range(0, 360, 5):
                    rad = math.radians(angle + self._wave_offset + i * 30)
                    wave = math.sin(rad * 3) * 5
                    r = radius + wave
                    x = center.x() + r * math.cos(rad)
                    y = center.y() + r * math.sin(rad)
                    points.append(QPointF(x, y))
                
                if points:
                    path.moveTo(points[0])
                    for point in points[1:]:
                        path.lineTo(point)
                    path.closeSubpath()
                
                painter.setPen(QPen(QColor(0, 217, 255, 150 - i * 30), 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
            
            # Active core
            gradient = QRadialGradient(center, 40)
            gradient.setColorAt(0, QColor(255, 255, 255, 200))
            gradient.setColorAt(0.5, QColor(0, 217, 255, 150))
            gradient.setColorAt(1, QColor(168, 85, 247, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, 40, 40)
            
            # Mic icon
            painter.setPen(QPen(QColor(10, 17, 40), 3))
            painter.drawEllipse(QRectF(center.x() - 10, center.y() - 20, 20, 25))
            painter.drawLine(QPointF(center.x(), center.y() + 5), QPointF(center.x(), center.y() + 20))
            painter.drawLine(QPointF(center.x() - 10, center.y() + 20), QPointF(center.x() + 10, center.y() + 20))
        else:
            # Inactive state
            gradient = QRadialGradient(center, 50)
            gradient.setColorAt(0, QColor(30, 41, 59, 200))
            gradient.setColorAt(1, QColor(15, 23, 42, 150))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(100, 116, 139, 150), 2))
            painter.drawEllipse(center, 50, 50)
            
            # Mic icon
            painter.setPen(QPen(QColor(100, 116, 139), 3))
            painter.drawEllipse(QRectF(center.x() - 10, center.y() - 20, 20, 25))
            painter.drawLine(QPointF(center.x(), center.y() + 5), QPointF(center.x(), center.y() + 20))
            painter.drawLine(QPointF(center.x() - 10, center.y() + 20), QPointF(center.x() + 10, center.y() + 20))


class HolographicChatBubble(QFrame):
    """Futuristic chat bubble with holographic effect"""
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setFrameStyle(QFrame.NoFrame)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if is_user:
            msg_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(168, 85, 247, 0.3), stop:1 rgba(139, 92, 246, 0.3));
                    color: #e0e7ff;
                    padding: 15px 20px;
                    border-radius: 20px;
                    border: 2px solid rgba(168, 85, 247, 0.5);
                    font-size: 14px;
                }
            """)
            layout.addStretch()
            layout.addWidget(msg_label)
        else:
            msg_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 217, 255, 0.2), stop:1 rgba(14, 165, 233, 0.2));
                    color: #00d9ff;
                    padding: 15px 20px;
                    border-radius: 20px;
                    border: 2px solid rgba(0, 217, 255, 0.5);
                    font-size: 14px;
                }
            """)
            layout.addWidget(msg_label)
            layout.addStretch()
        
        self.setStyleSheet("background: transparent;")


class ModernChatSection(QWidget):
    """Chat section with holographic design"""
    def __init__(self):
        super().__init__()
        self.messages = []
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel(f"◈ {Assistantname} INTERFACE ◈")
        title.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 28px;
                font-weight: bold;
                letter-spacing: 3px;
                background: transparent;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 24px;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.status_indicator)
        
        main_layout.addLayout(header_layout)
        
        # Chat scroll area
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
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d9ff, stop:1 #a855f7);
                border-radius: 4px;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_widget)
        main_layout.addWidget(scroll)
        
        # Status bar
        self.status_label = QLabel("System Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                padding: 10px 20px;
                background: rgba(30, 41, 59, 0.3);
                border: 1px solid rgba(0, 217, 255, 0.3);
                border-radius: 15px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        self.setStyleSheet("background: transparent;")
    
    def addMessage(self, message, is_user=False):
        bubble = HolographicChatBubble(message, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self.scrollToBottom)
    
    def scrollToBottom(self):
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            )
    
    def loadMessages(self):
        global old_chat_message
        try:
            with open(rf'{TempDirPath}\Responses.data', 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(messages, is_user=False)
                old_chat_message = messages
        except:
            pass
    
    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                status = file.read()
            if status:
                self.status_label.setText(status)
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        color: #00d9ff;
                        font-size: 24px;
                        background: transparent;
                    }
                """)
        except:
            pass


class HolographicHomeScreen(QWidget):
    """Main holographic interface screen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(40)
        
        layout.addStretch()
        
        # Holographic orb
        orb_container = QWidget()
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setContentsMargins(0, 0, 0, 0)
        
        self.orb = HolographicOrb()
        orb_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        layout.addWidget(orb_container)
        
        # Title
        title = QLabel(Assistantname)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 56px;
                font-weight: bold;
                letter-spacing: 12px;
                background: transparent;
                text-transform: uppercase;
            }
        """)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("ADVANCED AI SYSTEM")
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
        
        # Status
        self.status_label = QLabel("◈ ONLINE ◈")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 18px;
                padding: 15px;
                background: rgba(16, 185, 129, 0.1);
                border: 2px solid rgba(16, 185, 129, 0.3);
                border-radius: 20px;
            }
        """)
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        # Voice control button
        self.voice_btn = VoiceControlButton()
        voice_container = QWidget()
        voice_layout = QHBoxLayout(voice_container)
        voice_layout.addStretch()
        voice_layout.addWidget(self.voice_btn)
        voice_layout.addStretch()
        layout.addWidget(voice_container)
        
        # Instruction
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
    
    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                status = file.read()
            if status:
                self.status_label.setText(f"◈ {status.upper()} ◈")
                self.orb.setActive(True)
            else:
                self.orb.setActive(False)
        except:
            pass


class HolographicMessageScreen(QWidget):
    """Message screen with holographic chat"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = ModernChatSection()
        layout.addWidget(chat_section)
        
        self.setStyleSheet("background: transparent;")


class HolographicTopBar(QWidget):
    """Futuristic top navigation bar"""
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.setFixedHeight(70)
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(20)
        
        # Brand
        brand = QLabel(f"◈ {Assistantname}")
        brand.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        layout.addWidget(brand)
        
        layout.addStretch()
        
        # Navigation
        home_btn = HolographicButton("HOME", "⌂")
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(home_btn)
        
        chat_btn = HolographicButton("CHAT", "◈")
        chat_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(chat_btn)
        
        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        min_btn = QPushButton("─")
        min_btn.setFixedSize(40, 40)
        min_btn.clicked.connect(lambda: self.parent().showMinimized())
        min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 116, 139, 0.3);
                color: #64748b;
                border: 1px solid rgba(100, 116, 139, 0.5);
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(100, 116, 139, 0.5);
                color: white;
            }
        """)
        min_btn.setCursor(Qt.PointingHandCursor)
        controls_layout.addWidget(min_btn)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(40, 40)
        self.max_btn.clicked.connect(self.toggleMaximize)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 116, 139, 0.3);
                color: #64748b;
                border: 1px solid rgba(100, 116, 139, 0.5);
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(100, 116, 139, 0.5);
                color: white;
            }
        """)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        controls_layout.addWidget(self.max_btn)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(40, 40)
        close_btn.clicked.connect(lambda: self.parent().close())
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.3);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.5);
                border-radius: 20px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.6);
                color: white;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        controls_layout.addWidget(close_btn)
        
        layout.addLayout(controls_layout)
        
        self.setStyleSheet("""
            QWidget {
                background: rgba(10, 17, 40, 0.9);
                border-bottom: 2px solid rgba(0, 217, 255, 0.3);
            }
        """)
    
    def toggleMaximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.max_btn.setText("□")
        else:
            self.parent().showMaximized()
            self.max_btn.setText("❐")


class MainWindow(QMainWindow):
    """Main application window with holographic design"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()
    
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Central widget
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Stacked widget
        stacked_widget = QStackedWidget()
        home_screen = HolographicHomeScreen()
        message_screen = HolographicMessageScreen()
        stacked_widget.addWidget(home_screen)
        stacked_widget.addWidget(message_screen)
        
        # Top bar
        top_bar = HolographicTopBar(self, stacked_widget)
        central_layout.addWidget(top_bar)
        central_layout.addWidget(stacked_widget)
        
        self.setCentralWidget(central_widget)
        self.setGeometry(0, 0, screen_width, screen_height)
        
        # Animated gradient background
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1128, 
                    stop:0.3 #1a1f3a, 
                    stop:0.6 #0f172a,
                    stop:1 #0a1128);
            }
        """)


def GraphicalUserInterface():
    """Main entry point for the GUI"""
    try:
        os.makedirs(TempDirPath, exist_ok=True)
    except:
        pass
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark palette
    palette = app.palette()
    palette.setColor(palette.Window, QColor(10, 17, 40))
    palette.setColor(palette.WindowText, QColor(0, 217, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()