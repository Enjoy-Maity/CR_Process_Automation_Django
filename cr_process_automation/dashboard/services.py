from django.db import transaction
from .models import FlagTable
from django.db.models import F

def update_cr_flag_atomic(cr_no, field_name, new_value):
    """
    Atomically updates a specific flag field for a CR.
    Prevents race conditions by locking the row during update.
    """
    with transaction.atomic(using="default"):
        # Lock the row in the Master DB
        try:
            obj = CRWiseStatus.objects.select_for_update().get(cr_no=cr_no)
            
            # Dynamically set the field
            if hasattr(obj, field_name):
                setattr(obj, field_name, new_value)
                # Increment version to track changes
                obj.version = F('version') + 1
                obj.save()
                return True
            else:
                raise ValueError(f"Field {field_name} does not exist")
        except CRWiseStatus.DoesNotExist:
            # Handle case where CR doesn't exist (optional: create it)
            raise Exception(f"CR {cr_no} not found")