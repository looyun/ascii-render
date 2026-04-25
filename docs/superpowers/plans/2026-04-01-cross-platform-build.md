# Cross-Platform Binary Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add GitHub Actions workflow to build cross-platform (Linux/macOS/Windows) CLI binaries using PyInstaller with --onefile.

**Architecture:** PyInstaller takes the CLI entry point and bundles Python interpreter + dependencies into a single executable per platform.

**Tech Stack:** PyInstaller, GitHub Actions (ubuntu-latest, macos-latest, windows-latest)

---

## File Structure

- Modify: `pyproject.toml` - add PyInstaller as build dependency
- Create: `.github/workflows/build.yml` - GitHub Actions workflow

---

### Task 1: Add PyInstaller Configuration

- [ ] **Step 1: Update pyproject.toml to add PyInstaller**

```toml
[project.optional-dependencies]
dev = ["pytest>=7.0.0", "pytest-cov>=4.0.0"]
build = ["pyinstaller>=6.0.0"]
```

- [ ] **Step 2: Commit changes**

```bash
git add pyproject.toml
git commit -m "chore: add pyinstaller as build dependency"
```

---

### Task 2: Create GitHub Actions Workflow

- [ ] **Step 1: Create .github/workflows/build.yml**

```yaml
name: Build Binaries

on:
  release:
    types: [published]
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact: ascii-render-linux
            target: manylinux2014_x86_64
          - os: macos-latest
            artifact: ascii-render-macos
            target: macosx-x86_64
          - os: windows-latest
            artifact: ascii-render-windows.exe
            target: win64

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e ".[build]"

      - name: Build with PyInstaller
        run: |
          pyinstaller --onefile --name ${{ matrix.artifact }} \
            --add-data "ascii_render:ascii_render" \
            --hidden-import pillow \
            --hidden-import numpy \
            --hidden-import cv2 \
            --hidden-import click \
            ascii_render/cli.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact }}
          path: dist/${{ matrix.artifact }}*
```

- [ ] **Step 2: Commit the workflow**

```bash
mkdir -p .github/workflows
git add .github/workflows/build.yml
git commit -m "ci: add cross-platform build workflow"
```

---

### Task 3: Test Build Locally

- [ ] **Step 1: Test PyInstaller build on Linux**

```bash
# Activate venv
source venv/bin/activate

# Install pyinstaller
pip install pyinstaller

# Build
pyinstaller --onefile --name ascii-render \
  --collect-all ascii_render \
  ascii_render/cli.py

# Verify
ls -la dist/ascii-render
./dist/ascii-render --help
```

- [ ] **Step 2: Clean up build artifacts**

```bash
rm -rf build dist *.spec
```

---

### Task 4: Verify Workflow

- [ ] **Step 1: Push to GitHub and verify workflow appears**

```bash
git push origin main
# Check Actions tab on GitHub
```

---

## Summary

After completion:
- `pyproject.toml` includes `pyinstaller` in build dependencies
- `.github/workflows/build.yml` triggers on release/workflow_dispatch
- Builds for Linux/macOS/Windows producing `ascii-render-*` artifacts
- Locally testable with `pyinstaller --onefile` command

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-01-cross-platform-build.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**