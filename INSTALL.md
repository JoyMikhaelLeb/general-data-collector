# Installation Guide

This guide helps you set up the General Data Collector project on your local machine.

## Prerequisites

- **Python 3.11+** (check with `python3 --version`)
- **pip** (included with Python)
- **Make** (usually pre-installed on Mac/Linux)
- **Docker** (optional, for containerized deployment)

## Quick Start

### Option 1: Using pip (Recommended for most users)

The project automatically uses `pip` if `uv` is not available:

```bash
# Clone the repository
git clone <your-repo-url>
cd general-data-collector

# Install dependencies for a specific crawler
cd crawlers/harmonic_ai
make install

# Run the crawler
python3 crawler.py
```

### Option 2: Install all crawlers at once

```bash
# From the project root
make install-all
```

This will install dependencies for all 22 crawlers using pip.

### Option 3: Using uv (Advanced - Faster)

If you want faster dependency installation, you can optionally install `uv`:

#### On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then run:
```bash
make install-all  # Will automatically use uv if available
```

## Running Crawlers

### Single Crawler

```bash
# Navigate to crawler directory
cd crawlers/harmonic_ai

# Run directly
python3 crawler.py

# Or use Make
make run
```

### Using Make from Project Root

```bash
# Run specific crawler
make run-harmonic_ai

# Test specific crawler
make test-harmonic_ai

# Install specific crawler
make install-harmonic_ai
```

### All Crawlers (Docker Compose)

```bash
# Build all images
docker-compose build

# Run all crawlers
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

## Verify Installation

Test that everything is working:

```bash
cd crawlers/harmonic_ai
python3 test_functional.py
```

You should see:
```
============================================================
✓ ALL TESTS PASSED!
============================================================
```

## Common Issues

### "uv: No such file or directory"

**Solution**: The Makefiles now automatically fall back to `pip`. Just run the command again:
```bash
make install
```

### "ModuleNotFoundError: No module named 'aiohttp'"

**Solution**: Install dependencies:
```bash
pip3 install aiohttp beautifulsoup4 lxml python-dotenv
```

### "Permission denied" errors

**Solution**: Use pip with --user flag:
```bash
pip3 install --user aiohttp beautifulsoup4 lxml python-dotenv
```

Or create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
make install
```

### Docker not found

**Solution**: Install Docker from https://docs.docker.com/get-docker/

Docker is optional - you can run all crawlers directly with Python.

## Project Structure

```
general-data-collector/
├── crawlers/              # 22 crawler modules
│   └── harmonic_ai/      # Example crawler
│       ├── crawler.py    # Main code
│       ├── Makefile      # Build commands
│       └── tests/        # Tests
├── Makefile              # Root orchestration
├── docker-compose.yml    # Multi-crawler deployment
└── README.md            # Main documentation
```

## Development Setup

For development work:

```bash
# Install with dev dependencies
cd crawlers/harmonic_ai
pip3 install pytest pytest-asyncio pytest-cov black ruff mypy

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

## Next Steps

1. Read [README.md](README.md) for project overview
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Browse individual crawler READMEs in `crawlers/*/README.md`
4. Review [ARCHITECTURE.md](crawlers/harmonic_ai/ARCHITECTURE.md) for technical details

## Getting Help

- Check individual crawler documentation: `crawlers/*/README.md`
- Review architecture docs: `crawlers/*/ARCHITECTURE.md`
- Run `make help` for available commands
- Open an issue on GitHub

## Quick Command Reference

```bash
# Project root commands
make list              # List all crawlers
make install-all       # Install all dependencies
make test-all         # Test all crawlers
make help             # Show all commands

# Individual crawler commands (from crawler directory)
make install          # Install dependencies
make run             # Run crawler
make test            # Run tests
make docker-build    # Build Docker image
make docker-run      # Run in Docker

# Docker Compose (from project root)
docker-compose up    # Start all crawlers
docker-compose down  # Stop all crawlers
docker-compose logs  # View logs
```

## Troubleshooting

If you encounter any issues:

1. Ensure Python 3.11+ is installed: `python3 --version`
2. Update pip: `pip3 install --upgrade pip`
3. Try with a virtual environment (see above)
4. Check if the port is available (for Docker)
5. Review error logs carefully

For more help, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide or open an issue.
