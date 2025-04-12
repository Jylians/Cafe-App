import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from enum import Enum

class Persona:
    def __init__(self, nombre):
        self.nombre = nombre

class Cliente(Persona):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.historial_pedidos = []
    
    def realizar_pedido(self, pedido, inventario):
        resultado = f"Pedido realizado por {self.nombre}: Pedido con {len(pedido.productos)} productos, Estado: {pedido.estado}\n"
        if pedido.validar_pedido(inventario):
            self.historial_pedidos.append(pedido)
            pedido.procesar_pedido(inventario)
            resultado += f"Pedido realizado con éxito. Total: ${pedido.calcular_total()}\n"
            resultado += f"Estado del pedido cambiado a: {pedido.estado}"
            return True, resultado
        else:
            resultado += "No hay suficiente stock para procesar el pedido."
            return False, resultado

class RolEmpleado(Enum):
    MESERO = "Mesero"
    BARISTA = "Barista"
    GERENTE = "Gerente"

class Empleado(Persona):
    def __init__(self, nombre, rol):
        super().__init__(nombre)
        self.rol = rol

class ProductoBase:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

class Bebida(ProductoBase):
    def __init__(self, nombre, precio, tamaño, tipo, opciones_personalizadas):
        super().__init__(nombre, precio)
        self.tamaño = tamaño
        self.tipo = tipo
        self.opciones_personalizadas = opciones_personalizadas

class Postre(ProductoBase):
    def __init__(self, nombre, precio, vegano, sin_gluten):
        super().__init__(nombre, precio)
        self.vegano = vegano
        self.sin_gluten = sin_gluten

class Inventario:
    def __init__(self):
        self.ingredientes = {}
    
    def actualizar_stock(self, ingrediente, cantidad):
        self.ingredientes[ingrediente] = self.ingredientes.get(ingrediente, 0) + cantidad
        return f"Inventario actualizado: {ingrediente} - {self.ingredientes[ingrediente]} unidades disponibles"
    
    def verificar_disponibilidad(self, ingredientes_requeridos):
        return all(self.ingredientes.get(ing, 0) >= cant for ing, cant in ingredientes_requeridos.items())
    
    def descontar_ingredientes(self, ingredientes_requeridos):
        for ing, cant in ingredientes_requeridos.items():
            self.ingredientes[ing] -= cant

class Pedido:
    def __init__(self, productos):
        self.productos = productos
        self.estado = "Pendiente"
    
    def calcular_total(self):
        return sum(producto.precio for producto in self.productos)
    
    def validar_pedido(self, inventario):
        ingredientes_necesarios = {}
        for producto in self.productos:
            if isinstance(producto, Bebida):
                for opcion in producto.opciones_personalizadas:
                    ingredientes_necesarios[opcion] = ingredientes_necesarios.get(opcion, 0) + 1
        return inventario.verificar_disponibilidad(ingredientes_necesarios)
    
    def procesar_pedido(self, inventario):
        ingredientes_necesarios = {}
        for producto in self.productos:
            if isinstance(producto, Bebida):
                for opcion in producto.opciones_personalizadas:
                    ingredientes_necesarios[opcion] = ingredientes_necesarios.get(opcion, 0) + 1
        inventario.descontar_ingredientes(ingredientes_necesarios)
        self.estado = "En preparación"

class Promocion:
    def __init__(self, codigo, descuento, clientes_frecuentes):
        self.codigo = codigo
        self.descuento = descuento
        self.clientes_frecuentes = clientes_frecuentes
    
    def aplicar_descuento(self, cliente, total):
        if cliente in self.clientes_frecuentes:
            return total * (1 - self.descuento / 100)
        return total

class CoffeeShopGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Cafetería")
        self.root.geometry("1000x700")
        
        # Datos iniciales
        self.inventario = Inventario()
        self.clientes = []
        self.empleados = []
        self.productos = []
        self.promociones = []
        self.carrito = []
        self.cliente_actual = None
        
        self.inicializar_datos()
        
        # Crear pestañas
        self.notebook = ttk.Notebook(root)
        
        # Pestañas
        self.crear_tab_clientes()
        self.crear_tab_productos()
        self.crear_tab_inventario()
        self.crear_tab_empleados()
        self.crear_tab_promociones()
        
        self.notebook.pack(expand=True, fill='both')
        
        # Consola de salida
        self.console_frame = ttk.LabelFrame(root, text="Consola")
        self.console_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.console = tk.Text(self.console_frame, height=10)
        self.console.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=5)
    
    def log(self, mensaje):
        self.console.insert(tk.END, mensaje + "\n")
        self.console.see(tk.END)
    
    def inicializar_datos(self):
        # Inventario inicial
        ingredientes_iniciales = [
            ("leche de almendra", 10),
            ("azúcar", 20),
            ("chocolate", 15),
            ("leche", 30),
            ("café", 50)
        ]
        for ing, cant in ingredientes_iniciales:
            self.inventario.actualizar_stock(ing, cant)
        
        # Productos iniciales
        self.productos = [
            Bebida("Café Americano", 30, "Mediano", "Caliente", ["café"]),
            Bebida("Café Latte", 50, "Grande", "Caliente", ["café", "leche"]),
            Bebida("Café con Leche de Almendra", 60, "Grande", "Caliente", ["café", "leche de almendra"]),
            Postre("Brownie", 40, False, False),
            Postre("Muffin de Arándanos", 35, True, True)
        ]
        
        # Cliente de ejemplo
        cliente1 = Cliente("Juan Pérez")
        self.clientes.append(cliente1)
        
        # Empleado de ejemplo
        empleado1 = Empleado("María Rodríguez", RolEmpleado.BARISTA)
        self.empleados.append(empleado1)
        
        # Promoción de ejemplo
        promocion1 = Promocion("FIDELIDAD20", 20, [cliente1])
        self.promociones.append(promocion1)
    
    def crear_tab_clientes(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Clientes")
        
        # Lista de clientes
        frame_lista = ttk.LabelFrame(tab, text="Clientes Registrados")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.clientes_listbox = tk.Listbox(frame_lista)
        self.clientes_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.actualizar_lista_clientes()
        
        # Botones
        frame_botones = ttk.Frame(tab)
        frame_botones.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(frame_botones, text="Agregar Cliente", 
                  command=self.agregar_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Seleccionar Cliente", 
                  command=self.seleccionar_cliente).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Ver Historial", 
                  command=self.ver_historial_cliente).pack(side='left', padx=5)
    
    def crear_tab_productos(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Pedidos")
        
        # Frame superior - Productos disponibles
        frame_productos = ttk.LabelFrame(tab, text="Productos Disponibles")
        frame_productos.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.productos_listbox = tk.Listbox(frame_productos)
        self.productos_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.actualizar_lista_productos()
        
        # Frame inferior - Carrito
        frame_carrito = ttk.LabelFrame(tab, text="Carrito de Compras")
        frame_carrito.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Cliente seleccionado
        self.cliente_label = ttk.Label(frame_carrito, text="Cliente: Ninguno seleccionado")
        self.cliente_label.pack(anchor='w', padx=5, pady=5)
        
        # Lista del carrito
        self.carrito_listbox = tk.Listbox(frame_carrito)
        self.carrito_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Total
        self.total_label = ttk.Label(frame_carrito, text="Total: $0")
        self.total_label.pack(anchor='w', padx=5, pady=5)
        
        # Botones
        frame_botones = ttk.Frame(frame_carrito)
        frame_botones.pack(fill='x', pady=5)
        
        ttk.Button(frame_botones, text="Agregar al Carrito", 
                  command=self.agregar_al_carrito).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Quitar del Carrito", 
                  command=self.quitar_del_carrito).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Procesar Pedido", 
                  command=self.procesar_pedido).pack(side='left', padx=5)
        ttk.Button(frame_botones, text="Aplicar Promoción", 
                  command=self.aplicar_promocion).pack(side='left', padx=5)
    
    def crear_tab_inventario(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventario")
        
        # Lista de inventario
        frame_lista = ttk.LabelFrame(tab, text="Ingredientes en Stock")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.inventario_listbox = tk.Listbox(frame_lista)
        self.inventario_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.actualizar_lista_inventario()
        
        # Formulario para actualizar
        frame_form = ttk.LabelFrame(tab, text="Actualizar Inventario")
        frame_form.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_form, text="Ingrediente:").grid(row=0, column=0, padx=5, pady=5)
        self.ingrediente_entry = ttk.Entry(frame_form)
        self.ingrediente_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.cantidad_entry = ttk.Entry(frame_form)
        self.cantidad_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(frame_form, text="Agregar/Actualizar", 
                  command=self.actualizar_inventario).grid(row=2, column=0, columnspan=2, pady=5)
    
    def crear_tab_empleados(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Empleados")
        
        # Lista de empleados
        frame_lista = ttk.LabelFrame(tab, text="Empleados Registrados")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.empleados_listbox = tk.Listbox(frame_lista)
        self.empleados_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.actualizar_lista_empleados()
        
        # Formulario para agregar
        frame_form = ttk.LabelFrame(tab, text="Agregar Empleado")
        frame_form.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.empleado_nombre_entry = ttk.Entry(frame_form)
        self.empleado_nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Rol:").grid(row=1, column=0, padx=5, pady=5)
        self.empleado_rol_combobox = ttk.Combobox(frame_form, 
                                                values=[rol.value for rol in RolEmpleado])
        self.empleado_rol_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.empleado_rol_combobox.current(0)
        
        ttk.Button(frame_form, text="Agregar Empleado", 
                  command=self.agregar_empleado).grid(row=2, column=0, columnspan=2, pady=5)
    
    def crear_tab_promociones(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Promociones")
        
        # Lista de promociones
        frame_lista = ttk.LabelFrame(tab, text="Promociones Disponibles")
        frame_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.promociones_listbox = tk.Listbox(frame_lista)
        self.promociones_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.actualizar_lista_promociones()
        
        # Formulario para agregar
        frame_form = ttk.LabelFrame(tab, text="Crear Promoción")
        frame_form.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_form, text="Código:").grid(row=0, column=0, padx=5, pady=5)
        self.promo_codigo_entry = ttk.Entry(frame_form)
        self.promo_codigo_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_form, text="Descuento (%):").grid(row=1, column=0, padx=5, pady=5)
        self.promo_descuento_entry = ttk.Entry(frame_form)
        self.promo_descuento_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(frame_form, text="Agregar Promoción", 
                  command=self.agregar_promocion).grid(row=2, column=0, columnspan=2, pady=5)
    
    # Métodos para actualizar listas
    def actualizar_lista_clientes(self):
        self.clientes_listbox.delete(0, tk.END)
        for cliente in self.clientes:
            self.clientes_listbox.insert(tk.END, cliente.nombre)
    
    def actualizar_lista_productos(self):
        self.productos_listbox.delete(0, tk.END)
        for producto in self.productos:
            if isinstance(producto, Bebida):
                desc = f"{producto.nombre} - ${producto.precio} ({producto.tamaño}, {producto.tipo})"
            else:
                desc = f"{producto.nombre} - ${producto.precio}"
            self.productos_listbox.insert(tk.END, desc)
    
    def actualizar_lista_inventario(self):
        self.inventario_listbox.delete(0, tk.END)
        for ingrediente, cantidad in self.inventario.ingredientes.items():
            self.inventario_listbox.insert(tk.END, f"{ingrediente}: {cantidad} unidades")
    
    def actualizar_lista_empleados(self):
        self.empleados_listbox.delete(0, tk.END)
        for empleado in self.empleados:
            self.empleados_listbox.insert(tk.END, f"{empleado.nombre} - {empleado.rol.value}")
    
    def actualizar_lista_promociones(self):
        self.promociones_listbox.delete(0, tk.END)
        for promocion in self.promociones:
            clientes = ", ".join([c.nombre for c in promocion.clientes_frecuentes])
            self.promociones_listbox.insert(tk.END, 
                                          f"{promocion.codigo}: {promocion.descuento}% - Clientes: {clientes}")
    
    def actualizar_carrito(self):
        self.carrito_listbox.delete(0, tk.END)
        for producto in self.carrito:
            self.carrito_listbox.insert(tk.END, f"{producto.nombre} - ${producto.precio}")
        
        total = sum(producto.precio for producto in self.carrito)
        self.total_label.config(text=f"Total: ${total}")
    
    # Métodos de funcionalidad
    def agregar_cliente(self):
        nombre = simpledialog.askstring("Nuevo Cliente", "Ingrese el nombre del cliente:")
        if nombre:
            nuevo_cliente = Cliente(nombre)
            self.clientes.append(nuevo_cliente)
            self.actualizar_lista_clientes()
            self.log(f"Cliente agregado: {nombre}")
    
    def seleccionar_cliente(self):
        seleccion = self.clientes_listbox.curselection()
        if seleccion:
            self.cliente_actual = self.clientes[seleccion[0]]
            self.cliente_label.config(text=f"Cliente: {self.cliente_actual.nombre}")
            self.log(f"Cliente seleccionado: {self.cliente_actual.nombre}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un cliente de la lista")
    
    def ver_historial_cliente(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
        
        historial = f"\nHistorial de pedidos de {self.cliente_actual.nombre}:\n"
        if not self.cliente_actual.historial_pedidos:
            historial += "No hay pedidos registrados"
        else:
            for i, pedido in enumerate(self.cliente_actual.historial_pedidos):
                historial += f"Pedido {i+1}: ${pedido.calcular_total()} - Estado: {pedido.estado}\n"
                for producto in pedido.productos:
                    historial += f"  - {producto.nombre}\n"
        
        self.log(historial)
    
    def agregar_al_carrito(self):
        seleccion = self.productos_listbox.curselection()
        if seleccion:
            producto = self.productos[seleccion[0]]
            self.carrito.append(producto)
            self.actualizar_carrito()
            self.log(f"Producto agregado al carrito: {producto.nombre}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la lista")
    
    def quitar_del_carrito(self):
        seleccion = self.carrito_listbox.curselection()
        if seleccion:
            producto = self.carrito.pop(seleccion[0])
            self.actualizar_carrito()
            self.log(f"Producto removido del carrito: {producto.nombre}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
    
    def procesar_pedido(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
        
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        pedido = Pedido(self.carrito.copy())
        exito, mensaje = self.cliente_actual.realizar_pedido(pedido, self.inventario)
        
        self.log(mensaje)
        
        if exito:
            self.carrito = []
            self.actualizar_carrito()
            self.actualizar_lista_inventario()
    
    def aplicar_promocion(self):
        if not self.cliente_actual:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
        
        if not self.carrito:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return
        
        codigo = simpledialog.askstring("Promoción", "Ingrese el código de promoción:")
        if codigo:
            for promocion in self.promociones:
                if promocion.codigo == codigo:
                    total = sum(p.precio for p in self.carrito)
                    total_con_descuento = promocion.aplicar_descuento(self.cliente_actual, total)
                    
                    if total_con_descuento < total:
                        self.log(f"Promoción aplicada: {codigo}")
                        self.log(f"Total original: ${total}")
                        self.log(f"Total con descuento: ${total_con_descuento}")
                        self.total_label.config(text=f"Total: ${total_con_descuento} (con {promocion.descuento}% de descuento)")
                    else:
                        self.log("El cliente no es elegible para esta promoción")
                    return
            
            self.log(f"Código de promoción no válido: {codigo}")
    
    def actualizar_inventario(self):
        ingrediente = self.ingrediente_entry.get()
        cantidad = self.cantidad_entry.get()
        
        if not ingrediente or not cantidad:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return
        
        try:
            cantidad = int(cantidad)
            mensaje = self.inventario.actualizar_stock(ingrediente, cantidad)
            self.log(mensaje)
            self.actualizar_lista_inventario()
            self.ingrediente_entry.delete(0, tk.END)
            self.cantidad_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
    
    def agregar_empleado(self):
        nombre = self.empleado_nombre_entry.get()
        rol_str = self.empleado_rol_combobox.get()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "Ingrese un nombre")
            return
        
        rol = None
        for r in RolEmpleado:
            if r.value == rol_str:
                rol = r
                break
        
        if rol:
            nuevo_empleado = Empleado(nombre, rol)
            self.empleados.append(nuevo_empleado)
            self.actualizar_lista_empleados()
            self.log(f"Empleado agregado: {nombre} como {rol.value}")
            self.empleado_nombre_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Rol no válido")
    
    def agregar_promocion(self):
        codigo = self.promo_codigo_entry.get()
        descuento_str = self.promo_descuento_entry.get()
        
        if not codigo or not descuento_str:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return
        
        try:
            descuento = int(descuento_str)
            if descuento <= 0 or descuento > 100:
                raise ValueError
            
            nueva_promocion = Promocion(codigo, descuento, [])
            self.promociones.append(nueva_promocion)
            self.actualizar_lista_promociones()
            self.log(f"Promoción agregada: {codigo} con {descuento}% de descuento")
            self.promo_codigo_entry.delete(0, tk.END)
            self.promo_descuento_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "El descuento debe ser un número entre 1 y 100")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeShopGUI(root)
    root.mainloop()