from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import redirect
from django.contrib.auth.models import User
from datetime import timedelta

@receiver(user_logged_in)
def first_login_redirect(sender, request, user, **kwargs):

    if user.is_authenticated and abs((user.date_joined - user.last_login).total_seconds()) < 5:
        request.session['first_login'] = True  