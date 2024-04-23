from django.conf import settings


def admin_email_context(request):
    is_specific_admin = request.user.is_authenticated and request.user.email == settings.ADMIN_EMAIL
    return {'is_specific_admin': is_specific_admin}
