"""
frontend/envios/envios.py — Panel de Seguimiento de Envíos
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, SearchBar, PrimaryButton, SecondaryButton,
    LabeledEntry, LabeledCombo, Divider, MetricCard,
)


DEMO_ENVIOS = [
    ("GU-2024", "14/03/2026", "Chaqueta beige L", "Medellín", "Valentina R.", "En tránsito"),
    ("GU-2023", "13/03/2026", "Jean skinny 28", "Cali", "Carlos M.", "Entregado"),
    ("GU-2022", "12/03/2026", "Blusa floral M", "Bogotá", "Valentina R.", "Pendiente"),
    ("GU-2021", "11/03/2026", "Camiseta S ×2", "Pereira", "Carlos M.", "En tránsito"),
    ("GU-2020", "10/03/2026", "Falda plisada M", "Medellín", "Valentina R.", "Entregado"),
    ("GU-2019", "09/03/2026", "Vestido casual L", "Cali", "Carlos M.", "Cancelado"),
    ("GU-2018", "08/03/2026", "Jean slim 30", "Bogotá", "Valentina R.", "Entregado"),
    ("GU-2017", "07/03/2026", "Blusa flores S", "Pereira", "Carlos M.", "Pendiente"),
]

CIUDADES = ["Medellín", "Bogotá", "Cali", "Pereira", "Bucaramanga", "Barranquilla"]
VENDEDORES = ["Valentina R.", "Carlos M.", "Admin"]


class EnviosPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self._form_visible = False
        self._build()

    def _build(self):
        # ── Métricas ──────────────────────────────────────────────────────────
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(18, 0))
        for i in range(3):
            metrics.grid_columnconfigure(i, weight=1)

        MetricCard(metrics, "Envíos hoy", "12", "5 entregados").grid(row=0, column=0, sticky="ew", padx=(0, 10))
        MetricCard(metrics, "En tránsito", "3", "+2 vs ayer").grid(row=0, column=1, sticky="ew", padx=(0, 10))
        MetricCard(metrics, "Pendientes", "2", "Prioridad").grid(row=0, column=2, sticky="ew")

        # ── Barra búsqueda ───────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(14, 10))

        SearchBar(
            top,
            placeholder="Buscar por guía, cliente, ciudad...",
            btn_text="+ Nuevo envío",
            on_add=self._toggle_form,
        ).pack(side="left")

        self.ciudad_filter = ctk.CTkComboBox(
            top,
            values=["Todas"] + CIUDADES,
            width=140, height=36,
            font=FONT_BODY,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.ciudad_filter.set("Todas")
        self.ciudad_filter.pack(side="left", padx=(12, 0))

        # ── Tabla envíos ─────────────────────────────────────────────────────
        self.table = StyledTable(
            self,
            columns=[
                ("guia", "Guía", 80),
                ("fecha", "Fecha", 100),
                ("producto", "Producto", 170),
                ("destino", "Destino", 100),
                ("vendedor", "Vendedor", 110),
                ("estado", "Estado", 110),
            ],
            rows=DEMO_ENVIOS,
        )
        self.table.grid(row=2, column=0, sticky="nsew", padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.form_panel = self._build_form()

    def _build_form(self):
        panel = ctk.CTkFrame(self, fg_color=COLOR_WHITE, corner_radius=CORNER_R, border_width=1, border_color=COLOR_BORDER, width=280)
        panel.grid_propagate(False)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(inner, text="Nuevo envío", font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 14))
        Divider(inner).pack(fill="x", pady=(0, 14))

        self.f_guia = LabeledEntry(inner, "Nº Guía", placeholder="GU-YYYY-####")
        self.f_guia.pack(fill="x", pady=(0, 10))

        self.f_producto = LabeledEntry(inner, "Producto", placeholder="Chaqueta beige L")
        self.f_producto.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        self.f_cliente = LabeledEntry(row1, "Cliente", placeholder="Juan Pérez")
        self.f_cliente.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_destino = LabeledCombo(row1, "Destino", values=CIUDADES)
        self.f_destino.grid(row=0, column=1, sticky="ew")

        self.f_vendedor = LabeledCombo(inner, "Vendedor", values=VENDEDORES)
        self.f_vendedor.pack(fill="x", pady=(0, 10))

        self.f_direccion = ctk.CTkTextbox(inner, height=60, font=FONT_BODY, fg_color=COLOR_WHITE, border_color=COLOR_BORDER, border_width=1, corner_radius=BTN_CORNER)
        self.f_direccion.pack(fill="x", pady=(0, 16))
        self.f_direccion.insert("0.0", "Dirección completa de entrega...")

        Divider(inner).pack(fill="x", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "Registrar envío", command=self._on_save, width=160).pack(side="left", padx=(0, 8))
        SecondaryButton(btn_row, "Cancelar", command=self._toggle_form, width=90).pack(side="left")

        return panel

    def _toggle_form(self):
        if self._form_visible:
            self.form_panel.grid_remove()
            self._form_visible = False
        else:
            self.form_panel.grid(row=2, column=1, sticky="nsew", padx=(0, 24), pady=(0, 20))
            self._form_visible = True

    def _on_select(self, _event=None):
        pass  # Detalle envío futuro

    def _on_save(self):
        """
        TODO: Conectar con backend.envios.registrar_envio()
        Datos:
            guia      = self.f_guia.get()
            producto  = self.f_producto.get()
            cliente   = self.f_cliente.get()
            destino   = self.f_destino.get()
            vendedor  = self.f_vendedor.get()
            direccion = self.f_direccion.get("0.0", "end").strip()
        """
        pass

