import json

from django import forms


class MethodCallForm(forms.Form):
    method = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "например, auth.check"}),
    )
    params = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "{}"}),
        help_text="JSON-объект или массив параметров",
    )

    def clean_params(self):
        raw = self.cleaned_data["params"].strip()
        if not raw:
            return {}
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"Некорректный JSON: {exc}") from exc
        if not isinstance(value, (dict, list)):
            raise forms.ValidationError("Параметры должны быть JSON-объектом или массивом")
        return value