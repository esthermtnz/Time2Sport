from slegpn.models import Notification


def unread_notifications(request):
    """Gets the unread notification count"""
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user, read=False).count()
        return {'unread_notifications': count}
    return {}
