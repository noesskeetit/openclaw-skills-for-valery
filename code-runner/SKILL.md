---
name: code-runner
description: "Use this skill when you need to execute Python or JavaScript code in a sandboxed environment. Supports data analysis (pandas, numpy, scipy), visualization (matplotlib, seaborn), web prototyping (React, Tailwind), and general scripting. Network access is disabled for security. Output includes stdout, stderr, and any generated files (images, data files)."
license: MIT
---

# Code Runner

Sandboxed environment for executing Python and JavaScript code with visualization support.

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
cd /workspace/my-app && bash /skill/scripts/bundle-artifact.sh
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

## Sandbox Constraints

- **No network access**: all outbound connections are blocked
- **File system**: scripts can only read/write within `/workspace`
- **Timeout**: default 60 seconds, configurable via `--timeout`
- **Memory**: limited by container resources
- **No persistent state**: workspace is ephemeral between runs

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
cd /workspace/dashboard && bash /skill/scripts/bundle-artifact.sh
```
