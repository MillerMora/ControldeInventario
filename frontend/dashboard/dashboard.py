"""
frontend/dashboard/dashboard.py — Panel de Dashboard principal
"""

import datetime
import customtkinter as ctk
from frontend.theme import *
from frontend.components import MetricCard, StyledTable, AlertBanner, Divider
from backend import productos as backend_productos, ventas as backend_ventas, envios as backend_envios, db


class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()
        self._load_from_backend()

    def _build(self):
        # ── Cabecera ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Dashboard general",
            font=FONT_TITLE, text_color=COLOR_TEXT_PRIMARY,
        ).pack(side="left")
        hoy = datetime.datetime.now().strftime("%A %d de %B, %Y")
        ctk.CTkLabel(
            header, text=hoy,
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED,
        ).pack(side="right", pady=(6, 0))

        # ── Tarjetas de métricas ─────────────────────────────────────────────────
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 0))
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)

        self.metric_productos = MetricCard(
            metrics_frame, label="Productos totales", value="—", sub=""
        )
        self.metric_productos.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=0)

        self.metric_ventas_hoy = MetricCard(
            metrics_frame, label="Ventas hoy", value="—", sub=""
        )
        self.metric_ventas_hoy.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=0)

        self.metric_envios = MetricCard(
            metrics_frame, label="Envíos activos", value="—", sub=""
        )
        self.metric_envios.grid(row=0, column=2, sticky="ew", padx=(0, 10), pady=0)

        self.metric_stock = MetricCard(
            metrics_frame, label="Stock crítico", value="—", sub=""
        )
        self.metric_stock.grid(row=0, column=3, sticky="ew", padx=(0, 0), pady=0)

        # ── Fila inferior: tablas + alertas ────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_columnconfigure(2, weight=2)
        bottom.grid_rowconfigure(1, weight=1)

        # Ventas recientes
        ctk.CTkLabel(
            bottom, text="Últimas ventas",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.ventas_table = StyledTable(
            bottom,
            columns=[
                ("producto", "Producto",  140),
                ("talla",    "Talla",      55),
                ("qty",      "Qty",        45),
                ("total",    "Total",      65),
                ("estado",   "Estado",    100),
                ("vendedor", "Vendedor",  110),
            ],
            rows=[],
        )
        self.ventas_table.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        # Envíos activos
        ctk.CTkLabel(
            bottom, text="Envíos activos",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=1, sticky="w", pady=(0, 6))

        self.envios_table = StyledTable(
            bottom,
            columns=[
                ("guia",    "Guía",      70),
                ("cliente", "Cliente",   90),
                ("ciudad",  "Ciudad",    80),
                ("estado",  "Estado",    95),
            ],
            rows=[],
        )
        self.envios_table.grid(row=1, column=1, sticky="nsew", padx=(0, 12))

        # Alertas de stock
        ctk.CTkLabel(
            bottom, text="Alertas de stock",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=2, sticky="w", pady=(0, 6))

        alerts_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        alerts_frame.grid(row=1, column=2, sticky="nsew")

        self.alerts_frame = alerts_frame

        # Botón ir a inventario
        ctk.CTkButton(
            alerts_frame,
            text="Ver inventario completo →",
            font=FONT_SMALL,
            width=180, height=32,
            fg_color="transparent",
            hover_color=COLOR_CARD_ALT,
            text_color=COLOR_ACCENT,
            border_color=COLOR_ACCENT,
            border_width=1,
            corner_radius=BTN_CORNER,
            command=lambda: self.main_window._navigate("inventario")
                    if self.main_window else None,
        ).pack(anchor="w", pady=(4, 0))

    # ── Backend helpers ─────────────────────────────────────────────────────────
    def _load_from_backend(self):
        if not db.is_available():
            # Mostrar 404 suave en métricas
            self.metric_productos.configure(value="—", sub="404 backend no disponible")
            self.metric_ventas_hoy.configure(value="—", sub="")
            self.metric_envios.configure(value="—", sub="")
            self.metric_stock.configure(value="—", sub="")
            return

        # Productos / stock
        try:
            productos = backend_productos.listar_productos()
            stock_bajo = backend_productos.productos_con_bajo_stock()
        except Exception:
            productos = []
            stock_bajo = []

        self.metric_productos.configure(
            value=str(len(productos)),
            sub="Registrados en inventario",
        )
        self.metric_stock.configure(
            value=str(len(stock_bajo)),
            sub="Requieren reposición" if stock_bajo else "Todo en orden",
        )

        # Ventas
        try:
            ventas = backend_ventas.listar_ventas()
        except Exception:
            ventas = []

        hoy = datetime.date.today()
        ventas_hoy = [v for v in ventas if getattr(v["fecha"], "date", lambda: hoy)() == hoy]
        total_hoy = sum(float(v["total"]) for v in ventas_hoy) if ventas_hoy else 0.0
        self.metric_ventas_hoy.configure(
            value=f"${total_hoy:.2f}",
            sub=f"{len(ventas_hoy)} transacciones hoy",
        )

        tabla_ventas = []
        for v in ventas[:5]:
            tabla_ventas.append(
                (
                    v.get("detalle", ""),
                    "",
                    "",  # Qty no está detallada por producto en este resumen
                    f"${v['total']:.2f}",
                    v.get("estado", "").capitalize(),
                    v.get("vendedor", ""),
                )
            )
        self.ventas_table.load_rows(tabla_ventas)

        # Envíos
        try:
            envs = backend_envios.listar_envios()
        except Exception:
            envs = []

        activos = [e for e in envs if e.get("estado") == "EN_TRANSITO"]
        self.metric_envios.configure(
            value=str(len(activos)),
            sub=f"{len(envs)} totales",
        )

        tabla_envios = []
        for e in envs[:5]:
            tabla_envios.append(
                (
                    e["guia"],
                    e["cliente"],
                    e["ciudad_destino"],
                    e.get("estado", "").replace("_", " ").title(),
                )
            )
        self.envios_table.load_rows(tabla_envios)

        # Alertas de stock
        for child in self.alerts_frame.winfo_children():
            # Limpiar solo los AlertBanner existentes (no el botón)
            if isinstance(child, AlertBanner):
                child.destroy()

        for p in stock_bajo[:5]:
            nivel = "danger" if p["stock_actual"] <= max(1, int(p["stock_minimo"] * 0.4)) else "warning"
            msg = f"{p['nombre']} T.{p['talla']} — {p['stock_actual']} unidades (mínimo: {p['stock_minimo']})"
            AlertBanner(self.alerts_frame, msg, level=nivel).pack(
                fill="x", pady=(0, 8),
            )
