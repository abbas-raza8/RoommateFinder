from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from roommates.models import Profile, Message
from django.utils.translation import ugettext_lazy as _
import django_filters
from django.core.validators import MaxValueValidator, MinValueValidator 

class EditProfileForm(ModelForm):
        class Meta:
                model = User
                fields = ('first_name','last_name')

class ProfileForm(ModelForm):
        class Meta:
                model = Profile
                fields = ('profile_pic','first_name', 'last_name', 'pronouns','gender', 'bio','major', 'year','location_general', 'location_specific', 'room_status') #Note that we didn't mention user field here.
                labels = {
                        'year': _('Graduation year'),
                        'location_general': _('Living on-grounds?'),
                        'location_specific': _('Specific location'),
                        'room_status': _('Looking for a roommate?'),
                        }
# Title: How to Filter QuerySets Dynamically
#Author: Vitor Freitas
#Date: published 11/28/16, last accessed 5/6/21
#URL: https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html
#Software License: BSD-3

class UserFilter(django_filters.FilterSet): # https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html
        first_name = django_filters.CharFilter(lookup_expr='icontains')
        location_specific = django_filters.CharFilter(lookup_expr='icontains')
        year = django_filters.NumberFilter(validators=[MinValueValidator(2021), MaxValueValidator(2024)])
        class Meta:
                model = Profile
                fields = ['first_name', 'gender', 'year', 'location_general', 'location_specific', 'major']

#Title: Django forms request.user
#Author: StackOverflow user ButtersB
#Date: published 8/7/14, last accessed 5/6/21
#URL: https://stackoverflow.com/questions/3532316/django-forms-request-user/25184373#25184373
#Software License: BSD-3
class MessageForm(forms.Form):
        receiver = forms.ModelChoiceField(queryset=Profile.objects.all())

        def __init__(self, *args, **kwargs):
                user = kwargs.pop('user', None)
                super(MessageForm, self).__init__(*args, **kwargs)
                self.fields['receiver'].queryset = Profile.objects.filter(favorites=user)

        msg_content = forms.CharField(widget=forms.Textarea, max_length=500)

