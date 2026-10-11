"""Copy every row from a SQLite career-platform database into an empty target database.

Usage: TARGET_DATABASE_URL=postgresql://... uv run python -m scripts.copy_sqlite_to_postgres path/to/source.db
"""
from __future__ import annotations
import os
import sys
from sqlalchemy import create_engine, func, select, text
from app.config import normalize_database_url
from app.db import Base, connect_args_for
import app.models  # noqa: F401  (registers the tables on Base.metadata)


def _count(conn, table) -> int:
    return conn.execute(select(func.count()).select_from(table)).scalar_one()


def copy_database(source_url: str, target_url: str) -> dict[str, int]:
    target_url = normalize_database_url(target_url)
    source = create_engine(source_url, connect_args=connect_args_for(source_url))
    target = create_engine(target_url, connect_args=connect_args_for(target_url))
    Base.metadata.create_all(bind=target)
    tables = Base.metadata.sorted_tables  # parents before children
    counts: dict[str, int] = {}
    with source.connect() as src, target.begin() as dst:
        occupied = [t.name for t in tables if _count(dst, t)]
        if occupied:
            raise SystemExit(f"Target already has rows in: {', '.join(occupied)}. Nothing copied.")
        for table in tables:
            rows = [dict(row._mapping) for row in src.execute(select(table))]
            if rows:
                dst.execute(table.insert(), rows)
            counts[table.name] = len(rows)
        if dst.dialect.name == 'postgresql':
            # Rows arrived with explicit ids, so move each sequence past the highest one.
            for table in tables:
                if 'id' in table.c:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                        f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table.name}"
                    ))
    with target.connect() as dst:
        mismatched = {t.name for t in tables if _count(dst, t) != counts[t.name]}
    if mismatched:
        raise SystemExit(f"Row counts differ after copy: {sorted(mismatched)}")
    return counts


if __name__ == '__main__':
    if len(sys.argv) != 2 or 'TARGET_DATABASE_URL' not in os.environ:
        raise SystemExit(__doc__)
    for name, n in copy_database(f'sqlite:///{sys.argv[1]}', os.environ['TARGET_DATABASE_URL']).items():
        print(f'{name}: {n}')
