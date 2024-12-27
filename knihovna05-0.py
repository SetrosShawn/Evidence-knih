from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, 
                             QTreeWidgetItem, QInputDialog, QGridLayout, QTreeWidget, QListWidget,
                             QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QDesktopWidget, QStackedWidget, QButtonGroup, QSlider, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QPoint, QRectF, QSize, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QBrush
import sys
import sqlite3

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
    
    @staticmethod
    def apply_label_style(label: QLabel, color="#AAAAAA", font_size=12): # Přidána metoda pro label
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {font_size}px;
            }}
        """)
    
class DatabaseManager:
    def __init__(self, db_name="publikace.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Chyba při připojení k databázi: {e}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Chyba při provádění dotazu: {e}")
            return None

    def vytvor_databazi(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS kategorie (
                id INTEGER PRIMARY KEY,
                nazev TEXT,
                parent_id INTEGER,
                je_kategorie INTEGER,
                FOREIGN KEY (parent_id) REFERENCES kategorie(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS publikace (
                id INTEGER PRIMARY KEY,
                nazev TEXT,
                autor TEXT,
                rok_vydani INTEGER,
                kategorie_id INTEGER,
                popis_soubor TEXT,
                obrazek_soubor TEXT,
                pdf_soubor TEXT,
                FOREIGN KEY (kategorie_id) REFERENCES kategorie(id)
            )
            """
        ]
        for query in queries:
            self.execute_query(query)

    def vloz_kategorii(self, nazev, parent_id=None, je_kategorie=1):
        try:
            print(f"Vkládání kategorie: {nazev}, parent_id: {parent_id}, je_kategorie: {je_kategorie}")  # Debugovací výpis
            query = "INSERT INTO kategorie (nazev, parent_id, je_kategorie) VALUES (?, ?, ?)"
            self.execute_query(query, (nazev, parent_id, je_kategorie))
            last_id = self.cursor.lastrowid
            print(f"Kategorie byla vložena s ID: {last_id}")  # Ladicí výpis
            return last_id
        except sqlite3.Error as e:
            print(f"Chyba při vkládání kategorie: {e}")
            return None



    def vloz_publikaci(self, nazev, autor, rok_vydani, kategorie_id, popis_soubor, obrazek_soubor, pdf_soubor):
        query = "INSERT INTO publikace (nazev, autor, rok_vydani, kategorie_id, popis_soubor, obrazek_soubor, pdf_soubor) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.execute_query(query, (nazev, autor, rok_vydani, kategorie_id, popis_soubor, obrazek_soubor, pdf_soubor))

    def nacti_strom_kategorii(self):
        query = "SELECT id, nazev, parent_id FROM kategorie"
        kategorie = self.execute_query(query)

        strom = {}
        polozky = {id: {"nazev": nazev, "parent_id": parent_id, "deti": {}} for id, nazev, parent_id in kategorie}

        for id, data in polozky.items():
            parent_id = data["parent_id"]
            if parent_id is None:
                strom[id] = data
            else:
                if parent_id in polozky:
                    polozky[parent_id]["deti"][id] = data

        return strom

    def vyhledej_publikace_v_kategorii(self, kategorie_id):
        query = "SELECT id, nazev FROM publikace WHERE kategorie_id=?"
        return self.execute_query(query, (kategorie_id,))

    def smaz_kategorii(self, kategorie_id):
        try:
            self.execute_query("DELETE FROM publikace WHERE kategorie_id=?", (kategorie_id,)) # Smazání publikací patřících do kategorie
            self.execute_query("DELETE FROM kategorie WHERE id=?", (kategorie_id,)) # Smazání samotné kategorie
        except sqlite3.Error as e:
            print(f"Chyba při mazání kategorie: {e}")

    def vytvor_indexy(self):
        indexy = [
            "CREATE INDEX IF NOT EXISTS idx_nazev ON publikace (nazev)",
            "CREATE INDEX IF NOT EXISTS idx_autor ON publikace (autor)",
            "CREATE INDEX IF NOT EXISTS idx_rok_vydani ON publikace (rok_vydani)",
            "CREATE INDEX IF NOT EXISTS idx_kategorie ON publikace (kategorie_id)",
            "CREATE INDEX IF NOT EXISTS idx_parent_id ON kategorie (parent_id)"
        ]
        for index in indexy:
            self.execute_query(index)

# Třída pro správu kategorií
class KategorieManager(QObject):
    def __init__(self, tree_widget, db_manager):
        super().__init__()
        self.tree_widget = tree_widget
        self.db_manager = db_manager
        print("KategorieManager inicializován")  # debugovací výpis

    def _ensure_db_connection(self):
        """Zajistí připojení k databázi"""
        if not self.db_manager:
            raise RuntimeError("Database manager není inicializován")
        if not self.db_manager.connect():
            raise RuntimeError("Nelze se připojit k databázi")
        print("Databázové připojení ověřeno")  # debugovací výpis

    def pridat_kategorii(self, nazev=None):
        print("!!! VSTUP DO METODY pridat_kategorii !!!")  # Absolutní kontrola vstupu
        print(f"Přijatý název: {nazev}")
        try:
            print("Metoda pridat_kategorii byla zavolána.")  # Debugovací výpis
            nazev, ok = QInputDialog.getText(None, "Přidat kategorii", "Název kategorie:")
            print(f"Zadaný název: {nazev}, OK: {ok}")  # Výstup hodnoty z dialogu
            if ok and nazev:
                self._ensure_db_connection()
                kategorie_id = self.db_manager.vloz_kategorii(nazev, None, 1)
                print(f"Kategorie ID: {kategorie_id}")  # ID nové kategorie
                if kategorie_id:
                    self.obnov_strom()
            else:
                print("Dialog byl zrušen nebo název je prázdný.")  # Ladicí výpis
        except Exception as e:
            print(f"Chyba při přidávání kategorie: {e}")
            QMessageBox.critical(None, "Chyba", f"Nepodařilo se přidat kategorii: {str(e)}")


    def pridat_podkategorii(self):
        try:
            print("Funkce pridat_podkategorii byla zavolána")  # debugovací výpis
            current_item = self.tree_widget.currentItem()
            if not current_item:
                raise Exception("Není vybrána žádná nadřazená kategorie")

            parent_id = current_item.data(0, Qt.UserRole)
            if parent_id is None:
                raise Exception("Nelze určit ID nadřazené kategorie")

            nazev, ok = QInputDialog.getText(None, "Přidat podkategorii", "Název podkategorie:")
            if ok and nazev:
                print(f"Uživatel zadal název: {nazev}")  # debugovací výpis
                self._ensure_db_connection()
                kategorie_id = self.db_manager.vloz_kategorii(nazev, parent_id, 0)
                if kategorie_id:
                    print(f"Podkategorie úspěšně přidána s ID: {kategorie_id}")
                    self.obnov_strom()
                else:
                    raise Exception("Nepodařilo se vložit podkategorii")
        except Exception as e:
            print(f"Chyba při přidávání podkategorie: {e}")
            QMessageBox.critical(None, "Chyba", f"Nepodařilo se přidat podkategorii: {str(e)}")

    def smazat_kategorii(self):
        try:
            print("Funkce smazat_kategorii byla zavolána")  # debugovací výpis
            current_item = self.tree_widget.currentItem()
            if not current_item:
                raise Exception("Není vybrána žádná kategorie ke smazání")

            kategorie_id = current_item.data(0, Qt.UserRole)
            if kategorie_id is None:
                raise Exception("Nelze určit ID kategorie")

            odpoved = QMessageBox.question(None, "Smazat kategorii",
                "Opravdu chcete smazat tuto kategorii a všechny její podkategorie?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if odpoved == QMessageBox.Yes:
                self._ensure_db_connection()
                self.db_manager.smaz_kategorii(kategorie_id)
                print(f"Kategorie s ID {kategorie_id} byla smazána")
                self.obnov_strom()
        except Exception as e:
            print(f"Chyba při mazání kategorie: {e}")
            QMessageBox.critical(None, "Chyba", f"Nepodařilo se smazat kategorii: {str(e)}")
            
    def smazat_podkategorii(self):
        try:
            print("Funkce smazat_podkategorii byla zavolána")
            current_item = self.tree_widget.currentItem()
            if not current_item:
                raise Exception("Není vybrána žádná podkategorie ke smazání")

            podkategorie_id = current_item.data(0, Qt.UserRole)
            if podkategorie_id is None:
                raise Exception("Nelze určit ID podkategorie")

            odpoved = QMessageBox.question(None, "Smazat podkategorii",
                                            "Opravdu chcete smazat tuto podkategorii?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if odpoved == QMessageBox.Yes:
                self._ensure_db_connection()
                self.db_manager.smaz_kategorii(podkategorie_id) # Voláme upravenou metodu z DatabaseManager
                print(f"Podkategorie s ID {podkategorie_id} byla smazána")
                self.obnov_strom()
        except Exception as e:
            print(f"Chyba při mazání podkategorie: {e}")
            QMessageBox.critical(None, "Chyba", f"Nepodařilo se smazat podkategorii: {str(e)}")

    def obnov_strom(self):
        try:
            print("Obnova stromu kategorií byla zahájena.")  # Debugovací výpis
            self._ensure_db_connection()
            strom_kategorii = self.db_manager.nacti_strom_kategorii()
            print(f"Načtený strom kategorií: {strom_kategorii}")  # Ladicí výpis
            if strom_kategorii is None:
                raise Exception("Nepodařilo se načíst strom kategorií.")
            self.tree_widget.clear()
            self.napln_qtreewidget(self.tree_widget, strom_kategorii)
            self.tree_widget.update()
            print("Obnova stromu kategorií byla dokončena.")  # Debugovací výpis
        except Exception as e:
            print(f"Chyba při obnovování stromu kategorií: {e}")



    def napln_qtreewidget(self, tree_widget, strom, parent_item=None):
        """Pomocná metoda pro naplnění stromu daty."""
        for id, data in strom.items():
            if parent_item:
                item = QTreeWidgetItem(parent_item, [data["nazev"]])
            else:
                item = QTreeWidgetItem(tree_widget, [data["nazev"]])
            item.setData(0, Qt.UserRole, id)
            if data["deti"]:
                self.napln_qtreewidget(tree_widget, data["deti"], item)
                
class ButtonTabs(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.set_active_tab(0)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        button_container = QWidget()
        self.button_layout = QHBoxLayout(button_container)
        self.button_layout.setSpacing(10)
        self.button_layout.setContentsMargins(10, 5, 10, 5)
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True) # DŮLEŽITÉ: Nastavení exkluzivního chování
        self.button_group.buttonClicked.connect(self._on_tab_change)

        self.stack = QStackedWidget()

        layout.addWidget(button_container, alignment=Qt.AlignCenter)
        layout.addWidget(self.stack)

        self.add_default_tabs()

    def add_default_tabs(self):
        tab_names = ["Knihy", "Časopisy", "Datasheets", "Ostatní", "Vyhledávání", "Ostatní funkce"]
        for name in tab_names:
            content = QWidget()
            self.add_tab(name, content)

    def add_tab(self, title, widget):
        button = QPushButton(title)
        button.setCheckable(True)
        button.setFixedSize(120, 30)

        # Přidání stylů pro různé stavy
        StyleHelper.apply_button_style(button)

        self.button_group.addButton(button)
        self.button_layout.addWidget(button)
        self.stack.addWidget(widget)

    def _on_tab_change(self, button):
        index = self.button_group.buttons().index(button)
        self.stack.setCurrentIndex(index)
        self.tab_changed.emit(index)

    def set_active_tab(self, index):
        if 0 <= index < len(self.button_group.buttons()):
            button = self.button_group.buttons()[index]
            button.setChecked(True)
            self.stack.setCurrentIndex(index)

    tab_changed = pyqtSignal(int)
    
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
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Inicializace databáze
        self.db_manager = DatabaseManager()
        self.db_manager.connect()
        self.db_manager.vytvor_databazi()
        self.db_manager.vytvor_indexy()

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
        top_layout.setContentsMargins(20, 10, 20, 10)

        # Vytvoření a přidání ButtonTabs
        self.tabs = ButtonTabs()
        top_layout.addWidget(self.tabs, alignment=Qt.AlignCenter)

        # Middle windows - s vnitřními widgety
        self.left_window = RoundedWidget("#353535")
        self.right_window = RoundedWidget("#353535")

        # TreeWidget pro publikace v levém okně
        self.publications_tree = QTreeWidget()
        self.publications_tree.setHeaderLabel("Publikace")
        self.publications_tree.setColumnCount(1)

        # Nastavení vzhledu TreeWidget
        self.publications_tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item {
                height: 25px;
            }
        """)

        # ListWidget pro náhledy v pravém okně
        self.previews_widget = QListWidget()
        self.previews_widget.setViewMode(QListWidget.IconMode)
        self.previews_widget.setIconSize(QSize(150, 150))
        self.previews_widget.setSpacing(10)
        self.previews_widget.setResizeMode(QListWidget.Adjust)

        # Nastavení vzhledu ListWidget
        self.previews_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
        """)

        # Vytvoření rámečků pomocí StyleHelper
        self.framed_tree = StyleHelper.apply_frame_style(
            self.publications_tree,
            frame_color="#666666",
            border_width=2,
            border_radius=10,
            padding=15
        )

        self.framed_previews = StyleHelper.apply_frame_style(
            self.previews_widget,
            frame_color="#666666",
            border_width=2,
            border_radius=10,
            padding=15
        )

        # Layouty pro prostřední okna
        left_middle_layout = QVBoxLayout(self.left_window)
        left_middle_layout.setContentsMargins(15, 15, 15, 15)
        left_middle_layout.addWidget(self.framed_tree)

        right_middle_layout = QVBoxLayout(self.right_window)
        right_middle_layout.setContentsMargins(15, 15, 15, 15)
        right_middle_layout.addWidget(self.framed_previews)

        # Nastavení minimální šířky pro levé okno
        self.left_window.setMinimumWidth(300)

        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)
        middle_layout.addWidget(self.left_window, stretch=1)
        middle_layout.addWidget(self.right_window, stretch=2)

        # Bottom windows - fixed height 100px
        self.bottom_left_window = RoundedWidget("#353535")
        self.bottom_right_window = RoundedWidget("#353535")
        self.bottom_left_window.setFixedHeight(100)
        self.bottom_right_window.setFixedHeight(100)
        self.bottom_left_window.setMinimumWidth(300)

        # Layout pro bottom_left_window s mřížkou pro tlačítka
        bottom_left_layout = QGridLayout(self.bottom_left_window)
        self.bottom_left_window.setLayout(bottom_left_layout)
        bottom_left_layout.setContentsMargins(10, 10, 10, 10)
        bottom_left_layout.setHorizontalSpacing(5)
        bottom_left_layout.setVerticalSpacing(5)

        # Vytvoření a přidání tlačítek do mřížky S APLIKACÍ STYLU
        button_names = ["Přidat kategorii", "Přidat podkategorii", "Smazat kategorii", "Smazat podkategorii"]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, (name, pos) in enumerate(zip(button_names, positions)):
            button = QPushButton(name)
            if i >= 2:
                StyleHelper.apply_delete_button_style(button)
            else:
                StyleHelper.apply_button_style(button)
            bottom_left_layout.addWidget(button, *pos)

        # Layout pro bottom_right_window s centrováním tlačítka S APLIKACÍ STYLU
        bottom_right_layout = QHBoxLayout(self.bottom_right_window)
        bottom_right_layout.setContentsMargins(10, 10, 10, 10)

        button_right = QPushButton("Přidat publikaci") #opraven překlep "buklikaci" na "publikaci"
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
        
        # Label pro zobrazení aktivní záložky
        self.active_tab_label = QLabel("Aktivní záložka: Knihy") # Výchozí text
        StyleHelper.apply_label_style(self.active_tab_label) # Aplikace stylu
        left_middle_layout.addWidget(self.active_tab_label, alignment=Qt.AlignBottom | Qt.AlignLeft) # Umístění do levého dolního rohu

        # Propojení signálu tab_changed s metodou pro aktualizaci labelu
        self.tabs.tab_changed.connect(self.update_active_tab_label)
        
        # Control widget
        self.control_widget = ControlWidget(self)
        self.control_widget.setParent(self)
        self.control_widget.move(1045, 10)

        # Správná inicializace KategorieManager
        self.kategorie_manager = KategorieManager(self.publications_tree, self.db_manager)

        # Vytvoření Entry pole PRO ZADÁVÁNÍ TEXTU - POUZE JEDNOU A UVNITŘ LAYOUTU
        self.kategorie_entry = QLineEdit(self.bottom_left_window)
        bottom_left_layout.addWidget(self.kategorie_entry, 0, 2) # Přidání do layoutu

        self.setup_buttons()
        print("Setup buttons volán.")
        print("Konec inicializace MainWindow.")

        self.resize(1150, 900)
        self.nacti_data()
        
        
    def update_active_tab_label(self, index):
        """Aktualizuje label s názvem aktivní záložky."""
        tab_names = ["Knihy", "Časopisy", "Datasheets", "Ostatní", "Vyhledávání", "Ostatní funkce"]
        if 0 <= index < len(tab_names):
            self.active_tab_label.setText(f"Aktivní záložka: {tab_names[index]}")
        else:
            self.active_tab_label.setText("Aktivní záložka: Neznámá")
            
    def pridat_kategorii_z_ui(self):
        """Získá název kategorie z UI a zavolá metodu v KategorieManager"""
        text = self.kategorie_entry.text().strip()
        if text:
            try:
                self.kategorie_manager.pridat_kategorii(text)
                self.kategorie_entry.clear() # Vymaže textové pole po přidání
            except Exception as e:
                print(f"Chyba při přidávání kategorie: {e}")
        else:
            print("VAROVÁNÍ: Nelze přidat kategorii s prázdným názvem.")

    def pridat_podkategorii_z_ui(self):
        """Získá název podkategorie z UI a zavolá metodu v KategorieManager"""
        text = self.kategorie_entry.text().strip()
        if text:
            try:
                self.kategorie_manager.pridat_podkategorii(text)
                self.kategorie_entry.clear()
            except Exception as e:
                print(f"Chyba při přidávání podkategorie: {e}")
        else:
            print("VAROVÁNÍ: Nelze přidat podkategorii s prázdným názvem.")

    # Obdobně definujte metody pro ostatní akce (upravit, smazat kategorii/podkategorii)            
    
    def setup_buttons(self):
        """Nastavení propojení tlačítek s akcemi"""

        print("ZAČÁTEK setup_buttons()") # Úplný začátek

        buttons = self.bottom_left_window.findChildren(QPushButton)
        print(f"Nalezeno tlačítek: {len(buttons)}")
        print(f"Typ buttons: {type(buttons)}") # Vytiskne typ 'buttons'

        if not buttons:
            print("CHYBA: Nebyla nalezena žádná tlačítka v bottom_left_window!")
            return

        button_actions = {
            "Přidat kategorii": self.pridat_kategorii_z_ui,
            "Přidat podkategorii": self.pridat_podkategorii_z_ui,
            "Smazat kategorii": self.kategorie_manager.smazat_kategorii,
            "Smazat podkategorii": self.kategorie_manager.smazat_podkategorii,
        }
        print(f"button_actions: {button_actions}") # Vytiskne obsah slovníku

        for button in buttons:
            print(f"Zpracovává se tlačítko: {button.text()}")
            print(f"Typ button: {type(button)}") # Vytiskne typ 'button'
            action = button_actions.get(button.text())
            print(f"Akce pro tlačítko '{button.text()}': {action}") # Vytiskne akci

            if not action:
                print(f"VAROVÁNÍ: Pro tlačítko '{button.text()}' není definována žádná akce!")
                continue

            try:
                if button.text() in ("Přidat kategorii", "Přidat podkategorii"):
                    print("Kontrola pro přidávání kategorií/podkategorií")
                    print(f"Typ self.kategorie_entry: {type(self.kategorie_entry)}") #Typ self.kategorie_entry
                    print(f"Je self.kategorie_entry instancí QLineEdit?: {isinstance(self.kategorie_entry, QLineEdit)}") #Je instance?

                    text = self.kategorie_entry.text().strip()
                    print(f"Text z kategorie_entry: '{text}'") #Vypíše text z entry
                    if text:
                        button.clicked.connect(action)
                        print(f"Připojeno přidávání: {button.text()}")
                    else:
                        print("VAROVÁNÍ: Nelze přidat kategorii s prázdným názvem.")
                else:
                    button.clicked.connect(action)
                    print(f"Připojeno ostatní: {button.text()}")

                print(f"Úspěšně připojeno tlačítko: {button.text()}")
            except Exception as e:
                print(f"CHYBA při připojování tlačítka {button.text()}: {e}")

        print("KONEC setup_buttons()") # Úplný konec

                    
    # Implementace inicializace stromu kategorií a jejich kontrola
    def inicializace_stromu(self):
        try:
            if self.db_manager.connect():
                strom_kategorii = self.db_manager.nacti_strom_kategorii()
                if strom_kategorii:
                    self.kategorie_manager.napln_qtreewidget(self.publications_tree, strom_kategorii)
                    print("Strom kategorií úspěšně inicializován.")
                else:
                    print("Databáze je prázdná nebo nebyl nalezen žádný obsah.")
        except Exception as e:
            print(f"Chyba při inicializaci stromu kategorií: {e}")
            
    def nacti_data(self):
        """Načte data z databáze do TreeWidget."""
        if self.db_manager and self.db_manager.connect():
            strom_kategorii = self.db_manager.nacti_strom_kategorii()
            self.publications_tree.clear()
            self.kategorie_manager.napln_qtreewidget(self.publications_tree, strom_kategorii)


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
        
    def closeEvent(self, event):
        """Obsluha události zavírání okna."""
        if self.db_manager:  # Kontrola, zda db_manager existuje
            self.db_manager.disconnect() # Odpojení od databáze
        super().closeEvent(event) # Volání původní metody closeEvent pro standardní chování zavírání okna
    
    def set_theme(self, is_dark):
        if is_dark:
            app.setStyleSheet(DARK_THEME)
            self.top_window.color = "#353535"
            self.left_window.color = "#353535"
            self.right_window.color = "#353535"
            self.bottom_left_window.color = "#353535"
            self.bottom_right_window.color = "#353535"
        else:
            app.setStyleSheet(LIGHT_THEME)
            self.top_window.color = "#f0f0f0"
            self.left_window.color = "#f0f0f0"
            self.right_window.color = "#e0e0e0"
            self.bottom_left_window.color = "#f0f0f0"
            self.bottom_right_window.color = "#e0e0e0"
        
        # Vynutit překreslení všech oken
        self.top_window.update()
        self.left_window.update()
        self.right_window.update()
        self.bottom_left_window.update()
        self.bottom_right_window.update()

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
