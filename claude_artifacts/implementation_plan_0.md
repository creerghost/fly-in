# Feature Plan: Map Selector + Database + Map Editor

## Build Order

These features depend on each other, so we build them in this order:

```
1. Map Selector     ← quick win, 30 min
2. Database         ← foundation for everything persistent
3. Map Editor       ← builds on database (save created maps)
```

---

## Feature 1: Map Selector (Pick from Folder)

A dropdown in the left panel that lists all maps from your `maps/` directory, grouped by difficulty.

### API Changes

#### [MODIFY] [main.py](file:///home/vlnikola/fly-in/api/main.py)

New endpoint:
```
GET /maps          → list all maps with their category
GET /maps/{path}   → return the content of a specific map file
```

Response example:
```json
{
  "maps": [
    {"category": "easy", "name": "00_minimal.txt", "path": "easy/00_minimal.txt"},
    {"category": "easy", "name": "01_linear_path.txt", "path": "easy/01_linear_path.txt"},
    {"category": "hard", "name": "01_maze_nightmare.txt", "path": "hard/01_maze_nightmare.txt"}
  ]
}
```

### Frontend Changes

#### [MODIFY] [index.html](file:///home/vlnikola/fly-in/static/index.html)
- Add a `<select>` dropdown above the textarea
- Group options by category with `<optgroup>`

#### [MODIFY] [app.js](file:///home/vlnikola/fly-in/static/app.js)
- On page load: `fetch('/maps')` and populate the dropdown
- On selection change: `fetch('/maps/{path}')` and fill the textarea

---

## Feature 2: PostgreSQL Database

Store maps and simulation runs persistently. This replaces the file-based map storage and enables saving user-created maps.

### New Words

- **PostgreSQL** — a database (like a spreadsheet that programs can query). Stores data in tables with rows and columns.
- **SQLAlchemy** — a Python library for talking to databases. You write Python classes, it generates SQL queries.
- **Alembic** — handles database migrations (adding/changing tables without losing data).
- **ORM** — Object-Relational Mapping. Instead of writing SQL, you work with Python objects.

### Database Schema

```
┌──────────────────┐       ┌──────────────────────┐
│  maps             │       │  runs                 │
├──────────────────┤       ├──────────────────────┤
│  id (UUID, PK)   │──┐    │  id (UUID, PK)        │
│  name (str)      │  │    │  map_id (FK → maps)   │
│  category (str)  │  └───→│  status (str)         │
│  content (text)  │       │  nb_drones (int)      │
│  created_at      │       │  turns_total (int)    │
│  updated_at      │       │  result_json (JSON)   │
└──────────────────┘       │  created_at           │
                           └──────────────────────┘
```

### New Files

#### [NEW] api/database.py
- SQLAlchemy engine setup, session factory
- Reads `DATABASE_URL` from environment variable

#### [NEW] api/models.py
- `Map` and `Run` SQLAlchemy models (Python classes that map to database tables)

#### [NEW] api/schemas.py
- Pydantic models for API request/response validation

### Modified Files

#### [MODIFY] api/main.py
- New CRUD endpoints for maps:
  - `POST /api/maps` — save a new map
  - `GET /api/maps` — list all maps (from DB + from files)
  - `GET /api/maps/{id}` — get a single map
  - `DELETE /api/maps/{id}` — delete a map
- New endpoints for run history:
  - `GET /api/runs` — list past runs
  - `GET /api/runs/{id}` — get a past run with results
- `POST /runs` now also saves the run to the database

#### [MODIFY] docker-compose.yml
- Add PostgreSQL service
- Add volume for data persistence
- Set `DATABASE_URL` environment variable

#### [MODIFY] requirements.txt
- Add `sqlalchemy`, `asyncpg`, `alembic`

### Docker Compose Update

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://flyin:flyin@db:5432/flyin
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=flyin
      - POSTGRES_PASSWORD=flyin
      - POSTGRES_DB=flyin
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

---

## Feature 3: Map Editor

A visual editor on the canvas where you can click to place zones and draw connections.

### How It Works

1. **Editor Mode toggle** — a button switches between "Simulate" and "Edit" modes
2. In edit mode:
   - **Click empty space** → place a new zone (opens a small form for name, type)
   - **Click a zone** → select it (shows properties panel to edit name, type, max_drones)
   - **Drag from zone to zone** → create a connection
   - **Right-click** → delete zone or connection
   - **Drag a zone** → move it
3. **Export** → generates map file text and fills the textarea
4. **Save** → stores the map to the database via `POST /api/maps`

### Frontend Changes

#### [MODIFY] index.html
- Add "Edit / Simulate" mode toggle button
- Add zone properties panel (appears when a zone is selected)

#### [MODIFY] app.js
- Add editor state management (selected zone, drag state, mode)
- Add mouse event handlers for click, drag, right-click on canvas
- Add zone/connection creation/deletion logic
- Add `exportToMapText()` function that generates the `.txt` format
- Add `saveMap()` function that POSTs to the API

#### [MODIFY] style.css
- Style the editor controls, properties panel, mode toggle

---

## Verification Plan

### Feature 1 (Map Selector)
- Select a map from dropdown → textarea fills → Run → simulation works
- All 11 maps appear in the dropdown, grouped by difficulty

### Feature 2 (Database)
- `docker compose up` starts both API and PostgreSQL
- Save a map via API → retrieve it → matches
- Run a simulation → check it appears in run history

### Feature 3 (Map Editor)
- Create a map visually → export → run simulation → correct output
- Save map to database → reload page → map still there

---

## Open Questions

> [!IMPORTANT]
> 1. **Should I build all three now, or one at a time?** Feature 1 is fast (~30 min). Features 2 and 3 are bigger.
> 2. **For the database, do you want user accounts/auth?** Or just anonymous map/run storage for now?
> 3. **For the map editor, is right-click to delete OK?** Or would you prefer a delete button/mode?
