import datetime
from django import forms
from django.core.validators import RegexValidator
from main.models import Category, Brand, Product, Coupon, Feedback, DeliveryAddress, Payment, Orders, OrderDetails
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^(0|\+)\d{9,19}$', message="Phone number is invalid")


# Feedback Form
class FeedbackForm(forms.Form):
    name = forms.CharField(required=True, max_length=40)
    email = forms.EmailField(required=True, max_length=50)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    subject = forms.CharField(required=True, max_length=100)
    message = forms.CharField(required=True, max_length=2000, widget=forms.Textarea)

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'mobile', 'subject', 'message']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')

        if not name:
            raise ValidationError(_('Please enter your name'))
        if not email:
            raise ValidationError(_('Please enter your email'))
        if not mobile:
            raise ValidationError(_('Please enter your mobile number'))
        if not subject:
            raise ValidationError(_('Please enter your subject'))
        if not message:
            raise ValidationError(_('Please enter your message'))

        return cleaned_data

    def save(self):
        feedback = Feedback(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            mobile=self.cleaned_data['mobile'],
            subject=self.cleaned_data['subject'],
            message=self.cleaned_data['message'],
        )
        feedback.save()
        return feedback



# Checkout Form
class CheckoutForm(forms.Form):
    first_name = forms.CharField(required=True, max_length=100)
    last_name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True, max_length=100)
    mobile = forms.CharField(validators=[phone_regex], max_length=20, required=True)
    address = forms.CharField(required=True, max_length=200)
    city = forms.CharField(required=True, max_length=100)
    state = forms.CharField(required=True, max_length=100)
    zip_code = forms.CharField(required=True, max_length=100)
    country = forms.CharField(required=True, max_length=100)
    payment_method = forms.CharField(required=True, max_length=100)

    class Meta:
        model = DeliveryAddress
        fields = ['first_name', 'last_name', 'email', 'mobile', 'address', 'city', 'state', 'zip_code', 'country',
                  'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        address = cleaned_data.get('address')
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        zip_code = cleaned_data.get('zip_code')
        country = cleaned_data.get('country')
        payment_method = cleaned_data.get('payment_method')

    def save(self):
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        mobile = self.cleaned_data.get('mobile')
        address = self.cleaned_data.get('address')
        city = self.cleaned_data.get('city')
        state = self.cleaned_data.get('state')
        zip_code = self.cleaned_data.get('zip_code')
        country = self.cleaned_data.get('country')
        payment_method = self.cleaned_data.get('payment_method')
        delivery_address = DeliveryAddress(first_name=first_name, last_name=last_name, email=email, mobile=mobile,
                                           address=address, city=city, state=state, zip_code=zip_code, country=country,
                                           payment_method=payment_method)
        delivery_address.save()
        return delivery_address
