"""
Login provisional simple para pruebas
Este módulo será reemplazado por el login real que está desarrollando tu compañero
"""
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple


class LoginProvisional:
    """
    Ventana de login provisional con interfaz gráfica simple
    """
    def __init__(self):
        self.result = None
        self.window = None
    
    def show_login(self) -> Optional[Tuple[str, str]]:
        """
        Muestra ventana de login y retorna (username, password) o None si se cancela
        """
        self.window = tk.Tk()
        self.window.title("Login - Detector de Fatiga")
        self.window.geometry("400x250")
        self.window.resizable(False, False)
        
        # Centrar ventana
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Título
        title_label = tk.Label(
            self.window,
            text="DETECTOR DE FATIGA",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Frame para campos
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=10)
        
        # Usuario
        tk.Label(form_frame, text="Usuario:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = tk.Entry(form_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        self.username_entry.insert(0, "admin")  # Valor por defecto
        
        # Contraseña
        tk.Label(form_frame, text="Contraseña:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(form_frame, width=25, show="*", font=("Arial", 10))
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.password_entry.insert(0, "admin123")  # Valor por defecto
        
        # Nota
        note_label = tk.Label(
            self.window,
            text="Usuario por defecto: admin / admin123",
            font=("Arial", 8),
            fg="#7f8c8d"
        )
        note_label.pack(pady=5)
        
        # Botones
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)
        
        login_button = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            command=self._on_login,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2"
        )
        login_button.grid(row=0, column=0, padx=5)
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            cursor="hand2"
        )
        cancel_button.grid(row=0, column=1, padx=5)
        
        # Enter para login
        self.window.bind('<Return>', lambda e: self._on_login())
        self.window.bind('<Escape>', lambda e: self._on_cancel())
        
        # Foco en el campo de usuario
        self.username_entry.focus()
        
        # Esperar cierre
        self.window.mainloop()
        
        return self.result
    
    def _on_login(self):
        """Procesar login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos")
            return
        
        self.result = (username, password)
        self.window.destroy()
    
    def _on_cancel(self):
        """Cancelar login"""
        self.result = None
        self.window.destroy()


def get_credentials() -> Optional[Tuple[str, str]]:
    """
    Función helper para obtener credenciales de forma simple
    
    Returns:
        Tuple[str, str]: (username, password) o None si se cancela
    """
    login = LoginProvisional()
    return login.show_login()


if __name__ == "__main__":
    # Prueba del módulo
    credentials = get_credentials()
    if credentials:
        username, password = credentials
        print(f"Login exitoso: {username}")
    else:
        print("Login cancelado")
