from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, 
                             QSizePolicy, QGraphicsDropShadowEffect, QScrollArea, QGridLayout)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, 
                        QPixmap, QTextBlockFormat, QPainterPath, QLinearGradient, QPen, QBrush)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtProperty
from dotenv import dotenv_values
import sys
import os

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
    with open(TempDirectoryPath('Mic.data'), 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(TempDirectoryPath('Mic.data'), 'r', encoding='utf-8') as file:
        Status = file.read().strip()
    return Status

def SetAsssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitiated():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', 'w', encoding='utf-8') as file:
        file.write(Text)


class AnimatedButton(QPushButton):
    """Custom animated button with hover effects"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00d9ff, stop:1 #a855f7);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #a855f7, stop:1 #00d9ff);
            }
            QPushButton:pressed {
                padding: 13px 29px 11px 31px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 217, 255, 100))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


class GlowingMicButton(QLabel):
    """Animated microphone button with glow effect"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toggled = False
        self._glow_radius = 0  # Initialize BEFORE animation setup
        self.setFixedSize(120, 120)
        self.setAlignment(Qt.AlignCenter)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"glow_radius")
        self.animation.setDuration(1500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(30)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setLoopCount(-1)
        
        self.update_icon()
        
    @pyqtProperty(int)
    def glow_radius(self):
        return self._glow_radius
    
    @glow_radius.setter
    def glow_radius(self, value):
        self._glow_radius = value
        self.update()
        
    def update_icon(self):
        try:
            if self.toggled:
                icon_path = GraphicsDirectoryPath('Mic_on.png')
            else:
                icon_path = GraphicsDirectoryPath('Mic_off.png')
            
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        except:
            # Fallback if images don't exist
            self.setText("🎤" if self.toggled else "🔇")
            self.setStyleSheet("font-size: 48px;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw glowing circle when active
        if self.toggled:
            center = self.rect().center()
            
            # Outer glow
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(0, 217, 255, 50))
            gradient.setColorAt(1, QColor(168, 85, 247, 50))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, 50 + self._glow_radius, 50 + self._glow_radius)
            
            # Inner circle
            gradient2 = QLinearGradient(0, 0, self.width(), self.height())
            gradient2.setColorAt(0, QColor(0, 217, 255, 150))
            gradient2.setColorAt(1, QColor(168, 85, 247, 150))
            painter.setBrush(QBrush(gradient2))
            painter.drawEllipse(center, 45, 45)
        
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        self.toggled = not self.toggled
        self.update_icon()
        
        if self.toggled:
            self.animation.start()
            MicButtonInitiated()
        else:
            self.animation.stop()
            self._glow_radius = 0
            MicButtonClosed()
        
        self.update()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


class ModernChatBubble(QFrame):
    """Modern chat message bubble"""
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Message label
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        if is_user:
            msg_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #a855f7, stop:1 #8b5cf6);
                    color: white;
                    padding: 15px 20px;
                    border-radius: 20px;
                    font-size: 14px;
                    border-top-right-radius: 5px;
                }
            """)
            layout.addStretch()
            layout.addWidget(msg_label)
        else:
            msg_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1e293b, stop:1 #334155);
                    color: #00d9ff;
                    padding: 15px 20px;
                    border-radius: 20px;
                    font-size: 14px;
                    border-top-left-radius: 5px;
                }
            """)
            layout.addWidget(msg_label)
            layout.addStretch()
        
        self.setStyleSheet("background: transparent; border: none;")
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        msg_label.setGraphicsEffect(shadow)


class EnhancedChatSection(QWidget):
    """Enhanced chat section with modern design"""
    def __init__(self):
        super().__init__()
        self.messages = []
        self.initUI()
        
        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header with assistant name
        header = QLabel(f"⚡ {Assistantname}")
        header.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 32px;
                font-weight: bold;
                padding: 10px;
                background: transparent;
            }
        """)
        main_layout.addWidget(header)
        
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
                background: #1e293b;
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d9ff, stop:1 #a855f7);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00d9ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Chat container
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_widget)
        main_layout.addWidget(scroll)
        
        # Status label
        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-size: 16px;
                padding: 10px;
                background: rgba(16, 185, 129, 0.1);
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # GIF visualization
        self.gif_label = QLabel()
        try:
            movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
            movie.setScaledSize(QSize(400, 225))
            self.gif_label.setMovie(movie)
            self.gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
            main_layout.addWidget(self.gif_label)
        except:
            pass
        
        self.setStyleSheet("background: transparent;")
    
    def addMessage(self, message, is_user=False):
        bubble = ModernChatBubble(message, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        # Smooth scroll to bottom
        QTimer.singleShot(50, lambda: self.scrollToBottom())
    
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
        except FileNotFoundError:
            pass
    
    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                status = file.read()
            if status:
                self.status_label.setText(f"● {status}")
        except FileNotFoundError:
            pass


class ModernInitialScreen(QWidget):
    """Modern initial screen with glassmorphism"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)
        
        # Add stretch at top
        layout.addStretch(2)
        
        # Animated GIF
        gif_container = QWidget()
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setContentsMargins(0, 0, 0, 0)
        
        gif_label = QLabel()
        try:
            movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
            screen_width = QApplication.desktop().screenGeometry().width()
            gif_width = min(800, int(screen_width * 0.6))
            gif_height = int(gif_width * 9 / 16)
            movie.setScaledSize(QSize(gif_width, gif_height))
            gif_label.setMovie(movie)
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
            
            # Add glow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(40)
            shadow.setColor(QColor(0, 217, 255, 150))
            shadow.setOffset(0, 0)
            gif_label.setGraphicsEffect(shadow)
        except:
            gif_label.setText("⚡")
            gif_label.setStyleSheet("font-size: 120px; color: #00d9ff;")
        
        gif_layout.addWidget(gif_label)
        layout.addWidget(gif_container)
        
        # Title
        title = QLabel(Assistantname)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 48px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Ready to assist")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 18px;
                background: transparent;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Microphone button
        self.mic_button = GlowingMicButton()
        mic_container = QWidget()
        mic_layout = QHBoxLayout(mic_container)
        mic_layout.addStretch()
        mic_layout.addWidget(self.mic_button)
        mic_layout.addStretch()
        layout.addWidget(mic_container)
        
        # Instruction text
        instruction = QLabel("Click to activate voice control")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 14px;
                background: transparent;
                font-style: italic;
            }
        """)
        layout.addWidget(instruction)
        
        layout.addStretch(3)
        
        self.setStyleSheet("background: transparent;")
    
    def updateStatus(self):
        try:
            with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
                status = file.read()
            if status:
                self.status_label.setText(status)
        except FileNotFoundError:
            pass


class ModernMessageScreen(QWidget):
    """Modern message screen"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = EnhancedChatSection()
        layout.addWidget(chat_section)
        
        self.setStyleSheet("background: transparent;")


class ModernTopBar(QWidget):
    """Modern top bar with glassmorphism effect"""
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.setFixedHeight(60)
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Logo/Brand
        brand = QLabel(f"⚡ {Assistantname}")
        brand.setStyleSheet("""
            QLabel {
                color: #00d9ff;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(brand)
        
        layout.addStretch()
        
        # Navigation buttons
        home_btn = AnimatedButton("🏠 Home")
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        home_btn.setFixedHeight(40)
        layout.addWidget(home_btn)
        
        chat_btn = AnimatedButton("💬 Chat")
        chat_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        chat_btn.setFixedHeight(40)
        layout.addWidget(chat_btn)
        
        # Window controls
        min_btn = QPushButton("─")
        min_btn.setFixedSize(40, 40)
        min_btn.clicked.connect(lambda: self.parent().showMinimized())
        min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 116, 139, 0.3);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(100, 116, 139, 0.5);
            }
        """)
        layout.addWidget(min_btn)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(40, 40)
        self.max_btn.clicked.connect(self.toggleMaximize)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100, 116, 139, 0.3);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(100, 116, 139, 0.5);
            }
        """)
        layout.addWidget(self.max_btn)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(40, 40)
        close_btn.clicked.connect(lambda: self.parent().close())
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.3);
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.6);
            }
        """)
        layout.addWidget(close_btn)
        
        self.setStyleSheet("""
            QWidget {
                background: rgba(30, 41, 59, 0.8);
                border-radius: 0px;
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
    """Enhanced main window with modern design"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Central widget with gradient background
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Stacked widget for screens
        stacked_widget = QStackedWidget()
        initial_screen = ModernInitialScreen()
        message_screen = ModernMessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        # Top bar
        top_bar = ModernTopBar(self, stacked_widget)
        central_layout.addWidget(top_bar)
        central_layout.addWidget(stacked_widget)
        
        self.setCentralWidget(central_widget)
        self.setGeometry(0, 0, screen_width, screen_height)
        
        # Animated gradient background
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1128, stop:0.5 #1a1f3a, stop:1 #0a1128);
            }
        """)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()