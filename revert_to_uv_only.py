#!/usr/bin/env python3
"""
Revert all crawler Makefiles to use uv only (as originally designed).
"""

from pathlib import Path

# The uv-only install target
UV_ONLY_INSTALL = '''install: ## Install dependencies using uv
\t@echo "Installing dependencies with uv..."
\tuv pip install --system aiohttp beautifulsoup4 lxml python-dotenv pytest pytest-asyncio pytest-cov black ruff mypy
\t@echo "✓ Dependencies installed"'''

def update_makefile(makefile_path):
    """Update a single Makefile to use uv only."""
    with open(makefile_path, 'r') as f:
        content = f.read()

    # Find and replace the install target
    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is the start of the install target
        if line.startswith('install: ##'):
            # Skip the old install lines until we find the next target or empty line after commands
            new_lines.append(UV_ONLY_INSTALL)
            i += 1

            # Skip old install content
            while i < len(lines):
                if lines[i].startswith('\t'):
                    i += 1
                else:
                    break
        else:
            new_lines.append(line)
            i += 1

    # Write back
    with open(makefile_path, 'w') as f:
        f.write('\n'.join(new_lines))

    print(f"✓ Updated {makefile_path}")

def main():
    """Update all Makefiles to uv-only."""
    crawlers_dir = Path('crawlers')

    count = 0
    for crawler_dir in sorted(crawlers_dir.iterdir()):
        if crawler_dir.is_dir():
            makefile = crawler_dir / 'Makefile'
            if makefile.exists():
                update_makefile(makefile)
                count += 1

    print(f"\n✓ Updated {count} Makefiles to use uv only")

if __name__ == '__main__':
    main()
