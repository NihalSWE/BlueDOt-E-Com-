from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.models import Notification, Order, MaterialInventoryDetail, PartyRegSupplier, CustomerInfo

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Welcome to our platform!",
            message="Thank you for registering with us.",
            notification_type='success',
            icon='ri-user-add-line'  # User icon
        )

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    if created:
        # Notify admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title="New Order Created",
                message=f"Order #{instance.id} was placed by {instance.customer}",
                notification_type='info',
                icon='ri-shopping-cart-line'  # Order icon
            )

        # Notify customer if they have a user account
        if hasattr(instance.customer, 'user') and instance.customer.user:
            Notification.objects.create(
                user=instance.customer.user,
                title="Order Confirmation",
                message=f"Your order #{instance.id} has been received",
                notification_type='success',
                icon='ri-check-line',  # Approval icon
                url=f"/orders/{instance.id}/"
            )

@receiver(post_save, sender=MaterialInventoryDetail)
def notify_inventory_change(sender, instance, created, **kwargs):
    action = None
    icon = None

    if instance.mid_deal_type == 'buy':
        action = "purchased"
        icon = 'ri-shopping-cart-line'  # Order icon for purchase
    elif instance.mid_deal_type == 'sell':
        action = "sold"
        icon = 'ri-shopping-cart-line'  # Same icon, or choose differently if you want

    if not action:
        return

    title = f"Inventory {action.capitalize()}"
    quantity = instance.mid_buy_quentity if action == 'purchased' else instance.mid_sell_quentity
    message = f"Material {instance.mid_material} was {action} in quantity {quantity}."
    
    url = reverse('material_purchase_list')  # Link to your material purchase list

    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title=title,
            message=message,
            notification_type='info',
            icon=icon,
            url=url
        )

@receiver(post_save, sender=PartyRegSupplier)
def notify_supplier_created(sender, instance, created, **kwargs):
    if created:
        title = "New Supplier Created"
        message = f"Supplier {instance.prs_name} (ID: {instance.prs_slid}) has been registered."
        url = reverse('party_supplier_list')
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title=title,
                message=message,
                notification_type='info',
                icon='ri-user-add-line',  # User icon for supplier
                url=url
            )

@receiver(post_save, sender=CustomerInfo)
def notify_customer_created(sender, instance, created, **kwargs):
    if created:
        title = "New Customer Registered"
        message = f"Customer {instance.CustomerName} (ID: {instance.CustomerID}) has been added."
        url = reverse('customer_list')  # Replace with your customer list URL name
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title=title,
                message=message,
                notification_type='info',
                icon='ri-user-add-line',  # User icon for customer
                url=url
            )
