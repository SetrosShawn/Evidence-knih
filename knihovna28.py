import tkinter as tk
from tkinter import ttk
from tkinter import filedialog  # Pro výběr souborů (obrázek, PDF)
from tkinter import messagebox  # Pro zobrazování chybových hlášek a upozornění
from PIL import Image, ImageTk  # Pro zobrazení náhledu obrázků (vyžaduje Pillow knihovnu)
import json  # Pro práci se souborem JSON
import shutil
from PyPDF2 import PdfReader
import os
from tkinter import simpledialog
import uuid
import win32print
import win32ui
import ctypes
from ctypes import wintypes
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPainter, QFont
import sqlite3

class CategoryManager:
    def __init__(self, treeview, tab_name, parent_app):
        self.treeview = treeview
        self.tab_name = tab_name
        self.category_data = self.load_categories()
        self.parent_app = parent_app  # Odkaz na hlavní aplikaci

    def load_categories(self):
        """Načte kategorie ze souboru categories.json s validací dat."""
        try:
            with open("categories.json", "r", encoding="utf-8") as file:
                categories = json.load(file)

                # Validace struktury dat
                if not isinstance(categories, dict):
                    raise ValueError("Neplatná struktura dat v souboru categories.json.")
                
                for tab_name, category_data in categories.items():
                    if not isinstance(category_data, dict):
                        raise ValueError(f"Neplatná struktura dat pro záložku '{tab_name}'.")
                    for category, subcategories in category_data.items():
                        if not isinstance(subcategories, dict):
                            raise ValueError(f"Neplatná struktura podkategorií v kategorii '{category}'.")

                return categories

        except (FileNotFoundError, json.JSONDecodeError):
            # Pokud soubor neexistuje nebo je prázdný, vrátíme prázdnou strukturu
            return {tab: {} for tab in ["Knihy", "Časopisy", "Datasheets", "Ostatní"]}
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při načítání kategorií: {e}")
            return {tab: {} for tab in ["Knihy", "Časopisy", "Datasheets", "Ostatní"]}


    def save_categories(self):
        """Uloží aktuální stromovou strukturu kategorií do souboru categories.json."""
        try:
            self.parent_app.save_json_file("categories.json", self.category_data)
        except Exception as e:
            print(f"Chyba při ukládání kategorií: {e}")
            messagebox.showerror("Chyba", f"Došlo k chybě při ukládání kategorií: {e}")


    def add_category(self):
        """Přidá novou kategorii do stromové struktury."""
        category_name = simpledialog.askstring("Nová kategorie", "Zadejte název nové kategorie:")
        if not category_name:
            return  # Uživatel stiskl "Zrušit" nebo nezadal nic

        # Validace: Kontrola duplicit
        if category_name in self.category_data.get(self.tab_name, {}):
            messagebox.showerror("Chyba", f"Kategorie '{category_name}' již existuje v záložce '{self.tab_name}'.")
            return

        try:
            # Přidání nové kategorie
            self.category_data.setdefault(self.tab_name, {})[category_name] = {}
            self.save_categories()
            self.load_tree()  # Načtení stromového zobrazení
            messagebox.showinfo("Úspěch", f"Kategorie '{category_name}' byla úspěšně přidána.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Došlo k chybě při přidávání kategorie: {e}")


    def add_subcategory(self):
        """Přidá novou podkategorii do vybrané kategorie."""
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Varování", "Nejdříve vyberte kategorii, do které chcete přidat podkategorii.")
            return

        category_name = self.treeview.item(selected_item[0], "text")
        subcategory_name = simpledialog.askstring("Nová podkategorie", f"Zadejte název nové podkategorie pro kategorii '{category_name}':")
        if not subcategory_name:
            return  # Uživatel stiskl "Zrušit" nebo nezadal nic

        # Validace: Kontrola duplicit ve stejné kategorii
        if subcategory_name in self.category_data.get(self.tab_name, {}).get(category_name, {}):
            messagebox.showerror("Chyba", f"Podkategorie '{subcategory_name}' již existuje v kategorii '{category_name}' záložky '{self.tab_name}'.")
            return

        try:
            # Přidání nové podkategorie
            self.category_data.setdefault(self.tab_name, {}).setdefault(category_name, {})[subcategory_name] = {}
            self.save_categories()
            self.load_tree()  # Načtení stromového zobrazení
            messagebox.showinfo("Úspěch", f"Podkategorie '{subcategory_name}' byla úspěšně přidána do kategorie '{category_name}'.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Došlo k chybě při přidávání podkategorie: {e}")

   
    def validate_category(self, category_name, subcategory_name=None):
        """Zkontroluje, zda kategorie nebo podkategorie již existuje."""
        if subcategory_name:
            # Validace podkategorie
            return subcategory_name in self.category_data.get(self.tab_name, {}).get(category_name, {})
        else:
            # Validace kategorie
            return category_name in self.category_data.get(self.tab_name, {})

    def load_tree(self):
        """Načte strukturu kategorií a podkategorií do stromového zobrazení."""
        self.treeview.delete(*self.treeview.get_children())
        categories = self.category_data.get(self.tab_name, {})
        for category, subcategories in categories.items():
            category_id = self.treeview.insert("", "end", text=category, open=False)
            if isinstance(subcategories, dict):
                for subcategory in subcategories.keys():
                    self.treeview.insert(category_id, "end", text=subcategory, open=False)

    def remove_category(self):
        """Odstraní vybranou kategorii."""
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Varování", "Nejdříve vyberte kategorii, kterou chcete smazat.")
            return

        selected_category = self.treeview.item(selected_item[0], "text")

        # Potvrzovací dialog
        confirm = messagebox.askyesno("Potvrzení", f"Opravdu chcete smazat kategorii '{selected_category}' a všechny její publikace?")
        if not confirm:
            return

        try:
            if selected_category in self.category_data[self.tab_name]:
                del self.category_data[self.tab_name][selected_category]
                self.save_categories()
                self.load_tree()  # Načtení stromového zobrazení
                messagebox.showinfo("Úspěch", f"Kategorie '{selected_category}' byla úspěšně smazána.")
            else:
                messagebox.showerror("Chyba", f"Kategorie '{selected_category}' nebyla nalezena.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Došlo k chybě při mazání kategorie: {e}")


    def remove_subcategory(self):
        """Odstraní vybranou podkategorii."""
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("Varování", "Nejdříve vyberte podkategorii, kterou chcete smazat.")
            return

        selected_subcategory = self.treeview.item(selected_item[0], "text")
        parent_item = self.treeview.parent(selected_item[0])

        if not parent_item:
            messagebox.showerror("Chyba", "Pro smazání podkategorie musíte vybrat platnou podkategorii.")
            return

        selected_category = self.treeview.item(parent_item, "text")

        # Potvrzovací dialog
        confirm = messagebox.askyesno("Potvrzení", f"Opravdu chcete smazat podkategorii '{selected_subcategory}' a všechny její publikace?")
        if not confirm:
            return

        try:
            if selected_subcategory in self.category_data[self.tab_name].get(selected_category, {}):
                del self.category_data[self.tab_name][selected_category][selected_subcategory]
                self.save_categories()
                self.load_tree()  # Načtení stromového zobrazení
                messagebox.showinfo("Úspěch", f"Podkategorie '{selected_subcategory}' byla úspěšně smazána.")
            else:
                messagebox.showerror("Chyba", f"Podkategorie '{selected_subcategory}' nebyla nalezena.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Došlo k chybě při mazání podkategorie: {e}")


    def delete_publication_files(self, publications):
        """Odstraní celou složku publikace na základě ID."""
        if isinstance(publications, list):  # Pokud jde o seznam publikací
            for publication in publications:
                publication_id = publication.get("id")
                if publication_id:
                    publication_folder = os.path.join("Soubory", publication_id)
                    if os.path.exists(publication_folder):
                        shutil.rmtree(publication_folder)  # Smaže celou složku
        elif isinstance(publications, dict):  # Pokud jde o slovník podkategorií
            for subcategory in publications.values():
                if isinstance(subcategory, dict):
                    self.delete_publication_files(subcategory.get("publikace", []))


class PublicationManager:
    def __init__(self, tab_name, data_file="publications.json"):
        self.tab_name = tab_name
        self.data_file = data_file
        self.publication_data = self.load_publications()

    def load_publications(self):
        """Načte publikace ze souboru JSON a doplní dynamické cesty."""
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    for publication in category_data.get("publikace", []):
                        if "id" in publication:
                            publication_folder = os.path.join("Soubory", publication["id"])
                            publication["image_path"] = os.path.join(publication_folder, "image.png")
                            publication["pdf_path"] = os.path.join(publication_folder, "file.pdf")
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"Knihy": {}, "Časopisy": {}, "Datasheets": {}, "Ostatní": {}}

    def save_publications(self):
        with open(self.data_file, "w", encoding="utf-8") as file:
            json.dump(self.publication_data, file, ensure_ascii=False, indent=4)

    def add_publication(self, category, subcategory, details):
        target = subcategory if subcategory else category
        if target not in self.publication_data[self.tab_name]:
            self.publication_data[self.tab_name][target] = []
        self.publication_data[self.tab_name][target].append(details)
        self.save_publications()

    def get_publications(self, category, subcategory):
        target = subcategory if subcategory else category
        return self.publication_data[self.tab_name].get(target, [])

class AddPublicationDialog:
    def __init__(self, parent, title):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Atributy pro obrázek a PDF
        self.result = None
        self.image_path = ""
        self.pdf_path = ""
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Přidáme vstupní pole pro publikaci (název, autor, rok, popis) a tlačítka pro nahrání obálky a PDF
        ttk.Label(main_frame, text="Název publikace:").pack(anchor=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        # Další pole (např. pro autora, rok vydání atd.)...

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        # Tlačítka pro potvrzení a zrušení
        ttk.Button(btn_frame, text="Zrušit", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Přidat publikaci", command=self.confirm).pack(side=tk.RIGHT)

    def confirm(self):
        # Validace a uložení zadaných údajů
        self.result = {
            "title": self.title_entry.get(),
            # Další údaje zde...
        }
        self.dialog.destroy()

class PridatPublikaciDialog:
    def __init__(self, parent, category, subcategory, on_save_callback):
        self.publication_id = str(uuid.uuid4())  # Generování unikátního ID
        self.setup_directories()  # Vytvoření složky pro publikaci
        self.parent = parent
        self.category = category
        self.subcategory = subcategory
        self.on_save_callback = on_save_callback  # Funkce pro uložení publikace

        # Vytvoření dialogového okna
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Přidat publikaci")
        self.dialog.geometry("500x750")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Uchování cest k obrázku a PDF
        self.image_path = None
        self.pdf_path = None

        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Název publikace
        ttk.Label(main_frame, text="Název publikace:").pack(anchor=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))

        # Autor publikace
        ttk.Label(main_frame, text="Autor:").pack(anchor=tk.W, pady=(0, 5))
        self.author_entry = ttk.Entry(main_frame, width=50)
        self.author_entry.pack(fill=tk.X, pady=(0, 10))

        # Rok vydání
        ttk.Label(main_frame, text="Rok vydání:").pack(anchor=tk.W, pady=(0, 5))
        self.year_entry = ttk.Entry(main_frame, width=20)
        self.year_entry.pack(fill=tk.X, pady=(0, 10))

        # Popis publikace (nepovinné pole)
        ttk.Label(main_frame, text="Popis publikace:").pack(anchor=tk.W, pady=(0, 5))
        description_frame = ttk.Frame(main_frame)
        description_frame.pack(fill=tk.BOTH, pady=(0, 10), expand=True)

        description_scrollbar = ttk.Scrollbar(description_frame, orient="vertical")
        description_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.description_text = tk.Text(description_frame, wrap="word", yscrollcommand=description_scrollbar.set, width=50, height=5)
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        description_scrollbar.config(command=self.description_text.yview)

        # Náhled obrázku obálky s pevnou velikostí
        self.image_preview = tk.Label(main_frame, text="Náhled obálky", bg="lightgray", width=25, height=10)
        self.image_preview.pack(pady=(10, 10))

        # Tlačítko pro nahrání obálky
        self.upload_image_button = ttk.Button(main_frame, text="Nahrát obálku", command=self.upload_image)
        self.upload_image_button.pack(fill=tk.X, pady=(10, 5))

        # Tlačítko pro nahrání PDF
        self.upload_pdf_button = ttk.Button(main_frame, text="Nahrát PDF", command=self.upload_pdf)
        self.upload_pdf_button.pack(fill=tk.X, pady=(5, 10))

        # Informace o nahraném souboru obálky
        self.image_info = ttk.Label(main_frame, text="Obálka: Nenahráno")
        self.image_info.pack(anchor=tk.W)

        # Informace o nahraném PDF
        self.pdf_info = ttk.Label(main_frame, text="PDF: Nenahráno")
        self.pdf_info.pack(anchor=tk.W)

        # Tlačítka pro potvrzení a zrušení
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text="Zrušit", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Přidat publikaci", command=self.save_publication).pack(side=tk.RIGHT)
        
    def setup_directories(self):
        self.base_dir = os.path.join("Soubory", self.publication_id)  # Hlavní složka pro publikaci
        os.makedirs(self.base_dir, exist_ok=True)  # Vytvoření složky, pokud neexistuje

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Vyberte obrázek", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            dest_path = os.path.join(self.base_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)  # Kopírování souboru do dynamické složky
            self.image_path = dest_path  # Aktualizace cesty na novou
            self.image_info.config(text=f"Obálka: {os.path.basename(dest_path)}")  # Zobrazení názvu

            # Náhled obrázku
            max_width, max_height = 200, 200
            image = Image.open(dest_path)
            scale = min(max_width / image.width, max_height / image.height)
            image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_preview.config(image=photo, width=max_width, height=max_height)
            self.image_preview.image = photo  # Uložení reference pro Tkinter

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(title="Vyberte PDF", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            dest_path = os.path.join(self.base_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)  # Kopírování souboru do dynamické složky
            self.pdf_path = dest_path  # Aktualizace cesty na novou
            self.pdf_info.config(text=f"PDF: {os.path.basename(dest_path)}")  # Zobrazení názvu

    def save_publication(self):
        """Uloží novou publikaci po validaci vstupních dat."""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        # Validace povinných polí
        if not title or not author or not year:
            tk.messagebox.showwarning("Chyba", "Vyplňte všechna povinná pole (název, autor, rok).")
            return

        # Validace roku (čtyřmístný formát)
        if not year.isdigit() or len(year) != 4:
            tk.messagebox.showwarning("Chyba", "Rok musí být čtyřmístné číslo.")
            return

        # Zajištění dynamických cest
        image_relative_path = os.path.relpath(self.image_path, start="Soubory")
        pdf_relative_path = os.path.relpath(self.pdf_path, start="Soubory")

        # Data o publikaci
        publication_data = {
            "id": self.publication_id,
            "title": title,
            "author": author,
            "year": year,
            "description": description,
            "image_path": os.path.join("Soubory", image_relative_path),
            "pdf_path": os.path.join("Soubory", pdf_relative_path),
            "category": self.category,
            "subcategory": self.subcategory
        }

        self.on_save_callback(publication_data)  # Předání dat pro uložení
        self.dialog.destroy()
        
class PublicationDetailWindow:
    def __init__(self, master, parent_app, publication_data, on_delete_callback=None, on_close_callback=None):
        """Inicializace okna Detail publikace."""
        self.master = master
        self.parent_app = parent_app  # Odkaz na hlavní aplikaci
        self.publication_data = publication_data
        self.on_delete_callback = on_delete_callback
        self.on_close_callback = on_close_callback

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.master.title("Detail publikace")
        self.master.geometry("500x650")  # Pevná velikost okna
        self.master.config(bg="#f0f0f0")  # Standardní šedé pozadí

        # Hlavní rám pro zarovnání obsahu
        main_frame = tk.Frame(master, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Levý horní roh - Náhled obálky
        image_path = publication_data.get("image_path")
        thumbnail_frame = tk.Frame(main_frame, bg="#f0f0f0")
        thumbnail_frame.grid(row=0, column=0, rowspan=3, padx=(5, 15), pady=10)

        max_width, max_height = 200, 200
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                scale = min(max_width / image.width, max_height / image.height)
                new_size = (int(image.width * scale), int(image.height * scale))
                image = image.resize(new_size, Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label = tk.Label(thumbnail_frame, image=photo, bg="#f0f0f0")
                self.image_label.image = photo
            except Exception as e:
                self.image_label = tk.Label(thumbnail_frame, text="Chyba obrázku", bg="l#f0f0f0", width=25, height=10)
        else:
            self.image_label = tk.Label(thumbnail_frame, text="Bez obálky", bg="#f0f0f0", width=25, height=10)
        self.image_label.pack()

        # Informace o publikaci (vedle obrázku)
        details_frame = tk.Frame(main_frame, bg="#f0f0f0")
        details_frame.grid(row=0, column=1, sticky="nw", padx=10)

        self.title_label = tk.Label(details_frame, text=f"Název: {publication_data.get('title', 'Bez názvu')}",
                                    font=("Arial", 14, "bold"), bg="#f0f0f0", wraplength=250, justify="left")
        self.title_label.pack(anchor="w", pady=2)

        self.author_label = tk.Label(details_frame, text=f"Autor: {publication_data.get('author', 'Neznámý autor')}",
                                     font=("Arial", 12), bg="#f0f0f0")
        self.author_label.pack(anchor="w", pady=2)

        self.year_label = tk.Label(details_frame, text=f"Rok: {publication_data.get('year', 'Neznámý rok')}",
                                   font=("Arial", 12), bg="#f0f0f0")
        self.year_label.pack(anchor="w", pady=2)

        # Tlačítko Otevřít PDF
        open_pdf_btn = tk.Button(main_frame, text="Otevřít PDF", command=self.open_pdf, bg="blue", fg="white", font=("Arial", 14, "bold"))
        open_pdf_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Popis publikace
        description_label = tk.Label(main_frame, text="Popis:", bg="#f0f0f0", anchor="w")
        description_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.description = tk.Text(main_frame, height=5, wrap="word", bg="white", width=60)
        self.description.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.description.insert("1.0", publication_data.get("description", ""))
        self.description.config(state=tk.DISABLED)
        self.description.bind("<Button-1>", lambda e: self.show_description_window(publication_data.get("description", "")))

        # Vyhledávání v PDF
        search_frame = tk.Frame(main_frame, bg="#f0f0f0")
        search_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        tk.Label(search_frame, text="Vyhledat v PDF:", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_btn = tk.Button(search_frame, text="Vyhledat", command=self.search_in_pdf)
        search_btn.pack(side=tk.LEFT, padx=5)

        # Tlačítka dole
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.grid(row=8, column=0, columnspan=2, sticky="sew", pady=(10, 0))
        main_frame.rowconfigure(8, weight=1)

        
        edit_btn = tk.Button(
            button_frame,
            text="Editovat",
            command=lambda: EditPublikaceDialog(
                parent=self.master,
                tab_name=self.publication_data.get("tab_name"),
                category=self.publication_data.get("category"),
                subcategory=self.publication_data.get("subcategory"),
                publication_data=self.publication_data,
                parent_app=self.parent_app,  # Odkaz na hlavní aplikaci
                on_save_callback=self.refresh_details
            )
        )

        edit_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(button_frame, text="Smazat", command=self.delete_publication, bg="red", fg="white")
        delete_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(button_frame, text="Zavřít", command=self.master.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
    def on_close(self):
        """Volá se při zavření okna."""
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception as e:
                print(f"Chyba při volání on_close_callback: {e}")
        self.master.destroy()


    def refresh_details(self, updated_data=None):
        """Obnoví detail publikace po provedení editace."""
        if updated_data:
            # Pokud jsou nová data předána přímo, aktualizujeme je
            self.publication_data = updated_data
        else:
            # Pokud nejsou data předána, načteme publikaci z data.json
            try:
                with open("data.json", "r", encoding="utf-8") as file:
                    data = json.load(file)

                # Hledáme publikaci podle ID
                publication_id = self.publication_data.get("id")
                for tab_name, categories in data.items():
                    for category_name, category_data in categories.items():
                        for pub in category_data.get("publikace", []):
                            if pub.get("id") == publication_id:
                                self.publication_data = pub
                                break

                if not self.publication_data:
                    raise ValueError("Publikace nebyla nalezena po aktualizaci.")

            except Exception as e:
                messagebox.showerror("Chyba", f"Chyba při obnově detailu publikace: {e}")
                return

        # Aktualizujeme zobrazení detailu
        self.title_label.config(text=f"Název: {self.publication_data['title']}")
        self.author_label.config(text=f"Autor: {self.publication_data['author']}")
        self.year_label.config(text=f"Rok: {self.publication_data['year']}")

        self.description.config(state=tk.NORMAL)
        self.description.delete("1.0", tk.END)
        self.description.insert(tk.END, self.publication_data["description"])
        self.description.config(state=tk.DISABLED)


    def open_pdf(self):
        """Otevře PDF soubor publikace."""
        publication_folder = os.path.join("Soubory", self.publication_data.get("id", ""))
        
        # Předpokládám, že název souboru PDF je součástí cesty v 'pdf_path'
        pdf_name = os.path.basename(self.publication_data.get("pdf_path", "file.pdf"))
        pdf_path = os.path.join(publication_folder, pdf_name)

        # Normalizace cesty pro kompatibilitu
        pdf_path = os.path.normpath(pdf_path)

        # Ověření existence souboru
        if os.path.exists(pdf_path):
            try:
                os.startfile(pdf_path)
            except Exception as e:
                messagebox.showerror("Chyba", f"Došlo k chybě při otevírání PDF: {e}")
        else:
            messagebox.showerror("Chyba", f"PDF soubor '{pdf_name}' nebyl nalezen: {pdf_path}")


    def show_description_window(self, description):
        desc_window = tk.Toplevel(self.master)
        desc_window.title("Popis knihy")
        desc_window.geometry("500x650")  # Stejná velikost jako detailní okno
        desc_window.config(bg="white")

        description_text = tk.Text(desc_window, wrap="word", bg="white")
        description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        description_text.insert("1.0", description)
        description_text.config(state=tk.DISABLED)

        close_btn = tk.Button(desc_window, text="Zavřít", command=desc_window.destroy)
        close_btn.pack(pady=10)

    def search_in_pdf(self):
        pdf_path = self.publication_data.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Chyba", "PDF soubor nebyl nalezen.")
            return

        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Chyba", "Zadejte text k vyhledání.")
            return

        try:
            reader = PdfReader(pdf_path)
            results = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if query.lower() in text.lower():
                    results.append(f"Stránka {page_num + 1}: {text.strip()[:100]}...")

            if results:
                self.show_search_results(results)
            else:
                messagebox.showinfo("Výsledek", "Hledaný text nebyl nalezen.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Vyhledávání v PDF selhalo: {e}")

    def show_search_results(self, results):
        results_window = tk.Toplevel(self.master)
        results_window.title("Výsledky vyhledávání")

        # Dynamické nastavení velikosti na základě počtu výsledků
        result_count = len(results)
        width = min(600, max(400, 20 * max(len(line) for line in results)))  # Přizpůsobení šířky
        height = min(600, max(300, 20 * result_count))  # Přizpůsobení výšky
        results_window.geometry(f"{width}x{height}")

        results_list = tk.Listbox(results_window)
        results_list.pack(fill=tk.BOTH, expand=True)
        for result in results:
            results_list.insert(tk.END, result)

        close_btn = tk.Button(results_window, text="Zavřít", command=results_window.destroy)
        close_btn.pack(pady=5)

    def delete_publication(self):
        """Smaže publikaci a zavolá callback pro aktualizaci pravého okna."""
        confirm = messagebox.askyesno("Potvrzení", "Opravdu chcete tuto publikaci smazat?")
        if not confirm:
            return

        try:
            # Smazání souborů obrázku a PDF
            publication_folder = os.path.join("Soubory", self.publication_data.get("id", ""))
            if os.path.exists(publication_folder):
                shutil.rmtree(publication_folder)  # Smaže celou složku publikace

            # Načtení dat ze souboru data.json
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            # Hledání a odstranění publikace na základě ID
            publication_id = self.publication_data.get("id")
            found = False
            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Kontrola hlavní kategorie
                    if "publikace" in category_data:
                        publications = category_data["publikace"]
                        for pub in publications:
                            if pub.get("id") == publication_id:
                                publications.remove(pub)
                                found = True
                                break

                    # Kontrola podkategorií
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict) and "publikace" in subcategory_data:
                            publications = subcategory_data["publikace"]
                            for pub in publications:
                                if pub.get("id") == publication_id:
                                    publications.remove(pub)
                                    found = True
                                    break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break

            if not found:
                messagebox.showerror("Chyba", f"Publikace s ID '{publication_id}' nebyla nalezena.")
                return

            # Uložení změn zpět do souboru
            with open("data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            # Otevření hlavního okna a obnovení záložky
            if self.master and hasattr(self.master, "refresh_current_tab"):
                self.master.refresh_current_tab()

            messagebox.showinfo("Úspěch", "Publikace byla úspěšně smazána.")
            self.master.destroy()

            # Zavolání callbacku pro aktualizaci pravého okna
            if self.on_delete_callback:
                self.on_delete_callback()

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při mazání publikace: {e}")




            
    def edit_publication(self):
        """Otevře dialogové okno pro editaci publikace."""
        # Získáme název aktuálně vybrané záložky
        current_tab = self.tab_name  # Proměnná self.tab_name by měla držet název aktivní záložky (např. 'Knihy', 'Časopisy')

        # Debugging: Zkontrolujeme, co se předává
        print(f"Spouštím editaci pro záložku: {current_tab}, kategorie={self.publication_data.get('category')}, podkategorie={self.publication_data.get('subcategory')}")

        # Otevřeme dialog pro editaci publikace
        EditPublikaceDialog(
            parent=self.master,
            tab_name=current_tab,  # Předáváme název aktuální záložky
            category=self.publication_data.get("category"),
            subcategory=self.publication_data.get("subcategory"),
            publication_data=self.publication_data,
            on_save_callback=self.refresh_details  # Funkce pro obnovu detailního okna po editaci
        )
        
class EditPublikaceDialog:
    def __init__(self, parent, tab_name, category=None, subcategory=None, publication_data=None, parent_app=None, on_save_callback=None):
        """Inicializuje okno pro editaci publikace."""
        self.parent = parent
        self.tab_name = tab_name  # Správně uložíme název záložky
        self.category = category
        self.subcategory = subcategory
        self.publication_data = publication_data
        self.parent_app = parent_app  # Nastavíme odkaz na hlavní aplikaci
        self.on_save_callback = on_save_callback
        self.publication_id = publication_data.get("id")

        print(f"Editace spuštěna: záložka={self.tab_name}, kategorie={self.category}, podkategorie={self.subcategory}, ID={self.publication_id}")

        # Inicializace dialogového okna
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editace publikace")

        # Dynamická velikost okna
        self.dialog.geometry("600x900")  # Nastavení výchozí velikosti
        self.dialog.minsize(600, 500)    # Zajištění minimální velikosti okna
        self.dialog.resizable(True, True)  # Povolení změny velikosti okna
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Cesty k souborům publikace
        self.image_path = publication_data.get("image_path")
        self.pdf_path = publication_data.get("pdf_path")

        # Inicializace GUI
        self.setup_gui()


    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

         # Název publikace
        ttk.Label(main_frame, text="Název publikace:").pack(anchor=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        self.title_entry.insert(0, self.publication_data.get("title", ""))
    
        # Autor publikace
        ttk.Label(main_frame, text="Autor:").pack(anchor=tk.W, pady=(0, 5))
        self.author_entry = ttk.Entry(main_frame, width=50)
        self.author_entry.pack(fill=tk.X, pady=(0, 10))
        self.author_entry.insert(0, self.publication_data.get("author", ""))

        # Rok vydání
        ttk.Label(main_frame, text="Rok vydání:").pack(anchor=tk.W, pady=(0, 5))
        self.year_entry = ttk.Entry(main_frame, width=20)
        self.year_entry.pack(fill=tk.X, pady=(0, 10))
        self.year_entry.insert(0, self.publication_data.get("year", ""))

        # Popis publikace
        ttk.Label(main_frame, text="Popis publikace:").pack(anchor=tk.W, pady=(0, 5))
        description_frame = ttk.Frame(main_frame)
        description_frame.pack(fill=tk.BOTH, pady=(0, 10), expand=True)

        description_scrollbar = ttk.Scrollbar(description_frame, orient="vertical")
        description_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.description_text = tk.Text(description_frame, wrap="word", yscrollcommand=description_scrollbar.set, width=50, height=5)
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        description_scrollbar.config(command=self.description_text.yview)
        self.description_text.insert("1.0", self.publication_data.get("description", ""))

        # Přidání akce pro otevření externího okna
        self.description_text.bind("<Button-1>", self.open_description_window)

        # Náhled obrázku
        self.image_preview = tk.Label(main_frame, text="Náhled obálky", bg="lightgray", width=25, height=10)
        self.image_preview.pack(pady=(10, 10))
        if self.image_path and os.path.exists(self.image_path):
            self.update_image_preview(self.image_path)

        # Tlačítko pro nahrání obálky
        ttk.Button(main_frame, text="Nahrát obálku", command=self.upload_image).pack(fill=tk.X, pady=(10, 5))

        # Tlačítko pro nahrání PDF
        ttk.Button(main_frame, text="Nahrát PDF", command=self.upload_pdf).pack(fill=tk.X, pady=(5, 10))

        # Informace o nahraných souborech
        self.image_info = ttk.Label(main_frame, text=f"Obálka: {os.path.basename(self.image_path) if self.image_path else 'Nenahráno'}")
        self.image_info.pack(anchor=tk.W)

        self.pdf_info = ttk.Label(main_frame, text=f"PDF: {os.path.basename(self.pdf_path) if self.pdf_path else 'Nenahráno'}")
        self.pdf_info.pack(anchor=tk.W)

        # Tlačítka pro potvrzení a zrušení
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Rámeček pro změnu umístění
        location_frame = ttk.LabelFrame(main_frame, text="Změnit umístění", padding=10)
        location_frame.pack(fill=tk.BOTH, pady=(20, 10))

        # Combobox pro záložky
        ttk.Label(location_frame, text="Záložka:").grid(row=0, column=0, sticky="w", pady=5)
        self.tab_combobox = ttk.Combobox(location_frame, state="readonly", width=30)
        self.tab_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.tab_combobox['values'] = self.parent_app.get_tabs()  # Získání záložek
        self.tab_combobox.bind("<<ComboboxSelected>>", self.update_categories)

        # Combobox pro kategorie
        ttk.Label(location_frame, text="Kategorie:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_combobox = ttk.Combobox(location_frame, state="readonly", width=30)
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_subcategories)

        # Combobox pro podkategorie
        ttk.Label(location_frame, text="Podkategorie:").grid(row=2, column=0, sticky="w", pady=5)
        self.subcategory_combobox = ttk.Combobox(location_frame, state="readonly", width=30)
        self.subcategory_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Tlačítko pro přesun
        move_button = ttk.Button(location_frame, text="Přesunout", command=self.move_publication)
        move_button.grid(row=3, column=0, columnspan=2, pady=10)


        ttk.Button(btn_frame, text="Zrušit", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Uložit editaci", command=self.save_edits).pack(side=tk.RIGHT, padx=(5, 0))

        
    def open_description_window(self, event=None):
        external_window = tk.Toplevel(self.dialog)
        external_window.title("Upravit popis publikace")
        external_window.geometry("500x650")
        external_window.resizable(False, False)

        external_frame = ttk.Frame(external_window, padding="10")
        external_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(external_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        description_editor = tk.Text(external_frame, wrap="word", yscrollcommand=scrollbar.set, width=50, height=20)
        description_editor.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=description_editor.yview)

        # Předvyplnění aktuálního popisu
        description_editor.insert("1.0", self.description_text.get("1.0", tk.END).strip())

        # Tlačítka pro uložení a zavření
        btn_frame = ttk.Frame(external_window)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Uložit", command=lambda: self.save_description(description_editor, external_window)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Zavřít", command=external_window.destroy).pack(side=tk.RIGHT)

    def save_description(self, description_editor, window):
        new_description = description_editor.get("1.0", tk.END).strip()
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", new_description)
        window.destroy()

    def upload_image(self):
        file_path = filedialog.askopenfilename(title="Vyberte obrázek", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            dest_path = os.path.join(self.base_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)  # Kopírování souboru do složky
            self.image_path = dest_path  # Aktualizace cesty
            self.image_info.config(text=f"Obálka: {os.path.basename(dest_path)}")  # Zobrazení názvu


    def upload_pdf(self):
        file_path = filedialog.askopenfilename(title="Vyberte PDF", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            dest_path = os.path.join(self.base_dir, os.path.basename(file_path))
            shutil.copy(file_path, dest_path)  # Kopírování souboru do složky
            self.pdf_path = dest_path  # Aktualizace cesty
            self.pdf_info.config(text=f"PDF: {os.path.basename(dest_path)}")  # Zobrazení názvu


    def update_image_preview(self, file_path):
        max_width, max_height = 200, 200
        image = Image.open(file_path)
        scale = min(max_width / image.width, max_height / image.height)
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_preview.config(image=photo, width=max_width, height=max_height)
        self.image_preview.image = photo

    def save_edits(self):
        """Uloží provedené úpravy publikace."""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        if not title or not author or not year:
            messagebox.showwarning("Chyba", "Vyplňte všechna povinná pole (název, autor, rok).")
            return

        # Dynamické cesty na základě ID
        publication_folder = os.path.join("Soubory", self.publication_id)
        if self.image_path:
            self.image_path = os.path.join(publication_folder, os.path.basename(self.image_path))
        if self.pdf_path:
            self.pdf_path = os.path.join(publication_folder, os.path.basename(self.pdf_path))

        updated_data = {
            "id": self.publication_id,
            "title": title,
            "author": author,
            "year": year,
            "description": description,
            "image_path": self.image_path,
            "pdf_path": self.pdf_path,
            "category": self.category,
            "subcategory": self.subcategory,
        }

        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            # Hledání a aktualizace publikace
            def update_publication(node):
                """Pomocná funkce pro aktualizaci publikace ve struktuře."""
                publications = node.get("publikace", [])
                for pub in publications:
                    if pub.get("id") == updated_data["id"]:
                        pub.update(updated_data)
                        return True
                return False

            found = False
            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Kontrola hlavní kategorie
                    if update_publication(category_data):
                        found = True
                        break

                    # Kontrola podkategorií
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict) and update_publication(subcategory_data):
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

            if not found:
                messagebox.showerror("Chyba", f"Publikace s ID '{self.publication_id}' nebyla nalezena.")
                return

            # Uložení změn zpět do souboru
            with open("data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Úspěch", "Změny byly uloženy.")
            self.dialog.destroy()

            if self.on_save_callback:
                self.on_save_callback(updated_data)

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při ukládání změn: {e}")
            
    def update_categories(self, event=None):
        """Aktualizuje seznam kategorií na základě vybrané záložky."""
        selected_tab = self.tab_combobox.get()
        categories = self.parent_app.get_categories(selected_tab)
        self.category_combobox['values'] = categories
        self.category_combobox.set("")
        self.subcategory_combobox['values'] = []
        self.subcategory_combobox.set("")

    def update_subcategories(self, event=None):
        """Aktualizuje seznam podkategorií na základě vybrané kategorie."""
        selected_tab = self.tab_combobox.get()
        selected_category = self.category_combobox.get()
        subcategories = self.parent_app.get_subcategories(selected_tab, selected_category)
        self.subcategory_combobox['values'] = subcategories
        self.subcategory_combobox.set("")


    def move_publication(self):
        """Přesune publikaci na nové místo."""
        selected_tab = self.tab_combobox.get()
        selected_category = self.category_combobox.get()
        selected_subcategory = self.subcategory_combobox.get()

        if not selected_tab or not selected_category:
            messagebox.showwarning("Chyba", "Vyberte záložku a kategorii.")
            return

        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            publication_id = self.publication_id

            # Odstranění ze starého místa
            self.parent_app.remove_publication_from_old_location(data, publication_id)

            # Přidání na nové místo
            self.parent_app.add_publication_to_new_location(
                data, self.publication_data, selected_tab, selected_category, selected_subcategory
            )

            # Uložení změn
            with open("data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Úspěch", "Publikace byla úspěšně přesunuta.")
            self.dialog.destroy()  # Zavřít dialog

            # Obnoví aktuální záložku po přesunu publikace
            self.parent_app.refresh_current_tab()

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při přesunu publikace: {e}")


class SearchTab:
    def __init__(self, master, main_app):
        style = ttk.Style()
        style.configure("SearchTab.TButton", font=("Arial", 16), foreground="black")  # Přidáme prefix SearchTab
        style.configure("SearchTab.TEntry", font=("Arial", 16))
        style.configure("SearchTab.TLabelframe", font=("Arial", 16, "bold"))
        style.configure("SearchTab.TLabelframe.Label", font=("Arial", 16, "bold"))
        style.configure("SearchTab.Treeview", rowheight=30, font=("Arial", 14))
        style.configure("SearchTab.Treeview.Heading", font=("Arial", 14, "bold"))
                
        """Inicializace záložky Vyhledávání."""
        self.master = master
        self.main_app = main_app  # Uložení odkazu na hlavní aplikaci
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Nastavení mřížky pro zarovnání na střed
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # Vnější rám pro vycentrování
        self.inner_frame = ttk.Frame(self.frame)
        self.inner_frame.grid(row=0, column=0)

        # První pole: Vyhledat v názvu publikací
        self.create_title_search_frame()

        # Druhé pole: Vyhledat v popisu publikace
        self.create_description_search_frame()

        # Třetí pole: Vyhledat v PDF souboru
        self.create_pdf_search_frame()

    def create_title_search_frame(self):
        """Vytvoří rámeček pro vyhledávání v názvu publikací."""
        title_frame = ttk.LabelFrame(self.inner_frame, text="Vyhledat v názvu publikací", style="SearchTab.TLabelframe", labelanchor="n")
        title_frame.grid(row=0, column=0, pady=30, sticky="ew")

        # Pole pro zadání vyhledávání
        entry = ttk.Entry(title_frame, font=("Arial", 16))
        entry.grid(row=0, column=0, padx=10, pady=10)

        # Tlačítko pro spuštění vyhledávání
        search_btn = ttk.Button(title_frame, text="Vyhledat", command=lambda: self.search_titles(entry.get()), style="SearchTab.TButton")
        search_btn.grid(row=0, column=1, padx=10, pady=10)
        style = ttk.Style()
        style.configure("SearchTab.TButton", font=("Arial", 16))


    def create_description_search_frame(self):
        """Vytvoří rámeček pro vyhledávání v popisu publikací."""
        description_frame = ttk.LabelFrame(self.inner_frame, text="Vyhledat v popisu publikací", style="SearchTab.TLabelframe", labelanchor="n")
        description_frame.grid(row=1, column=0, pady=30, sticky="ew")

        # Pole pro zadání vyhledávání
        entry = ttk.Entry(description_frame, font=("Arial", 16))
        entry.grid(row=0, column=0, padx=10, pady=10)

        # Tlačítko pro spuštění vyhledávání
        search_btn = ttk.Button(description_frame, text="Vyhledat", command=lambda: self.search_descriptions(entry.get()), style="SearchTab.TButton")
        search_btn.grid(row=0, column=1, padx=10, pady=10)
        style = ttk.Style()
        style.configure("SearchTab.TButton", font=("Arial", 16))

    def create_pdf_search_frame(self):
        """Vytvoří rámeček pro vyhledávání v PDF souboru."""
        pdf_frame = ttk.LabelFrame(self.inner_frame, text="Vyhledat v PDF souboru", style="SearchTab.TLabelframe", labelanchor="n")
        pdf_frame.grid(row=2, column=0, pady=30, sticky="ew")

        # Combobox pro dynamické vyhledávání názvu publikace
        combobox = ttk.Combobox(pdf_frame, font=("Arial", 16))
        combobox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Pole pro zadání textu k vyhledání v PDF
        entry = ttk.Entry(pdf_frame, font=("Arial", 20))
        entry.grid(row=1, column=0, padx=10, pady=10)

        # Tlačítko pro spuštění vyhledávání
        search_btn = ttk.Button(pdf_frame, text="Vyhledat", command=lambda: self.search_in_pdf(combobox, entry.get()), style="SearchTab.TButton")
        search_btn.grid(row=1, column=1, padx=10, pady=10)
        style = ttk.Style()
        style.configure("SearchTab.TButton", font=("Arial", 16))

        # Načtení názvů publikací do Comboboxu
        self.populate_combobox(combobox)

    def populate_combobox(self, combobox):
        """Načte názvy publikací do Comboboxu z kategorií i podkategorií."""
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            titles = []
            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Hlavní kategorie
                    for pub in category_data.get("publikace", []):
                        titles.append(pub.get("title", "Bez názvu"))

                    # Podkategorie
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                titles.append(pub.get("title", "Bez názvu"))

            combobox["values"] = sorted(titles)  # Nastavení hodnot do Comboboxu
            combobox.bind("<KeyRelease>", lambda e: self.filter_combobox(combobox, titles))

        except FileNotFoundError:
            messagebox.showerror("Chyba", "Soubor data.json nebyl nalezen.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při načítání dat: {e}")



    def filter_combobox(self, combobox, titles):
        """Filtruje názvy publikací podle více slov."""
        query = combobox.get().lower()
        query_words = query.split()  # Rozdělení na jednotlivá slova
        filtered = [
            title for title in titles
            if all(word in title.lower() for word in query_words)  # Každé slovo musí být v názvu
        ]
        combobox["values"] = filtered
        combobox.event_generate("<Down>")  # Otevření seznamu při filtrování

    def search_titles(self, query):
        """Vyhledá v názvu publikací a doplní dynamické cesty."""
        if not query.strip():
            messagebox.showwarning("Chyba", "Zadejte hledaný text.")
            return

        results = []
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Prohledávání hlavních kategorií
                    for pub in category_data.get("publikace", []):
                        if query.lower() in pub.get("title", "").lower():
                            self.add_dynamic_paths(pub)
                            results.append(pub)

                    # Prohledávání podkategorií
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                if query.lower() in pub.get("title", "").lower():
                                    self.add_dynamic_paths(pub)
                                    results.append(pub)

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při čtení dat: {e}")
            return

        self.show_search_results(results, "Vyhledávání v názvech")



    def search_descriptions(self, query):
        if not query.strip():
            messagebox.showwarning("Chyba", "Zadejte hledaný text.")
            return

        results = []
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Prohledávání hlavních kategorií
                    for pub in category_data.get("publikace", []):
                        if query.lower() in pub.get("description", "").lower():
                            results.append({
                                "tab": tab_name,
                                "category": category_name,
                                "subcategory": None,
                                "title": pub.get("title"),
                                "text": pub.get("description"),
                                "id": pub.get("id", "")
                            })

                    # Prohledávání podkategorií
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                if query.lower() in pub.get("description", "").lower():
                                    results.append({
                                        "tab": tab_name,
                                        "category": category_name,
                                        "subcategory": subcategory_name,
                                        "title": pub.get("title"),
                                        "text": pub.get("description"),
                                        "id": pub.get("id", "")
                                    })
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při čtení dat: {e}")
            return

        self.show_search_results(results, "Vyhledávání v popisech", highlight_key="text", highlight_query=query)

    def add_dynamic_paths(self, publication):
        """Doplní dynamické cesty pro obrázky a PDF na základě ID publikace."""
        if "id" in publication:
            publication_folder = os.path.join("Soubory", publication["id"])
            publication["image_path"] = os.path.join(publication_folder, os.path.basename(publication.get("image_path", "")))
            publication["pdf_path"] = os.path.join(publication_folder, os.path.basename(publication.get("pdf_path", "")))


    def search_in_pdf(self, combobox, query):
        """Vyhledávání textu v PDF."""
        if not query.strip():
            messagebox.showwarning("Chyba", "Zadejte text k vyhledání.")
            return

        selected_title = combobox.get()
        if not selected_title.strip():
            messagebox.showwarning("Chyba", "Vyberte publikaci z nabídky.")
            return

        results = []
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Prohledávání hlavních kategorií
                    for pub in category_data.get("publikace", []):
                        if pub.get("title") == selected_title:
                            pdf_path = self.get_pdf_path(pub)
                            results.extend(self.search_pdf_file(pdf_path, query, tab_name, category_name, None, pub))

                    # Prohledávání podkategorií
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                if pub.get("title") == selected_title:
                                    pdf_path = self.get_pdf_path(pub)
                                    results.extend(self.search_pdf_file(pdf_path, query, tab_name, category_name, subcategory_name, pub))

        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při čtení PDF: {e}")
            return

        self.show_search_results(results, f"Výsledky hledání v PDF: {selected_title}", highlight_key="text", highlight_query=query)

    def get_pdf_path(self, pub):
        """Sestaví dynamickou cestu k PDF souboru."""
        return os.path.join("Soubory", pub["id"], os.path.basename(pub.get("pdf_path", "")))

    def search_pdf_file(self, pdf_path, query, tab_name, category_name, subcategory_name=None, pub=None):
        """Vyhledá text v PDF souboru."""
        if not os.path.exists(pdf_path):
            messagebox.showerror("Chyba", f"PDF soubor '{pdf_path}' neexistuje.")
            return []

        results = []
        with open(pdf_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if query.lower() in text.lower():
                    results.append({
                        "tab": tab_name,
                        "category": category_name,
                        "subcategory": subcategory_name,
                        "title": pub.get("title", "Bez názvu"),  # Zobrazení názvu publikace
                        "text": f"Strana {page_num}: {text}",
                        "page": page_num,
                        "id": pub.get("id", "Neznámé ID")
                    })
        return results

    
    def show_search_results(self, results, title, highlight_key=None, highlight_query=None):
        result_window = tk.Toplevel(self.master)
        result_window.title(title)
        result_window.geometry("1200x600")
        result_window.minsize(1200, 600)
        result_window.maxsize(2000, 600)

        # Hlavní rámec pro obsah
        main_frame = tk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas a scrollbar pro tabulku
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.config(xscrollcommand=scrollbar.set)

        result_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=result_frame, anchor="nw")

        columns = ("index", "tab", "category", "subcategory", "title", "page", "text", "id")
        tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse")

        tree.heading("index", text="Počet výsledků", anchor="center")
        tree.heading("tab", text="Záložka", anchor="center")
        tree.heading("category", text="Kategorie", anchor="w")
        tree.heading("subcategory", text="Podkategorie", anchor="w")
        tree.heading("title", text="Název publikace", anchor="w")
        tree.heading("page", text="Strana", anchor="center")
        tree.heading("text", text="Vyhledaný text", anchor="w")
        tree.heading("id", text="ID", anchor="center")  # Skrytý sloupec pro ID

        tree.column("index", width=120, anchor="center")
        tree.column("tab", width=120, anchor="center")
        tree.column("category", width=200, anchor="w")
        tree.column("subcategory", width=200, anchor="w")
        tree.column("title", width=250, anchor="w")
        tree.column("page", width=100, anchor="center")
        tree.column("text", width=800, stretch=True, anchor="w")
        tree.column("id", width=0, stretch=False)  # Skrytý sloupec

        tree.pack(fill=tk.BOTH, expand=True)

        for idx, result in enumerate(results, start=1):
            text = result.get(highlight_key, "") if highlight_key else result.get("text", "")
            if highlight_query:
                text = text.replace(highlight_query, f"[{highlight_query}]")
            tree.insert("", "end", values=(
                idx,
                result.get("tab", ""),
                result.get("category", ""),
                result.get("subcategory", ""),
                result.get("title", ""),
                result.get("page", ""),
                text.replace("\n", " ").strip(),
                result.get("id", "")  # ID publikace
            ))

        def on_row_double_click(event):
            selected_item = tree.selection()
            if selected_item:
                item_data = tree.item(selected_item[0])["values"]
                pub_id = item_data[-1]  # ID je v posledním sloupci
                if pub_id:
                    print("Otevírám detail publikace s ID:", pub_id)
                    self.main_app.open_publication_detail({"id": pub_id})

        tree.bind("<Double-1>", on_row_double_click)

        # Aktualizace oblasti posuvníku
        result_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Informační zpráva
        info_frame = tk.Frame(result_window, bg="lightgray")
        info_frame.pack(fill=tk.X, side="bottom", pady=5)

        info_label = tk.Label(info_frame, text="Pro zobrazení detailu publikace, stačí dvakrát kliknout na výsledek vyhledávání.", 
                            bg="lightgray", font=("Arial", 10))
        info_label.pack(anchor="w", padx=10)


    def open_publication_detail(self, pub_id):
        """Otevře detail publikace na základě jejího ID."""
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            
            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    for pub in category_data.get("publikace", []):
                        if pub.get("id") == pub_id:
                            self.master.open_publication_detail(pub)
                            return
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při otevírání detailu publikace: {e}")


class UniversalPrinter:
    def __init__(self):
        self.app = QApplication([])  # Vytvoření PyQt aplikace

    def print_text(self, text, title="Tisk textu"):
        """Otevře dialog pro tisk textu."""
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        dialog.setWindowTitle(title)

        if dialog.exec_() == QPrintDialog.Accepted:
            document = QTextDocument()
            document.setPlainText(text)
            document.print_(printer)
            QMessageBox.information(None, "Tisk", "Tisk byl úspěšně odeslán na tiskárnu.")
        else:
            QMessageBox.warning(None, "Tisk", "Tisk byl zrušen.")

    def print_preview(self, text, title="Náhled tisku"):
        """Otevře náhled tisku textu."""
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer)
        preview.setWindowTitle(title)
        
        def render_preview(printer):
            document = QTextDocument()
            document.setPlainText(text)
            document.print_(printer)

        preview.paintRequested.connect(render_preview)
        preview.exec_()

    def print_table(self, headers, rows, title="Tisk tabulky"):
        """Vytiskne tabulku s danými záhlavími a řádky."""
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        dialog.setWindowTitle(title)

        if dialog.exec_() == QPrintDialog.Accepted:
            document = QTextDocument()
            html = "<table border='1' style='width: 100%; border-collapse: collapse;'>"
            html += "<tr>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr>"
            for row in rows:
                html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            html += "</table>"
            document.setHtml(html)
            document.print_(printer)
            QMessageBox.information(None, "Tisk", "Tisk tabulky byl úspěšně odeslán na tiskárnu.")
        else:
            QMessageBox.warning(None, "Tisk", "Tisk byl zrušen.")

    def print_from_webview(self, webview: QWebEngineView):
        """Tisk obsahu z QWebEngineView."""
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        dialog.setWindowTitle("Tisk obsahu webové stránky")

        if dialog.exec_() == QPrintDialog.Accepted:
            webview.page().print(printer, lambda success: QMessageBox.information(None, "Tisk", "Tisk proběhl úspěšně." if success else "Tisk selhal."))



            
class KnihovnaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Správce elektronické knihovny")
        self.root.geometry("1200x750")

        # Definice seznamu záložek
        self.tab_names = ["Knihy", "Časopisy", "Datasheets", "Ostatní", "Vyhledávání"]

        # Inicializace datových souborů
        self.initialize_data_file()
        self.initialize_categories_file()

        # Vytvoření menu
        self.create_menu()

        # Styl notebooku
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), padding=[20, 10])

        # Vytvoření notebooku (záložek)
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Správa záložek
        self.publication_managers = {}
        for name in self.tab_names:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=name)

            if name != "Vyhledávání":
                self.setup_tab_layout(tab_frame, name)
            else:
                search_tab = SearchTab(tab_frame, self)  # 'self' odkazuje na KnihovnaApp
                
        self.notebook.bind("<<NotebookTabChanged>>", self.refresh_current_tab)

        self.initialize_data_file()
        self.initialize_categories_file()
        self.refresh_all_tabs()
        
    def get_tabs(self):
        """Vrátí seznam záložek."""
        return ["Knihy", "Časopisy", "Datasheets", "Ostatní"]
    
    def get_categories(self, tab_name):
        categories = self.load_json_file("categories.json").get(tab_name, {})
        return list(categories.keys())

    def get_subcategories(self, tab_name, category_name):
        categories = self.load_json_file("categories.json").get(tab_name, {})
        return list(categories.get(category_name, {}).keys())


    def initialize_data_file(self):
        """Inicializuje soubor data.json, pokud neexistuje."""
        data = self.load_json_file("data.json")
        if data is None:
            data = {tab: {} for tab in self.tab_names if tab != "Vyhledávání"}
        self.save_json_file("data.json", data)


    def initialize_categories_file(self):
        """Inicializuje soubor categories.json, pokud neexistuje."""
        categories = self.load_json_file("categories.json")
        if categories is None:
            categories = {tab: {} for tab in self.tab_names if tab != "Vyhledávání"}
        self.save_json_file("categories.json", categories)

    def refresh_all_tabs(self):
        """Obnoví kategorie a stromové zobrazení ve všech záložkách."""
        for tab_name, manager in self.publication_managers.items():
            manager.category_data = manager.load_categories()
            manager.load_tree()  # Načtení stromového zobrazení
            print(f"Záložka '{tab_name}' byla úspěšně načtena.")

            
    def refresh_current_tab(self, event=None):
        """Obnoví obsah aktuální záložky při přepnutí."""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab in self.publication_managers:
            manager = self.publication_managers[current_tab]
            # Načtení kategorií a publikací pro danou záložku
            manager.category_data = manager.load_categories()
            self.refresh_publications(category=None, subcategory=None)
            
    def load_json_file(self, file_path):
        """Načte obsah JSON souboru."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Soubor '{file_path}' nebyl nalezen. Vytváří se nový soubor.")
            return {}  # Vrátí prázdný slovník, pokud soubor neexistuje
        except json.JSONDecodeError:
            print(f"Chybný formát JSON v souboru '{file_path}'.")
            messagebox.showerror("Chyba", f"Soubor '{file_path}' má neplatný formát.")
            return None  # Vrátí None při chybě dekódování
        except Exception as e:
            print(f"Neočekávaná chyba při čtení souboru '{file_path}': {e}")
            messagebox.showerror("Chyba", f"Neočekávaná chyba při čtení souboru: {e}")
            return None

    def save_json_file(self, file_path, data):
        """Uloží obsah do JSON souboru."""
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Soubor '{file_path}' byl úspěšně uložen.")
        except PermissionError:
            print(f"Nemáte oprávnění k zápisu do souboru '{file_path}'.")
            messagebox.showerror("Chyba", f"Nemáte oprávnění k zápisu do souboru '{file_path}'.")
        except Exception as e:
            print(f"Neočekávaná chyba při ukládání do souboru '{file_path}': {e}")
            messagebox.showerror("Chyba", f"Neočekávaná chyba při ukládání souboru: {e}")
            
    def remove_publication_from_old_location(self, data, publication_id):
        """Najde a odstraní publikaci podle jejího ID ze souboru data.json."""
        for tab_name, categories in data.items():
            for category_name, category_data in categories.items():
                # Hlavní kategorie
                if "publikace" in category_data:
                    publications = category_data["publikace"]
                    for pub in publications:
                        if pub.get("id") == publication_id:
                            publications.remove(pub)
                            return True

                # Podkategorie
                for subcategory_name, subcategory_data in category_data.items():
                    if isinstance(subcategory_data, dict) and "publikace" in subcategory_data:
                        publications = subcategory_data["publikace"]
                        for pub in publications:
                            if pub.get("id") == publication_id:
                                publications.remove(pub)
                                return True
        return False

    def add_publication_to_new_location(self, data, publication, tab, category, subcategory=None):
        """Přidá publikaci do nové záložky, kategorie a podkategorie v data.json."""
        # Vytvoření cesty v datové struktuře
        if subcategory:
            data.setdefault(tab, {}).setdefault(category, {}).setdefault(subcategory, {}).setdefault("publikace", []).append(publication)
        else:
            data.setdefault(tab, {}).setdefault(category, {}).setdefault("publikace", []).append(publication)
            
    def create_menu(self):
        """Vytvoří hlavní menu aplikace."""
        menu_bar = tk.Menu(self.root)

        # Tiskové menu
        print_menu = tk.Menu(menu_bar, tearoff=0)

        # Dynamické podmenu pro tisk záložek
        tabs_menu = tk.Menu(print_menu, tearoff=0)
        for tab in self.get_tabs():
            tabs_menu.add_command(label=tab, command=lambda t=tab: self.print_tab(t))
        print_menu.add_cascade(label="Záložky", menu=tabs_menu)

        # Dynamické podmenu pro tisk kategorií
        categories_menu = tk.Menu(print_menu, tearoff=0)

        def populate_categories_menu():
            categories_menu.delete(0, tk.END)  # Vyčistíme staré položky
            for tab in self.get_tabs():
                submenu = tk.Menu(categories_menu, tearoff=0)
                for category in self.get_categories(tab):
                    submenu.add_command(
                        label=category,
                        command=lambda t=tab, c=category: self.print_category(t, c)
                    )
                categories_menu.add_cascade(label=tab, menu=submenu)

        populate_categories_menu()
        print_menu.add_cascade(label="Kategorie", menu=categories_menu)

        # Dynamické podmenu pro tisk podkategorií
        subcategories_menu = tk.Menu(print_menu, tearoff=0)

        def populate_subcategories_menu():
            subcategories_menu.delete(0, tk.END)  # Vyčistíme staré položky
            for tab in self.get_tabs():
                tab_menu = tk.Menu(subcategories_menu, tearoff=0)
                for category in self.get_categories(tab):
                    cat_menu = tk.Menu(tab_menu, tearoff=0)
                    for subcategory in self.get_subcategories(tab, category):
                        cat_menu.add_command(
                            label=subcategory,
                            command=lambda t=tab, c=category, s=subcategory: self.print_subcategory(t, c, s)
                        )
                    tab_menu.add_cascade(label=category, menu=cat_menu)
                subcategories_menu.add_cascade(label=tab, menu=tab_menu)

        populate_subcategories_menu()
        print_menu.add_cascade(label="Podkategorie", menu=subcategories_menu)

        # Přidání tiskového menu do hlavní nabídky
        menu_bar.add_cascade(label="Tisk", menu=print_menu)

        # Export/Import menu
        export_import_menu = tk.Menu(menu_bar, tearoff=0)

        # Export souboru
        export_import_menu.add_command(label="Export souboru", command=self.export_file)

        # Import souboru
        export_import_menu.add_command(label="Import souboru", command=self.import_file)

        # Přidání Export/Import menu do hlavní nabídky
        menu_bar.add_cascade(label="Export/Import", menu=export_import_menu)

        # Zobrazení menu
        self.root.config(menu=menu_bar)

    # Doplnění metod export_file a import_file

    def export_file(self):
        """Metoda pro export souboru."""
        try:
            # Nastavení výchozího souboru JSON a SQLite databáze
            json_file = "data.json"  # Předpokládá se, že data.json je ve stejném adresáři jako aplikace
            database_file = "exported_data.sqlite"

            # Volání metody pro export dat
            self.export_to_sqlite(json_file, database_file)

            # Informování uživatele o úspěšném exportu
            messagebox.showinfo("Export", f"Export dat do SQLite databáze byl úspěšný!\nDatabáze: {database_file}")
        except Exception as e:
            # Zobrazení chybové zprávy, pokud nastane problém
            messagebox.showerror("Chyba při exportu", f"Nepodařilo se exportovat data: {e}")

    def import_file(self):
        """Metoda pro import souboru."""
        messagebox.showinfo("Import", "Funkce pro import souboru zatím není implementována.")


        
    def print_tab(self, tab_name):
        """Tiskne všechny publikace z dané záložky."""
        publications = self.get_publications_by_tab(tab_name)
        if not publications:
            messagebox.showinfo("Tisk", f"Žádné publikace v záložce '{tab_name}'")
            return
        self.preview_print(publications, f"Tisk z záložky '{tab_name}'")

    def print_category(self, tab_name, category_name):
        """Tiskne všechny publikace z dané kategorie."""
        publications = self.get_publications_by_category(tab_name, category_name)
        if not publications:
            messagebox.showinfo("Tisk", f"Žádné publikace v kategorii '{category_name}' (záložka '{tab_name}')")
            return
        self.preview_print(publications, f"Tisk z kategorie '{category_name}' (záložka '{tab_name}')")

    def print_subcategory(self, tab_name, category_name, subcategory_name):
        """Tiskne všechny publikace z dané podkategorie."""
        publications = self.get_publications_by_subcategory(tab_name, category_name, subcategory_name)
        if not publications:
            messagebox.showinfo("Tisk", f"Žádné publikace v podkategorii '{subcategory_name}' (kategorie '{category_name}', záložka '{tab_name}')")
            return
        self.preview_print(publications, f"Tisk z podkategorie '{subcategory_name}' (kategorie '{category_name}', záložka '{tab_name}')")

    def preview_print(self, publications, title):
        """Zobrazí náhled před tiskem s tabulkou a posuvníkem s dynamickou šířkou sloupců a minimální šířkou."""
        preview_window = tk.Toplevel(self.root)
        preview_window.title(title)
        preview_window.geometry("900x400")

        # Hlavní rámec pro tabulku a posuvník
        frame = ttk.Frame(preview_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Tabulka (Treeview)
        columns = ("Název", "Autor", "Rok", "Umístění")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Definice sloupců
        tree.heading("Název", text="Název")
        tree.heading("Autor", text="Autor")
        tree.heading("Rok", text="Rok vydání")
        tree.heading("Umístění", text="Umístění")

        # Posuvník
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=scrollbar.set)

        # Naplnění tabulky daty
        for pub in publications:
            location = (
                f"Záložka ({pub.get('tab', 'Neznámá záložka')}) - "
                f"Kategorie ({pub.get('category', 'Neznámá kategorie')}) - "
                f"Podkategorie ({pub.get('subcategory', 'Bez podkategorie')})"
            )
            tree.insert("", tk.END, values=(pub['title'], pub['author'], pub['year'], location))

        # Minimální šířka sloupců a dynamické přizpůsobení šířky
        column_min_width = {
            "Název": 150,
            "Autor": 120,
            "Rok": 80,
            "Umístění": 250,
        }

        for col in columns:
            # Dynamický výpočet šířky
            max_width = max(
                len(str(tree.set(item, col))) for item in tree.get_children()
            ) * 10  # Koeficient pro dostatečný prostor

            # Zajištění minimální šířky
            final_width = max(max_width, column_min_width[col])
            tree.column(col, width=final_width, anchor=tk.W)

        # Tlačítko pro tisk
        print_button = ttk.Button(preview_window, text="Tisk", command=lambda: self.print_text(self.generate_print_content(title, publications)))
        print_button.pack(pady=10)


    def generate_print_content(self, title, publications):
        """Generuje textový obsah pro tisk."""
        print_content = f"{title}\n\n"
        for pub in publications:
            location = (
                f"Záložka ({pub.get('tab', 'Neznámá záložka')}) - "
                f"Kategorie ({pub.get('category', 'Neznámá kategorie')}) - "
                f"Podkategorie ({pub.get('subcategory', 'Bez podkategorie')})"
            )
            print_content += (
                f"Název: {pub['title']}\nAutor: {pub['author']}\nRok vydání: {pub['year']}\n"
                f"Umístění: {location}\n\n"
            )
        return print_content

    def ensure_utf8(self, text):
        """Zajistí, že text je bezpečně kódován v UTF-8."""
        try:
            if isinstance(text, bytes):
                text = text.decode("utf-8")
            elif not isinstance(text, str):
                text = str(text)
            text.encode("utf-8")  # Ověříme, že text lze zapsat v UTF-8
            return text
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            print(f"Chyba při kódování textu: {e}, původní text: {text}")
            return text.encode("utf-8", errors="replace").decode("utf-8")

    def print_text(self, content):
        """Tiskne textový obsah pomocí PyQt5 Print Dialog."""
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QPainter, QFont  # Přidán správný import

            app = QApplication.instance() or QApplication([])  # Zajistí instanci aplikace

            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer)

            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)
                painter.setFont(QFont("Arial", 10))  # Nastavení písma
                painter.begin(printer)  # Zahájení kreslení na tiskárnu
                margin = 10
                y_offset = margin

                for line in content.splitlines():
                    if y_offset + 20 > printer.pageRect().height():  # Nová stránka
                        printer.newPage()
                        y_offset = margin

                    painter.drawText(margin, y_offset, line)
                    y_offset += 20

                painter.end()  # Ukončení kreslení na tiskárnu
                messagebox.showinfo("Tisk", "Seznam publikací byl úspěšně odeslán na tiskárnu.")
        except Exception as e:
            messagebox.showerror("Chyba při tisku", f"Nepodařilo se vytisknout publikace: {e}")


    def get_publications_by_tab(self, tab_name):
        """Získá všechny publikace v dané záložce."""
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            publications = []
            for category_name, category_data in data.get(tab_name, {}).items():
                if isinstance(category_data, dict):
                    # Kategorie
                    for pub in category_data.get("publikace", []):
                        pub["tab"] = tab_name
                        pub["category"] = category_name
                        pub["subcategory"] = None
                        publications.append(pub)
                    # Podkategorie
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                pub["tab"] = tab_name
                                pub["category"] = category_name
                                pub["subcategory"] = subcategory_name
                                publications.append(pub)
            return publications
        except Exception as e:
            print(f"Chyba při načítání publikací z tabulky: {e}")
            return []


    def get_publications_by_category(self, tab_name, category_name):
        """Získá všechny publikace v dané kategorii."""
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            publications = []
            category_data = data.get(tab_name, {}).get(category_name, {})

            # Publikace přímo v kategorii
            for pub in category_data.get("publikace", []):
                pub["tab"] = tab_name
                pub["category"] = category_name
                pub["subcategory"] = None
                publications.append(pub)

            # Publikace v podkategoriích
            for subcategory_name, subcategory_data in category_data.items():
                if isinstance(subcategory_data, dict):
                    for pub in subcategory_data.get("publikace", []):
                        pub["tab"] = tab_name
                        pub["category"] = category_name
                        pub["subcategory"] = subcategory_name
                        publications.append(pub)

            return publications
        except Exception as e:
            print(f"Chyba při načítání publikací z kategorie: {e}")
            return []

    def get_publications_by_subcategory(self, tab_name, category_name, subcategory_name):
            """Získá publikace z dané podkategorie."""
            try:
                with open("data.json", "r", encoding="utf-8") as file:
                    data = json.load(file)

                # Navigace do podkategorie
                subcategory_data = (
                    data.get(tab_name, {})
                        .get(category_name, {})
                        .get(subcategory_name, {})
                )

                publications = []
                for pub in subcategory_data.get("publikace", []):
                    pub["tab"] = tab_name
                    pub["category"] = category_name
                    pub["subcategory"] = subcategory_name
                    publications.append(pub)

                return publications
            except Exception as e:
                print(f"Chyba při načítání publikací z podkategorie: {e}")
                return []



    def setup_tab_layout(self, parent, tab_name):
        """Nastavení rozložení záložky."""
        # Hlavní rám pro levý a pravý panel
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Levý panel s pevnou šířkou
        left_frame = tk.Frame(main_frame, width=270, height=600)
        left_frame.pack(side="left", fill=tk.Y)
        left_frame.pack_propagate(False)

        # Pravý panel
        right_frame = tk.Frame(main_frame, width=800, height=600, bg="white")
        right_frame.pack(side="right", fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)

        # Posuvník a stromové zobrazení v levém panelu
        left_scrollbar = tk.Scrollbar(left_frame, orient="vertical")
        left_scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(left_frame, yscrollcommand=left_scrollbar.set, selectmode="browse", show="tree")
        tree.pack(fill=tk.BOTH, expand=True)
        left_scrollbar.config(command=tree.yview)

        ## Správa kategorií
        category_manager = CategoryManager(treeview=tree, tab_name=tab_name, parent_app=self)
        self.publication_managers[tab_name] = category_manager

        # Oddělený rámec pro tlačítka pod levým oknem
        button_frame = tk.Frame(parent)
        button_frame.pack(side="left", fill=tk.X, padx=(10, 0), pady=(5, 0))

        # První řada tlačítek pro přidání kategorií a podkategorií
        add_button_row = tk.Frame(button_frame)
        add_button_row.pack(fill=tk.X)

        add_category_btn = ttk.Button(add_button_row, text="Přidat kategorii", command=category_manager.add_category)
        add_subcategory_btn = ttk.Button(add_button_row, text="Přidat podkategorii", command=category_manager.add_subcategory)
        add_category_btn.pack(side="left", padx=2, expand=True, fill="x")
        add_subcategory_btn.pack(side="left", padx=2, expand=True, fill="x")

        # Druhá řada tlačítek pro odstranění kategorií a podkategorií
        remove_button_row = tk.Frame(button_frame)
        remove_button_row.pack(fill=tk.X, pady=(5, 0))

        remove_category_btn = ttk.Button(remove_button_row, text="Odebrat kategorii", command=category_manager.remove_category)
        remove_subcategory_btn = ttk.Button(remove_button_row, text="Odebrat podkategorii", command=category_manager.remove_subcategory)
        remove_category_btn.pack(side="left", padx=2, expand=True, fill="x")
        remove_subcategory_btn.pack(side="left", padx=2, expand=True, fill="x")

        # Rámec pro obsah v pravém panelu
        content_canvas = tk.Canvas(right_frame, bg="white")
        content_canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Vertikální posuvník pro pravý panel
        right_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=content_canvas.yview)
        right_scrollbar.pack(side="right", fill="y")
        content_canvas.config(yscrollcommand=right_scrollbar.set)

        # Vnitřní rámec pro publikace uvnitř pravého panelu
        publication_frame = tk.Frame(content_canvas, bg="white")
        content_canvas.create_window((0, 0), window=publication_frame, anchor="nw")

        # Aktualizace oblasti posuvníku podle obsahu
        def update_scroll_region(event):
            content_canvas.config(scrollregion=content_canvas.bbox("all"))

        publication_frame.bind("<Configure>", update_scroll_region)

        # Explicitně nezobrazujeme žádné publikace při inicializaci
        self.display_publications(publication_frame, category=None, subcategory=None, publications=None)

        # Tlačítko "Přidat publikaci" ve spodním rámu pod pravým panelem
        bottom_frame = tk.Frame(parent)
        bottom_frame.pack(fill=tk.X)
        ttk.Button(bottom_frame, text="Přidat publikaci", command=lambda: self.add_publication(tab_name)).pack(anchor="center", pady=5)

        # Propojení publication_frame s CategoryManager
        category_manager.publication_frame = publication_frame
    
        # Propojení výběru ve stromu s obnovou pravého okna
        tree.bind("<<TreeviewSelect>>", lambda event: self.on_tree_selection_change(tab_name))


    def display_publications(self, frame, category=None, subcategory=None, publications=None):
        """Vykreslí publikace v pravém okně."""
        # Vymazání aktuálního obsahu rámu
        for widget in frame.winfo_children():
            widget.destroy()

        if not publications:
            print(f"Nebyly nalezeny publikace pro kategorii '{category}' a podkategorii '{subcategory}'.")
            tk.Label(frame, text="Žádné publikace k zobrazení.", bg="white").pack(pady=10)
            return

        # Maximální rozměry obrázku pro náhled
        max_width, max_height = 150, 200

        # Vykreslení každé publikace
        for i, publication in enumerate(publications):
            thumbnail_frame = tk.Frame(frame, bg="white", bd=2, relief="groove")
            thumbnail_frame.grid(row=i // 5, column=i % 5, padx=10, pady=10)

            # Zobrazení obrázku
            image_path = publication.get("image_path")
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    # Zajištění poměru stran při změně velikosti
                    scale = min(max_width / image.width, max_height / image.height)
                    image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(thumbnail_frame, image=photo, bg="white", cursor="hand2")
                    image_label.image = photo  # Uchování reference na obrázek

                    # Přidání funkce pro zpracování kliknutí na obrázek
                    image_label.bind("<Button-1>", lambda e, pub=publication: self.open_publication_detail(pub))
                except Exception as e:
                    print(f"Chyba při načítání obrázku: {e}")
                    image_label = tk.Label(thumbnail_frame, text="Chyba obrázku", bg="lightgray", width=20, height=10)
            else:
                image_label = tk.Label(thumbnail_frame, text="Bez obálky", bg="lightgray", width=20, height=10)
            image_label.pack()

            # Zobrazení názvu publikace
            title = publication.get("title", "Bez názvu")
            title_label = tk.Label(thumbnail_frame, text=title, wraplength=140, bg="white", justify="center")
            title_label.pack()

        # Aktualizace oblasti posuvníku
        canvas = frame.master
        if isinstance(canvas, tk.Canvas):
            canvas.config(scrollregion=canvas.bbox("all"))


    def refresh_publications(self, category=None, subcategory=None):
        """Načte a zobrazí publikace pro danou kategorii nebo podkategorii."""
        try:
            data = self.load_json_file("data.json")
            if data is None:
                return  # Pokud nastane chyba při čtení, nedělat nic

            current_tab = self.notebook.tab(self.notebook.select(), "text")
            publications = []
            if category:
                category_data = data.get(current_tab, {}).get(category, {})
                if subcategory:
                    publications = category_data.get(subcategory, {}).get("publikace", [])
                else:
                    publications = category_data.get("publikace", [])

            # Zobrazení publikací v pravém panelu
            right_frame = self.publication_managers[current_tab].publication_frame
            self.display_publications(right_frame, category, subcategory, publications)
        except Exception as e:
            print(f"Chyba při obnovování publikací: {e}")
            messagebox.showerror("Chyba", f"Došlo k chybě při obnovování publikací: {e}")


    def on_tree_selection_change(self, tab_name):
        """Zpracuje změnu výběru ve stromovém zobrazení a aktualizuje pravé okno."""
        treeview = self.publication_managers[tab_name].treeview
        selected_items = treeview.selection()

        if not selected_items:
            # Pokud není nic vybráno, ponecháme pravé okno prázdné
            self.refresh_publications(None, None)
            return

        selected_item = selected_items[0]
        selected_category = treeview.item(selected_item, "text")
        parent_item = treeview.parent(selected_item)

        if parent_item:
            # Vybrána podkategorie
            selected_subcategory = selected_category
            selected_category = treeview.item(parent_item, "text")
        else:
            # Vybrána kategorie
            selected_subcategory = None

        self.refresh_publications(selected_category, selected_subcategory)
        
    def open_publication_detail(self, publication_data):
        """Otevře nové okno s detailem publikace."""
        try:
            # Načtení aktuálních dat
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)

            # Hledání publikace podle ID
            publication_id = publication_data.get("id")
            found_publication = None

            for tab_name, categories in data.items():
                for category_name, category_data in categories.items():
                    # Hledání v hlavní kategorii
                    for pub in category_data.get("publikace", []):
                        if pub.get("id") == publication_id:
                            found_publication = pub
                            break

                    # Hledání v podkategoriích
                    for subcategory_name, subcategory_data in category_data.items():
                        if isinstance(subcategory_data, dict):
                            for pub in subcategory_data.get("publikace", []):
                                if pub.get("id") == publication_id:
                                    found_publication = pub
                                    break

                    if found_publication:
                        break
                if found_publication:
                    break

            if not found_publication:
                messagebox.showerror("Chyba", "Publikace nebyla nalezena.")
                return

            # Vytvoření detailního okna publikace
            detail_window = tk.Toplevel(self.root)
            PublicationDetailWindow(
                master=detail_window,
                parent_app=self,  # Přidání odkazu na hlavní aplikaci
                publication_data=found_publication,
                on_delete_callback=lambda: self.refresh_publications(
                    found_publication.get("category"), found_publication.get("subcategory")
                ),
                on_close_callback=self.refresh_right_panel
            )


        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při otevírání detailu publikace: {e}")

        
    def refresh_right_panel(self):
        """Obnoví pravý panel podle aktuálního výběru ve stromovém zobrazení."""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab not in self.publication_managers:
            print(f"Záložka '{current_tab}' nemá správce publikací.")
            return

        treeview = self.publication_managers[current_tab].treeview
        selected_items = treeview.selection()

        if selected_items:
            selected_item = selected_items[0]
            selected_category = treeview.item(selected_item, "text")
            parent_item = treeview.parent(selected_item)

            if parent_item:
                # Vybrána podkategorie
                selected_subcategory = selected_category
                selected_category = treeview.item(parent_item, "text")
            else:
                # Vybrána kategorie
                selected_subcategory = None

            self.refresh_publications(selected_category, selected_subcategory)
        else:
            # Pokud není nic vybráno, vyprázdní pravý panel
            self.refresh_publications(None, None)
           
    def add_publication(self, tab_name):
        # Získání aktuálně vybraného stromového zobrazení
        treeview = self.publication_managers[tab_name].treeview
        selected_items = treeview.selection()  # Získá vybraný uzel

        if not selected_items:
            # Pokud není nic vybráno, zobrazí se upozornění
            messagebox.showwarning("Chyba", "Vyberte kategorii nebo podkategorii pro přidání publikace.")
            return

        # Získání názvu vybrané kategorie nebo podkategorie
        selected_item = selected_items[0]
        selected_category = treeview.item(selected_item, "text")  # Název aktuálního uzlu

        # Kontrola, zda je vybraná podkategorie
        parent_item = treeview.parent(selected_item)
        if parent_item:
            # Pokud má uzel rodiče, je to podkategorie
            selected_subcategory = selected_category
            selected_category = treeview.item(parent_item, "text")  # Název nadřazené kategorie
        else:
            # Pokud uzel nemá rodiče, je to kategorie
            selected_subcategory = None

        # Vytvoření dialogu pro přidání publikace
        PridatPublikaciDialog(
            parent=self.root,
            category=selected_category,
            subcategory=selected_subcategory,
            on_save_callback=self.save_publication
        )

    def save_publication(self, publication_data):
        """Uloží publikaci do JSON a aktualizuje pravý panel."""
        # Zajištění dynamické složky publikace
        publication_folder = os.path.join("Soubory", publication_data["id"])
        os.makedirs(publication_folder, exist_ok=True)

        # Přesun obrázku, pouze pokud není již na správném místě
        if publication_data["image_path"]:
            image_name = os.path.basename(publication_data["image_path"])
            new_image_path = os.path.join(publication_folder, image_name)
            
            if publication_data["image_path"] != new_image_path:  # Kontrola, zda soubor není již na správném místě
                shutil.copy(publication_data["image_path"], new_image_path)
            publication_data["image_path"] = new_image_path  # Aktualizace cesty v datech

        # Přesun PDF, pouze pokud není již na správném místě
        if publication_data["pdf_path"]:
            pdf_name = os.path.basename(publication_data["pdf_path"])
            new_pdf_path = os.path.join(publication_folder, pdf_name)
            
            if publication_data["pdf_path"] != new_pdf_path:  # Kontrola, zda soubor není již na správném místě
                shutil.copy(publication_data["pdf_path"], new_pdf_path)
            publication_data["pdf_path"] = new_pdf_path  # Aktualizace cesty v datech

        # Zajištění unikátního ID publikace
        if "id" not in publication_data:
            import uuid
            publication_data["id"] = str(uuid.uuid4())

        # Načtení existujících dat
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"Knihy": {}, "Časopisy": {}, "Datasheets": {}, "Ostatní": {}}

        # Zajištění struktury v JSON
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        category = publication_data["category"]
        subcategory = publication_data["subcategory"]

        node = data.setdefault(tab_name, {}).setdefault(category, {})
        if subcategory:
            node = node.setdefault(subcategory, {})
        node.setdefault("publikace", []).append(publication_data)

        # Uložení do JSON
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Publikace '{publication_data['title']}' byla úspěšně uložena.")

        # Obnovení pravého okna
        self.refresh_publications(category, subcategory)

    def export_to_sqlite(self, json_file, database_file):
        """Exportuje data z JSON do SQLite včetně souborů (obrázky a PDF)."""
        try:
            # Načtení dat z JSON souboru
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Připojení k databázi
            conn = sqlite3.connect(database_file)
            cursor = conn.cursor()

            # Vytvoření tabulky publikací
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publications (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    year TEXT,
                    description TEXT,
                    image BLOB,
                    pdf BLOB,
                    category TEXT,
                    subcategory TEXT
                )
            ''')

            # Funkce pro načtení souboru jako blob data
            def file_to_blob(file_path):
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        return f.read()
                return None

            # Iterace přes data a vkládání do databáze
            for tab, categories in data.items():
                for category, subcategories in categories.items():
                    for subcategory, content in subcategories.items():
                        if "publikace" in content:
                            for pub in content["publikace"]:
                                # Načtení souborů jako blob
                                image_blob = file_to_blob(pub.get("image_path", ""))
                                pdf_blob = file_to_blob(pub.get("pdf_path", ""))

                                # Vložení do databáze
                                cursor.execute('''
                                    INSERT OR REPLACE INTO publications (
                                        id, title, author, year, description, image, pdf, category, subcategory
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    pub["id"], pub["title"], pub["author"], pub["year"], pub["description"],
                                    image_blob, pdf_blob, category, subcategory
                                ))

            # Uložení změn a zavření databáze
            conn.commit()
            conn.close()

            print("Export do SQLite byl úspěšný.")
            return True

        except Exception as e:
            print(f"Chyba při exportu do SQLite: {e}")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = KnihovnaApp(root)
    root.mainloop()
    
    
# Pozdější integrace třídy class UniversalPrinter:

# Pokud budete chtít třídu využít, můžete zavolat její metody pro konkrétní potřeby, např.:

# printer = UniversalPrinter()
# printer.print_text("Toto je testovací text.")