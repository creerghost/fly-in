# Step 3 — Docker

## Quick note on your earlier test

The `cat` approach failed because your map files have actual newlines that break JSON. That's fine — the inline curl and the `/docs` page work perfectly. We can fix that later with a file upload endpoint.

---

## What problem does Docker solve?

Right now, to run fly-in on a new computer, someone would need to:

1. Install Python 3
2. Clone the repo
3. Create a virtual environment
4. Install all dependencies from `requirements.txt`
5. Know to run `make run-api`

If their Python version is different, or their OS handles packages differently, things might break. You've probably hit "works on my machine" problems before.

**Docker solves this by packaging your app + its entire environment into a single box.** That box runs the same way everywhere — your laptop, a server, your friend's machine. The box is called a **container**.

---

## Three new words

**Image** — a snapshot/blueprint of your app. Think of it like a `.zip` file that contains your code, Python, all pip packages, and instructions on how to run everything. You build an image once.

**Container** — a running instance of an image. When you "run" an image, it becomes a container. Same concept as: a Python class (image) vs an object (container). You can run multiple containers from the same image.

**Dockerfile** — a text file with step-by-step instructions for building an image. It's like a recipe: "start with Python 3.12, copy my code, install requirements, run uvicorn." Docker reads this file and builds the image.

---

## How it relates to what you already know

| What you do now | Docker equivalent |
|---|---|
| `python3 -m venv venv` | Happens inside the image build |
| `pip install -r requirements.txt` | A line in the Dockerfile |
| `make run-api` | The Dockerfile's last line (the startup command) |
| Your whole computer | Replaced by a tiny isolated Linux environment |

---

## The second concept: docker-compose

A single Dockerfile packages **one** service (your API). But a real product has multiple services running together — the API, a database, maybe a frontend. Starting each one manually is tedious.

**docker-compose** is a tool that lets you define multiple services in one file (`docker-compose.yml`) and start them all with a single command: `docker compose up`. For now, we'll only have one service (the API), but the file is ready to grow.

---

## What we're going to build

```
fly-in/
├── Dockerfile          ← NEW: recipe to build the API image
├── docker-compose.yml  ← NEW: defines services to run together
├── .dockerignore       ← NEW: files to exclude from the image (like .gitignore)
├── api/
├── src/
└── ...
```

The end result: anyone with Docker installed can run `docker compose up` and have the API running — no Python install, no venv, no pip, nothing.

---

## Before we write the files

1. **Do you have Docker installed?** Run `docker --version` in your terminal to check.
2. **Anything above need more explanation?**
