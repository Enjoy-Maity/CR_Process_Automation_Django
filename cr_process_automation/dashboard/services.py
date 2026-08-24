from django.db import transaction
from .models import MasterCRDatabase, SelectedDateTable, FlagTable
from django.db.models import F
from .exceptions import (
    ValidationException,
    DatabaseException,
    NotFoundException,
    DuplicateRecordException
)
import logging

logger = logging.getLogger(__name__)


def update_cr_flag_atomic(cr_no, field_name, new_value):
    """
    Atomically updates a specific flag field for a CR in MasterCRDatabase.
    Prevents race conditions by locking the row during update.
    
    Args:
        cr_no (str): The CR number to update
        field_name (str): The field name to update
        new_value (str/int/bool): The new value for the field
    
    Returns:
        dict: Updated object information
    
    Raises:
        NotFoundException: If CR not found
        ValidationException: If field doesn't exist
        DatabaseException: If database operation fails
    """
    try:
        with transaction.atomic(using="default"):
            # Lock the row in the Master DB to prevent concurrent updates
            try:
                obj = MasterCRDatabase.objects.select_for_update().get(
                    cr_no=cr_no,
                    is_active=True
                )
            except MasterCRDatabase.DoesNotExist:
                raise NotFoundException(
                    f"CR with number '{cr_no}' not found in active records.",
                    title="CR Not Found"
                )
            
            # Validate field exists on the model
            if not hasattr(obj, field_name):
                raise ValidationException(
                    f"Field '{field_name}' does not exist on MasterCRDatabase model.",
                    title="Invalid Field Name"
                )
            
            # Store old value for logging
            old_value = getattr(obj, field_name)
            
            # Update the field
            setattr(obj, field_name, new_value)
            obj.save()
            
            logger.info(
                f"Updated CR {cr_no}: {field_name} changed from '{old_value}' to '{new_value}'"
            )
            
            return {
                'success': True,
                'cr_no': cr_no,
                'field': field_name,
                'old_value': old_value,
                'new_value': new_value,
                'version': obj.version
            }
            
    except (ValidationException, NotFoundException):
        # Re-raise custom exceptions
        raise
    except Exception as e:
        logger.error(
            f"Failed to update CR {cr_no}, field {field_name}: {str(e)}",
            exc_info=True
        )
        raise DatabaseException(
            f"Failed to update CR flag: {str(e)}",
            title="Database Update Failed"
        )


def update_cr_flags_batch(updates):
    """
    Atomically updates multiple flags for multiple CRs.
    Each CR update is wrapped in its own atomic transaction.
    
    Args:
        updates (list): List of dicts with keys: cr_no, field_name, new_value
    
    Returns:
        dict: Summary of successful and failed updates
    
    Example:
        updates = [
            {'cr_no': 'CR001', 'field_name': 'activity_status', 'new_value': 'Completed'},
            {'cr_no': 'CR002', 'field_name': 'activity_status', 'new_value': 'Failed'},
        ]
    """
    if not updates:
        raise ValidationException(
            "Updates list cannot be empty.",
            title="Invalid Input"
        )
    
    successful = []
    failed = []
    
    for update in updates:
        try:
            result = update_cr_flag_atomic(
                cr_no=update['cr_no'],
                field_name=update['field_name'],
                new_value=update['new_value']
            )
            successful.append(result)
        except Exception as e:
            failed.append({
                'cr_no': update['cr_no'],
                'field_name': update['field_name'],
                'error': str(e)
            })
            logger.error(f"Batch update failed for CR {update['cr_no']}: {str(e)}")
    
    return {
        'successful': successful,
        'failed': failed,
        'total': len(updates),
        'success_count': len(successful),
        'failure_count': len(failed)
    }


def sync_selected_date_to_master(selected_date_obj, user=None):
    """
    Syncs a SelectedDateTable record to MasterCRDatabase with CoW.
    Creates a new version in MasterCRDatabase.
    
    Args:
        selected_date_obj (SelectedDateTable): The record to sync
        user (User): Optional user information for audit trail
    
    Returns:
        dict: Information about the synced record
    
    Raises:
        DatabaseException: If sync fails
    """
    if not selected_date_obj:
        raise ValidationException(
            "SelectedDateTable object cannot be None.",
            title="Invalid Input"
        )
    
    try:
        with transaction.atomic(using="default"):
            # Get fields to copy (exclude id, pk, version tracking fields)
            exclude_fields = {'id', 'pk', 'is_active', 'version', 'parent_reference'}
            sync_data = {}
            
            for field in selected_date_obj._meta.fields:
                if field.name not in exclude_fields:
                    sync_data[field.name] = getattr(selected_date_obj, field.name)
            
            # Find existing active master record
            try:
                master_obj = MasterCRDatabase.objects.select_for_update().get(
                    cr_no=selected_date_obj.cr_no,
                    is_active=True
                )
                # Mark old as inactive
                MasterCRDatabase.objects.filter(pk=master_obj.pk).update(is_active=False)
                
                # Create new version
                new_master = MasterCRDatabase(
                    parent_reference_id=master_obj.pk,
                    version=master_obj.version + 1,
                    is_active=True,
                    **sync_data
                )
                new_master.save()
                
            except MasterCRDatabase.DoesNotExist:
                # Create new master record if doesn't exist
                new_master = MasterCRDatabase(
                    is_active=True,
                    version=1,
                    **sync_data
                )
                new_master.save()
            
            logger.info(
                f"Synced CR {selected_date_obj.cr_no} from SelectedDateTable to MasterCRDatabase"
            )
            
            return {
                'success': True,
                'cr_no': selected_date_obj.cr_no,
                'master_version': new_master.version,
                'synced_at': str(new_master.updated_at) if hasattr(new_master, 'updated_at') else None
            }
            
    except Exception as e:
        logger.error(
            f"Failed to sync CR {selected_date_obj.cr_no} to MasterCRDatabase: {str(e)}",
            exc_info=True
        )
        raise DatabaseException(
            f"Failed to sync record: {str(e)}",
            title="Sync Failed"
        )


def get_active_cr(cr_no):
    """
    Retrieves the active version of a CR.
    
    Args:
        cr_no (str): CR number to retrieve
    
    Returns:
        MasterCRDatabase: The active CR record
    
    Raises:
        NotFoundException: If CR not found
    """
    try:
        return MasterCRDatabase.objects.get(
            cr_no=cr_no,
            is_active=True
        )
    except MasterCRDatabase.DoesNotExist:
        raise NotFoundException(
            f"Active CR with number '{cr_no}' not found.",
            title="CR Not Found"
        )


def get_cr_history(cr_no):
    """
    Retrieves the complete version history of a CR.
    
    Args:
        cr_no (str): CR number
    
    Returns:
        QuerySet: All versions of the CR ordered by version descending
    
    Raises:
        NotFoundException: If CR not found in any version
    """
    try:
        cr_history = MasterCRDatabase.objects.filter(
            cr_no=cr_no
        ).order_by('-version')
        
        if not cr_history.exists():
            raise NotFoundException(
                f"CR with number '{cr_no}' not found in history.",
                title="CR Not Found"
            )
        
        return cr_history
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve CR history for {cr_no}: {str(e)}")
        raise DatabaseException(
            f"Failed to retrieve CR history: {str(e)}",
            title="History Retrieval Failed"
        )


def bulk_update_activity_status(cr_nos, new_status):
    """
    Updates activity_status for multiple CRs.
    Useful for batch operations.
    
    Args:
        cr_nos (list): List of CR numbers
        new_status (str): New activity status value
    
    Returns:
        dict: Update summary
    
    Raises:
        ValidationException: If cr_nos is empty or invalid
    """
    if not cr_nos:
        raise ValidationException(
            "CR number list cannot be empty.",
            title="Invalid Input"
        )
    
    if not isinstance(cr_nos, list):
        raise ValidationException(
            "CR numbers must be provided as a list.",
            title="Invalid Input Format"
        )
    
    if not new_status or not isinstance(new_status, str):
        raise ValidationException(
            "Status value must be a non-empty string.",
            title="Invalid Status"
        )
    
    updates = [
        {'cr_no': cr_no, 'field_name': 'activity_status', 'new_value': new_status}
        for cr_no in cr_nos
    ]
    
    return update_cr_flags_batch(updates)


def validate_cr_exists(cr_no):
    """
    Validates if a CR exists in the active records.
    
    Args:
        cr_no (str): CR number to validate
    
    Returns:
        bool: True if CR exists
    
    Raises:
        NotFoundException: If CR doesn't exist
    """
    if not cr_no or not isinstance(cr_no, str):
        raise ValidationException(
            "CR number must be a non-empty string.",
            title="Invalid CR Number"
        )
    
    if not MasterCRDatabase.objects.filter(cr_no=cr_no, is_active=True).exists():
        raise NotFoundException(
            f"CR with number '{cr_no}' does not exist.",
            title="CR Not Found"
        )
    return True


def get_crs_by_region(region, execution_date=None):
    """
    Retrieves all active CRs for a specific region.
    
    Args:
        region (str): Region name (north, south, east, west)
        execution_date (date): Optional filter by execution date
    
    Returns:
        QuerySet: Active CRs for the region
    
    Raises:
        ValidationException: If region is invalid
    """
    valid_regions = ['north', 'south', 'east', 'west']
    
    if not region or region.lower() not in valid_regions:
        raise ValidationException(
            f"Invalid region '{region}'. Must be one of {', '.join(valid_regions)}.",
            title="Invalid Region"
        )
    
    query = MasterCRDatabase.objects.filter(
        region__iexact=region,
        is_active=True
    )
    
    if execution_date:
        query = query.filter(execution_date=execution_date)
    
    return query.order_by('-version')


def get_crs_by_planning_status(planning_status, execution_date=None):
    """
    Retrieves all active CRs with a specific planning status.
    
    Args:
        planning_status (str): Planning status value
        execution_date (date): Optional filter by execution date
    
    Returns:
        QuerySet: Active CRs with matching planning status
    
    Raises:
        ValidationException: If planning_status is invalid
    """
    if not planning_status or not isinstance(planning_status, str):
        raise ValidationException(
            "Planning status must be a non-empty string.",
            title="Invalid Planning Status"
        )
    
    query = MasterCRDatabase.objects.filter(
        planning_status__iexact=planning_status,
        is_active=True
    )
    
    if execution_date:
        query = query.filter(execution_date=execution_date)
    
    return query.order_by('-version')


def get_cr_count_by_region(execution_date=None):
    """
    Gets count of active CRs grouped by region.
    
    Args:
        execution_date (date): Optional filter by execution date
    
    Returns:
        dict: Region-wise CR count
    """
    from django.db.models import Count
    
    query = MasterCRDatabase.objects.filter(is_active=True)
    
    if execution_date:
        query = query.filter(execution_date=execution_date)
    
    counts = query.values('region').annotate(count=Count('cr_no'))
    
    return {item['region']: item['count'] for item in counts}


def revert_cr_to_version(cr_no, version_number):
    """
    Reverts a CR to a previous version.
    Creates a new active record with the reverted data.
    
    Args:
        cr_no (str): CR number
        version_number (int): Version to revert to
    
    Returns:
        dict: Information about reverted CR
    
    Raises:
        NotFoundException: If CR or version not found
        DatabaseException: If revert fails
    """
    try:
        with transaction.atomic(using="default"):
            # Get the version to revert to
            try:
                old_version = MasterCRDatabase.objects.get(
                    cr_no=cr_no,
                    version=version_number
                )
            except MasterCRDatabase.DoesNotExist:
                raise NotFoundException(
                    f"Version {version_number} of CR '{cr_no}' not found.",
                    title="Version Not Found"
                )
            
            # Get current active version
            try:
                current = MasterCRDatabase.objects.get(
                    cr_no=cr_no,
                    is_active=True
                )
            except MasterCRDatabase.DoesNotExist:
                raise NotFoundException(
                    f"No active version found for CR '{cr_no}'.",
                    title="CR Not Found"
                )
            
            # Mark current as inactive
            MasterCRDatabase.objects.filter(pk=current.pk).update(is_active=False)
            
            # Create new version with old_version data
            exclude_fields = {'id', 'pk', 'is_active', 'version', 'parent_reference'}
            revert_data = {}
            
            for field in old_version._meta.fields:
                if field.name not in exclude_fields:
                    revert_data[field.name] = getattr(old_version, field.name)
            
            new_version = MasterCRDatabase(
                parent_reference_id=current.pk,
                version=current.version + 1,
                is_active=True,
                **revert_data
            )
            new_version.save()
            
            logger.info(
                f"Reverted CR {cr_no} from version {current.version} to version {version_number}"
            )
            
            return {
                'success': True,
                'cr_no': cr_no,
                'from_version': current.version,
                'to_version': version_number,
                'new_active_version': new_version.version
            }
            
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to revert CR {cr_no} to version {version_number}: {str(e)}",
            exc_info=True
        )
        raise DatabaseException(
            f"Failed to revert CR: {str(e)}",
            title="Revert Failed"
        )