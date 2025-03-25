from django.db import models
from django.conf import settings
import os
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from users.models import SysUsers
from django.utils.timezone import now
from django.contrib.auth import get_user_model 

def report_template_path(instance, filename):
    """Generate file path as 'media/reports/report_<id>.<ext>'."""
    ext = filename.split('.')[-1]  # Extract original extension
    if instance.pk:
        filename = f"report_{instance.pk}.{ext}"
    else:
        filename = f"report_temp.{ext}"  # Temporary filename before saving
    return os.path.join("reports", filename)

class SysSReports(models.Model):
    name = models.CharField(max_length=250)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.CharField(max_length=400, blank=True, null=True)
    position = models.CharField(max_length=400, blank=True, null=True)
    rep_type = models.CharField(
        max_length=3,
        choices=[("001", "Simple"), ("002", "Old System")],
        default="001"
    )
    job = models.BooleanField(default=False)
    uploadable = models.BooleanField(default=False)
    module = models.CharField(max_length=200, blank=True, null=True)
    template = models.FileField(upload_to=report_template_path, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.rep_type})"

    def save(self, *args, **kwargs):
        """Ensure file name is updated to 'report_<id>.<ext>' after first save."""
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save to generate ID

        if is_new and self.template:
            ext = self.template.name.split('.')[-1]
            new_filename = f"report_{self.pk}.{ext}"
            new_path = os.path.join("reports", new_filename)

            old_path = self.template.path
            new_full_path = os.path.join(settings.MEDIA_ROOT, new_path)

            if os.path.exists(old_path):  # Ensure file exists before renaming
                os.rename(old_path, new_full_path)
            
            self.template.name = new_path  # Update filename in DB
            super().save(update_fields=["template"])

    def get_owner(self):
        return self.owner.creater
    
    class Meta:
        verbose_name = 'All Report'
        verbose_name_plural = 'All Reports'

class SysModules(models.Model):
    rep = models.ForeignKey(SysSReports, on_delete=models.CASCADE)
    module_code = models.CharField(max_length=200, blank=True, null=True)  # Will be auto-set
    list_id = models.IntegerField()
    resource = models.CharField(max_length=400)
    module_type = models.CharField(max_length=200, default="01")
    row_number = models.IntegerField()

    def __str__(self):
        return f"{self.module_code} - {self.list_id}"
    
    def clean(self):
        """Ensure that only reports with rep_type='001' can be used."""
        if self.rep and self.rep.rep_type != "001":
            raise ValidationError("Only reports with rep_type='001' can be used to create a module.")

    def save(self, *args, **kwargs):
        """Override save to enforce validation and set module_code."""
        self.clean()  # Validate before saving
        if self.rep:  # Set module_code automatically
            self.module_code = self.rep.module
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Report Module'
        verbose_name_plural = 'Report Modules'
    
# Signal to set module_code before saving
@receiver(pre_save, sender=SysModules)
def set_module_code(sender, instance, **kwargs):
    if instance.rep:  # Ensure related SysSReports exists
        instance.module_code = instance.rep.module  # Copy module value

# ✅ Signal to update `SysModules` when `SysSReports.module` changes
@receiver(post_save, sender=SysSReports)
def update_sysmodules(sender, instance, **kwargs):
    """Update all related SysModules when SysSReports.module is updated."""
    SysModules.objects.filter(rep=instance).update(module_code=instance.module)

class SysRepParams(models.Model):
    rep = models.ForeignKey("SysSReports", on_delete=models.CASCADE)  # Foreign Key to SysSReports
    param_name = models.CharField(max_length=250)  # Parameter name

    TYPE_CHOICES = [
        ("string", "String"),
        ("integer", "Integer"),
        ("date", "Date"),
        ("boolean", "Boolean"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # Type selection

    class Meta:
        unique_together = ("rep", "param_name")  # Ensuring uniqueness of (rep_id, param_name)
        verbose_name = "Report Parameter"

    def __str__(self):
        return f"{self.rep.name} - {self.param_name} ({self.type})"
    
class SysRepOrders(models.Model):
    rep = models.ForeignKey(SysSReports, on_delete=models.CASCADE)  # Report reference
    user = models.ForeignKey(SysUsers, on_delete=models.CASCADE)  # User who requested the report

    progress = models.IntegerField(default=0)  # Progress percentage

    STATE_CHOICES = [
        ("A", "Active"),
        ("C", "Canceled"),
        ("E", "Error"),
        ("S", "Successful"),
    ]
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default="A")  # Execution state

    message = models.TextField(blank=True, null=True)  # Execution message
    date_begin = models.DateTimeField(auto_now_add=True)  # Start time (auto set)
    date_end = models.DateTimeField(blank=True, null=True)  # End time (set when finished)

    job_id = models.IntegerField()  # Job ID (if executed in a job queue)
    machine = models.CharField(max_length=400)  # Machine where the report was generated

    class Meta:
        ordering = ["-date_begin"]  # Latest orders first
        verbose_name = "Report Order"
        verbose_name_plural = "Report Orders"

    def __str__(self):
        return f"Order {self.id} - {self.rep.name} ({self.get_state_display()})"

class SysRepParamsHis(models.Model):
    order = models.ForeignKey(SysRepOrders, on_delete=models.CASCADE)  # Related report order
    param_name = models.CharField(max_length=250)  # Parameter name (filled automatically)
    value = models.TextField()  # Parameter value

    class Meta:
        ordering = ["-order"]
        verbose_name = "Report Parameter History"
        verbose_name_plural = "Report Parameters History"
        unique_together = ("order", "param_name")  # Ensure unique param per order

    def clean(self):
        """Ensure param_name is valid for the related report."""
        valid_params = SysRepParams.objects.filter(rep=self.order.rep).values_list("param_name", flat=True)
        if self.param_name not in valid_params:
            raise ValidationError(f"Invalid param_name '{self.param_name}' for report {self.order.rep.name}.")

    def save(self, *args, **kwargs):
        """Automatically assign param_name if not provided."""
        if not self.param_name:
            valid_params = SysRepParams.objects.filter(rep=self.order.rep)
            if valid_params.exists():
                self.param_name = valid_params.first().param_name  # Assign the first available param
            else:
                raise ValidationError("No parameters available for this report.")
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order.id} - {self.param_name}: {self.value}"


class SysAccessGroupUsers(models.Model):
    group_code = models.CharField(max_length=50)  # Unique group identifier
    group_name = models.CharField(max_length=255)
    user = models.ForeignKey(SysUsers, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("group_code", "user") 
        verbose_name = "Group User"
        verbose_name_plural = "Group User"

    def __str__(self):
        return f"{self.user.fio} ({self.group_name})"


class SysAccessGroup(models.Model):
    rep_id = models.ForeignKey(SysSReports, on_delete=models.CASCADE)
    group_code = models.CharField(max_length=50)
    group_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Group Access"
        verbose_name_plural = "Group Accesses"

    def clean(self):
        """Ensure group_code exists in SysAccessGroupUsers before saving"""
        if not SysAccessGroupUsers.objects.filter(group_code=self.group_code).exists():
            raise ValidationError(f"Group code '{self.group_code}' does not exist in SysAccessGroupUsers.")

    def save(self, *args, **kwargs):
        
        self.clean()

        """When saving a new access group, automatically add users from SysAccessGroupUsers to SysReportAccess."""
        super().save(*args, **kwargs)  # Save the group first
        
        group_users = SysAccessGroupUsers.objects.filter(group_code=self.group_code)
        for group_user in group_users:
            SysReportAccess.objects.get_or_create(
                user_id=group_user.user,
                rep_id=self.rep_id
            )

    def __str__(self):
        return f"Group: {self.group_name} - Report: {self.rep_id.name}"
    
class SysReportAccess(models.Model):
    rep_id = models.ForeignKey(SysSReports, on_delete=models.CASCADE)
    user_id = models.ForeignKey(SysUsers, on_delete=models.CASCADE) 
    accessed_date = models.DateTimeField(default=now)

    class Meta:
        verbose_name = "Report Access"
        verbose_name_plural = "Report Accesses"
        unique_together = ('rep_id', 'user_id')

    def __str__(self):
        return f"{self.user_id.fio} accessed {self.rep_id.name} on {self.accessed_date}"
