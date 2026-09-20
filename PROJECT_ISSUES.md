# Project issues and fixes

This document summarizes issues found during re-examination of the OmniCommerce project and their status.

**Integration documentation:** All 8 channels (Shopify, Amazon, Flipkart, Myntra, Meta Ads, Google Ads, Delhivery, Selloship) have in-app **Guide** buttons with step-by-step setup. Backend catalog in `apps/api-python/app/http/controllers/integrations.py` defines `setupSteps` (and optionally `setupGuide`) per provider. See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for full integration rules and tables.

**Inventory scoping:** `GET /api/inventory` is now scoped to the current user: only variants that appear in orders from the user's connected channel accounts are returned. If no marketplace is connected, the list is empty. This prevents stored inventory from being visible to all users when no channel is integrated. File: `apps/api-python/app/http/controllers/inventory.py`.

**Workers page:** Redesigned to show all connected channels (from `/integrations/connected-summary`) with per-channel "Sync orders" and "Sync inventory" (Shopify only). Each action calls the correct endpoint (`/sync/orders/{accountId}` or `/integrations/shopify/sync`). Job queue shows SyncJobs for the user's channel accounts.

**Webhooks:** Subscriptions and events are channel-agnostic; subscription labels include channel name (e.g. "SHOPIFY (mystore)", "AMAZON"). Filter source dropdown is built from actual event sources. Register button label: "Register webhooks (Shopify)".

**Integrations UI:** Card layout uses `min-h-[280px]` and `items-start` so opening one card's Configure form does not change the height of other cards. All connect/setup CTAs use the same label: "Configure".

---

## Critical (fixed)

### 1. Order actions allowed on any user's order (IDOR)
- **Fix:** Each of confirm/pack/ship/cancel verifies `order.channel_account_id` is in the current user's channel account IDs; otherwise returns `403 Access denied`.
- **Files:** `apps/api-python/app/http/controllers/orders.py`

### 2. Password reset token leaked in API response
- **Fix:** `/forgot-password` endpoint now returns `reset_link` in response ONLY when `IS_DEVELOPMENT` is True. In production, tokens are strictly emailed and omitted from API responses.
- **Files:** `apps/api-python/app/http/controllers/auth.py`

### 3. Weak / default ENCRYPTION_KEY in production
- **Fix:** Added startup validation check in `main.py` alerting if `ENCRYPTION_KEY` is set to the default public key in production.
- **Files:** `apps/api-python/main.py`, `apps/api-python/app/config.py`

### 4. Database seed script running without guards in production
- **Fix:** `seed.py` now blocks execution in `PRODUCTION` unless `--force` is explicitly passed and supports custom admin credentials via environment variables (`SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD`).
- **Files:** `apps/api-python/seed.py`

### 5. Audit logs visible to all users
- **Fix:** Query filtered by `AuditLog.user_id == current_user.id`. Admins also see system logs (`user_id IS NULL`).
- **Files:** `apps/api-python/app/http/controllers/audit.py`

---

## Design / product (documented)

### 6. Inventory, warehouses, products: global vs per-user
- **Current:** Shared catalog/warehouses. Acceptable for single-tenant.
- **Optional later:** If multi-tenant is required, add `user_id` (or tenant_id) to models and scope all reads/writes.

### 7. SKU costs: global
- **Current:** Shared SKU cost table. Acceptable for company-wide cost master.

---

## Optional & logic improvements (fixed)

### 8. Warehouse resolution inconsistent across order endpoints
- **Fix:** `confirm_order` was hardcoding "Main Warehouse", while `ship_order` and `cancel_order` used `get_default_warehouse(db)`. Now all order endpoints consistently use `get_default_warehouse(db)`.
- **Files:** `apps/api-python/app/http/controllers/orders.py`

### 9. Webhook register creds format & retry endpoint
- **Fix:** `POST /webhooks/register/{integration_id}` accepts JSON creds and raw token. Added retry endpoint for webhooks.
- **Files:** `apps/api-python/app/http/controllers/webhooks.py`

---

## Summary

| Category            | Status |
|---------------------|--------|
| Critical            | 5 fixed |
| Design (optional)   | 2 documented for future |
| Optional/Logic improvements | 2 fixed |

All identified security, correctness, and hygiene issues have been addressed and verified.
