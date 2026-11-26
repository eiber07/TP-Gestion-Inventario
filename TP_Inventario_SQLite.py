import sqlite3

# Conectamos el programa con la base de datos.
# Si el archivo no existe, SQLite lo crea.
conexion = sqlite3.connect("inventario.db")
cursor = conexion.cursor()

def crear_tabla():
    """Crea la tabla de productos si todavía no existe."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL CHECK(cantidad >= 0),
            precio REAL NOT NULL CHECK(precio >= 0),
            categoria TEXT
        )
    """)
    conexion.commit()

def pedir_nombre():
    """Solicita un nombre y no permite que quede vacío."""
    nombre = input("Nombre: ").strip()
    while nombre == "":
        nombre = input("El nombre no puede estar vacío. Ingresalo nuevamente: ").strip()
    return nombre

def pedir_entero(mensaje, minimo):
    """Pide un número entero que sea igual o mayor que el mínimo."""
    numero = input(mensaje).strip()
    while not numero.isdigit() or int(numero) < minimo:
        numero = input(f"Ingresá un número entero mayor o igual a {minimo}: ").strip()
    return int(numero)

def pedir_precio():
    """Solicita y valida un precio que puede tener centavos."""
    while True:
        texto = input("Precio: ").strip().replace(",", ".")
        try:
            precio = float(texto)
            if 0 <= precio < float("inf"):
                return precio
        except ValueError:
            pass
        print("Ingresá un precio válido, igual o mayor que cero.")

def mostrar_producto(producto):
    """Muestra los seis datos de un producto."""
    print(f"ID: {producto[0]} | Nombre: {producto[1]} | Categoría: {producto[5]} | Descripción: {producto[2]} | Cantidad: {producto[3]} | Precio: ${producto[4]:.2f}")

def buscar_por_id(id_producto):
    """Busca en la base un producto por su identificador."""
    cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
    return cursor.fetchone()

def agregar_producto():
    """Pide los datos y registra un producto nuevo."""
    nombre = pedir_nombre()
    descripcion = input("Descripción (opcional): ").strip()
    cantidad = pedir_entero("Cantidad: ", 0)
    precio = pedir_precio()
    categoria = input("Categoría (opcional): ").strip()

    # Los signos ? representan los valores que ingresa el usuario.
    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, descripcion, cantidad, precio, categoria))
    conexion.commit()
    print(f"Producto agregado correctamente. Su ID es {cursor.lastrowid}.")

def mostrar_productos():
    """Muestra todos los productos registrados."""
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()

    if len(productos) == 0:
        print("No hay productos registrados.")
    else:
        for producto in productos:
            mostrar_producto(producto)
            print("------------------------------")

def actualizar_producto():
    """Reemplaza los datos de un producto identificado por su ID."""
    id_producto = pedir_entero("ID a actualizar: ", 1)
    producto = buscar_por_id(id_producto)

    if producto is None:
        print("No existe un producto con ese ID.")
        return

    print("Datos actuales:")
    mostrar_producto(producto)
    print("Ingresá nuevamente los datos del producto:")

    nombre = pedir_nombre()
    descripcion = input("Descripción (opcional): ").strip()
    cantidad = pedir_entero("Cantidad: ", 0)
    precio = pedir_precio()
    categoria = input("Categoría (opcional): ").strip()

    cursor.execute("""
        UPDATE productos
        SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
        WHERE id = ?
    """, (nombre, descripcion, cantidad, precio, categoria, id_producto))
    conexion.commit()
    print("Producto actualizado correctamente.")

def eliminar_producto():
    """Elimina un producto por ID después de pedir confirmación."""
    id_producto = pedir_entero("ID a eliminar: ", 1)
    producto = buscar_por_id(id_producto)

    if producto is None:
        print("No existe un producto con ese ID.")
        return

    mostrar_producto(producto)
    confirmar = input("¿Confirmás la eliminación? (s/n): ").strip().lower()
    while confirmar != "s" and confirmar != "n":
        confirmar = input("Ingresá s para confirmar o n para cancelar: ").strip().lower()

    if confirmar == "s":
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        print(f"Producto '{producto[1]}' eliminado correctamente.")
    else:
        print("Eliminación cancelada.")

def buscar_producto():
    """Permite consultar los datos completos de un producto por ID."""
    id_producto = pedir_entero("ID a buscar: ", 1)
    producto = buscar_por_id(id_producto)

    if producto is None:
        print("No se encontró un producto con ese ID.")
    else:
        mostrar_producto(producto)

def reporte_stock():
    """Muestra los productos con cantidad menor o igual al límite ingresado."""
    limite = pedir_entero("Mostrar productos con cantidad igual o inferior a: ", 0)
    cursor.execute("""
        SELECT * FROM productos WHERE cantidad <= ? ORDER BY cantidad, id
    """, (limite,))
    productos = cursor.fetchall()

    if len(productos) == 0:
        print("No hay productos con esa cantidad o menos.")
    else:
        print("Productos con stock bajo:")
        for producto in productos:
            mostrar_producto(producto)
            print("------------------------------")

def menu():
    """Muestra el menú hasta que el usuario elija salir."""
    opcion = ""
    while opcion != "7":
        print("\nSISTEMA DE GESTIÓN DE INVENTARIO")
        print("1. Agregar | 2. Mostrar | 3. Actualizar | 4. Eliminar | 5. Buscar | 6. Reporte | 7. Salir")
        opcion = input("Elegí una opción: ").strip()

        try:
            if opcion == "1":
                agregar_producto()
            elif opcion == "2":
                mostrar_productos()
            elif opcion == "3":
                actualizar_producto()
            elif opcion == "4":
                eliminar_producto()
            elif opcion == "5":
                buscar_producto()
            elif opcion == "6":
                reporte_stock()
            elif opcion == "7":
                print("¡Nos vemos, gracias!")
            else:
                print("Opción inválida. Elegí un número del 1 al 7.")
        except sqlite3.Error as error:
            # Si ocurre un error con SQLite, se deshace la operación pendiente.
            conexion.rollback()
            print(f"Error en la base de datos: {error}")

# Al terminar, cerramos la conexión con la base de datos.
try:
    crear_tabla()
    menu()
finally:
    conexion.close()
