# Standardní knihovny
import os
import sys
import json
import shutil
import sqlite3
from datetime import datetime
from functools import lru_cache

# PDF knihovna
import PyPDF2

# PyQt5 importy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QLineEdit, QTextEdit, QFileDialog, QListWidgetItem, 
    QTreeWidgetItem, QInputDialog, QGridLayout, QTreeWidget, QListWidget, 
    QScrollArea, QCheckBox, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QDesktopWidget, QStackedWidget, QButtonGroup, QSlider, 
    QComboBox, QFrame, QDialog, QSpinBox, QSizePolicy, QProgressBar, QTabWidget, QGroupBox,
    QAbstractItemView, QRadioButton
)
from PyQt5.QtCore import (
    Qt, QPoint, QRectF, QSize, QObject, pyqtSignal, QThread, QTimer
)
from PyQt5.QtGui import (
    QPainter, QColor, QPainterPath, QLinearGradient, QBrush, 
    QPixmap, QIcon, QPen, QFont, QPalette, QStandardItemModel, 
    QStandardItem, QFontMetrics, QCursor
)

# Pomocné Qt moduly
from PyQt5 import QtWidgets, QtGui, QtCore

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # Podpora DPI škálování
QApplication.setAttribute(Qt.AA_UseStyleSheetPropagationInWidgetStyles)

class StyleHelper:
    
    @staticmethod
    def apply_window_background(widget, color="#353535"):
        """
        Aplikuje barvu pozadí na daný widget.
        :param widget: Widget, na který se má aplikovat barva pozadí.
        :param color: Hex kód barvy pozadí.
        """
        widget.setStyleSheet(f"background-color: {color}; border-radius: 15px;")
        
    @staticmethod
    def apply_text_widget_style(
        widget,
        frame_color="#666666",
        background_color="#353535",
        text_color="black",
        font_family="Arial",
        font_size=10,
        bold=False,
        italic=False,
        border_radius=15,
        border_width=2,
        padding=5
    ):
        """
        Aplikuje jednotný styl pro textové widgety (QLineEdit, QTextEdit).
        """
        from PyQt5.QtGui import QFont
        font = QFont(font_family, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        widget.setFont(font)

        # Základní stylesheet pro textové widgety
        base_style = f"""
            border: {border_width}px solid {frame_color};
            border-radius: {border_radius}px;
            background-color: {background_color};
            color: {text_color};
            padding: {padding}px;
        """

        # Nastavení stylu
        widget.setStyleSheet(base_style)

        return widget
    
    @staticmethod
    def apply_button_style(button: QPushButton, default_color="#444444", hover_color="#666666", click_color="#222222", checked_color="#777777"):
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(150, 40)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {default_color};
                border: 2px solid #555555; /* Jemný vnější okraj */
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 2px solid #777777; /* Zvýraznění okraje při najetí */
            }}
            QPushButton:pressed {{
                background-color: {click_color};
                /* Vnitřní stín pro efekt stisknutí */
                box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5); 
                border: 1px solid #333333; /* Zjemnění okraje při stisknutí */
            }}
            QPushButton:checked {{ /* Styl pro zaškrtnuté tlačítko */
                background-color: {checked_color};
                /* Vnitřní stín pro efekt stisknutí */
                box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5);
                border: 1px solid #333333;
            }}
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #666666, stop: 1 #444444); /* Gradient pro odlesk */
                border: 2px solid #555555;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
            }}
        """)
        
        """1. Jemnější odlesk (gradient):

        Pro jemnější odlesk můžeme upravit gradient a přidat více "zastávek" (stop) s jemnějšími přechody barev:
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                            stop: 0 #5a5a5a,  /* Jemnější světlá */
                            stop: 0.2 #4f4f4f, /* Přechod */
                            stop: 0.8 #494949, /* Další přechod */
                            stop: 1 #444444);  /* Původní tmavá */
            Přidáním více zastávek a jemnějšími změnami barev mezi nimi docílíme plynulejšího a přirozenějšího odlesku.
            
            2. Barva textu pro :pressed a :checked:

        Můžeme také změnit barvu textu při stisknutí nebo zaškrtnutí tlačítka, aby byl efekt ještě výraznější:
        QPushButton:pressed {
            background-color: {click_color};
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5);
            border: 1px solid #333333;
            color: #eeeeee; /* Světlejší text při stisknutí */
        }
        QPushButton:checked {
            background-color: {checked_color};
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5);
            border: 1px solid #333333;
            color: #eeeeee; /* Světlejší text při zaškrtnutí */
        }
        
        3. Vlastnosti písma:

        Můžeme také ovlivnit vlastnosti písma, jako je velikost, tučnost nebo rodina písma:
        QPushButton {
            /* ... ostatní styly */
             font-size: 14px;
            font-weight: bold;
            font-family: "Arial"; /* Nebo jiný font */
        }
        
        4. Změna velikosti okraje při najetí myší (alternativa k barvě):

        Místo změny barvy okraje při najetí myší můžeme mírně zvětšit jeho tloušťku:
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #888888, stop: 1 #666666);
            border: 3px solid #777777; /* Zvětšení okraje */
            padding: 4px 9px; /* Kompenzace zvětšení okraje, aby se tlačítko nezvětšilo */
        }
        Tím se vytvoří jemný "vyskočící" efekt. Důležité je zde i zmenšit padding o 1px z každé strany, aby se celková velikost tlačítka nezměnila.

        Kompletní příklad s vylepšeními:
        """
        """@staticmethod
        def apply_button_style(button: QPushButton, default_color="#444444", hover_color="#666666", click_color="#222222", checked_color="#777777"):
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(150, 40)
        button.setStyleSheet(f"""
        """QPushButton {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                        stop: 0 #5a5a5a,
                                        stop: 0.2 #4f4f4f,
                                        stop: 0.8 #494949,
                                        stop: 1 #444444);
            border: 2px solid #555555;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #888888, stop: 1 #666666);
            border: 3px solid #777777;
            padding: 4px 9px;
        }}
        QPushButton:pressed {{
            background-color: {click_color};
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5);
            border: 1px solid #333333;
            color: #eeeeee;
        }}
        QPushButton:checked {{
            background-color: {checked_color};
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.5);
            border: 1px solid #333333;
            color: #eeeeee;
        }}
    """
        
    @staticmethod
    def apply_delete_button_style(button):
        StyleHelper.apply_button_style(button, default_color="#990000", hover_color="#BB0000", click_color="#660000")

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
    def show_confirm_dialog(title, message, dialog_type=None, parent=None):
        """
        Zobrazí potvrzovací dialog podle nastavení.
        
        Args:
            title: Titulek dialogu
            message: Zpráva dialogu
            dialog_type: Typ dialogu pro kontrolu nastavení ('delete', 'category_delete', 'import', 'backup')
            parent: Rodičovské okno
            
        Returns:
            QDialog.Accepted nebo QDialog.Rejected
        """
        # Kontrola nastavení dialogů
        if parent and dialog_type:
            settings_manager = parent.window().settings_manager
            dialog_settings = settings_manager.get_setting('ui', 'dialogs')
            
            # Mapování typů dialogů na klíče nastavení
            dialog_keys = {
                'delete': 'confirm_delete',
                'category_delete': 'confirm_category_delete',
                'import': 'confirm_import',
                'backup': 'confirm_backup'
            }
            
            # Pokud je dialog vypnutý v nastavení, vrátit rovnou Accepted
            if not dialog_settings.get(dialog_keys.get(dialog_type, ''), True):
                return QDialog.Accepted
        
        # Zobrazení dialogu
        return StyleHelper.create_message_box(title, message, "question", parent)
        
    @staticmethod
    def apply_small_combobox_style(combobox, default_color="#444444", hover_color="#666666"):
        """
        Aplikuje styl pro menší combobox s výškou 30px a šířkou 170px.
        Používá se pro umístění více comboboxů vedle sebe.
        """
        combobox.setFixedSize(170, 30)
        combobox.setStyleSheet(f'''
            QComboBox {{
                background-color: {default_color};
                color: white;
                border-radius: 15px;
                padding: 5px;
                border: 2px solid #666666;
            }}
            QComboBox:hover {{
                background-color: {hover_color};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                border-left: 1px solid #666666;
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #666666;
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
    def enable_clear_selection(tree_widget):
        """
        Umožní odznačení výběru v QTreeWidget kliknutím mimo položku.

        Args:
            tree_widget (QTreeWidget): Strom, na který se má aplikovat funkčnost.
        """
        original_mouse_press_event = tree_widget.mousePressEvent

        def custom_mouse_press_event(event):
            item = tree_widget.itemAt(event.pos())
            if not item:  # Kliknutí mimo položku
                tree_widget.clearSelection()
            original_mouse_press_event(event)

        tree_widget.mousePressEvent = custom_mouse_press_event


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
    def apply_frame_style(widget, frame_color="#666666", border_width=2, border_radius=15, padding=15):
        """
        Přidá rámeček okolo libovolného widgetu.
        """
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                border: {border_width}px solid {frame_color};
                border-radius: {border_radius}px;
                background-color: transparent;
                padding: {padding}px;
            }}
        """)
        
        # Vytvoření layoutu pro frame
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)  # Odstraníme vnitřní okraje
        layout.addWidget(widget)
        
        return frame
    
    @staticmethod
    def apply_label_style(label: QLabel, color="#AAAAAA", font_size=12): # Přidána metoda pro label
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
            }}
        """)
        
    @staticmethod
    def apply_treewidget_style(tree_widget, background_color="#353535", text_color="white",
                           font_family="Arial", font_size=12, font_bold=False, font_italic=False,
                           selection_border_color="#00A0FF", selection_border_radius=5,
                           hover_background_color="#444444", hover_border_radius=3):
        tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {background_color};
                border: none;
                font-family: "{font_family}";
                font-size: {font_size}pt;
                color: {text_color};
                show-decoration-selected: 0;
                outline: none;
            }}
            
            QTreeWidget::item {{
                border: none;
                padding: 5px;
                background: transparent;
            }}
            
            QTreeWidget::item:selected,
            QTreeWidget::item:selected:active,
            QTreeWidget::item:selected:!active {{
                background: transparent;
                border: 2px solid {selection_border_color};
                border-radius: {selection_border_radius}px;
            }}
            
            QTreeWidget::branch {{
                background: transparent;
            }}
            
            QTreeWidget::branch:selected {{
                background: transparent;
            }}
            
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                image: url(icons/plus.png);
                background: transparent;
            }}
            
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                image: url(icons/minus.png);
                background: transparent;
            }}
            
            
            
            # Nastavení QSrollBar pro QTreeWidget
             
            QScrollBar:vertical {{
                background: #333333; /* Tmavší pozadí scrollbaru */
                width: 10px; /* Šířka scrollbaru */
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #555555; /* Barva posuvníku */
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none; /* Skrytí šipek scrollbaru */
            }}

            QHeaderView {{
                background-color: transparent;
                border: none;
                font-family: "{font_family}";
                font-size: {font_size}pt;
                color: {text_color};
            }}
            QScrollBar:horizontal {{  /* Nové styly pro horizontální scrollbar */
                background: #333333;
                height: 10px;        /* Výška scrollbaru */
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #555555;
                min-width: 20px;     /* Minimální šířka posuvníku */
                border-radius: 4px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                background: none;
            }}
        """)
        
    @staticmethod
    def create_input_dialog(title, label, parent=None):
        dialog = QDialog(parent)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        StyleHelper.make_draggable(dialog)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Použití FramedRoundedWidget
        container = FramedRoundedWidget(color="#2B2B2B", border_color="#555555", border_width=3, border_radius=15)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        header = StyleHelper.setup_header(
            title,
            container,
            on_minimize=dialog.showMinimized,
            on_close=dialog.reject
        )
        container_layout.addWidget(header)

        input_label = QLabel(label)
        input_label.setStyleSheet("color: white;")
        container_layout.addWidget(input_label)

        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        container_layout.addWidget(input_field)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Zrušit")
        StyleHelper.apply_button_style(ok_button)
        StyleHelper.apply_button_style(cancel_button)

        ok_button.clicked.connect(lambda: dialog.accept() if input_field.text() else None)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        container_layout.addLayout(button_layout)

        main_layout.addWidget(container)
        dialog.resize(400, 200)

        if dialog.exec_() == QDialog.Accepted:
            return input_field.text()
        return None


    
    @staticmethod
    def create_message_box(title, text, icon_type="info", parent=None):
        dialog = QDialog(parent)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        StyleHelper.make_draggable(dialog)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Použití FramedRoundedWidget
        container = FramedRoundedWidget(color="#2B2B2B", border_color="#555555", border_width=3, border_radius=15)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        header = StyleHelper.setup_header(
            title,
            container,
            on_minimize=dialog.showMinimized,
            on_close=dialog.reject
        )
        container_layout.addWidget(header)

        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white;")
        container_layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        StyleHelper.apply_button_style(ok_button)

        cancel_button = None
        if icon_type == "question":
            cancel_button = QPushButton("Zrušit")
            StyleHelper.apply_button_style(cancel_button)
            cancel_button.clicked.connect(dialog.reject)

        ok_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        if cancel_button:
            button_layout.addWidget(cancel_button)

        container_layout.addLayout(button_layout)
        main_layout.addWidget(container)

        dialog.setMinimumWidth(400)
        if dialog.exec_() == QDialog.Accepted:
            return QDialog.Accepted
        return QDialog.Rejected


    
    @staticmethod
    def create_external_window(parent=None, title="Externí okno"):
        dialog = QDialog(parent)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)  # Bez okrajů
        dialog.setAttribute(Qt.WA_TranslucentBackground)  # Průhledné pozadí
        StyleHelper.make_draggable(dialog)  # Přetahování okna

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Žádné okraje

        # Použití RoundedWidget
        container = RoundedWidget(color="#353535")  # Zaoblené šedé pozadí
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        # Hlavička
        header = StyleHelper.setup_header(
            title,
            container,
            on_minimize=dialog.showMinimized,
            on_close=dialog.reject
        )
        container_layout.addWidget(header)

        # Obsah
        label = QLabel("Toto je obsah externího okna")
        label.setStyleSheet("color: white;")
        button = QPushButton("Zavřít")
        StyleHelper.apply_button_style(button)
        button.clicked.connect(dialog.close)

        container_layout.addWidget(label)
        container_layout.addWidget(button)
        main_layout.addWidget(container)

        dialog.resize(400, 300)
        return dialog
    
    @staticmethod
    def make_draggable(widget):
        widget.dragging = False
        widget.offset = QPoint()

        def mouse_press_event(event):
            if event.button() == Qt.LeftButton:
                widget.dragging = True
                widget.offset = event.pos()

        def mouse_move_event(event):
            if widget.dragging:
                widget.move(event.globalPos() - widget.offset)

        def mouse_release_event(event):
            if event.button() == Qt.LeftButton:
                widget.dragging = False

        widget.mousePressEvent = mouse_press_event
        widget.mouseMoveEvent = mouse_move_event
        widget.mouseReleaseEvent = mouse_release_event

    @staticmethod
    def setup_header(title, parent_widget, on_minimize, on_close):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)

        minimize_btn = QPushButton("_")
        minimize_btn.setFixedSize(25, 25)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FFA500;
            }
        """)
        minimize_btn.clicked.connect(on_minimize)

        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FF4444;
            }
        """)
        close_btn.clicked.connect(on_close)

        header_layout.addWidget(title_label, stretch=1, alignment=Qt.AlignTop)
        header_layout.addWidget(minimize_btn, alignment=Qt.AlignRight | Qt.AlignTop)
        header_layout.addWidget(close_btn, alignment=Qt.AlignRight | Qt.AlignTop)

        return header

    @staticmethod
    def apply_text_widget_style(
        widget,
        frame_color="#666666",
        background_color="#353535",
        text_color="white",
        font_family="Arial",
        font_size=10,
        bold=False,
        italic=False,
        border_radius=15,
        border_width=2,
        padding=15,
        label_color="black",        # Barva textu popisku
        label_font_size=10,         # Velikost písma popisku
        label_font_family="Arial",  # Font popisku
        label_bold=True,            # Tučný popisek
        label_italic=False          # Kurzíva popisku
    ):
        """
        Aplikuje jednotný styl pro textové widgety a jejich popisky
        """
        # Nastavení fontu pro widget
        font = QFont(font_family, font_size)
        font.setBold(bold)
        font.setItalic(italic)
        widget.setFont(font)

        # Základní stylesheet pro textové widgety
        base_style = f"""
            border: {border_width}px solid {frame_color};
            border-radius: {border_radius}px;
            background-color: {background_color};
            color: {text_color};
            padding: {padding}px;
        """

        # Styl pro popisky
        label_style = f"""
            QLabel {{
                color: {label_color};
                background-color: transparent;
                font-family: {label_font_family};
                font-size: {label_font_size}pt;
                font-weight: {700 if label_bold else 400};
                font-style: {' italic' if label_italic else 'normal'};
            }}
        """

        # Specifické styly pro jednotlivé typy widgetů
        widget_styles = {
            'QLineEdit': f"QLineEdit {{ {base_style} }}",
            'QTextEdit': f"QTextEdit {{ {base_style} }}",
            'QTextDocument': f"QTextDocument {{ {base_style} }}"
        }

        widget_type = widget.__class__.__name__
        if widget_type in widget_styles:
            widget.setStyleSheet(widget_styles[widget_type])

        # Pro QTextDocument je potřeba dodatečné nastavení
        if widget_type == 'QTextDocument':
            widget.setDefaultFont(font)
            widget.setDefaultStyleSheet(widget_styles[widget_type])

        return widget, label_style
    
    # Příklad použití:
        """
        from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit, QWidget, QVBoxLayout

        app = QApplication([])
        window = QWidget()
        layout = QVBoxLayout()

        # Vytvoření widgetů s popisky - vše se styluje automaticky
        name_input = LabeledWidget("Jméno:", QLineEdit())
        email_input = LabeledWidget("Email:", QLineEdit())
        notes_input = LabeledWidget("Poznámky:", QTextEdit(), label_position="top")

        layout.addWidget(name_input)
        layout.addWidget(email_input)
        layout.addWidget(notes_input)

        window.setLayout(layout)
        window.show()
        app.exec_()
        """
    @staticmethod
    def create_labeled_input(label_text, placeholder_text, multiline=False, required=True):
        """
        Vytvoří label a input pole s daným nastavením
        """
        label = QLabel(label_text)
        
        # Vytvoření správného typu input pole
        if multiline:
            input_field = QTextEdit()
            input_field.setFixedHeight(120)
            input_field.setPlaceholderText(placeholder_text)
            input_field.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            input_field = QLineEdit()
            input_field.setFixedHeight(50)
            input_field.setPlaceholderText(placeholder_text)
        
        # Aplikace stylu na vstupní pole
        widget, _ = StyleHelper.apply_text_widget_style(input_field)
        
        # Stylování labelu
        label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-size: 10pt;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
        """)
        
        input_field.setProperty("required", required)
        
        return label, input_field
    
    @staticmethod
    def create_floating_value_slider(orientation=Qt.Horizontal):
        """
        Vytvoří slider s plovoucí hodnotou nad posuvníkem.
        
        Args:
            orientation: Qt.Horizontal nebo Qt.Vertical
        
        Returns:
            QWidget s integrovaným sliderem a hodnotou
        """
        slider_widget = QWidget()
        layout = QVBoxLayout(slider_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        value_label = QLabel()
        value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)

        slider = QSlider(orientation)
        StyleHelper.apply_slider_style(slider)

        slider.valueChanged.connect(lambda value: value_label.setText(str(value)))
        
        layout.addWidget(value_label)
        layout.addWidget(slider)
        
        # Přidání metod pro kompatibilitu s QSlider
        slider_widget.slider = slider
        slider_widget.setValue = slider.setValue
        slider_widget.value = slider.value
        slider_widget.valueChanged = slider.valueChanged
        slider_widget.setRange = slider.setRange
        
        return slider_widget
    
     # # # # # # # #
     # # # # # # # #
    
    @staticmethod
    def create_styled_dialog(title, content_widget=None, parent=None, min_width=400, min_height=200):
        """
        Vytvoří standardně stylované dialogové okno.
        
        Args:
            title: Titulek dialogu
            content_widget: Widget s obsahem dialogu (QWidget nebo None)
            parent: Rodičovské okno (QWidget nebo None)
            min_width: Minimální šířka dialogu (int)
            min_height: Minimální výška dialogu (int)
        
        Returns:
            Tuple[QDialog, QVBoxLayout]: Dialog a layout pro přidání obsahu
        """
        dialog = QDialog(parent)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        StyleHelper.make_draggable(dialog)  # Přidání možnosti přetahování
        
        # Hlavní layout
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Kontejner s rámečkem
        container = FramedRoundedWidget(
            color="#2B2B2B", 
            border_color="#555555",
            border_width=3,
            border_radius=15
        )
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Hlavička
        header = StyleHelper.setup_header(
            title,
            container,
            on_minimize=dialog.showMinimized,
            on_close=dialog.reject
        )
        container_layout.addWidget(header)
        
        # Přidání obsahu, pokud byl dodán
        if content_widget:
            container_layout.addWidget(content_widget)
        
        # Nastavení minimální velikosti
        dialog.setMinimumSize(min_width, min_height)
        
        main_layout.addWidget(container)
        
        return dialog, container_layout

    @staticmethod
    def create_styled_message_dialog(title, message, icon_type="info", parent=None, buttons=None):
        """
        Vytvoří stylované dialogové okno se zprávou.
        
        Args:
            title: Titulek dialogu
            message: Text zprávy
            icon_type: Typ ikony ("info", "warning", "error", "question")
            parent: Rodičovské okno
            buttons: List tuple (text_tlačítka, callback_funkce) nebo None pro standardní OK
        
        Returns:
            QDialog.Accepted nebo QDialog.Rejected
        """
        # Vytvoření obsahu
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Text zprávy
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white;")
        content_layout.addWidget(message_label)
        
        # Tlačítka
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if not buttons:
            # Standardní tlačítka podle typu
            if icon_type == "question":
                buttons = [
                    ("OK", QDialog.Accepted),
                    ("Zrušit", QDialog.Rejected)
                ]
            else:
                buttons = [("OK", QDialog.Accepted)]
        
        for btn_text, callback in buttons:
            btn = QPushButton(btn_text)
            StyleHelper.apply_button_style(btn)
            if callable(callback):
                btn.clicked.connect(callback)
            else:
                btn.clicked.connect(lambda checked, code=callback: dialog.done(code))
            button_layout.addWidget(btn)
        
        content_layout.addLayout(button_layout)
        
        # Vytvoření dialogu
        dialog, _ = StyleHelper.create_styled_dialog(title, content, parent)
        
        return dialog.exec_()

    @staticmethod
    def create_styled_input_dialog(title, label_text, parent=None, default_text=""):
        """
        Vytvoří stylované dialogové okno pro vstup textu.
        
        Args:
            title: Titulek dialogu
            label_text: Text popisku pro vstupní pole
            parent: Rodičovské okno
            default_text: Výchozí text v poli
        
        Returns:
            str nebo None: Zadaný text nebo None při zrušení
        """
        # Vytvoření obsahu
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Popisek
        label = QLabel(label_text)
        label.setStyleSheet("color: white;")
        content_layout.addWidget(label)
        
        # Vstupní pole
        input_field = QLineEdit(default_text)
        StyleHelper.apply_text_widget_style(input_field)
        content_layout.addWidget(input_field)
        
        # Tlačítka
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Zrušit")
        StyleHelper.apply_button_style(ok_button)
        StyleHelper.apply_button_style(cancel_button)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        content_layout.addLayout(button_layout)
        
        # Vytvoření dialogu
        dialog, _ = StyleHelper.create_styled_dialog(title, content, parent)
        
        # Připojení signálů
        ok_button.clicked.connect(lambda: dialog.accept() if input_field.text() else None)
        cancel_button.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QDialog.Accepted:
            return input_field.text()
        return None

class SearchManager:
    """
    Třída pro správu vyhledávání v aplikaci.
    Poskytuje metody pro různé typy vyhledávání a zpracování výsledků.
    """
    def __init__(self, db_path='publications.db'):
        self.db_path = db_path
        # Cache pro optimalizaci vyhledávání
        self._title_cache = {}
        self._description_cache = {}
        self._pdf_cache = {}

    def search_by_title(self, query):
        """Vyhledávání podle názvu publikace"""
        print(f"Searching titles for: {query}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, author, year
            FROM publications
            WHERE LOWER(title) LIKE LOWER(?)
        """, (f'%{query}%',))
        
        results = cursor.fetchall()
        conn.close()

        print(f"Found {len(results)} matches in titles")
        
        # Přidání kontextu z popisu pro každý výsledek
        extended_results = []
        for result in results:
            pub_id = result[0]
            desc_file = f"publications/{pub_id}/description.txt"
            context = None
            
            if os.path.exists(desc_file):
                try:
                    with open(desc_file, 'r', encoding='utf-8') as f:
                        description = f.read()
                        if description:
                            context = self._create_context_snippet(description, query)
                except UnicodeDecodeError:
                    with open(desc_file, 'r', encoding='windows-1250') as f:
                        description = f.read()
                        if description:
                            context = self._create_context_snippet(description, query)
            
            extended_results.append((*result, context))

        return extended_results

    def search_by_description(self, query):
        """Vyhledávání v popisech publikací"""
        print(f"Searching descriptions for: {query}")
        results = []
        for pub_id in self._get_all_publication_ids():
            desc_file = f"publications/{pub_id}/description.txt"
            if os.path.exists(desc_file):
                try:
                    with open(desc_file, 'r', encoding='utf-8') as f:
                        description = f.read()
                except UnicodeDecodeError:
                    with open(desc_file, 'r', encoding='windows-1250') as f:
                        description = f.read()
                
                if query.lower() in description.lower():
                    snippet = self._create_context_snippet(description, query)
                    pub_info = self._get_publication_info(pub_id)
                    if pub_info:
                        results.append((*pub_info, snippet))
        
        print(f"Found {len(results)} matches in descriptions")
        return results

    def search_in_pdf(self, query):
        """
        Vylepšená verze vyhledávání v PDF s lepším debugováním a ošetřením chyb.
        """
        results = []
        print(f"Starting PDF search for query: {query}")
        
        # Získání všech ID publikací
        publication_ids = self._get_all_publication_ids()
        print(f"Found {len(publication_ids)} publications to search")
        
        for pub_id in publication_ids:
            pdf_file = self._find_pdf_file(pub_id)
            if pdf_file:
                print(f"Processing PDF file: {pdf_file}")
                try:
                    with open(pdf_file, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        total_pages = len(pdf_reader.pages)
                        print(f"PDF has {total_pages} pages")
                        
                        for page_num in range(total_pages):
                            try:
                                text = pdf_reader.pages[page_num].extract_text()
                                if text and query.lower() in text.lower():
                                    snippet = self._create_context_snippet(text, query)
                                    pub_info = self._get_publication_info(pub_id)
                                    if pub_info:
                                        print(f"Found match in publication {pub_id} on page {page_num + 1}")
                                        results.append((*pub_info, page_num + 1, snippet))
                            except Exception as e:
                                print(f"Error extracting text from page {page_num}: {e}")
                                continue
                                
                except Exception as e:
                    print(f"Error processing PDF {pdf_file}: {e}")
                    continue
                
        print(f"PDF search completed. Found {len(results)} results")
        return results

    def _get_all_publication_ids(self):
        """Získá ID všech publikací z databáze."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM publications")
        ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ids

    def _get_publication_info(self, pub_id):
        """Získá základní informace o publikaci."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, author, year
            FROM publications
            WHERE id = ?
        """, (pub_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def _find_pdf_file(self, pub_id):
        """
        Vylepšená verze hledání PDF souboru s lepším ošetřením cest.
        """
        # Získání absolutní cesty k adresáři publications
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pub_dir = os.path.join(base_dir, "publications", str(pub_id))
        
        print(f"Checking for PDF in directory: {pub_dir}")
        
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(pub_dir, file)
                    print(f"Found PDF file: {pdf_path}")
                    return pdf_path
                    
        print(f"No PDF file found for publication {pub_id}")
        return None

    def _create_context_snippet(self, text, query, context_size=50):
        """
        Vytvoří výňatek textu s zvýrazněním nalezeného výrazu.
        
        Args:
            text (str): Prohledávaný text
            query (str): Hledaný výraz
            context_size (int): Počet znaků před a za nalezeným výrazem
            
        Returns:
            str: Formátovaný výňatek textu s zvýrazněným nálezem
        """
        query_lower = query.lower()
        text_lower = text.lower()
        start_idx = text_lower.find(query_lower)
        
        if start_idx == -1:
            return ""
        
        # Výpočet začátku a konce kontextu
        snippet_start = max(0, start_idx - context_size)
        snippet_end = min(len(text), start_idx + len(query) + context_size)
        
        # Příprava částí textu
        prefix = "..." if snippet_start > 0 else ""
        before_match = text[snippet_start:start_idx]
        match = text[start_idx:start_idx + len(query)]  # Původní text (ne převedený na malá písmena)
        after_match = text[start_idx + len(query):snippet_end]
        suffix = "..." if snippet_end < len(text) else ""
        
        # Sestavení výsledku s HTML značkami pro zvýraznění
        highlighted_text = f"{prefix}{before_match}<span style='color: #FFD700; font-weight: bold;'>{match}</span>{after_match}{suffix}"
        
        return highlighted_text
    
    def get_all_pdf_files(self):
        """Získá seznam všech PDF souborů"""
        pdf_files = []
        for pub_id in self._get_all_publication_ids():
            pdf_file = self._find_pdf_file(pub_id)
            if pdf_file:
                pdf_files.append((pub_id, pdf_file))
        return pdf_files

    def search_in_single_pdf(self, pdf_info, query):
        """
        Optimalizované vyhledávání v jednom PDF souboru.
        """
        pub_id, pdf_path = pdf_info
        results = []
        print(f"\nSearching in PDF: {pdf_path}")
        print(f"Looking for query: '{query}'")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    try:
                        text = pdf_reader.pages[page_num].extract_text()
                        if not text:
                            continue
                            
                        text_lower = text.lower()
                        query_lower = query.lower()
                        start_pos = 0
                        
                        while True:
                            pos = text_lower.find(query_lower, start_pos)
                            if pos == -1:
                                break
                                
                            # Vytvoření zvýrazněného kontextu
                            context_size = 50
                            snippet_start = max(0, pos - context_size)
                            snippet_end = min(len(text), pos + len(query) + context_size)
                            
                            before = text[snippet_start:pos]
                            match = text[pos:pos + len(query)]
                            after = text[pos + len(query):snippet_end]
                            
                            prefix = "..." if snippet_start > 0 else ""
                            suffix = "..." if snippet_end < len(text) else ""
                            
                            # Vytvoření HTML pro zvýraznění
                            snippet = f"{prefix}{before}<span style='color: #FFD700; font-weight: bold;'>{match}</span>{after}{suffix}"
                            
                            pub_info = self._get_publication_info(pub_id)
                            if pub_info:
                                results.append((*pub_info, page_num + 1, snippet))
                            
                            start_pos = pos + len(query)
                            
                    except Exception as e:
                        print(f"Error processing page {page_num + 1}: {str(e)}")
                        continue
                    
        except Exception as e:
            print(f"Error opening PDF {pdf_path}: {str(e)}")
            return results

        print(f"Found {len(results)} results in this PDF")
        return results
    
    def _create_context_snippet_from_position(self, text, position, query, context_size=50):
        """
        Vytvoří výňatek textu kolem konkrétní pozice nálezu.
        """
        start = max(0, position - context_size)
        end = min(len(text), position + len(query) + context_size)
        
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        
        # Zvýraznění nalezeného textu pomocí ** pro případné formátování
        before = text[start:position]
        match = text[position:position + len(query)]
        after = text[position + len(query):end]
        
        return f"{prefix}{before}**{match}**{after}{suffix}"

    def clear_cache(self):
        """Vymaže všechny cache"""
        self._title_cache.clear()
        self._description_cache.clear()
        self._pdf_cache.clear()

    def optimize_cache(self):
        """Optimalizuje velikost cache"""
        # Omezení velikosti jednotlivých cache
        max_cache_size = 1000
        
        for cache in [self._title_cache, self._description_cache, self._pdf_cache]:
            while len(cache) > max_cache_size:
                cache.pop(next(iter(cache)))
    
class SearchWidget(QWidget):
    # Signály pro komunikaci s ostatními komponentami
    search_results = pyqtSignal(list, str)  # Výsledky a typ vyhledávání
    search_started = pyqtSignal()  # Signál pro začátek vyhledávání
    search_completed = pyqtSignal()  # Signál pro konec vyhledávání

    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.history_manager = SearchHistoryManager()
        self.search_manager = SearchManager()  # Přidáno
        self.search_history = []
        self.favorite_searches = []
        self.current_search_params = {}
        self.advanced_settings = {}
        
        # Načtení výchozího nastavení
        search_settings = self.settings_manager.get_setting('ui', 'search') if self.settings_manager else {}
        default_checkboxes = search_settings.get('default_checkboxes', {})
        
        self.init_ui()
        
        # Nastavení výchozích hodnot checkboxů
        self.cb_title.setChecked(default_checkboxes.get('title', True))
        self.cb_description.setChecked(default_checkboxes.get('description', False))
        self.cb_pdf.setChecked(default_checkboxes.get('pdf', False))
        
        self.connect_signals()

    def init_ui(self):
        """Inicializace uživatelského rozhraní."""
        # Stylizace checkboxů
        self.checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 2px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
            QCheckBox::indicator:hover {
                border-color: #888888;
            }
        """
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Sekce pro vyhledávání
        search_group = QFrame()
        search_group.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        search_layout = QVBoxLayout(search_group)

        # Pole pro vyhledávání
        self.search_input = QLineEdit()
        StyleHelper.apply_text_widget_style(self.search_input)
        self.search_input.setPlaceholderText("Zadejte hledaný text...")

        # Panel pro tlačítka pokročilých funkcí
        advanced_button_panel = QHBoxLayout()
        

        # Zaškrtávací políčka pro typ vyhledávání
        checkboxes_frame = QFrame()
        checkboxes_layout = QVBoxLayout(checkboxes_frame)
        checkboxes_layout.setSpacing(5)

        self.cb_title = QCheckBox("Název publikace")
        self.cb_description = QCheckBox("Popis publikace")
        self.cb_pdf = QCheckBox("PDF obsah")
        
        # Nastavení stylu pro checkboxy
        for cb in [self.cb_title, self.cb_description, self.cb_pdf]:
            cb.setStyleSheet(self.checkbox_style)

        self.cb_title.setChecked(False)  # Výchozí volba

        checkboxes_layout.addWidget(self.cb_title)
        checkboxes_layout.addWidget(self.cb_description)
        checkboxes_layout.addWidget(self.cb_pdf)

        # Progress bar a status label pro vyhledávání
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #444444;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        self.status_label.hide()

        # Tlačítko pro vyhledávání
        self.search_button = QPushButton("Vyhledat")
        StyleHelper.apply_button_style(self.search_button)

        # Tlačítko pro zrušení vyhledávání
        self.cancel_button = QPushButton("Zrušit")
        StyleHelper.apply_button_style(self.cancel_button)
        self.cancel_button.hide()

        # Layout pro tlačítka vyhledávání
        search_buttons_layout = QHBoxLayout()
        search_buttons_layout.addWidget(self.search_button)
        search_buttons_layout.addWidget(self.cancel_button)

        # Přidání všech komponent do hlavního layoutu vyhledávání
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(checkboxes_frame)
        search_layout.addWidget(self.progress_bar)
        search_layout.addWidget(self.status_label)
        search_layout.addLayout(search_buttons_layout)
        
        # Přidání do hlavního layoutu
        layout.addWidget(search_group)
        
        # Sekce pro zobrazení aktivních kritérií
        advanced_criteria_group = QFrame()
        advanced_criteria_group.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        advanced_criteria_layout = QVBoxLayout(advanced_criteria_group)

        criteria_title = QLabel("Aktivní kritéria pokročilého vyhledávání:")
        criteria_title.setStyleSheet("color: white; font-weight: bold;")
        advanced_criteria_layout.addWidget(criteria_title)

        self.criteria_list = QLabel("Žádná aktivní kritéria")
        self.criteria_list.setWordWrap(True)
        self.criteria_list.setStyleSheet("color: #AAAAAA;")
        advanced_criteria_layout.addWidget(self.criteria_list)

        layout.addWidget(advanced_criteria_group)
        
        layout.addStretch()

    def connect_signals(self):
        """Připojení všech signálů"""
        self.search_button.clicked.connect(self.start_search)
        self.cancel_button.clicked.connect(self.cancel_search)
        # Odstraňte nebo zakomentujte řádky odkazující na neexistující tlačítka
        # self.advanced_search_button.clicked.connect(self.show_advanced_search)
        # self.history_button.clicked.connect(self.show_search_history)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        for cb in [self.cb_title, self.cb_description, self.cb_pdf]:
            cb.stateChanged.connect(self.update_search_params)

    def start_search(self):
        """Spustí vyhledávání s aktuálními parametry"""
        query = self.search_input.text()
        
        if query:
            self.history_manager.add_to_history(self.current_search_params)

        if not any([self.cb_title.isChecked(), self.cb_description.isChecked(), self.cb_pdf.isChecked()]):
            StyleHelper.create_message_box(
                "Upozornění", 
                "Vyberte prosím alespoň jeden typ vyhledávání.", 
                "warning", 
                self
            )
            return

        # Sloučení základních a pokročilých parametrů vyhledávání
        self.current_search_params = {
            'query': query,
            'search_in_title': self.cb_title.isChecked(),
            'search_in_description': self.cb_description.isChecked(),
            'search_in_pdf': self.cb_pdf.isChecked(),
            'timestamp': datetime.now(),
            **self.advanced_settings  # Přidání pokročilých nastavení
        }

        self.search_worker = SearchWorker(self.current_search_params, self.search_manager)
        
        # Připojení signálů
        self.search_worker.progress.connect(self.update_progress)
        self.search_worker.result_found.connect(self.on_result_found)
        self.search_worker.search_completed.connect(self.on_search_completed)
        self.search_worker.status_message.connect(self.update_status)
        
        # Nastavení UI pro vyhledávání
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.show()
        self.search_button.hide()
        self.cancel_button.show()
        self.search_started.emit()
        
        # Spuštění vyhledávání
        self.search_worker.start()
        
    def update_criteria_display(self, settings):
        criteria = []
        
        # Přidání základního filtru
        if self.search_input.text():
            criteria.append(f"Vyhledávaný text: {self.search_input.text()}")
            if self.cb_title.isChecked():
                criteria.append("- v názvech")
            if self.cb_description.isChecked():
                criteria.append("- v popisech")
            if self.cb_pdf.isChecked():
                criteria.append("- v PDF souborech")
                
        # Přidání pokročilých kritérií
        if settings:
            if settings.get('tab') and settings['tab'] != "-- Vyberte záložku --":
                criteria.append(f"Záložka: {settings['tab']}")
                if settings.get('category') and settings['category'] != "-- Vyberte kategorii --":
                    criteria.append(f"Kategorie: {settings['category']}")
                    if settings.get('subcategory') and settings['subcategory'] != "-- Žádná podkategorie --":
                        criteria.append(f"Podkategorie: {settings['subcategory']}")
                        
             # Rozsah let
            if settings.get('year_range'):
                year_from = settings['year_range']['from']
                year_to = settings['year_range']['to']
                criteria.append(f"Rok vydání: {year_from} - {year_to}")
                        
            if settings.get('keywords'):
                criteria.append(f"Klíčová slova: {settings['keywords']}")
                if settings.get('match_type'):
                    criteria.append(f"Způsob shody: {settings['match_type']}")
                
            if settings.get('case_sensitive'):
                criteria.append("Rozlišovat velikost písmen")
            if settings.get('use_regex'):
                criteria.append("Použít regulární výrazy")
            if settings.get('partial_match'):
                criteria.append("Povolit částečnou shodu")
                
            # Maximum výsledků
            if settings.get('max_results') and settings['max_results'] != 100:
                criteria.append(f"Maximum výsledků: {settings['max_results']}")

            self.criteria_list.setText("\n".join(criteria) if criteria else "Žádná aktivní kritéria")
            
             # Zobrazení
            if settings.get('view_type'):
                criteria.append(f"Zobrazení: {settings['view_type']}")

            # Řazení
            if settings.get('sort_by', 'Relevance') != 'Relevance':
                criteria.append(f"Řazení: {settings['sort_by']}")

        self.criteria_list.setText("\n".join(criteria) if criteria else "Žádná aktivní kritéria")

    def cancel_search(self):
        """Zruší probíhající vyhledávání"""
        if hasattr(self, 'search_worker'):
            self.search_worker.cancel()
            self.update_status("Vyhledávání se ukončuje...")

    def update_progress(self, value):
        """Aktualizuje progress bar"""
        self.progress_bar.setValue(value)

    def update_status(self, message):
        """Aktualizuje stavovou zprávu"""
        self.status_label.setText(message)
        self.progress_bar.setFormat(f"%p%")

    def on_result_found(self, result):
        command, data = result
                
        if command == 'view_type':
            if hasattr(self, 'search_results_widget'):
                if data == 'Mřížka':
                    self.search_results_widget.switch_to_grid_view()
                elif data == 'Seznam':
                    self.search_results_widget.switch_to_list_view()
        elif command == 'all':
            self.search_results.emit(data, 'combined')
        
    def on_search_completed(self):
        """Handler pro dokončení vyhledávání"""
        self.progress_bar.hide()
        self.status_label.hide()
        self.cancel_button.hide()
        self.search_button.show()
        self.search_completed.emit()
        
        # Ukončení workeru
        if hasattr(self, 'search_worker'):
            self.search_worker.quit()
            self.search_worker.wait()

    def show_advanced_search(self):
        """Otevře dialog pro pokročilé vyhledávání"""
        dialog = AdvancedSearchWindow(self, category_manager=self.window().category_manager)
        dialog.search_settings_changed.connect(self.apply_advanced_settings)
        dialog.exec_()

    def apply_advanced_settings(self, settings):
        """Aplikuje pokročilá nastavení vyhledávání"""
        self.advanced_settings = settings
        self.update_criteria_display(settings)

    def show_search_history(self):
        """Zobrazí historii vyhledávání"""
        history_window = SearchHistoryWindow(self)
        history_window.search_selected.connect(self.load_search_from_history)
        history_window.exec_()

    def load_search_from_history(self, search_params):
        """Načte vyhledávání z historie"""
        self.search_input.setText(search_params.get('query', ''))
        self.cb_title.setChecked(search_params.get('search_in_title', False))
        self.cb_description.setChecked(search_params.get('search_in_description', False))
        self.cb_pdf.setChecked(search_params.get('search_in_pdf', False))
        self.start_search()

    def on_search_text_changed(self, text):
        """Handler pro změnu textu ve vyhledávacím poli"""
        pass

    def update_search_params(self):
        """Aktualizuje parametry vyhledávání"""
        self.current_search_params.update({
            'search_in_title': self.cb_title.isChecked(),
            'search_in_description': self.cb_description.isChecked(),
            'search_in_pdf': self.cb_pdf.isChecked()
        })

    def clear_search_results(self):
        """Vyčistí výsledky vyhledávání"""
        self.search_input.clear()
        self.update_criteria_display({})  # Reset zobrazení kritérií
        self.search_results.emit([], None)
        
class SearchResultsWidget(QWidget):
    """
    Widget pro zobrazení výsledků vyhledávání.
    Zobrazuje výsledky jako karty s náhledy a základními informacemi.
    """
    result_double_clicked = pyqtSignal(int)  # Předává ID publikace

    def __init__(self, settings_manager=None, parent=None):
        super().__init__(parent)
        self.filters_widget = None
        self.settings_manager = settings_manager
        
        # Konstanty pro velikosti karet v hlavním okně
        self.MAIN_WINDOW_CARD_WIDTH = 680  # Šířka karty pro seznam
        self.MAIN_WINDOW_GRID_CARD_WIDTH = 330  # Šířka karty pro mřížku
        self.CARD_SPACING = 10  # Spacing mezi kartami
        
        self.init_ui()  

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        top_panel = QFrame()
        top_panel.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        top_layout = QVBoxLayout(top_panel)
        top_layout.setSpacing(5)

        view_buttons_row = QHBoxLayout()
        view_buttons_row.addStretch()
        
        self.list_view_btn = QPushButton("Seznam")
        self.grid_view_btn = QPushButton("Mřížka")
        
        for btn in [self.list_view_btn, self.grid_view_btn]:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            StyleHelper.apply_button_style(btn)
            view_buttons_row.addWidget(btn)
        
        view_buttons_row.addStretch()
        self.list_view_btn.setChecked(True)

        info_row = QHBoxLayout()
        
        self.results_count = QLabel("Nalezeno: 0 výsledků")
        self.results_count.setStyleSheet("color: white;")
        
        sort_label = QLabel("Řadit podle:")
        sort_label.setStyleSheet("color: white;")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Relevance", "Názvu", "Roku", "Autora"])
        StyleHelper.apply_small_combobox_style(self.sort_combo)

        info_row.addWidget(self.results_count)
        info_row.addStretch()
        info_row.addWidget(sort_label)
        info_row.addWidget(self.sort_combo)

        top_layout.addLayout(view_buttons_row)
        top_layout.addLayout(info_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(10)
        self.results_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.results_container)

        layout.addWidget(top_panel)
        layout.addWidget(self.scroll_area)

        self.list_view_btn.clicked.connect(self.switch_to_list_view)
        self.grid_view_btn.clicked.connect(self.switch_to_grid_view)

    def show_results(self, results, search_type):
        """Zobrazí výsledky vyhledávání"""
        print(f"\nShowing results of type: {search_type}")
        print(f"Number of results: {len(results)}")
        
        # Kontrola nastavení externího okna
        main_window = self.window()
        if isinstance(main_window, QMainWindow):
            use_external = main_window.settings_manager.get_setting('ui', 'view', 'use_external_window')
            if use_external and not isinstance(self.window(), QDialog):  # Přidaná kontrola typu okna
                main_window.open_search_results_window(results, search_type)
                return

        # Uložení původních výsledků
        self.original_results = results
        self.original_search_type = search_type
        
        # Nastavení výchozího zobrazení podle settings_manager
        if hasattr(self, 'settings_manager'):
            default_view = self.settings_manager.get_setting('ui', 'view', 'default_view', default='Seznam')
            self.current_view = default_view.lower()
            self.list_view_btn.setChecked(default_view == 'Seznam')
            self.grid_view_btn.setChecked(default_view == 'Mřížka')
        
        # Standardní zobrazení
        self._clear_results()
        self.results_count.setText(f"Nalezeno: {len(results)} výsledků")
        
        # Explicitně nastavíme typ zobrazení před zobrazením
        if self.current_view == 'grid':
            QTimer.singleShot(0, self.show_grid_view)  # Použití QTimer pro správné načtení layoutu
        else:
            QTimer.singleShot(0, self.switch_to_list_view)
        
        # Zobrazení filtrů pouze v hlavním okně
        if isinstance(main_window, QMainWindow):
            if results:
                main_window.bottom_right_layout.addWidget(main_window.filters_widget)
                main_window.filters_widget.show()
                main_window.filters_widget.raise_()
            else:
                main_window.filters_widget.hide()
                
    def _display_current_view(self):
        """Zobrazí výsledky podle aktuálně zvoleného pohledu"""
        self._clear_results()
        
        if not hasattr(self, 'original_results') or not self.original_results:
            self.results_count.setText("Nalezeno: 0 výsledků")
            return
                
        self.results_count.setText(f"Nalezeno: {len(self.original_results)} výsledků")
        
        # Zpoždění pro správné načtení layoutu
        if self.current_view == 'list':
            QTimer.singleShot(0, self.switch_to_list_view)
        elif self.current_view == 'grid':
            QTimer.singleShot(0, self.show_grid_view)
                
        self.results_layout.addStretch()
        
        # Force update
        self.update()
        QApplication.processEvents()
                
    def restore_original_results(self):
        """Obnoví původní výsledky vyhledávání"""
        print("\nRestoring original results")
        if hasattr(self, 'original_results'):
            print(f"Found {len(self.original_results)} original results")
            self._display_current_view()
        else:
            print("No original results to restore")
            
    def show_filtered_results(self, results, search_type):
        """Zobrazí filtrované výsledky bez přepsání původních"""
        print(f"\nShowing filtered results: {len(results)}")
        
        # Vyčištění předchozích výsledků
        self._clear_results()
        
        # Aktualizace počtu výsledků
        self.results_count.setText(f"Nalezeno: {len(results)} výsledků")

        # Zobrazení podle aktuálního typu zobrazení
        if self.current_view == 'list':
            for result_data, result_type in results:
                result_card = self._create_result_card(result_data, result_type)
                self.results_layout.addWidget(result_card)
        elif self.current_view == 'grid':
            self.original_results = results  # Dočasná aktualizace pro grid view
            self.show_grid_view()
            self.original_results = getattr(self, '_stored_original_results', [])  # Obnovení původních

        self.results_layout.addStretch()
        
    
    def _get_external_card_width(self, columns):
        """Vypočítá šířku karty pro externí okno na základě počtu sloupců"""
        if self.current_view == 'list':
            return self.MAIN_WINDOW_CARD_WIDTH  # Zachováme stejnou šířku jako v hlavním okně
        else:
            return self.MAIN_WINDOW_GRID_CARD_WIDTH  # Zachováme stejnou šířku jako v hlavním okně

    def _create_external_grid_layout(self):
        """Vytvoří grid layout pro externí okno"""
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setAlignment(Qt.AlignTop)
        
        columns = (self.external_grid_columns if self.current_view == 'grid' 
                else self.external_list_columns)
        
        row = 0
        col = 0
        
        for result_data, result_type in self.original_results:
            if result_type == 'title':
                card = self._create_title_grid_card(result_data)
            elif result_type == 'description':
                card = self._create_description_grid_card(result_data)
            elif result_type == 'pdf':
                card = self._create_pdf_grid_card(result_data)
                
            card_width = self._get_external_card_width(columns)
            card.setFixedWidth(card_width)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        return grid_widget

    def _clear_results(self):
        """Vyčistí všechny výsledky z kontejneru."""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.results_container.update()

    def clear_all_results(self):
        """Kompletně vymaže všechny výsledky a resetuje widget"""
        self._clear_results()
        self.results_count.setText("Nalezeno: 0 výsledků")
        
        # Vymazání uložených výsledků
        if hasattr(self, 'original_results'):
            delattr(self, 'original_results')
        if hasattr(self, 'original_search_type'):
            delattr(self, 'original_search_type')
        
        # Reset zobrazení na Seznam
        self.current_view = 'list'
        self.list_view_btn.setChecked(False)
        self.grid_view_btn.setChecked(False)
        self.list_view_btn.setChecked(True)
        
        # Vyčištění zaškrtávacích polí ve vyhledávání
        main_window = self.window()
        if hasattr(main_window, 'search_widget'):
            main_window.search_widget.cb_title.setChecked(False)
            main_window.search_widget.cb_description.setChecked(False)
            main_window.search_widget.cb_pdf.setChecked(False)

    def _create_result_card(self, result, search_type):
        """Vytvoří kartu s výsledkem vyhledávání."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #888888;
                background-color: #333333;
            }
        """)
        card_layout = QHBoxLayout(card)

        # Náhled publikace
        cover_label = QLabel()
        cover_label.setFixedSize(100, 150)
        pub_id = result[0]  # ID je vždy první položka
        cover_path = self._find_cover_image(pub_id)
        if cover_path:
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(
                80, 120,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            cover_label.setText("Bez\nnáhledu")
            cover_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: #444444;
                    border: 1px solid #666666;
                    border-radius: 5px;
                }
            """)
        cover_label.setAlignment(Qt.AlignCenter)

        # Informace o publikaci
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(5)

        # Název publikace
        title_label = QLabel(str(result[1]))  # Název je druhá položka
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
        """)
        title_label.setWordWrap(True)
        info_layout.addWidget(title_label)

        # Pro všechny typy vyhledávání zobrazíme autora a rok
        if len(result) > 2:  # Kontrola na existenci autora
            author_label = QLabel(f"Autor: {result[2] if result[2] else 'Neznámý'}")
            author_label.setStyleSheet("color: #CCCCCC;")
            info_layout.addWidget(author_label)

        if len(result) > 3:  # Kontrola na existenci roku
            year_label = QLabel(f"Rok vydání: {result[3] if result[3] else 'Neznámý'}")
            year_label.setStyleSheet("color: #CCCCCC;")
            info_layout.addWidget(year_label)

        # Specifické informace podle typu vyhledávání
        if search_type == "description" and len(result) > 4:
            # Pro vyhledávání v popisu zobrazíme nalezený text
            context_header = QLabel("Nalezený text:")
            context_header.setStyleSheet("color: #CCCCCC; font-weight: bold;")
            info_layout.addWidget(context_header)
            
            snippet_label = QLabel()
            snippet_label.setTextFormat(Qt.RichText)  # Pro zvýraznění textu
            snippet_label.setText(str(result[4]))
            snippet_label.setStyleSheet("""
                QLabel {
                    color: #CCCCCC;
                    background-color: #222222;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 2px;
                }
            """)
            snippet_label.setWordWrap(True)
            info_layout.addWidget(snippet_label)
        
        elif search_type == "pdf":
            if len(result) > 4:  # Číslo stránky
                # Vytvoření horizontálního layoutu pro stránku a tlačítko
                page_container = QWidget()
                page_layout = QHBoxLayout(page_container)
                page_layout.setContentsMargins(0, 0, 0, 0)
                page_layout.setSpacing(5)
                
                # Label pro číslo stránky
                page_label = QLabel(f"Strana: {result[4]}")
                page_label.setStyleSheet("color: #CCCCCC;")
                
                # Tlačítko pro otevření PDF
                open_page_button = QPushButton("→")  # Šipka jako ikona
                open_page_button.setFixedSize(25, 25)  # Čtvercové tlačítko
                open_page_button.setCursor(Qt.PointingHandCursor)
                open_page_button.setToolTip("Otevřít PDF na této stránce")
                open_page_button.setStyleSheet("""
                    QPushButton {
                        background-color: #444444;
                        border: 1px solid #666666;
                        color: white;
                        border-radius: 4px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #555555;
                        border-color: #777777;
                    }
                    QPushButton:pressed {
                        background-color: #333333;
                    }
                """)
                
                # Připojení funkce pro otevření PDF na konkrétní stránce
                page_num = result[4]
                open_page_button.clicked.connect(
                    lambda checked, pid=result[0], pnum=page_num: 
                    self.open_pdf_at_page(pid, pnum)
                )
                
                # Přidání komponent do horizontálního layoutu
                page_layout.addWidget(page_label)
                page_layout.addWidget(open_page_button)
                page_layout.addStretch()
                
                info_layout.addWidget(page_container)
                
                if len(result) > 5:  # Kontext
                    context_header = QLabel("Nalezený text:")
                    context_header.setStyleSheet("color: #CCCCCC; font-weight: bold;")
                    info_layout.addWidget(context_header)
                    
                    snippet_label = QLabel()
                    snippet_label.setTextFormat(Qt.RichText)  # Pro zvýraznění textu
                    snippet_label.setText(str(result[5]))
                    snippet_label.setStyleSheet("""
                        QLabel {
                            color: #CCCCCC;
                            background-color: #222222;
                            border-radius: 5px;
                            padding: 5px;
                            margin: 2px;
                        }
                    """)
                    snippet_label.setWordWrap(True)
                    info_layout.addWidget(snippet_label)

        # Přidání komponent do layoutu karty
        card_layout.addWidget(cover_label)
        card_layout.addWidget(info_widget, stretch=1)

        # Nastavení události pro dvojklik
        card.mouseDoubleClickEvent = lambda event: self.result_double_clicked.emit(pub_id)

        return card
    
    def show_grid_view(self):
        """Zobrazí výsledky v mřížce"""
        if not hasattr(self, 'original_results') or not self.original_results:
            return
                    
        self._clear_results()
        
        # Určení počtu sloupců podle typu okna
        columns = 2  # Výchozí hodnota pro hlavní okno
        if hasattr(self, 'is_external_window') and self.is_external_window:
            columns = self.external_grid_columns
        
        # Vytvoření hlavního kontejneru
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Grid layout pro karty
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setAlignment(Qt.AlignTop)
        
        # Rozmístění karet
        row = 0
        col = 0
        
        for result_data, result_type in self.original_results:
            if result_type == 'title':
                card = self._create_title_grid_card(result_data)
            elif result_type == 'description':
                card = self._create_description_grid_card(result_data)
            elif result_type == 'pdf':
                card = self._create_pdf_grid_card(result_data)
                
            card.setFixedWidth(self.MAIN_WINDOW_GRID_CARD_WIDTH)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        main_layout.addWidget(grid_widget)
        main_layout.addStretch()
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(main_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded if hasattr(self, 'is_external_window') else Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #444444;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.results_layout.addWidget(scroll_area)
        
    
    def _create_title_grid_card(self, result):
        """Vytvoří kartu pro výsledek vyhledávání v názvu"""
        card = QFrame()
        card.setMinimumWidth(350)
        card.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #888888;
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Název publikace - bez rámečku, pouze text
        title = QLabel(result[1])
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14pt;
                font-weight: bold;
                background-color: transparent;
                padding: 5px;
            }
        """)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(title)
        
        # Náhled s rámečkem
        cover_frame = QFrame()
        cover_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        cover_frame.setMinimumHeight(200)
        cover_layout = QVBoxLayout(cover_frame)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        
        cover_label = QLabel()
        cover_label.setMinimumSize(200, 280)
        cover_label.setStyleSheet("border: none;")
        
        pub_id = result[0]
        cover_path = self._find_cover_image(pub_id)
        
        if cover_path:
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(
                200, 280,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            cover_label.setText("Bez náhledu")
            cover_label.setStyleSheet("color: white;")
        cover_label.setAlignment(Qt.AlignCenter)
        
        cover_layout.addWidget(cover_label, alignment=Qt.AlignCenter)
        layout.addWidget(cover_frame)
        
        # Informace bez rámečku
        info_container = QWidget()
        info_container.setStyleSheet("background-color: transparent;")
        info_layout = QHBoxLayout(info_container)
        
        author = QLabel(f"Autor: {result[2] if result[2] else 'Neznámý'}")
        year = QLabel(f"Rok: {result[3] if result[3] else 'Neznámý'}")
        
        for label in [author, year]:
            label.setStyleSheet("color: #CCCCCC; background-color: transparent;")
            info_layout.addWidget(label)
                
        layout.addWidget(info_container)
        
        card.mouseDoubleClickEvent = lambda event: self.result_double_clicked.emit(pub_id)
        
        return card
    
    def _create_description_grid_card(self, result):
        """Vytvoří kartu pro výsledek vyhledávání v popisu"""
        card = QFrame()
        card.setMinimumWidth(350)
        card.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #888888;
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Název bez rámečku
        title = QLabel(result[1])
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14pt;
                font-weight: bold;
                background-color: transparent;
                padding: 5px;
            }
        """)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(title)
        
        # Text nálezu s rámečkem
        found_text = QLabel()
        found_text.setTextFormat(Qt.RichText)
        found_text.setText(str(result[4]))
        found_text.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        found_text.setWordWrap(True)
        found_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(found_text)
        
        # Spodní část s náhledem a informacemi
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        
        # Náhled s rámečkem
        cover_frame = QFrame()
        cover_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        frame_layout = QVBoxLayout(cover_frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        
        cover_label = QLabel()
        cover_label.setMinimumSize(100, 150)
        cover_label.setStyleSheet("border: none;")
        
        pub_id = result[0]
        cover_path = self._find_cover_image(pub_id)
        
        if cover_path:
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(
                100, 150,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            cover_label.setText("Bez\nnáhledu")
            cover_label.setStyleSheet("color: white;")
        cover_label.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(cover_label)
        bottom_layout.addWidget(cover_frame)
        
        # Informace bez rámečku
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        
        author = QLabel(f"Autor: {result[2] if result[2] else 'Neznámý'}")
        year = QLabel(f"Rok: {result[3] if result[3] else 'Neznámý'}")
        
        for label in [author, year]:
            label.setStyleSheet("color: #CCCCCC; background-color: transparent;")
            info_layout.addWidget(label)
        
        bottom_layout.addWidget(info_container)
        layout.addWidget(bottom_container)
        
        card.mouseDoubleClickEvent = lambda event: self.result_double_clicked.emit(pub_id)
        
        return card

    def _create_pdf_grid_card(self, result):
        """Vytvoří kartu pro výsledek vyhledávání v PDF"""
        card = QFrame()
        card.setMinimumWidth(350)
        card.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #888888;
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Název bez rámečku
        title = QLabel(result[1])
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14pt;
                font-weight: bold;
                background-color: transparent;
                padding: 5px;
            }
        """)
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(title)
        
        # Text nálezu a číslo stránky s jedním rámečkem
        found_text_container = QFrame()
        found_text_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        found_text_layout = QVBoxLayout(found_text_container)
        found_text_layout.setSpacing(5)
        
        # Informace o stránce
        page_widget = QWidget()
        page_layout = QHBoxLayout(page_widget)
        page_layout.setContentsMargins(0, 0, 0, 5)
        
        page_label = QLabel(f"Strana: {result[4]}")
        page_label.setStyleSheet("color: white;")
        
        open_button = QPushButton("→")
        open_button.setFixedSize(25, 25)
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                border: 2px solid #666666;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        open_button.clicked.connect(lambda: self.open_pdf_at_page(result[0], result[4]))
        
        page_layout.addWidget(page_label)
        page_layout.addWidget(open_button)
        page_layout.addStretch()
        
        found_text_layout.addWidget(page_widget)
        
        # Nalezený text
        found_text = QLabel()
        found_text.setTextFormat(Qt.RichText)
        found_text.setText(str(result[5]))
        found_text.setStyleSheet("color: white;")
        found_text.setWordWrap(True)
        found_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        found_text_layout.addWidget(found_text)
        
        layout.addWidget(found_text_container)
        
        # Spodní část
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        
        # Náhled s rámečkem
        cover_frame = QFrame()
        cover_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        frame_layout = QVBoxLayout(cover_frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        
        cover_label = QLabel()
        cover_label.setMinimumSize(100, 150)
        cover_label.setStyleSheet("border: none;")
        
        pub_id = result[0]
        cover_path = self._find_cover_image(pub_id)
        
        if cover_path:
            pixmap = QPixmap(cover_path)
            cover_label.setPixmap(pixmap.scaled(
                100, 150,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            cover_label.setText("Bez\nnáhledu")
            cover_label.setStyleSheet("color: white;")
        cover_label.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(cover_label)
        bottom_layout.addWidget(cover_frame)
        
        # Informace bez rámečku
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        
        author = QLabel(f"Autor: {result[2] if result[2] else 'Neznámý'}")
        year = QLabel(f"Rok: {result[3] if result[3] else 'Neznámý'}")
        
        for label in [author, year]:
            label.setStyleSheet("color: #CCCCCC; background-color: transparent;")
            info_layout.addWidget(label)
        
        bottom_layout.addWidget(info_container)
        layout.addWidget(bottom_container)
        
        card.mouseDoubleClickEvent = lambda event: self.result_double_clicked.emit(pub_id)
        
        return card
    
    
    def open_pdf_at_page(self, pub_id, page_number):
        """Otevře PDF soubor na konkrétní stránce."""
        pub_dir = f"publications/{pub_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(pub_dir, file)
                    try:
                        # Cesta k SumatraPDF
                        sumatra_path = "C:\\Program Files\\SumatraPDF\\SumatraPDF.exe"
                        if os.path.exists(sumatra_path):
                            import subprocess
                            subprocess.Popen([sumatra_path, '-page', str(page_number), pdf_path])
                        else:
                            os.startfile(pdf_path)
                    except Exception as e:
                        print(f"Chyba při otevírání PDF: {e}")
                        os.startfile(pdf_path)
                    break

    def _find_cover_image(self, pub_id):
        """Najde cestu k náhledu publikace."""
        pub_dir = f"publications/{pub_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.startswith("cover"):
                    return os.path.join(pub_dir, file)
        return None
    
    def switch_to_list_view(self):
        """Přepne na zobrazení seznamu"""
        self.current_view = 'list'
        self.list_view_btn.setChecked(True)
        self.grid_view_btn.setChecked(False)
        
        self._clear_results()
        
        if not hasattr(self, 'original_results'):
            return

        # Určení počtu sloupců podle typu okna
        columns = 1  # Výchozí hodnota pro hlavní okno
        if hasattr(self, 'is_external_window') and self.is_external_window:
            columns = self.external_list_columns
            
        # Vytvoření hlavního kontejneru
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Grid layout pro karty
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setAlignment(Qt.AlignTop)
        
        # Rozmístění karet do sloupců
        row = 0
        col = 0
        
        for result_data, result_type in self.original_results:
            card = self._create_result_card(result_data, result_type)
            card.setFixedWidth(self.MAIN_WINDOW_CARD_WIDTH)
            grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
                
        main_layout.addWidget(grid_widget)
        main_layout.addStretch()
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(main_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded if hasattr(self, 'is_external_window') else Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #444444;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.results_layout.addWidget(scroll_area)
        
    def switch_to_grid_view(self):
        """Přepne na zobrazení mřížky"""
        self.current_view = 'grid'
        self.list_view_btn.setChecked(False)
        self.grid_view_btn.setChecked(True)
        self._display_current_view()
        
    def apply_view_type(self, view_type):
        if view_type == 'Mřížka':
            self.switch_to_grid_view()
        elif view_type == 'Seznam':
            self.switch_to_list_view()
            
    
class SearchFiltersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Hlavní layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # První řádek - nadpis
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        filters_label = QLabel("Filtry výsledků:")
        filters_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(filters_label)
        title_layout.addStretch()
        
        layout.addWidget(title_container)

        # Druhý řádek - pole filtrů
        filters_container = QWidget()
        filters_layout = QHBoxLayout(filters_container)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        filters_layout.setSpacing(10)

        self.year_filter = QLineEdit()
        self.author_filter = QLineEdit()
        StyleHelper.apply_text_widget_style(self.year_filter)
        StyleHelper.apply_text_widget_style(self.author_filter)
        self.year_filter.setPlaceholderText("Filtrovat podle roku...")
        self.author_filter.setPlaceholderText("Filtrovat podle autora...")

        filters_layout.addWidget(self.year_filter)
        filters_layout.addWidget(self.author_filter)

        layout.addWidget(filters_container)

        # Tlačítka pro smazání výsledků a filtrů
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        self.clear_button = QPushButton("Smazat\nvýsledky vyhledávání")
        StyleHelper.apply_button_style(self.clear_button)
        self.clear_button.setStyleSheet(self.clear_button.styleSheet() + """
            QPushButton {
                text-align: center;
            }
        """)

        self.reset_filters_button = QPushButton("Zrušit filtr")
        StyleHelper.apply_button_style(self.reset_filters_button)

        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.reset_filters_button)

        layout.addLayout(buttons_layout)

    
    def connect_signals(self, search_widget):
        """Připojení signálů pro filtry"""
        main_window = self.window()
        if hasattr(main_window, 'search_results_widget'):
            search_results_widget = main_window.search_results_widget

            # Připojení filtrů
            self.year_filter.textChanged.connect(
                lambda: self._apply_filters(search_results_widget))
            self.author_filter.textChanged.connect(
                lambda: self._apply_filters(search_results_widget))

            # Tlačítka
            self.clear_button.clicked.connect(
                lambda: self._clear_results(search_widget))
            self.reset_filters_button.clicked.connect(
                lambda: self._reset_filters(search_results_widget))

    def reset_filters(self):
        """Zruší všechny aktivní filtry a obnoví původní výsledky"""
        # Vyčistit textová pole filtrů
        self.year_filter.clear()
        self.author_filter.clear()

        # Zde byste měli mít nějakou metodu pro obnovení původních výsledků vyhledávání
        # Předpokládám, že máte přístup k widgetu výsledků vyhledávání
        main_window = self.window()
        if hasattr(main_window, 'search_results_widget'):
            search_results_widget = main_window.search_results_widget
            
            # Zde byste měli zavolat metodu, která obnoví původní výsledky
            # Pokud taková metoda neexistuje, budete ji muset implementovat
            # Příklad:
            if hasattr(search_results_widget, 'restore_original_results'):
                search_results_widget.restore_original_results()

    def show(self):
        super().show()
        self.year_filter.clear()
        self.author_filter.clear()

    def _apply_filters(self, results_widget):
        """Aplikuje filtry na výsledky"""
        year_filter = self.year_filter.text().strip()
        author_filter = self.author_filter.text().strip().lower()

        if not hasattr(results_widget, 'original_results'):
            return

        # Když jsou filtry prázdné, obnovíme originální výsledky
        if not year_filter and not author_filter:
            results_widget.restore_original_results()
            return

        filtered_results = []
        for result in results_widget.original_results:
            result_data, result_type = result
            include = True

            # Kontrola roku
            if year_filter and len(result_data) > 3 and result_data[3]:
                if not str(result_data[3]).startswith(year_filter):
                    include = False

            # Kontrola autora
            if include and author_filter and len(result_data) > 2 and result_data[2]:
                if not author_filter in result_data[2].lower():
                    include = False

            if include:
                filtered_results.append(result)

        # Aktualizace zobrazení
        if filtered_results or (not year_filter and not author_filter):
            self._update_results(results_widget, filtered_results)
            
    def _update_results(self, results_widget, filtered_results):
        """Aktualizuje zobrazené výsledky"""
        # Vyčištění aktuálních výsledků
        while results_widget.results_layout.count():
            item = results_widget.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Aktualizace počtu výsledků
        results_widget.results_count.setText(f"Nalezeno: {len(filtered_results)} výsledků")

        # Vytvoření karet pro výsledky
        for result in filtered_results:
            result_card = results_widget._create_result_card(result[0], result[1])
            results_widget.results_layout.addWidget(result_card)

        results_widget.results_layout.addStretch()
            
    def _clear_results(self, search_widget):
        """Smaže výsledky vyhledávání a kritéria"""
        if search_widget:
            search_widget.search_input.clear()
            search_widget.advanced_settings = {}  # Vyčištění pokročilých nastavení
            search_widget.update_criteria_display({})  # Vyčištění zobrazení kritérií
            
            # Vyčištění checkboxů
            search_widget.cb_title.setChecked(False)
            search_widget.cb_description.setChecked(False)
            search_widget.cb_pdf.setChecked(False)
            
            # Vyčištění výsledků
            main_window = self.window()
            if hasattr(main_window, 'search_results_widget'):
                main_window.search_results_widget.clear_all_results()
                
        # Skrytí filtrů
        self.hide()
        
        # Vyčištění filtrů
        self.year_filter.clear()
        self.author_filter.clear()

    def _reset_filters(self, results_widget):
        """Reset filtrů a obnovení původních výsledků"""
        # Blokování signálů
        self.year_filter.blockSignals(True)
        self.author_filter.blockSignals(True)

        # Vyčištění filtrů
        self.year_filter.clear()
        self.author_filter.clear()

        # Obnovení signálů
        self.year_filter.blockSignals(False)
        self.author_filter.blockSignals(False)

        # Obnovení původních výsledků
        if hasattr(results_widget, 'original_results'):
            self._update_results(results_widget, results_widget.original_results)
        
    def setVisible(self, visible):
        """
        Explicitní nastavení viditelnosti widgetu a jeho potomků
        """
        super().setVisible(visible)
        
        # Projdeme všechny potomky a nastavíme jejich viditelnost
        for child in self.findChildren(QWidget):
            child.setVisible(visible)
        
        #Force update
        self.update()

    def on_year_filter_changed(self, text):
        """Handler pro změnu filtru roku"""
        if text:
            self.add_filter('year', text)
        else:
            self.remove_filter('year')
        self.filters_changed.emit()

    def on_author_filter_changed(self, text):
        """Handler pro změnu filtru autora"""
        if text:
            self.add_filter('author', text)
        else:
            self.remove_filter('author')
        self.filters_changed.emit()

    def add_filter(self, filter_type, value):
        """Přidá nový filtr"""
        if filter_type not in self.active_filters:
            display_text = f"{filter_type.capitalize()}: {value}"
            tag = self.add_filter_tag(display_text, filter_type)
            self.active_filters[filter_type] = {
                'value': value,
                'tag': tag
            }

    def add_filter_tag(self, filter_text, filter_type):
        """Přidá nový tag pro aktivní filtr"""
        tag = QFrame()
        tag.setStyleSheet("""
            QFrame {
                background-color: #444444;
                border: 1px solid #666666;
                border-radius: 10px;
                padding: 5px;  # Zvětšení vnitřního odsazení
                margin: 3px 0; # Přidání mezery mezi tagy
            }
        """)
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(5, 2, 5, 2)
        tag_layout.setSpacing(5)

        # Text filtru
        label = QLabel(filter_text)
        label.setStyleSheet("color: white;")
        
        # Tlačítko pro odstranění filtru
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF4444;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_filter(filter_type))
        
        tag_layout.addWidget(label)
        tag_layout.addWidget(remove_btn)
        
        self.active_filters_layout.addWidget(tag)
        return tag

    def remove_filter(self, filter_type):
        """Odstraní filtr"""
        if filter_type in self.active_filters:
            filter_data = self.active_filters[filter_type]
            if filter_data['tag']:
                filter_data['tag'].deleteLater()
            del self.active_filters[filter_type]
            
            # Vyčištění odpovídajícího vstupního pole
            if filter_type == 'year':
                self.year_filter.clear()
            elif filter_type == 'author':
                self.author_filter.clear()
                
            self.filters_changed.emit()

    def clear_all_filters(self):
        """Vyčistí všechny filtry"""
        for filter_type in list(self.active_filters.keys()):
            self.remove_filter(filter_type)
        self.year_filter.clear()
        self.author_filter.clear()

    def apply_filters(self, results):
        """Aplikuje všechny aktivní filtry na výsledky"""
        filtered_results = results

        # Filtr podle roku
        if 'year' in self.active_filters:
            year_filter = self.active_filters['year']['value']
            filtered_results = [r for r in filtered_results 
                              if len(r[0]) > 3 and str(r[0][3]) == year_filter]

        # Filtr podle autora
        if 'author' in self.active_filters:
            author_filter = self.active_filters['author']['value'].lower()
            filtered_results = [r for r in filtered_results 
                              if len(r[0]) > 2 and r[0][2] and 
                              author_filter in r[0][2].lower()]

        return filtered_results
    
import json

class SearchHistoryManager:
    def __init__(self):
        self.history = []
        self.favorites = []
        self.max_history_items = 100
        self.load_saved_data()

    def add_to_history(self, search_params):
        self.history.insert(0, {
            'query': search_params.get('query', ''),
            'search_in_title': search_params.get('search_in_title', False),
            'search_in_description': search_params.get('search_in_description', False),
            'search_in_pdf': search_params.get('search_in_pdf', False),
            'timestamp': datetime.now(),
            'advanced_settings': search_params.get('advanced_settings', {})
        })
        if len(self.history) > self.max_history_items:
            self.history.pop()
        self.save_history()

    def add_to_favorites(self, search_params, name=None):
        """Přidá vyhledávání mezi oblíbené"""
        if not name:
            name = f"Vyhledávání {len(self.favorites) + 1}"
        search_params['name'] = name
        search_params['saved_date'] = datetime.now()
        self.favorites.append(search_params)
        self.save_favorites()

    def remove_from_favorites(self, index):
        """Odstraní vyhledávání z oblíbených"""
        if 0 <= index < len(self.favorites):
            self.favorites.pop(index)
            self.save_favorites()

    def clear_history(self):
        """Vyčistí historii vyhledávání"""
        self.history.clear()
        self.save_history()

    def get_formatted_history(self):
        """Vrátí formátovanou historii pro zobrazení"""
        formatted = []
        for item in self.history:
            formatted.append({
                'text': self._format_search_params(item),
                'timestamp': item['timestamp'],
                'params': item
            })
        return formatted

    def get_formatted_favorites(self):
        """Vrátí formátované oblíbené položky pro zobrazení"""
        return [{'text': item['name'], 'params': item} for item in self.favorites]

    def _format_search_params(self, params):
        """Formátuje parametry vyhledávání do čitelné podoby"""
        parts = []
        if 'query' in params:
            parts.append(f'Text: "{params["query"]}"')
        if 'search_in_title' in params and params['search_in_title']:
            parts.append('Název')
        if 'search_in_description' in params and params['search_in_description']:
            parts.append('Popis')
        if 'search_in_pdf' in params and params['search_in_pdf']:
            parts.append('PDF')
        return ' | '.join(parts)

    def save_history(self):
        try:
            with open('search_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.history, f, default=str)
        except Exception as e:
            print(f"Chyba při ukládání historie: {e}")

    def save_favorites(self):
        """Uloží oblíbené položky do souboru"""
        try:
            with open('search_favorites.json', 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, default=str)
        except Exception as e:
            print(f"Chyba při ukládání oblíbených: {e}")

    def load_saved_data(self):
        """Načte uloženou historii a oblíbené položky"""
        try:
            if os.path.exists('search_history.json'):
                with open('search_history.json', 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            if os.path.exists('search_favorites.json'):
                with open('search_favorites.json', 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
        except Exception as e:
            print(f"Chyba při načítání dat: {e}")

class SearchHistoryWindow(QDialog, StyleHelper):
    search_selected = pyqtSignal(dict)  # Signál pro vybrané vyhledávání

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = SearchHistoryManager()
        self.init_ui()  # Nejprve inicializujte UI
        self.refresh_lists()  # Až poté obnovte seznamy
    
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Historie vyhledávání")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        header = StyleHelper.setup_header(
            "Historie vyhledávání",
            container,
            on_minimize=self.showMinimized,
            on_close=self.close
        )
        header.setStyleSheet("border: none;")

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabBar::tab {
                color: white;
                background-color: #444444;
                padding: 8px 15px;
                border-radius: 5px;
                margin: 2px;
                font-size: 12pt;
            }
            QTabBar::tab:selected {
                background-color: #666666;
            }
        """)

        # Historie - záložka
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        self.history_list = QListWidget()
        StyleHelper.apply_treewidget_style(self.history_list)
        self.history_list.setStyleSheet("""
            QListWidget {
                color: white;
                font-size: 12pt;
                background-color: #353535;
                border: none;
            }
            QListWidget::item {
                color: white;
                padding: 8px;
                font-size: 12pt;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #555555;
            }
        """)
        self.history_list.itemDoubleClicked.connect(self.on_history_item_selected)

        history_buttons_layout = QHBoxLayout()
        clear_history_btn = QPushButton("Vyčistit historii")
        add_to_favorites_btn = QPushButton("Přidat do oblíbených")
        
        for btn in [clear_history_btn, add_to_favorites_btn]:
            StyleHelper.apply_button_style(btn)
            history_buttons_layout.addWidget(btn)

        clear_history_btn.clicked.connect(self.clear_history)
        add_to_favorites_btn.clicked.connect(self.add_current_to_favorites)

        history_layout.addWidget(self.history_list)
        history_layout.addLayout(history_buttons_layout)
        tab_widget.addTab(history_tab, "Historie")

        # Oblíbené - záložka
        favorites_tab = QWidget()
        favorites_layout = QVBoxLayout(favorites_tab)

        self.favorites_list = QListWidget()
        StyleHelper.apply_treewidget_style(self.favorites_list)
        self.favorites_list.setStyleSheet("""
            QListWidget {
                color: white;
                font-size: 12pt;
                background-color: #353535;
                border: none;
            }
            QListWidget::item {
                color: white;
                padding: 8px;
                font-size: 12pt;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #555555;
            }
        """)
        self.favorites_list.itemDoubleClicked.connect(self.on_favorite_item_selected)

        favorites_buttons_layout = QHBoxLayout()
        remove_favorite_btn = QPushButton("Odstranit vybrané")
        rename_favorite_btn = QPushButton("Přejmenovat")
        
        for btn in [remove_favorite_btn, rename_favorite_btn]:
            StyleHelper.apply_button_style(btn)
            favorites_buttons_layout.addWidget(btn)

        remove_favorite_btn.clicked.connect(self.remove_favorite)
        rename_favorite_btn.clicked.connect(self.rename_favorite)

        favorites_layout.addWidget(self.favorites_list)
        favorites_layout.addLayout(favorites_buttons_layout)
        tab_widget.addTab(favorites_tab, "Oblíbené")

        container_layout.addWidget(header)
        container_layout.addWidget(tab_widget)

        main_layout.addWidget(container)

        self.resize(600, 400)
        StyleHelper.make_draggable(self)

    def setup_history_tab(self, tab_widget):
        """Vytvoří záložku s historií vyhledávání"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Seznam historie
        self.history_list = QListWidget()
        StyleHelper.apply_treewidget_style(self.history_list)
        self.history_list.itemDoubleClicked.connect(self.on_history_item_selected)

        # Tlačítka
        buttons_layout = QHBoxLayout()
        clear_history_btn = QPushButton("Vyčistit historii")
        add_to_favorites_btn = QPushButton("Přidat do oblíbených")
        
        for btn in [clear_history_btn, add_to_favorites_btn]:
            StyleHelper.apply_button_style(btn)
            buttons_layout.addWidget(btn)

        clear_history_btn.clicked.connect(self.clear_history)
        add_to_favorites_btn.clicked.connect(self.add_current_to_favorites)

        layout.addWidget(self.history_list)
        layout.addLayout(buttons_layout)
        
        tab_widget.addTab(tab, "Historie")

    def setup_favorites_tab(self, tab_widget):
        """Vytvoří záložku s oblíbenými položkami"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Seznam oblíbených
        self.favorites_list = QListWidget()
        StyleHelper.apply_treewidget_style(self.favorites_list)
        self.favorites_list.itemDoubleClicked.connect(self.on_favorite_item_selected)

        # Tlačítka
        buttons_layout = QHBoxLayout()
        remove_favorite_btn = QPushButton("Odstranit vybrané")
        rename_favorite_btn = QPushButton("Přejmenovat")
        
        for btn in [remove_favorite_btn, rename_favorite_btn]:
            StyleHelper.apply_button_style(btn)
            buttons_layout.addWidget(btn)

        remove_favorite_btn.clicked.connect(self.remove_favorite)
        rename_favorite_btn.clicked.connect(self.rename_favorite)

        layout.addWidget(self.favorites_list)
        layout.addLayout(buttons_layout)
        
        tab_widget.addTab(tab, "Oblíbené")

    def refresh_lists(self):
        """Obnoví seznamy historie a oblíbených"""
        # Historie
        self.history_list.clear()
        for item in self.history_manager.get_formatted_history():
            list_item = QListWidgetItem(item['text'])
            list_item.setData(Qt.UserRole, item['params'])
            self.history_list.addItem(list_item)

        # Oblíbené
        self.favorites_list.clear()
        for item in self.history_manager.get_formatted_favorites():
            list_item = QListWidgetItem(item['text'])
            list_item.setData(Qt.UserRole, item['params'])
            self.favorites_list.addItem(list_item)

    def on_history_item_selected(self, item):
        """Handler pro výběr položky z historie"""
        params = item.data(Qt.UserRole)
        self.search_selected.emit(params)
        self.close()

    def on_favorite_item_selected(self, item):
        """Handler pro výběr oblíbené položky"""
        params = item.data(Qt.UserRole)
        self.search_selected.emit(params)
        self.close()

    def clear_history(self):
        """Vyčistí historii vyhledávání"""
        reply = StyleHelper.create_message_box(
            "Potvrzení",
            "Opravdu chcete vymazat celou historii vyhledávání?",
            "question",
            self
        )
        if reply == QDialog.Accepted:
            self.history_manager.clear_history()
            self.refresh_lists()

    def add_current_to_favorites(self):
        current_item = self.history_list.currentItem()
        if current_item:
            params = current_item.data(Qt.UserRole)
            name = StyleHelper.create_input_dialog(
                "Název oblíbeného vyhledávání",
                "Zadejte název pro toto vyhledávání:",
                self
            )
            if name:
                self.history_manager.add_to_favorites(params, name)
                self.refresh_lists()

    def rename_favorite(self):
        """Přejmenuje oblíbenou položku"""
        current_item = self.favorites_list.currentItem()
        if current_item:
            old_name = current_item.text()
            new_name, ok = QInputDialog.getText(
                self,
                "Přejmenování",
                "Zadejte nový název:",
                QLineEdit.Normal,
                old_name
            )
            if ok and new_name:
                index = self.favorites_list.row(current_item)
                self.history_manager.favorites[index]['name'] = new_name
                self.history_manager.save_favorites()
                self.refresh_lists()

    def remove_favorite(self):
        """Odstraní vybranou oblíbenou položku"""
        current_item = self.favorites_list.currentItem()
        if current_item:
            index = self.favorites_list.row(current_item)
            self.history_manager.remove_from_favorites(index)
            self.refresh_lists()

class AdvancedSearchWindow(QDialog, StyleHelper):
    search_settings_changed = pyqtSignal(dict)  # Signál pro změnu nastavení

    def __init__(self, parent=None, category_manager=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.favorites = []  # Seznam pro oblíbené položky
        self._load_favorites()  # Načtení při startu
        self.setup_ui()  # Změna názvu metody zde
        
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Pokročilé vyhledávání")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #353535;
                border-radius: 15px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        header = StyleHelper.setup_header(
            "Pokročilé vyhledávání",
            container,
            on_minimize=self.showMinimized,
            on_close=self.close
        )
        header.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
            QPushButton {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FFA500;
            }
        """)
        container_layout.addWidget(header)

        # Záložky pro různé sekce nastavení
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }
            QWidget {
                border-radius: 15px;
            }
            QTabBar::tab {
                background-color: #444444;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #666666;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """)

        # Vytvoření záložek
        self.create_range_tab(tab_widget)
        self.create_criteria_tab(tab_widget)
        self.create_method_tab(tab_widget)
        self.create_display_tab(tab_widget)
        self.create_favorites_tab(tab_widget)

        container_layout.addWidget(tab_widget)

        buttons_container = QWidget()
        button_layout = QHBoxLayout(buttons_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.apply_button = QPushButton("Použít nastavení")
        self.save_button = QPushButton("Uložit jako oblíbené")
        self.close_button = QPushButton("Zavřít")

        for btn in [self.apply_button, self.save_button, self.close_button]:
            StyleHelper.apply_button_style(btn)
            button_layout.addWidget(btn)

        self.apply_button.clicked.connect(self.apply_settings)
        self.save_button.clicked.connect(self.save_as_favorite)
        self.close_button.clicked.connect(self.close)

        container_layout.addWidget(buttons_container)
        main_layout.addWidget(container)
                
        self.resize(800, 600)
        StyleHelper.make_draggable(self)

        # Mapování záložek
        self.tab_mapping = {
            "Knihy": "books",
            "Časopisy": "magazines", 
            "Datasheets": "datasheets",
            "Ostatní": "others"
   }

    def save_current_settings(self):
        """Uloží aktuální nastavení"""
        settings = self.collect_settings()
        name, ok = QInputDialog.getText(
            self,
            "Uložit nastavení",
            "Zadejte název pro toto nastavení:"
        )
        if ok and name:
            settings['name'] = name
            settings['saved_date'] = str(datetime.now())
            self._add_favorite_to_list(settings)
            self._save_favorites()

        # Inicializace seznamu oblíbených pokud ještě neexistuje
        if not hasattr(self, '_favorites'):
            self._favorites = []

        # Aktualizace zobrazení
        self.favorites_list.clear()
        for settings in self._favorites:
            self._add_favorite_to_list(settings)
    
    
    def create_criteria_tab(self, tab_widget):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Časový rozsah
        year_group = QGroupBox("Rok vydání")
        year_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
                background: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        year_layout = QVBoxLayout(year_group)
        
        self.use_year_range = QCheckBox("Použít rozsah let")
        self.use_year_range.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 2px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
            QCheckBox::indicator:hover {
                border-color: #888888;
            }
        """)
        year_layout.addWidget(self.use_year_range)
        
        year_range_layout = QHBoxLayout()
        
        from_label = QLabel("Od:")
        to_label = QLabel("Do:")
        from_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")
        to_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")
        
        self.year_from = QSpinBox()
        self.year_to = QSpinBox()
        current_year = datetime.now().year
        
        spinbox_style = """
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
                min-width: 80px;
            }
            QSpinBox::up-button {
                width: 25px;
                height: 15px;
                border-left: 1px solid #666666;
                background: #555555;
                border-top-right-radius: 5px;
            }
            QSpinBox::down-button {
                width: 25px;
                height: 15px;
                border-left: 1px solid #666666;
                background: #555555;
                border-bottom-right-radius: 5px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #666666;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 7px solid white;
            }
            QSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid white;
            }
        """
        
        for spinbox in [self.year_from, self.year_to]:
            spinbox.setRange(1900, current_year)
            spinbox.setValue(current_year)
            spinbox.setStyleSheet(spinbox_style)
            spinbox.setEnabled(False)
        
        self.use_year_range.stateChanged.connect(lambda state: self.year_from.setEnabled(state == Qt.Checked))
        self.use_year_range.stateChanged.connect(lambda state: self.year_to.setEnabled(state == Qt.Checked))
        
        year_range_layout.addWidget(from_label)
        year_range_layout.addWidget(self.year_from)
        year_range_layout.addWidget(to_label)
        year_range_layout.addWidget(self.year_to)
        year_range_layout.addStretch()
        
        year_layout.addLayout(year_range_layout)

        # Textová kritéria
        text_group = QGroupBox("Textová kritéria")
        text_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
                background: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        text_layout = QVBoxLayout(text_group)
        
        keywords_layout = QHBoxLayout()
        keywords_label = QLabel("Klíčová slova:")
        keywords_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")
        
        self.keywords_input = QLineEdit()
        StyleHelper.apply_text_widget_style(self.keywords_input)
        self.keywords_input.setPlaceholderText("Zadejte klíčová slova oddělená čárkou")
        
        keywords_layout.addWidget(keywords_label)
        keywords_layout.addWidget(self.keywords_input)

        self.match_type = QComboBox()
        self.match_type.addItems(["Všechna slova", "Libovolné slovo", "Přesná fráze"])
        StyleHelper.apply_small_combobox_style(self.match_type)

        text_layout.addLayout(keywords_layout)
        text_layout.addWidget(self.match_type)

        layout.addWidget(year_group)
        layout.addWidget(text_group)
        layout.addStretch()
        
        tab_widget.addTab(tab, "Kritéria")
    

    def create_method_tab(self, tab_widget):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Způsob porovnání
        match_group = QGroupBox("Způsob porovnání")
        match_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        match_layout = QVBoxLayout(match_group)

        # Základní checkboxy
        self.case_sensitive = QCheckBox("Rozlišovat velikost písmen")
        self.use_regex = QCheckBox("Použít regulární výrazy") 
        self.partial_match = QCheckBox("Povolit částečnou shodu")
        
        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 2px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
            QCheckBox::indicator:hover {
                border-color: #888888;
            }
        """
        
        for checkbox in [self.case_sensitive, self.use_regex, self.partial_match]:
            checkbox.setStyleSheet(checkbox_style)
            match_layout.addWidget(checkbox)

        limits_group = QGroupBox("Omezení vyhledávání")
        limits_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        limits_layout = QVBoxLayout(limits_group)

        max_results_layout = QHBoxLayout()
        max_results_label = QLabel("Maximum výsledků:")
        max_results_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")

        spinbox_style = """
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
                min-width: 80px;
            }
            QSpinBox::up-button {
                width: 25px;
                height: 15px;
                border-left: 1px solid #666666;
                background: #555555;
                border-top-right-radius: 5px;
            }
            QSpinBox::down-button {
                width: 25px;
                height: 15px;
                border-left: 1px solid #666666;
                background: #555555;
                border-bottom-right-radius: 5px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #666666;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 7px solid white;
            }
            QSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid white;
            }
        """

        self.max_results = QSpinBox()
        self.max_results.setRange(10, 1000)
        self.max_results.setValue(100)
        self.max_results.setStyleSheet(spinbox_style)
        
        max_results_layout.addWidget(max_results_label)
        max_results_layout.addWidget(self.max_results)
        max_results_layout.addStretch()
        limits_layout.addLayout(max_results_layout)

        layout.addWidget(match_group)
        layout.addWidget(limits_group)
        layout.addStretch()
        
        tab_widget.addTab(tab, "Způsob")

    def create_display_tab(self, tab_widget):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        view_group = QGroupBox("Zobrazení výsledků")
        view_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        view_layout = QVBoxLayout(view_group)
        
        view_label = QLabel("Typ zobrazení:")
        view_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")
        
        self.view_type = QComboBox()
        self.view_type.addItems(["Seznam", "Mřížka"])
        StyleHelper.apply_small_combobox_style(self.view_type)
        
        view_layout.addWidget(view_label)
        view_layout.addWidget(self.view_type)

        sort_group = QGroupBox("Řazení")
        sort_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        sort_layout = QVBoxLayout(sort_group)
        
        sort_label = QLabel("Řadit podle:")
        sort_label.setStyleSheet("QLabel { color: white; background: transparent; border: none; }")
        
        self.sort_by = QComboBox()
        self.sort_by.addItems(["Relevance", "Název", "Autor", "Rok"])
        StyleHelper.apply_small_combobox_style(self.sort_by)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_by)

        layout.addWidget(view_group)
        layout.addWidget(sort_group)
        layout.addStretch()
        
        tab_widget.addTab(tab, "Zobrazení")

    def create_favorites_tab(self, tab_widget):
        """Vytvoří záložku pro správu oblíbených vyhledávání"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        self.favorites_list = QListWidget()
        StyleHelper.apply_treewidget_style(self.favorites_list)

        buttons_layout = QHBoxLayout()
        
        # Tlačítka pro správu
        self.delete_selected_btn = QPushButton("Smazat vybrané")
        StyleHelper.apply_button_style(self.delete_selected_btn)
        self.delete_selected_btn.clicked.connect(self.delete_selected_favorite)
        
        buttons_layout.addWidget(self.delete_selected_btn)

        # Načtení uložených oblíbených položek
        if hasattr(self, 'favorites'):
            for settings in self.favorites:
                self._add_favorite_to_list(settings)

        layout.addWidget(self.favorites_list)
        layout.addLayout(buttons_layout)
        
        tab_widget.addTab(tab, "Oblíbené")
        
    def create_range_tab(self, tab_widget):
        """Vytvoří záložku pro nastavení rozsahu vyhledávání"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Záložka
        tab_group = QGroupBox("Záložka")
        tab_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        tab_layout = QVBoxLayout(tab_group)
        
        self.tab_combo = QComboBox()
        self.tab_combo.addItems(["Vše", "Knihy", "Časopisy", "Datasheets", "Ostatní"])
        StyleHelper.apply_small_combobox_style(self.tab_combo)
        self.tab_combo.currentTextChanged.connect(self.on_tab_changed)
        tab_layout.addWidget(self.tab_combo)

        # Kategorie
        category_group = QGroupBox("Kategorie")
        category_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        category_layout = QVBoxLayout(category_group)
        
        self.category_combo = QComboBox()
        self.category_combo.setEnabled(False)
        StyleHelper.apply_small_combobox_style(self.category_combo)
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_combo)

        # Podkategorie
        subcat_group = QGroupBox("Podkategorie")
        subcat_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        subcat_layout = QVBoxLayout(subcat_group)
        
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setEnabled(False)
        StyleHelper.apply_small_combobox_style(self.subcategory_combo)
        subcat_layout.addWidget(self.subcategory_combo)

        layout.addWidget(tab_group)
        layout.addWidget(category_group)
        layout.addWidget(subcat_group)
        layout.addStretch()
        
        tab_widget.addTab(tab, "Rozsah")
        
    def create_criteria_display(self):
        """Vytvoření widgetu pro zobrazení aktivních kritérií"""
        criteria_widget = QFrame()
        criteria_widget.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        
        layout = QVBoxLayout(criteria_widget)
        
        title = QLabel("Aktivní kritéria vyhledávání:")
        title.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title)
        
        self.criteria_list = QLabel("Žádná aktivní kritéria")
        self.criteria_list.setWordWrap(True)
        self.criteria_list.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(self.criteria_list)
        
        return criteria_widget

    def update_criteria_display(self):
        """Aktualizace zobrazení aktivních kritérií"""
        criteria = []
        
        # Rozsah
        if self.tab_combo.currentText() != "-- Vyberte záložku --":
            criteria.append(f"Záložka: {self.tab_combo.currentText()}")
            if self.category_combo.currentText() != "-- Vyberte kategorii --":
                criteria.append(f"Kategorie: {self.category_combo.currentText()}")
                if self.subcategory_combo.currentText() != "-- Žádná podkategorie --":
                    criteria.append(f"Podkategorie: {self.subcategory_combo.currentText()}")
        
        # Kritéria
        if self.year_from.value() != 1900 or self.year_to.value() != datetime.now().year:
            criteria.append(f"Rok: {self.year_from.value()} - {self.year_to.value()}")
        if self.keywords_input.text():
            criteria.append(f"Klíčová slova: {self.keywords_input.text()}")
        if self.match_type.currentIndex() > 0:
            criteria.append(f"Způsob shody: {self.match_type.currentText()}")
        
        # Způsob
        if self.case_sensitive.isChecked():
            criteria.append("Rozlišovat velikost písmen")
        if self.use_regex.isChecked():
            criteria.append("Použít regulární výrazy")
        if self.partial_match.isChecked():
            criteria.append("Povolit částečnou shodu")
        if self.max_results.value() != 100:
            criteria.append(f"Maximum výsledků: {self.max_results.value()}")
        
        # Zobrazení
        if self.view_type.currentIndex() > 0:
            criteria.append(f"Zobrazení: {self.view_type.currentText()}")
        if self.sort_by.currentIndex() > 0:
            criteria.append(f"Řazení: {self.sort_by.currentText()}")
        
        self.criteria_list.setText("\n".join(criteria) if criteria else "Žádná aktivní kritéria")
        
    def save_as_favorite(self):
        """Uloží aktuální nastavení vyhledávání jako oblíbené"""
        settings = self.collect_settings()
        
        # Vytvoření stylizovaného dialogu
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        StyleHelper.make_draggable(dialog)

        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(15, 15, 15, 15)

        container = FramedRoundedWidget(color="#2B2B2B", border_color="#555555", border_width=3, border_radius=15)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)

        header = StyleHelper.setup_header(
            "Uložit nastavení",
            container,
            on_minimize=dialog.showMinimized,
            on_close=dialog.reject
        )
        header.setStyleSheet("border: none;")
        container_layout.addWidget(header)

        input_label = QLabel("Zadejte název pro toto nastavení:")
        input_label.setStyleSheet("color: white; border: none;")

        input_label = QLabel("Zadejte název pro toto nastavení:")
        input_label.setStyleSheet("color: white;")
        container_layout.addWidget(input_label)

        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        container_layout.addWidget(input_field)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Zrušit")
        StyleHelper.apply_button_style(ok_button)
        StyleHelper.apply_button_style(cancel_button)

        ok_button.clicked.connect(lambda: dialog.accept() if input_field.text() else None)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        container_layout.addLayout(button_layout)

        main_layout.addWidget(container)
        dialog.resize(400, 200)

        if dialog.exec_() == QDialog.Accepted and input_field.text():
            settings['name'] = input_field.text()
            settings['saved_date'] = str(datetime.now())
            self._add_favorite_to_list(settings)
            self._save_favorites()

    def on_tab_changed(self, tab_name):
        if tab_name == "Vše":
            self.category_combo.setEnabled(False)
            self.subcategory_combo.setEnabled(False)
            return

        category_type = None
        if tab_name in self.tab_mapping:  # Použijeme tab_mapping pro převod na správný název tabulky
            category_type = self.tab_mapping[tab_name]
        
        if category_type:
            self.category_combo.setEnabled(True)
            self.category_combo.clear()
            self.category_combo.addItem("-- Vyberte kategorii --")
            
            categories = self.category_manager.load_categories(category_type)
            for category in categories:
                self.category_combo.addItem(category['name'])

    def on_category_changed(self, category_name):
        """Handler pro změnu kategorie"""
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("-- Žádná podkategorie --")
        self.subcategory_combo.setEnabled(False)

        if category_name == "-- Vyberte kategorii --":
            return

        # Získání typu kategorie z aktuální záložky
        tab_name = self.tab_combo.currentText()
        category_type = self.tab_mapping.get(tab_name)  # Použití tab_mapping
        
        if category_type:
            categories = self.category_manager.load_categories(category_type)
            selected_category = next(
                (cat for cat in categories if cat['name'] == category_name),
                None
            )
            
            if selected_category and selected_category['subcategories']:
                for _, subcategory_name in selected_category['subcategories']:
                    self.subcategory_combo.addItem(subcategory_name)
                self.subcategory_combo.setEnabled(True)
                
    def collect_settings(self):
        """Shromáždí všechna nastavení do slovníku"""
        settings = {
            'tab': self.tab_combo.currentText(),
            'category': self.category_combo.currentText(),
            'subcategory': self.subcategory_combo.currentText(),
            'keywords': self.keywords_input.text(),
            'match_type': self.match_type.currentText(),
            'case_sensitive': self.case_sensitive.isChecked(),
            'use_regex': self.use_regex.isChecked(),
            'partial_match': self.partial_match.isChecked(),
            'max_results': self.max_results.value(),
            'view_type': self.view_type.currentText(),
            'sort_by': self.sort_by.currentText()
        }

        # Přidání rozsahu let pouze pokud je aktivován
        if self.use_year_range.isChecked():
            settings.update({
                'year_from': self.year_from.value(),
                'year_to': self.year_to.value()
            })

        return settings

    def load_settings(self, settings):
        """Načte nastavení ze slovníku"""
        if not settings:
            return

        # Nastavení záložky a kategorií
        self.tab_combo.setCurrentText(settings.get('tab', 'Vše'))
        if settings.get('category'):
            self.category_combo.setCurrentText(settings['category'])
        if settings.get('subcategory'):
            self.subcategory_combo.setCurrentText(settings['subcategory'])

        # Nastavení časového rozsahu
        self.year_from.setValue(settings.get('year_from', self.year_from.value()))
        self.year_to.setValue(settings.get('year_to', self.year_to.value()))

        # Nastavení textových kritérií
        self.keywords_input.setText(settings.get('keywords', ''))
        self.match_type.setCurrentText(settings.get('match_type', 'Všechna slova'))

        # Nastavení způsobu vyhledávání
        self.case_sensitive.setChecked(settings.get('case_sensitive', False))
        self.use_regex.setChecked(settings.get('use_regex', False))
        self.partial_match.setChecked(settings.get('partial_match', False))
        self.max_results.setValue(settings.get('max_results', 100))

        # Nastavení zobrazení
        self.view_type.setCurrentText(settings.get('view_type', 'Seznam'))
        self.sort_by.setCurrentText(settings.get('sort_by', 'Relevance'))

    def apply_settings(self):
        settings = self.collect_settings()
        filtered_settings = {}
        
        # Filtrování kategorie/podkategorie
        if settings.get('tab') != "-- Vyberte záložku --":
            filtered_settings['tab'] = settings['tab']
            if settings.get('category') != "-- Vyberte kategorii --":
                filtered_settings['category'] = settings['category']
                if settings.get('subcategory') != "-- Žádná podkategorie --":
                    filtered_settings['subcategory'] = settings['subcategory']

        # Rok vydání
        if self.use_year_range.isChecked():
            filtered_settings['year_range'] = {
                'from': self.year_from.value(),
                'to': self.year_to.value()
            }
            filtered_settings['use_year_range'] = True  # Přidáno pro zobrazení v kritériích

        # Klíčová slova a typ shody
        if settings.get('keywords'):
            filtered_settings['keywords'] = settings['keywords']
            filtered_settings['match_type'] = settings['match_type']

        # Způsob vyhledávání
        if settings.get('case_sensitive'):
            filtered_settings['case_sensitive'] = True
        if settings.get('use_regex'):
            filtered_settings['use_regex'] = True
        if settings.get('partial_match'):
            filtered_settings['partial_match'] = True

        # Zobrazení a řazení
        if settings.get('view_type') != 'Seznam':
            filtered_settings['view_type'] = settings['view_type']
        if settings.get('sort_by') != 'Relevance':
            filtered_settings['sort_by'] = settings['sort_by']
            
        # Maximum výsledků
        if self.max_results.value() != 100:
            filtered_settings['max_results'] = self.max_results.value()

        self.current_settings = filtered_settings
        self.search_settings_changed.emit(filtered_settings)
        self.close()

    def _add_favorite_to_list(self, settings):
        item = QListWidgetItem(settings['name'])
        item.setData(Qt.UserRole, settings)
        item.setForeground(QColor("white"))  # Bílé písmo
        font = item.font()
        font.setPointSize(12)  # Větší písmo
        item.setFont(font)
        self.favorites_list.addItem(item)

    def delete_selected_favorite(self):
        current_item = self.favorites_list.currentItem()
        if current_item:
            reply = StyleHelper.create_message_box(
                "Potvrzení", 
                "Opravdu chcete smazat toto nastavení?", 
                "question", 
                self
            )
            if reply == QDialog.Accepted:
                row = self.favorites_list.row(current_item)
                self.favorites_list.takeItem(row)
                self._save_favorites()

    def _save_favorites(self):
        """Uloží oblíbené položky do souboru"""
        favorites_to_save = []
        for i in range(self.favorites_list.count()):
            item = self.favorites_list.item(i)
            favorites_to_save.append(item.data(Qt.UserRole))
        
        try:
            with open('search_favorites_settings.json', 'w', encoding='utf-8') as f:
                json.dump(favorites_to_save, f, default=str)
        except Exception as e:
            print(f"Chyba při ukládání oblíbených nastavení: {e}")

    def _load_favorites(self):
        """Načte oblíbené položky ze souboru"""
        try:
            if os.path.exists('search_favorites_settings.json'):
                with open('search_favorites_settings.json', 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
        except Exception as e:
            print(f"Chyba při načítání oblíbených nastavení: {e}")
            
class SearchWorker(QThread):
    progress = pyqtSignal(int)  # Signál pro průběh (0-100)
    result_found = pyqtSignal(tuple)  # Signál pro nalezený výsledek
    search_completed = pyqtSignal()  # Signál pro dokončení
    status_message = pyqtSignal(str)  # Signál pro stavové zprávy

    def __init__(self, search_params, search_manager):
        super().__init__()
        self.search_params = search_params
        self.search_manager = search_manager
        self.is_cancelled = False
        self._results_cache = {}
        self.total_progress = 0
        self.current_progress = 0

    def run(self):
        """Provede vyhledávání podle zadaných parametrů"""
        try:
            query = self.search_params.get('query', '')
            all_results = []

            # Výpočet celkového počtu kroků
            self.total_steps = 0
            if self.search_params.get('search_in_title'):
                self.total_steps += 1
            if self.search_params.get('search_in_description'):
                self.total_steps += 1
            if self.search_params.get('search_in_pdf'):
                self.total_steps += 1

            self.current_step = 0

            # Získání parametrů filtrování kategorií 
            tab = self.search_params.get('tab')
            category = self.search_params.get('category')
            subcategory = self.search_params.get('subcategory')
            allowed_pub_ids = None

            if tab and category:
                # Připojení k databázi kategorií
                conn = sqlite3.connect('categories.db')
                cursor = conn.cursor()
                
                category_type = {
                    "Knihy": "books",
                    "Časopisy": "magazines", 
                    "Datasheets": "datasheets",
                    "Ostatní": "others"
                }.get(tab)

                if category_type:
                    try:
                        if subcategory:
                            # Získání ID podkategorie
                            cursor.execute("""
                                SELECT id FROM {}_categories 
                                WHERE name = ? AND parent_id IN 
                                    (SELECT id FROM {}_categories WHERE name = ?)
                            """.format(category_type, category_type), (subcategory, category))
                        else:
                            # Získání ID kategorie
                            cursor.execute("""
                                SELECT id FROM {}_categories 
                                WHERE name = ?
                            """.format(category_type), (category,))
                        
                        category_id = cursor.fetchone()
                        
                        if category_id:
                            # Přepnutí na databázi publikací
                            cursor.close()
                            conn.close()
                            conn = sqlite3.connect('publications.db')
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                SELECT id FROM publications
                                WHERE category_id = ? AND category_type = ?
                            """, (category_id[0], category_type))
                            allowed_pub_ids = {row[0] for row in cursor.fetchall()}
                    except Exception as e:
                        print(f"Chyba při hledání kategorie: {e}")
                    finally:
                        cursor.close()
                        conn.close()

            # Vyhledávání v názvech
            if self.search_params.get('search_in_title'):
                self.status_message.emit("Vyhledávání v názvech...")
                print("\nSearching in titles")
                title_results = self.search_manager.search_by_title(query)
                if title_results:
                    filtered_results = [r for r in title_results 
                                        if not allowed_pub_ids or r[0] in allowed_pub_ids]
                    for result in filtered_results:
                        all_results.append((result, 'title'))
                self.current_step += 1
                self.update_progress()

            # Vyhledávání v popisech
            if self.search_params.get('search_in_description'):
                self.status_message.emit("Vyhledávání v popisech...")
                print("\nSearching in descriptions")
                desc_results = self.search_manager.search_by_description(query)
                if desc_results:
                    filtered_results = [r for r in desc_results
                                        if not allowed_pub_ids or r[0] in allowed_pub_ids]
                    for result in filtered_results:
                        all_results.append((result, 'description'))
                self.current_step += 1
                self.update_progress()

            # Vyhledávání v PDF
            if self.search_params.get('search_in_pdf'):
                self.status_message.emit("Vyhledávání v PDF souborech...")
                print("\nStarting PDF search")
                pdf_files = self.search_manager.get_all_pdf_files()
                
                if allowed_pub_ids:
                    pdf_files = [(pub_id, path) for pub_id, path in pdf_files 
                                if pub_id in allowed_pub_ids]
                
                for pdf_file in pdf_files:
                    if self.is_cancelled:
                        break
                    
                    results_for_file = self.search_manager.search_in_single_pdf(
                        pdf_file, 
                        query
                    )
                    
                    if results_for_file:
                        for result in results_for_file:
                            all_results.append((result, 'pdf'))

                self.current_step += 1
                self.update_progress()

            # Filtrování podle roku
            if year_range := self.search_params.get('year_range'):
                filtered_results = []
                for result_tuple in all_results:
                    result, result_type = result_tuple
                    try:
                        if isinstance(result[3], (int, str)) and result[3]:
                            year = int(str(result[3]))
                            if year_range['from'] <= year <= year_range['to']:
                                filtered_results.append(result_tuple)
                    except (IndexError, ValueError, TypeError):
                        continue
                all_results = filtered_results
                
            # Aplikování limitu počtu výsledků
            max_results = self.search_params.get('max_results')
            if max_results and isinstance(max_results, int):
                all_results = all_results[:max_results]

             # Nejdřív odešleme všechny výsledky
            if all_results:
                self.result_found.emit(('all', all_results))
                
            # Pak teprve aplikujeme nastavení zobrazení
            if view_type := self.search_params.get('view_type'):
                self.result_found.emit(('view_type', view_type))
                
            # Řazení výsledků
            sort_by = self.search_params.get('sort_by')
            if sort_by:
                if sort_by == 'Název':
                    all_results.sort(key=lambda x: x[0][1])
                elif sort_by == 'Autor':
                    all_results.sort(key=lambda x: x[0][2] or '')
                elif sort_by == 'Rok':
                    all_results.sort(key=lambda x: x[0][3] or 0)

            # Odeslání všech výsledků najednou
            print(f"\nSearch completed. Total results: {len(all_results)}")
            if all_results:
                self.result_found.emit(('all', all_results))

        except Exception as e:
            self.status_message.emit(f"Chyba při vyhledávání: {str(e)}")
            print(f"Chyba vyhledávání: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.search_completed.emit()

    def update_progress(self):
        """Aktualizuje progress bar"""
        if self.total_steps > 0:  # Přidaná kontrola dělení nulou
            progress = int((self.current_step / self.total_steps) * 100)
            self.progress.emit(min(progress, 100))

    def _generate_cache_key(self):
        """Vygeneruje klíč pro cache na základě parametrů vyhledávání"""
        params = sorted(
            (k, v) for k, v in self.search_params.items() 
            if k not in ['timestamp']
        )
        return tuple(params)

    def cancel(self):
        """Zruší probíhající vyhledávání"""
        self.is_cancelled = True

    
class CategoryManager:
    def __init__(self, db_name='categories.db'):
        self.db_name = db_name
        self.init_database()
        self.init_publications_database()
        self.add_sort_order_column()
    
    def init_database(self):
        """Inicializace databáze a vytvoření tabulky pro každý typ publikace"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Vytvoření tabulek pro různé typy publikací
        publication_types = ['books', 'magazines', 'datasheets', 'others']
        
        for pub_type in publication_types:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {pub_type}_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES {pub_type}_categories (id)
                )
            ''')

        conn.commit()
        conn.close()
        
    def add_sort_order_column(self):
        """Přidá sloupec pro řazení do všech tabulek kategorií"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for category_type in ['books', 'magazines', 'datasheets', 'others']:
            try:
                # Kontrola existence sloupce
                cursor.execute(f"PRAGMA table_info({category_type}_categories)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'sort_order' not in columns:
                    cursor.execute(f"""
                        ALTER TABLE {category_type}_categories
                        ADD COLUMN sort_order INTEGER DEFAULT 0
                    """)
                    
                    # Inicializace hodnot
                    cursor.execute(f"""
                        UPDATE {category_type}_categories
                        SET sort_order = (
                            SELECT COUNT(*)
                            FROM {category_type}_categories AS t2
                            WHERE t2.id <= {category_type}_categories.id
                        )
                    """)
                    
                    conn.commit()
                    print(f"Added sort_order column to {category_type}_categories")
                    
            except Exception as e:
                print(f"Error adding sort_order to {category_type}_categories: {str(e)}")
                conn.rollback()
        
        conn.close()
        
    def init_publications_database(self):
        # Vytvoření tabulky pro publikace v samostatné databázi
        pub_conn = sqlite3.connect('publications.db')
        pub_cursor = pub_conn.cursor()

        # Vytvoření tabulky pro publikace, pokud neexistuje
        pub_cursor.execute('''
            CREATE TABLE IF NOT EXISTS publications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                year INTEGER,
                category_id INTEGER,
                category_type TEXT
            )
        ''')

        pub_conn.commit()
        pub_conn.close()
    
    def load_categories(self, category_type):
        """Načte kategorie pro daný typ publikace"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Načtení hlavních kategorií
        cursor.execute(f"SELECT id, name FROM {category_type}_categories WHERE parent_id IS NULL")
        categories = cursor.fetchall()
        
        result = []
        for cat_id, cat_name in categories:
            # Načtení podkategorií
            cursor.execute(f"SELECT id, name FROM {category_type}_categories WHERE parent_id = ?", (cat_id,))
            subcategories = cursor.fetchall()
            
            result.append({
                'id': cat_id,
                'name': cat_name,
                'subcategories': subcategories
            })
        
        conn.close()
        return result
    
    def add_category(self, category_type, name, parent_id=None):
        """Přidá novou kategorii"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(f"INSERT INTO {category_type}_categories (name, parent_id) VALUES (?, ?)", 
                      (name, parent_id))
        new_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return new_id
    
    def delete_category(self, category_type, category_id):
        """Smaže kategorii a její podkategorie"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Nejprve smažeme všechny podkategorie
        cursor.execute(f"DELETE FROM {category_type}_categories WHERE parent_id = ?", (category_id,))
        # Pak smažeme samotnou kategorii
        cursor.execute(f"DELETE FROM {category_type}_categories WHERE id = ?", (category_id,))
        
        conn.commit()
        conn.close()
    
    def get_category_id(self, category_type, name):
        """Získá ID kategorie podle jejího jména"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT id FROM {category_type}_categories WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None    
    
class ButtonTabs(QWidget):
    # Signály pro komunikaci s hlavním oknem
    tab_changed = pyqtSignal(int)          # Signál pro změnu indexu záložky
    tab_name_changed = pyqtSignal(str)     # Signál pro změnu názvu záložky

    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_manager = CategoryManager()
        self.init_ui()
        self.set_active_tab(0)  # Nastaví první záložku jako aktivní

    def init_ui(self):
        # Hlavní layout pro celý widget
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Kontejner pro tlačítka
        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        self.button_layout.setSpacing(10)
        self.button_layout.setContentsMargins(10, 5, 10, 5)
        self.button_layout.setAlignment(Qt.AlignCenter)

        # Skupina tlačítek zajišťující, že může být vybrána jen jedna záložka
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_tab_change)

        # Přidání kontejneru s tlačítky do hlavního layoutu
        layout.addWidget(button_container, alignment=Qt.AlignCenter)

        # Vytvoření záložek
        self.add_tabs()

    def add_tabs(self):
        # Mapování názvů záložek na typy kategorií v databázi
        self.tab_mapping = {
            "Knihy": "books",
            "Časopisy": "magazines",
            "Datasheets": "datasheets",
            "Ostatní": "others",
            "Vyhledávání": None,
            "Nastavení": None
        }
        
        # Vytvoření tlačítka pro každou záložku
        for tab_name in self.tab_mapping.keys():
            self.add_tab(tab_name)
            
    def is_content_tab(self, tab_name):
        """Kontroluje, zda záložka má zobrazovat standardní obsah."""
        return tab_name in ["Knihy", "Časopisy", "Datasheets", "Ostatní"]

    def add_tab(self, title):
        # Vytvoření a nastavení jednoho tlačítka záložky
        button = QPushButton(title)
        button.setCheckable(True)
        button.setFixedSize(120, 30)
        StyleHelper.apply_button_style(button)
        self.button_group.addButton(button)
        self.button_layout.addWidget(button)

    def _on_tab_change(self, button):
        # Handler pro změnu záložky
        index = self.button_group.buttons().index(button)
        self.tab_changed.emit(index)
        self.tab_name_changed.emit(button.text())

    def set_active_tab(self, index):
        """Nastaví konkrétní záložku jako aktivní"""
        if 0 <= index < len(self.button_group.buttons()):
            button = self.button_group.buttons()[index]
            button.setChecked(True)
            tab_name = button.text()
            self.tab_name_changed.emit(tab_name)

    def get_current_category_type(self):
        """Vrátí typ kategorie pro aktuální záložku"""
        current_button = self.button_group.checkedButton()
        if current_button:
            tab_name = current_button.text()
            return self.tab_mapping.get(tab_name)
        return None
    
class ControlWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dragging = False
        self.offset = QPoint()
        self.is_dark_theme = True  # Výchozí tmavé téma

        self.setObjectName("ControlWidget")
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Nastavení průhledného pozadí pro ControlWidget
        self.setStyleSheet("background-color: transparent;")

        # Vytvoření layoutu pro tlačítka
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Tlačítko pro přepínání tématu
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(25, 25)
        self.theme_btn.setStyleSheet("background: none; border: none; color: white;")
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Tlačítko pro minimalizaci
        min_btn = QPushButton("—")
        min_btn.setFixedSize(25, 25)
        min_btn.setStyleSheet("""
            background: none;
            border: none;
            color: white;  /* Nastavení stejné barvy jako tlačítko pro zavření */
        """)
        min_btn.clicked.connect(self.main_window.showMinimized)

        # Tlačítko pro zavření
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet("""
            background: none;
            border: none;
            color: white;  /* Barva tlačítka zavření */
        """)
        close_btn.clicked.connect(self.main_window.close)

        # Přidání tlačítek do layoutu
        layout.addWidget(self.theme_btn)
        layout.addWidget(min_btn)
        layout.addWidget(close_btn)

        self.setFixedSize(layout.sizeHint())

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.theme_btn.setText("🌙" if self.is_dark_theme else "☀️")
        # self.main_window.set_theme(self.is_dark_theme)

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
    """Widget s možností zaoblených rohů a barvy pozadí."""
    def __init__(self, color="#ffffff"):
        super().__init__()
        self.color = color
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        rect_f = QRectF(rect)  # Převod QRect na QRectF
        path = QPainterPath()
        path.addRoundedRect(rect_f, 15, 15)

        painter.setPen(Qt.NoPen)
        painter.fillPath(path, QColor(self.color))
        
class FramedRoundedWidget(QWidget):
    """Widget s možností zaoblených rohů, barvy pozadí a viditelného rámečku."""
    def __init__(self, color="#ffffff", border_color="#666666", border_width=2, border_radius=15):
        super().__init__()
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Rámeček
        rect = QRectF(self.rect().adjusted(self.border_width, self.border_width, -self.border_width, -self.border_width))
        path = QPainterPath()
        path.addRoundedRect(rect, self.border_radius, self.border_radius)

        # Barva pozadí
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Barva rámečku
        pen = QPen(QColor(self.border_color))  # Použití QPen pro definici stylu pera
        pen.setWidth(self.border_width)       # Nastavení šířky rámečku
        painter.setPen(pen)                   # Aplikace pera na malíře
        painter.drawPath(path)                # Vykreslení rámečku
        
class PublicationItem(QtGui.QStandardItem):
    """
    Třída reprezentující jednu publikaci v seznamu.
    Obsahuje informace o obrázku a názvu publikace.
    """
    def __init__(self, image_path, title, pub_id):
        super().__init__()
        self.image_path = image_path
        self.title = title
        self.full_title = title
        self.truncated_title = title[:20] + "..." if len(title) > 20 else title
        
        self.setData(self.truncated_title, QtCore.Qt.DisplayRole)
        self.setData(self.full_title, QtCore.Qt.ToolTipRole)
        self.setData(pub_id, QtCore.Qt.UserRole)  # Uložení ID publikace
        
        # Nastavení základních dat pro zobrazení
        self.setData(self.truncated_title, QtCore.Qt.DisplayRole)  # Zobrazovaný text
        self.setData(self.full_title, QtCore.Qt.ToolTipRole)      # Text tooltipu
        
        # Načtení a nastavení náhledového obrázku
        self.original_pixmap = load_scaled_image(image_path)
        if self.original_pixmap and not self.original_pixmap.isNull():
            self.setData(self.original_pixmap, QtCore.Qt.DecorationRole)  # Obrázek pro zobrazení
        else:
            # Vytvoření placeholder pixmapu pro chybějící obrázky
            placeholder = QtGui.QPixmap(100, 150)
            placeholder.fill(QtGui.QColor(200, 200, 200))  # Šedé pozadí
            self.setData(placeholder, QtCore.Qt.DecorationRole)
        
        # Nastavení velikosti položky v seznamu
        self.setSizeHint(QtCore.QSize(120, 180))

@lru_cache(maxsize=1000)
def load_scaled_image(image_path, width=100, height=150):
    """
    Cachovaná funkce pro načítání a škálování obrázků.
    
    Args:
        image_path (str): Cesta k obrázku
        width (int): Požadovaná šířka obrázku
        height (int): Požadovaná výška obrázku
    
    Returns:
        QPixmap: Škálovaný obrázek nebo prázdný QPixmap pokud obrázek neexistuje
    """
    if os.path.exists(image_path):
        return QtGui.QPixmap(image_path).scaled(
            width, height,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,      # Zachování poměru stran
            QtCore.Qt.TransformationMode.SmoothTransformation  # Vyhlazení při škálování
        )
    return QtGui.QPixmap()

class PublicationDelegate(QtWidgets.QStyledItemDelegate):
    """
    Delegate třída určující způsob vykreslování jednotlivých položek v seznamu.
    Umožňuje přizpůsobit vzhled a chování položek, včetně hover efektů.
    """
    def paint(self, painter, option, index):
        """
        Metoda pro vykreslení jedné položky seznamu s podporou hover efektů.
        
        Args:
            painter: QPainter objekt pro vykreslování
            option: StyleOptionViewItem obsahující parametry stylu
            index: ModelIndex položky, která se má vykreslit
        """
        # Uložení původního stavu painteru
        painter.save()
        
        # Nastavení anti-aliasingu pro hladké rohy
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Vytvoření cesty pro zaoblené rohy
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(option.rect).adjusted(2, 2, -2, -2)  # Konverze na QRectF
        path.addRoundedRect(rect, 15, 15)  # Radius 15 pro zaoblené rohy
        
        # Získání dat z modelu pro vykreslení
        pixmap = index.data(QtCore.Qt.DecorationRole)    # Obrázek
        
        # Použití MouseOver stavu přímo z option
        is_hovered = option.state & QtWidgets.QStyle.State_MouseOver
        title = index.data(QtCore.Qt.ToolTipRole) if is_hovered else index.data(QtCore.Qt.DisplayRole)
        
        # Vykreslení pozadí při různých stavech (hover, selected)
        if is_hovered:
            painter.fillPath(path, QtGui.QColor(0, 0, 0, 0))  # Světle šedá při najetí myší
        elif option.state & QtWidgets.QStyle.State_Selected:
            painter.fillPath(path, QtGui.QColor(0, 0, 0, 0))    # Barva výběru
            
        # Nastavení pera pro rámeček
        pen = QtGui.QPen(QtGui.QColor("#666666"))  # Stejná barva jako v StyleHelper
        pen.setWidth(2)  # Šířka 2px jako v StyleHelper
        painter.setPen(pen)
        painter.drawPath(path)
            
        # Výpočet oblasti pro obrázek a text
        title_height = self.get_text_height(option, title)
        available_height = option.rect.height() - title_height - 10
        
        # Dynamická změna velikosti obrázku při hoveru - pouze pro dlouhé texty
        text_needed_height = self.get_text_height(option, title)
        if is_hovered and text_needed_height > 30:  # 30 pixelů je přibližná výška pro krátký text
            img_height = min(available_height, 120)
        else:
            img_height = min(available_height, 150)
                
        # Škálování a vykreslení obrázku
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                100, img_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            
            # Vykreslení obrázku na střed položky
            img_x = option.rect.x() + (option.rect.width() - scaled_pixmap.width()) // 2
            img_y = option.rect.y() + 5
            painter.drawPixmap(
                QtCore.QRect(img_x, img_y, scaled_pixmap.width(), scaled_pixmap.height()),
                scaled_pixmap
            )
            
            # Nastavení oblasti pro text pod obrázkem
            text_y = img_y + scaled_pixmap.height() + 5
        else:
            # Pokud není obrázek, text začíná od horního okraje
            text_y = option.rect.y() + 5
        
        text_rect = QtCore.QRect(
            option.rect.x() + 5,
            text_y,
            option.rect.width() - 10,
            option.rect.height() - (text_y - option.rect.y()) - 5
        )
        
        # Nastavení fontu pro text
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QtGui.QColor("white"))  # Nastavení bílé barvy textu
        
        # Vykreslení textu se zalamováním slov
        painter.drawText(
            text_rect,
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter | QtCore.Qt.TextWordWrap,
            title
        )
        
        # Obnovení původního stavu painteru
        painter.restore()

    def get_text_height(self, option, text):
        """
        Výpočet výšky textu pro správné umístění v položce.
        
        Args:
            option: StyleOptionViewItem obsahující parametry stylu
            text: Text, jehož výška se má vypočítat
        
        Returns:
            int: Výška textu v pixelech
        """
        metrics = QtGui.QFontMetrics(option.font)
        rect = option.rect.adjusted(5, 0, -5, 0)
        return metrics.boundingRect(rect, QtCore.Qt.TextWordWrap, text).height()

class PublicationsView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        
        self.setStyleSheet("""
            QListView {
                border: none;
                background: transparent;
            }
            QListView::item {
                border: none;
            }
        """)
        
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSpacing(10)
        self.setWordWrap(True)
        self.setMouseTracking(True)
        
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        
        self.setItemDelegate(PublicationDelegate(self))
        
        self.setUniformItemSizes(False)
        self.setBatchSize(100)
        
        self.setMovement(QtWidgets.QListView.Static)
        
        self.viewport().setAttribute(QtCore.Qt.WA_Hover)
        self.viewport().setStyleSheet("background: transparent; border: none;")

    def mouseDoubleClickEvent(self, event):
        """Handler pro dvojklik na položku"""
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
            
        item = self.model().itemFromIndex(index)
        pub_id = item.data(QtCore.Qt.UserRole)
        self.window().open_publication_details(pub_id)
        
class AddPublications(QDialog, StyleHelper):
    def __init__(self, parent=None, selected_category=None, selected_tab=None, category_manager=None):
        super().__init__(parent)

        self.selected_category = selected_category
        self.selected_tab = selected_tab
        self.category_manager = category_manager  # Uložení category_manager jako atribut


        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Přidat publikaci")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        header = StyleHelper.setup_header(
            "Přidat publikaci",
            container,
            on_minimize=self.showMinimized,
            on_close=self.close
        )
        container_layout.addWidget(header)

        self.content_frame = QWidget()
        content_frame_layout = QVBoxLayout(self.content_frame)
        content_frame_layout.setContentsMargins(10, 10, 10, 10)
        content_frame_layout.setSpacing(5)

        title_label, self.title_input = self.create_labeled_input("Název publikace", "Zadejte název publikace")
        author_label, self.author_input = self.create_labeled_input("Autor", "Zadejte jméno autora", required=False)
        year_label, self.year_input = self.create_labeled_input("Rok vydání", "Zadejte rok vydání", required=False)
        desc_label, self.description_input = self.create_labeled_input("Popis publikace", "Vložte popis publikace", multiline=True, required=False)

        self.cover_container, self.cover_preview = self.setup_cover_preview()

        content_frame_layout.addWidget(title_label)
        content_frame_layout.addWidget(self.title_input)
        content_frame_layout.addWidget(author_label)
        content_frame_layout.addWidget(self.author_input)
        content_frame_layout.addWidget(year_label)
        content_frame_layout.addWidget(self.year_input)
        content_frame_layout.addWidget(desc_label)
        content_frame_layout.addWidget(self.description_input)
        content_frame_layout.addWidget(self.cover_container)
        content_frame_layout.addStretch()

        framed_content = StyleHelper.apply_frame_style(
            self.content_frame,
            frame_color="#666666",
            border_width=2,
            border_radius=15,
            padding=8
        )

        container_layout.addWidget(framed_content, stretch=1)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        self.add_publication_button = QPushButton("Přidat publikaci")
        self.add_publication_button.clicked.connect(self.add_publication)
        self.close_button = QPushButton("Zavřít")

        StyleHelper.apply_button_style(self.add_publication_button)
        StyleHelper.apply_button_style(self.close_button)

        self.close_button.clicked.connect(self.close)
        # self.add_publication_button.clicked.connect(self.add_publication) # Odkomentujte později

        buttons_layout.addWidget(self.add_publication_button)
        buttons_layout.addWidget(self.close_button)

        container_layout.addWidget(buttons_container, alignment=Qt.AlignRight)

        main_layout.addWidget(container)

        self.resize(400, 1100)
        self.setMinimumSize(400, 900)

        StyleHelper.make_draggable(self)
        self._desired_size = QSize(400, 850)
        
    def add_publication(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not title:
            StyleHelper.create_message_box("Chyba", "Prosím zadejte název publikace.", "warning", self)
            return

        # Validace roku, pokud je zadán
        if year:
            try:
                year = int(year)
            except ValueError:
                StyleHelper.create_message_box("Chyba", "Rok musí být celé číslo.", "warning", self)
                return

        # Kontrola vybrané kategorie
        if not self.selected_category or not self.selected_tab:
            StyleHelper.create_message_box("Chyba", "Vyberte prosím kategorii pro publikaci.", "warning", self)
            return

        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()

        try:
            category_id = self.category_manager.get_category_id(self.selected_tab, self.selected_category)

            cursor.execute('''
                INSERT INTO publications (title, author, year, category_id, category_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author or None, year, category_id, self.selected_tab))

            publication_id = cursor.lastrowid
            conn.commit()

            # Uložení fyzických souborů
            pub_dir = f"publications/{publication_id}"
            os.makedirs(pub_dir, exist_ok=True)

            # Uložení popisu
            desc_file = f"{pub_dir}/description.txt"
            with open(desc_file, 'w', encoding='utf-8') as f:
                f.write(description)

            # Kopírování obálky
            if self.cover_path:
                cover_file = f"{pub_dir}/cover{os.path.splitext(self.cover_path)[1]}"
                shutil.copy2(self.cover_path, cover_file)

            # Kopírování PDF
            if self.pdf_path:
                pdf_file = f"{pub_dir}/{os.path.basename(self.pdf_path)}"
                shutil.copy2(self.pdf_path, pdf_file)

            self.close()

        except Exception as e:
            conn.rollback()
            StyleHelper.create_message_box(
                "Chyba", 
                f"Nepodařilo se přidat publikaci: {str(e)}", 
                "warning", 
                self
            )
        finally:
            conn.close()
        
    def showEvent(self, event):
        """Metoda volaná těsně před zobrazením okna"""
        super().showEvent(event)
        # Nastavíme požadovanou velikost
        self.resize(self._desired_size)
        self.setMinimumSize(self._desired_size)
        # Vynutíme překreslení
        QApplication.processEvents()
        
    def setup_cover_preview(self):
        """
        Vytvoří a nastaví widget pro náhled obálky publikace s tlačítky a informacemi o souborech
        """
        # Vytvoření QLabel pro náhled s větší fixní velikostí
        cover_preview = QLabel()
        cover_preview.setAlignment(Qt.AlignCenter)
        cover_preview.setMinimumSize(120, 170)  # Nastavíme větší minimální velikost
        cover_preview.setMaximumSize(150, 200)  # Nastavíme stejnou maximální velikost
        
        # Vypneme automatické škálování obsahu, budeme ho kontrolovat sami
        cover_preview.setScaledContents(False)

        framed_preview, _ = StyleHelper.apply_text_widget_style(
            cover_preview,
            padding=3
        )

        # Vytvoření tlačítek
        add_cover_button = QPushButton("Přidat náhled")
        add_pdf_button = QPushButton("Přidat PDF")
        
        # Aplikace stylu na tlačítka
        StyleHelper.apply_button_style(add_cover_button)
        StyleHelper.apply_button_style(add_pdf_button)
        
        # Připojení event handlerů
        add_cover_button.clicked.connect(self.load_cover_image)
        add_pdf_button.clicked.connect(self.load_pdf_file)
        
        # Vytvoření informačních labelů
        self.cover_info_label = QLabel("Žádný náhled není nahrán")
        self.pdf_info_label = QLabel("Žádný PDF soubor není nahrán")
        
        # Aplikace stylu na informační texty
        StyleHelper.apply_label_style(self.cover_info_label)
        StyleHelper.apply_label_style(self.pdf_info_label)
        
        # Layout pro tlačítka vedle sebe
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(add_cover_button)
        buttons_layout.addWidget(add_pdf_button)

        # Hlavní kontejner pro vertikální uspořádání
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Přidání náhledu do horizontálně centrovaného kontejneru
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addStretch()
        h_layout.addWidget(framed_preview)
        h_layout.addStretch()

        # Přidání všech komponent do hlavního layoutu
        layout.addWidget(h_container)
        layout.addWidget(buttons_widget)
        layout.addSpacing(10)
        layout.addWidget(self.cover_info_label)
        layout.addWidget(self.pdf_info_label)
        layout.addStretch()

        # Uložení cest k souborům jako atributy třídy
        self.cover_path = None
        self.pdf_path = None

        return container, cover_preview

    def load_cover_image(self):
        """
        Otevře dialog pro výběr obrázku a nastaví ho jako náhled
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vybrat náhled publikace",
            "",
            "Obrázky (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.cover_path = file_path
                
                # Škálování obrázku na velikost náhledu se zachováním poměru stran
                scaled_pixmap = pixmap.scaled(
                    self.cover_preview.minimumSize(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.cover_preview.setPixmap(scaled_pixmap)
                file_name = os.path.basename(file_path)
                self.cover_info_label.setText(f"Nahrán náhled: {file_name}")
            else:
                QMessageBox.warning(self, "Chyba", "Nepodařilo se načíst obrázek.")

    def load_pdf_file(self):
        """
        Otevře dialog pro výběr PDF souboru
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vybrat PDF soubor",
            "",
            "PDF soubory (*.pdf)"
        )
        
        if file_path:
            # Uložení cesty k souboru
            self.pdf_path = file_path
            # Aktualizace informačního textu
            file_name = os.path.basename(file_path)
            self.pdf_info_label.setText(f"Nahrán PDF soubor: {file_name}")
            
class PublicationDetailsWindow(QDialog, StyleHelper):
    def __init__(self, parent=None, publication_id=None, category_manager=None):
        super().__init__(parent)
        self.publication_id = publication_id
        self.category_manager = category_manager

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Detail publikace")
        
        # Nastavení velikosti okna
        self.resize(600, 800)

        # --- Základní nastavení okna ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Hlavní container ---
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        # --- Hlavička ---
        header = StyleHelper.setup_header(
            "Detail publikace",
            container,
            on_minimize=self.showMinimized,
            on_close=self.close
        )
        container_layout.addWidget(header)

        # --- Content frame ---
        self.content_frame = QWidget()
        content_frame_layout = QVBoxLayout(self.content_frame)
        content_frame_layout.setContentsMargins(10, 10, 10, 10)
        content_frame_layout.setSpacing(15)

        # --- Načtení dat publikace ---
        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, author, year, category_id, category_type
            FROM publications
            WHERE id = ?
        ''', (self.publication_id,))
        publication_data = cursor.fetchone()
        conn.close()

        title, author, year, category_id, category_type = publication_data

        # --- Nadpis publikace ---
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 5px;
                margin-top: 5px;
                margin-bottom: 10px;
            }
        """)
        content_frame_layout.addWidget(title_label)

        # --- Náhled publikace ---
        cover_path = self.find_cover_image(self.publication_id)
        preview_section = self.create_preview_section(cover_path)
        content_frame_layout.addWidget(preview_section)

        # --- Informace o publikaci ---
        info_section = self.create_info_section(author, year)
        content_frame_layout.addWidget(info_section)

        # --- Popis publikace ---
        desc_section = self.create_description_section()
        content_frame_layout.addWidget(desc_section)

        framed_content = StyleHelper.apply_frame_style(
            self.content_frame,
            frame_color="#666666",
            border_width=2,
            border_radius=15,
            padding=8
        )
        
        # --- Tlačítka ---
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        self.close_button = QPushButton("Zavřít")
        self.edit_button = QPushButton("Editovat")

        StyleHelper.apply_button_style(self.close_button)
        StyleHelper.apply_button_style(self.edit_button)

        self.close_button.clicked.connect(self.close)
        self.edit_button.clicked.connect(self.open_edit_window)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        buttons_layout.addWidget(self.edit_button)

        # --- Sestavení layoutu ---
        container_layout.addWidget(framed_content, stretch=1)
        container_layout.addWidget(buttons_container)
        main_layout.addWidget(container)

        StyleHelper.make_draggable(self)
        
    def create_preview_section(self, cover_path):
        """Vytvoří sekci s náhledem publikace"""
        preview_section = QWidget()
        layout = QVBoxLayout(preview_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("Náhled publikace")
        title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-size: 10pt;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
        """)

        # Náhled a PDF tlačítko
        preview_widget = QWidget()
        preview_layout = QHBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(20)

        # Náhled v rámečku
        cover_frame = QFrame()
        cover_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 3px;
            }
        """)
        cover_frame.setFixedSize(170, 220)
        cover_frame_layout = QVBoxLayout(cover_frame)
        cover_frame_layout.setContentsMargins(5, 5, 5, 5)

        # Náhled bez rámečku
        cover_label = QLabel()
        cover_label.setAlignment(Qt.AlignCenter)
        if cover_path:
            pixmap = QPixmap(cover_path)
            scaled_pixmap = pixmap.scaled(
                150, 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            cover_label.setPixmap(scaled_pixmap)
            cover_label.setStyleSheet("border: none;")
        else:
            cover_label.setText("Žádný náhled")
            cover_label.setStyleSheet("color: white; border: none;")
        
        cover_frame_layout.addWidget(cover_label, alignment=Qt.AlignCenter)

        # PDF tlačítko
        open_pdf_button = QPushButton("Otevřít PDF")
        StyleHelper.apply_button_style(open_pdf_button)
        open_pdf_button.clicked.connect(self.open_pdf)

        preview_layout.addWidget(cover_frame, alignment=Qt.AlignCenter)
        preview_layout.addWidget(open_pdf_button, alignment=Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(preview_widget)

        return preview_section

    def create_info_section(self, author, year):
        """Vytvoří sekci s informacemi o publikaci"""
        info_section = QWidget()
        layout = QVBoxLayout(info_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Explicitně nastavíme všechny styly včetně border: none
        title = QLabel("Informace o publikaci")
        title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-size: 10pt;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
        """)

        # Informace
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(5)

        author_label = QLabel(f"Autor: {author}" if author else "Autor: Neznámý")
        year_label = QLabel(f"Rok vydání: {year}" if year else "Rok vydání: Neznámý")

        author_label.setStyleSheet("color: white; border: none;")
        year_label.setStyleSheet("color: white; border: none;")

        info_layout.addWidget(author_label)
        info_layout.addWidget(year_label)

        layout.addWidget(title)
        layout.addWidget(info_frame)

        return info_section

    def create_description_section(self):
        """Vytvoří sekci s popisem publikace"""
        desc_section = QWidget()
        layout = QVBoxLayout(desc_section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("Popis publikace")
        title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-size: 10pt;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
        """)

        # Načtení popisu
        description_file = f"publications/{self.publication_id}/description.txt"
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                description = f.read()
        else:
            description = "Žádný popis není k dispozici"

        # Text popisu
        description_text = QLabel(description)
        description_text.setWordWrap(True)
        description_text.setFixedHeight(100)
        description_text.setStyleSheet("""
            QLabel {
                color: white;
                background-color: #353535;
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        description_text.mouseDoubleClickEvent = lambda event: self.open_description_window(description)

        layout.addWidget(title)
        layout.addWidget(description_text)

        return desc_section

    def find_cover_image(self, pub_id):
        """Najde obrázek obálky pro danou publikaci"""
        pub_dir = f"publications/{pub_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.startswith("cover"):
                    return os.path.join(pub_dir, file)
        return None

    def open_pdf(self):
        """Otevře PDF soubor publikace"""
        pub_dir = f"publications/{self.publication_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.endswith(".pdf"):
                    os.startfile(os.path.join(pub_dir, file))
                    break

    def open_description_window(self, description):
        description_window = QDialog(self)
        description_window.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        description_window.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(description_window)
        main_layout.setContentsMargins(15, 15, 15, 15)

        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 20)

        header = StyleHelper.setup_header(
            "Popis publikace",
            container,
            on_minimize=description_window.showMinimized,
            on_close=description_window.close
        )
        container_layout.addWidget(header)

        # Vytvoříme rámeček pro popis
        description_frame = QFrame()
        description_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #666666;
                border-radius: 15px;
                background-color: transparent;
            }
        """)
        description_layout = QVBoxLayout(description_frame)
        description_layout.setContentsMargins(15, 15, 15, 15)

        # Text popisu
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                border: none;
            }
        """)
        description_layout.addWidget(description_label)
        container_layout.addWidget(description_frame)

        # Tlačítko Zavřít
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        close_button = QPushButton("Zavřít")
        StyleHelper.apply_button_style(close_button)
        close_button.clicked.connect(description_window.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        container_layout.addWidget(button_container)
        main_layout.addWidget(container)

        StyleHelper.make_draggable(description_window)
        
        description_window.setMinimumWidth(400)
        description_window.setMinimumHeight(300)
        description_window.exec_()
        
    def open_edit_window(self):
        edit_window = EditPublication(
            self,
            publication_id=self.publication_id,
            category_manager=self.category_manager
        )
        edit_window.exec_()
        # Po zavření okna obnovíme data v detailu
        self.refresh_data()

    def refresh_data(self):
        """Obnoví data v detailu po editaci"""
        # Načtení aktuálních dat z databáze
        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, author, year, category_id, category_type
            FROM publications
            WHERE id = ?
        ''', (self.publication_id,))
        publication_data = cursor.fetchone()
        conn.close()

        if publication_data:
            title, author, year, _, _ = publication_data

            # Najdeme a aktualizujeme title_label
            for i in range(self.content_frame.layout().count()):
                widget = self.content_frame.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "font-size: 18pt" in widget.styleSheet():
                    widget.setText(title)
                    break

            # Aktualizace jednotlivých sekcí
            content_layout = self.content_frame.layout()
            
            # Uložíme title_label
            title_label = content_layout.itemAt(0).widget()
            
            # Vyčistíme layout kromě title_label
            while content_layout.count() > 1:
                item = content_layout.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()

            # Znovu vytvoření sekcí
            cover_path = self.find_cover_image(self.publication_id)
            preview_section = self.create_preview_section(cover_path)
            info_section = self.create_info_section(author, year)
            desc_section = self.create_description_section()

            # Přidání aktualizovaných sekcí
            content_layout.addWidget(preview_section)
            content_layout.addWidget(info_section)
            content_layout.addWidget(desc_section)
        
class EditPublication(QDialog, StyleHelper):
    def __init__(self, parent=None, publication_id=None, category_manager=None):
        super().__init__(parent)
        self.publication_id = publication_id
        self.category_manager = category_manager
        self.cover_path = None
        self.pdf_path = None
        
        # Přidáme mapování záložek
        self.tab_mapping = {
            "Knihy": "books",
            "Časopisy": "magazines",
            "Datasheets": "datasheets",
            "Ostatní": "others"
        }
        
        # Nejdřív nastavíme velikost
        self.setMinimumSize(600, 800)
        self.setFixedSize(650, 900)  # Použijeme setFixedSize místo resize
        
        # Pak inicializujeme UI
        self.init_ui()
        self.load_publication_data()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Editace publikace")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        header = StyleHelper.setup_header(
            "Editace publikace",
            container,
            on_minimize=self.showMinimized,
            on_close=self.close
        )
        container_layout.addWidget(header)

        self.content_frame = QWidget()
        content_frame_layout = QVBoxLayout(self.content_frame)
        content_frame_layout.setContentsMargins(10, 10, 10, 10)
        content_frame_layout.setSpacing(5)

        # Vytvoření inputů
        title_label, self.title_input = self.create_labeled_input("Název publikace", "Zadejte název publikace")
        author_label, self.author_input = self.create_labeled_input("Autor", "Zadejte jméno autora", required=False)
        year_label, self.year_input = self.create_labeled_input("Rok vydání", "Zadejte rok vydání", required=False)
        desc_label, self.description_input = self.create_labeled_input("Popis publikace", "Vložte popis publikace", multiline=True, required=False)

        self.cover_container, self.cover_preview = self.setup_cover_preview()

        # Přidání widgetů do layoutu
        content_frame_layout.addWidget(title_label)
        content_frame_layout.addWidget(self.title_input)
        content_frame_layout.addWidget(author_label)
        content_frame_layout.addWidget(self.author_input)
        content_frame_layout.addWidget(year_label)
        content_frame_layout.addWidget(self.year_input)
        content_frame_layout.addWidget(desc_label)
        content_frame_layout.addWidget(self.description_input)
        content_frame_layout.addWidget(self.cover_container)
        self.location_section = self.setup_location_change()
        content_frame_layout.addWidget(self.location_section)
        content_frame_layout.addStretch()

        framed_content = StyleHelper.apply_frame_style(
            self.content_frame,
            frame_color="#666666",
            border_width=2,
            border_radius=15,
            padding=8
        )

        container_layout.addWidget(framed_content, stretch=1)

        # Tlačítka
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        self.save_button = QPushButton("Uložit změny")
        self.close_button = QPushButton("Zavřít")

        StyleHelper.apply_button_style(self.save_button)
        StyleHelper.apply_button_style(self.close_button)

        self.save_button.clicked.connect(self.save_changes)
        self.close_button.clicked.connect(self.close)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.close_button)

        container_layout.addWidget(buttons_container, alignment=Qt.AlignRight)
        main_layout.addWidget(container)
        
        StyleHelper.make_draggable(self)

    def load_publication_data(self):
        """Načte existující data publikace"""
        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, author, year, category_id, category_type
            FROM publications
            WHERE id = ?
        ''', (self.publication_id,))
        publication_data = cursor.fetchone()
        conn.close()

        if publication_data:
            title, author, year, category_id, category_type = publication_data
            
            # Nastavení základních informací
            self.title_input.setText(title)
            self.author_input.setText(author if author else "")
            self.year_input.setText(str(year) if year else "")
            
            # Načtení kategorií současného umístění
            if category_type:
                categories = self.category_manager.load_categories(category_type)
                current_category = None
                parent_category = None
                
                # Hledání aktuální kategorie a její nadřazené kategorie
                for cat in categories:
                    if cat['id'] == category_id:
                        current_category = cat['name']
                        break
                    for sub_id, sub_name in cat['subcategories']:
                        if sub_id == category_id:
                            current_category = sub_name
                            parent_category = cat['name']
                            break
                    if current_category:
                        break
                
                # Nastavení comboboxů podle aktuálních dat
                for tab_name, tab_type in self.tab_mapping.items():
                    if tab_type == category_type:
                        self.tab_combo.setCurrentText(tab_name)
                        break
                
                if parent_category:
                    self.category_combo.setCurrentText(parent_category)
                    # Načtení podkategorií
                    self.on_category_changed(parent_category)
                    self.subcategory_combo.setCurrentText(current_category)
                else:
                    self.category_combo.setCurrentText(current_category)

            # Načtení popisu
            description_file = f"publications/{self.publication_id}/description.txt"
            if os.path.exists(description_file):
                with open(description_file, 'r') as f:
                    description = f.read()
                    self.description_input.setText(description)

            # Načtení náhledu
            cover_path = self.find_cover_image()
            if cover_path:
                self.cover_path = cover_path
                pixmap = QPixmap(cover_path)
                scaled_pixmap = pixmap.scaled(
                    self.cover_preview.minimumSize(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.cover_preview.setPixmap(scaled_pixmap)
                self.cover_info_label.setText(f"Nahrán náhled: {os.path.basename(cover_path)}")

            # Načtení PDF
            pdf_path = self.find_pdf_file()
            if pdf_path:
                self.pdf_path = pdf_path
                self.pdf_info_label.setText(f"Nahrán PDF soubor: {os.path.basename(pdf_path)}")

            # Nastavení aktuálního umístění publikace
            if publication_data and category_type:
                # Nastavení záložky
                for tab_name, tab_type in self.tab_mapping.items():
                    if tab_type == category_type:
                        self.tab_combo.setCurrentText(tab_name)
                        
                        # Načtení kategorií pro vybranou záložku
                        categories = self.category_manager.load_categories(category_type)
                        
                        # Najít aktuální kategorii a její případnou nadřazenou kategorii
                        current_category = None
                        parent_category = None
                        
                        for cat in categories:
                            # Kontrola hlavní kategorie
                            if cat['id'] == category_id:
                                current_category = cat['name']
                                break
                            # Kontrola podkategorií
                            for sub_id, sub_name in cat['subcategories']:
                                if sub_id == category_id:
                                    current_category = sub_name
                                    parent_category = cat['name']
                                    break
                            if current_category:
                                break
                        
                        # Nastavení kategorie a podkategorie
                        if parent_category:
                            self.category_combo.setCurrentText(parent_category)
                            self.subcategory_combo.setEnabled(True)
                            self.subcategory_combo.setCurrentText(current_category)
                        else:
                            self.category_combo.setCurrentText(current_category)
                        
                        break

    def find_cover_image(self):
        """Najde cestu k náhledovému obrázku"""
        pub_dir = f"publications/{self.publication_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.startswith("cover"):
                    return os.path.join(pub_dir, file)
        return None

    def find_pdf_file(self):
        """Najde cestu k PDF souboru"""
        pub_dir = f"publications/{self.publication_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.endswith(".pdf"):
                    return os.path.join(pub_dir, file)
        return None

    def setup_cover_preview(self):
        """Vytvoří a nastaví widget pro náhled obálky publikace"""
        # Vytvoření QLabel pro náhled s větší fixní velikostí
        cover_preview = QLabel()
        cover_preview.setAlignment(Qt.AlignCenter)
        cover_preview.setMinimumSize(120, 170)
        cover_preview.setMaximumSize(150, 200)
        cover_preview.setScaledContents(False)

        framed_preview, _ = StyleHelper.apply_text_widget_style(
            cover_preview,
            padding=3
        )

        # Vytvoření tlačítek
        add_cover_button = QPushButton("Změnit náhled")
        add_pdf_button = QPushButton("Změnit PDF")
        
        StyleHelper.apply_button_style(add_cover_button)
        StyleHelper.apply_button_style(add_pdf_button)
        
        add_cover_button.clicked.connect(self.load_cover_image)
        add_pdf_button.clicked.connect(self.load_pdf_file)
        
        self.cover_info_label = QLabel("Žádný náhled není nahrán")
        self.pdf_info_label = QLabel("Žádný PDF soubor není nahrán")
        
        StyleHelper.apply_label_style(self.cover_info_label)
        StyleHelper.apply_label_style(self.pdf_info_label)
        
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(add_cover_button)
        buttons_layout.addWidget(add_pdf_button)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addStretch()
        h_layout.addWidget(framed_preview)
        h_layout.addStretch()

        layout.addWidget(h_container)
        layout.addWidget(buttons_widget)
        layout.addSpacing(10)
        layout.addWidget(self.cover_info_label)
        layout.addWidget(self.pdf_info_label)
        layout.addStretch()

        return container, cover_preview

    def load_cover_image(self):
        """Otevře dialog pro výběr obrázku a nastaví ho jako náhled"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vybrat náhled publikace",
            "",
            "Obrázky (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.cover_path = file_path
                scaled_pixmap = pixmap.scaled(
                    self.cover_preview.minimumSize(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.cover_preview.setPixmap(scaled_pixmap)
                file_name = os.path.basename(file_path)
                self.cover_info_label.setText(f"Nahrán náhled: {file_name}")
            else:
                QMessageBox.warning(self, "Chyba", "Nepodařilo se načíst obrázek.")

    def load_pdf_file(self):
        """Otevře dialog pro výběr PDF souboru"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vybrat PDF soubor",
            "",
            "PDF soubory (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            file_name = os.path.basename(file_path)
            self.pdf_info_label.setText(f"Nahrán PDF soubor: {file_name}")
            
    def setup_location_change(self):
        """Vytvoří sekci pro změnu umístění publikace"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Nadpis sekce
        title = QLabel("Změna umístění")
        title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                font-size: 10pt;
                font-weight: bold;
                padding: 0px;
                border: none;
            }
        """)
        layout.addWidget(title)

        # Kontejner pro comboboxes vedle sebe
        combos_container = QWidget()
        combos_layout = QHBoxLayout(combos_container)
        combos_layout.setContentsMargins(0, 0, 0, 0)
        combos_layout.setSpacing(10)

        # Combobox pro záložky
        self.tab_combo = QComboBox()
        self.tab_combo.addItem("-- Vyberte záložku --")
        self.tab_combo.addItems(list(self.tab_mapping.keys()))
        StyleHelper.apply_small_combobox_style(self.tab_combo)
        self.tab_combo.currentTextChanged.connect(self.on_tab_changed)

        # Combobox pro kategorie
        self.category_combo = QComboBox()
        self.category_combo.addItem("-- Vyberte kategorii --")
        StyleHelper.apply_small_combobox_style(self.category_combo)
        self.category_combo.setEnabled(False)
        self.category_combo.currentTextChanged.connect(self.on_category_changed)

        # Combobox pro podkategorie
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.addItem("-- Žádná podkategorie --")
        StyleHelper.apply_small_combobox_style(self.subcategory_combo)
        self.subcategory_combo.setEnabled(False)

        # Přidání comboboxes do horizontálního layoutu
        combos_layout.addWidget(self.tab_combo)
        combos_layout.addWidget(self.category_combo)
        combos_layout.addWidget(self.subcategory_combo)

        layout.addWidget(combos_container)
        return container

    def on_tab_changed(self, tab_name):
        """Handler pro změnu záložky"""
        # Reset kategorií a podkategorií
        self.category_combo.clear()
        self.category_combo.addItem("-- Vyberte kategorii --")
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("-- Žádná podkategorie --")
        
        if tab_name == "-- Vyberte záložku --":
            self.category_combo.setEnabled(False)
            self.subcategory_combo.setEnabled(False)
            return

        category_type = self.tab_mapping.get(tab_name)
        if category_type:
            # Načtení kategorií pro vybranou záložku
            categories = self.category_manager.load_categories(category_type)
            
            # Přidání kategorií do comboboxu
            for category in categories:
                self.category_combo.addItem(category['name'])
            
            self.category_combo.setEnabled(True)
            self.subcategory_combo.setEnabled(False)

    def on_category_changed(self, category_name):
        """Handler pro změnu kategorie"""
        # Reset podkategorií
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("-- Žádná podkategorie --")
        self.subcategory_combo.setEnabled(False)

        if category_name == "-- Vyberte kategorii --":
            return

        category_type = self.tab_mapping.get(self.tab_combo.currentText())
        if category_type:
            categories = self.category_manager.load_categories(category_type)
            
            # Najít vybranou kategorii a její podkategorie
            selected_category = next(
                (cat for cat in categories if cat['name'] == category_name),
                None
            )
            
            if selected_category and selected_category['subcategories']:
                for _, subcategory_name in selected_category['subcategories']:
                    self.subcategory_combo.addItem(subcategory_name)
                self.subcategory_combo.setEnabled(True)

    def save_changes(self):
        """Upravená metoda save_changes pro zpracování změny umístění"""
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        description = self.description_input.toPlainText()

        if not title:
            StyleHelper.create_message_box("Chyba", "Prosím zadejte název publikace.", "warning", self)
            return

        # Načtení původních dat pro případ, že uživatel nevybral nové umístění
        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category_id, category_type
            FROM publications
            WHERE id = ?
        ''', (self.publication_id,))
        orig_data = cursor.fetchone()
        orig_category_id, orig_category_type = orig_data if orig_data else (None, None)

        # Zjištění nové kategorie a typu
        new_tab = self.tab_combo.currentText()
        new_category_id = orig_category_id
        new_category_type = orig_category_type

        # Pokud byla vybrána nová záložka (není výchozí hodnota)
        if new_tab != "-- Vyberte záložku --":
            new_category = self.category_combo.currentText()
            new_subcategory = self.subcategory_combo.currentText()
            if new_subcategory == "-- Žádná podkategorie --":
                new_subcategory = None

            tab_mapping = {
                "Knihy": "books",
                "Časopisy": "magazines",
                "Datasheets": "datasheets",
                "Ostatní": "others"
            }
            new_category_type = tab_mapping.get(new_tab)
            
            # Získání ID nové kategorie
            category_name = new_subcategory if new_subcategory else new_category
            new_category_id = self.category_manager.get_category_id(new_category_type, category_name)

        # Aktualizace databáze
        cursor.execute('''
            UPDATE publications 
            SET title = ?, author = ?, year = ?, category_id = ?, category_type = ?
            WHERE id = ?
        ''', (title, author, year, new_category_id, new_category_type, self.publication_id))
        conn.commit()
        conn.close()

        # Aktualizace souborů
        pub_dir = f"publications/{self.publication_id}"

        # Aktualizace popisu
        desc_file = f"{pub_dir}/description.txt"
        with open(desc_file, 'w') as f:
            f.write(description)

        # Aktualizace náhledu
        if self.cover_path and not self.cover_path.startswith(pub_dir):
            # Najít a smazat starý náhled
            for file in os.listdir(pub_dir):
                if file.startswith("cover"):
                    os.remove(os.path.join(pub_dir, file))
            # Kopírovat nový náhled
            cover_file = f"{pub_dir}/cover{os.path.splitext(self.cover_path)[1]}"
            shutil.copy2(self.cover_path, cover_file)

        # Aktualizace PDF
        if self.pdf_path and not self.pdf_path.startswith(pub_dir):
            # Najít a smazat staré PDF
            for file in os.listdir(pub_dir):
                if file.endswith(".pdf"):
                    os.remove(os.path.join(pub_dir, file))
            # Kopírovat nové PDF
            pdf_file = f"{pub_dir}/{os.path.basename(self.pdf_path)}"
            shutil.copy2(self.pdf_path, pdf_file)

        self.close()
        
class FramedContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Hlavní layout pro tento widget - nastavíme nulové odsazení
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Změněno na 0
        
        # Vytvoření vnitřního widgetu s rámečkem
        self.frame = QFrame(self)
        self.frame.setStyleSheet("""
            QFrame {
                border: 2px solid #666666;
                border-radius: 15px;
                background-color: transparent;
            }
        """)
        
        # Layout pro frame
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vnitřní kontejner pro obsah
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Přidání content_container do frame
        self.frame_layout.addWidget(self.content_container)
        
        # Přidání frame do hlavního layoutu
        self.main_layout.addWidget(self.frame)
        
    def add_widget(self, widget):
        """Přidá widget do vnitřního kontejneru"""
        self.content_layout.addWidget(widget)
        
    def clear_content(self):
        """Vyčistí obsah kontejneru"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.update()
        
    def clear_content(self):
        """Vyčistí obsah kontejneru"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
class SettingsMenuWidget(QWidget):
    pageChanged = pyqtSignal(int)  # Signál pro změnu stránky
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.settings_menu = QListWidget()
        self.settings_menu.setFrameStyle(0)
        self.settings_menu.setAttribute(Qt.WA_TranslucentBackground)
        self.settings_menu.viewport().setAutoFillBackground(False)
        self.settings_menu.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                font-size: 14pt;
                color: white;
                min-width: 250px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 15px;
                background: transparent;
            }
            QListWidget::item:selected {
                border: 2px solid #666666;
                background: transparent;
            }
            QListWidget::item:hover:!selected {
                background-color: #333333;
            }
        """)
        
        self.settings_menu.addItems([
            "Správa dat",
            "Uživatelské rozhraní",
            "Správa kategorií",
            "Publikace",
            "Vzhled aplikace"
        ])
        
        self.settings_menu.currentRowChanged.connect(self.pageChanged.emit)
        layout.addWidget(self.settings_menu)
                
class SettingsContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

    def show_page(self, index):
        self.clear_content()
        if index == 0:
            self.show_data_management()
        elif index == 1:
            self.show_ui_settings()
        elif index == 2:
            self.show_category_management()
        elif index == 3:
            self.show_publication_settings()
        elif index == 4:
            self.show_appearance_settings()

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def export_database(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Export databáze", "", "ZIP archiv (*.zip)")
        if not file_path:
            return
        if not file_path.endswith('.zip'):
            file_path += '.zip'

        progress_dialog = QDialog()
        progress_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        progress_dialog.setAttribute(Qt.WA_TranslucentBackground)
        progress_dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(progress_dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        
        label = QLabel("Probíhá export...")
        label.setStyleSheet("color: white; font-size: 12pt;")
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #444444;
                border-radius: 3px;
            }
        """)
        
        container_layout.addWidget(label)
        container_layout.addWidget(progress_bar)
        layout.addWidget(container)

        progress_dialog.show()
        QApplication.processEvents()

        try:
            temp_dir = "temp_export"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # Progress tracking
            total_steps = 3  # DB, JSON, Publications
            current_step = 0

            # Databáze
            shutil.copy2("publications.db", temp_dir)
            shutil.copy2("categories.db", temp_dir)
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # JSON soubory
            json_files = [f for f in os.listdir() if f.endswith('.json')]
            for json_file in json_files:
                shutil.copy2(json_file, temp_dir)
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # Publications
            shutil.copytree("publications", os.path.join(temp_dir, "publications"))
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # ZIP
            shutil.make_archive(file_path[:-4], 'zip', temp_dir)
            shutil.rmtree(temp_dir)

            progress_dialog.close()
            StyleHelper.create_message_box("Export", "Export databáze byl úspěšně dokončen.", "info")

        except Exception as e:
            progress_dialog.close()
            StyleHelper.create_message_box("Chyba", f"Při exportu došlo k chybě: {str(e)}", "warning")

    def import_database(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Import databáze", "", "ZIP archiv (*.zip)")
        if not file_path:
            return

        progress_dialog = QDialog()
        progress_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        progress_dialog.setAttribute(Qt.WA_TranslucentBackground)
        progress_dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(progress_dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        
        label = QLabel("Probíhá import...")
        label.setStyleSheet("color: white; font-size: 12pt;")
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #444444;
                border-radius: 3px;
            }
        """)
        
        container_layout.addWidget(label)
        container_layout.addWidget(progress_bar)
        layout.addWidget(container)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            temp_dir = "temp_import"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # Rozbalení ZIP archivu
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            progress_bar.setValue(33)

            # Kontrola existence potřebných souborů
            required_files = ["publications.db", "categories.db"]
            for file in required_files:
                if not os.path.exists(os.path.join(temp_dir, file)):
                    raise FileNotFoundError(f"Chybí požadovaný soubor: {file}")

            # Záloha současných dat
            backup_dir = "backup_before_import"
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            os.makedirs(backup_dir)
            
            for file in os.listdir("."):
                if file.endswith(".db") or file.endswith(".json"):
                    shutil.copy2(file, backup_dir)
            if os.path.exists("publications"):
                shutil.copytree("publications", os.path.join(backup_dir, "publications"))
            progress_bar.setValue(66)

            # Import nových dat
            for file in os.listdir(temp_dir):
                if file.endswith(".db") or file.endswith(".json"):
                    shutil.copy2(os.path.join(temp_dir, file), ".")
            
            if os.path.exists("publications"):
                shutil.rmtree("publications")
            shutil.copytree(os.path.join(temp_dir, "publications"), "publications")
            
            progress_bar.setValue(100)
            shutil.rmtree(temp_dir)
            progress_dialog.close()

            StyleHelper.create_message_box(
                "Import", 
                "Import databáze byl úspěšně dokončen.\nPůvodní data byla zazálohována do složky 'backup_before_import'.",
                "info"
            )

        except Exception as e:
            progress_dialog.close()
            StyleHelper.create_message_box("Chyba", f"Při importu došlo k chybě: {str(e)}", "warning")
            
            # Obnovení ze zálohy v případě chyby
            if os.path.exists(backup_dir):
                for file in os.listdir(backup_dir):
                    source = os.path.join(backup_dir, file)
                    if os.path.isdir(source):
                        if os.path.exists(file):
                            shutil.rmtree(file)
                        shutil.copytree(source, file)
                    else:
                        shutil.copy2(source, ".")
                shutil.rmtree(backup_dir)

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def create_backup(self):
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        progress_dialog = QDialog()
        progress_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        progress_dialog.setAttribute(Qt.WA_TranslucentBackground)
        progress_dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(progress_dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        
        label = QLabel("Vytváření zálohy...")
        label.setStyleSheet("color: white; font-size: 12pt;")
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #444444;
                border-radius: 3px;
            }
        """)
        
        container_layout.addWidget(label)
        container_layout.addWidget(progress_bar)
        layout.addWidget(container)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            os.makedirs(backup_dir)
            current_step = 0
            total_steps = 3

            # Zálohování databází
            for db in ["publications.db", "categories.db"]:
                if os.path.exists(db):
                    shutil.copy2(db, os.path.join(backup_dir, db))
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # Zálohování JSON souborů
            json_files = [f for f in os.listdir() if f.endswith('.json')]
            for json_file in json_files:
                shutil.copy2(json_file, os.path.join(backup_dir, json_file))
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # Zálohování složky publikací
            if os.path.exists("publications"):
                shutil.copytree("publications", os.path.join(backup_dir, "publications"))
            current_step += 1
            progress_bar.setValue(100)

            progress_dialog.close()
            StyleHelper.create_message_box(
                "Záloha",
                f"Záloha byla úspěšně vytvořena ve složce '{backup_dir}'",
                "info"
            )

        except Exception as e:
            progress_dialog.close()
            StyleHelper.create_message_box("Chyba", f"Při vytváření zálohy došlo k chybě: {str(e)}", "warning")

    def restore_backup(self):
        # Dialog pro výběr složky se zálohou
        backup_dir = QFileDialog.getExistingDirectory(None, "Vyberte složku se zálohou", "",
                                                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if not backup_dir:
            return

        # Kontrola, zda složka obsahuje potřebné soubory
        required_files = ["publications.db", "categories.db"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(backup_dir, f))]
        if missing_files:
            StyleHelper.create_message_box(
                "Chyba",
                f"Vybraná složka neobsahuje všechny potřebné soubory: {', '.join(missing_files)}",
                "warning"
            )
            return

        progress_dialog = QDialog()
        progress_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        progress_dialog.setAttribute(Qt.WA_TranslucentBackground)
        progress_dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(progress_dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        
        label = QLabel("Obnovování ze zálohy...")
        label.setStyleSheet("color: white; font-size: 12pt;")
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #666666;
                border-radius: 5px;
                text-align: center;
                background-color: #353535;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #444444;
                border-radius: 3px;
            }
        """)
        
        container_layout.addWidget(label)
        container_layout.addWidget(progress_bar)
        layout.addWidget(container)
        progress_dialog.show()
        QApplication.processEvents()

        try:
            current_step = 0
            total_steps = 3

            # Obnova databází
            for db in required_files:
                if os.path.exists(db):
                    os.remove(db)
                shutil.copy2(os.path.join(backup_dir, db), ".")
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # Obnova JSON souborů
            json_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
            for json_file in json_files:
                if os.path.exists(json_file):
                    os.remove(json_file)
                shutil.copy2(os.path.join(backup_dir, json_file), ".")
            current_step += 1
            progress_bar.setValue(int(current_step/total_steps * 100))

            # Obnova složky publikací
            backup_publications = os.path.join(backup_dir, "publications")
            if os.path.exists(backup_publications):
                if os.path.exists("publications"):
                    shutil.rmtree("publications")
                shutil.copytree(backup_publications, "publications")
            current_step += 1
            progress_bar.setValue(100)

            progress_dialog.close()
            StyleHelper.create_message_box(
                "Obnova ze zálohy",
                "Data byla úspěšně obnovena ze zálohy",
                "info"
            )

        except Exception as e:
            progress_dialog.close()
            StyleHelper.create_message_box("Chyba", f"Při obnovování ze zálohy došlo k chybě: {str(e)}", "warning")

    def clear_cache(self):
        files_to_clear = {
            'search_history.json': 'Historie vyhledávání',
            'search_favorites.json': 'Oblíbené položky vyhledávání',
            'search_favorites_settings.json': 'Nastavení vyhledávání'
        }

        # Dialog pro výběr co vyčistit
        dialog = QDialog()
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        
        title = QLabel("Vyberte, co chcete vyčistit:")
        title.setStyleSheet("color: white; font-size: 14pt; margin-bottom: 10px;")
        container_layout.addWidget(title)

        checkboxes = {}
        for file, desc in files_to_clear.items():
            cb = QCheckBox(desc)
            cb.setStyleSheet("""
                QCheckBox {
                    color: white;
                    font-size: 12px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #666666;
                    border-radius: 4px;
                    background-color: #353535;
                }
                QCheckBox::indicator:checked {
                    background-color: #888888;
                }
            """)
            checkboxes[file] = cb
            container_layout.addWidget(cb)

        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("Vyčistit")
        cancel_button = QPushButton("Zrušit")
        StyleHelper.apply_button_style(ok_button)
        StyleHelper.apply_button_style(cancel_button)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        container_layout.addLayout(buttons_layout)
        layout.addWidget(container)

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            cleared = []
            for file, cb in checkboxes.items():
                if cb.isChecked() and os.path.exists(file):
                    try:
                        if file.endswith('.json'):
                            with open(file, 'w') as f:
                                json.dump([], f)
                        cleared.append(files_to_clear[file])
                    except Exception as e:
                        StyleHelper.create_message_box(
                            "Chyba",
                            f"Chyba při čištění {files_to_clear[file]}: {str(e)}",
                            "warning"
                        )
                        return
            
            if cleared:
                StyleHelper.create_message_box(
                    "Vyčištění mezipaměti",
                    f"Úspěšně vyčištěno: {', '.join(cleared)}",
                    "info"
                )

    def show_data_management(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Správa dat")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(title)

        db_group = QGroupBox("Databáze")
        db_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        db_layout = QVBoxLayout(db_group)

        export_btn = QPushButton("Exportovat databázi")
        import_btn = QPushButton("Importovat databázi")
        StyleHelper.apply_button_style(export_btn)
        StyleHelper.apply_button_style(import_btn)
        db_layout.addWidget(export_btn)
        db_layout.addWidget(import_btn)

        backup_group = QGroupBox("Zálohování")
        backup_group.setStyleSheet(db_group.styleSheet())
        backup_layout = QVBoxLayout(backup_group)

        create_backup_btn = QPushButton("Vytvořit zálohu")
        restore_backup_btn = QPushButton("Obnovit ze zálohy")
        StyleHelper.apply_button_style(create_backup_btn)
        StyleHelper.apply_button_style(restore_backup_btn)
        backup_layout.addWidget(create_backup_btn)
        backup_layout.addWidget(restore_backup_btn)

        cache_group = QGroupBox("Mezipaměť")
        cache_group.setStyleSheet(db_group.styleSheet())
        cache_layout = QVBoxLayout(cache_group)

        clear_cache_btn = QPushButton("Vyčistit mezipaměť")
        StyleHelper.apply_button_style(clear_cache_btn)
        cache_layout.addWidget(clear_cache_btn)

        layout.addWidget(db_group)
        layout.addWidget(backup_group)
        layout.addWidget(cache_group)
        layout.addStretch()

        self.content_layout.addWidget(container)

        export_btn.clicked.connect(self.export_database)
        import_btn.clicked.connect(self.import_database)
        create_backup_btn.clicked.connect(self.create_backup)
        restore_backup_btn.clicked.connect(self.restore_backup)
        clear_cache_btn.clicked.connect(self.clear_cache)

    def show_ui_settings(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Uživatelské rozhraní")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # Výchozí záložka
        tab_group = QGroupBox("Výchozí záložka")
        tab_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        tab_layout = QVBoxLayout(tab_group)
        
        self.default_tab_combo = QComboBox()
        self.default_tab_combo.addItems(["Knihy", "Časopisy", "Datasheets", "Ostatní"])
        StyleHelper.apply_small_combobox_style(self.default_tab_combo)
        
        settings_manager = self.window().settings_manager
        current_default_tab = settings_manager.get_setting('ui', 'default_tab')
        if current_default_tab:
            index = self.default_tab_combo.findText(current_default_tab)
            if index >= 0:
                self.default_tab_combo.setCurrentIndex(index)
        
        self.default_tab_combo.currentTextChanged.connect(
            lambda text: settings_manager.set_setting(text, 'ui', 'default_tab')
        )
        
        tab_layout.addWidget(self.default_tab_combo)
        layout.addWidget(tab_group)

        # Zobrazení výsledků vyhledávání
        view_group = QGroupBox("Zobrazení publikací ve výsledcích vyhledávání")
        view_group.setStyleSheet(tab_group.styleSheet())
        view_layout = QVBoxLayout(view_group)
        
        # Horní část s comboboxem a checkboxem
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        self.default_view_combo = QComboBox()
        self.default_view_combo.addItems(["Seznam", "Mřížka"])
        StyleHelper.apply_small_combobox_style(self.default_view_combo)
        
        # Načtení uložených hodnot
        current_default_view = settings_manager.get_setting('ui', 'view', 'default_view', default='Seznam')
        index = self.default_view_combo.findText(current_default_view)
        if index >= 0:
            self.default_view_combo.setCurrentIndex(index)
        
        self.external_window_check = QCheckBox("Otevřít v externím okně")
        self.external_window_check.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
        """)
        
        def update_search_display(state):
            main_window = self.window()
            settings_manager = main_window.settings_manager  # Získáme settings_manager z hlavního okna
            
            settings_manager.set_setting(bool(state), 'ui', 'view', 'use_external_window')
            
            # Aktualizace zobrazení, pokud je otevřené vyhledávání
            if hasattr(main_window, 'search_results_widget') and hasattr(main_window, 'external_info_label'):
                if state:
                    main_window.search_results_widget.hide()
                    main_window.external_info_label.show()
                else:
                    main_window.search_results_widget.show()
                    main_window.external_info_label.hide()

        self.external_window_check.setChecked(
            settings_manager.get_setting('ui', 'view', 'use_external_window', default=False)
        )
        self.external_window_check.stateChanged.connect(update_search_display)

        # SpinBoxy pro počet sloupců
        spinbox_container = QWidget()
        spinbox_layout = QHBoxLayout(spinbox_container)
        spinbox_layout.setContentsMargins(0, 0, 0, 0)
        spinbox_layout.setSpacing(40)  # Zvětšený rozestup mezi sloupci

        spinbox_style = """
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
                min-width: 60px;
                max-width: 60px;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                height: 10px;
                background-color: #555555;
                border: none;
                border-radius: 3px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                height: 10px;
                background-color: #555555;
                border: none;
                border-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #666666;
            }
            QSpinBox::up-arrow {
                width: 0;
                height: 0;
            }
            QSpinBox::down-arrow {
                width: 0;
                height: 0;
            }
        """

        # Kontejner pro levou část (ComboBox a CheckBox)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Přidání ComboBoxu a CheckBoxu do levého kontejneru
        left_layout.addWidget(self.default_view_combo)
        left_layout.addWidget(self.external_window_check)

        # Kontejner pro SpinBoxy
        spinboxes_container = QWidget()
        spinboxes_layout = QVBoxLayout(spinboxes_container)
        spinboxes_layout.setContentsMargins(0, 0, 0, 0)
        spinboxes_layout.setSpacing(10)  # Zvětšený rozestup mezi řádky

        # SpinBox pro Seznam
        list_container = QWidget()
        list_layout = QHBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(5)
        list_layout.setAlignment(Qt.AlignLeft)  # Zarovnání doleva

        list_columns_label = QLabel("Zobrazení v Seznamu")
        list_columns_label.setFixedWidth(150)  # Nastavení pevné šířky
        list_columns_label.setStyleSheet("color: white; background: transparent; border: none;")
        self.list_columns_spin = QSpinBox()
        self.list_columns_spin.setRange(1, 3)
        self.list_columns_spin.setValue(settings_manager.get_setting('ui', 'view', 'external_list_columns', default=1))
        self.list_columns_spin.setStyleSheet(spinbox_style)
        list_columns_suffix = QLabel("sloupců")
        list_columns_suffix.setStyleSheet("color: white; background: transparent; border: none;")

        list_layout.addWidget(list_columns_label)
        list_layout.addWidget(self.list_columns_spin)
        list_layout.addWidget(list_columns_suffix)

        # SpinBox pro Mřížku
        grid_container = QWidget()
        grid_layout = QHBoxLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(5)
        grid_layout.setAlignment(Qt.AlignLeft)  # Zarovnání doleva

        grid_columns_label = QLabel("Zobrazení v Mřížce")
        grid_columns_label.setFixedWidth(150)  # Stejná pevná šířka
        grid_columns_label.setStyleSheet("color: white; background: transparent; border: none;")
        self.grid_columns_spin = QSpinBox()
        self.grid_columns_spin.setRange(2, 8)
        self.grid_columns_spin.setValue(settings_manager.get_setting('ui', 'view', 'external_grid_columns', default=4))
        self.grid_columns_spin.setStyleSheet(spinbox_style)
        grid_columns_suffix = QLabel("sloupců")
        grid_columns_suffix.setStyleSheet("color: white; background: transparent; border: none;")

        grid_layout.addWidget(grid_columns_label)
        grid_layout.addWidget(self.grid_columns_spin)
        grid_layout.addWidget(grid_columns_suffix)

        # Přidání SpinBoxů do jejich kontejneru
        spinboxes_layout.addWidget(list_container)
        spinboxes_layout.addWidget(grid_container)

         # Hlavní layout pro zobrazení
        view_content_layout = QHBoxLayout()
        view_content_layout.setContentsMargins(0, 0, 0, 0)
        view_content_layout.setSpacing(40)  # Přidáme sem nastavení mezery
        view_content_layout.addWidget(left_container)
        view_content_layout.addWidget(spinboxes_container)
        view_content_layout.addStretch()

        view_layout.addLayout(view_content_layout)

        # Navigace
        nav_group = QGroupBox("Navigace")
        nav_group.setStyleSheet(tab_group.styleSheet())
        nav_layout = QVBoxLayout(nav_group)

        self.remember_category_check = QCheckBox("Pamatovat poslední otevřenou kategorii")
        self.remember_category_check.setStyleSheet(self.external_window_check.styleSheet())
        self.remember_category_check.setChecked(
            settings_manager.get_setting('ui', 'navigation', 'remember_last_category')
        )

        self.auto_expand_check = QCheckBox("Automaticky rozbalovat kategorie")
        self.auto_expand_check.setStyleSheet(self.external_window_check.styleSheet())
        self.auto_expand_check.setChecked(
            settings_manager.get_setting('ui', 'navigation', 'auto_expand_categories')
        )

        nav_layout.addWidget(self.remember_category_check)
        nav_layout.addWidget(self.auto_expand_check)

        # Připojení signálů
        self.default_view_combo.currentTextChanged.connect(
            lambda text: settings_manager.set_setting(text, 'ui', 'view', 'default_view')
        )
        self.external_window_check.setChecked(
            settings_manager.get_setting('ui', 'view', 'use_external_window', default=False)
        )
        self.external_window_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'view', 'use_external_window')
        )
        self.list_columns_spin.valueChanged.connect(
            lambda value: settings_manager.set_setting(value, 'ui', 'view', 'external_list_columns')
        )
        self.grid_columns_spin.valueChanged.connect(
            lambda value: settings_manager.set_setting(value, 'ui', 'view', 'external_grid_columns')
        )
        self.remember_category_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'navigation', 'remember_last_category')
        )
        self.auto_expand_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'navigation', 'auto_expand_categories')
        )

        layout.addWidget(view_group)
        layout.addWidget(nav_group)
        layout.addStretch()

        self.content_layout.addWidget(container)

    def show_category_management(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        category_widget = CategoryManagementWidget(
            self.window().category_manager,
            parent=self,
            main_window=self.window()
            
        )
        layout.addWidget(category_widget)

        self.content_layout.addWidget(container)

    def show_publication_settings(self):
        pass

    def show_appearance_settings(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Vzhled aplikace")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # Ponecháme prázdnou metodu pro budoucí použití
        layout.addStretch()
        self.content_layout.addWidget(container)
        
    def show_search_settings(self):
        """Zobrazí nastavení vyhledávání"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Nastavení vyhledávání")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # Výchozí zaškrtnutí
        checkboxes_group = QGroupBox("Výchozí nastavení vyhledávání")
        checkboxes_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        checkboxes_layout = QVBoxLayout(checkboxes_group)

        self.title_check = QCheckBox("Vyhledávat v názvech")
        self.desc_check = QCheckBox("Vyhledávat v popisech")
        self.pdf_check = QCheckBox("Vyhledávat v PDF")

        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
        """

        for cb in [self.title_check, self.desc_check, self.pdf_check]:
            cb.setStyleSheet(checkbox_style)
            checkboxes_layout.addWidget(cb)

        # Historie vyhledávání
        history_group = QGroupBox("Historie vyhledávání")
        history_group.setStyleSheet(checkboxes_group.styleSheet())
        history_layout = QVBoxLayout(history_group)

        history_label = QLabel("Počet položek historie:")
        history_label.setStyleSheet("color: white;")
        
        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(10, 1000)
        self.history_size_spin.setSingleStep(10)
        self.history_size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #444444;
                color: white;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_size_spin)

        # Načtení hodnot
        settings_manager = self.window().settings_manager
        search_settings = settings_manager.get_setting('ui', 'search')
        
        self.title_check.setChecked(search_settings['default_checkboxes'].get('title', True))
        self.desc_check.setChecked(search_settings['default_checkboxes'].get('description', False))
        self.pdf_check.setChecked(search_settings['default_checkboxes'].get('pdf', False))
        self.history_size_spin.setValue(search_settings.get('history_size', 100))

        # Připojení signálů
        self.title_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'search', 'default_checkboxes', 'title')
        )
        self.desc_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'search', 'default_checkboxes', 'description')
        )
        self.pdf_check.stateChanged.connect(
            lambda state: settings_manager.set_setting(bool(state), 'ui', 'search', 'default_checkboxes', 'pdf')
        )
        self.history_size_spin.valueChanged.connect(
            lambda value: settings_manager.set_setting(value, 'ui', 'search', 'history_size')
        )

        layout.addWidget(checkboxes_group)
        layout.addWidget(history_group)
        layout.addStretch()

        self.content_layout.addWidget(container)
        
    def show_dialog_settings(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Potvrzovací dialogy")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        dialogs_group = QGroupBox("Nastavení dialogů")
        dialogs_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        dialogs_layout = QVBoxLayout(dialogs_group)

        checkbox_style = """
            QCheckBox {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 4px;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
            }
        """

        settings_manager = self.window().settings_manager
        dialog_settings = settings_manager.get_setting('ui', 'dialogs')

        checkboxes = {
            'confirm_delete': ('Potvrdit smazání publikace', True),
            'confirm_category_delete': ('Potvrdit smazání kategorie', True),
            'confirm_import': ('Potvrdit import dat', True),
            'confirm_backup': ('Potvrdit vytvoření zálohy', True)
        }

        self.dialog_checkboxes = {}
        for key, (label, default) in checkboxes.items():
            checkbox = QCheckBox(label)
            checkbox.setStyleSheet(checkbox_style)
            checkbox.setChecked(dialog_settings.get(key, default))
            checkbox.stateChanged.connect(
                lambda state, k=key: settings_manager.set_setting(bool(state), 'ui', 'dialogs', k)
            )
            self.dialog_checkboxes[key] = checkbox
            dialogs_layout.addWidget(checkbox)

        layout.addWidget(dialogs_group)
        layout.addStretch()

        self.content_layout.addWidget(container)

class SettingsManager:
    def __init__(self):
        self.settings_file = 'settings.json'
        self.default_settings = {
            'ui': {
                'default_tab': 'Knihy',
                'view': {
                    'default_view': 'Seznam',
                    'use_external_window': False,
                    'grid_columns': 4,
                    'thumbnail_size': 150
                },
                'navigation': {
                    'remember_last_category': False,
                    'auto_expand_categories': False
                },
                'search': {
                    'default_checkboxes': {
                        'title': True,
                        'description': False,
                        'pdf': False
                    },
                    'history_size': 100
                },
                'dialogs': {
                    'confirm_delete': True,
                    'confirm_category_delete': True,
                    'confirm_import': True,
                    'confirm_backup': True
                }
            }
        }
        self.settings = self.load_settings()
        
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Chyba při ukládání nastavení: {e}")

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Slučte načtená nastavení s výchozími
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    return settings
        except Exception:
            pass
        return self.default_settings.copy()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get_setting(self, *keys, default=None):
        """
        Získá nastavení z konfigurace.
        
        Args:
            *keys: Klíče pro přístup k nastavení
            default: Výchozí hodnota, pokud nastavení neexistuje
            
        Returns:
            Hodnota nastavení nebo výchozí hodnota
        """
        current = self.settings
        for key in keys[:-1]:
            current = current.get(key, {})
        return current.get(keys[-1], default)

    def set_setting(self, value, *keys):
        current = self.settings
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        self.save_settings()
        
class CategoryManagementWidget(QWidget):
    def __init__(self, category_manager, parent=None, main_window=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.main_window = main_window
        self.tab_mapping = {
            "Knihy": "books",
            "Časopisy": "magazines",
            "Datasheets": "datasheets",
            "Ostatní": "others"
        }
        self.init_ui()
        self.load_categories()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Správa kategorií")
        title.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # Výběr záložky
        tab_group = QGroupBox("Záložka")
        tab_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        tab_layout = QVBoxLayout(tab_group)

        self.tab_combo = QComboBox()
        self.tab_combo.addItems(["Knihy", "Časopisy", "Datasheets", "Ostatní"])
        StyleHelper.apply_small_combobox_style(self.tab_combo)
        self.tab_combo.currentTextChanged.connect(self.load_categories)
        tab_layout.addWidget(self.tab_combo)

        # Strom kategorií
        tree_group = QGroupBox("Kategorie")
        tree_group.setStyleSheet(tab_group.styleSheet())
        tree_layout = QVBoxLayout(tree_group)

        self.categories_tree = DraggableTreeWidget()  # Použití vlastní třídy
        self.categories_tree.setHeaderHidden(True)
        StyleHelper.apply_treewidget_style(self.categories_tree)
        self.categories_tree.itemMoved.connect(self.handle_item_moved)  # Připojení nového signálu
        tree_layout.addWidget(self.categories_tree)

        # Tlačítka akcí
        actions_layout = QHBoxLayout()
        
        self.rename_btn = QPushButton("Přejmenovat")
        self.move_tab_btn = QPushButton("Přesunout do záložky")
        
        for btn in [self.rename_btn, self.move_tab_btn]:
            StyleHelper.apply_button_style(btn)
            actions_layout.addWidget(btn)

        self.rename_btn.clicked.connect(self.rename_category)
        self.move_tab_btn.clicked.connect(self.move_to_tab)

        tree_layout.addLayout(actions_layout)

        layout.addWidget(tab_group)
        layout.addWidget(tree_group)
        layout.addStretch()

    def handle_item_moved(self, item, parent, old_index=None, new_index=None):
        """
        Zpracuje přesun položky ve stromě.
        Pokud jsou zadány indexy, jde o přeuspořádání.
        Pokud ne, jde o změnu hierarchie.
        """
        if not item:
            return
                
        category_type = self.tab_mapping[self.tab_combo.currentText()]
        conn = sqlite3.connect('categories.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            if old_index is not None and new_index is not None:
                # Změna pořadí
                items = []
                if parent == self.categories_tree.invisibleRootItem():
                    for i in range(self.categories_tree.topLevelItemCount()):
                        items.append(self.categories_tree.topLevelItem(i))
                else:
                    for i in range(parent.childCount()):
                        items.append(parent.child(i))
                
                # Aktualizace pořadí
                for i, current_item in enumerate(items):
                    cursor.execute(f"""
                        UPDATE {category_type}_categories
                        SET sort_order = ?
                        WHERE id = ?
                    """, (i, current_item.data(0, Qt.UserRole)))
                    
                print(f"Updated order for {len(items)} items")
            else:
                # Změna hierarchie
                if parent and parent != self.categories_tree.invisibleRootItem():
                    # Přesun pod jinou kategorii
                    parent_id = parent.data(0, Qt.UserRole)
                    cursor.execute(f"""
                        UPDATE {category_type}_categories
                        SET parent_id = ?, sort_order = (
                            SELECT COALESCE(MAX(sort_order) + 1, 0)
                            FROM {category_type}_categories
                            WHERE parent_id = ?
                        )
                        WHERE id = ?
                    """, (parent_id, parent_id, item.data(0, Qt.UserRole)))
                else:
                    # Přesun na nejvyšší úroveň
                    cursor.execute(f"""
                        UPDATE {category_type}_categories
                        SET parent_id = NULL, sort_order = (
                            SELECT COALESCE(MAX(sort_order) + 1, 0)
                            FROM {category_type}_categories
                            WHERE parent_id IS NULL
                        )
                        WHERE id = ?
                    """, (item.data(0, Qt.UserRole),))
                
                print(f"Updated hierarchy for item {item.text(0)}")
                    
            conn.commit()
            # Obnovení pohledu ve správci kategorií
            self.load_categories()
            
            # Obnovení kategorií pro všechny záložky stejného typu
            for tab_name, db_type in self.tab_mapping.items():
                if db_type == category_type:
                    self.main_window.load_categories_for_current_tab(db_type)
                    
        except Exception as e:
            conn.rollback()
            print(f"Error details: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()  # Tento řádek poskytne kompletní stack trace
            StyleHelper.create_message_box(
                "Chyba",
                f"Nepodařilo se aktualizovat pozici kategorie: {str(e)}",
                "warning",
                self
            )
        finally:
            conn.close()
        
    def load_categories(self, tab=None):
        """Načte kategorie pro vybranou záložku"""
        self.categories_tree.clear()
        
        tab_name = tab if tab else self.tab_combo.currentText()
        category_type = self.tab_mapping.get(tab_name)
        
        if category_type:
            conn = sqlite3.connect('categories.db')
            cursor = conn.cursor()
            
            try:
                # Načtení hlavních kategorií seřazených podle sort_order
                cursor.execute(f"""
                    SELECT id, name 
                    FROM {category_type}_categories 
                    WHERE parent_id IS NULL 
                    ORDER BY sort_order
                """)
                
                categories = cursor.fetchall()
                
                for cat_id, cat_name in categories:
                    category_item = QTreeWidgetItem([cat_name])
                    category_item.setData(0, Qt.UserRole, cat_id)
                    self.categories_tree.addTopLevelItem(category_item)
                    
                    # Načtení podkategorií seřazených podle sort_order
                    cursor.execute(f"""
                        SELECT id, name 
                        FROM {category_type}_categories 
                        WHERE parent_id = ? 
                        ORDER BY sort_order
                    """, (cat_id,))
                    
                    subcategories = cursor.fetchall()
                    
                    for sub_id, sub_name in subcategories:
                        subcategory_item = QTreeWidgetItem([sub_name])
                        subcategory_item.setData(0, Qt.UserRole, sub_id)
                        category_item.addChild(subcategory_item)
                    
                    category_item.setExpanded(True)
                    
            finally:
                conn.close()

    def rename_category(self):
        """Přejmenuje vybranou kategorii nebo podkategorii"""
        selected_item = self.categories_tree.currentItem()
        if not selected_item:
            StyleHelper.create_message_box(
                "Upozornění",
                "Vyberte kategorii k přejmenování",
                "warning",
                self
            )
            return

        new_name = StyleHelper.create_styled_input_dialog(
            "Přejmenování kategorie",
            "Zadejte nový název:",
            self
        )
        
        if new_name:
            category_type = self.tab_mapping[self.tab_combo.currentText()]
            category_id = selected_item.data(0, Qt.UserRole)
            
            conn = sqlite3.connect('categories.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute(f"""
                    UPDATE {category_type}_categories
                    SET name = ?
                    WHERE id = ?
                """, (new_name, category_id))
                
                conn.commit()
                selected_item.setText(0, new_name)
                
            except Exception as e:
                StyleHelper.create_message_box(
                    "Chyba",
                    f"Nepodařilo se přejmenovat kategorii: {str(e)}",
                    "warning",
                    self
                )
            finally:
                conn.close()

    def move_to_tab(self):
        """Přesune vybranou kategorii do jiné záložky"""
        selected_item = self.categories_tree.currentItem()
        if not selected_item:
            StyleHelper.create_message_box(
                "Upozornění",
                "Vyberte kategorii k přesunutí",
                "warning",
                self
            )
            return

        current_tab = self.tab_combo.currentText()
        target_tabs = [tab for tab in ["Knihy", "Časopisy", "Datasheets", "Ostatní"] 
                    if tab != current_tab]

        # Vytvoření dialogu pro výběr cílové záložky a kategorie
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Záložka
        tab_label = QLabel("Vyberte cílovou záložku:")
        tab_label.setStyleSheet("color: white; font-weight: bold;")
        
        tab_combo = QComboBox()
        tab_combo.addItems(target_tabs)
        StyleHelper.apply_small_combobox_style(tab_combo)
        
        # Cílová kategorie
        target_group = QGroupBox("Cílové umístění")
        target_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666666;
                border-radius: 15px;
                padding: 15px;
                color: white;
                font-weight: bold;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        target_layout = QVBoxLayout(target_group)
        
        # Radio buttony pro výběr typu přesunu
        self.move_type_group = QButtonGroup(dialog)
        
        make_category = QRadioButton("Přesunout jako samostatnou kategorii")
        make_subcategory = QRadioButton("Přesunout jako podkategorii")
        
        radio_style = """
            QRadioButton {
                color: white;
                font-size: 12px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #666666;
                border-radius: 10px;
                background-color: #353535;
            }
            QRadioButton::indicator:checked {
                background-color: #888888;
            }
        """
        
        make_category.setStyleSheet(radio_style)
        make_subcategory.setStyleSheet(radio_style)
        
        self.move_type_group.addButton(make_category, 0)
        self.move_type_group.addButton(make_subcategory, 1)
        make_category.setChecked(True)
        
        # ComboBox pro výběr cílové kategorie
        self.target_category_combo = QComboBox()
        StyleHelper.apply_small_combobox_style(self.target_category_combo)
        self.target_category_combo.setEnabled(False)
        
        # Připojení signálů
        make_subcategory.toggled.connect(self.target_category_combo.setEnabled)
        tab_combo.currentTextChanged.connect(
            lambda text: self._update_target_categories(text, self.target_category_combo)
        )
        
        # Naplnění kategorií pro první záložku
        self._update_target_categories(tab_combo.currentText(), self.target_category_combo)
        
        target_layout.addWidget(make_category)
        target_layout.addWidget(make_subcategory)
        target_layout.addWidget(self.target_category_combo)
        
        # Tlačítka
        buttons = QHBoxLayout()
        ok_btn = QPushButton("Přesunout")
        cancel_btn = QPushButton("Zrušit")
        StyleHelper.apply_button_style(ok_btn)
        StyleHelper.apply_button_style(cancel_btn)
        
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        
        container_layout.addWidget(tab_label)
        container_layout.addWidget(tab_combo)
        container_layout.addWidget(target_group)
        container_layout.addLayout(buttons)
        layout.addWidget(container)
        
        if dialog.exec_() == QDialog.Accepted:
            target_tab = tab_combo.currentText()
            move_as_subcategory = make_subcategory.isChecked()
            target_category = self.target_category_combo.currentText() if move_as_subcategory else None
            
            self._move_category_to_tab(
                selected_item,
                target_tab,
                target_category
            )

    def _update_target_categories(self, tab_name, combo):
        combo.clear()
        category_type = self.tab_mapping[tab_name]
        
        conn = sqlite3.connect('categories.db')
        cursor = conn.cursor()
        
        try:
            # Získat všechny hlavní kategorie
            cursor.execute(f"""
                SELECT id, name 
                FROM {category_type}_categories 
                WHERE parent_id IS NULL
            """)
            
            categories = cursor.fetchall()
            for cat_id, cat_name in categories:
                # Odstraňte omezení, které vylučuje kategorie s podkategoriemi
                combo.addItem(cat_name)
        finally:
            conn.close()

    def _move_category_to_tab(self, item, target_tab, target_category=None):
        """Přesune kategorii do jiné záložky"""
        source_type = self.tab_mapping[self.tab_combo.currentText()]
        target_type = self.tab_mapping[target_tab]
        
        category_id = item.data(0, Qt.UserRole)
        category_name = item.text(0)
        
        print(f"Moving category: {category_name} (ID: {category_id})")
        print(f"From: {source_type} to: {target_type}")
        print(f"Target category: {target_category}")

        # Připojení k databázím
        cat_conn = sqlite3.connect('categories.db')
        cat_cursor = cat_conn.cursor()
        
        pub_conn = sqlite3.connect('publications.db')  # Samostatné připojení pro publikace
        pub_cursor = pub_conn.cursor()
        
        try:
            cat_cursor.execute("BEGIN TRANSACTION")
            pub_cursor.execute("BEGIN TRANSACTION")
            
            # Získání cílové kategorie ID
            target_parent_id = None
            if target_category:
                cat_cursor.execute(f"""
                    SELECT id FROM {target_type}_categories 
                    WHERE name = ? AND parent_id IS NULL
                """, (target_category,))
                result = cat_cursor.fetchone()
                if result:
                    target_parent_id = result[0]
                    print(f"Target parent ID: {target_parent_id}")
            
            # Vložení nové kategorie
            cat_cursor.execute(f"""
                INSERT INTO {target_type}_categories (name, parent_id)
                VALUES (?, ?)
            """, (category_name, target_parent_id))
            
            new_category_id = cat_cursor.lastrowid
            print(f"New category ID: {new_category_id}")
            
            # Přesun podkategorií
            if item.childCount() > 0:
                subcategories = []
                for i in range(item.childCount()):
                    child = item.child(i)
                    subcategories.append((child.text(0), child.data(0, Qt.UserRole)))
                
                for subcat_name, old_subcat_id in subcategories:
                    # Vložení nové podkategorie
                    cat_cursor.execute(f"""
                        INSERT INTO {target_type}_categories (name, parent_id)
                        VALUES (?, ?)
                    """, (subcat_name, new_category_id))
                    
                    new_subcat_id = cat_cursor.lastrowid
                    print(f"Moving subcategory: {subcat_name} ({old_subcat_id} -> {new_subcat_id})")
                    
                    # Aktualizace publikací pro podkategorii
                    pub_cursor.execute("""
                        UPDATE publications 
                        SET category_type = ?, category_id = ?
                        WHERE category_type = ? AND category_id = ?
                    """, (target_type, new_subcat_id, source_type, old_subcat_id))
            
            # Aktualizace publikací hlavní kategorie
            pub_cursor.execute("""
                UPDATE publications 
                SET category_type = ?, category_id = ?
                WHERE category_type = ? AND category_id = ?
            """, (target_type, new_category_id, source_type, category_id))
            
            # Smazání původních kategorií
            cat_cursor.execute(f"""
                DELETE FROM {source_type}_categories
                WHERE id = ? OR parent_id = ?
            """, (category_id, category_id))
            
            cat_conn.commit()
            pub_conn.commit()
            print("Transaction committed successfully")
            
            # Obnovení zobrazení
            self.load_categories()
            
        except Exception as e:
            cat_conn.rollback()
            pub_conn.rollback()
            print(f"Error during category move: {str(e)}")
            print(f"SQL State: {e.__cause__}")
            StyleHelper.create_message_box(
                "Chyba",
                f"Nepodařilo se přesunout kategorii: {str(e)}",
                "warning",
                self
            )
        finally:
            cat_conn.close()
            pub_conn.close()

    def handle_item_drop(self, event):
        """Zpracuje přetažení položky v stromě"""
        item = self.categories_tree.currentItem()
        if not item:
            return
        
        new_parent = self.categories_tree.itemAt(event.pos())
        if new_parent == item:
            return
            
        category_type = self.tab_mapping[self.tab_combo.currentText()]
        
        conn = sqlite3.connect('categories.db')
        cursor = conn.cursor()
        
        try:
            if new_parent:
                # Přesun pod jinou kategorii
                cursor.execute(f"""
                    UPDATE {category_type}_categories
                    SET parent_id = ?
                    WHERE id = ?
                """, (new_parent.data(0, Qt.UserRole), item.data(0, Qt.UserRole)))
            else:
                # Přesun na nejvyšší úroveň
                cursor.execute(f"""
                    UPDATE {category_type}_categories
                    SET parent_id = NULL
                    WHERE id = ?
                """, (item.data(0, Qt.UserRole),))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            StyleHelper.create_message_box(
                "Chyba",
                f"Nepodařilo se přesunout kategorii: {str(e)}",
                "warning",
                self
            )
        finally:
            conn.close()

            
class DraggableTreeWidget(QTreeWidget):
    itemMoved = pyqtSignal(QTreeWidgetItem, QTreeWidgetItem, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.InternalMove)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.dragged_item = None
        self.drop_indicator_pos = QAbstractItemView.OnItem
        self.setIndentation(20)
        self.old_parent = None
        self.old_index = None

    def dragEnterEvent(self, event):
        if event.source() == self:
            self.dragged_item = self.currentItem()
            # Uložení původní pozice
            self.old_parent = self.dragged_item.parent() or self.invisibleRootItem()
            self.old_index = (
                self.old_parent.indexOfChild(self.dragged_item) if self.old_parent != self.invisibleRootItem() 
                else self.indexOfTopLevelItem(self.dragged_item)
            )
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not self.dragged_item:
            event.ignore()
            return

        target = self.itemAt(event.pos())
        if not target:
            event.ignore()
            return

        # Povolení přesunu mezi stejnými úrovněmi a dovnitř kategorií
        current_level = self.dragged_item.parent() is None
        target_level = target.parent() is None

        if current_level != target_level:
            event.ignore()
            return

        rect = self.visualItemRect(target)
        y_pos = event.pos().y()

        # Rozšíření možností drop indikátoru
        if y_pos < rect.top() + rect.height() / 3:
            self.drop_indicator_pos = QAbstractItemView.AboveItem
        elif y_pos > rect.bottom() - rect.height() / 3:
            self.drop_indicator_pos = QAbstractItemView.BelowItem
        else:
            self.drop_indicator_pos = QAbstractItemView.OnItem

        event.accept()
        self.viewport().update()

    def dropEvent(self, event):
        if not self.dragged_item or not self.itemAt(event.pos()):
            event.ignore()
            return

        target = self.itemAt(event.pos())
        new_parent = target.parent() or self.invisibleRootItem()

        # Kontrola úrovně přesunu
        current_level = self.dragged_item.parent() is None
        target_level = target.parent() is None

        if current_level != target_level:
            event.ignore()
            return

        current_index = (
            new_parent.indexOfChild(self.dragged_item) if new_parent != self.invisibleRootItem()
            else self.indexOfTopLevelItem(self.dragged_item)
        )
        
        new_index = (
            new_parent.indexOfChild(target) if new_parent != self.invisibleRootItem()
            else self.indexOfTopLevelItem(target)
        )

        # Úprava indexu podle pozice drop indikátoru
        if self.drop_indicator_pos == QAbstractItemView.BelowItem:
            new_index += 1
        elif self.drop_indicator_pos == QAbstractItemView.OnItem:
            # Přesun jako podpoložky, pokud je indikátor OnItem
            if current_level == target_level:  # Umožnit jen mezi stejnými úrovněmi
                new_parent = target
                new_index = target.childCount()

        try:
            # Provedení přesunu
            if new_parent == self.invisibleRootItem():
                item = self.takeTopLevelItem(current_index)
                self.insertTopLevelItem(new_index if new_index < current_index else new_index - 1, item)
            else:
                if current_level:  # Pokud jde o hlavní kategorii
                    item = self.takeTopLevelItem(current_index)
                    new_parent.insertChild(new_index, item)
                else:  # Pokud jde o podkategorii
                    item = self.dragged_item.parent().takeChild(current_index)
                    new_parent.insertChild(new_index if new_index < current_index else new_index - 1, item)

            self.setCurrentItem(item)
            
            # Emitování signálu o přesunu s novým indexem
            self.itemMoved.emit(
                item, 
                new_parent, 
                self.old_index, 
                new_index if new_index < current_index else new_index - 1
            )
            
            event.accept()

        except Exception as e:
            print(f"Drop error: {str(e)}")
            event.ignore()

        self.dragged_item = None
        self.old_parent = None
        self.old_index = None
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.dragged_item and self.itemAt(self.mapFromGlobal(QCursor.pos())):
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            
            target = self.itemAt(self.mapFromGlobal(QCursor.pos()))
            if target and target != self.dragged_item:
                rect = self.visualItemRect(target)
                pen = QPen(QColor("#00A0FF"))
                pen.setWidth(2)
                painter.setPen(pen)
                
                if self.drop_indicator_pos == QAbstractItemView.AboveItem:
                    painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
                elif self.drop_indicator_pos == QAbstractItemView.BelowItem:
                    painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
                elif self.drop_indicator_pos == QAbstractItemView.OnItem:
                    # Zvýraznění rámečku pro vložení jako podpoložky
                    painter.drawRect(rect)          
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.category_manager = CategoryManager()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Centrální widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Hlavní layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Top window - fixed height 80px
        self.top_window = RoundedWidget("#353535")
        self.top_window.setFixedHeight(80)

        # Vytvořit layout pro top_window
        top_layout = QHBoxLayout(self.top_window)
        StyleHelper.apply_window_background(self.top_window)
        top_layout.setContentsMargins(20, 10, 20, 10)

        # Middle windows
        self.left_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.left_window)
        self.right_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.right_window)
        self.left_window.setMinimumWidth(300)

        # Vytvoření layoutů pro okna
        left_layout = QVBoxLayout(self.left_window)
        right_middle_layout = QVBoxLayout(self.right_window)
        left_layout.setContentsMargins(20, 20, 20, 20)
        right_middle_layout.setContentsMargins(20, 20, 20, 20)

        # Vytvoření kontejnerů pro standardní obsah
        self.standard_left_content = QWidget()
        self.standard_right_content = QWidget()
        standard_left_layout = QVBoxLayout(self.standard_left_content)
        standard_right_layout = QVBoxLayout(self.standard_right_content)
        standard_left_layout.setContentsMargins(0, 0, 0, 0)
        standard_right_layout.setContentsMargins(0, 0, 0, 0)

        # Vytvoření stromu pro standardní obsah
        self.publications_tree = QTreeWidget()
        self.publications_tree.setHeaderHidden(True)
        StyleHelper.apply_treewidget_style(
            self.publications_tree,
            text_color="white",
            font_bold=True,
            font_size=12,
            font_family="Consolas",
            selection_border_color="#666666",
            selection_border_radius=10,
            hover_background_color="#555555",
            hover_border_radius=10
        )
        StyleHelper.enable_clear_selection(self.publications_tree)

        # Rámeček kolem stromu
        framed_tree = StyleHelper.apply_frame_style(
            self.publications_tree, 
            frame_color="#666666", 
            border_width=2, 
            border_radius=15, 
            padding=4
        )
        
        # Přidání stromu do standardního levého obsahu
        standard_left_layout.addWidget(framed_tree)

        # Vytvoření obsahu pro pravou stranu
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Publikace a vyhledávací pole
        self.publications_view = PublicationsView()
        self.publications_model = QtGui.QStandardItemModel()
        self.publications_view.setModel(self.publications_model)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Vyhledat publikaci...")
        self.search_box.textChanged.connect(self.filter_publications)
        StyleHelper.apply_text_widget_style(self.search_box)

        self.publications_view.doubleClicked.connect(self.open_publication_details)

        # Přidání widgetů do content_layout
        content_layout.addWidget(self.search_box)
        content_layout.addWidget(self.publications_view)

        # Rámeček pro pravý obsah
        framed_content = StyleHelper.apply_frame_style(
            content_container,
            frame_color="#666666",
            border_width=2,
            border_radius=15,
            padding=0
        )

        # Přidání obsahu do standardního pravého kontejneru
        standard_right_layout.addWidget(framed_content)

        # Vytvoření kontejnerů pro speciální záložky
        self.search_left_container = FramedContainer()
        self.search_right_container = FramedContainer()
        self.settings_left_container = FramedContainer()
        self.settings_right_container = FramedContainer()

        # Přidání všech kontejnerů do hlavních layoutů
        left_layout.addWidget(self.standard_left_content)
        left_layout.addWidget(self.search_left_container)
        left_layout.addWidget(self.settings_left_container)
        right_middle_layout.addWidget(self.standard_right_content)
        right_middle_layout.addWidget(self.search_right_container)
        right_middle_layout.addWidget(self.settings_right_container)

        # Skrytí všech kontejnerů na začátku
        self.search_left_container.hide()
        self.search_right_container.hide()
        self.settings_left_container.hide()
        self.settings_right_container.hide()

        # Layout pro prostřední okna
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        middle_layout.addWidget(self.left_window, stretch=1)
        middle_layout.addWidget(self.right_window, stretch=2)

        # Bottom windows s novými layouty
        self.bottom_left_window = RoundedWidget("#353535")
        self.bottom_right_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.bottom_left_window)
        StyleHelper.apply_window_background(self.bottom_right_window)

        # Vytvoření základních layoutů pro spodní okna
        self.bottom_left_layout = QVBoxLayout(self.bottom_left_window)
        self.bottom_right_layout = QVBoxLayout(self.bottom_right_window)
        self.bottom_left_layout.setContentsMargins(10, 10, 10, 10)
        self.bottom_right_layout.setContentsMargins(10, 10, 10, 10)

        # Nastavení fixních velikostí
        self.bottom_left_window.setFixedHeight(130)
        self.bottom_right_window.setFixedHeight(130)
        self.bottom_left_window.setMinimumWidth(300)
        self.left_window.setFixedWidth(300)
        self.right_window.setMinimumWidth(800)

        # Vytvoření kontejneru pro tlačítka kategorií
        self.category_button_container = QWidget()
        button_grid = QGridLayout(self.category_button_container)
        button_grid.setSpacing(5)

        # Vytvoření tlačítek pro kategorie
        self.category_buttons = {}
        button_names = ["Přidat kategorii", "Přidat podkategorii", 
                        "Smazat kategorii", "Smazat podkategorii"]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, (name, pos) in enumerate(zip(button_names, positions)):
            button = QPushButton(name)
            if i >= 2:
                StyleHelper.apply_delete_button_style(button)
            else:
                StyleHelper.apply_button_style(button)
            button_grid.addWidget(button, *pos)
            self.category_buttons[name] = button

        # Připojení signálů pro tlačítka kategorií
        self.category_buttons["Přidat kategorii"].clicked.connect(self.add_category)
        self.category_buttons["Přidat podkategorii"].clicked.connect(self.add_subcategory)
        self.category_buttons["Smazat kategorii"].clicked.connect(self.delete_category)
        self.category_buttons["Smazat podkategorii"].clicked.connect(self.delete_subcategory)

        # Přidání kontejneru do levého spodního layoutu
        self.bottom_left_layout.addWidget(self.category_button_container)

        # Tlačítko pro přidání publikace
        self.add_publication_button = QPushButton("Přidat publikaci")
        StyleHelper.apply_button_style(self.add_publication_button)
        self.add_publication_button.setEnabled(False)
        self.add_publication_button.clicked.connect(self.open_add_publication_window)
        self.bottom_right_layout.addWidget(self.add_publication_button, alignment=Qt.AlignCenter)

        # Bottom layout
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.addWidget(self.bottom_left_window, stretch=1)
        bottom_layout.addWidget(self.bottom_right_window, stretch=2)

        # Přidání všech částí do hlavního layoutu
        main_layout.addWidget(self.top_window)
        main_layout.addLayout(middle_layout, stretch=1)
        main_layout.addLayout(bottom_layout)

        # ButtonTabs a Control widget
        self.tabs = ButtonTabs()
        top_layout.addWidget(self.tabs, alignment=Qt.AlignCenter)
        self.tabs.tab_name_changed.connect(self.handle_tab_change)
        
        # Nastavení aktivní záložky podle nastavení
        default_tab = self.settings_manager.get_setting('ui', 'default_tab')
        if default_tab:
            tab_index = list(self.tabs.tab_mapping.keys()).index(default_tab)
            self.tabs.set_active_tab(tab_index)
            self.handle_tab_change(default_tab)

        self.control_widget = ControlWidget(self)
        self.control_widget.setParent(self)
        self.control_widget.move(1090, 10)

        # Connect signálů
        self.publications_tree.itemSelectionChanged.connect(self.update_add_publication_button_state)
        self.publications_tree.itemSelectionChanged.connect(self.save_last_category)

        # Načtení a nastavení výchozí záložky
        default_tab = self.settings_manager.get_setting('ui', 'default_tab')
        if default_tab in self.tabs.tab_mapping:
            tab_index = list(self.tabs.tab_mapping.keys()).index(default_tab)
            self.tabs.set_active_tab(tab_index)
               
        
        self.show_initial_tab()
        # Nastavení výchozí velikosti okna
        self.resize(1150, 900)
        
    def reset_window_sizes(self):
        """Resetuje velikosti všech oken na výchozí hodnoty"""
        # Získání minimální šířky z bottom_left_window pro konzistenci
        left_width = 360
        
        # Fixní šířky pro levá okna
        self.left_window.setFixedWidth(left_width)
        self.bottom_left_window.setFixedWidth(left_width)
        
        # Pravá okna
        self.right_window.setMinimumWidth(800)
        self.bottom_right_window.setMinimumWidth(800)
        
        # Fixní výšky pro horní a spodní okna
        self.top_window.setFixedHeight(80)
        self.bottom_left_window.setFixedHeight(130)
        self.bottom_right_window.setFixedHeight(130)
        
        # Reset výšky prostředních oken
        self.left_window.setFixedHeight(16777215)  # QWIDGETSIZE_MAX
        self.right_window.setFixedHeight(16777215)
            
    
    def update_bottom_windows_content(self, content_type):
        """
        Aktualizuje obsah obou spodních oken podle typu obsahu.
        """
        if content_type == 'standard':
            # Vyčistíme oba layouty
            for layout in [self.bottom_left_layout, self.bottom_right_layout]:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().hide()
                        if not isinstance(item.widget(), (QPushButton, QWidget)):
                            item.widget().setParent(None)

            # Znovu přidáme kontejner s tlačítky do levého layoutu
            self.category_button_container.show()
            if self.bottom_left_layout.indexOf(self.category_button_container) == -1:
                self.bottom_left_layout.addWidget(self.category_button_container)

            # Zobrazíme všechna tlačítka kategorií
            for button in self.category_buttons.values():
                button.show()
                button.setEnabled(True)

            # Znovu přidáme a zobrazíme tlačítko pro přidání publikace
            self.add_publication_button.show()
            if self.bottom_right_layout.indexOf(self.add_publication_button) == -1:
                self.bottom_right_layout.addWidget(self.add_publication_button, alignment=Qt.AlignCenter)
        
        elif content_type == 'search':
            # Skryjeme standardní tlačítka a kontejnery
            self.category_button_container.hide()
            self.add_publication_button.hide()
            
            # Vyčistíme pravé spodní okno
            while self.bottom_right_layout.count():
                item = self.bottom_right_layout.takeAt(0)
                if item.widget():
                    item.widget().hide()
                    if not isinstance(item.widget(), QPushButton):
                        item.widget().setParent(None)
                    
        elif content_type == 'settings':
            # Skryjeme standardní tlačítka a kontejnery
            self.category_button_container.hide()
            self.add_publication_button.hide()
            
    def open_publication_details(self, index_or_id):
        """
        Otevře detail publikace.
        
        Args:
            index_or_id: Může být buď QModelIndex (ze standardního seznamu) nebo int (ID publikace z vyhledávání)
        """
        if isinstance(index_or_id, int):
            # Voláno z výsledků vyhledávání
            pub_id = index_or_id
        else:
            # Voláno ze standardního seznamu publikací
            item = self.publications_model.itemFromIndex(index_or_id)
            pub_id = item.data(QtCore.Qt.UserRole)
        
        # Otevření okna s detaily
        publication_details_window = PublicationDetailsWindow(
            self,
            publication_id=pub_id,
            category_manager=self.category_manager
        )
        publication_details_window.exec_()
        
        # Obnovení zobrazení po zavření okna
        if hasattr(self, 'selected_category') and hasattr(self, 'selected_tab'):
            if self.selected_category and self.selected_tab:
                category_id = self.category_manager.get_category_id(self.selected_tab, self.selected_category)
                self.load_publications_for_category(category_id, self.selected_tab)
        
        # Zrušení focusu a výběru po zavření okna
        self.publications_view.clearSelection()
        self.publications_view.clearFocus()
        
    def load_publications_for_category(self, category_id, category_type):
        self.publications_model.clear()

        conn = sqlite3.connect('publications.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title 
            FROM publications
            WHERE category_id = ? AND category_type = ?
        ''', (category_id, category_type))

        for pub_id, title in cursor.fetchall():
            cover_path = self.find_cover_image(pub_id)
            item = PublicationItem(cover_path, title, pub_id)  # Předání ID publikace
            self.publications_model.appendRow(item)

        conn.close()

    def find_cover_image(self, pub_id):
        pub_dir = f"publications/{pub_id}"
        if os.path.exists(pub_dir):
            for file in os.listdir(pub_dir):
                if file.startswith("cover"):
                    return os.path.join(pub_dir, file)
        return None  # Pokud obrázek neexistuje
 
    
    def init_tree_widget(self):
        self.publications_tree = QTreeWidget()
        self.publications_tree.setHeaderHidden(True)
        self.publications_tree.setColumnCount(1)
        
        # Aplikace stylu
        StyleHelper.apply_tree_widget_style(
            self.publications_tree,
            default_bg="#282c34",
            text_color="#abb2bf",
            border_color="#3e4451",
            selected_border="#666666",
            hover_bg="#3e4451",
            widget_radius=5,
            item_radius=15
        )
        
    def add_category(self):
        """Přidá novou hlavní kategorii do aktuální záložky"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            StyleHelper.create_message_box("Upozornění", "Tato záložka nepodporuje kategorie.", "warning", self)
            return

        name = StyleHelper.create_input_dialog("Nová kategorie", "Zadejte název kategorie:", self)
        if name:
            self.category_manager.add_category(category_type, name)
            self.load_categories_for_current_tab(category_type)


    def add_subcategory(self):
        """Přidá novou podkategorii k vybrané kategorii"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            StyleHelper.create_message_box("Upozornění", "Tato záložka nepodporuje kategorie.", "warning", self)
            return

        selected_items = self.publications_tree.selectedItems()
        if not selected_items:
            StyleHelper.create_message_box("Upozornění", "Prosím vyberte nadřazenou kategorii.", "warning", self)
            return

        parent_item = selected_items[0]
        if parent_item.parent():
            StyleHelper.create_message_box("Upozornění", "Nelze přidat podkategorii k podkategorii.", "warning", self)
            return

        name = StyleHelper.create_input_dialog("Nová podkategorie", "Zadejte název podkategorie:", self)
        if name:
            parent_id = self.category_manager.get_category_id(category_type, parent_item.text(0))
            self.category_manager.add_category(category_type, name, parent_id)
            self.load_categories_for_current_tab(category_type)


    def delete_category(self):
        """Smaže vybranou kategorii a všechny její podkategorie"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            StyleHelper.create_message_box("Upozornění", "Tato záložka nepodporuje kategorie.", "warning", self)
            return

        selected_items = self.publications_tree.selectedItems()
        if not selected_items:
            StyleHelper.create_message_box("Upozornění", "Prosím vyberte kategorii ke smazání.", "warning", self)
            return

        item = selected_items[0]
        if item.parent():
            StyleHelper.create_message_box("Upozornění", "Prosím vyberte hlavní kategorii.", "warning", self)
            return

        # Potvrzovací dialog
        reply = StyleHelper.create_message_box(
            "Potvrzení",
            "Opravdu chcete smazat tuto kategorii a všechny její podkategorie?",
            "question",
            self
        )
        if reply == QDialog.Accepted:
            category_id = self.category_manager.get_category_id(category_type, item.text(0))
            self.category_manager.delete_category(category_type, category_id)
            self.load_categories_for_current_tab(category_type)


    def delete_subcategory(self):
        """Smaže vybranou podkategorii"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            StyleHelper.create_message_box("Upozornění", "Tato záložka nepodporuje kategorie.", "warning", self)
            return

        selected_items = self.publications_tree.selectedItems()
        if not selected_items:
            StyleHelper.create_message_box("Upozornění", "Prosím vyberte podkategorii ke smazání.", "warning", self)
            return

        item = selected_items[0]
        if not item.parent():
            StyleHelper.create_message_box("Upozornění", "Vybraná položka není podkategorie.", "warning", self)
            return

        # Potvrzovací dialog
        reply = StyleHelper.create_message_box(
            "Potvrzení",
            "Opravdu chcete smazat tuto podkategorii?",
            "question",
            self
        )
        if reply == QDialog.Accepted:
            category_id = self.category_manager.get_category_id(category_type, item.text(0))
            self.category_manager.delete_category(category_type, category_id)
            self.load_categories_for_current_tab(category_type)

    def open_add_publication_window(self):
        """Otevře nové externí okno pro přidání publikace."""
        if self.selected_category and self.selected_tab:
            add_publication_window = AddPublications(
                self,
                selected_category=self.selected_category,
                selected_tab=self.selected_tab,
                category_manager=self.category_manager  # Předání category_manager
            )
            add_publication_window.setFixedSize(600, 800)
            add_publication_window.exec_()

            # Po zavření okna pro přidání publikace obnovíme seznam
            category_id = self.category_manager.get_category_id(self.selected_tab, self.selected_category)
            self.load_publications_for_category(category_id, self.selected_tab)

    def update_add_publication_button_state(self):
        """Aktualizuje stav tlačítka 'Přidat publikaci' na základě výběru v stromu."""
        selected_items = self.publications_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            # Uložení vybrané kategorie a záložky
            self.selected_category = item.text(0)
            self.selected_tab = self.tabs.get_current_category_type()
            self.add_publication_button.setEnabled(True)

            # Načtení publikací pro vybranou kategorii/podkategorii
            category_id = self.category_manager.get_category_id(self.selected_tab, self.selected_category)
            self.load_publications_for_category(category_id, self.selected_tab)
        else:
            self.selected_category = None
            self.selected_tab = None
            self.add_publication_button.setEnabled(False)
            self.publications_model.clear()
            
    def open_search_results_window(self, results, search_type):
        # Kontrola, zda již není otevřené externí okno
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and hasattr(widget, 'is_search_results'):
                widget.close()
                widget.deleteLater()
        
        dialog = QDialog(self)
        dialog.is_search_results = True
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        container = RoundedWidget(color="#353535")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 10, 20, 10)

        # Hlavička s tlačítky
        header = self.create_search_results_header(dialog)
        container_layout.addWidget(header)

        # Vytvoření a nastavení widgetu pro výsledky
        results_widget = SearchResultsWidget(settings_manager=self.settings_manager)
        results_widget.result_double_clicked.connect(self.open_publication_details)
        
        # Načtení nastavení pro zobrazení
        settings_manager = self.settings_manager
        default_view = settings_manager.get_setting('ui', 'view', 'default_view', default='Seznam')
        list_columns = settings_manager.get_setting('ui', 'view', 'external_list_columns', default=1)
        grid_columns = settings_manager.get_setting('ui', 'view', 'external_grid_columns', default=4)
        
        # Nastavení dat a typu zobrazení
        results_widget.original_results = results
        results_widget.original_search_type = search_type
        results_widget.is_external_window = True  # Příznak pro externí okno
        results_widget.external_list_columns = list_columns
        results_widget.external_grid_columns = grid_columns
        
        # Vytvoření a nastavení scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(results_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #444444;
                width: 12px;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #666666;
                min-height: 20px;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px;
                width: 0px;
            }
        """)
        
        container_layout.addWidget(scroll_area)
        layout.addWidget(container)

        # Nastavení výchozího zobrazení
        results_widget.list_view_btn.setChecked(default_view == 'Seznam')
        results_widget.grid_view_btn.setChecked(default_view == 'Mřížka')
        
        if default_view == 'Seznam':
            QTimer.singleShot(0, results_widget.switch_to_list_view)
        else:
            QTimer.singleShot(0, results_widget.show_grid_view)

        # Nastavení velikosti okna
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        dialog.resize(width, height)
        dialog.setMinimumSize(800, 600)
        
        StyleHelper.make_draggable(dialog)
        
        QApplication.processEvents()
        dialog.show()
        
        return dialog
        
    def clear_all_containers(self):
        """Vyčistí všechny kontejnery a skryje widgety"""
        # Vyčištění spodních oken
        for layout in [self.bottom_left_layout, self.bottom_right_layout]:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().hide()
                    
        # Skrytí všech kontejnerů
        self.standard_left_content.hide()
        self.standard_right_content.hide()
        self.search_left_container.hide()
        self.search_right_container.hide()
        self.settings_left_container.hide()
        self.settings_right_container.hide()
        
        # Skrytí tlačítek
        self.category_button_container.hide()
        self.add_publication_button.hide()
        
        if hasattr(self, 'advanced_buttons_container'):
            self.advanced_buttons_container.hide()
            
    def handle_tab_change(self, tab_name):
        if tab_name:
            self.clear_all_containers()
            self.reset_window_sizes()
            
            if self.tabs.is_content_tab(tab_name):
                self.show_standard_content()
                category_type = self.tabs.tab_mapping.get(tab_name)
                if category_type:
                    self.load_categories_for_current_tab(category_type)
                    self.publications_view.setViewMode(QtWidgets.QListView.IconMode)
            else:
                self.hide_standard_content()
                if tab_name == "Vyhledávání":
                    self.show_search_content()
                elif tab_name == "Nastavení":
                    self.show_settings_content()

    def load_categories_for_current_tab(self, category_type):
        """Načte kategorie pro aktuální záložku do levého okna"""
        self.publications_tree.clear()
        
        conn = sqlite3.connect('categories.db')
        cursor = conn.cursor()
        
        try:
            # Načtení hlavních kategorií seřazených podle sort_order
            cursor.execute(f"""
                SELECT id, name 
                FROM {category_type}_categories 
                WHERE parent_id IS NULL 
                ORDER BY sort_order
            """)
            
            categories = cursor.fetchall()
            
            for cat_id, cat_name in categories:
                category_item = QTreeWidgetItem([cat_name])
                category_item.setData(0, Qt.UserRole, cat_id)
                self.publications_tree.addTopLevelItem(category_item)
                
                # Načtení podkategorií seřazených podle sort_order
                cursor.execute(f"""
                    SELECT id, name 
                    FROM {category_type}_categories 
                    WHERE parent_id = ? 
                    ORDER BY sort_order
                """, (cat_id,))
                
                subcategories = cursor.fetchall()
                
                for sub_id, sub_name in subcategories:
                    subcategory_item = QTreeWidgetItem([sub_name])
                    subcategory_item.setData(0, Qt.UserRole, sub_id)
                    category_item.addChild(subcategory_item)
                
                # Automatické rozbalení pokud je nastaveno
                if self.settings_manager.get_setting('ui', 'navigation', 'auto_expand_categories', default=False):
                    category_item.setExpanded(True)
            
        except Exception as e:
            print(f"Chyba při načítání kategorií: {e}")
        finally:
            conn.close()

        # Obnovení poslední vybrané kategorie pokud je nastaveno
        if self.settings_manager.get_setting('ui', 'navigation', 'remember_last_category', default=False):
            last_category = self.settings_manager.get_setting('ui', 'navigation', f'last_category_{category_type}')
            if last_category:
                # Projdeme všechny položky a najdeme odpovídající
                for i in range(self.publications_tree.topLevelItemCount()):
                    top_item = self.publications_tree.topLevelItem(i)
                    if top_item.text(0) == last_category:
                        self.publications_tree.setCurrentItem(top_item)
                        break
                    # Kontrola podkategorií
                    for j in range(top_item.childCount()):
                        child_item = top_item.child(j)
                        if child_item.text(0) == last_category:
                            top_item.setExpanded(True)
                            self.publications_tree.setCurrentItem(child_item)
                            break
                
    def show_standard_content(self):
        """Zobrazí standardní obsah pro knihy, časopisy atd."""
        self.standard_left_content.show()
        self.standard_right_content.show()
        
        # Aktualizace spodních oken
        self.update_bottom_windows_content('standard')
        
        # Skrytí ostatního obsahu
        self.search_left_container.hide()
        self.search_right_container.hide()
        self.settings_left_container.hide()
        self.settings_right_container.hide()

        # Znovu zobrazení původních tlačítek v bottom_left_layout
        # (tj. category_button_container)
        self.category_button_container.show()

    def hide_standard_content(self):
        """Skryje standardní obsah"""
        self.standard_left_content.hide()
        self.standard_right_content.hide()
        
        # Vyčištění spodních oken
        self.category_button_container.hide()
        self.add_publication_button.hide()
        
        # Vyčištění dalších kontejnerů
        if hasattr(self, 'settings_menu'):
            self.settings_menu.hide()
        if hasattr(self, 'settings_content'):
            self.settings_content.hide()
            
    def show_search_content(self):
        self.clear_all_containers()
        
        if not hasattr(self, 'search_widget'):
            self.search_widget = SearchWidget(
                settings_manager=self.settings_manager,
                parent=self
            )
            self.search_results_widget = SearchResultsWidget(
                settings_manager=self.settings_manager,
                parent=self
            )
            self.filters_widget = SearchFiltersWidget(parent=self)
            
            self.search_results_widget.result_double_clicked.connect(self.open_publication_details)
            self.search_widget.search_results.connect(self.search_results_widget.show_results)
            self.search_widget.search_results_widget = self.search_results_widget
            
            # Vytvoření informačního labelu pro externí okno
            self.external_info_label = QLabel("Výsledky budou zobrazeny v externím okně")
            self.external_info_label.setAlignment(Qt.AlignCenter)
            self.external_info_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 16pt;
                    font-weight: bold;
                    background-color: transparent;
                    padding: 20px;
                }
            """)
            self.external_info_label.hide()  # Skryjeme label na začátku
            
            self.search_left_container.add_widget(self.search_widget)
            self.search_right_container.add_widget(self.search_results_widget)
            self.search_right_container.add_widget(self.external_info_label)
            self.filters_widget.connect_signals(self.search_widget)
            
            self.advanced_buttons_container = QWidget()
            advanced_buttons_layout = QHBoxLayout(self.advanced_buttons_container)
            advanced_buttons_layout.setContentsMargins(0, 0, 0, 0)
            advanced_buttons_layout.setSpacing(10)

            self.advanced_search_button = QPushButton("Pokročilé vyhledávání")
            self.history_button = QPushButton("Historie vyhledávání")

            StyleHelper.apply_button_style(self.advanced_search_button)
            StyleHelper.apply_button_style(self.history_button)

            self.advanced_search_button.clicked.connect(lambda: self.search_widget.show_advanced_search())
            self.history_button.clicked.connect(lambda: self.search_widget.show_search_history())
            
            advanced_buttons_layout.addStretch()
            advanced_buttons_layout.addWidget(self.advanced_search_button)
            advanced_buttons_layout.addWidget(self.history_button)
            advanced_buttons_layout.addStretch()

        # Kontrola nastavení externího okna
        use_external = self.settings_manager.get_setting('ui', 'view', 'use_external_window', default=False)
        
        if use_external:
            self.search_results_widget.hide()
            self.external_info_label.show()
        else:
            self.search_results_widget.show()
            self.external_info_label.hide()

        self.bottom_left_layout.addWidget(self.advanced_buttons_container, alignment=Qt.AlignCenter)
        self.advanced_buttons_container.show()
        self.search_left_container.show()
        self.search_right_container.show()

    def on_search_results(self, results, search_type):
        print("DEBUG: on_search_results START")
        
        if not results:
            if hasattr(self, 'filters_widget'):
                self.filters_widget.hide()
            return
        
        if hasattr(self, 'filters_widget'):
            print("DEBUG: Aktualizuji filtry")
            self.filters_widget.clear_all_filters()
            
            # Aktualizace umístění a viditelnosti
            if self.bottom_right_layout.indexOf(self.filters_widget) == -1:
                self.bottom_right_layout.addWidget(self.filters_widget)
            
            self.filters_widget.show()
            self.filters_widget.raise_()
            
            # Force update
            self.filters_widget.update()
            self.bottom_right_window.update()
            QApplication.processEvents()
        
        print("DEBUG: Filtry byly aktualizovány a zobrazeny")

    def show_settings_content(self):
        """Zobrazí obsah pro záložku Nastavení"""
        self.clear_all_containers()
        
        # Vytvoření nových widgetů pro nastavení
        self.settings_menu = SettingsMenuWidget()
        self.settings_content = SettingsContentWidget()
        self.settings_menu.pageChanged.connect(self.settings_content.show_page)
        
        # Zachování stejné šířky jako u spodního okna
        left_width = 360  # Použití stejné hodnoty jako v reset_window_sizes
        self.left_window.setFixedWidth(left_width)
        self.right_window.setMinimumWidth(800)
        
        self.settings_left_container.add_widget(self.settings_menu)
        self.settings_right_container.add_widget(self.settings_content)

        self.settings_left_container.show()
        self.settings_right_container.show()

        # Skrytí spodních oken
        self.category_button_container.hide()
        self.add_publication_button.hide()
    
    def center_widget(self, parent_widget, child_widget):
        """Centrovat widget uvnitř rodiče."""
        parent_layout = QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        parent_layout.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(child_widget)
        
    def centerWindow(self):
        """Centrovat hlavní okno na střed obrazovky."""
        qr = self.frameGeometry()
        cp = QApplication.desktop().screen().rect().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showEvent(self, event):
        """Zarovnat okno na střed obrazovky při zobrazení."""
        super().showEvent(event)
        self.centerWindow()
    

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

    def filter_publications(self, text):
        """Filtrování publikací podle textu."""
        for row in range(self.publications_model.rowCount()):
            item = self.publications_model.item(row)
            matches = text.lower() in item.full_title.lower()
            self.publications_view.setRowHidden(row, not matches)
            
    def show_initial_tab(self):
        """Zobrazí výchozí záložku při startu aplikace"""
        default_tab = self.settings_manager.get_setting('ui', 'default_tab')
        if default_tab in self.tabs.tab_mapping:
            tab_index = list(self.tabs.tab_mapping.keys()).index(default_tab)
            self.tabs.set_active_tab(tab_index)
            self.handle_tab_change(default_tab)
            
    def create_search_results_header(self, dialog):
        """Vytvoří hlavičku pro okno s výsledky vyhledávání"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("Výsledky vyhledávání")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)

        # Tlačítko pro změnu velikosti
        resize_btn = QPushButton("□")
        resize_btn.setFixedSize(25, 25)
        button_style = """
            QPushButton {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #FFA500;
            }
        """
        resize_btn.setStyleSheet(button_style)
        
        minimize_btn = QPushButton("_")
        minimize_btn.setFixedSize(25, 25)
        minimize_btn.setStyleSheet(button_style)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setStyleSheet(button_style)

        is_maximized = True
        def toggle_size():
            nonlocal is_maximized
            if is_maximized:
                dialog.resize(800, 600)
                resize_btn.setText("□")
            else:
                dialog.showMaximized()
                resize_btn.setText("❐")
            is_maximized = not is_maximized

        resize_btn.clicked.connect(toggle_size)
        minimize_btn.clicked.connect(dialog.showMinimized)
        close_btn.clicked.connect(dialog.close)

        header_layout.addWidget(title_label, stretch=1, alignment=Qt.AlignTop)
        header_layout.addWidget(resize_btn, alignment=Qt.AlignRight | Qt.AlignTop)
        header_layout.addWidget(minimize_btn, alignment=Qt.AlignRight | Qt.AlignTop)
        header_layout.addWidget(close_btn, alignment=Qt.AlignRight | Qt.AlignTop)

        return header
    
    def save_last_category(self):
        """Uloží poslední vybranou kategorii"""
        if not self.settings_manager.get_setting('ui', 'navigation', 'remember_last_category', default=False):
            return

        selected_items = self.publications_tree.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            category_type = self.tabs.get_current_category_type()
            if category_type:
                self.settings_manager.set_setting(
                    selected_item.text(0), 
                    'ui', 'navigation', 
                    f'last_category_{category_type}'
                )


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(current_dir, 'icons')
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
