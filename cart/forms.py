from django import forms
import datetime
from cart.models import Coupon

class CouponForm(forms.Form):
    code = forms.CharField(max_length=100)
    discount = forms.IntegerField()
    expiry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self):
        cleaned_data = self.cleaned_data
        coupon = Coupon(
            code=cleaned_data['code'],
            discount=cleaned_data['discount'],
            expiry=cleaned_data['expiry'],
        )
        coupon.save()
        return coupon






class AddressForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    company_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Company name'}))
    phone_number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Phone number'}))
    email_address = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    address_line_1 = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Address line 01'}))
    address_line_2 = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Address line 02'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Town/City'}))
    zip_code = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Postcode/ZIP'}))
    order_notes = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={'placeholder': 'Order Notes'}))

