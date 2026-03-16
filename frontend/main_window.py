"""
frontend/main_window.py — Ventana principal con navegación lateral
Todo en una sola ventana: sidebar + panel dinámico
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import AlertBanner, Divider
from backend import productos as backend_productos, db


NAV_ITEMS = [
    ("dashboard",   "📊", "Dashboard"),
    ("inventario",  "📦", "Inventario"),
    ("ventas",      "🛍",  "Ventas"),
    ("envios",      "🚚", "Envíos"),
    ("usuarios",    "👤", "Usuarios"),
]


class MainWindow(ctk.CTk):
    def __init__(self, current_user):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.minsize(960, 620)
        self.configure(fg_color=COLOR_BG)
        self._center_window()

        self.current_user = current_user

        self._active_panel = None
        self._nav_buttons  = {}
        self._panels       = {}

        self._build_layout()
        self._load_panels()
        self._update_stock_badge()
        self._navigate("dashboard")

    def _center_window(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - WINDOW_W) // 2
        y = (sh - WINDOW_H) // 2
        self.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    # ── Estructura base ─────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

    # ── Sidebar ─────────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_W, fg_color=COLOR_SIDEBAR, corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(10, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 20))

        ctk.CTkLabel(
            logo_frame, text="Almacor",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLOR_ACCENT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text="Vélaris",
            font=FONT_NAV_SM,
            text_color=COLOR_TEXT_SIDEBAR_M,
        ).pack(anchor="w")

        Divider(sidebar, fg_color="#2C2C2E").grid(
            row=1, column=0, sticky="ew", padx=0, pady=0,
        )

        # Sección de navegación
        nav_label = ctk.CTkLabel(
            sidebar, text="MÓDULOS",
            font=("Helvetica Neue", 9, "bold"),
            text_color=COLOR_TEXT_SIDEBAR_M,
        )
        nav_label.grid(row=2, column=0, sticky="w", padx=20, pady=(16, 6))

        visible_items = []
        for key, icon, label in NAV_ITEMS:
            # Solo administradores pueden ver el módulo de usuarios
            if key == "usuarios" and not self.current_user.get("es_admin"):
                continue
            visible_items.append((key, icon, label))

        for i, (key, icon, label) in enumerate(visible_items):
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=COLOR_SIDEBAR_ITEM,
                text_color=COLOR_TEXT_SIDEBAR_M,
                font=FONT_NAV,
                corner_radius=8,
                command=lambda k=key: self._navigate(k),
            )
            btn.grid(row=3 + i, column=0, sticky="ew", padx=10, pady=2)
            self._nav_buttons[key] = btn

        # Separador antes del pie
        Divider(sidebar, fg_color="#2C2C2E").grid(
            row=10, column=0, sticky="sew", padx=0, pady=0,
        )

        # Usuario actual (pie de sidebar)
        user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        user_frame.grid(row=11, column=0, sticky="ew", padx=14, pady=14)

        avatar = ctk.CTkFrame(
            user_frame, width=34, height=34,
            fg_color=COLOR_ACCENT, corner_radius=17,
        )
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar, text="AD", font=("Helvetica Neue", 11, "bold"),
            text_color=COLOR_WHITE,
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            info,
            text=self.current_user.get("nombre", "Usuario"),
            font=FONT_SMALL,
            text_color=COLOR_TEXT_SIDEBAR,
        ).pack(anchor="w")
        rol_label = "Administrador" if self.current_user.get("es_admin") else "Empleado"
        ctk.CTkLabel(
            info,
            text=rol_label,
            font=FONT_MICRO,
            text_color=COLOR_TEXT_SIDEBAR_M,
        ).pack(anchor="w")

        # Logout
        ctk.CTkButton(
            user_frame, text="↩", width=28, height=28,
            fg_color="transparent", hover_color=COLOR_SIDEBAR_ITEM,
            text_color=COLOR_TEXT_SIDEBAR_M, font=FONT_BODY,
            command=self._logout,
        ).pack(side="right")

    # ── Área de contenido ────────────────────────────────────────────────────────
    def _build_content_area(self):
        self.content_wrapper = ctk.CTkFrame(
            self, fg_color=COLOR_BG, corner_radius=0,
        )
        self.content_wrapper.grid(row=0, column=1, sticky="nsew")
        self.content_wrapper.grid_columnconfigure(0, weight=1)
        self.content_wrapper.grid_rowconfigure(1, weight=1)

        # Topbar
        topbar = ctk.CTkFrame(
            self.content_wrapper,
            height=TOPBAR_H,
            fg_color=COLOR_WHITE,
            corner_radius=0,
        )
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        self.topbar_title = ctk.CTkLabel(
            topbar, text="", font=FONT_HEADING,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.topbar_title.grid(row=0, column=0, padx=24, pady=0, sticky="w")

        # Alertas en topbar
        self.alert_badge = ctk.CTkButton(
            topbar,
            text="",
            font=FONT_SMALL,
            width=220,
            height=30,
            fg_color=COLOR_WARNING_BG,
            hover_color="#FFE0B2",
            text_color=COLOR_WARNING,
            corner_radius=6,
        )
        self.alert_badge.grid(row=0, column=2, padx=16, pady=0, sticky="e")

        # Contenedor de paneles
        self.panel_container = ctk.CTkFrame(
            self.content_wrapper, fg_color=COLOR_BG, corner_radius=0,
        )
        self.panel_container.grid(row=1, column=0, sticky="nsew")
        self.panel_container.grid_columnconfigure(0, weight=1)
        self.panel_container.grid_rowconfigure(0, weight=1)

    # ── Carga diferida de paneles ─────────────────────────────────────────────
    def _load_panels(self):
        from frontend.dashboard.dashboard     import DashboardPanel
        from frontend.gestionar_productos.productos import ProductosPanel
        from frontend.ventas.ventas           import VentasPanel
        from frontend.envios.envios           import EnviosPanel
        from frontend.gestionar_usuario.usuarios import UsuariosPanel

        panel_classes = {
            "dashboard":  DashboardPanel,
            "inventario": ProductosPanel,
            "ventas":     VentasPanel,
            "envios":     EnviosPanel,
        }

        if self.current_user.get("es_admin"):
            panel_classes["usuarios"] = UsuariosPanel
        for key, cls in panel_classes.items():
            panel = cls(self.panel_container, main_window=self)
            panel.grid(row=0, column=0, sticky="nsew")
            self._panels[key] = panel

    # ── Navegación ────────────────────────────────────────────────────────────
    _TITLES = {
        "dashboard":  "Dashboard general",
        "inventario": "Gestión de inventario",
        "ventas":     "Registro de ventas",
        "envios":     "Seguimiento de envíos",
        "usuarios":   "Administración de usuarios",
    }

    def _navigate(self, key):
        # Ocultar todos
        for panel in self._panels.values():
            panel.grid_remove()

        # Mostrar el seleccionado
        self._panels[key].grid()

        # Actualizar topbar
        self.topbar_title.configure(text=self._TITLES.get(key, key.title()))

        # Actualizar estilos del nav
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLOR_SIDEBAR_ACTIVE,
                    text_color=COLOR_WHITE,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_SIDEBAR_M,
                )
        self._active_panel = key

    def _logout(self):
        self.after(50, self._launch_login)

    def _launch_login(self):
        self.destroy()
        from frontend.login.login import LoginWindow
        LoginWindow().mainloop()

    # ── Alertas de stock en topbar ─────────────────────────────────────────────
    def _update_stock_badge(self):
        if not db.is_available():
            self.alert_badge.configure(
                text="404 — Backend no disponible",
                fg_color=COLOR_DANGER_BG,
                text_color=COLOR_DANGER,
            )
            return

        try:
            items = backend_productos.productos_con_bajo_stock()
        except Exception:
            self.alert_badge.configure(
                text="404 — Error consultando stock",
                fg_color=COLOR_DANGER_BG,
                text_color=COLOR_DANGER,
            )
            return

        count = len(items)
        if count == 0:
            self.alert_badge.configure(
                text="✓ Stock en niveles normales",
                fg_color=COLOR_SUCCESS_BG,
                text_color=COLOR_SUCCESS,
            )
        else:
            self.alert_badge.configure(
                text=f"⚠  {count} producto(s) con stock bajo",
                fg_color=COLOR_WARNING_BG,
                text_color=COLOR_WARNING,
            )
