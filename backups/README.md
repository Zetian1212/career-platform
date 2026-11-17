# Database backups

`career-platform-db-20261117.sql`: plain-SQL `pg_dump` (PostgreSQL 18.6, `--no-owner --no-privileges`) of the production database, taken 2026-11-17 from RDS `career-platform-db-r1`. That instance was point-in-time restored from the original `career-platform-db`, which became permanently unreadable after the AWS account suspension (2026-11-07 to 2026-11-17) and was then deleted. All 9 tables hash identical to the 2026-11-05 Railway final dump.

Every row is published content already shown on the site; there are no credentials in it.

Restore into an empty database:

```sh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f backups/career-platform-db-20261117.sql
```
