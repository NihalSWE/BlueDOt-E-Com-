# utils.py (in your existing app)
from django.contrib.contenttypes.models import ContentType
from backend.models import Notification
from backend.models import User
def create_notification(user, title, message, notification_type='info', icon=None, url=None):
    """
    Create a notification for a user
    """
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        icon=icon or 'ri-notification-2-line',
        url=url
    )

def notify_admins(title, message, notification_type='info', icon=None):
    """
    Send notification to all admin users
    """
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        create_notification(
            user=admin,
            title=title,
            message=message,
            notification_type=notification_type,
            icon=icon
        )