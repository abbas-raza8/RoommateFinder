import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 
from cloudinary.models import CloudinaryField

"""
Title: Model Field Reference
Author: Django Staff
Code Version: 3.1
URL: https://docs.djangoproject.com/en/3.1/ref/models/fields/
Software License: 3-Clause BSD
"""
class Profile(models.Model):  
    #Fields
    """
    Title: How to Extend Django User Model
    Author: Vitor Freitas
    Date: July 22, 2016
    URL: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    """
    user = models.OneToOneField(User,on_delete=models.CASCADE,)

    first_name = models.CharField(max_length=20, default ="") #names 
    last_name = models.CharField(max_length=20, default ="") #character length can be adjusted

    FEMALE = 'F'            #gender choices
    MALE = 'M'
    NONBINARY = 'NB'
    OTHER = 'O'
    GENDER_CHOICES = [
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (NONBINARY, 'Nonbinary'),
        (OTHER, 'Other'),
    ]
    gender = models.CharField(  #gender
        max_length=2,
        choices=GENDER_CHOICES,
        default=OTHER,
    )
        

    def blank_default():
        return ""
    pronouns = models.CharField(max_length=16,null=True, blank=True,default=blank_default) #pronouns, allowed to be blank

    bio = models.TextField(max_length=500,null=True,blank=True,default=blank_default)   #biography, allowed to be blank
    
    def year_default():
        return datetime.datetime.now().year #needs both datetimes
    year = models.PositiveSmallIntegerField(default=year_default(), validators=[MinValueValidator(2021), MaxValueValidator(2024)]) #year, defaults to current year

    """
    REFERENCES
    Title: Cloudinary Documentation
    Author: Cloudinary
    URL: https://cloudinary.com/documentation/django_integration
    """
    #profile picture, needs pillow so "python3 -m pip install --upgrade Pillow", uninstall PIL if installed
    profile_pic = CloudinaryField(
        default = "default_profile_pic.gif",
        unique_filename = False,
        use_filename = True,


        )#models.ImageField(default='default_profile_pic.gif', upload_to='')
    
    location_general = models.BooleanField(default=True) #general location. Do you want to live on or off grounds (yes=on grounds, no=off grounds)
    location_specific = models.TextField(max_length=200, blank=True,default=blank_default) 
    
    
    relation_status = models.BooleanField(default=True) #relationship Status, do you want to be close with your roommate yes/no

    room_status = models.BooleanField(default=True) #Are you still looking for a roommate? yes/no
    favorites=models.ManyToManyField(User, related_name="favorite", default=None, blank=True)
    blocked=models.ManyToManyField(User, related_name="block", default=None, blank=True)

    #This is the major field, it is very long, list. Majors are from: https://www.virginia.edu/academics/majors
    MAJOR_LIST = [ #With the exception of Unknown and Other, majors are listed alphabetically
        ('UKN', 'Unknown'),
        ('OTH', 'Other'),
        ('AE', 'Aerospace Engineering'),
        ('AAAS', 'African American and African Studies'),
        ('AS', 'American Studies'),
        ('ANT','Anthropology'),
        ('ACE', 'Archaeology'),
        ('ARCH', 'Architectural History'),
        ('ARC', 'Architecture'),
        ('ASTR', 'Astronomy'),
        ('BIS', 'Bachelor of Interdisciplinary Studies'),
        ('BPS', 'Bachelor of Professional Studies in Health Sciences Management'),
        ('BIO', 'Biology'),
        ('BME', 'Biomedical Engineering'),
        ('CHE', 'Chemical Engineering'),
        ('CHEM', 'Chemistry'),
        ('CIVE', 'Civil Engineering'),
        ('CLAS', 'Classics'),
        ('COGS', 'Cognitive Science'),
        ('COMM', 'Commerce'),
        ('CMPL', 'Comparative Literature'),
        ('CE', 'Computer Engineering'),
        ('CS', 'Computer Science'),
        ('DAN', 'Dance'),
        ('DRA', 'Drama'),
        ('EALL', 'East Asian Languages, Literatures and Culture'),
        ('ECON', 'Economics'),
        ('EEE', 'Electrical Engineering'),
        ('ES', 'Engineering Science'),
        ('ENGL', 'English'),
        ('ENVR', 'Environmental Sciences'),
        ('ETP', 'Environmental Thought and Practice'),
        ('TEP', 'Five-Year Teacher Education Program'),
        ('FREN', 'French'),
        ('GERM', 'German'),
        ('GEMS', 'German Studies'),
        ('GBL', 'Global Studies'),
        ('HIST', 'History'),
        ('HOA', 'History of Art'),
        ('HBIO', 'Human Biology'),
        ('IMGS', 'Interdisciplinary Major of Global Studies'),
        ('JS', 'Jewish Studies'),
        ('KINE', 'Kinesiology'),
        ('LAS', 'Latin American Studies'),
        ('LING', 'Linguistics'),
        ('MSE', 'Materials Science and Engineering'),
        ('MATH', 'Mathematics'),
        ('MECH', 'Mechanical Engineering'),
        ('MEDA', 'Media Studies'),
        ('MEDS', 'Medieval Studies'),
        ('MESA', 'Middle Eastern and South Asian Languages and Cultures'),
        ('MUS', 'Music'),
        ('NEUR', 'Neuroscience'),
        ('NURS', 'Nursing'),
        ('PHIL', 'Philosophy'),
        ('PHYS', 'Physics'),
        ('PST', 'Political and Social Thought'),
        ('PPPL', 'Political Philosophy, Policy, and Law'),
        ('POL', 'Politics'),
        ('PSYC', 'Psychology'),
        ('RS', 'Religious Studies'),
        ('SLL', 'Slavic Languages and Literatures'),
        ('S', 'Sociology'),
        ('SPAN', 'Spanish'),
        ('SCD', 'Speech Communication Disorders'),
        ('STAT', 'Statistics'),
        ('SA', 'Studio Art'),
        ('SYS', 'Systems Engineering'),
        ('UEP', 'Urban and Environmental Planning'),
        ('WGS', 'Women, Gender & Sexuality'),
        ('YSI', 'Youth & Social Innovation'),
    ]
    major = models.CharField( #the default major for a profile is unknown
        max_length=4,
        choices=MAJOR_LIST,
        default='UKN',
    )
    is_favorited = False
    #Meta
    class Meta:
        ordering  = ['last_name', 'first_name'] #default ordering by last name, first name

    #functions
    def __str__(self):
        return self.first_name + " " + self.last_name

    def is_same_gender(other_person): #method to check whether a user is the same gender
        return other_person.gender == self.gender

    def is_same_year(other_person): #method to check whether the user is in the same year
        return other_person.year == self.year

    """
    Title: How to Extend Django User Model
    Author: Vitor Freitas
    Date: July 22, 2016
    URL: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    """
    #This code says create a default profile for new users
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

"""
Title: How to create a user to user message system using Django?
Author: Stack Overflow user Ancho
Date: September 21, 2015
URL: https://stackoverflow.com/a/32688863
"""
class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, related_name="receiver", on_delete=models.CASCADE)
    msg_content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
