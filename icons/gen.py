"""
Generate an SVG sprite from individual SVG files.

Reads every .svg file in the source directory, wraps each one
in a <symbol> element whose id is the filename without .svg,
and writes a single sprite file.
"""

import os
import re
import sys


def extract_viewbox(svg_text):
  """Return the viewBox value from an SVG root element."""
  match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_text)
  return match.group(1) if match else "0 0 1200 1200"


def extract_inner(svg_text):
  """Return the content between the <svg> and </svg> tags."""
  # Strip XML declaration if present.
  svg_text = re.sub(
    r'<\?xml[^?]*\?>\s*', '', svg_text
  )
  # Remove the outer <svg ...> and </svg> tags.
  svg_text = re.sub(
    r'<svg[^>]*>', '', svg_text, count=1
  )
  svg_text = re.sub(
    r'</svg>\s*$', '', svg_text, count=1
  )
  return svg_text.strip()


def build_sprite(src_dir, out_path):
  """Build an SVG sprite from all .svg files in src_dir."""
  files = sorted(
    f for f in os.listdir(src_dir)
    if f.lower().endswith('.svg')
  )
  if not files:
    print(f"No .svg files found in {src_dir}")
    sys.exit(1)

  symbols = []
  for filename in files:
    icon_id = filename[:-4]  # strip .svg
    filepath = os.path.join(src_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as fh:
      svg_text = fh.read()
    viewbox = extract_viewbox(svg_text)
    inner = extract_inner(svg_text)
    symbols.append(
      f'  <symbol id="{icon_id}" '
      f'viewBox="{viewbox}">\n'
      f'    {inner}\n'
      f'  </symbol>'
    )

  sprite = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' style="display: none;">\n'
    + '\n'.join(symbols)
    + '\n</svg>\n'
  )

  with open(out_path, 'w', encoding='utf-8') as fh:
    fh.write(sprite)
  print(f"Wrote {len(files)} symbols to {out_path}")


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print(
      "Usage: python generate_sprite.py"
      " <svg_dir> <output.svg>"
    )
    sys.exit(1)
  build_sprite(sys.argv[1], sys.argv[2])
