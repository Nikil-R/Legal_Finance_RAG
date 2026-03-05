# Backup and Restore

## Backup
- Command: `python scripts/backup_chroma.py --source ./chroma_db --target-dir ./backups`
- Frequency: at least daily in production
- Retention: keep 14 daily and 8 weekly backups

## Restore
1. Stop API service.
2. Extract backup archive into `CHROMA_PERSIST_DIR`.
3. Start API service.
4. Validate `/health` and run a smoke query.

## Validation
- Verify `chroma.sqlite3` exists after restore.
- Run `GET /api/v1/documents/stats` and compare expected counts.
