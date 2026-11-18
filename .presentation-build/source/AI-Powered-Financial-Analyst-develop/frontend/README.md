# Frontend

React + Tailwind CSS dashboard. Talks only to the backend REST API (`backend/`) —
never to the `ai/` modules or the database directly.

| Folder | Purpose |
|---|---|
| `src/components/` | Reusable, presentation-only UI components |
| `src/pages/` | Route-level views (Dashboard, Login, TickerDetail, Chat, Reports) |
| `src/routes/` | React Router route definitions |
| `src/services/` | Axios API clients (one file per backend resource) |
| `src/hooks/` | Custom React hooks (e.g. `useAuth`, `useTickerData`) |
| `src/context/` | React Context providers (auth state, theme) |
| `src/assets/` | Static images/icons |
| `src/styles/` | Global CSS / Tailwind entrypoint |

Run locally: `npm install && npm run dev` (or via `docker compose up frontend`).
