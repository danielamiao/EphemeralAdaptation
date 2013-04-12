EphemeralAdaptation
===================

This is a project for 6.831 UI Design and Implementation Class Assignment RS1, it reproduces an ephemeral adaptation menu experiment from the paper http://terpconnect.umd.edu/~leahkf/pubs/CHI2009-findlater-ephemeral.pdf and uses Python+Django with Javascript/jQuery and AJAX support. The interface uses minimal Twitter Bootstrap as well.

===================
Collaborators: None except for discussions on Piazza

Youtube URL of live demo: http://www.youtube.com/watch?v=bL__5kXQIQY

Live Demo URL: http://dmiao.scripts.mit.edu/6831/rs/ea/

===================
Browser: Tested on Chrome, may work on Firefox and other browers

Platform Requirement: Ubuntu Linux (if running server locally)

Other Software: Django Version 1.4.3 (if running server locally)

===================
Instructions (for running server locally):

1. Assume Django 1.4.3 is installed correctly, edit the 
rs/local_settings.py file to reflect your own local development
configurations. Never commit this file to the repo!

2. Initialize your development database using "python manage.py syncdb"

3. Start the server by "python manage.py runserver"

4. You should now be able to access the project at the port specified
in your local_settings.py or settings.py, most often this will be 
http://localhost:8000/ea/

===================
Suggested Reading Material for Troubleshooting:

1. Django Tutorial (for Django): https://docs.djangoproject.com/en/1.5/intro/tutorial01/

2. If you do not wish for multiple Django versions to conflict, a common way is to use
virtualenvwrapper. A useful tutorial: http://www.jeffknupp.com/blog/2012/10/24/starting-a-django-14-project-the-right-way/

3. Twitter Bootstrap was used minimally to improve the general aesthetics a bit:
http://twitter.github.io/bootstrap/
