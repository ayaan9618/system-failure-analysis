# LogLens

LogLens is a terminal-based log analysis tool for detecting failure windows, estimating downtime, analyzing error patterns, inferring likely root causes, and generating reports and charts from infrastructure and application logs.

## Installation Options

You can use LogLens in two main ways:

1. Run from the source code after cloning the repository
2. Use the Windows `.exe` build

---

## Option 1: Install From Source

### Step 1: Clone the repository

```bash
git clone <your-repository-url>
cd system-failure-analysis
```

### Step 2: Install and run on Windows

Quick install:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\install_windows.ps1
```

Manual install:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install .
```

Run:

```powershell
loglens
```

### Step 2: Install and run on Linux

Quick install:

```bash
chmod +x packaging/install_linux.sh
./packaging/install_linux.sh
```

Manual install:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

Run:

```bash
loglens
```

---

## Option 2: Use the Windows Executable

If you already have the built executable, you do not need to install Python or run `pip install .`.

Run:

```powershell
.\packaging\dist\loglens.exe
```

If the `.exe` has not been built yet, build it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build_windows_exe.ps1
```

The executable will be created at:

```text
packaging/dist/loglens.exe
```

---

## Direct Development Run

If you only want to test the project quickly without installing it as a package:

Windows:

```powershell
python main.py
```

Linux:

```bash
python3 main.py
```

---

## How Package Installation Works

When you run:

```bash
pip install .
```

Python reads [`pyproject.toml`](./pyproject.toml), installs the required dependencies, and creates the `loglens` command.

That command is mapped to:

```text
loglens = main:main
```

So when you type:

```bash
loglens
```

Python runs the `main()` function from [`main.py`](./main.py).

---

## Example Commands

```bash
loglens
loglens --input logs/cloud_failure_log.json
loglens logs/cloud_failure_log.xml --skip-pdf
loglens --input logs/reader.deployment.log --output-dir output_cli
```

---

## Project Layout

- application source: [`main.py`](./main.py), [`modules`](./modules), [`logs`](./logs)
- packaging and installer files: [`packaging`](./packaging)
- build artifacts: [`packaging/build`](./packaging/build), [`packaging/dist`](./packaging/dist)
- temporary files: [`packaging/temp`](./packaging/temp)
- Python package metadata: [`pyproject.toml`](./pyproject.toml)
