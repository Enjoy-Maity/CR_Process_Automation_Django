import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MasterCRDatabase, CRWiseStatus
from .utils.replica_sync import async_sync_master_to_replica

logger = logging.getLogger(__name__)


def _trigger_replica_sync(sender, **kwargs):
    """
    Generic handler: triggers async replica sync after
    any write operation on the master DB.
    """
    model_name = sender.__name__
    logger.info(f"Write detected on '{model_name}'. Triggering replica sync.")
    async_sync_master_to_replica()


# --- MasterCRDatabase Signals ---
@receiver(post_save, sender=MasterCRDatabase)
def on_master_cr_save(sender, instance, created, **kwargs):
    action = "INSERT" if created else "UPDATE"
    logger.info(f"MasterCRDatabase {action}: cr_no={instance.cr_no}, version={instance.version}")
    async_sync_master_to_replica()


@receiver(post_delete, sender=MasterCRDatabase)
def on_master_cr_delete(sender, instance, **kwargs):
    logger.info(f"MasterCRDatabase DELETE: cr_no={instance.cr_no}")
    async_sync_master_to_replica()


# --- CRWiseStatus Signals ---
@receiver(post_save, sender=CRWiseStatus)
def on_cr_status_save(sender, instance, created, **kwargs):
    action = "INSERT" if created else "UPDATE"
    logger.info(f"CRWiseStatus {action}: cr_no={instance.cr_no}, version={instance.version}")
    async_sync_master_to_replica()


@receiver(post_delete, sender=CRWiseStatus)
def on_cr_status_delete(sender, instance, **kwargs):
    logger.info(f"CRWiseStatus DELETE: cr_no={instance.cr_no}")
    async_sync_master_to_replica()
