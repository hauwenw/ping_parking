# Coding Conventions — Python / FastAPI Backend

**Date**: 2026-02-14
**Applies to**: `ping-parking-api/` codebase
**Stack**: Python 3.11+, FastAPI 0.110+, SQLAlchemy 2.0+, Pydantic 2.0+, Alembic, pytest

---

## 1. General Python Style

### Formatting & Linting
- **Formatter**: `ruff format` (Black-compatible, line length 88)
- **Linter**: `ruff check` with default rules + `I` (isort), `F` (pyflakes), `E` (pycodestyle)
- **Type checking**: `mypy --strict` on all new code
- **Pre-commit**: Run `ruff format && ruff check && mypy app/` before commits

### Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Files/modules | `snake_case` | `customer_service.py` |
| Classes | `PascalCase` | `CustomerService` |
| Functions/methods | `snake_case` | `get_customer_by_id()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_LOGIN_ATTEMPTS = 5` |
| Private | `_leading_underscore` | `_hash_password()` |
| Type vars | `PascalCase` | `T = TypeVar("T")` |

### Import Order
```python
# 1. Standard library
from datetime import datetime
from typing import Annotated
from uuid import UUID

# 2. Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local application
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerService
```

### Type Hints
- **Required** on all function signatures (parameters and return types)
- Use `Annotated` for dependency injection types
- Use `Optional[X]` or `X | None` for nullable fields
- Prefer specific types over `Any`

```python
# Good
async def get_customer(customer_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> CustomerResponse:
    ...

# Avoid
async def get_customer(customer_id, db):
    ...
```

---

## 2. FastAPI Conventions

### Project Structure (Layered Architecture)
```
app/
├── main.py              # App init, middleware, router includes
├── config.py            # Settings via pydantic-settings
├── database.py          # Engine, session factory
├── dependencies.py      # Shared dependencies (get_db, get_current_user)
├── api/                 # Route handlers (thin controllers)
│   ├── __init__.py
│   ├── router.py        # Aggregates all sub-routers
│   ├── customers.py
│   ├── spaces.py
│   ├── agreements.py
│   ├── payments.py
│   ├── tags.py
│   ├── sites.py
│   └── auth.py
├── schemas/             # Pydantic request/response models
│   ├── customer.py
│   ├── space.py
│   └── ...
├── models/              # SQLAlchemy ORM models
│   ├── base.py          # DeclarativeBase
│   ├── customer.py
│   ├── space.py
│   └── ...
├── services/            # Business logic layer
│   ├── customer_service.py
│   ├── agreement_service.py
│   └── audit_logger.py
└── utils/               # Shared utilities
    ├── auth.py          # JWT creation/validation
    ├── validators.py    # Taiwan phone, etc.
    └── errors.py        # Custom exception classes
```

### Router Conventions
- One file per domain in `api/`
- Use `APIRouter` with `prefix` and `tags`
- Route handlers should be thin — delegate to services
- Use `Annotated` for dependency injection

```python
# app/api/customers.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.admin_user import AdminUser
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AdminUser, Depends(get_current_user)],
) -> CustomerResponse:
    service = CustomerService(db)
    return await service.create(data, current_user)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[AdminUser, Depends(get_current_user)],
) -> CustomerResponse:
    service = CustomerService(db)
    customer = await service.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="找不到該客戶")
    return customer
```

### Router Registration
```python
# app/api/router.py
from fastapi import APIRouter
from app.api import auth, customers, spaces, agreements, payments, tags, sites

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(spaces.router)
api_router.include_router(agreements.router)
api_router.include_router(payments.router)
api_router.include_router(tags.router)
api_router.include_router(sites.router)
```

### Dependency Injection
- Define shared dependencies in `dependencies.py`
- Use `Depends()` with `Annotated` type aliases
- DB sessions use `yield` for cleanup

```python
# app/dependencies.py
from typing import Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.utils.auth import decode_jwt_token

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AdminUser:
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無效的認證令牌")
    # ... look up user
    return user

# Type aliases for cleaner signatures
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[AdminUser, Depends(get_current_user)]
```

---

## 3. Pydantic Schema Conventions

### Naming Pattern
| Purpose | Suffix | Example |
|---------|--------|---------|
| Create request | `Create` | `CustomerCreate` |
| Update request | `Update` | `CustomerUpdate` |
| API response | `Response` | `CustomerResponse` |
| List response | `ListResponse` | `CustomerListResponse` |
| Internal/DB read | `InDB` | `CustomerInDB` |

### Schema Structure
```python
# app/schemas/customer.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class CustomerBase(BaseModel):
    """Shared fields between create and update."""
    name: str
    phone: str
    contact_phone: str | None = None
    email: EmailStr | None = None
    notes: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Phone must be Taiwan mobile format: 09XXXXXXXX."""
        import re
        if not re.match(r"^09\d{8}$", v):
            raise ValueError("手機號碼格式錯誤，請輸入09開頭的10碼號碼")
        return v


class CustomerCreate(CustomerBase):
    """Request body for POST /customers."""
    pass


class CustomerUpdate(BaseModel):
    """Request body for PATCH /customers/{id}. All fields optional."""
    name: str | None = None
    phone: str | None = None
    contact_phone: str | None = None
    email: EmailStr | None = None
    notes: str | None = None


class CustomerResponse(CustomerBase):
    """Response body for customer endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    active_agreement_count: int = 0
```

### Rules
- Use `field_validator` with `@classmethod` for custom validation
- Error messages in Traditional Chinese
- Use `ConfigDict(from_attributes=True)` for ORM model conversion
- Keep `Create` schemas strict (required fields), `Update` schemas lenient (all optional)
- Never expose internal fields (password hashes, encryption keys) in response schemas

---

## 4. SQLAlchemy Model Conventions

### Base Model
```python
# app/models/base.py
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Add created_at and updated_at to any model."""
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class UUIDMixin:
    """Add UUID primary key."""
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
```

### Model Pattern
```python
# app/models/customer.py
from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Customer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(10), index=True)
    contact_phone: Mapped[str | None] = mapped_column(String(10))
    email: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    agreements: Mapped[list["Agreement"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, name={self.name!r})"
```

### Rules
- Use `Mapped[]` type annotations (SQLAlchemy 2.0 style) — never use `Column()`
- Use `mapped_column()` for column config
- `UUID` primary keys via `UUIDMixin`
- `created_at` / `updated_at` via `TimestampMixin` (except `system_logs` which has no `updated_at`)
- Explicit `__tablename__` on every model (plural snake_case: `customers`, `agreements`)
- Use `relationship()` with `back_populates` (not `backref`)
- PostgreSQL array type for tags: `tags: Mapped[list[str]] = mapped_column(ARRAY(String))`

---

## 5. Service Layer Conventions

### Pattern
- One service class per domain
- Constructor takes `AsyncSession`
- All business logic lives here (not in routes, not in models)
- Services call `AuditLogger` after successful mutations

```python
# app/services/customer_service.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit_logger import AuditLogger


class CustomerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit = AuditLogger(db)

    async def create(self, data: CustomerCreate, user: AdminUser) -> Customer:
        customer = Customer(**data.model_dump())
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        await self.audit.log_create("customers", customer.id, data.model_dump(), user)
        return customer

    async def get_by_id(self, customer_id: UUID) -> Customer | None:
        result = await self.db.execute(select(Customer).where(Customer.id == customer_id))
        return result.scalar_one_or_none()

    async def update(self, customer_id: UUID, data: CustomerUpdate, user: AdminUser) -> Customer:
        customer = await self.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)
        old_values = {k: getattr(customer, k) for k in data.model_dump(exclude_unset=True)}
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        await self.db.commit()
        await self.db.refresh(customer)
        await self.audit.log_update("customers", customer.id, old_values, data.model_dump(exclude_unset=True), user)
        return customer
```

---

## 6. Error Handling

### Custom Exception Classes
```python
# app/utils/errors.py
from uuid import UUID


class BusinessError(Exception):
    """Base class for business logic errors."""
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BusinessError):
    def __init__(self, entity: str, entity_id: UUID):
        super().__init__(f"找不到{entity} (ID: {entity_id})", "NOT_FOUND")


class DuplicateError(BusinessError):
    def __init__(self, entity: str, field: str, value: str):
        super().__init__(f"{entity}的{field}「{value}」已存在", "DUPLICATE")


class DoubleBookingError(BusinessError):
    def __init__(self, space_name: str):
        super().__init__(f"車位「{space_name}」已有有效合約，無法重複分配", "DOUBLE_BOOKING")
```

### Global Exception Handler
```python
# In app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.errors import BusinessError, NotFoundError

app = FastAPI()

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"code": exc.code, "message": exc.message})

@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"code": exc.code, "message": exc.message})
```

### Rules
- Error messages always in **Traditional Chinese**
- Raise `BusinessError` subclasses from services, not `HTTPException`
- Only route handlers or exception handlers should produce HTTP responses
- Never catch broad `Exception` silently — let it propagate

---

## 7. Database & Alembic Conventions

### Async Engine Setup
```python
# app/database.py
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

### Migration Naming
```bash
# Format: YYYY_MM_DD_HHMM_description
alembic revision --autogenerate -m "add_customers_table"
alembic revision --autogenerate -m "add_tags_array_to_spaces"
```

### Rules
- Always use `--autogenerate` — models are the source of truth
- Review every generated migration before running
- One logical change per migration
- Never edit a migration that has been applied to production
- Use `expire_on_commit=False` for async sessions

---

## 8. Testing Conventions

### File Structure
```
tests/
├── conftest.py           # Shared fixtures (db, client, auth)
├── test_auth.py          # Authentication tests
├── test_customers.py     # Customer CRUD tests
├── test_agreements.py    # Agreement lifecycle tests
├── test_payments.py      # Payment tests
└── test_audit.py         # Audit logging tests
```

### Fixture Pattern
```python
# tests/conftest.py
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import async_session_factory

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
async def auth_client(client: AsyncClient):
    """Authenticated client with admin token."""
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin1@ping.tw",
        "password": "Password123",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
```

### Test Naming
```python
# test_customers.py
import pytest

@pytest.mark.anyio
async def test_create_customer_success(auth_client):
    """POST /customers with valid data returns 201."""
    ...

@pytest.mark.anyio
async def test_create_customer_duplicate_phone_fails(auth_client):
    """POST /customers with existing phone returns 409."""
    ...

@pytest.mark.anyio
async def test_get_customer_not_found(auth_client):
    """GET /customers/{id} with invalid ID returns 404."""
    ...
```

### Rules
- Use `pytest.mark.anyio` for async tests
- Use `AsyncClient` (httpx) over `TestClient` for async endpoints
- Test file names: `test_{domain}.py`
- Test function names: `test_{action}_{scenario}` (snake_case)
- Use testcontainers for real PostgreSQL in CI
- Each test should be independent — no shared mutable state between tests

---

## 9. Configuration

### Settings Pattern
```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str

    # Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # App
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### Rules
- All config via environment variables — never hardcode secrets
- Use `pydantic-settings` for validation and type coercion
- `.env` for local dev, Fly.io secrets for production
- Provide `.env.example` with placeholder values (never real secrets)

---

## 10. API Response Format

### Consistent JSON Structure
```json
// Success (single)
{
  "id": "uuid",
  "name": "王大明",
  "phone": "0912345678",
  "created_at": "2026-02-14T10:30:00+08:00"
}

// Success (list with pagination)
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}

// Error
{
  "code": "DOUBLE_BOOKING",
  "message": "車位「A區-01」已有有效合約，無法重複分配"
}
```

### Rules
- Use ISO 8601 with timezone for all datetime fields
- Pagination: `page` (1-indexed) + `page_size` (default 20, max 100)
- All error messages in Traditional Chinese
- Use semantic HTTP status codes: 200, 201, 400, 401, 404, 409, 422, 500
