This folder contains traduction files for FlOpEDT.

For the time being English is the only non-native language supported.

More info on how to add a internationalised text [here](https://docs.djangoproject.com/en/2.1/topics/i18n/translation/).

After adding new internationalised strings, you have to do the following:
* go in the FlOpEDT folder
* run `django-admin makemessages -l en`  
It will create the file `FlOpEDT/locale/en/LC_MESSAGES/django.po`
* Edit this file and translate sentences
* run `django-admin compilemessages`  
It compiles `django.po` to be used by Django
The resulting file is `django.mo`

Now you can invite your English-speaking friends to enjoy FlOpEDT!

