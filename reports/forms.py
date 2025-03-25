from django.forms import ModelForm, Select
from .models import SysRepParamsHis, SysRepParams

class SysRepParamsHisForm(ModelForm):
    class Meta:
        model = SysRepParamsHis
        fields = "__all__"  # Include all fields
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.order:
            # Get only valid param_names related to the order's report
            valid_params = SysRepParams.objects.filter(rep=self.instance.order.rep).values_list("param_name", "param_name")
            self.fields["param_name"].widget = Select(choices=[("", "---------")] + list(valid_params))
        
        # Disable editing if object already exists
        if self.instance.pk:
            self.fields["param_name"].disabled = True