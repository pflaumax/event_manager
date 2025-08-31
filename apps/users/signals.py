from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from apps.users.models import CustomUser
import logging

logger = logging.getLogger(__name__)

@receiver(pre_social_login)
def link_or_create_social_account(sender, request, sociallogin, **kwargs):
    """
    Link social account to existing user if email matches,
    or create a new CustomUser if not exists.
    """
    # Переконуємося, що sociallogin має акаунт
    if not hasattr(sociallogin, 'account') or not sociallogin.account:
        return

    email = sociallogin.account.extra_data.get('email')

    if not email:
        logger.warning("OAuth login attempt without email")
        return

    try:
        # Спробуємо знайти існуючого користувача по email
        existing_user = CustomUser.objects.get(email=email)
        logger.info(f"Linking OAuth account to existing user: {existing_user.email}")
        # Підключаємо соц акаунт до існуючого користувача
        sociallogin.connect(request, existing_user)

    except CustomUser.DoesNotExist:
        # Якщо користувач не існує, створюємо нового
        if not sociallogin.user or not sociallogin.user.pk:
            # Отримуємо роль з POST запиту
            user_role = 'visitor'  # За замовчуванням
            if request.method == 'POST' and 'user_role' in request.POST:
                selected_role = request.POST.get('user_role')
                if selected_role in ['visitor', 'creator']:
                    user_role = selected_role
                    logger.info(f"User selected role: {user_role}")

            # Генеруємо унікальний username
            base_username = email.split('@')[0]
            username = base_username
            counter = 1

            # Переконуємося що username унікальний
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Створюємо користувача через менеджер
            new_user = CustomUser.objects.create_user(
                email=email,
                username=username,
                role=user_role  # Використовуємо вибрану роль
            )

            # Користувачі з OAuth активні одразу
            new_user.is_active = True
            new_user.save()

            logger.info(f"Created new OAuth user: {new_user.email} with role: {user_role}")

            # Прив'язуємо створеного користувача до sociallogin
            sociallogin.user = new_user