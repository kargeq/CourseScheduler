from django import forms
from .models import Schedule, tutorMeUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule

        fields = ['tutor', 'class_name', 'input_rate', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


class EditProfileForm(UserChangeForm):
    first_name = forms.CharField(required=False, max_length=20)
    phone_number = forms.CharField(required=False, max_length=20)
    PREFERRED_CONTACT_CHOICES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
    ]
    preferred_contact = forms.ChoiceField(choices=PREFERRED_CONTACT_CHOICES, widget=forms.RadioSelect, required=False)

    class Meta:
        model = tutorMeUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'preferred_contact'
        )

        

class BugReportForm(forms.Form):
    bug_description = forms.CharField(label="enter any issues you may encounter", widget=forms.Textarea)

