# Workspace

## Overview

pnpm workspace monorepo using TypeScript + a Python Telegram bot.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Telegram Bot (`artifacts/telegram-bot/`)

A professional exclusive Telegram bot for generating test credit/debit card numbers.

### Features
- **License key system**: Time-based access control (minutes, hours, days)
- **CC Generator**: Country → Bank → Network → Category → Debit/Credit → Quantity
- **20+ Countries**, 50+ banks, 9 card networks (Visa, Mastercard, Amex, Discover, JCB, UnionPay, Rupay, Elo, Diners)
- **Up to 10,000 cards** per generation with real-time progress bar
- **Admin panel** (`/admin`): stats, uptime, license generation, user management, broadcast
- **Flask health server**: port 8000 for Uptime Robot / Render keep-alive

### Stack
- **Python 3.11**
- **python-telegram-bot 21.6** (async)
- **Flask 3.0** (health server)
- **SQLite** (user/license database)

### Key Commands
- `/start` — Open main menu (checks authorization)
- `/redeem [KEY]` — Redeem a licence key
- `/admin` — Admin panel (admin ID: 8731647972)

### Bot Config
- Bot token stored in `config.py` + `BOT_TOKEN` env var
- Admin ID: `8731647972`
- Database: `bot_data.db` (SQLite, auto-created)

### Deployment (Render)
- `render.yaml` is configured for Render hosting
- `Procfile` included
- Health endpoint: `GET /health` or `GET /ping`
- Set `BOT_TOKEN` and `ADMIN_ID` as environment variables on Render

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
