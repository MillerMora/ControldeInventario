"""
frontend/login/login.py — Pantalla de inicio de sesión de Almacor
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import PrimaryButton, LabeledEntry
from backend import auth, db


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Almacor — Iniciar sesión")
        self.geometry("900x580")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        self._center_window(900, 580)
        self._build_ui()
        self._check_backend()

    def _center_window(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ── Layout dividido: izquierda decorativa | derecha formulario ─────────
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()

    # ── Panel izquierdo (branding) ─────────────────────────────────────────────
    def _build_left_panel(self):
        left = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)

        # Patrón decorativo (líneas geométricas)
        canvas = ctk.CTkCanvas(left, bg=COLOR_SIDEBAR,
                               highlightthickness=0, width=540, height=580)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        for i in range(0, 700, 40):
            canvas.create_line(i, 0, i - 300, 580,
                               fill="#2C2C2E", width=1)

        center = ctk.CTkFrame(left, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logotipo
        ctk.CTkLabel(
            center, text="Almacor",
            font=(FONT_FAMILY, 48, "bold"),
            text_color=COLOR_ACCENT,
        ).pack()

        ctk.CTkLabel(
            center, text="Sistema de gestión para Vélaris",
            font=FONT_NAV,
            text_color=COLOR_TEXT_SIDEBAR_M,
        ).pack(pady=(4, 0))

        # Línea decorativa
        sep = ctk.CTkFrame(center, height=2, width=80, fg_color=COLOR_ACCENT)
        sep.pack(pady=24)

        # Módulos
        modules = [
            ("▪", "Inventario inteligente"),
            ("▪", "Control de ventas"),
            ("▪", "Seguimiento de envíos"),
            ("▪", "Gestión de usuarios"),
        ]
        for icon, text in modules:
            row = ctk.CTkFrame(center, fg_color="transparent")
            row.pack(anchor="w", pady=3)
            ctk.CTkLabel(row, text=icon, font=FONT_BODY,
                         text_color=COLOR_ACCENT, width=20).pack(side="left")
            ctk.CTkLabel(row, text=text, font=FONT_BODY,
                         text_color=COLOR_TEXT_SIDEBAR_M).pack(side="left")

    # ── Panel derecho (formulario) ─────────────────────────────────────────────
    def _build_right_panel(self):
        right = ctk.CTkFrame(self, fg_color=COLOR_WHITE, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78)

        # Encabezado
        ctk.CTkLabel(
            form, text="Bienvenido",
            font=FONT_TITLE,
            text_color=COLOR_TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            form, text="Ingresa tus credenciales para continuar.",
            font=FONT_BODY,
            text_color=COLOR_TEXT_SECONDARY,
        ).pack(anchor="w", pady=(4, 28))

        # Campos
        self.field_user = LabeledEntry(form, "Usuario", placeholder="tu.usuario")
        self.field_user.pack(fill="x", pady=(0, 14))

        self.field_pass = LabeledEntry(form, "Contraseña",
                                       placeholder="••••••••", show="•")
        self.field_pass.pack(fill="x", pady=(0, 6))

        # Recordar sesión
        remember_row = ctk.CTkFrame(form, fg_color="transparent")
        remember_row.pack(fill="x", pady=(0, 28))
        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            remember_row, text="Recordar sesión",
            variable=self.remember_var,
            font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            border_color=COLOR_BORDER_DARK,
        ).pack(side="left")

        # Botón ingresar
        PrimaryButton(form, "Ingresar →", command=self._on_login,
                      width=999).pack(fill="x")

        # Mensaje de error (oculto por defecto)
        self.error_label = ctk.CTkLabel(
            form, text="", font=FONT_SMALL,
            text_color=COLOR_DANGER,
        )
        self.error_label.pack(pady=(12, 0))

        # Footer
        ctk.CTkLabel(
            right, text="Almacor v1.0  ·  Vélaris",
            font=FONT_MICRO,
            text_color=COLOR_TEXT_MUTED,
        ).place(relx=0.5, rely=0.97, anchor="s")

    # ── Lógica de login (placeholder — conectar al backend) ────────────────────
    def _on_login(self):
        usuario  = self.field_user.get().strip()
        password = self.field_pass.get().strip()

        if not usuario or not password:
            self._show_error("Por favor completa todos los campos.")
            return

        # Validar disponibilidad de backend
        if not db.is_available():
            self._show_404()
            return

        user = auth.login_user(usuario, password)  # Acepta usuario o email
        if not user:
            self._show_error("Usuario o contraseña incorrectos.")
            return

        # Login correcto
        self._open_main_window(user)

    def _show_error(self, msg):
        self.error_label.configure(text=msg)

    def _show_404(self):
        """
        Muestra un mensaje tipo 404 cuando el backend/BD no está disponible.
        No cierra la aplicación, solo informa al usuario.
        """
        self._show_error("404 — Backend / base de datos no disponible.")

    def _check_backend(self):
        """
        Comprobación temprana para mostrar 404 si la BD no existe.
        """
        if not db.is_available():
            self._show_404()

    def _open_main_window(self, user):
        self.after(50, lambda: self._launch_main(user))

    def _launch_main(self, user):
        self.destroy()
        from frontend.main_window import MainWindow
        app = MainWindow(current_user=user)
        app.mainloop()
