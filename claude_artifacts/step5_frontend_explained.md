# Step 5 — Frontend

## Progress so far

| Step | Status |
|---|---|
| 1. FastAPI basics | ✅ |
| 2. Wrap engine in API | ✅ |
| 3. Docker | ✅ |
| 4. CI/CD | ✅ |
| **5. Frontend** | ← you are here |

---

## What is "the frontend"?

Right now your simulation has two interfaces:
- **CLI** — `python fly_in.py map.txt` prints text to the terminal
- **Pygame** — `--visual` opens a desktop window with animated drones
- **API** — `POST /runs` returns JSON data

None of these let someone use fly-in from a browser. The **frontend** is a web page that:
1. Lets the user paste (or draw) a map
2. Sends it to your API
3. Shows the simulation results visually — animated drones moving through zones

It replaces the Pygame window with something that runs in any browser and can be shared with a URL.

---

## How it connects to what you already have

```
┌──────────────┐         HTTP          ┌──────────────┐
│   Browser    │  ───── POST /runs ──→ │   Your API   │
│  (frontend)  │  ←── JSON response ── │  (FastAPI)    │
│  HTML/CSS/JS │                       │  Python       │
└──────────────┘                       └──────────────┘
```

The frontend is **completely separate** from your Python code. It's just HTML, CSS, and JavaScript files that talk to your API the same way `curl` does — by sending HTTP requests. Your API doesn't know or care whether the request comes from curl, the `/docs` page, or your frontend.

---

## Three concepts mapped to Python

| Web concept | Python equivalent |
|---|---|
| **HTML** — structure of the page | Like defining classes and data structures |
| **CSS** — how it looks (colors, layout) | Like the Pygame renderer's visual config |
| **JavaScript** — logic and interactivity | Like your Python code — variables, functions, loops |

You write all three in the same project. The browser reads them and renders the page.

---

## What we'll build (version 1)

A single web page with:

1. **A text area** where you paste map file content (like you did with curl)
2. **A "Run" button** that sends the map to `POST /runs`
3. **A results panel** that shows the turn-by-turn movements
4. **An animated canvas** that draws zones as nodes, connections as edges, and animates drones moving through them turn by turn

It will look something like this:
```
┌─────────────────────────────────────────────┐
│  🛸 fly-in                                  │
├──────────────────┬──────────────────────────┤
│                  │                          │
│  Map Input       │   Simulation Canvas      │
│  ┌────────────┐  │   ┌──────────────────┐   │
│  │nb_drones: 2│  │   │  (start)──(a)    │   │
│  │start_hub:..│  │   │          │       │   │
│  │hub: a ...  │  │   │        (goal)    │   │
│  │end_hub:... │  │   │                  │   │
│  │connection:.│  │   │   D1 ●  D2 ●     │   │
│  └────────────┘  │   └──────────────────┘   │
│                  │                          │
│  [▶ Run]         │   Turn: 2/5  [⏮ ⏯ ⏭]    │
│                  │                          │
│  Results:        │                          │
│  Turn 1: D1-a    │                          │
│  Turn 2: D1-goal │                          │
│                  │                          │
└──────────────────┴──────────────────────────┘
```

---

## How we'll serve it

Two options:
- **Option A**: FastAPI serves the HTML files directly (simplest — one server does everything)
- **Option B**: Separate frontend dev server (more complex, better for bigger projects)

For now, **Option A** — we add a `static/` folder to your project and tell FastAPI to serve it. Zero extra setup.

---

## Files we'll create

```
fly-in/
├── static/
│   ├── index.html    ← the page structure
│   ├── style.css     ← how it looks
│   └── app.js        ← logic: send requests, animate canvas
├── api/
│   └── main.py       ← add static file serving (1 line)
└── ...
```

---

## Ready?

If the above makes sense, I'll build the frontend. It'll be a polished, dark-themed page with the animated canvas — not a bare-bones prototype.
