# 📘 Sale Service – Documentación

Microservicio encargado de gestionar **clientes, ventas y detalles de ventas**.  
Forma parte del ecosistema Abyssium compuesto por: `auth-service`, `company-service`, `inventory-service`, `product-service`, etc.

Este servicio **NO administra usuarios ni empresas**, pero **toma el `empresas_id_empresa` del usuario autenticado** usando la cookie del `auth-service`.

---

## 📂 Estructura del Proyecto

```
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
└── README.md
```

---

## 🧩 Dependencias Importantes

- **FastAPI**
- **SQLAlchemy Async**
- **Pydantic**
- **PostgreSQL**
- **Supabase** (solo para auth-service)
- **JWT + Cookie session** (auth-service)

---

## 🔐 Autenticación & Autorización

El acceso se controla mediante:

```python
current_user: CurrentUser = Depends(require_permission("acción", "recurso"))
```

### Acciones válidas

```
create, read, update, delete
```

### Recursos usados por este servicio

```
clientes
ventas
ventas_detalles
```

> El `auth-service` valida tokens, roles y permisos.

---

## 🧠 Conceptos Clave del Servicio

### ✔ Un cliente **siempre pertenece a la empresa del usuario**

No se envía `empresas_id_empresa` en el body.

### ✔ Una venta **siempre pertenece a la empresa y al usuario actual**

También guarda automáticamente:

- Usuario que realizó la venta
- Fecha
- Total

### ✔ El detalle de venta **no toca inventarios aquí**

El inventario se modifica en el `inventory-service`.

---

## 🗄 Modelos del Microservicio

### Cliente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_cliente` | PK | Identificador único |
| `nombre` | String | Nombre del cliente |
| `tipo` | String | Tipo de cliente |
| `telefono` | String | Teléfono de contacto |
| `email` | String | Correo electrónico |
| `notas` | String | Notas adicionales |
| `empresas_id_empresa` | FK | ID de la empresa |

### Venta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_venta` | PK | Identificador único |
| `descuento` | Decimal | Descuento aplicado |
| `razon_social` | String | Razón social |
| `nit` | String | NIT |
| `clientes_id_cliente` | FK | ID del cliente |
| `moneda_id_moneda` | FK | ID de la moneda |
| `usuarios_id_usuario` | FK | ID del usuario |
| `total` | Decimal | Total de la venta |
| `fecha_creacion` | DateTime | Fecha de creación |
| `empresas_id_empresa` | FK | ID de la empresa |

### Venta Detalle

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_venta_detalle` | PK | Identificador único |
| `venta_id_venta` | FK | ID de la venta |
| `productos_id_producto` | FK | ID del producto |
| `cantidad` | Integer | Cantidad |
| `precio_unitario` | Decimal | Precio unitario |
| `descuento_item` | Decimal | Descuento por ítem |

---

## 🛠 Endpoints

### 📌 Clientes

#### `POST /clientes`

Crear cliente

**Body:**

```json
{
  "nombre": "Cliente 1",
  "tipo": "natural",
  "telefono": "777888",
  "email": "test@example.com",
  "notas": "algo"
}
```

#### `GET /clientes`

Lista clientes de la empresa

#### `GET /clientes/{id}`

Obtiene un cliente por ID

#### `PATCH /clientes/{id}`

Actualiza un cliente

#### `DELETE /clientes/{id}`

Soft delete de un cliente

---

### 📌 Ventas

#### `POST /ventas`

Crea una venta y devuelve la venta con ID

**Body:**

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

#### `GET /ventas`

Lista ventas de la empresa

#### `GET /ventas/{id}`

Obtiene una venta por ID

#### `DELETE /ventas/{id}`

Elimina una venta (soft delete si deseas modificar)

---

### 📌 Venta Detalle

#### `POST /ventas/{venta_id}/detalle`

Crea un ítem de detalle

**Body:**

```json
{
  "productos_id_producto": 11,
  "cantidad": 2,
  "precio_unitario": 50,
  "descuento_item": 0
}
```

#### `GET /ventas/{venta_id}/detalle`

Lista los detalles de una venta

#### `DELETE /ventas/{venta_id}/detalle/{detalle_id}`

Elimina un detalle

---

## 🔄 Flujo típico

1. Usuario inicia sesión → cookie con JWT → `auth-service`
2. `sale-service` recibe cookie y `deps.py` obtiene:
   - `id_usuario`
   - `id_empresa`
   - `roles`
   - `permisos`
3. Usuario crea cliente
4. Usuario crea venta
5. Usuario crea detalles de venta
6. (Opcional) Un servicio externo descuenta inventario
7. Reportes se generan externamente (Power BI o microservicio de reportes)

---

## 📦 Instalación y Ejecución

### 1. Crear entorno virtual

**Linux/Mac:**

```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Definir archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET=...
COOKIE_NAME=session
```

### 4. Ejecutar servidor

```bash
uvicorn app.main:app --reload
```

---

## 🔍 Notas Técnicas Importantes

- **NO declares ForeignKey hacia empresas, productos, moneda, clientes, usuarios**, salvo ventas → venta_detalle.
  Estos modelos no existen en este microservicio.
- La BD sí tiene FKs reales, pero los modelos NO deben mapearlos.
- Las validaciones que cruzan servicios se hacen mediante llamadas API o simplemente confiando en IDs.

---

## 🧪 Colección Postman

Se genera aparte, pero se incluye en:

```
sale-service/postman/sale-service-collection.json
```

---

## 📝 Licencia

Este proyecto forma parte del ecosistema Abyssium.
