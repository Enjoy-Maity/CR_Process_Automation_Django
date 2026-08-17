from .replica_sync import async_sync_master_to_replica


def deactivate_record(queryset, db_alias='default'):
    """
    Deactivates a record via .update() and manually
    triggers replica sync since .update() bypasses signals.
    """
    updated_count = queryset.using(db_alias).update(is_active=False)
    if updated_count > 0:
        async_sync_master_to_replica()
    return updated_count

    