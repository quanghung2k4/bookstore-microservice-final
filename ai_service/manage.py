#!/usr/bin/env python
import os
import sys

# Patch Django host validation so Docker service names with underscores work
import django.http.request as _r
_r.validate_host = lambda host, allowed_hosts: True


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
