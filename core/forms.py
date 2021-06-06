from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import DocumentImage

PAYMENT_CHOICES = (
    ("S", "Stripe"),
    ("P", "Paypal")
)


class ImageClassification(forms.ModelForm):
    class Meta:
        model = DocumentImage

        fields = ('image',)


class CheckOutForm(forms.Form):
    shipping_address = forms.CharField(max_length=100, required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label="(Selected country)").formfield(
        widget=CountrySelectWidget(attrs={
            "class": "custom-select d-block w-100",
            'id': 'shipping_country'
        }), required=False
    )
    shipping_zip = forms.CharField(max_length=6, required=False)
    same_shipping_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    billing_address = forms.CharField(max_length=100, required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label="(Selected country)").formfield(
        widget=CountrySelectWidget(attrs={
            "class": "custom-select d-block w-100",
            'id': 'billing_country'
        }), required=False
    )
    billing_zip = forms.CharField(max_length=6, required=False)
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        choices=PAYMENT_CHOICES, widget=forms.RadioSelect())


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'PromoCode',
        'aria-label': "Recipient's username",
        'aria-describedby': "basic-addon2"

    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()
