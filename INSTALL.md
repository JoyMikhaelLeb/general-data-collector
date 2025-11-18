# Installation Guide

This guide helps you set up the General Data Collector project on your local machine.

## Prerequisites

- **Python 3.11+** (check with `python3 --version`)
- **uv** (Fast Python package manager - required)
- **Make** (usually pre-installed on Mac/Linux)
- **Docker** (optional, for containerized deployment)

## Step 1: Install uv

The project uses **uv** for fast, reliable dependency management. Install it first:

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Add to PATH

After installation, add uv to your PATH:

```bash
# For zsh (macOS default)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation
```bash
uv --version
# Should output: uv 0.x.x
```

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd general-data-collector

# Install all crawler dependencies
make install-all
```

This will install dependencies for all 22 crawlers using uv (very fast!).

## Step 3: Run a Crawler

### Single Crawler

```bash
# Navigate to crawler directory
cd crawlers/harmonic_ai

# Run the crawler
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

## Running with Docker

If you prefer Docker (no uv needed in container):

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

## Common Issues

### "uv: command not found"

**Solution**: uv is not installed or not in PATH.

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add to PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.zshrc  # or ~/.bashrc
```

### "Unable to read current working directory"

**Solution**: macOS permission issue. Navigate away and back:
```bash
cd ~
cd general-data-collector
```

Or open a new terminal window.

### "ModuleNotFoundError" after installation

**Solution**: Re-run the install:
```bash
cd crawlers/harmonic_ai
make install
```

### Docker not found

**Solution**: Install Docker from https://docs.docker.com/get-docker/

Docker is optional - you can run all crawlers directly with Python + uv.

## Development Setup

For development work:

```bash
# Install specific crawler with dev dependencies
cd crawlers/harmonic_ai
make install

# Run tests
make test

# Format code
make format

# Run linting
make lint
```

## Why uv?

uv is a blazing-fast Python package installer and resolver, written in Rust:

- **10-100x faster** than pip
- **Reliable** dependency resolution
- **Compatible** with pip and PyPI
- **Lightweight** (~10MB)

Learn more at: https://github.com/astral-sh/uv

## Quick Command Reference

```bash
# Project root commands
make list              # List all crawlers
make install-all       # Install all dependencies (uses uv)
make test-all         # Test all crawlers
make help             # Show all commands

# Individual crawler commands (from crawler directory)
make install          # Install dependencies (uses uv)
make run             # Run crawler
make test            # Run tests
make docker-build    # Build Docker image
make docker-run      # Run in Docker

# Docker Compose (from project root)
docker-compose up    # Start all crawlers
docker-compose down  # Stop all crawlers
docker-compose logs  # View logs
```

## Alternative: Using Docker Only

If you don't want to install uv on your local machine, you can use Docker exclusively:

```bash
# Build a specific crawler image
cd crawlers/harmonic_ai
make docker-build

# Run in Docker
make docker-run

# Test in Docker
make docker-test
```

All dependencies are installed inside the container using uv.

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

## Troubleshooting

If you encounter any issues:

1. Ensure Python 3.11+ is installed: `python3 --version`
2. Ensure uv is installed: `uv --version`
3. Check uv is in PATH: `which uv`
4. Try opening a new terminal window
5. Review error logs carefully

For more help, see the [CONTRIBUTING.md](CONTRIBUTING.md) guide or open an issue.
