import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import sys
import datetime
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from controllers import deviceController, backupController, conexion


class BackupGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Software de Backups - Dispositivos de Red")
        self.master.geometry("700x650")
        self.master.resizable(False, False)
        self.master.configure(bg="#404040")

        # Fuentes
        self.font_titulo = font.Font(family="Verdana", size=14, weight="bold")
        self.font_normal = font.Font(family="Verdana", size=10)
        self.font_boton = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_encabezado = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_contenido = font.Font(family="Verdana", size=9)

        self.fields = self.inicializar_campos()
        self.selected_device_id = None
        self.selected_device_name = None 

        self.entry_widgets = {}
        self.construir_widgets()
        self.actualizar_vista_arbol()  # NUEVO

    def inicializar_campos(self):
        return {
            "Nombre": tk.StringVar(),
            "IP": tk.StringVar(),
            "Usuario": tk.StringVar(),
            "Contraseña": tk.StringVar(),
            "Puerto SSH": tk.StringVar(),
            "Hora": tk.StringVar(),
            "Periodicidad": tk.StringVar(),
        }

    def construir_widgets(self):
        self.construir_botones_superiores()
        self.construir_lista_dispositivos()
        self.construir_formulario_detalles()
        self.construir_botones_inferiores()

    def construir_botones_superiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        tk.Button(
            frame,
            text="Nuevo",
            width=12,
            command=self.habilitar_nuevo_dispositivo,
            bg="#8575E4",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame,
            text="Editar",
            width=12,
            command=self.editar_dispositivo,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame,
            text="Eliminar",
            width=12,
            command=self.eliminar_dispositivo,
            bg="red",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            frame,
            text="Gestionar Backup",
            width=16,
            font=self.font_boton,
            command=self.abrir_ventana_backups,
        ).grid(row=0, column=3, padx=5)


    def abrir_ventana_backups(self):
        if self.selected_device_id is None:
            messagebox.showwarning("Seleccionar Dispositivo", "Por favor, selecciona un dispositivo para gestionar sus backups.")
            return

        ventana = tk.Toplevel(self.master)
        ventana.title(f"Historial de Backups para: {self.selected_device_name}")
        ventana.geometry("700x450")
        ventana.configure(bg="#404040")
        ventana.resizable(False, False)

        tk.Label(
            ventana,
            text=f"Backups de {self.selected_device_name}",
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        ).pack(pady=10)

        frame_tabla = tk.Frame(ventana, bg="#404040")
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        # El ID no se muestra, pero se almacena en el iid para eliminación
        columnas = ("Fecha", "Archivo de Backup", "Dispositivo")   # PROBABLEMENTE QUITAR ARCHIVO BACKUP
        self.backup_tree = ttk.Treeview( 
            frame_tabla,
            columns=columnas,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=10,
        )
        for col in columnas:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=200)

        self.backup_tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.backup_tree.yview)
        scrollbar_x.config(command=self.backup_tree.xview)

        # Cargar los backups reales del dispositivo seleccionado
        self._load_device_backups_into_treeview(self.backup_tree, self.selected_device_id, self.selected_device_name)

        # Frame para botones de la ventana de backups
        button_frame_backup = tk.Frame(ventana, pady=10, bg="#404040")
        button_frame_backup.pack()

        tk.Button(
            button_frame_backup,
            text="Realizar Backup",
            width=15,
            command=self.realizar_backup, 
            bg="#008000",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame_backup,
            text="Eliminar Backup",
            width=15,
            command=self.eliminar_backup, 
            bg="red",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=1, padx=10)

    def _load_device_backups_into_treeview(self, treeview_widget, device_id, device_name):
        for item in treeview_widget.get_children():
            treeview_widget.delete(item)

        # Obtener los backups reales para este device_id desde el controlador
        backups = backupController.get_backups_for_device(device_id)

        for backup in backups:
            treeview_widget.insert(
                "",
                "end",
                iid=backup["ID"], # Usamos el ID del backup como iid para futuras operaciones
                values=(backup["Fecha"], backup["Archivo"], device_name)
            )

    def realizar_backup(self):
        if self.selected_device_id is None:
            messagebox.showwarning("Error", "No hay dispositivo seleccionado para realizar backup.")
            return

        device_data = deviceController.get_device_by_id(self.selected_device_id)
        if not device_data:
            messagebox.showerror("Error", "No se pudieron obtener los datos del dispositivo seleccionado.")
            return

        host = device_data["IP"]
        usuario = device_data["Usuario"]
        contrasena = device_data["Contraseña"]
        try:
            puerto = int(device_data["Puerto SSH"])
        except ValueError:
            messagebox.showerror("Error", "El puerto SSH no es un número válido.")
            return

        messagebox.showinfo("Iniciando Backup", "Intentando generar backup en el Mikrotik. Esto puede tomar unos segundos...")
        
        # Generar el backup en el Mikrotik
        success_gen, msg_gen = conexion.genera_backup(host, usuario, contrasena, puerto)
        if not success_gen:
            messagebox.showerror("Error al Generar Backup", msg_gen)
            return
        
        # Dar un pequeño tiempo para que el Mikrotik genere el archivo
        time.sleep(2)

        messagebox.showinfo("Descargando Backup", "Backup generado. Intentando descargar el archivo más reciente...")

        # Descargar el contenido del backup más reciente
        success_download, backup_content, backup_filename = conexion.obtener_y_descargar_backup_mas_reciente(
            host, usuario, contrasena, puerto
        )

        if not success_download:
            messagebox.showerror("Error al Descargar Backup", backup_filename)
            return

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Almacenar el contenido del backup en la base de datos
        success_db = backupController.add_backup(current_time, self.selected_device_id, backup_content)

        if success_db:
            messagebox.showinfo("Backup Realizado", f"Backup '{backup_filename}' para {self.selected_device_name} guardado en la base de datos.")
            if hasattr(self, 'backup_tree') and self.backup_tree.winfo_exists():
                self._load_device_backups_into_treeview(self.backup_tree, self.selected_device_id, self.selected_device_name)
        else:
            messagebox.showerror("Error", f"No se pudo guardar el backup '{backup_filename}' en la base de datos.")


    def eliminar_backup(self):
        if self.selected_device_id is None:
            messagebox.showwarning("Error", "No hay dispositivo seleccionado.")
            return

        selected_backup_item = self.backup_tree.focus()
        if not selected_backup_item:
            messagebox.showwarning("Seleccionar Backup", "Por favor, selecciona un backup para eliminar.")
            return

        # selected_backup_item ya es el iid (identificador interno del item), que es el ID del backup
        backup_id_to_delete = selected_backup_item
        
        confirm = messagebox.askyesno(
            "Confirmar Eliminación", "¿Estás seguro de que deseas eliminar este backup?"
        )

        if confirm:
            success = backupController.delete_backup(backup_id_to_delete)

            if success:
                messagebox.showinfo("Backup Eliminado", "Backup eliminado correctamente de la base de datos.")
                self._load_device_backups_into_treeview(self.backup_tree, self.selected_device_id, self.selected_device_name)
            else:
                messagebox.showerror("Error", "No se pudo eliminar el backup de la base de datos.")


    def construir_lista_dispositivos(self):

        frame = tk.LabelFrame(
            self.master,
            text="Dispositivos Registrados",
            padx=10,
            pady=10,
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        )
        frame.pack(padx=10, pady=5, fill="x")

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#505050",
            foreground="white",
            fieldbackground="#505050",
            font=self.font_tabla_contenido,
        )
        style.map("Treeview", background=[["selected", "blue"]])
        style.configure(
            "Treeview.Heading",
            background="#606060",
            foreground="white",
            font=self.font_tabla_encabezado,
        )

        container = tk.Frame(frame)
        container.pack(fill="both", expand=True)
        # Barra vertical
        scrollbar_y = ttk.Scrollbar(container, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        # Barrita horizontal
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        cols = ("Nombre", "IP", "Usuario", "Contraseña", "Periodicidad")
        self.tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            height=5,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True)

        # Vincular las scrollbars con el Treeview
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_arbol)
        self.actualizar_vista_arbol() # SOSPECHOSO

        self.tree_menu = tk.Menu(self.master, tearoff=0)
        self.tree_menu.add_command(
            label="Mostrar Contraseña", command=self.mostrar_contrasena_tab
        )
        self.tree_menu.add_command(
            label="Ocultar Contraseña", command=self.ocultar_contrasena_tabla
        )
        for col in cols:
            if col == "Periodicidad":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=200)

        self.tree.bind("<Button-3>", self._mostrar_menu_tabla)

    def habilitar_nuevo_dispositivo(self):
        self.selected_device_id = None
        self.limpiar_formulario()
        self.habilitar_campos()
        # for entry in self.entry_widgets.values():
        #     entry.config(state="normal")
        self.tree.unbind("<<TreeviewSelect>>")
        messagebox.showinfo(
            "Nuevo dispositivo", "Puedes ingresar los detalles de un nuevo dispositivo."
        )
        self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_arbol)
        
    def _mostrar_menu_tabla(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.tree_menu.post(event.x_root, event.y_root)

    def mostrar_contrasena_tab(self):  # NUEVO
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            device_id = (
                self.tree.item(item_id, "tags")[0]
                if self.tree.item(item_id, "tags")
                else None
            )
            if device_id is not None:
                device_data = deviceController.get_device_by_id(device_id)
                if device_data:
                    values[3] = device_data["Contraseña"]
                    self.tree.item(item_id, values=values)

    def ocultar_contrasena_tabla(self):  # NUEVO
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            contrasena_actual = values[3]
            contrasena_oculta = (
                "*" * len(contrasena_actual) if contrasena_actual else ""
            )
            values[3] = contrasena_oculta
            self.tree.item(item_id, values=values)

    def construir_formulario_detalles(self):

        frame = tk.LabelFrame(
            self.master,
            text="Detalles del Dispositivo",
            padx=10,
            pady=10,
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        )
        frame.pack(padx=10, pady=5, fill="both", expand=True)

        row_idx = 0
        for label_text, var in self.fields.items():
            tk.Label(
                frame, text=label_text, bg="#404040", fg="white", font=self.font_normal
            ).grid(row=row_idx, column=0, sticky="w", pady=2)

            if label_text == "Contraseña":
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    width=35,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                    show="*",
                    state="disabled",
                )
                toggle_button = tk.Button(
                    frame,
                    text="Mostrar",
                    width=12,
                    command=lambda e=entry: self._toggle_password_visibility(e),
                    bg="#606060",
                    fg="white",
                    font=self.font_normal,
                    state="disabled",
                )
                toggle_button.grid(row=row_idx, column=2, padx=5)
                self.entry_widgets["__toggle_button"] = toggle_button
            else:
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    width=35,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                    state="disabled",
                )
            if label_text == "Periodicidad":
                options = ["Diaria", "Semanal", "Mensual", "Anual"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=var,
                    values=options,
                    state="disabled",
                    width=32,
                    font=self.font_normal,
                )
                entry.current(0)
                if var.get() == "":  # NUEVO
                    var.set(options[0])

            entry.grid(row=row_idx, column=1, sticky="w", pady=2)
            self.entry_widgets[label_text] = entry
            row_idx += 1
        """self.limpiar_btn = tk.Button(
            frame,
            text="Limpiar",
            width=12,
            command=self.limpiar_formulario,
            bg="#A9DCF0",
            fg="black",
            font=self.font_boton,
            state="disabled",  # Bloqueado por defecto
        )
        self.limpiar_btn.grid(row=row_idx, column=2, sticky="", pady=5, padx=5)"""

    def habilitar_campos(
        self,
    ):
        for entry in self.entry_widgets.values():
            if isinstance(entry, ttk.Combobox):
                entry.config(state="readonly")
            else:
                entry.config(state="normal")
        if "__toggle_button" in self.entry_widgets:
            self.entry_widgets["__toggle_button"].config(state="normal")
        if hasattr(self, "limpiar_btn"):
            self.limpiar_btn.config(state="normal")

    def bloquear_campos(
        self,
    ):
        for entry in self.entry_widgets.values():
            entry.config(state="disabled")
        if "__toggle_button" in self.entry_widgets:
            self.entry_widgets["__toggle_button"].config(state="disabled")
        if hasattr(self, "limpiar_btn"):
            self.limpiar_btn.config(state="disabled")

    def _toggle_password_visibility(self, entry):

        # POSIBLE MEJORA(reemplaza toda la implementación anterior)
        # if entry.cget("show") == "*":
        #     entry.config(show="")
        #     for widget in entry.master.winfo_children():
        #         if isinstance(widget, tk.Button) and widget.grid_info().get("row") == entry.grid_info().get("row") and widget.grid_info().get("column") == 2:
        #             widget.config(text="Ocultar")
        #             break
        # else:
        #     entry.config(show="*")
        #     for widget in entry.master.winfo_children():
        #         if isinstance(widget, tk.Button) and widget.grid_info().get("row") == entry.grid_info().get("row") and widget.grid_info().get("column") == 2:
        #             widget.config(text="Mostrar")
        #             break

        # Se supone que de la forma anterior es mejor, porque !button no siempre va a ser el botón que buscás.

        if entry.cget("show") == "*":
            entry.config(show="")
            entry.master.children["!button"].config(text="Ocultar")
        else:
            entry.config(show="*")
            entry.master.children["!button"].config(text="Mostrar")

    def construir_botones_inferiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        tk.Button(
            frame,
            text="Guardar",
            width=15,
            command=self.guardar_dispositivo,
            bg="#008000",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            frame,
            text="Cancelar",
            width=15,
            command=self.limpiar_formulario,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            frame,
            text="Probar Conexión SSH",
            width=20,
            font=self.font_boton,
            command=self.probar_conexion_ssh
        ).grid(row=0, column=2, padx=10)

    def limpiar_formulario(self):
        for var in self.fields.values():
            var.set("")
        self.fields["Hora"].set("HH:mm")
        self.fields["Periodicidad"].set("Diaria")  # NUEVO
        self.selected_id = None
        self.selected_device_name = None
        self.tree.selection_set(())
        if "Nombre" in self.entry_widgets:
            self.entry_widgets["Nombre"].focus_set()
            
        if "Contraseña" in self.entry_widgets:
            self.entry_widgets["Contraseña"].config(show="*")
            if "__toggle_button" in self.entry_widgets:
                self.entry_widgets["__toggle_button"].config(text="Mostrar")
        self.bloquear_campos()
        # POSIBLE MEJORA(se agrega, no reemplaza nada)
        # for label_text, entry_widget in self.entry_widgets.items():
        #     if label_text == "Contraseña":
        #         entry_widget.config(show="*")
        #         for widget in entry_widget.master.winfo_children():
        #             if isinstance(widget, tk.Button) and widget.grid_info().get("row") == entry_widget.grid_info().get("row") and widget.grid_info().get("column") == 2:
        #                 widget.config(text="Mostrar")
        #                 break

    def al_seleccionar_arbol(self, event):  # NUEVO
        selected_item = self.tree.focus()
        if selected_item:
            device_id = self.tree.item(selected_item, "tags")[0]
            self.selected_device_id = device_id

            device_values = self.tree.item(selected_item, 'values')
            self.selected_device_name = device_values[0] if device_values else "Dispositivo Desconocido"
            
            device_data = deviceController.get_device_by_id(device_id)
            if device_data:
                for key, var in self.fields.items():
                    var.set(device_data.get(key, ""))

            if "Contraseña" in self.entry_widgets:
                self.entry_widgets["Contraseña"].config(show="*")
                if "__toggle_button" in self.entry_widgets:
                    self.entry_widgets["__toggle_button"].config(text="Mostrar")
            self.bloquear_campos()
        else:
            self.limpiar_formulario()

    def validar_ip(self, ip):
        partes = ip.strip().split(".")
        if len(partes) != 4:
            return False
        try:
            return all(0 <= int(parte) <= 255 for parte in partes)
        except ValueError:
            return False

    def validar_hora(self, hora):
        try:
            datetime.datetime.strptime(hora.strip(), "%H:%M")
            return True
        except ValueError:
            return False

    def guardar_dispositivo(self):
        nuevo_dato = {key: var.get().strip() for key, var in self.fields.items()}
        obligatorios = [
            "Nombre",
            "IP",
            "Usuario",
            "Contraseña",
            "Puerto SSH",
            "Periodicidad",
        ]
        faltantes = [campo for campo in obligatorios if not nuevo_dato.get(campo)]
        if faltantes:
            mensaje = "Por favor completa los siguientes campos:\n- " + "\n- ".join(
                faltantes
            )
            messagebox.showerror("Campos obligatorios", mensaje)
            return

        if not self.validar_ip(nuevo_dato["IP"]):
            messagebox.showerror(
                "IP inválida", "La dirección IP no tiene un formato válido."
            )
            return

        if not self.validar_hora(nuevo_dato["Hora"]):
            messagebox.showerror(
                "Hora inválida", "La hora debe tener el formato HH:MM (24h)."
            )
            return

        if not nuevo_dato["Puerto SSH"].isdigit():
            messagebox.showerror("Puerto inválido", "El puerto SSH debe ser numérico.")
            return
        puerto = int(nuevo_dato["Puerto SSH"])
        if not (1 <= puerto <= 65535):
            messagebox.showerror(
                "Puerto inválido", "El puerto SSH debe estar entre 1 y 65535."
            )
            return

        if self.selected_device_id is not None:

            success = deviceController.update_device(
                self.selected_device_id, nuevo_dato
            )
            if success:
                messagebox.showinfo("Éxito", "Dispositivo actualizado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo actualizar el dispositivo.")
        else:
            success = deviceController.add_device(
                nuevo_dato["Nombre"],
                nuevo_dato["IP"],
                nuevo_dato["Puerto SSH"],
                nuevo_dato["Usuario"],
                nuevo_dato["Contraseña"],
                nuevo_dato["Periodicidad"],
                nuevo_dato["Hora"],
            )
            if success:
                messagebox.showinfo("Éxito", "Dispositivo guardado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo guardar el dispositivo.")

        self.actualizar_vista_arbol()
        self.limpiar_formulario()
        self.bloquear_campos()

    def editar_dispositivo(self):
        selected = self.tree.focus()
        if selected:
            self.al_seleccionar_arbol(None)
            self.habilitar_campos()  # Habilita los campos para edición
            messagebox.showinfo(
                "Edición",
                "Puedes modificar los campos y presionar Guardar para actualizar el dispositivo.",
            )
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para editar."
            )

    def eliminar_dispositivo(self):  # NUEVO
        selected = self.tree.focus()
        if selected:
            device_id = self.tree.item(selected, "tags")[0]
            confirm = messagebox.askyesno(
                "Confirmar", "¿Estás seguro de que deseas eliminar este dispositivo?"
            )
            if confirm:
                success = deviceController.delete_device(device_id)
                if success:
                    messagebox.showinfo(
                        "Eliminado", "Dispositivo eliminado correctamente."
                    )
                    self.actualizar_vista_arbol()
                    self.limpiar_formulario()
                    self.bloquear_campos()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el dispositivo.")
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para eliminar."
            )

    def actualizar_vista_arbol(self):  # NUEVO
        for item in self.tree.get_children():
            self.tree.delete(item)

        devices = deviceController.get_all_devices_data()

        for device in devices:
            contrasena_oculta = "*" * len(device["Contraseña"])
            self.tree.insert(
                "",
                "end",
                iid=device["ID"],
                tags=(device["ID"],),
                values=(
                    device["Nombre"],
                    device["IP"],
                    device["Usuario"],
                    contrasena_oculta,
                    device["Periodicidad"],
                ),
            )

    def probar_conexion_ssh(self):
        if self.selected_device_id is None:
            messagebox.showwarning("Probar Conexión", "Por favor, selecciona un dispositivo de la lista para probar la conexión SSH.")
            return

        device_data = deviceController.get_device_by_id(self.selected_device_id)

        if device_data:
            host = device_data["IP"]
            usuario = device_data["Usuario"]
            contrasena = device_data["Contraseña"]
            try:
                puerto = int(device_data["Puerto SSH"])
            except ValueError:
                messagebox.showerror("Error de Puerto", "El puerto SSH no es un número válido.")
                return

            success, message = conexion.verificar_conexion_ssh(host, usuario, contrasena, puerto)

            if success:
                messagebox.showinfo("Conexión SSH", f"Éxito: {message}")
            else:
                messagebox.showerror("Conexión SSH", f"Fallo: {message}")
        else:
            messagebox.showerror("Error", "No se pudieron obtener los detalles del dispositivo seleccionado.")


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()
