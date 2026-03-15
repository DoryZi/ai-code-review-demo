# CLAUDE.md

CLI todo application backed by SQLite. Python 3.14, no external dependencies.

## Commands

```bash
source venv/bin/activate

python todo.py add Buy groceries
python todo.py list
python todo.py list -a        # include completed
python todo.py done <id>      # toggle completion
python todo.py delete <id>
```

## Structure

- **db.py** — Database layer. All SQLite operations (CRUD) against a `todos.db` file stored in the project root. Uses `sqlite3.Row` for dict-like row access.
- **todo.py** — CLI entry point. Uses `argparse` with subcommands (`add`, `list`, `done`, `delete`). Calls `init_db()` on every invocation to ensure the table exists.

## Docstring Standard

All functions must have detailed docstrings covering:
- Summary of what the function does.
- **Args:** each parameter with name, type, and meaning.
- **Returns:** type and description of the return value.
- **Raises:** any exceptions the function may raise.

## Code Examples

### Do

```python
def generate_description(title):
    """Use Claude API to auto-generate a todo description.

    Args:
        title (str): The todo item title to generate
            a description for.

    Returns:
        str: A 1-2 sentence actionable description.

    Raises:
        anthropic.APIError: If the API call fails.
    """
```

### Don't

```python
def generate_description(title):
    """Generate a description."""
```

## Infrastructure

For deployment, debugging, or any infrastructure work, read these files first:
- **infra/CLAUDE.md** — Commands and structure for infra work.
- **infra/Infra.md** — Architecture diagrams and component relationships.

## Boundaries
- never commit secrets, api keys or sensitive data.
- do not delete files
- keep files between 200-800 chars, break files into smaller files. 
