from django import forms

CHOICES_FIELD = (
    ('manual', 'MANUAL'),
    ('automatic', 'AUTOMATIC')
)


class FirstComponent(forms.Form):

    manual_number = forms.CharField(
        max_length=8)

    builty_type = forms.ChoiceField(
        choices=CHOICES_FIELD, widget=forms.RadioSelect())
