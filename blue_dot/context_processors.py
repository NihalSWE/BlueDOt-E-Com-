from backend.models import Category,AddCart
# adjust if your model is in another app
from backend.models import Notification

def categories_processor(request):
    return {
        'global_categories': Category.objects.all()
    }
    
def cart_count_processor(request):
    session_key = request.session.session_key
    if not session_key:
        return {'cart_item_count': 0}
    
    count = AddCart.objects.filter(session_key=session_key).count()
    return {'cart_item_count': count}
    
    


def notifications(request):
    if request.user.is_authenticated:
        all_notifications = Notification.objects.filter(user=request.user)
        notifications = all_notifications.order_by('-created_at')[:3]
        unread_count = all_notifications.filter(is_read=False).count()
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_notification_count': unread_count
    }
