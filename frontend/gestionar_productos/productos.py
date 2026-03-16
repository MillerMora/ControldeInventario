"""
frontend/gestionar_productos/productos.py — Panel de Gestión de Inventario
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, SearchBar, PrimaryButton, SecondaryButton,
    DangerButton, LabeledEntry, LabeledCombo, Divider,
)


DEMO_PRODUCTOS = [
    ("P-001", "Blusa floral",    "M",  "Rosa",  "15", "Estante A-3", "Disponible",  "$40"),
    ("P-002", "Jean skinny",     "28", "Azul",  "8",  "Estante B-1", "Disponible",  "$65"),
    ("P-003", "Jean slim",       "30", "Negro", "2",  "Estante B-2", "Stock bajo",  "$65"),
    ("P-004", "Chaqueta beige",  "L",  "Beige", "6",  "Estante C-1", "Disponible",  "$120"),
    ("P-005", "Blusa flores",    "S",  "Blanco","1",  "Estante A-1", "Crítico",     "$38"),
    ("P-006", "Camiseta básica", "XS", "Gris",  "22", "Estante A-5", "Disponible",  "$15"),
    ("P-007", "Falda plisada",   "M",  "Negro", "9",  "Estante D-2", "Disponible",  "$55"),
    ("P-008", "Vestido casual",  "L",  "Verde", "4",  "Estante D-4", "Disponible",  "$85"),
]

TALLAS  = ["XS", "S", "M", "L", "XL", "XXL",
           "24", "26", "28", "30", "32", "34", "36"]
ESTADOS = ["Disponible", "Stock bajo", "Crítico", "Inactivo"]


class ProductosPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self._form_visible = False
        self._build()

    def _build(self):
        # ── Barra superior ────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2,
                 sticky="ew", padx=24, pady=(18, 10))

        SearchBar(
            top,
            placeholder="Buscar por nombre, talla, color...",
            btn_text="+ Nuevo producto",
            on_add=self._toggle_form,
        ).pack(side="left")

        # Filtro de estado
        self.filter_combo = ctk.CTkComboBox(
            top,
            values=["Todos", "Disponible", "Stock bajo", "Crítico"],
            width=140, height=36,
            font=FONT_BODY,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.filter_combo.set("Todos")
        self.filter_combo.pack(side="left", padx=(12, 0))

        # ── Tabla principal ───────────────────────────────────────────────────
        self.table = StyledTable(
            self,
            columns=[
                ("ref",       "Ref.",     62),
                ("nombre",    "Producto", 160),
                ("talla",     "Talla",    60),
                ("color",     "Color",    80),
                ("stock",     "Stock",    60),
                ("ubicacion", "Ubicación",110),
                ("estado",    "Estado",  105),
                ("precio",    "Precio",   70),
            ],
            rows=DEMO_PRODUCTOS,
        )
        self.table.grid(row=1, column=0, sticky="nsew",
                        padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Panel lateral de formulario ───────────────────────────────────────
        self.form_panel = self._build_form_panel()
        # oculto al inicio

    def _build_form_panel(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=COLOR_WHITE,
            corner_radius=CORNER_R,
            border_width=1,
            border_color=COLOR_BORDER,
            width=270,
        )
        panel.grid_propagate(False)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        self.form_title_lbl = ctk.CTkLabel(
            inner, text="Nuevo producto",
            font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY,
        )
        self.form_title_lbl.pack(anchor="w", pady=(0, 14))

        Divider(inner).pack(fill="x", pady=(0, 14))

        # Campos del formulario
        self.f_nombre = LabeledEntry(inner, "Nombre del producto",
                                     placeholder="Ej. Blusa floral")
        self.f_nombre.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        self.f_talla = LabeledCombo(row1, "Talla", values=TALLAS)
        self.f_talla.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_color = LabeledEntry(row1, "Color", placeholder="Ej. Rosa")
        self.f_color.grid(row=0, column=1, sticky="ew")

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        self.f_stock = LabeledEntry(row2, "Stock", placeholder="0")
        self.f_stock.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_precio = LabeledEntry(row2, "Precio", placeholder="$0")
        self.f_precio.grid(row=0, column=1, sticky="ew")

        self.f_ubicacion = LabeledEntry(inner, "Ubicación",
                                        placeholder="Ej. Estante A-3")
        self.f_ubicacion.pack(fill="x", pady=(0, 10))

        self.f_estado = LabeledCombo(inner, "Estado", values=ESTADOS)
        self.f_estado.pack(fill="x", pady=(0, 16))

        # Stock mínimo
        self.f_min_stock = LabeledEntry(inner, "Stock mínimo",
                                        placeholder="5")
        self.f_min_stock.pack(fill="x", pady=(0, 16))

        Divider(inner).pack(fill="x", pady=(0, 14))

        # Botones de acción
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")

        self.save_btn = PrimaryButton(btn_row, "Guardar", command=self._on_save,
                                      width=120)
        self.save_btn.pack(side="left", padx=(0, 8))
        SecondaryButton(btn_row, "Cancelar", command=self._toggle_form,
                        width=90).pack(side="left")

        self.delete_btn = DangerButton(inner, "Eliminar producto",
                                       command=self._on_delete, width=999)
        self.delete_btn.pack(fill="x", pady=(10, 0))
        self.delete_btn.pack_forget()  # solo visible al editar

        return panel

    # ── Acciones UI ─────────────────────────────────────────────────────────────

    def _toggle_form(self):
        if self._form_visible:
            self.form_panel.grid_remove()
            self._form_visible = False
            self._clear_form()
            self.form_title_lbl.configure(text="Nuevo producto")
            self.delete_btn.pack_forget()
        else:
            self.form_panel.grid(
                row=1, column=1, sticky="nsew",
                padx=(0, 24), pady=(0, 20),
            )
            self._form_visible = True

    def _on_select(self, _event=None):
        data = self.table.get_selected()
        if not data:
            return
        # Rellenar formulario con datos de la fila seleccionada
        ref, nombre, talla, color, stock, ubicacion, estado, precio = data
        if not self._form_visible:
            self._toggle_form()
        self.form_title_lbl.configure(text=f"Editar — {ref}")
        self.f_nombre.set(nombre)
        self.f_talla.set(talla)
        self.f_color.set(color)
        self.f_stock.set(stock)
        self.f_ubicacion.set(ubicacion)
        self.f_estado.set(estado)
        self.f_precio.set(precio)
        self.delete_btn.pack(fill="x", pady=(10, 0))

    def _clear_form(self):
        for field in [self.f_nombre, self.f_color, self.f_stock,
                      self.f_precio, self.f_ubicacion, self.f_min_stock]:
            field.clear()
        self.f_talla.set(TALLAS[0])
        self.f_estado.set(ESTADOS[0])

    def _on_save(self):
        """
        TODO: Llamar a backend para INSERT / UPDATE en MySQL.
        Datos capturados:
            nombre   = self.f_nombre.get()
            talla    = self.f_talla.get()
            color    = self.f_color.get()
            stock    = self.f_stock.get()
            precio   = self.f_precio.get()
            ubicacion= self.f_ubicacion.get()
            estado   = self.f_estado.get()
            min_stock= self.f_min_stock.get()
        """
        pass

    def _on_delete(self):
        """
        TODO: Llamar a backend para DELETE en MySQL.
        Ref del producto seleccionado en la tabla.
        """
        pass