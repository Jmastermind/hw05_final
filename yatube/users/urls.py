from django.contrib.auth import views as auth
from django.urls import include, path

from users.views import SignUp

app_name = '%(app_label)s'

passwords = [
    path(
        'change/done/',
        auth.PasswordChangeDoneView.as_view(
            template_name='users/passwords/change/done.html',
        ),
        name='password_change_done',
    ),
    path(
        'change/form',
        auth.PasswordChangeView.as_view(
            template_name='users/passwords/change/form.html',
        ),
        name='password_change_form',
    ),
    path(
        'reset/complete/',
        auth.PasswordResetCompleteView.as_view(
            template_name='users/passwords/reset/complete.html',
        ),
        name='password_reset_complete',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth.PasswordResetConfirmView.as_view(
            template_name='users/passwords/reset/confirm.html',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth.PasswordResetDoneView.as_view(
            template_name='users/password/reset/done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/form/',
        auth.PasswordResetView.as_view(
            template_name='users/passwords/reset/form.html',
        ),
        name='password_reset_form',
    ),
]

urlpatterns = [
    path(
        'login/',
        auth.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path('passwords/', include(passwords)),
    path('signup/', SignUp.as_view(), name='signup'),
]
