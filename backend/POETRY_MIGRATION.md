# Poetry Migration Guide

This document explains the migration from pip + requirements.txt to Poetry for dependency management.

## What Changed

### Before (pip + requirements.txt)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### After (Poetry)
```bash
poetry install
```

## Why Poetry?

1. **Better Dependency Resolution**: Poetry resolves conflicts automatically
2. **Lock File**: `poetry.lock` ensures reproducible builds
3. **Separation of Concerns**: Production vs dev dependencies clearly separated
4. **Modern Tooling**: Industry standard for Python projects
5. **Simplified Workflow**: No need to manually manage virtual environments

## Migration Steps (Already Done)

✅ Created `pyproject.toml` with all dependencies from `requirements.txt`
✅ Configured Serverless Framework to use Poetry (`usePoetry: true`)
✅ Updated package.json scripts to use `poetry run`
✅ Updated all documentation (README.md, CLAUDE.md)
✅ Installed dependencies with Poetry

## New Workflow

### Installation

```bash
# Install all dependencies (production + dev)
poetry install

# Install only production dependencies
poetry install --only main
```

### Running Commands

All Python commands should now be run with `poetry run`:

```bash
# Run tests
poetry run pytest

# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type check
poetry run mypy src/
```

Or use npm scripts:

```bash
npm run test
npm run format
npm run lint
npm run type-check
```

### Managing Dependencies

#### Add a new production dependency
```bash
poetry add package-name

# With version constraint
poetry add "package-name>=1.0.0,<2.0.0"
```

#### Add a new dev dependency
```bash
poetry add --group dev package-name
```

#### Update dependencies
```bash
# Update all dependencies
poetry update

# Update specific package
poetry update package-name
```

#### Remove a dependency
```bash
poetry remove package-name
```

### Show installed packages
```bash
# Show all packages
poetry show

# Show dependency tree
poetry show --tree

# Show outdated packages
poetry show --outdated
```

## Important Files

### pyproject.toml
Main configuration file containing:
- Project metadata
- Dependencies (production and dev)
- Tool configurations (black, mypy, pytest, pylint)

**Should be committed to git**: ✅ Yes

### poetry.lock
Lock file with exact versions of all dependencies and their subdependencies.

**Should be committed to git**: ✅ Yes (ensures reproducible builds)

### Virtual Environment
Poetry creates and manages the virtual environment automatically in:
- Linux/Mac: `~/.cache/pypoetry/virtualenvs/`
- Windows: `%LOCALAPPDATA%\pypoetry\Cache\virtualenvs\`

**Should be committed to git**: ❌ No (automatically ignored)

## Serverless Integration

The `serverless-python-requirements` plugin automatically detects Poetry:

```yaml
custom:
  pythonRequirements:
    dockerizePip: true
    layer: true
    usePoetry: true  # ← Enables Poetry support
    poetryInclude:
      - packages
    slim: true
    strip: false
```

When you run `serverless deploy`, it will:
1. Use `poetry export` to generate requirements.txt
2. Install dependencies using Docker
3. Package them as a Lambda layer

## Common Commands Reference

| Task | Old Command | New Command |
|------|-------------|-------------|
| Install dependencies | `pip install -r requirements.txt` | `poetry install` |
| Add dependency | `echo "package" >> requirements.txt && pip install package` | `poetry add package` |
| Add dev dependency | Manual editing | `poetry add --group dev package` |
| Update dependencies | `pip install -U package` | `poetry update package` |
| Run tests | `pytest` | `poetry run pytest` or `npm run test` |
| Format code | `black src/` | `poetry run black src/` or `npm run format` |
| Activate venv | `source venv/bin/activate` | Not needed (use `poetry run` or `poetry shell`) |

## Troubleshooting

### Issue: Command not found
**Solution**: Make sure you're using `poetry run` before the command:
```bash
poetry run pytest  # Not just: pytest
```

### Issue: Dependencies not installing
**Solution**: Delete poetry.lock and reinstall:
```bash
rm poetry.lock
poetry install
```

### Issue: Serverless deployment fails
**Solution**: Ensure Poetry plugin is configured in serverless.yml:
```yaml
custom:
  pythonRequirements:
    usePoetry: true
```

### Issue: Want to use old requirements.txt
**Solution**: Poetry can export to requirements.txt:
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Migration Checklist for Team Members

When pulling this change:

- [ ] Install Poetry if not already installed: `curl -sSL https://install.python-poetry.org | python3 -`
- [ ] Navigate to backend directory: `cd backend`
- [ ] Delete old virtual environment if it exists: `rm -rf venv/`
- [ ] Install dependencies with Poetry: `poetry install`
- [ ] Verify installation: `poetry run python -c "import boto3; print('Success!')"`
- [ ] Test serverless offline: `npm run dev`

## Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Basic Usage](https://python-poetry.org/docs/basic-usage/)
- [Serverless Python Requirements Plugin](https://www.serverless.com/plugins/serverless-python-requirements)

## Questions?

If you encounter any issues with the Poetry migration, please:
1. Check this migration guide
2. Review the [Poetry documentation](https://python-poetry.org/docs/)
3. Create an issue in the repository

---

**Migration Date**: November 15, 2025
**Migration Reason**: Dependency conflicts with requirements.txt
