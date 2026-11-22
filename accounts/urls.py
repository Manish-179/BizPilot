
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views


urlpatterns = [
                    
    path('register/', views.register_view, name='register'),
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(next_page='login'),
        name='logout'
    ),

               
    path('accounts/profile/', views.dashboard_view, name='dashboard'),

                         
    path('businesses/', views.business_list_view, name='business_list'),
    path('businesses/add/', views.add_business_view, name='add_business'),
    path(
        'businesses/<int:business_id>/edit/',
        views.edit_business_view,
        name='edit_business'
    ),
    path(
        'businesses/<int:business_id>/delete/',
        views.delete_business_view,
        name='delete_business'
    ),

                         
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path(
        'customers/<int:customer_id>/edit/',
        views.edit_customer_view,
        name='edit_customer'
    ),
    path(
        'customers/<int:customer_id>/delete/',
        views.delete_customer_view,
        name='delete_customer'
    ),

                     
    path('leads/', views.lead_list_view, name='lead_list'),
    path('leads/add/', views.add_lead_view, name='add_lead'),
    path(
        'leads/<int:lead_id>/edit/',
        views.edit_lead_view,
        name='edit_lead'
    ),
    path(
        'leads/<int:lead_id>/delete/',
        views.delete_lead_view,
        name='delete_lead'
    ),
    path(
        'leads/<int:lead_id>/update-status/',
        views.update_lead_status_view,
        name='update_lead_status'
    ),

                        
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.add_product_view, name='add_product'),
    path(
        'products/<int:product_id>/edit/',
        views.edit_product_view,
        name='edit_product'
    ),
    path(
        'products/<int:product_id>/delete/',
        views.delete_product_view,
        name='delete_product'
    ),

                      
    path('brands/', views.brand_list_view, name='brand_list'),
    path(
        'brands/<int:business_id>/setup/',
        views.brand_setup_view,
        name='brand_setup'
    ),

                
    path(
        'storefront/<int:business_id>/',
        views.storefront_view,
        name='storefront'
    ),
    path(
        'storefront/<int:business_id>/enquiry/',
        views.storefront_enquiry_view,
        name='storefront_enquiry'
    ),

                
    path('automation/', views.automation_view, name='automation'),
    path(
        'automation/complete/<int:lead_id>/',
        views.complete_follow_up_view,
        name='complete_follow_up'
    ),

                  
    path('auto-replies/', views.auto_reply_list_view, name='auto_reply_list'),
    path('auto-replies/add/', views.add_auto_reply_view, name='add_auto_reply'),
    path(
        'auto-replies/<int:reply_id>/edit/',
        views.edit_auto_reply_view,
        name='edit_auto_reply'
    ),
    path(
        'auto-replies/<int:reply_id>/delete/',
        views.delete_auto_reply_view,
        name='delete_auto_reply'
    ),

               
    path('analytics/', views.analytics_view, name='analytics'),

              
    path('settings/', views.settings_view, name='settings'),
    path('ai/product-description/', views.ai_generate_product_description_view, name='ai_generate_product_description'),
    path('ai-assistant/', views.ai_chatbot_view, name='ai_chatbot'),
]
