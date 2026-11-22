
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Business,
    Customer,
    Lead,
    Product,
    Brand,
    AutoReply,
    UserSettings
)


                                            
                   
                                            

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


                                            
                            
                                            

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter first name'
            }),

            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter last name'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address'
            }),
        }


                                            
               
                                            

class BusinessForm(forms.ModelForm):

    country_code = forms.ChoiceField(
        choices=[
            ('+91', 'India (+91)'),
            ('+1', 'USA (+1)'),
            ('+44', 'UK (+44)'),
            ('+61', 'Australia (+61)'),
            ('+971', 'UAE (+971)'),
        ],
        initial='+91',
        label='Country Code'
    )

    class Meta:
        model = Business
        fields = [
            'name',
            'category',
            'phone',
            'email',
            'address',
            'website'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            phone = self.instance.phone or ''

            for code, label in self.fields['country_code'].choices:
                if phone.startswith(code):
                    self.initial['country_code'] = code
                    self.initial['phone'] = phone[len(code):].strip()
                    break

    def clean(self):
        cleaned_data = super().clean()

        country_code = cleaned_data.get('country_code')
        phone = (cleaned_data.get('phone') or '').strip()

        if country_code and phone:
            if not phone.startswith('+'):
                cleaned_data['phone'] = f'{country_code}{phone}'

        return cleaned_data


                                            
               
                                            

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = [
            'business',
            'name',
            'phone',
            'email',
            'address'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter customer name'
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address'
            }),

            'address': forms.Textarea(attrs={
                'placeholder': 'Enter customer address',
                'rows': 3
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['business'].queryset = Business.objects.filter(
                owner=user
            )


                                            
           
                                            

class LeadForm(forms.ModelForm):

    class Meta:
        model = Lead
        fields = [
            'business',
            'name',
            'phone',
            'email',
            'source',
            'status',
            'follow_up_at',
            'notes',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter lead name'
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number'
            }),

            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address'
            }),

            'follow_up_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),

            'notes': forms.Textarea(attrs={
                'placeholder': 'Enter notes',
                'rows': 3
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['business'].queryset = Business.objects.filter(
                owner=user
            )


                                            
              
                                            

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'business',
            'name',
            'description',
            'price',
            'category',
            'image',
            'is_published'
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['business'].queryset = Business.objects.filter(
                owner=user
            )


                                            
            
                                            

class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        fields = [
            'business',
            'logo',
            'primary_color',
            'secondary_color',
            'banner',
            'tagline',
            'storefront_enabled'
        ]

        widgets = {
            'primary_color': forms.TextInput(attrs={
                'type': 'color'
            }),

            'secondary_color': forms.TextInput(attrs={
                'type': 'color'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['business'].queryset = Business.objects.filter(
                owner=user
            )


                                            
                 
                                            

class AutoReplyForm(forms.ModelForm):

    class Meta:
        model = AutoReply
        fields = [
            'business',
            'trigger',
            'message',
            'is_active'
        ]

        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write your automatic reply message...'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['business'].queryset = Business.objects.filter(
                owner=user
            )


                                            
                    
                                            

class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = UserSettings
        fields = [
            'theme',
            'accent_color',
            'email_notifications',
            'lead_notifications',
            'followup_reminders',
            'overdue_alerts',
            'automation_enabled',
        ]

        widgets = {
            'theme': forms.Select(),
            'accent_color': forms.TextInput(attrs={
                'type': 'color'
            }),
            'email_notifications': forms.CheckboxInput(),
            'lead_notifications': forms.CheckboxInput(),
            'followup_reminders': forms.CheckboxInput(),
            'overdue_alerts': forms.CheckboxInput(),
            'automation_enabled': forms.CheckboxInput(),
        }
