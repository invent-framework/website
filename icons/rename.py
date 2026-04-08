"""Rename SVG files: strip 'noun-' prefix and trailing '-digits'."""

import os
import re

for name in os.listdir("."):
    print(name)
    if not name.endswith(".svg"):
        continue
    new = re.sub(r"^noun-", "", name)
    new = re.sub(r"-\d+\.svg$", ".svg", new)
    if new != name:
        os.rename(name, new)
        print(f"{name} -> {new}")
