#!/usr/bin/env python3
"""
Update all crawler Makefiles to support both uv and pip.
"""

from pathlib import Path

# The new install target
NEW_INSTALL = '''install: ## Install dependencies (uses uv if available, otherwise pip)
\t@echo "Installing dependencies..."
\t@if command -v uv >/dev/null 2>&1; then \\
\t\techo "Using uv..."; \\
\t\tuv pip install --system aiohttp beautifulsoup4 lxml python-dotenv pytest pytest-asyncio pytest-cov black ruff mypy 2>/dev/null || true; \\
\telse \\
\t\techo "Using pip..."; \\
\t\tpip3 install aiohttp beautifulsoup4 lxml python-dotenv pytest pytest-asyncio pytest-cov black ruff mypy 2>/dev/null || true; \\
\tfi
\t@echo "✓ Dependencies installed"'''

def update_makefile(makefile_path):
    """Update a single Makefile."""
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
            new_lines.append(NEW_INSTALL)
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
    """Update all Makefiles."""
    crawlers_dir = Path('crawlers')

    count = 0
    for crawler_dir in sorted(crawlers_dir.iterdir()):
        if crawler_dir.is_dir():
            makefile = crawler_dir / 'Makefile'
            if makefile.exists():
                update_makefile(makefile)
                count += 1

    print(f"\n✓ Updated {count} Makefiles")

if __name__ == '__main__':
    main()
