from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Profile, Message
from django.urls import reverse, NoReverseMatch
from django.views import generic
from roommates.forms import (EditProfileForm, ProfileForm, MessageForm)
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from roommates.forms import UserFilter
from django.views.generic.base import TemplateView
from django.db.models import Value
from django.db.models.functions import Concat
from django.contrib import messages
from django.contrib.auth.decorators import login_required

        
# lists all profiles on record excluding those with a blank name.
# profiles with a blank name have not been edited since default creation
"""
Title: Multi Attribute Matching of Profiles
Author: Stack Overflow User Shahbaz
Date: published May 7, 2012
URL: https://stackoverflow.com/questions/10480491/multi-attribute-matching-of-profiles
"""
class ProfileView(LoginRequiredMixin, generic.ListView): #LoginRequiredMixin used to resolve NoReverseMatch error if users try to access browse page without logging in 
    login_url = 'roommates:login'
    redirect_field_name = 'roommates:login'
    template_name = "profiles/index.html"
    context_object_name = "profile_list"
    
    def get_queryset(self):
        try: 
            userr = self.request.user.profile
            match_list = {}
            # Only shows people who are looking for roommmates and is not yourself
            profile_list = Profile.objects.filter(room_status = True).exclude(id=userr.id)

            for prof in profile_list:
                if prof.blocked.filter(id=self.request.user.id).exists(): #guess this isn't returning what I expect
                   profile_list = profile_list.exclude(id=prof.id)

            for person in profile_list:

                weight = 0
                # Gender match
                if userr.gender == person.gender:
                    weight += 6
                # Year similarity: 2 for same year, 1 for 1 apart, 0 for >= 2 apart
                weight += max(2 - abs(person.year - userr.year), 0)
                # Location general similarity
                if userr.location_general == person.location_general:
                    weight += 3
                #major similarity: 2 for same major
                if userr.major == person.major:
                    weight += 2
                match_list[person] = weight

                if person.favorites.filter(id=self.request.user.id).exists(): #guess this isn't returning what I expect
                    person.is_favorited = True
                    person.save()
                else:
                    person.is_favorited = False
            # Sorts dict of matches by match score and returns the keys
            return sorted(match_list, key=match_list.get, reverse=True)
        except (AttributeError, NoReverseMatch):  # if the user is not logged on, redirect to the login page
            return HttpResponseRedirect(reverse('roommates:login'))


# loads the current users profile as a form. Information updates when POSTed
# redirects to profile list page after successful form editing
"""
Title: Learn Django 3 - Creating a User Bookmark/Favourites Features - Part 10
Author: Very Academy
Date: published August 13,2020
Code version: 3.0
URL:  https://www.youtube.com/watch?v=H4QPHLmsZMU&t=1504s&ab_channel=VeryAcademy

Accessed about a month ago but the page is no longer available:
https://www.oodlestechnologies.com/blogs/How-to-Edit-User-Profile-Both-Django-User-and-Custom-User-Fields/
"""
def favorite_list(request):
    try: 
        new = Profile.objects.filter(favorites =request.user) #filter(favorites=request.user)
        return render(request, 'profiles/favorites.html', {'new': new})
    except (AttributeError, TypeError):  # if the user is not logged on, redirect to the login page
        return HttpResponseRedirect(reverse('roommates:login'))

def favorite_add(request, id):
    try: 
        prof= get_object_or_404(Profile, id=id)
        if prof.favorites.filter(id=request.user.id).exists():
            prof.favorites.remove(request.user)
        else:
            prof.favorites.add(request.user)
            prof.is_favorited = True
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    except (AttributeError, NoReverseMatch):  # if the user is not logged on, redirect to the login page
        return HttpResponseRedirect(reverse('roommates:login'))

"""
Title: Learn Django 3 - Creating a User Bookmark/Favourites Features - Part 10
Author: Very Academy
Date: published August 13,2020
Code version: 3.0
URL:  https://www.youtube.com/watch?v=H4QPHLmsZMU&t=1504s&ab_channel=VeryAcademy
"""
def block_list(request):
    try: 
        new = Profile.objects.filter(blocked =request.user) #filter(blocked=request.user)
        return render(request, 'profiles/blocked.html', {'new': new})
    except (AttributeError, TypeError):  # if the user is not logged on, redirect to the login page
        return HttpResponseRedirect(reverse('roommates:login'))

def block_add(request, id):
    try: 
        prof= get_object_or_404(Profile, id=id)
        if prof.blocked.filter(id=request.user.id).exists():
            prof.blocked.remove(request.user)
        else:
            prof.blocked.add(request.user)
            prof.favorites.remove(request.user)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    except (AttributeError, NoReverseMatch):  # if the user is not logged on, redirect to the login page
        return HttpResponseRedirect(reverse('roommates:login'))

"""
Title: Create An Edit Profile Page - Django Blog #23
Author: Codemy.com
Date: published June 11 2020
Code version: 3.0
URL:  https://www.youtube.com/watch?v=R6-pB5PAA6s&t=27s&ab_channel=Codemy.com
"""
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        # request.FILES is show the selected image or file
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid() and profile_form.is_valid():
            try:
                user_form = form.save()
                custom_form = profile_form.save(False)
                custom_form.user = user_form
                custom_form.save()
                return redirect('../../browse')
            except Exception as e:
                messages.error(request, "Please enter a valid profile picture. Valid types are: PNG, JPG, IMG, and GIF")
        else:
            messages.error(request, 'Please enter a valid graduation year: 2021-2024.')
        
        return HttpResponseRedirect(reverse('roommates:edit'))
    # if we are not doing a POST yet (not saving form data) then allow user to enter data
    else:
        try:
            form = EditProfileForm(instance=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
            args = {}
            args['form'] = form
            args['profile_form'] = profile_form
            return render(request, 'profiles/edit.html', args)
        except AttributeError:  # if the user is not logged on, redirect to the login page
            return HttpResponseRedirect(reverse('roommates:login'))

# not 100% sure what is depending on this, but site wouldn't work when deleted


def index(request):
    return HttpResponse("Team A-24 Roommate Finder")

"""
Title: 
Author: Learning About Electronics
Date: published 2018
Code version: 1.9
URL:  http://www.learningaboutelectronics.com/Articles/How-to-add-search-functionality-to-a-website-in-Django.php
"""
class SearchResultsView(generic.ListView): 
    model = Profile
    template_name = 'profiles/search_results.html'

    def get_queryset(self):
        user = self.request.user.profile 
        query = self.request.GET.get('q')
        object_list = Profile.objects.annotate(name=Concat('first_name', Value(' '), 'last_name'),).filter(name__icontains=query).exclude(id=user.id)
        for prof in object_list:
            if prof.blocked.filter(id=self.request.user.id).exists(): #guess this isn't returning what I expect
                object_list = object_list.exclude(id=prof.id)
        for prof in object_list:
            if prof.favorites.filter(id=self.request.user.id).exists(): #guess this isn't returning what I expect
                prof.is_favorited = True
        return object_list

class MyProfileView(LoginRequiredMixin, generic.ListView):
    login_url = 'roommates:login'
    redirect_field_name = 'roommates:login'
    template_name = "profiles/profile.html"
    context_object_name = "profile_list"

    def get_queryset(self):
        try: 
            user = self.request.user.profile
            return Profile.objects.filter(pk=user.pk)
        except (AttributeError, NoReverseMatch):  # if the user is not logged on, redirect to the login page
            return HttpResponseRedirect(reverse('roommates:login'))

def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('roommates:login'))

def filter(request):
    form = UserFilter(request.GET)
    if form.is_valid():
        profile_list = Profile.objects.exclude(user=request.user)
        profile_favs = Profile.objects.all()
        for prof in profile_list:
            if prof.blocked.filter(id=request.user.id).exists(): #guess this isn't returning what I expect
                profile_list = profile_list.exclude(id=prof.id)
            if prof.favorites.filter(id=request.user.id).exists(): #guess this isn't returning what I expect
                prof.is_favorited = True
                prof.save()
            else:
                profile_favs = profile_favs.exclude(id=prof.id)
               # profile_list = profile_list.exclude(id=prof.id)
        user_filter = UserFilter(request.GET, queryset=profile_list)
        return render(request, 'profiles/filter_list.html', {'filter': user_filter, 'favs':profile_favs})
    messages.error(request, 'Please enter a valid graduation year: 2021-2024.')
    return HttpResponseRedirect(reverse('roommates:filter'))

class LegalView(TemplateView): #do not need to be logged on to see how we use your data
    template_name = 'roommates/legal.html'

@login_required(login_url='roommates:login')
def create_message(request):
    profile = Profile.objects.get(user=request.user.id)
    # Messages received from a blocked user will not show
    inbox = Message.objects.filter(receiver=profile.id).exclude(sender__in=Profile.objects.filter(blocked=request.user))
    sent = Message.objects.filter(sender=profile.id)

    if request.method == 'POST':
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = Message.objects.create(
                msg_content=form.cleaned_data['msg_content'],
                receiver=form.cleaned_data['receiver'],
                sender=profile
            )
            message.save()
            return HttpResponseRedirect(request.path_info)

    else:
        form = MessageForm(user=request.user)

    return render(request, 'profiles/messages.html', {'form': form, 'inbox': inbox, 'sent': sent})

@login_required(login_url='roommates:login')
def delete_message(request, id):
    try: 
        message = get_object_or_404(Message, id=id)
        message.delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    except (AttributeError, NoReverseMatch):  # if the user is not logged on, redirect to the login page
        return HttpResponseRedirect(reverse('roommates:login'))
