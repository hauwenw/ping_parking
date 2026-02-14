# Coding Conventions — JavaScript / Next.js Frontend

**Date**: 2026-02-14
**Applies to**: `ping-parking-web/` codebase
**Stack**: Next.js 14 (App Router), TypeScript 5.x, Tailwind CSS 3.x, shadcn/ui, SWR

---

## 1. General TypeScript Style

### Formatting & Linting
- **Formatter**: Prettier (printWidth: 100, singleQuote: true, semi: false)
- **Linter**: ESLint with `next/core-web-vitals` + `@typescript-eslint/recommended`
- **Pre-commit**: Run `npm run lint && npm run type-check` before commits

### Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Files (components) | `kebab-case.tsx` | `customer-form.tsx` |
| Files (utils/lib) | `kebab-case.ts` | `api-client.ts` |
| Files (Next.js special) | Framework names | `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx` |
| Components | `PascalCase` | `CustomerForm` |
| Functions/hooks | `camelCase` | `useCustomers()`, `formatPhone()` |
| Constants | `UPPER_SNAKE_CASE` | `API_BASE_URL` |
| Types/Interfaces | `PascalCase` | `Customer`, `AgreementStatus` |
| Enums | `PascalCase` | `PaymentStatus.Pending` |
| CSS classes | Tailwind utilities | `className="flex items-center gap-2"` |

### Import Order
```typescript
// 1. React/Next.js
import { Suspense } from 'react'
import { useRouter } from 'next/navigation'

// 2. Third-party libraries
import useSWR from 'swr'
import { format } from 'date-fns'

// 3. shadcn/ui components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

// 4. Local components
import { CustomerForm } from '@/components/customer-form'

// 5. Local utilities/types
import { apiClient } from '@/lib/api-client'
import type { Customer } from '@/types/customer'
```

### Type Annotations
- **Prefer `type` over `interface`** for object shapes (consistency)
- Use `interface` only when declaration merging is needed
- Never use `any` — prefer `unknown` and narrow with type guards
- Export types from `types/` directory

```typescript
// types/customer.ts
export type Customer = {
  id: string
  name: string
  phone: string
  contactPhone: string | null
  email: string | null
  notes: string | null
  createdAt: string
  updatedAt: string
  activeAgreementCount: number
}

export type CustomerCreate = Pick<Customer, 'name' | 'phone'> & {
  contactPhone?: string
  email?: string
  notes?: string
}
```

---

## 2. Next.js App Router Conventions

### Directory Structure
```
app/
├── login/
│   └── page.tsx                    # Login page
├── admin/
│   ├── layout.tsx                  # Admin shell (sidebar + header)
│   ├── agreements/
│   │   ├── page.tsx                # Agreement list (default landing)
│   │   ├── [id]/
│   │   │   └── page.tsx            # Agreement detail
│   │   ├── loading.tsx             # Skeleton loader
│   │   └── error.tsx               # Error boundary
│   ├── customers/
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   │   └── page.tsx
│   │   ├── loading.tsx
│   │   └── error.tsx
│   ├── spaces/
│   │   ├── page.tsx
│   │   ├── [id]/
│   │   │   └── page.tsx
│   │   ├── loading.tsx
│   │   └── error.tsx
│   └── settings/
│       ├── page.tsx                # Tag/site management
│       ├── audit-logs/
│       │   └── page.tsx
│       ├── loading.tsx
│       └── error.tsx
├── layout.tsx                      # Root layout (<html>, <body>)
├── not-found.tsx                   # 404 page
└── globals.css                     # Tailwind base styles
```

### File Convention Rules
| File | Purpose | Required? |
|------|---------|-----------|
| `page.tsx` | Route UI | Yes (defines a route) |
| `layout.tsx` | Shared UI wrapper | Root layout required |
| `loading.tsx` | Suspense fallback skeleton | Recommended per section |
| `error.tsx` | Error boundary (must be `'use client'`) | Recommended per section |
| `not-found.tsx` | 404 UI | Root level |

### Server vs Client Components
```
Default: Server Components (no directive needed)
Client:  Add 'use client' at top of file

Rules:
- Server Components: data fetching, reading backend, rendering HTML
- Client Components: interactivity, event handlers, useState/useEffect, browser APIs
- Keep 'use client' boundary as low as possible in the component tree
- Never import server-only code in client components
```

**Pattern: Server parent, client child**
```tsx
// app/admin/customers/page.tsx (Server Component — no directive)
import { CustomerTable } from '@/components/customer-table'
import { apiClient } from '@/lib/api-client'

export default async function CustomersPage() {
  const customers = await apiClient.getCustomers()
  return (
    <div>
      <h1 className="text-2xl font-bold">客戶管理</h1>
      <CustomerTable initialData={customers} />
    </div>
  )
}
```

```tsx
// components/customer-table.tsx (Client Component — needs interactivity)
'use client'

import { useState } from 'react'
import type { Customer } from '@/types/customer'

export function CustomerTable({ initialData }: { initialData: Customer[] }) {
  const [search, setSearch] = useState('')
  // ... interactive table with filtering
}
```

---

## 3. Component Conventions

### Component File Structure
```tsx
// 1. 'use client' directive (if needed)
'use client'

// 2. Imports
import { useState } from 'react'
import { Button } from '@/components/ui/button'

// 3. Types (or import from types/)
type CustomerFormProps = {
  customer?: Customer
  onSubmit: (data: CustomerCreate) => Promise<void>
  onCancel: () => void
}

// 4. Component (named export, not default — except pages)
export function CustomerForm({ customer, onSubmit, onCancel }: CustomerFormProps) {
  // 5. Hooks first
  const [isLoading, setIsLoading] = useState(false)

  // 6. Handlers
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // ...
  }

  // 7. Render
  return (
    <form onSubmit={handleSubmit}>
      {/* ... */}
    </form>
  )
}
```

### Rules
- **Pages**: `export default function` (Next.js requirement)
- **Components**: Named exports (`export function CustomerForm`)
- **One component per file** — colocate small helpers in the same file only if they're tightly coupled
- Props type defined inline or imported from `types/`
- Use shadcn/ui components as base — customize via Tailwind classes, don't override internal styles

### Component Categories
```
components/
├── ui/                  # shadcn/ui primitives (auto-generated, don't modify)
│   ├── button.tsx
│   ├── input.tsx
│   ├── dialog.tsx
│   └── ...
├── layout/              # Layout components
│   ├── sidebar.tsx
│   ├── header.tsx
│   └── page-header.tsx
├── forms/               # Form components
│   ├── customer-form.tsx
│   ├── agreement-form.tsx
│   └── login-form.tsx
├── tables/              # Table components
│   ├── customer-table.tsx
│   ├── agreement-table.tsx
│   └── data-table.tsx   # Reusable base table
└── shared/              # Shared UI
    ├── status-badge.tsx
    ├── tag-dot.tsx
    └── confirm-dialog.tsx
```

---

## 4. Data Fetching Conventions

### API Client
```typescript
// lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private token: string | null = null

  setToken(token: string) {
    this.token = token
  }

  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
        ...options?.headers,
      },
    })

    if (!res.ok) {
      const error = await res.json().catch(() => ({ message: '系統錯誤，請稍後再試' }))
      throw new ApiError(res.status, error.message, error.code)
    }

    return res.json()
  }

  // Domain methods
  getCustomers(params?: CustomerListParams) { return this.fetch<PaginatedResponse<Customer>>('/customers' + toQueryString(params)) }
  getCustomer(id: string) { return this.fetch<Customer>(`/customers/${id}`) }
  createCustomer(data: CustomerCreate) { return this.fetch<Customer>('/customers', { method: 'POST', body: JSON.stringify(data) }) }
  updateCustomer(id: string, data: CustomerUpdate) { return this.fetch<Customer>(`/customers/${id}`, { method: 'PATCH', body: JSON.stringify(data) }) }
}

export const apiClient = new ApiClient()
```

### SWR for Client Components
```typescript
// hooks/use-customers.ts
'use client'

import useSWR from 'swr'
import { apiClient } from '@/lib/api-client'
import type { Customer, PaginatedResponse } from '@/types/customer'

export function useCustomers(params?: CustomerListParams) {
  const key = params ? `/customers?${new URLSearchParams(params as any)}` : '/customers'
  return useSWR<PaginatedResponse<Customer>>(key, () => apiClient.getCustomers(params))
}

export function useCustomer(id: string) {
  return useSWR<Customer>(`/customers/${id}`, () => apiClient.getCustomer(id))
}
```

### Rules
- **Server Components**: Use `apiClient` directly with `await` (server-side fetch)
- **Client Components**: Use SWR hooks for data fetching with caching
- Never call `fetch()` directly in client components — always go through `apiClient` or SWR hooks
- Custom hooks in `hooks/` directory, named `use-{domain}.ts`

---

## 5. Styling Conventions (Tailwind CSS)

### General Rules
- Use Tailwind utility classes — no custom CSS files except `globals.css`
- Use `cn()` helper (from shadcn/ui) for conditional classes
- Responsive: desktop-first (`md:` and `lg:` prefixes for desktop, mobile is the base)
- Color palette: Use shadcn/ui CSS variables (`bg-background`, `text-foreground`, `border`)

```tsx
import { cn } from '@/lib/utils'

function StatusBadge({ status }: { status: AgreementStatus }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-1 text-xs font-medium',
        status === 'active' && 'bg-green-100 text-green-700',
        status === 'expired' && 'bg-gray-100 text-gray-700',
        status === 'terminated' && 'bg-red-100 text-red-700',
        status === 'pending' && 'bg-yellow-100 text-yellow-700',
      )}
    >
      {statusLabels[status]}
    </span>
  )
}
```

### Spacing Scale
- Use Tailwind's default spacing scale (4px base): `p-2` = 8px, `p-4` = 16px, etc.
- Page padding: `p-6` (24px)
- Card padding: `p-4` (16px)
- Section gap: `gap-6` (24px)
- Form field gap: `gap-4` (16px)

---

## 6. Form Handling

### Pattern: Controlled Forms with shadcn/ui
```tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

type CustomerFormProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: CustomerCreate) => Promise<void>
  initialData?: Customer
}

export function CustomerFormDialog({ open, onOpenChange, onSubmit, initialData }: CustomerFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrors({})

    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData) as unknown as CustomerCreate

    try {
      await onSubmit(data)
      onOpenChange(false)
    } catch (err) {
      if (err instanceof ApiError) {
        setErrors({ _form: err.message })
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{initialData ? '編輯客戶' : '新增客戶'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">姓名 *</Label>
            <Input id="name" name="name" defaultValue={initialData?.name} required />
          </div>
          <div>
            <Label htmlFor="phone">手機號碼 *</Label>
            <Input id="phone" name="phone" defaultValue={initialData?.phone} placeholder="09XX-XXX-XXX" required />
          </div>
          {errors._form && <p className="text-sm text-red-500">{errors._form}</p>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>取消</Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '儲存中...' : '儲存'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

### Rules
- Use modal dialogs (shadcn `Dialog`) for create/edit forms
- All form labels in Traditional Chinese
- Show loading state on submit button
- Display errors inline below the form or per-field
- Use `defaultValue` for edit forms, not `value` (avoids controlled input complexity)

---

## 7. Localization / Formatting

### Formatter Utilities
```typescript
// lib/utils/format.ts

/** Display phone: 0912345678 → 0912-345-678 */
export function formatPhone(phone: string): string {
  if (phone.length !== 10) return phone
  return `${phone.slice(0, 4)}-${phone.slice(4, 7)}-${phone.slice(7)}`
}

/** Display currency: 3600 → NT$3,600 */
export function formatTWD(amount: number): string {
  return `NT$${amount.toLocaleString('zh-TW')}`
}

/** Display date: 2026-02-14 → 2026年02月14日 */
export function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return `${d.getFullYear()}年${String(d.getMonth() + 1).padStart(2, '0')}月${String(d.getDate()).padStart(2, '0')}日`
}

/** Display datetime: ISO → 2026年02月14日 10:30 */
export function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr)
  return `${formatDate(dateStr)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
```

### Rules
- All UI labels in Traditional Chinese — no English text in the UI
- Use formatter functions consistently (never format inline)
- Store phone as `09XXXXXXXX`, display as `09XX-XXX-XXX`
- Store currency as integer (no decimals for TWD)
- Store dates as ISO 8601 with timezone

---

## 8. Error Handling

### Error Boundary Pattern
```tsx
// app/admin/customers/error.tsx
'use client'

export default function CustomersError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <h2 className="text-lg font-semibold">載入客戶資料時發生錯誤</h2>
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <Button onClick={reset} variant="outline">重試</Button>
    </div>
  )
}
```

### API Error Class
```typescript
// lib/api-error.ts
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
```

### Rules
- Every route segment should have an `error.tsx` boundary
- Error messages displayed in Traditional Chinese
- Use `loading.tsx` for skeleton states during data fetching
- API errors caught at the form/component level, not globally

---

## 9. Authentication Flow

### Token Management
```typescript
// lib/auth.ts
'use client'

const TOKEN_KEY = 'ping_auth_token'

export function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}
```

### Protected Route Pattern
```tsx
// components/auth-guard.tsx
'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { getToken } from '@/lib/auth'

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (!getToken()) {
      router.replace('/login')
    }
  }, [router])

  if (!getToken()) return null
  return <>{children}</>
}
```

### Rules
- Store JWT in memory or localStorage (httpOnly cookies ideal but complex with separate backend)
- Wrap admin layout with `AuthGuard`
- Redirect to `/login` on 401 responses from API
- Clear token on logout and redirect

---

## 10. Path Aliases

### tsconfig.json
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Usage
```typescript
// Always use @ alias — never relative paths beyond one level
import { Button } from '@/components/ui/button'      // Good
import { apiClient } from '@/lib/api-client'          // Good
import { formatTWD } from '@/lib/utils/format'        // Good
import { CustomerForm } from './customer-form'         // OK for same directory
import { CustomerForm } from '../../components/...'    // Bad — use @/ alias
```
