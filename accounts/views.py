import json

import re
from urllib.parse import quote

from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import (
    RegisterForm,
    BusinessForm,
    CustomerForm,
    LeadForm,
    ProductForm,
    BrandForm,
    AutoReplyForm,
    UserProfileForm,
    UserSettingsForm,
)

from .ai_services import generate_gemini_text, GeminiAPIError

from .models import (
    Business,
    Customer,
    Lead,
    Product,
    Brand,
    AutoReply,
    UserSettings,
)


                                                           
                    
                                                           

def add_lead_contact_links(leads):
    for lead in leads:
        phone = re.sub(r"\D", "", lead.phone or "")

        lead.call_url = f"tel:+{phone}" if phone else ""

        if phone:
            message = (
                f"Hello {lead.name}, "
                f"we are following up regarding your enquiry "
                f"with {lead.business.name}. "
                f"How can we help you?"
            )

            lead.whatsapp_url = (
                f"https://wa.me/{phone}?text={quote(message)}"
            )
        else:
            lead.whatsapp_url = ""

    return leads


                                                           
          
                                                           

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


                                                           
           
                                                           

@login_required
def dashboard_view(request):
    businesses = Business.objects.filter(owner=request.user)

                                                 
    user_settings, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    total_businesses = businesses.count()

    total_customers = Customer.objects.filter(
        business__owner=request.user
    ).count()

    total_products = Product.objects.filter(
        business__owner=request.user
    ).count()

    total_leads = Lead.objects.filter(
        business__owner=request.user
    ).count()

    converted_leads = Lead.objects.filter(
        business__owner=request.user,
        status='converted'
    ).count()

    conversion_rate = (
        round((converted_leads / total_leads) * 100, 2)
        if total_leads > 0 else 0
    )

    recent_leads = Lead.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')[:5]

    now = timezone.now()

    upcoming_followups = Lead.objects.filter(
        business__owner=request.user,
        follow_up_at__isnull=False,
        follow_up_at__gte=now,
        follow_up_completed=False
    ).select_related('business').order_by('follow_up_at')[:5]

    overdue_followups = Lead.objects.filter(
        business__owner=request.user,
        follow_up_at__isnull=False,
        follow_up_at__lt=now,
        follow_up_completed=False
    ).count()

    pending_followups = Lead.objects.filter(
        business__owner=request.user,
        follow_up_at__isnull=False,
        follow_up_at__gte=now,
        follow_up_completed=False
    ).count()

    return render(request, 'accounts/dashboard.html', {
        'businesses': businesses,
        'total_businesses': total_businesses,
        'total_customers': total_customers,
        'total_products': total_products,
        'total_leads': total_leads,
        'converted_leads': converted_leads,
        'conversion_rate': conversion_rate,
        'recent_leads': recent_leads,
        'upcoming_followups': upcoming_followups,
        'overdue_followups': overdue_followups,
        'pending_followups': pending_followups,
        'user_settings': user_settings,
    })


@login_required
def business_list_view(request):
    businesses = Business.objects.filter(owner=request.user)

    return render(request, 'accounts/business_list.html', {
        'businesses': businesses,
        'category_choices': Business.Category.choices,
    })


@login_required
def add_business_view(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)

        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return redirect('business_list')
    else:
        form = BusinessForm()

    return render(request, 'accounts/add_business.html', {
        'form': form
    })


@login_required
def edit_business_view(request, business_id):
    business = get_object_or_404(
        Business,
        id=business_id,
        owner=request.user
    )

    if request.method == 'POST':
        form = BusinessForm(request.POST, instance=business)

        if form.is_valid():
            form.save()
            return redirect('business_list')
    else:
        form = BusinessForm(instance=business)

    return render(request, 'accounts/edit_business.html', {
        'form': form,
        'business': business
    })


@login_required
def delete_business_view(request, business_id):
    business = get_object_or_404(
        Business,
        id=business_id,
        owner=request.user
    )

    if request.method == 'POST':
        business.delete()
        return redirect('business_list')

    return render(request, 'accounts/delete_business.html', {
        'business': business
    })


                                                           
                     
                                                           

@login_required
def customer_list_view(request):
    customers = Customer.objects.filter(
        business__owner=request.user
    ).select_related('business')

    return render(request, 'accounts/customer_list.html', {
        'customers': customers
    })


@login_required
def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(user=request.user)

    return render(request, 'accounts/add_customer.html', {
        'form': form
    })


@login_required
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        form = CustomerForm(
            request.POST,
            instance=customer,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(
            instance=customer,
            user=request.user
        )

    return render(request, 'accounts/edit_customer.html', {
        'form': form,
        'customer': customer
    })


@login_required
def delete_customer_view(request, customer_id):
    customer = get_object_or_404(
        Customer,
        id=customer_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')

    return render(request, 'accounts/delete_customer.html', {
        'customer': customer
    })


                                                           
                 
                                                           

@login_required
def lead_list_view(request):
    leads = Lead.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')

    leads = add_lead_contact_links(leads)

    total_leads = leads.count()
    new_leads = leads.filter(status='new').count()
    converted_leads = leads.filter(status='converted').count()
    lost_leads = leads.filter(status='lost').count()

    return render(request, 'accounts/lead_list.html', {
        'leads': leads,
        'total_leads': total_leads,
        'new_leads': new_leads,
        'converted_leads': converted_leads,
        'lost_leads': lost_leads,
        'status_choices': Lead.Status.choices,
    })


@login_required
def add_lead_view(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)

        if form.is_valid():
            lead = form.save(commit=False)

            country_code = request.POST.get(
                'country_code', '+91'
            ).strip()

            allowed_codes = [
                '+91', '+1', '+44', '+971', '+61', '+92',
                '+880', '+977', '+94', '+81', '+86', '+49',
                '+33', '+39', '+34', '+7', '+55', '+27',
                '+966', '+974', '+965', '+968', '+60', '+65',
                '+66', '+62', '+63', '+84', '+82', '+90',
                '+20', '+234', '+254', '+353', '+31', '+41',
                '+46', '+47', '+48', '+351', '+52', '+64'
            ]

            if country_code not in allowed_codes:
                country_code = '+91'

            phone_number = (lead.phone or '').strip()

            if phone_number and not phone_number.startswith('+'):
                lead.phone = f"{country_code} {phone_number}"

            lead.save()
            return redirect('lead_list')

    else:
        form = LeadForm(user=request.user)

    return render(request, 'accounts/add_lead.html', {
        'form': form
    })


@login_required
def edit_lead_view(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        business__owner=request.user
    )

    country_codes = [
        '+91', '+1', '+44', '+971', '+61', '+92',
        '+880', '+977', '+94', '+81', '+86', '+49',
        '+33', '+39', '+34', '+7', '+55', '+27',
        '+966', '+974', '+965', '+968', '+60', '+65',
        '+66', '+62', '+63', '+84', '+82', '+90',
        '+20', '+234', '+254', '+353', '+31', '+41',
        '+46', '+47', '+48', '+351', '+52', '+64'
    ]

    existing_phone = (lead.phone or '').strip()
    existing_code = '+91'
    phone_number = existing_phone

    for code in sorted(country_codes, key=len, reverse=True):
        if existing_phone.startswith(code + ' '):
            existing_code = code
            phone_number = existing_phone[len(code):].strip()
            break

    if request.method == 'POST':
        original_follow_up_at = lead.follow_up_at

        form = LeadForm(
            request.POST,
            instance=lead,
            user=request.user
        )

        if form.is_valid():
            updated_lead = form.save(commit=False)

            country_code = request.POST.get(
                'country_code', '+91'
            ).strip()

            if country_code not in country_codes:
                country_code = '+91'

            phone = (updated_lead.phone or '').strip()

            for code in sorted(country_codes, key=len, reverse=True):
                if phone.startswith(code + ' '):
                    phone = phone[len(code):].strip()
                    break

            if phone and not phone.startswith('+'):
                updated_lead.phone = f'{country_code} {phone}'

            if updated_lead.follow_up_at != original_follow_up_at:
                updated_lead.follow_up_completed = False
                updated_lead.reminder_sent_at = None
                updated_lead.overdue_alert_sent_at = None

            updated_lead.save()

            messages.success(
                request,
                'Lead updated successfully.'
            )

            return redirect('lead_list')

    else:
        form = LeadForm(
            instance=lead,
            user=request.user
        )

        form.initial['phone'] = phone_number

    return render(request, 'accounts/edit_lead.html', {
        'form': form,
        'lead': lead,
        'selected_country_code': existing_code
    })


@login_required
def update_lead_status_view(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        new_status = request.POST.get('status', '').strip()
        allowed_statuses = dict(Lead.Status.choices)

        if new_status in allowed_statuses:
            lead.status = new_status
            lead.save(update_fields=['status', 'updated_at'])

            messages.success(
                request,
                'Lead status updated successfully.'
            )
        else:
            messages.error(
                request,
                'Invalid lead status.'
            )

    return redirect('lead_list')


@login_required
def delete_lead_view(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        lead.delete()
        return redirect('lead_list')

    return render(request, 'accounts/delete_lead.html', {
        'lead': lead
    })


                                                           
                    
                                                           

@login_required
def product_list_view(request):
    products = Product.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')

    return render(request, 'accounts/product_list.html', {
        'products': products
    })


@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(user=request.user)

    return render(request, 'accounts/add_product.html', {
        'form': form
    })


@login_required
def edit_product_view(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(
            instance=product,
            user=request.user
        )

    return render(request, 'accounts/edit_product.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        product.delete()
        return redirect('product_list')

    return render(request, 'accounts/delete_product.html', {
        'product': product
    })


                                                           
                  
                                                           

@login_required
def brand_list_view(request):
    businesses = Business.objects.filter(
        owner=request.user
    ).order_by('-created_at')

    brands = Brand.objects.filter(
        business__owner=request.user
    ).select_related('business')

    return render(request, 'accounts/brand_list.html', {
        'businesses': businesses,
        'brands': brands
    })


@login_required
def brand_setup_view(request, business_id):
    business = get_object_or_404(
        Business,
        id=business_id,
        owner=request.user
    )

    brand, created = Brand.objects.get_or_create(
        business=business
    )

    if request.method == 'POST':
        form = BrandForm(
            request.POST,
            request.FILES,
            instance=brand,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm(
            instance=brand,
            user=request.user
        )

    form.fields['business'].queryset = Business.objects.filter(
        id=business.id,
        owner=request.user
    )

    return render(request, 'accounts/brand_setup.html', {
        'form': form,
        'business': business,
        'brand': brand
    })


                                                           
                   
                                                           

def storefront_view(request, business_id):
    business = get_object_or_404(
        Business,
        id=business_id
    )

    brand = get_object_or_404(
        Brand,
        business=business,
        storefront_enabled=True
    )

    products = Product.objects.filter(
        business=business,
        is_published=True
    ).order_by('-created_at')

    whatsapp_number = ''.join(
        char for char in (business.phone or '')
        if char.isdigit()
    )

    return render(request, 'accounts/storefront.html', {
        'business': business,
        'brand': brand,
        'products': products,
        'whatsapp_number': whatsapp_number,
    })


                                                           
                                  
                                                           

@login_required
def automation_view(request):
    now = timezone.now()

    follow_ups = Lead.objects.filter(
        business__owner=request.user,
        follow_up_at__isnull=False,
        follow_up_completed=False
    ).select_related('business').order_by('follow_up_at')

    follow_ups = add_lead_contact_links(follow_ups)

    overdue_count = follow_ups.filter(
        follow_up_at__lt=now
    ).count()

    upcoming_count = follow_ups.filter(
        follow_up_at__gte=now
    ).count()

    return render(request, 'accounts/automation.html', {
        'follow_ups': follow_ups,
        'overdue_count': overdue_count,
        'upcoming_count': upcoming_count,
        'now': now,
    })


@login_required
def complete_follow_up_view(request, lead_id):
    lead = get_object_or_404(
        Lead,
        id=lead_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        lead.follow_up_completed = True
        lead.save(update_fields=['follow_up_completed'])

        messages.success(
            request,
            'Follow-up marked as completed.'
        )

    return redirect('automation')


                                                           
                       
                                                           

@login_required
def auto_reply_list_view(request):
    auto_replies = AutoReply.objects.filter(
        business__owner=request.user
    ).select_related('business').order_by('-created_at')

    return render(request, 'accounts/auto_reply_list.html', {
        'auto_replies': auto_replies
    })


@login_required
def add_auto_reply_view(request):
    if request.method == 'POST':
        form = AutoReplyForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('auto_reply_list')
    else:
        form = AutoReplyForm(user=request.user)

    return render(request, 'accounts/add_auto_reply.html', {
        'form': form
    })


@login_required
def edit_auto_reply_view(request, reply_id):
    auto_reply = get_object_or_404(
        AutoReply,
        id=reply_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        form = AutoReplyForm(
            request.POST,
            instance=auto_reply,
            user=request.user
        )

        if form.is_valid():
            form.save()
            return redirect('auto_reply_list')
    else:
        form = AutoReplyForm(
            instance=auto_reply,
            user=request.user
        )

    return render(request, 'accounts/edit_auto_reply.html', {
        'form': form,
        'auto_reply': auto_reply
    })


@login_required
def delete_auto_reply_view(request, reply_id):
    auto_reply = get_object_or_404(
        AutoReply,
        id=reply_id,
        business__owner=request.user
    )

    if request.method == 'POST':
        auto_reply.delete()
        return redirect('auto_reply_list')

    return render(request, 'accounts/delete_auto_reply.html', {
        'auto_reply': auto_reply
    })


                                                           
                    
                                                           

def storefront_enquiry_view(request, business_id):
    business = get_object_or_404(
        Business,
        id=business_id
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        notes = request.POST.get('notes', '').strip()

        if name and phone:
            Lead.objects.create(
                business=business,
                name=name,
                phone=phone,
                email=email,
                source='form',
                status='new',
                notes=notes
            )

            return redirect(
                'storefront',
                business_id=business.id
            )

    return render(request, 'accounts/storefront_enquiry.html', {
        'business': business
    })


                                                           
           
                                                           

@login_required
def analytics_view(request):
    leads = Lead.objects.filter(
        business__owner=request.user
    )

    total_leads = leads.count()

    new_leads = leads.filter(status='new').count()
    contacted_leads = leads.filter(status='contacted').count()
    qualified_leads = leads.filter(status='qualified').count()
    converted_leads = leads.filter(status='converted').count()
    lost_leads = leads.filter(status='lost').count()

    conversion_rate = (
        round((converted_leads / total_leads) * 100, 2)
        if total_leads > 0 else 0
    )

    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'contacted_leads': contacted_leads,
        'qualified_leads': qualified_leads,
        'converted_leads': converted_leads,
        'lost_leads': lost_leads,
        'conversion_rate': conversion_rate,
    }

    return render(request, 'accounts/analytics.html', context)


                                                           
          
                                                           

@login_required
def settings_view(request):
    businesses = Business.objects.filter(
        owner=request.user
    ).order_by('name')

                                                            
                               
    user_settings, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    profile_form = UserProfileForm(
        instance=request.user
    )

    password_form = PasswordChangeForm(
        user=request.user
    )

    settings_form = UserSettingsForm(
        instance=user_settings
    )

    if request.method == 'POST':
        action = request.POST.get('action')

                        
        if action == 'profile':
            profile_form = UserProfileForm(
                request.POST,
                instance=request.user
            )

            if profile_form.is_valid():
                profile_form.save()

                messages.success(
                    request,
                    'Profile updated successfully.'
                )

                return redirect('settings')

                         
        elif action == 'password':
            password_form = PasswordChangeForm(
                user=request.user,
                data=request.POST
            )

            if password_form.is_valid():
                user = password_form.save()

                update_session_auth_hash(request, user)

                messages.success(
                    request,
                    'Password changed successfully.'
                )

                return redirect('settings')

                            
        elif action == 'preferences':
            settings_form = UserSettingsForm(
                request.POST,
                instance=user_settings
            )

            if settings_form.is_valid():
                settings_form.save()

                messages.success(
                    request,
                    'Settings preferences updated successfully.'
                )

                return redirect('settings')

    return render(request, 'accounts/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'settings_form': settings_form,
        'user_settings': user_settings,
        'businesses': businesses,
    })


                                                           
                                                        
                                                           

@login_required
def ai_generate_product_description_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request data."}, status=400)

    name = str(payload.get("name", "")).strip()[:150]
    category = str(payload.get("category", "")).strip()[:60]
    price = str(payload.get("price", "")).strip()[:40]
    if not name:
        return JsonResponse({"error": "Enter a product name first."}, status=400)

    prompt = (
        "Write a clear, appealing, truthful ecommerce product description. "
        "Do not invent specifications, certifications, guarantees, materials, "
        "or benefits not supplied. Use a friendly professional tone and 60-100 words. "
        "Return only the description.\\n"
        f"Product name: {name}\\nCategory: {category or 'Not specified'}\\n"
        f"Price: {price or 'Not specified'}"
    )
    try:
        description = generate_gemini_text(prompt)
    except GeminiAPIError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    return JsonResponse({"description": description})


@login_required
def ai_chatbot_view(request):
    businesses = Business.objects.filter(
        owner=request.user
    ).order_by("name")

    answer = ""
    error = ""
    question = ""
    selected_business = None

    if request.method == "POST":
        business_id = request.POST.get("business")
        question = request.POST.get("question", "").strip()[:1200]

        if not business_id:
            error = "Please select a business."
        else:
            selected_business = get_object_or_404(
                Business,
                id=business_id,
                owner=request.user
            )

            if not question:
                error = "Enter a customer question first."

            else:
                products = Product.objects.filter(
                    business=selected_business,
                    is_published=True
                ).order_by("-created_at")[:30]

                product_context = "\n".join(
                    (
                        f"Product: {p.name}\n"
                        f"Description: {p.description[:350]}\n"
                        f"Price: {p.price}\n"
                        f"Category: {p.get_category_display()}"
                    )
                    for p in products
                ) or "No published products are currently listed."

                prompt = (
                    "You are the professional customer-support assistant "
                    "for the business described below.\n\n"

                    "Your task is to draft a helpful, friendly and concise "
                    "reply to the customer's question.\n\n"

                    "IMPORTANT FORMATTING RULES:\n"
                    "1. Write in clean, professional plain text.\n"
                    "2. Do not use Markdown formatting.\n"
                    "3. Never use **, ##, asterisks or Markdown bullet symbols.\n"
                    "4. Use natural sentences and readable paragraphs.\n"
                    "5. Display product names, categories and prices clearly.\n"
                    "6. Keep the reply friendly, polite and customer-focused.\n"
                    "7. Avoid unnecessary introductions and repetition.\n\n"

                    "ACCURACY RULES:\n"
                    "1. Use only the business information and product facts "
                    "provided below.\n"
                    "2. Never invent prices, stock availability, delivery "
                    "times, policies, contact details or promises.\n"
                    "3. If information is missing, politely say the business "
                    "needs to confirm it.\n"
                    "4. Do not claim that you have actually sent a message "
                    "or completed an action.\n\n"

                    f"BUSINESS INFORMATION:\n"
                    f"Business name: {selected_business.name}\n"
                    f"Category: {selected_business.get_category_display()}\n"
                    f"Phone: {selected_business.phone or 'Not provided'}\n"
                    f"Email: {selected_business.email or 'Not provided'}\n"
                    f"Address: {selected_business.address or 'Not provided'}\n"
                    f"Website: {selected_business.website or 'Not provided'}\n\n"

                    f"PUBLISHED PRODUCTS:\n{product_context}\n\n"

                    f"CUSTOMER QUESTION:\n{question}\n\n"

                    "Now write the suggested customer reply."
                )

                try:
                    answer = generate_gemini_text(prompt)

                except GeminiAPIError as exc:
                    error = str(exc)

    return render(
        request,
        "accounts/ai_chatbot.html",
        {
            "businesses": businesses,
            "answer": answer,
            "error": error,
            "question": question,
            "selected_business": selected_business,
        }
    )
