from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from apps.users.models import CustomUser


@receiver(pre_social_login)
def link_social_account(sender, request, sociallogin, **kwargs):
    """
    Link social account to existing user if email matches.
    """
    if not hasattr(sociallogin, 'account') or not sociallogin.account:
        return

    email = sociallogin.account.extra_data.get('email')

    if email:
        try:
            existing_user = CustomUser.objects.get(email=email)
            sociallogin.connect(request, existing_user)

        except CustomUser.DoesNotExist:
            if not sociallogin.user or not sociallogin.user.pk:
                sociallogin.user = CustomUser.create_from_social_account(sociallogin.account)