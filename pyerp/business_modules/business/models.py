from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Employee(models.Model):
    """Employee model representing staff members."""

    # Link to Django User (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_profile",
        verbose_name=_("Associated User Account"),
        help_text=_("Link to the Django user account for login and permissions."),
    )

    # Basic information
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("Employee Number"),
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Legacy ID"),
        help_text=_("ID from the legacy system"),
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name=_("First Name"),
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_("Last Name"),
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Birth Date"),
    )
    
    # Contact information
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_("Email"),
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Phone"),
    )
    mobile_phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Mobile Phone"),
    )
    
    # Address information
    street = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Street"),
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Postal Code"),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("City"),
    )
    
    # Employment information
    hire_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Hire Date"),
    )
    termination_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Termination Date"),
    )
    is_terminated = models.BooleanField(
        default=False,
        verbose_name=_("Is Terminated"),
    )
    is_present = models.BooleanField(
        default=True,
        verbose_name=_("Is Present"),
    )
    
    # Working hours
    weekly_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Weekly Hours"),
    )
    daily_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Daily Hours"),
    )
    
    # Financial information
    salary_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Salary Code"),
    )
    annual_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Annual Salary"),
    )
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Monthly Salary"),
    )
    
    # Leave information
    annual_vacation_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Annual Vacation Days"),
    )
    
    # System information
    ad_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("AD Username"),
        help_text=_("Active Directory username"),
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )
    
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ["last_name", "first_name"]
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.employee_number})"
    
    @property
    def full_name(self):
        """Return the full name of the employee."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self):
        """Return whether the employee is active (not terminated)."""
        return not self.is_terminated
