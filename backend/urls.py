from django.urls import path
from . import views
# from . import views_admin
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # home page
    # path('home',views.home,name='admin-home'),
    path('home/banner/',views.home_banner,name='home_banner'),
    path('home/practice-area/',views.practice_area,name='practice_area'),
    path('home/practice-area-create/',views.practice_area_create, name='practice_area_create'),
    path('home_CTA',views.home_CTA,name='home_CTA'),
    path('pricing_card',views.pricing_card,name='pricing_card'),
    path('cart_banner',views.cart_banner,name="cart_banner"),

    path('home_centerCard',views.home_centerCard,name='home_centerCard'),
    path('home-center-card/edit/<int:card_id>/', views.edit_center_card, name='edit_center_card'),
    path('home-center-card/delete/<int:card_id>/', views.delete_center_card, name='delete_center_card'),
    # Home
    
    path('contactUs',views.contactUs,name='contactUs'),
    path('contactUs_location',views.contactUs_location,name='contactUs_location'),
    path('contactUs_msg',views.contactUs_msg,name   ='contactUs_msg'),
    
    path('aboutUs_banner',views.aboutUs_banner,name='aboutUs_banner'),
    path('aboutUs_aboutarea',views.aboutUs_aboutarea,name='aboutUs_aboutarea'),
    path('aboutUs_callToaction',views.aboutUs_callToaction,name='aboutUs_callToaction'),
    path('aboutUs_chooseUs',views.aboutUs_chooseUs,name='aboutUs_chooseUs'),
    path('aboutus_faq',views.aboutus_faq,name='aboutus_faq'),
    
    # Categories urls
    path('category-list/', views.category_list, name='category_list'),
    path('category-create/',views.category_create,name='category_create'),
    path('category-update/<int:pk>/',views.update_category,name='update_category'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    # Categories urls
    
    # Users
    path('user-list/', views.user_list, name='user_list'),
    path('update-user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'), 
    # Users
    
    
    # Unit urls
    path('unit-list/', views.units, name='units'),
    # Unit urls
    
    
    # Products urls
    path('product-list/', views.product_list, name='product_list'),
    path('product-create/',views.product_create,name='product_create'),
    path('category-update/<int:pk>/',views.update_category,name='update_category'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('product_banner',views.product_banner,name='product_banner'),
    path('product_review',views.product_review,name='product_review'),
    # Products urls
    
    # Brands urls
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/create/', views.brand_create, name='brand_create'),
    path('brands/edit/<int:pk>/', views.brand_update, name='brand_edit'),
    path('brands/delete/<int:pk>/', views.brand_delete, name='brand_delete'),
    # Brands urls
    
    
    # Order urls
    path('order_list',views.order_list,name='order_list'),
    path('initial-orders',views.initial_orders,name='initial_orders'),
    path('initial-order-create',views.initial_order_create,name='initial_order_create'),
    path('initial-order-update/<int:id>/',views.initial_order_update,name='initial_order_update'),
    path('approve-order/<int:id>',views.approve_order,name='approve_order'),
    path('orders/<int:order_id>/product/<int:product_id>/materials/', views.get_materials_by_product, name='get_materials_by_product'),
    path('order_detail/<int:id>',views.order_detail,name='order_detail'),
    # Order urls
    
    path('product_list/',views.product_list,name='product_list'),
    path('add_product/',views.add_product,name='add_product'),
    path('category_list',views.category_list,name='category_list'),
    
    path('order_detail',views.order_detail,name='order_detail'),
    path('customer_list',views.customer_list,name='customer_list'),
    path('customer_overview',views.customer_overview,name='customer_overview'),
    path('security',views.security,name='security'),
    path('billing',views.billing,name='billing'),
    path('notification',views.notification,name='notification'),
    path('store_details',views.store_details,name='store_details'),
    path('payments',views.payments,name='payments'),
    path('checkout',views.checkout,name='checkout'),
    path('shipping',views.shipping,name='shipping'),
    path('location',views.location,name='location'),
    path('setting_notification',views.setting_notification,name='setting_notification'),
    path('invoice_add',views.invoice_add,name='invoice_add'),
    path('invoice_edit',views.invoice_edit,name='invoice_edit'),
    path('invoice_preview',views.invoice_preview,name='invoice_preview'),
    path('invoice_list',views.invoice_list,name='invoice_list'),
    path('access_roles',views.access_roles,name='access_roles'),
    path('access_permission',views.access_permission,name='access_permission'),
    
    # FAQ
    path('Ourfaq_banner',views.Ourfaq_banner,name='Ourfaq_banner'),
    path('Ourfaq_faqs',views.Ourfaq_faqs,name='Ourfaq_faqs'),

     path('suppliers/', views.party_supplier_list, name='party_supplier_list'),
    path('suppliers/create/', views.party_supplier_create, name='party_supplier_create'),
    path('suppliers/<str:slid>/', views.party_supplier_detail, name='party_supplier_detail'),
    path('suppliers/<str:slid>/update/', views.party_supplier_update, name='party_supplier_update'),
    path('suppliers/<str:slid>/delete/', views.party_supplier_delete, name='party_supplier_delete'),
    path('material-type/', views.material_type_list, name='material_type_list'),            # To show the list page with modals
    path('material-type/create/', views.material_type_create, name='material_type_create'), # To handle create POST
    path('material-type/<int:id>/update/', views.material_type_update, name='material_type_update'),
    path('material-type/<int:id>/delete/', views.material_type_delete, name='material_type_delete'), # To handle delete POST
    path('material/', views.material_list, name='material_list'),
    path('material/create/', views.material_create, name='material_create'),
    path('material/<int:id>/update/', views.material_update, name='material_update'),
    path('material/<int:id>/delete/', views.material_delete, name='material_delete'),

    path('materials/', views.material_list, name='material_list'),              # List all materials
    path('materials/create/', views.material_create, name='material_create'),   # Create a new material
    path('materials/<int:id>/update/', views.material_update, name='material_update'),  # Update a material
    path('materials/<int:id>/delete/', views.material_delete, name='material_delete'),  # Delete a material

    path('material-purchases/', views.material_purchase_list, name='material_purchase_list'),           # List all purchases
    path('material-purchases/create/', views.material_purchase_create, name='material_purchase_create'), # Create purchase
    path('material-purchases/<int:id>/update/', views.material_purchase_update, name='material_purchase_update'),  # Update purchase
    path('material-purchases/<int:id>/delete/', views.material_purchase_delete, name='material_purchase_delete'),  # Delete purchase

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/update/<int:id>/', views.customer_update, name='customer_update'),
    path('customers/delete/<int:id>/', views.customer_delete, name='customer_delete'),
    # WareHouse


    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/update/<int:id>/', views.warehouse_update, name='warehouse_update'),
    path('warehouses/delete/<int:id>/', views.warehouse_delete, name='warehouse_delete'),  # 👈 Add this
    
    
    path('reports/inventory-stock/', views.inventory_stock_report, name='inventory_stock_report'),
    path('report/daily-report/', views.daily_purchase_report, name='daily_purchase_report'),
     path('report/low-stock-report/', views.low_stock_report, name='low_stock_report'),

    path('reports/material-transactions/', views.material_transactions_report, name='material_transactions_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/product-material-usage/', views.product_material_usage_report, name='product_material_usage_report'),
    path('customer-report/', views.customer_report, name='customer_report'),
    path('reports/profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    path('supplier/<str:supplier_id>/', views.supplier_detail, name='supplier_detail'),
      path('reports/daily-sell/', views.daily_sell_report, name='daily_sell_report'),
    
    
    path('home_CTA',views.home_CTA,name='home_CTA'),
    path('pricing_card',views.pricing_card,name='pricing_card'),
    
    
    
    path('discount-categories/', views.discount_category_list, name='discount_category_list'),
    path('discount-categories/create/', views.discount_category_create, name='discount_category_create'),
    path('discount-categories/update/<int:pk>/', views.discount_category_update, name='discount_category_update'),
    path('discount-categories/delete/<int:pk>/', views.discount_category_delete, name='discount_category_delete'),
    # Discount URLs
    path('discounts/', views.discount_list, name='discount_list'),
    path('discounts/create/', views.discount_create, name='discount_create'),
    path('discounts/update/<int:pk>/', views.discount_update, name='discount_update'),
    path('discounts/delete/<int:pk>/', views.discount_delete, name='discount_delete'),
    
    
     # Blog urls
    path('blog_banner/', views.blog_banner, name='blog_banner'),
    path('blog_post/', views.blog_post, name='blog_post'),
    path('blog_post/create/', views.create_or_update_post, name='blog_create'),
    path('blog_post/<int:id>/', views.get_post, name='blog_get'),
    path('blog_post/delete/<int:id>/', views.delete_post, name='blog_delete'),
    # Add this for CKEditor image uploads
    path('ckeditor/upload/', views.ckeditor_upload, name='ckeditor_upload'),
    
    path('blog_comments',views.blog_comments,name='blog_comments'),
      path('last-orders/', views.last_10_orders_api, name='api-last-orders'),
    
    # Blog urls
    
     #checkout#
    path('checkout_banner',views.checkout_banner,name='checkout_banner'),
    path('order_summary',views.order_summary,name='order_summary'),
    path('delete-order/', views.delete_order, name='delete_order'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),
    

    #checkout#
    path('supplier-payment/', views.supplier_payment, name='supplier_payment'),
    path('get-invoices/', views.get_invoices_for_party, name='get_invoices_for_party'),
    path('get-invoice-details/', views.get_invoice_details, name='get_invoice_details'),
    path('purchase/<int:purchase_id>/invoice/', views.invoice_purchase, name='invoice_purchase'),
    path('purchase/<int:purchase_id>/invoice/print/', views.print_invoice_purchase, name='print_invoice_purchase'),
    
    
    #search banner
    path('search_banner/', views.search_banner, name='search_banner'),
    #search banner 
    
    #thankyou banner
    path('thankyou_banner/', views.thankyou_banner, name='thankyou_banner'),
    #thankyou banner
]