---
name: code-runner
description: "Use this skill when you need to execute Python or JavaScript code. Supports data analysis (pandas, numpy, scipy), visualization (matplotlib, seaborn), web prototyping (React, Tailwind), and general scripting. Output includes stdout, stderr, and any generated files (images, data files). Isolation (network, filesystem) is the responsibility of the runtime environment."
license: MIT
---

# Code Runner

## Requirements

- **System:** `python3`, `node`
- **Python:** see `requirements.txt` (pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, sympy, Pillow, openpyxl, beautifulsoup4, Flask)
- **npm (global, optional):** `typescript`, `react`, `react-dom` — only for React artifact scaffolding

Execute Python and JavaScript code with visualization support. Captures stdout/stderr, tracks newly-created files, and enforces a per-invocation timeout.

## Available Packages

### Python

Pre-installed packages:

- **Data analysis**: pandas, numpy, scipy, scikit-learn, openpyxl
- **Visualization**: matplotlib, seaborn, Pillow
- **Math/symbolic**: sympy
- **Web scraping/parsing**: beautifulsoup4
- **Web framework**: Flask
- **General**: standard library (json, csv, os, sys, re, etc.)

### Node.js

Pre-installed globally:

- **TypeScript**: tsc compiler
- **React**: react, react-dom
- **Bundling**: available via init-artifact.sh / bundle-artifact.sh scripts

## Usage

### Running Python code

From a file:

```bash
python3 scripts/run_python.py /workspace/script.py
```

Inline code:

```bash
python3 scripts/run_python.py -c "import pandas as pd; print(pd.__version__)"
```

With custom timeout (default 60s):

```bash
python3 scripts/run_python.py --timeout 120 /workspace/heavy_computation.py
```

### Running JavaScript code

From a file:

```bash
python3 scripts/run_node.py /workspace/script.js
```

Inline code:

```bash
python3 scripts/run_node.py -c "console.log(JSON.stringify({hello: 'world'}, null, 2))"
```

### React Project Scaffolding

Initialize a full React + Tailwind + shadcn/ui project:

```bash
bash scripts/init-artifact.sh my-app
```

Bundle a React project into a single HTML file:

```bash
cd /workspace/my-app && bash scripts/bundle-artifact.sh
```

## Output Format

All runners output JSON to stdout:

```json
{
  "stdout": "Hello, world!\n",
  "stderr": "",
  "exit_code": 0,
  "new_files": ["/workspace/output.png", "/workspace/results.csv"]
}
```

Fields:
- `stdout` -- captured standard output from the script
- `stderr` -- captured standard error from the script
- `exit_code` -- process exit code (0 = success, -1 = timeout)
- `new_files` -- list of files created during execution in the workspace

## Execution Environment

This skill executes code in the same process environment as its caller. It does **not** provide isolation by itself: network and filesystem access are whatever the host grants. Isolation (network blocking, filesystem restrictions, memory limits) is the responsibility of the runtime environment (Docker, OpenClaw sandbox, firejail, etc.).

- **Timeout**: default 60 seconds, configurable via `--timeout`. Enforced via `subprocess.run(timeout=...)` — on timeout the child process is killed and `exit_code` is `-1`.
- **Working directory**: scripts run with `cwd` set to `WORKSPACE` (see Configuration below).
- **new_files tracking**: the runner diffs the workspace before/after execution and reports newly-created regular files (directories excluded).

## Configuration

- `WORKSPACE` environment variable — path to the working directory used as `cwd` and scanned for new files. Default: `/workspace`.
- The runners create the workspace directory if it does not already exist (`os.makedirs(..., exist_ok=True)`).

## Examples

### Data Analysis with Chart

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.DataFrame({
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'revenue': [12000, 15000, 13500, 17000, 19500],
    'costs': [8000, 9500, 8800, 10200, 11000]
})

data['profit'] = data['revenue'] - data['costs']

fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(data['month']))
ax.bar([i - 0.2 for i in x], data['revenue'], 0.4, label='Revenue', color='#2196F3')
ax.bar([i + 0.2 for i in x], data['costs'], 0.4, label='Costs', color='#FF5722')
ax.plot(x, data['profit'], 'go-', label='Profit', linewidth=2)
ax.set_xticks(x)
ax.set_xticklabels(data['month'])
ax.set_ylabel('USD')
ax.set_title('Monthly Financial Overview')
ax.legend()
plt.tight_layout()
plt.savefig('/workspace/financial_chart.png', dpi=150)
print(data.to_string(index=False))
```

### React Component Generation

```bash
bash scripts/init-artifact.sh dashboard
# Edit src/App.tsx with your component code
# Then bundle:
cd /workspace/dashboard && bash scripts/bundle-artifact.sh
```
