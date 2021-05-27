import unittest
from django.test import TestCase
from roommates.models import Profile
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from roommates.forms import UserFilter

class TravisTest(unittest.TestCase): #This test will always pass
    def test_will_pass(self):
        self.assertFalse(False)

#testing the profile model
"""
Assorted syntax for all tests gotten from: 
Title: Django Tutorial Part 10: Testing a Django web application
Author: Mozilla Staff/contributor
URL: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing
"""
class ProfileViewTest(TestCase):
    """
    Set up a test user
    Then have login credentials using the created test user
    """

    def setUp(self):
        #This makes a test user for getting past authentication
        #Also sets up profiles for these test users
        #Don't forget to delete them in the teardown at the bottom
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='k8\E/r#j')
        test_user2.save()
        test_user3 = User.objects.create_user(username='testuser3', password='bDL/sV#EQz89')
        test_user3.save()

    def test1_user_login(self): #this verifies that a person is logged in alright
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK') #login the user
        response = self.client.get(reverse('roommates:login')) #"put" the user in the right page, the name is from urls
        self.assertEqual(response.status_code, 200, msg="the user isn't being logged in properly") 
        #status code 200 means that it was a success

    def test2_see_profiles(self): #are we getting the right template when loading the /browse page
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('roommates:browse'))
        self.assertTemplateUsed(response, 'profiles/index.html')

    def test3_edit_profile_redirect(self): 
        #if a user isn't logged in and tries to edit their profile they will be redirected to the login screen
        response = self.client.get(reverse('roommates:edit'))
        self.assertRedirects(response, '/')

    def test4_edit_profile_login(self): #are we getting the right template when viewing the edit screen
        test_user1 = User.objects.get(username='testuser1')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('roommates:edit'))
        self.assertTemplateUsed(response, 'profiles/edit.html')

    """
    For the next 3 tests:
    Title: Django Testing Cheat Sheet
    Author: Valentino Gagliardi
    Date: December 19, 2020
    URL: https://www.valentinog.com/blog/testing-django/#testing-a-many-to-many-relationship
    
    Title: Setting HTTP_REFERER header in Django test
    Author: Stack Overflow user supervacuo
    Date: August 5, 2012
    URL: https://stackoverflow.com/questions/11801946/setting-http-referer-header-in-django-test/11819426#11819426
    """
    def test5_add_favorite(self): #if we add a profile to our favorite profiles, does it show up on the favorites page
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        url = reverse('roommates:favorite_add', kwargs={'id': profile2.pk})
        redirect_url = reverse('roommates:browse')
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #add the user's profile to the favorites list of profile2
        self.assertEqual(profile2.favorites.count(), 1, msg='favorites are not being added') #profile2 should have profile 1 on their list of favorites

    def test6_default_no_favorites(self): #verify that a profile without added favorites has a count 0
        test_user1 = User.objects.get(username='testuser1')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        
        self.assertEqual(profile1.favorites.count(), 0, msg='default profile does not have empty favorites list')

    def test7_favorite_then_unfavorite(self): #check if a favorited profile is then unfavorited, it is removed
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        url = reverse('roommates:favorite_add', kwargs={'id': profile2.pk})
        redirect_url = reverse('roommates:browse')
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #add the user's profile to the favorites list of profile2
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #adding to favorites again will remove profile1 from profile2's favorites
        self.assertEqual(profile2.favorites.count(), 0, msg='favorites are not being removed properly') #profile2 should have profile 1 on their list of favorites

    """
    For the next 3 tests: 
    Title: Test cases development for filter query search in Django
    Author: Stack Overflow user ruddra
    Date: December 21, 2018
    URL: https://stackoverflow.com/questions/53879200/test-cases-development-for-filter-query-search-in-django
    """
    def test8_search_existing_profile(self): #search for a profile that exists, it shows up
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        profile2.first_name='testuser'
        url = '{url}?{filter}={value}'.format(  # With string format finally we expect a url like:
            url=reverse('roommates:search_results'), # '/search/?q=testuser'
            filter='q', value='testuser')
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['object_list'], Profile.objects.filter(first_name='testuser'),
            msg='the correct profiles are not being shown')

    def test9_searching_profile_does_not_exist(self): #try searching for someone who doesn't have a profile
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        profile2.first_name='testuser'
        url = '{url}?{filter}={value}'.format(  # With string format finally we expect a url like:
            url=reverse('roommates:search_results'), # '/search/?q=john'  no profiles with the name john
            filter='q', value='john')
        response = self.client.get(url)
        self.assertEqual(response.context['object_list'].count(), 0) # object_list should be empty
            

    def test10_search_for_multiple_profiles(self): #search for profiles sharing same name/part of name
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile

        profile2.first_name='testuser'
        profile3.first_name='testuser' # both have the same name

        url = '{url}?{filter}={value}'.format(  # With string format finally we expect a url like:
            url=reverse('roommates:search_results'), # '/search/?q=testuser'
            filter='q', value='testuser')
        response = self.client.get(url)
        self.assertQuerysetEqual(response.context['object_list'], Profile.objects.filter(first_name='testuser'), # should contain both user 2 & 3
            msg='the correct profiles are not being shown')
    
    def test11_my_profile_page_shows_only_self(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile

        response = self.client.get(reverse('roommates:my_profile'))
        self.assertEqual(response.context['profile_list'][0], Profile.objects.get(pk=profile1.pk), # should only be user's profile
            msg='the my profile page of the user is not showing the profile of the user')
   
    """
    For the next 3 tests:
    Title: Django Testing Cheat Sheet
    Author: Valentino Gagliardi
    Date: December 19, 2020
    URL: https://www.valentinog.com/blog/testing-django/#testing-a-many-to-many-relationship
    
    Title: Setting HTTP_REFERER header in Django test
    Author: Stack Overflow user supervacuo
    Date: August 5, 2012
    URL: https://stackoverflow.com/questions/11801946/setting-http-referer-header-in-django-test/11819426#11819426
    """
    def test12_add_block(self): #if we add a profile to our favorite profiles, does it work
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        url = reverse('roommates:block_add', kwargs={'id': profile2.pk})
        redirect_url = reverse('roommates:browse')
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #add the user's profile to the blocked list of profile2
        self.assertEqual(profile2.blocked.count(), 1, 
            msg='blocked users are not being removed properly') #profile2 should have blocked profile1

    def test13_default_no_blocked(self): #verify that a profile without added blocked has a count 0
        test_user1 = User.objects.get(username='testuser1')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        
        self.assertEqual(profile1.blocked.count(), 0, msg='default profile does not have empty favorites list')

    def test14_block_then_unblock(self): #check if a blocked profile is then unblocked, it is removed
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile

        url = reverse('roommates:block_add', kwargs={'id': profile2.pk})
        redirect_url = reverse('roommates:browse')
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #add the user's profile to the blocked list of profile2
        response = self.client.post(path=url, HTTP_REFERER=redirect_url) #adding to favorites again will remove profile1 from profile2's blocked list
        self.assertEqual(profile2.blocked.count(), 0, 
            msg='blocked users are not being removed properly') #profile2 should have no blocked profiles

    def test15_privacy_policy(self): #is the user (doesn't have to be logged in) seeing our privacy policy
        response = self.client.get(reverse('roommates:privacy_policy'))
        self.assertTemplateUsed(response, 'roommates/legal.html')

    def test16_default_profile_picture(self): #check that the url is the correct picture
        test_user1 = User.objects.get(username='testuser1')
        profile1 = test_user1.profile
        img_path = profile1.profile_pic.url
        expected_path = "http://res.cloudinary.com/duu2qerbq/image/upload/default_profile_pic.gif" #picture name is default_profile_pic.gif
        self.assertEqual(img_path, expected_path, msg='the path for the files is incorrect')

    def test17_filter_by_gender(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.gender='F'
        profile2.save()
        profile3.gender='F'
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'gender': 'F'}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 2)

    def test18_filter_by_name(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.first_name='Brad'
        profile2.save()
        profile3.first_name='John'
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'first_name': 'brad'}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 1)
    
    def test19_filter_by_year(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.year=2022
        profile2.save()
        profile3.year=2021
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'year': 2021}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 1)
    
    def test20_filter_by_on_grounds(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.location_general=True
        profile2.save()
        profile3.location_general=True
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'location_general': True}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 2)

    def test21_filter_by_location_specific(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.location_specific='JPA or Bice'
        profile2.save()
        profile3.location_specific='Bice'
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'location_specific': 'bice'}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 2)
    
    def test22_filter_by_major(self):
        test_user1 = User.objects.get(username='testuser1')
        test_user2 = User.objects.get(username='testuser2')
        test_user3 = User.objects.get(username='testuser3')
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        profile1 = test_user1.profile
        profile2 = test_user2.profile
        profile3 = test_user3.profile        

        profile2.major='CE'
        profile2.save()
        profile3.major='ASTR'
        profile3.save()

        qs = Profile.objects.all().exclude(id=profile1.id)        
        f = UserFilter(data={'major': 'CE'}, queryset=qs)
        result = f.qs
        self.assertEqual(result.count(), 1)
            

    def tearDown(self):
        #This deletes the test user or else the computer throws a fit
        test_user1 = User.objects.get(username='testuser1')
        test_user1.delete()
        test_user2 = User.objects.get(username='testuser2')
        test_user2.delete()
        test_user3 = User.objects.get(username='testuser3')
        test_user3.delete()
