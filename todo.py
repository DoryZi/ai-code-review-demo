#!/usr/bin/env python3
"""Simple CLI Todo app backed by SQLite."""

import argparse
import sys
from db import init_db, add_todo, list_todos, toggle_todo, delete_todo, search_todos
from utils import generate_description


def cmd_add(args):
    title = " ".join(args.title)
    if not title.strip():
        print("Error: title cannot be empty.")
        sys.exit(1)
    add_todo(title)
    desc = generate_description(title)
    print(f"Added: {title}")
    print(f"Description: {desc}")


def cmd_list(args):
    todos = list_todos(show_all=args.all)
    if not todos:
        print("No todos found.")
        return
    for t in todos:
        status = "x" if t["completed"] else " "
        print(f"  [{status}] {t['id']}: {t['title']}")


def cmd_done(args):
    toggle_todo(args.id)
    print(f"Toggled todo #{args.id}")


def cmd_delete(args):
    delete_todo(args.id)
    print(f"Deleted todo #{args.id}")


def cmd_search(args):
    """Handle the search subcommand.

    Args:
        args (argparse.Namespace): Parsed arguments with query list.

    Returns:
        None
    """
    query = " ".join(args.query)
    results = search_todos(query)
    if not results:
        print("No todos found.")
        return
    for t in results:
        status = "x" if t["completed"] else " "
        print(f"  [{status}] {t['id']}: {t['title']}")


def main():
    init_db()

    parser = argparse.ArgumentParser(description="Simple Todo App")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new todo")
    p_add.add_argument("title", nargs="+", help="Todo title")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List todos")
    p_list.add_argument("-a", "--all", action="store_true", help="Show completed too")
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = sub.add_parser("done", help="Toggle a todo's completed status")
    p_done.add_argument("id", type=int, help="Todo ID")
    p_done.set_defaults(func=cmd_done)

    # search
    p_search = sub.add_parser("search", help="Search todos by title")
    p_search.add_argument("query", nargs="+", help="Search query")
    p_search.set_defaults(func=cmd_search)

    # delete
    p_del = sub.add_parser("delete", help="Delete a todo")
    p_del.add_argument("id", type=int, help="Todo ID")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
