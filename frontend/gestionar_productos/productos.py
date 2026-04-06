"""
frontend/gestionar_productos/productos.py — Panel de Gestión de Inventario
"""

import tkinter.messagebox as messagebox
import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, SearchBar, PrimaryButton, SecondaryButton,
    DangerButton, LabeledEntry, LabeledCombo, Divider,
)
from backend import productos as backend_productos, db

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
        self._productos_cache = []
        self._productos_filtered = []
        self._selected_id = None
        self._build()
        self._load_from_backend()

    def _build(self):
        # ── Barra superior ────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2,
                 sticky="ew", padx=24, pady=(18, 10))

        self.search = SearchBar(
            top,
            placeholder="Buscar por nombre, talla, color...",
            btn_text="+ Nuevo producto",
            on_search=self._apply_filters,
            on_add=self._toggle_form,
        )
        self.search.pack(side="left")

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
        self.filter_combo.configure(command=lambda _v=None: self._apply_filters())
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
            rows=[],
        )
        self.table.grid(row=1, column=0, sticky="nsew",
                        padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<Button-1>", self._on_single_click)
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

        inner = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_fg_color=COLOR_CARD_ALT,
            scrollbar_button_color=COLOR_BORDER_DARK,
            scrollbar_button_hover_color=COLOR_TEXT_MUTED,
        )
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
            # Abrir siempre en modo "Nuevo producto" por defecto
            self._selected_id = None
            self._clear_form()
            self.form_title_lbl.configure(text="Nuevo producto")
            self.delete_btn.pack_forget()
            self.form_panel.grid(
                row=1, column=1, sticky="nsew",
                padx=(0, 24), pady=(0, 20),
            )
            self._form_visible = True

    def _on_select(self, _event=None):
        """Fallback for double-click/keyboard selection"""
        print("[UI productos] Selection event")
        self._populate_form()

    def _on_single_click(self, event):
        """Stable single-click handler with debounce"""
        print("[UI productos] Single click event")
        self.after(150, self._populate_form)

    def _populate_form(self):
        """Populate form with full data from selected row"""
        data = self.table.get_selected()
        if not data:
            print("[UI productos] No row selected")
            self._selected_id = None
            return
        
        ref, nombre, talla, color, stock, ubicacion, estado, precio = data
        
        # Find full product data in cache using ref
        self._selected_id = None
        cache_match = False
        for p in self._productos_cache:
            if p["referencia"] == ref:
                self._selected_id = p["id"]
                cache_match = True
                break
        
        if not cache_match:
            print(f"[UI productos] Cache miss for ref {ref}, reloading...")
            self._load_from_backend()
            # Retry after reload
            self.after(200, self._populate_form)
            return
        
        print(f"[UI productos] Populated ID: {self._selected_id} (ref: {ref})")

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
        
        # Load stock_minimo from cache
        for p in self._productos_cache:
            if p["id"] == self._selected_id:
                self.f_min_stock.set(str(p.get("stock_minimo", "")))
                break
        
        self.delete_btn.pack(fill="x", pady=(10, 0))

    def _clear_form(self):
        for field in [self.f_nombre, self.f_color, self.f_stock,
                      self.f_precio, self.f_ubicacion, self.f_min_stock]:
            field.clear()
        self.f_talla.set(TALLAS[0])
        self.f_estado.set(ESTADOS[0])

    def _on_save(self):
        print(f"[UI productos] Save clicked, selected_id={self._selected_id}")
        if not db.is_available():
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return

        try:
            nombre = self.f_nombre.get().strip()
            talla = self.f_talla.get().strip()
            color = self.f_color.get().strip()
            stock = int(self.f_stock.get() or "0")
            precio_txt = (self.f_precio.get() or "0").replace("$", "").replace(",", "")
            precio = float(precio_txt or 0)
            ubicacion = self.f_ubicacion.get().strip()
            min_stock = int(self.f_min_stock.get() or "0")
        except ValueError:
            messagebox.showerror("Error", "Por favor revisa que stock, stock mínimo y precio sean numéricos.")
            return

        if not nombre:
            messagebox.showerror("Error", "El nombre del producto es obligatorio.")
            return

        data = {
            "referencia": f"P-{nombre[:3].upper()}",
            "nombre": nombre,
            "talla": talla,
            "color": color,
            "stock": stock,
            "ubicacion": ubicacion,
            "precio": precio,
            "stock_minimo": min_stock,
        }

        try:
            if self._selected_id is None:
                backend_productos.crear_producto(data)
                print("[UI productos] Created new")
            else:
                backend_productos.actualizar_producto(self._selected_id, data)
                print("[UI productos] Updated")
            print("[UI productos] Backend success, reloading...")
            self._load_from_backend()
            print("[UI productos] Reloaded")
            self.table.tree.selection_remove(self.table.tree.selection())
            self._toggle_form()
            self.after(200, self._apply_filters)
            print("[UI productos] UI updated")
        except Exception as exc:
            print(f"[UI productos ERROR] {exc}")
            messagebox.showerror("Error", f"No se pudo guardar el producto.\n{exc}")

    def _on_delete(self):
        print(f"[UI productos] Delete clicked, id={self._selected_id}")
        if self._selected_id is None:
            print("[UI productos] No ID")
            return
        if not db.is_available():
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return
        
        try:
            # Verificar dependencias ANTES de eliminar
            delete_info = backend_productos.get_delete_info(self._selected_id)
            print(f"[UI productos] Delete info: {delete_info}")
            
            if delete_info['dependencias'] == 0:
                # Sin dependencias: eliminar directamente
                backend_productos.eliminar_producto(self._selected_id)
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            else:
                # Con dependencias: mostrar confirmación
                msg = (f"¡ADVERTENCIA!\n\n"
                       f"Este producto está asociado a {delete_info['dependencias']} venta(s).\n\n"
                       f"Si lo eliminas:\n"
                       f"• El producto desaparecerá del inventario\n"
                       f"• Las ventas históricas mantendrán la referencia (integridad preservada)\n\n"
                       f"¿Deseas continuar con la eliminación?")
                
                result = messagebox.askyesno("Confirmar eliminación", msg, icon="warning")
                if result:
                    backend_productos.eliminar_producto(self._selected_id)
                    messagebox.showinfo("Éxito", 
                        f"Producto eliminado.\n"
                        f"Las {delete_info['dependencias']} ventas mantienen referencia histórica.")
                else:
                    print("[UI productos] Delete cancelled by user")
                    return
            
            # Refresh UI
            print("[UI productos] Backend delete OK")
            self._selected_id = None
            self._load_from_backend()
            self.table.tree.selection_remove(self.table.tree.selection())
            self._toggle_form()
            self.after(200, self._apply_filters)
            print("[UI productos] Delete UI done")
            
        except Exception as exc:
            print(f"[UI productos ERROR delete] {exc}")
            messagebox.showerror("Error", f"No se pudo eliminar el producto.\n{str(exc)}")

    # ── Backend helpers ─────────────────────────────────────────────────────────
    def _load_from_backend(self):
        print("[UI productos] Loading backend...")
        if not db.is_available():
            print("[UI productos] DB unavailable")
            self.table.load_rows([])
            return
        try:
            productos = backend_productos.listar_productos()
            print(f"[UI productos] Loaded {len(productos)} from backend")
        except Exception as exc:
            print(f"[UI productos ERROR load] {exc}")
            self.table.load_rows([])
            return

        self._productos_cache = productos
        self._productos_filtered = productos
        self._apply_filters()

    def _apply_filters(self):
        """
        Aplica filtro de estado + búsqueda (sin reconsultar MySQL).
        """
        print("[UI productos] Applying filters...")
        if not self._productos_cache:
            self.table.load_rows([])
            return

        q = (self.search.get() or "").strip().lower()
        estado = (self.filter_combo.get() or "Todos").strip()

        filtered = []
        for p in self._productos_cache:
            if estado != "Todos" and p.get("estado") != estado:
                continue
            haystack = " ".join(
                [
                    str(p.get("referencia", "")),
                    str(p.get("nombre", "")),
                    str(p.get("talla", "")),
                    str(p.get("color", "")),
                    str(p.get("ubicacion", "")),
                    str(p.get("estado", "")),
                ]
            ).lower()
            if q and q not in haystack:
                continue
            filtered.append(p)

        self._productos_filtered = filtered
        rows = []
        for p in filtered:
            rows.append(
                (
                    p["referencia"],
                    p["nombre"],
                    p["talla"],
                    p["color"],
                    str(p["stock_actual"]),
                    p.get("ubicacion", ""),
                    p.get("estado", ""),
                    f"${p['precio']:.2f}",
                )
            )
        print(f"[UI productos] Table updated with {len(rows)} rows")
        self.table.load_rows(rows)

