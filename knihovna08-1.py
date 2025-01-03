from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, 
                             QTreeWidgetItem, QInputDialog, QGridLayout, QTreeWidget, QListWidget,
                             QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QDesktopWidget, QStackedWidget, QButtonGroup, QSlider, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QPoint, QRectF, QSize, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QBrush, QPixmap, QIcon
import sys
import sqlite3
import os


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
    def apply_tree_font_style(tree_widget, font_family="Arial", font_size=14, bold=True):
        """
        Metoda pro změnu písma ve stromovém menu.
        :param tree_widget: Instance QTreeWidget, na kterou se má aplikovat styl.
        :param font_family: Rodina fontu (např. "Arial").
        :param font_size: Velikost písma.
        :param bold: Zda má být písmo tučné.
        """
        font = tree_widget.font()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        tree_widget.setFont(font)
        

    @staticmethod
    def get_icon_path(icon_name):
        """Získá absolutní cestu k ikoně a ověří její existenci"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(current_dir, 'icons')
        icon_path = os.path.join(icons_dir, icon_name)
        
        if not os.path.exists(icons_dir):
            try:
                os.makedirs(icons_dir)
                print(f"Vytvořena složka pro ikony: {icons_dir}")
            except Exception as e:
                print(f"Nepodařilo se vytvořit složku icons: {e}")
        
        if not os.path.exists(icon_path):
            icon_path = os.path.join(current_dir, icon_name)
        
        if os.path.exists(icon_path):
            print(f"Nalezena ikona: {icon_path}")
            return icon_path.replace('\\', '/')
        else:
            print(f"Ikona nebyla nalezena: {icon_name}")
            return None

    @staticmethod
    def apply_treewidget_style(tree_widget, background_color="#2B2B2B", text_color="white",
                               font_family="Arial", font_size=12, font_bold=False, font_italic=False,
                               selection_border_color="#00A0FF", selection_border_radius=5,
                               hover_background_color="#444444", hover_border_radius=3):
        """Globální metoda pro stylování QTreeWidget."""

        font_style = ""
        if font_bold:
            font_style += "bold "
        if font_italic:
            font_style += "italic "

        tree_widget.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {background_color};
                border: none;
                font-family: "{font_family}";
                font-size: {font_size}pt;
                font-style: {font_style}; /* Aplikace stylu písma */
                color: {text_color};
                show-decoration-selected: 1;
                outline: none;
            }}

            QTreeWidget::item {{
                height: 25px;
                color: {text_color};
            }}

            QTreeWidget::item:selected {{
                background: transparent; /* Odstraněno modré pozadí */
                border: 4px solid {selection_border_color};
                border-radius: {selection_border_radius}px;
                margin: 0px;
            }}
            
            QTreeWidget::indicator {{
                width: 20px;
                height: 20px;
                background: none;
            }}
            
            QTreeWidget::indicator:checked {{
                background: transparent;
                border: none;
            }}
            
            QTreeWidget::branch:selected {{
                background-color: transparent; /* Odstranění modrého pozadí */
            }}
            
            QTreeWidget::branch:open {{
                background-color: transparent; /* Transparentní pozadí u otevřených větví */
            }}

            QTreeWidget::item:hover {{
                background-color: {hover_background_color};
                border-radius: {hover_border_radius}px;
                padding: 0px;
            }}

            QTreeWidget::branch {{
                color: #666666;
            }}
            QTreeWidget::branch:has-children:!has-siblings:adjoins-item {{
                border-image: url(none);
            }}
            QTreeWidget::branch:has-children:has-siblings:adjoins-item {{
                border-image: url(none);
            }}
            QTreeWidget::item:hover {{
                background-color: #555555;
                border: 1px solid #777777; /* Přidáno ohraničení při najetí */
                border-radius: {hover_border_radius}px;
                padding: 0px;
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
        
# Nastavení vlastní třídy pro TreeWidget pro správu ikon
class CustomTreeWidget(QTreeWidget):
    def drawBranches(self, painter, rect, index):
        if not index.parent().isValid():  # Pro položky nejvyšší úrovně
            is_expanded = self.isExpanded(index)
            icon = self.property("minus_icon" if is_expanded else "plus_icon")
                
            if icon:
                icon_size = QSize(20, 20)
                icon_rect = QRect(rect.x(), rect.y(), icon_size.width(), icon_size.height())
                icon.paint(painter, icon_rect)
        else:
            super().drawBranches(painter, rect, index)
        
class CategoryManager:
    def __init__(self, db_name='categories.db'):
        self.db_name = db_name
        self.init_database()
    
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
            "Ostatní funkce": None
        }
        
        # Vytvoření tlačítka pro každou záložku
        for tab_name in self.tab_mapping.keys():
            self.add_tab(tab_name)

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
        # Nastaví konkrétní záložku jako aktivní
        if 0 <= index < len(self.button_group.buttons()):
            button = self.button_group.buttons()[index]
            button.setChecked(True)

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
        
class CustomTreeWidget(QTreeWidget):
    def drawBranches(self, painter, rect, index):
        is_expanded = self.isExpanded(index)
        icon = QIcon(":/arrow_down.svg" if is_expanded else ":/arrow_right.svg")
        if icon:
            icon_size = QSize(16, 16)
            icon.paint(painter, QRect(rect.x(), rect.y(), icon_size.width(), icon_size.height()))
        super().drawBranches(painter, rect, index)

        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
        StyleHelper.apply_window_background(self.top_window)
        self.right_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.top_window)
        
        
        # Vytvoření stromu
        self.publications_tree = QTreeWidget()
        self.publications_tree.setHeaderHidden(True)
        self.publications_tree.expandsOnDoubleClick = True
        self.publications_tree.setAutoExpandDelay(-1)
        
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
        
        # Rámeček kolem stromu
        framed_tree = StyleHelper.apply_frame_style(
            self.publications_tree, 
            frame_color="#666666", 
            border_width=2, 
            border_radius=6, 
            padding=4
        )
        
        # Přidání stromu do levého layoutu
        left_layout = QVBoxLayout(self.left_window)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.addWidget(framed_tree)
        
        # ListWidget pro náhledy v pravém okně
        self.previews_widget = QListWidget()
        self.previews_widget.setViewMode(QListWidget.IconMode)
        self.previews_widget.setIconSize(QSize(150, 150))
        self.previews_widget.setSpacing(10)
        self.previews_widget.setResizeMode(QListWidget.Adjust)
        
        self.previews_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
        """)

        self.framed_previews = StyleHelper.apply_frame_style(
            self.previews_widget,
            frame_color="#666666",
            border_width=2,
            border_radius=15,
            padding=15
        )

        # Layouty pro prostřední okna
        self.left_window.setMinimumWidth(300)

        right_middle_layout = QVBoxLayout(self.right_window)
        right_middle_layout.setContentsMargins(15, 15, 15, 15)
        right_middle_layout.addWidget(self.framed_previews)

        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        middle_layout.addWidget(self.left_window, stretch=1)
        middle_layout.addWidget(self.right_window, stretch=2)

        # Bottom windows
        self.bottom_left_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.top_window)
        self.bottom_right_window = RoundedWidget("#353535")
        StyleHelper.apply_window_background(self.top_window)
        self.bottom_left_window.setFixedHeight(100)
        self.bottom_right_window.setFixedHeight(100)
        self.bottom_left_window.setMinimumWidth(300)

        # Layout pro bottom_left_window
        bottom_left_layout = QGridLayout(self.bottom_left_window)
        bottom_left_layout.setContentsMargins(10, 10, 10, 10)
        bottom_left_layout.setHorizontalSpacing(5)
        bottom_left_layout.setVerticalSpacing(5)

        # Vytvoření a přidání tlačítek do mřížky
        button_names = ["Přidat kategorii", "Přidat podkategorii", "Smazat kategorii", "Smazat podkategorii"]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        self.category_buttons = {}
        for i, (name, pos) in enumerate(zip(button_names, positions)):
            button = QPushButton(name)
            if i >= 2:
                StyleHelper.apply_delete_button_style(button)
            else:
                StyleHelper.apply_button_style(button)
            bottom_left_layout.addWidget(button, *pos)
            self.category_buttons[name] = button

        # Layout pro bottom_right_window
        bottom_right_layout = QHBoxLayout(self.bottom_right_window)
        bottom_right_layout.setContentsMargins(10, 10, 10, 10)

        button_right = QPushButton("Přidat publikaci")
        StyleHelper.apply_button_style(button_right)
        bottom_right_layout.addWidget(button_right, alignment=Qt.AlignCenter)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.addWidget(self.bottom_left_window, stretch=1)
        bottom_layout.addWidget(self.bottom_right_window, stretch=2)

        # Přidání oken do hlavního layoutu
        main_layout.addWidget(self.top_window)
        main_layout.addLayout(middle_layout, stretch=1)
        main_layout.addLayout(bottom_layout)

        # ButtonTabs
        self.tabs = ButtonTabs()
        top_layout.addWidget(self.tabs, alignment=Qt.AlignCenter)
        self.tabs.tab_name_changed.connect(self.handle_tab_change)
        
        # Control widget
        self.control_widget = ControlWidget(self)
        self.control_widget.setParent(self)
        self.control_widget.move(1045, 10)

        # Připojení signálů pro tlačítka kategorií
        self.category_buttons["Přidat kategorii"].clicked.connect(self.add_category)
        self.category_buttons["Přidat podkategorii"].clicked.connect(self.add_subcategory)
        self.category_buttons["Smazat kategorii"].clicked.connect(self.delete_category)
        self.category_buttons["Smazat podkategorii"].clicked.connect(self.delete_subcategory)

        self.resize(1150, 900)
        self.handle_tab_change("Knihy")
        
    
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
            QMessageBox.warning(self, 'Upozornění', 'Tato záložka nepodporuje kategorie.')
            return

        name, ok = QInputDialog.getText(self, 'Nová kategorie', 'Zadejte název kategorie:')
        if ok and name:
            # Použijeme category_manager z hlavního okna
            self.category_manager.add_category(category_type, name)
            self.load_categories_for_current_tab(category_type)

    def add_subcategory(self):
        """Přidá novou podkategorii k vybrané kategorii"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            QMessageBox.warning(self, 'Upozornění', 'Tato záložka nepodporuje kategorie.')
            return

        # Použijeme publications_tree z hlavního okna místo neexistujícího atributu v ButtonTabs
        selected_items = self.publications_tree.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, 'Upozornění', 'Prosím vyberte nadřazenou kategorii.')
            return
            
        parent_item = selected_items[0]
        if parent_item.parent():
            QMessageBox.warning(self, 'Upozornění', 'Nelze přidat podkategorii k podkategorii.')
            return
            
        name, ok = QInputDialog.getText(self, 'Nová podkategorie', 'Zadejte název podkategorie:')
        if ok and name:
            parent_id = self.category_manager.get_category_id(category_type, parent_item.text(0))
            self.category_manager.add_category(category_type, name, parent_id)
            self.load_categories_for_current_tab(category_type)

    def delete_category(self):
        """Smaže vybranou kategorii a všechny její podkategorie"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            QMessageBox.warning(self, 'Upozornění', 'Tato záložka nepodporuje kategorie.')
            return

        # Použijeme publications_tree z hlavního okna
        selected_items = self.publications_tree.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, 'Upozornění', 'Prosím vyberte kategorii ke smazání.')
            return
            
        item = selected_items[0]
        if item.parent():
            QMessageBox.warning(self, 'Upozornění', 'Prosím vyberte hlavní kategorii.')
            return

        reply = QMessageBox.question(self, 'Potvrzení', 
                                'Opravdu chcete smazat tuto kategorii a všechny její podkategorie?',
                                QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            category_id = self.category_manager.get_category_id(category_type, item.text(0))
            self.category_manager.delete_category(category_type, category_id)
            self.load_categories_for_current_tab(category_type)

    def delete_subcategory(self):
        """Smaže vybranou podkategorii"""
        category_type = self.tabs.get_current_category_type()
        if not category_type:
            QMessageBox.warning(self, 'Upozornění', 'Tato záložka nepodporuje kategorie.')
            return

        # Použijeme publications_tree z hlavního okna
        selected_items = self.publications_tree.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, 'Upozornění', 'Prosím vyberte podkategorii ke smazání.')
            return
            
        item = selected_items[0]
        if not item.parent():
            QMessageBox.warning(self, 'Upozornění', 'Vybraná položka není podkategorie.')
            return
            
        reply = QMessageBox.question(self, 'Potvrzení', 
                                'Opravdu chcete smazat tuto podkategorii?',
                                QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            category_id = self.category_manager.get_category_id(category_type, item.text(0))
            self.category_manager.delete_category(category_type, category_id)
            self.load_categories_for_current_tab(category_type)

    def handle_tab_change(self, tab_name):
        """Zpracuje změnu záložky a aktualizuje strom kategorií"""
        category_type = self.tabs.tab_mapping.get(tab_name)
        if category_type:
            self.load_categories_for_current_tab(category_type)

    def load_categories_for_current_tab(self, category_type):
        """Načte kategorie pro aktuální záložku do levého okna"""
        self.publications_tree.clear()
        
        categories = self.category_manager.load_categories(category_type)
        for category in categories:
            category_item = QTreeWidgetItem([category['name']])
            self.publications_tree.addTopLevelItem(category_item)
            
            for sub_id, sub_name in category['subcategories']:
                subcategory_item = QTreeWidgetItem([sub_name])
                category_item.addChild(subcategory_item)

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

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(current_dir, 'icons')
    print(f"Aktuální adresář: {current_dir}")
    print(f"Adresář s ikonami: {icons_dir}")
    print(f"Existuje složka icons? {os.path.exists(icons_dir)}")
    print(f"Obsah složky icons: {os.listdir(icons_dir) if os.path.exists(icons_dir) else 'složka neexistuje'}")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
