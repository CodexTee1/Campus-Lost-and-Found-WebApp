from django import forms

from .models import Item


class ReportItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "category",
            "name",
            "description",
            "location",
            "date_lost_or_found",
            "status",
            "image",
        ]
        widgets = {
            "date_lost_or_found": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
