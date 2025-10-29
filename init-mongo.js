// Conectarse a la base de datos 'LPFM'
db = db.getSiblingDB('LPFM');

// Limpiar colecciones anteriores (opcional, pero bueno para pruebas)
db.usuarios.deleteMany({});
db.productos.deleteMany({});
db.pedidos.deleteMany({});

// --- 1. Crear Colección 'usuarios' e insertar un dato ---
db.createCollection('usuarios');
let usuarioResult = db.usuarios.insertOne(
  { 
    "nombre_completo": "Gerson Jared Villagrana Ponce",
    "email": "gerson@example.com",
    "password_hash": "hash_encriptado_aqui",
    "direcciones": [
      {
        "alias": "Casa",
        "calle": "Av. Siempre Viva 123",
        "colonia": "Centro",
        "cp": "45000",
        "ciudad": "Zapopan"
      }
    ],
    "fecha_registro": new Date() // Usamos new Date()
  }
);

// Guardamos el ID real que MongoDB acaba de crear
let miUsuarioId = usuarioResult.insertedId;


// --- 2. Crear Colección 'productos' e insertar un dato ---
db.createCollection('productos');
let productoResult = db.productos.insertOne(
  {
    // No ponemos _id, Mongo lo genera solo
    "nombre": "Laptop Gamer XYZ",
    "descripcion": "Laptop con 16GB RAM, SSD 1TB, Tarjeta Gráfica RTX 9000",
    "precio": 35000.50,
    "stock": 25,
    "categoria": "Electrónica",
    "sku": "LAP-XYZ-9000",
    "url_imagen": "https://example.com/images/laptop.jpg",
    "especificaciones": {
      "marca": "XYZ",
      "peso_kg": 2.1,
      "pantalla": "15.6 pulgadas"
    },
    "publicado": true
  }
);

// Guardamos el ID real que MongoDB acaba de crear
let miProductoId = productoResult.insertedId;


// --- 3. Crear Colección 'pedidos' e insertar un dato ---
db.createCollection('pedidos');
db.pedidos.insertOne(
  {
    // No ponemos _id, Mongo lo genera solo
    "usuario_id": miUsuarioId,       // <-- Usamos la variable del usuario real
    "fecha_creacion": new Date(),    // <-- Usamos new Date()
    "estado": "pendiente_pago", 
    "items": [
      {
        "producto_id": miProductoId, // <-- Usamos la variable del producto real
        "nombre_producto": "Laptop Gamer XYZ", 
        "cantidad": 1,
        "precio_compra": 35000.50
      }
    ],
    "direccion_envio": { 
      "calle": "Av. Siempre Viva 123",
      "colonia": "Centro",
      "cp": "45000",
      "ciudad": "Zapopan"
    },
    "subtotal": 35000.50,
    "envio": 150.00,
    "total": 35150.50,
    "id_pago_paypal": "PAYPAL_ID_PENDIENTE_..." 
  }
);