# Step 4 — CI/CD with GitHub Actions

## What is CI/CD?

Right now your workflow is: write code → `git push` → done. If you forgot to run `make lint` before pushing, broken code lands on GitHub. If the Docker build is broken, nobody knows until someone tries to run it.

**CI** (Continuous Integration) means: every time you push code, a robot automatically runs checks — linting, tests, building — and tells you if something is broken. It catches mistakes before they reach anyone else.

**CD** (Continuous Deployment) means: if all checks pass, the robot automatically deploys the new version. We'll skip CD for now and focus on CI — the automated checks.

---

## What is GitHub Actions?

GitHub has a built-in CI system called **Actions**. You write a YAML file that says "when someone pushes code, do these things." GitHub provides free servers (called **runners**) that execute your instructions. You don't need to set up or pay for anything.

The YAML file lives in your repo at `.github/workflows/ci.yml`. GitHub detects it automatically.

---

## Three new words

**Workflow** — the entire YAML file. It defines *when* to run and *what* to do. You can have multiple workflows (e.g., one for CI, one for deployment).

**Job** — a group of steps that run on the same machine. A workflow can have multiple jobs. Jobs run in parallel by default, or you can make them sequential.

**Step** — a single command or action within a job. Like one line in a recipe: "install dependencies", "run linter", "build Docker image".

---

## How it maps to what you already know

| What you do manually | GitHub Actions does it automatically |
|---|---|
| `make lint` | A step that runs flake8 + mypy |
| `make run` (test with a map) | A step that runs a quick simulation |
| `docker compose up --build` | A step that builds the Docker image |
| Looking at terminal output | GitHub shows ✅ or ❌ on your commit/PR |

---

## What our pipeline will do

```
Push to GitHub
    │
    ▼
┌─────────────────────────┐
│  Job 1: Lint & Test     │
│                         │
│  1. Checkout code       │  ← git clone your repo on the runner
│  2. Set up Python 3.12  │  ← install Python
│  3. Install deps        │  ← pip install -r requirements.txt
│  4. Run flake8          │  ← style checks
│  5. Run mypy            │  ← type checks
│  6. Run a simulation    │  ← quick smoke test
│                         │
└─────────┬───────────────┘
          │ (only if lint passes)
          ▼
┌─────────────────────────┐
│  Job 2: Docker Build    │
│                         │
│  1. Checkout code       │
│  2. Build Docker image  │  ← make sure it still builds
│                         │
└─────────────────────────┘
```

**Job 1** catches code quality issues. **Job 2** makes sure the Docker image isn't broken. Job 2 only runs if Job 1 passes — no point building a broken image.

---

## What you'll see on GitHub

After pushing, go to the **Actions** tab on your repo. You'll see the workflow running with a yellow dot (in progress), then either a green check (all passed) or a red X (something failed). Click on it to see the logs — exactly like your terminal output.

---

## Files we'll create

```
fly-in/
├── .github/
│   └── workflows/
│       └── ci.yml    ← NEW: the entire pipeline
└── ...
```

Just one file. That's the whole setup.

---

## Ready?

If everything above makes sense, say the word and I'll write the `ci.yml` file.
