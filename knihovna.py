from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout, QLabel, QPushButton, QDesktopWidget, QSlider, QComboBox, QFrame, QButtonGroup)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QBrush
import sys

# Definice stylů pro světlé a tmavé téma
LIGHT_THEME = """
    QWidget {
        color: #333333;
        background-color: transparent;
    }
    QWidget#RoundedWidget {
        background-color: transparent;
        border-radius: 15px;
    }
    QLabel {
        color: #333333;
    }
    QPushButton {
        background-color: #f0f0f0;
        border: none;
        border-radius: 12px;
        color: #333333;
    }
    QPushButton:hover {
        background-color: #e0e0e0;
    }
    QWidget#ControlWidget {
        background-color: rgba(240, 240, 240, 150);
        border-radius: 15px;
    }
"""

DARK_THEME = """
    QWidget {
        color: #ffffff;
        background-color: transparent;
    }
    QWidget#RoundedWidget {
        background-color: transparent;
        border-radius: 15px;
    }
    QLabel {
        color: #ffffff;
    }
    QPushButton {
        background-color: #424242;
        border: none;
        border-radius: 12px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #616161;
    }
    QWidget#ControlWidget {
        background-color: rgba(66, 66, 66, 150);
        border-radius: 15px;
    }
"""

class StyleHelper:
    @staticmethod
    def apply_button_style(button, default_color="#444444", hover_color="#666666", click_color="#222222"):
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(150, 50)
        button.default_color = QColor(default_color)
        button.hover_color = QColor(hover_color)
        button.click_color = QColor(click_color)
        button.light_color = QColor("#AAAAAA")
        button.current_color = button.default_color

        def paint_event(event):
            painter = QPainter(button)
            painter.setRenderHint(QPainter.Antialiasing)

            rect = button.rect()

            # Gradient pro 3D efekt
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, button.light_color)  # Světlejší nahoře
            gradient.setColorAt(0.5, button.current_color)  # Přechod
            gradient.setColorAt(1, button.default_color.darker(150))  # Tmavší dole
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(rect, 25, 25)

            # Vnější obrys tlačítka
            painter.setPen(QColor("#FFFFFF"))
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 25, 25)

            # Text tlačítka
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignCenter, button.text())

        def enter_event(event):
            button.current_color = button.hover_color
            button.update()

        def leave_event(event):
            button.current_color = button.default_color
            button.update()

        def mouse_press_event(event):
            if event.button() == Qt.LeftButton:
                button.current_color = button.click_color
                button.update()

        def mouse_release_event(event):
            if event.button() == Qt.LeftButton:
                button.current_color = button.hover_color
                button.update()

        button.paintEvent = paint_event
        button.enterEvent = enter_event
        button.leaveEvent = leave_event
        button.mousePressEvent = mouse_press_event
        button.mouseReleaseEvent = mouse_release_event

    @staticmethod
    def apply_combobox_style(combobox, default_color="#444444", hover_color="#666666"):
        combobox.setFixedSize(150, 50)
        combobox.setStyleSheet(f'''
            QComboBox {{
                background-color: {default_color};
                color: white;
                border-radius: 25px;
                padding: 5px;
                border: 2px solid white;
            }}
            QComboBox:hover {{
                background-color: {hover_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 1px solid white;
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid white;
                margin: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {default_color};
                selection-background-color: {hover_color};
                color: white;
                border-radius: 10px;
            }}
        ''')

    @staticmethod
    def apply_slider_style(slider, default_color="#444444", hover_color="#666666"):
        slider.setOrientation(Qt.Horizontal)
        slider.setStyleSheet(f'''
            QSlider::groove:horizontal {{
                height: 8px;
                background: {default_color};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1px solid {hover_color};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {hover_color};
            }}
        ''')

    @staticmethod
    def apply_frame_style(widget, frame_color="#DDDDDD", border_width=5, border_radius=12, padding=10):
        """
        Přidá rámeček okolo libovolného widgetu.
        :param widget: Widget, na který se má rámeček aplikovat.
        :param frame_color: Barva rámečku (např. #DDDDDD).
        :param border_width: Šířka rámečku.
        :param border_radius: Zaoblení rohů rámečku.
        :param padding: Vnitřní mezera mezi widgetem a rámečkem.
        """
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                border: {border_width}px solid {frame_color};
                border-radius: {border_radius}px;
                padding: {padding}px;
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.addWidget(widget)
        return frame
    
class ControlWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dragging = False
        self.offset = QPoint()
        self.is_dark_theme = True  # Výchozí tmavé téma
        
        self.setObjectName("ControlWidget")
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Vytvoření layoutu pro tlačítka
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Tlačítko pro přepínání tématu
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(25, 25)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Tlačítko pro minimalizaci
        min_btn = QPushButton("—")
        min_btn.setFixedSize(25, 25)
        min_btn.clicked.connect(self.main_window.showMinimized)
        
        # Tlačítko pro zavření
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.clicked.connect(self.main_window.close)
        
        # Přidání tlačítek do layoutu
        layout.addWidget(self.theme_btn)
        layout.addWidget(min_btn)
        layout.addWidget(close_btn)
        
        # Nastavení vzhledu close tlačítka
        close_btn.setStyleSheet("""
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        
        self.setFixedSize(layout.sizeHint())
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_btn.setText("🌙" if self.is_dark_theme else "☀️")
        self.main_window.set_theme(self.is_dark_theme)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

class RoundedWidget(QWidget):
    def __init__(self, color="#ffffff"):
        super().__init__()
        self.setObjectName("RoundedWidget")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = color
        
        layout = QVBoxLayout(self)
        label = QLabel("Obsah okna")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
    def set_color(self, color):
        self.color = color
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        painter.setPen(Qt.NoPen)
        painter.fillPath(path, QColor(self.color))
        
class ButtonTabs(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Hlavní vertikální layout
        layout = QVBoxLayout(self)
        layout.setSpacing(5)  # Mezera mezi tlačítky a obsahem
        layout.setContentsMargins(5, 5, 5, 5)  # Mezery okolo

        # Container pro tlačítka
        self.button_container = QWidget()
        self.button_container.setObjectName("ButtonContainer")
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setSpacing(5)  # Mezera mezi tlačítky
        self.button_layout.setContentsMargins(5, 5, 5, 5)  # Mezery okolo tlačítek
        
        # Nastavení průhledného pozadí pro container
        self.button_container.setStyleSheet("""
            QWidget#ButtonContainer {
                background-color: transparent;
            }
        """)

        # Inicializace button group pro správu "tabů"
        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self._on_tab_change)

        # Widget pro obsah tabů
        self.stack = QStackedWidget()

        # Přidání containerů do hlavního layoutu
        layout.addWidget(self.button_container)
        layout.addWidget(self.stack)

    def add_tab(self, title, widget):
        """Přidá nový tab s tlačítkem a widgetem"""
        # Vytvoření tlačítka pro tab
        button = QPushButton(title)
        button.setCheckable(True)
        button.setFixedSize(100, 30)  # Nastavení fixní velikosti tlačítka
        
        # Aplikace vlastního stylu tlačítka pomocí StyleHelper
        StyleHelper.apply_button_style(
            button,
            default_color="#424242",
            hover_color="#616161",
            click_color="#2196F3"
        )
        
        # Přidání tlačítka do skupiny a layoutu
        self.button_group.addButton(button)
        self.button_layout.addWidget(button)
        
        # Přidání widgetu do stacku
        self.stack.addWidget(widget)
        
        # Pokud je to první tab, vybereme ho
        if self.button_group.buttons().__len__() == 1:
            button.setChecked(True)
            self.stack.setCurrentIndex(0)

    def _on_tab_change(self, button):
        """Handler pro změnu aktivního tabu"""
        index = self.button_group.buttons().index(button)
        self.stack.setCurrentIndex(index)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Nejdřív nastavíme velikost a vlastnosti okna
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Nastavíme fixní velikost okna před centrováním
        self.setFixedSize(1150, 890)  # Upravená velikost podle vašich komponent
        
        self.dragging = False
        self.offset = QPoint()
        
        # Vytvoření centrálního widgetu
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        central_widget.setStyleSheet("background: transparent;")
        
        # Hlavní vertikální layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # Stejná mezera jako mezi levým a pravým oknem
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Vytvoření tab menu
        self.tabs = ButtonTabs(self)
        # Nastavení minimální výšky pro tab menu
        self.tabs.setFixedHeight(60)
        # Nahrazení původního top_window taby
        self.top_window = self.tabs

        # Přidání tabů s obsahem
        tab1_content = RoundedWidget("#424242")
        tab2_content = RoundedWidget("#424242")
        tab3_content = RoundedWidget("#424242")
        tab4_content = RoundedWidget("#424242")
        tab5_content = RoundedWidget("#424242")
        tab6_content = RoundedWidget("#424242")

        # Přidání tabů do ButtonTabs
        self.tabs.add_tab("Knihy", tab1_content)
        self.tabs.add_tab("Časopisy", tab2_content)
        self.tabs.add_tab("Datasheets", tab3_content)
        self.tabs.add_tab("Ostatní", tab4_content)
        self.tabs.add_tab("Vyhledávání", tab5_content)
        self.tabs.add_tab("Ostatní funkce", tab6_content)
        
        # Horizontální layout pro prostřední okna
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        
        # Horizontální layout pro spodní okna
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Vytvoření prostředních oken
        self.left_window = RoundedWidget("#424242")
        self.right_window = RoundedWidget("#353535")
        
        # Vytvoření spodních oken
        self.bottom_left_window = RoundedWidget("#424242")
        self.bottom_right_window = RoundedWidget("#353535")
        
        # Nastavení velikostí oken
        self.left_window.setMinimumSize(300, 700)
        self.right_window.setMinimumSize(800, 700)
        
        # Nastavení fixní výšky spodních oken
        self.bottom_left_window.setFixedHeight(100)
        self.bottom_right_window.setFixedHeight(100)
        
        # Nastavení minimální šířky spodních oken - stejná jako u oken nad nimi
        self.bottom_left_window.setMinimumWidth(300)
        self.bottom_right_window.setMinimumWidth(800)
        
        # Přidání oken do layoutů
        main_layout.addWidget(self.top_window)
        
        middle_layout.addWidget(self.left_window)
        middle_layout.addWidget(self.right_window)
        main_layout.addLayout(middle_layout)
        
        bottom_layout.addWidget(self.bottom_left_window)
        bottom_layout.addWidget(self.bottom_right_window)
        main_layout.addLayout(bottom_layout)
        
        # Vytvoření a umístění ovládacího widgetu
        self.control_widget = ControlWidget(self)
        self.control_widget.setParent(self)
        self.control_widget.move(1025, 80)
        
        # Upravená velikost hlavního okna pro accommodaci nových oken
        self.setGeometry(100, 100, 800, 690)  # Zvětšená výška pro všechna okna
        self.centerWindow()
        
    def centerWindow(self):
        self.setWindowTitle('Centrované Okno')
        self.setGeometry(0, 0, 800, 600)  # Nastavte požadovanou velikost okna
        self.center()
        
    def centerWindow(self):
        # Získání geometrie okna
        qr = self.frameGeometry()
        # Získání středu obrazovky
        cp = QDesktopWidget().availableGeometry().center()
        # Přesunutí geometrie okna na střed obrazovky
        qr.moveCenter(cp)
        # Přesunutí okna na vypočtenou pozici
        self.move(qr.topLeft())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centerWindow()  # Centrování při změně velikosti
    
    def showEvent(self, event):
        super().showEvent(event)
        self.centerWindow()  # Centrování při zobrazení okna
    
    def set_theme(self, is_dark):
        if is_dark:
            app.setStyleSheet(DARK_THEME)
            for i in range(self.tabs.stack.count()):
                widget = self.tabs.stack.widget(i)
                if isinstance(widget, RoundedWidget):
                    widget.set_color("#424242")
            self.left_window.set_color("#424242")
            self.right_window.set_color("#353535")
            self.bottom_left_window.set_color("#424242")
            self.bottom_right_window.set_color("#353535")
        else:
            app.setStyleSheet(LIGHT_THEME)
            for i in range(self.tabs.stack.count()):
                widget = self.tabs.stack.widget(i)
                if isinstance(widget, RoundedWidget):
                    widget.set_color("#f0f0f0")
            self.left_window.set_color("#f0f0f0")
            self.right_window.set_color("#e0e0e0")
            self.bottom_left_window.set_color("#f0f0f0")
            self.bottom_right_window.set_color("#e0e0e0")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Aplikování výchozího tmavého tématu
    app.setStyleSheet(DARK_THEME)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
