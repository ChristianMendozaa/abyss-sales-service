# 📘 Sale Service – Documentación

Microservicio encargado de gestionar **clientes, ventas y detalles de ventas**.  
Forma parte del ecosistema Abyssium compuesto por: `auth-service`, `company-service`, `inventory-service`, `product-service`, etc.

Este servicio **NO administra usuarios ni empresas**, pero **toma el `empresas_id_empresa` del usuario autenticado** usando la cookie del `auth-service`.


# 📂 Estructura del Proyecto


sale-service/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── deps.py              ← obtiene usuario actual desde auth-service
│   ├── supabase_service.py  ← helper para supabase admin (no siempre requerido)
│   │
│   ├── models/
│   │   ├── cliente.py
│   │   ├── venta.py
│   │   └── venta_detalle.py
│   │
│   ├── schemas/
│   │   ├── cliente.py
│   │   ├── venta.py
│   │   └── venta_detalle.py
│   │
│   └── routers/
│       ├── clientes.py
│       └── ventas.py
│
├── requirements.txt
└── README.md  (este documento)

---

# 🧩 Dependencias Importantes

- **FastAPI**
- **SQLAlchemy Async**
- **Pydantic**
- **PostgreSQL**
- **Supabase (solo para auth-service)**
- **JWT + Cookie session** (auth-service)

---

# 🔐 Autenticación & Autorización

El acceso se controla mediante:

```
current_user: CurrentUser = Depends(require_permission("acción", "recurso"))
```

Las acciones válidas son:

```
create, read, update, delete
```

Recursos usados por este servicio:

```
clientes
ventas
ventas_detalles
```

El `auth-service` valida tokens, roles y permisos.

---

# 🧠 Conceptos Clave del Servicio

### ✔ Un cliente **siempre pertenece a la empresa del usuario**

No se envía `empresas_id_empresa` en el body.

### ✔ Una venta **siempre pertenece a la empresa y al usuario actual**

También guarda automáticamente:

* usuario que realizó la venta
* fecha
* total

### ✔ El detalle de venta **no toca inventarios aquí**

El inventario se modifica en el `inventory-service`.

---

# 🗄 Modelos del Microservicio

## Cliente

```
id_cliente (PK)
nombre
tipo
telefono
email
notas
empresas_id_empresa
```

## Venta

```
id_venta (PK)
descuento
razon_social
nit
clientes_id_cliente
moneda_id_moneda
usuarios_id_usuario
total
fecha_creacion
empresas_id_empresa
```

## Venta Detalle

```
id_venta_detalle (PK)
venta_id_venta (FK → venta)
productos_id_producto
cantidad
precio_unitario
descuento_item
```

---

# 🛠 Endpoints

## 📌 Clientes

### **POST /clientes**

Crear cliente

Body:

```json
{
  "nombre": "Cliente 1",
  "tipo": "natural",
  "telefono": "777888",
  "email": "test@example.com",
  "notas": "algo"
}
```

### **GET /clientes**

Lista clientes de la empresa

### **GET /clientes/{id}**

Obtiene un cliente

### **PATCH /clientes/{id}**

Actualiza cliente

### **DELETE /clientes/{id}**

Soft delete

---

## 📌 Ventas

### **POST /ventas**

Crea una venta y devuelve la venta con ID

Body:

```json
{
  "descuento": 0,
  "razon_social": "Juan Perez",
  "nit": "123456",
  "clientes_id_cliente": 1,
  "moneda_id_moneda": 1,
  "total": 120
}
```

### **GET /ventas**

Lista ventas de la empresa

### **GET /ventas/{id}**

Obtiene venta

### **DELETE /ventas/{id}**

Elimina venta (soft delete si deseas modificar)

---

## 📌 Venta Detalle

### **POST /ventas/{venta_id}/detalle**

Crea un ítem de detalle

Body:

```json
{
  "productos_id_producto": 11,
  "cantidad": 2,
  "precio_unitario": 50,
  "descuento_item": 0
}
```

### **GET /ventas/{venta_id}/detalle**

Lista los detalles de una venta

### **DELETE /ventas/{venta_id}/detalle/{detalle_id}**

Elimina un detalle

---

# 🔄 Flujo típico

1. Usuario inicia sesión → cookie con JWT → `auth-service`.
2. `sale-service` recibe cookie y `deps.py` obtiene:

   * id_usuario
   * id_empresa
   * roles
   * permisos
3. Usuario crea cliente.
4. Usuario crea venta.
5. Usuario crea detalles de venta.
6. (Opcional) Un servicio externo descuenta inventario.
7. Reportes se generan externamente (Power BI o microservicio de reportes).

---

# 📦 Instalación y Ejecución

### 1. Crear entorno virtual

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Instalar dependencias

```
pip install -r requirements.txt
```

### 3. Definir archivo `.env`

```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET=...
COOKIE_NAME=session
```

### 4. Ejecutar servidor

```
uvicorn app.main:app --reload
```

---

# 🔍 Notas Técnicas Importantes

* **NO declares ForeignKey hacia empresas, productos, moneda, clientes, usuarios**, salvo ventas → venta_detalle.
  Estos modelos no existen en este microservicio.
* La BD sí tiene FKs reales, pero los modelos NO deben mapearlos.
* Las validaciones que cruzan servicios se hacen mediante llamadas API o simplemente confiando en IDs.

---

# 🧪 Colección Postman

Se genera aparte, pero se incluye en:

```
sale-service/postman/sale-service-collection.json
```