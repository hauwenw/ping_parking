# Security & Authentication Stories

**Total Stories**: 6 (all Must Have)
**Sprint**: Sprint 1 (3 stories) + Sprint 4 (3 stories)

## Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-SEC-001 | Admin Authentication (JWT) | Must Have | Sprint 1 |
| US-SEC-002 | Session Management and Auto-Logout | Must Have | Sprint 1 |
| US-SEC-003 | Role-Based Access Control (Admin-Only) | Must Have | Sprint 1 |
| US-SEC-004 | Privacy-Compliant Data Entry (No National ID) | Must Have | Sprint 2 |
| US-SEC-005 | Row Level Security (RLS) Enforcement | ~~Must Have~~ Dropped | — |
| US-SEC-006 | License Plate Encryption and Masking | Must Have | Sprint 4 |

## Overview

Foundation security for Phase 1: authentication, session management, role-based access, privacy compliance, and data protection. RLS dropped — access control handled in FastAPI middleware.

**Key Dependencies**: admin_users table, JWT middleware, database schema
**Estimated Effort**: 12-15 story points
