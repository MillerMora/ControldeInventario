"""
frontend/ventas/ventas.py — Panel de Registro de Ventas
"""

import tkinter.messagebox as messagebox
import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, SearchBar, PrimaryButton, SecondaryButton,
    LabeledEntry, LabeledCombo, Divider, MetricCard,
)
from backend import ventas as backend_ventas, productos as backend_productos, usuarios as backend_usuarios, db


class VentasPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self._form_visible = False
        self._productos_idx = {}
        self._vendedores_idx = {}
        self._build()
        self._load_from_backend()

    def _build(self):
        # ── Métricas del día ─────────────────────────────────────────────────
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=0, column=0, columnspan=2,
                     sticky="ew", padx=24, pady=(18, 0))
        for i in range(3):
            metrics.grid_columnconfigure(i, weight=1)

        MetricCard(metrics, "Ventas hoy",    "$1,340", "8 transacciones").grid(
            row=0, column=0, sticky="ew", padx=(0, 10))
        MetricCard(metrics, "Ventas mes",    "$18,420", "+23% vs mes anterior",
                   sub_color=COLOR_SUCCESS).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        MetricCard(metrics, "Ticket promedio", "$167",  "Hoy").grid(
            row=0, column=2, sticky="ew")

        # ── Barra de búsqueda ─────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, columnspan=2,
                 sticky="ew", padx=24, pady=(14, 10))

        SearchBar(
            top,
            placeholder="Buscar por ID, producto, vendedor...",
            btn_text="+ Nueva venta",
            on_add=self._toggle_form,
        ).pack(side="left")

        # Filtro de fecha
        self.date_filter = ctk.CTkComboBox(
            top,
            values=["Hoy", "Esta semana", "Este mes", "Todo"],
            width=130, height=36,
            font=FONT_BODY,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.date_filter.set("Hoy")
        self.date_filter.pack(side="left", padx=(12, 0))

        # ── Tabla de ventas ──────────────────────────────────────────────────
        self.table = StyledTable(
            self,
            columns=[
                ("id",       "ID",        70),
                ("fecha",    "Fecha",    100),
                ("producto", "Producto", 170),
                ("total",    "Total",     75),
                ("descuento","Descuento", 80),
                ("vendedor", "Vendedor", 120),
                ("estado",   "Estado",   105),
            ],
            rows=[],
        )
        self.table.grid(row=2, column=0, sticky="nsew",
                        padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Formulario nueva venta ─────────────────────────────────────────────
        self.form_panel = self._build_form()

    def _build_form(self):
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

        ctk.CTkLabel(inner, text="Nueva venta",
                     font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY,
                     ).pack(anchor="w", pady=(0, 14))
        Divider(inner).pack(fill="x", pady=(0, 14))

        self.f_producto  = LabeledCombo(inner, "Producto",  values=[])
        self.f_producto.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        self.f_talla = LabeledEntry(row1, "Talla", placeholder="M")
        self.f_talla.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_cantidad = LabeledEntry(row1, "Cantidad", placeholder="1")
        self.f_cantidad.grid(row=0, column=1, sticky="ew")

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        self.f_precio_u = LabeledEntry(row2, "Precio unit.", placeholder="$0")
        self.f_precio_u.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_descuento = LabeledEntry(row2, "Descuento", placeholder="$0")
        self.f_descuento.grid(row=0, column=1, sticky="ew")

        self.f_vendedor = LabeledCombo(inner, "Vendedor", values=[])
        self.f_vendedor.pack(fill="x", pady=(0, 10))

        self.f_cliente  = LabeledEntry(inner, "Cliente (opcional)",
                                       placeholder="Nombre del cliente")
        self.f_cliente.pack(fill="x", pady=(0, 10))

        self.f_notas = ctk.CTkTextbox(
            inner, height=60, font=FONT_BODY,
            fg_color=COLOR_WHITE, border_color=COLOR_BORDER,
            border_width=1, corner_radius=BTN_CORNER,
        )
        self.f_notas.pack(fill="x", pady=(0, 16))
        self.f_notas.insert("0.0", "Notas adicionales...")

        # Total calculado
        total_frame = ctk.CTkFrame(inner, fg_color=COLOR_CARD_ALT,
                                   corner_radius=8)
        total_frame.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(total_frame, text="Total estimado",
                     font=FONT_SMALL, text_color=COLOR_TEXT_SECONDARY,
                     ).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(total_frame, text="$0.00",
                     font=FONT_HEADING, text_color=COLOR_ACCENT,
                     ).pack(side="right", padx=12, pady=8)

        Divider(inner).pack(fill="x", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "Registrar venta", command=self._on_save,
                      width=160).pack(side="left", padx=(0, 8))
        SecondaryButton(btn_row, "Cancelar", command=self._toggle_form,
                        width=90).pack(side="left")

        return panel

    def _toggle_form(self):
        if self._form_visible:
            self.form_panel.grid_remove()
            self._form_visible = False
        else:
            self.form_panel.grid(row=2, column=1, sticky="nsew",
                                 padx=(0, 24), pady=(0, 20))
            self._form_visible = True

    def _on_select(self, _event=None):
        pass  # Ver detalle de venta (futuro)

    def _on_save(self):
        if not db.is_available():
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return

        nombre_producto = self.f_producto.get()
        vendedor_nombre = self.f_vendedor.get()
        if not nombre_producto or not vendedor_nombre:
            messagebox.showerror("Error", "Selecciona producto y vendedor.")
            return

        try:
            cantidad = int(self.f_cantidad.get() or "0")
            precio_txt = (self.f_precio_u.get() or "0").replace("$", "").replace(",", "")
            precio_unit = float(precio_txt or 0)
            desc_txt = (self.f_descuento.get() or "0").replace("$", "").replace(",", "")
            descuento = float(desc_txt or 0)
        except ValueError:
            messagebox.showerror("Error", "Revisa que cantidad, precio y descuento sean numéricos.")
            return

        if cantidad <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
            return

        producto_id = self._productos_idx.get(nombre_producto)
        vendedor_id = self._vendedores_idx.get(vendedor_nombre)
        if not producto_id or not vendedor_id:
            messagebox.showerror("Error", "No se pudo resolver producto o vendedor en la base de datos.")
            return

        data = {
            "producto_id": producto_id,
            "talla": self.f_talla.get().strip(),
            "cantidad": cantidad,
            "precio_unit": precio_unit,
            "descuento": descuento,
            "cliente": self.f_cliente.get().strip() or None,
            "vendedor_id": vendedor_id,
            "notas": self.f_notas.get("0.0", "end").strip() or None,
            "codigo": None,
        }

        try:
            backend_ventas.registrar_venta(data)
            self._load_from_backend()
            self._toggle_form()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar la venta.\n{exc}")

    # ── Backend helpers ─────────────────────────────────────────────────────────
    def _load_from_backend(self):
        if not db.is_available():
            self.table.load_rows([])
            return

        # Cargar ventas
        try:
            rows = backend_ventas.listar_ventas()
        except Exception:
            self.table.load_rows([])
        else:
            tabla_rows = []
            for v in rows:
                tabla_rows.append(
                    (
                        v["codigo"],
                        v["fecha"].strftime("%d/%m/%Y") if hasattr(v["fecha"], "strftime") else str(v["fecha"]),
                        v.get("detalle", ""),
                        f"${v['total']:.2f}",
                        f"${v['descuento']:.2f}" if v.get("descuento") else "—",
                        v.get("vendedor", ""),
                        v.get("estado", "").capitalize(),
                    )
                )
            self.table.load_rows(tabla_rows)

        # Cargar combos de productos y vendedores
        try:
            productos = backend_productos.listar_productos()
            usuarios = backend_usuarios.listar_usuarios()
        except Exception:
            return

        self._productos_idx = {p["nombre"]: p["id"] for p in productos}
        self._vendedores_idx = {
            u["nombre"]: u["id"] for u in usuarios if u["rol"].upper() != "ADMIN"
        }

        if self._productos_idx:
            self.f_producto.set(next(iter(self._productos_idx.keys())))
            self.f_producto.combo.configure(values=list(self._productos_idx.keys()))
        if self._vendedores_idx:
            self.f_vendedor.set(next(iter(self._vendedores_idx.keys())))
            self.f_vendedor.combo.configure(values=list(self._vendedores_idx.keys()))

