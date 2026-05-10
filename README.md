# Smart Store Backend

E-commerce backend with Admin Product Management, Cart, Checkout, Coupons, Order History, Trending, and C++ Trie-based Search.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [C++ Trie Search Engine](#c-trie-search-engine)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [Development Notes](#development-notes)

---

## Architecture Overview

```
Client (Postman / Frontend)
        │
        ▼
   FastAPI Server (main.py)
        │
        ├── API Routes (/api/v1/...)
        │       │
        │       ▼
        │   Services (business logic)
        │       │
        │       ├── SQLAlchemy ORM ──► PostgreSQL (source of truth)
        │       │
        │       └── C++ Trie ──► In-memory search index (pybind11)
        │
        └── JWT Auth (passlib + python-jose)
```

**Key design decisions:**
- **PostgreSQL is the single source of truth.** All data lives in Postgres.
- **C++ Trie is a read-optimized index.** It mirrors product names from the DB for microsecond-level autocomplete and exact search. It is loaded from the DB on server startup and kept in sync when products are created, updated, or deleted.
- **Services layer separates business logic from routes.** Routes are thin — they validate input, call a service function, and return a response.

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | FastAPI | Async Python web framework with auto-generated OpenAPI docs |
| **Database** | PostgreSQL | Relational database (source of truth) |
| **ORM** | SQLAlchemy 2.x | Database access via Python objects |
| **Auth** | python-jose + passlib[bcrypt] | JWT token generation + password hashing |
| **Validation** | Pydantic v2 | Request/response schema validation |
| **Search Engine** | C++ Trie (pybind11) | In-memory autocomplete and exact search |
| **DB Driver** | psycopg2-binary | PostgreSQL adapter for Python |
| **Package Manager** | uv | Fast Python package manager |

---

## Project Structure

```
Book-Store/
├── main.py                          # FastAPI app entry point
├── pyproject.toml                   # Dependencies and project metadata
├── .gitignore
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/                         # API layer (routes + dependencies)
│   │   ├── router.py                # Central router — gathers all route modules
│   │   ├── deps.py                  # FastAPI dependencies (auth, admin checks)
│   │   ├── routes/
│   │   │   ├── admin.py             # Admin-only product CRUD
│   │   │   ├── cart.py              # Cart management (add, update, remove items)
│   │   │   ├── checkout.py          # Checkout flow (cart → order)
│   │   │   ├── products.py          # Public product listing
│   │   │   ├── search.py            # Autocomplete + exact search
│   │   │   └── trending.py          # Top purchased products
│   │   └── v1/
│   │       └── auth.py              # Register, login, /me
│   │
│   ├── core/                        # App configuration and security
│   │   ├── config.py                # Environment variables (DB URL, JWT secret)
│   │   └── security.py              # JWT creation, password hash/verify
│   │
│   ├── cpp_bridge/                  # C++ Trie integration
│   │   ├── __init__.py
│   │   ├── c.cpp                    # Original Trie implementation (reference)
│   │   ├── trie_wrapper.cpp         # Trie + pybind11 bindings (compiled to .so)
│   │   └── trie_module.*.so         # Compiled shared library (gitignored)
│   │
│   ├── db/                          # Database configuration
│   │   └── session.py               # SQLAlchemy engine + SessionLocal + get_db
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── base.py                  # declarative_base()
│   │   ├── user.py                  # User + UserRole enum
│   │   ├── product.py               # Product (name, price, stock, category)
│   │   ├── cart.py                  # Cart (one per user)
│   │   ├── cart_item.py             # CartItem (product + quantity in a cart)
│   │   ├── order.py                 # Order + OrderStatus enum
│   │   ├── order_item.py            # OrderItem (snapshot of product at purchase time)
│   │   ├── coupon.py                # Coupon + DiscountType enum (percent/flat)
│   │   └── trending.py              # Trending (product_id + total_bought)
│   │
│   ├── schemas/                     # Pydantic validation schemas
│   │   ├── auth.py                  # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── product.py               # ProductCreate, ProductUpdate, ProductResponse
│   │   ├── cart.py                  # AddCartItem, CartItemResponse, CartResponse
│   │   ├── checkout.py              # CheckoutCreate, CheckoutResponse
│   │   ├── order.py                 # OrderResponse, OrderItemResponse
│   │   ├── coupon.py                # CouponResponse
│   │   └── trending.py              # TrendingResponse
│   │
│   ├── services/                    # Business logic layer
│   │   ├── auth_service.py          # register_user, authenticate_user
│   │   ├── product_service.py       # CRUD + stock update + trie sync
│   │   ├── cart_service.py          # Cart operations (add, update, remove, clear)
│   │   ├── checkout_service.py      # Atomic checkout (stock deduction, order creation)
│   │   ├── coupon_service.py        # Coupon validation + discount calculation
│   │   ├── search_service.py        # C++ Trie autocomplete + exact search
│   │   └── trending_service.py      # Update + fetch trending stats
│   │
│   └── utils/                       # Utility functions
│       └── normalization.py         # Normalize product names for trie indexing
```

---

## Data Flow

### Registration & Login
```
POST /register → auth_service.register_user()
   → hash password (bcrypt) → save User to DB → return user_id

POST /login → auth_service.authenticate_user()
   → verify password → create JWT (python-jose) → return access_token
```

### Product Creation (Admin)
```
POST /admin/products → product_service.create_product()
   → normalize name → save to DB → sync_trie_insert() → return product
```

### Search (Any User)
```
GET /search/autocomplete?q=har → search_service.autocomplete_products()
   → normalize query → C++ Trie.autocomplete() → map results back via DB → return names

GET /search/exact?q=harry+potter → search_service.exact_search_product()
   → normalize query → C++ Trie.search() → if found, fetch from DB → return product
```

### Checkout
```
POST /checkout → checkout_service.process_checkout()
   → validate cart not empty
   → validate coupon (if provided) → calculate discount
   → for each cart item:
       → re-check stock (with row lock)
       → deduct stock
       → create OrderItem (with price snapshot)
       → update Trending stats
   → clear cart
   → commit transaction (atomic)
   → return order
```

---

## Database Schema

```
┌──────────┐     ┌───────────┐     ┌──────────────┐
│  users   │     │ products  │     │   coupons    │
├──────────┤     ├───────────┤     ├──────────────┤
│ id (PK)  │     │ id (PK)   │     │ id (PK)      │
│ name     │◄────┤ created_by│     │ coupon_code  │
│ email    │     │ product_  │     │ discount_type│
│ hashed_  │     │   name    │     │ coupon_      │
│  password│     │ normalized│     │   discount   │
│ role     │     │   _name   │     │ is_active    │
│ is_active│     │ product_  │     └──────────────┘
│ created_ │     │   price   │
│   at     │     │ product_  │
└──────────┘     │   stock   │
      │          │ category  │
      │          │ is_active │
      │          │ created_at│
      │          └───────────┘
      │                │
      ▼                │
┌──────────┐           │         ┌──────────────┐
│  carts   │           │         │  trendings   │
├──────────┤           │         ├──────────────┤
│ id (PK)  │           │         │ product_id   │
│ user_id  │           └────────►│  (PK, FK)    │
│ is_active│                     │ total_bought │
│ created_ │                     │ updated_at   │
│   at     │                     └──────────────┘
└──────────┘
      │
      ▼
┌──────────────┐     ┌──────────┐     ┌──────────────┐
│ cart_items    │     │ orders   │     │ order_items   │
├──────────────┤     ├──────────┤     ├──────────────┤
│ id (PK)      │     │ id (PK)  │     │ id (PK)      │
│ cart_id (FK)  │     │ user_id  │     │ order_id (FK)│
│ product_id   │     │ subtotal │     │ product_id   │
│  (FK)        │     │ discount │     │ product_name │
│ quantity     │     │ final_   │     │   _snapshot  │
│ created_at   │     │   amount │     │ price_       │
└──────────────┘     │ coupon_  │     │   snapshot   │
                     │   code   │     │ quantity     │
                     │ status   │     │ line_total   │
                     │ created_ │     └──────────────┘
                     │   at     │
                     └──────────┘
```

**Key design notes:**
- `OrderItem` stores `product_name_snapshot` and `price_snapshot` — the product name and price **at the time of purchase**. If the admin later changes the price, existing orders aren't affected.
- `Cart` has a one-to-one relationship with `User` (one cart per user).
- `CartItem` has a unique constraint on `(cart_id, product_id)` — you can't add the same product twice, you update the quantity instead.
- `Trending` uses `product_id` as its primary key — one row per product, updated on every checkout.
- Products are **soft-deleted** (`is_active=False`) rather than actually removed from the database.

---

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | None | Create a new user account |
| `POST` | `/login` | None | Login and receive JWT token |
| `GET` | `/me` | Bearer | Get current user profile |

### Admin (`/api/v1/admin`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/products` | Admin | Create a new product |
| `PUT` | `/products/{id}` | Admin | Update product details |
| `DELETE` | `/products/{id}` | Admin | Soft-delete a product |
| `PATCH` | `/products/{id}/stock` | Admin | Update product stock |

### Products (`/api/v1/products`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | None | List all active products |
| `GET` | `/{id}` | None | Get a single product by ID |

### Cart (`/api/v1/cart`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Bearer | View current cart with items and totals |
| `POST` | `/items` | Bearer | Add a product to cart |
| `PUT` | `/items/{item_id}` | Bearer | Update item quantity (0 = remove) |
| `DELETE` | `/items/{item_id}` | Bearer | Remove an item from cart |
| `DELETE` | `/` | Bearer | Clear the entire cart |

### Checkout (`/api/v1/checkout`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/` | Bearer | Process checkout (optional coupon code) |

### Search (`/api/v1/search`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/autocomplete?q=...` | None | Get product name suggestions (C++ Trie) |
| `GET` | `/exact?q=...` | None | Find exact product match (C++ Trie + DB) |

### Trending (`/api/v1/trending`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/?limit=10` | None | Get top trending products by purchase count |

---

## C++ Trie Search Engine

The search system uses a **Trie (prefix tree)** data structure written in C++ for high-speed autocomplete and exact search. The C++ code is compiled into a Python-importable shared library (`.so`) using **pybind11**.

### Why C++ instead of pure Python?

A Trie implemented in Python uses dictionaries at every node, which means:
- Each node allocates a Python `dict` object (56+ bytes overhead)
- Every character lookup goes through Python's hash table
- Garbage collector has to track thousands of small objects

The C++ version uses fixed-size arrays (`Node *links[128]`), meaning:
- Zero hash overhead — direct array indexing by ASCII value
- Cache-friendly memory layout
- No garbage collection pauses
- **10-100x faster** for autocomplete queries on large datasets

### How it works

```
Python                              C++ (in-memory)
───────                             ───────────────
search_service.py                   trie_wrapper.cpp
      │                                   │
      │  from trie_module import Trie     │
      │──────────────────────────────────►│
      │                                   │
      │  trie.insert("harry potter")     │  Node→h→a→r→r→y→ →p→o→t→t→e→r ✓
      │  trie.autocomplete("har")        │  DFS from h→a→r → ["harry potter", ...]
      │  trie.search("harry potter")     │  Walk nodes → True/False
      │  trie.remove("harry potter")     │  Mark end node as deleted (soft delete)
```

### Trie lifecycle

1. **Server starts** → `load_trie_from_db()` reads all active products from Postgres and inserts their normalized names into the C++ Trie
2. **Admin creates product** → `sync_trie_insert()` adds it to the Trie immediately
3. **Admin updates product name** → `sync_trie_remove()` old name + `sync_trie_insert()` new name
4. **Admin deletes product** → `sync_trie_remove()` marks it as deleted in the Trie

### Compiling the Trie module

You need a C++ compiler (Apple Clang works, no need for Xcode IDE):

```bash
# Make sure xcode command line tools are set up
sudo xcode-select --switch /Library/Developer/CommandLineTools

# Compile
cd app/cpp_bridge
c++ -O3 -shared -std=c++17 -fPIC \
  $(../../.venv/bin/python -m pybind11 --includes) \
  trie_wrapper.cpp \
  -o trie_module$(../../.venv/bin/python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))") \
  -undefined dynamic_lookup
```

This produces `trie_module.cpython-311-darwin.so` which Python can `import` directly.

### pybind11 bindings (what makes it work)

The magic is in `trie_wrapper.cpp` at the bottom:

```cpp
#include <pybind11/pybind11.h>  // Core pybind11
#include <pybind11/stl.h>       // Auto-converts vector<string> ↔ list[str]

PYBIND11_MODULE(trie_module, m) {
    py::class_<Trie>(m, "Trie")
        .def(py::init<>())                    // Trie() constructor
        .def("insert", &Trie::insert)         // t.insert("word")
        .def("search", &Trie::search)         // t.search("word") → bool
        .def("remove", &Trie::remove)         // t.remove("word")
        .def("autocomplete", &Trie::find);    // t.autocomplete("prefix") → list[str]
}
```

This tells pybind11: "Take my C++ `Trie` class and expose it to Python with these method names." The `pybind11/stl.h` header automatically handles converting `vector<string>` to Python `list[str]` and back.

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL running locally (or via Docker)
- C++ compiler (Apple Clang via `xcode-select --install` on macOS)
- [uv](https://docs.astral.sh/uv/) package manager

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/PranjalBisen/Book-Store.git
cd Book-Store

# 2. Install Python dependencies
uv sync

# 3. Set up PostgreSQL
# Create a database called 'bookstore' with a user that has access
createdb bookstore

# 4. Compile the C++ Trie module
cd app/cpp_bridge
c++ -O3 -shared -std=c++17 -fPIC \
  $(../../.venv/bin/python -m pybind11 --includes) \
  trie_wrapper.cpp \
  -o trie_module$(../../.venv/bin/python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))") \
  -undefined dynamic_lookup
cd ../..

# 5. Run the server
.venv/bin/uvicorn main:app --reload
```

The server starts at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `"secret"` | JWT signing key (change in production!) |
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/bookstore` | PostgreSQL connection string |

Set them via shell export or a `.env` file:

```bash
export SECRET_KEY="your-super-secret-key-here"
export DATABASE_URL="postgresql://myuser:mypass@localhost:5432/bookstore"
```

---

## Running the Server

```bash
# Using uvicorn directly (recommended for development)
.venv/bin/uvicorn main:app --reload

# Or via the main.py entry point
.venv/bin/python main.py
```

On startup, the server will:
1. Create all database tables if they don't exist (`Base.metadata.create_all`)
2. Load all active product names into the C++ Trie (`load_trie_from_db`)
3. Start accepting requests on port 8000

---

## Development Notes

### Coding Style
- **No spaces around operators** (`x=1`, not `x = 1`) — this is a deliberate project convention.
- Services raise `HTTPException` directly for simplicity (no custom exception layer).
- Models use `datetime.utcnow` (without parentheses) as column defaults so SQLAlchemy calls it at insert time.

### Security
- Passwords are hashed with **bcrypt** via `passlib`.
- JWT tokens are signed with **HS256** via `python-jose`.
- Admin routes are protected by the `require_admin` dependency which checks `UserRole.admin`.
- The checkout flow uses `with_for_update()` row-level locks to prevent race conditions on stock.

### Checkout Atomicity
The checkout process runs as a **single database transaction**. If any step fails (stock check, order creation, trending update), the entire transaction is rolled back. This prevents partial orders or incorrect stock counts.

---

## Author

**Pranjal D. Bisen**

- GitHub: [PranjalBisen](https://github.com/PranjalBisen)
