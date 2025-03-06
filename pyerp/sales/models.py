from django.db import models
from django.db.utils import OperationalError


class SalesModel(models.Model):
    """
    Base model for sales-related models.
    This is a placeholder model - you'll need to implement your actual models.
    """
    class Meta:
        abstract = True  # noqa: F841


def get_sales_status():
    """
    A safe helper function that can be imported to check if the sales module is working.  # noqa: E501
    This will be used by other modules that might attempt to import from sales.
    """
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.close()
        return "Sales module database connection is working"
    except OperationalError:
        return "Sales module found but database is not available"
    except Exception as e:
        return f"Sales module error: {str(e)}"
