#!/usr/bin/env python3
from __future__ import annotations

import shutil

TOOLS = ["pdftotext", "python", "python3"]

for tool in TOOLS:
    found = shutil.which(tool) is not None
    print(f"{tool}: {'OK' if found else 'MISSING'}")
