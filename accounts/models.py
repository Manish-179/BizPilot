
from django.conf import settings
from django.db import models


class Business(models.Model):

    class Category(models.TextChoices):
        RETAIL = "retail", "Retail"
        FOOD = "food", "Food & Beverage"
        TECHNOLOGY = "technology", "Technology"
        EDUCATION = "education", "Education"
        HEALTH = "health", "Healthcare"
        SERVICES = "services", "Professional Services"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businesses"
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=Category.choices)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lead(models.Model):

    class Source(models.TextChoices):
        CALL = "call", "Call"
        WHATSAPP = "whatsapp", "WhatsApp"
        FORM = "form", "Website Form"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CONVERTED = "converted", "Converted"
        LOST = "lost", "Lost"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="leads"
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.FORM
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    follow_up_at = models.DateTimeField(
        blank=True,
        null=True
    )

    follow_up_completed = models.BooleanField(default=False)

                                 
    reminder_sent_at = models.DateTimeField(
        blank=True,
        null=True
    )

    overdue_alert_sent_at = models.DateTimeField(
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    class Category(models.TextChoices):
        CLOTHING = "clothing", "Clothing"
        ELECTRONICS = "electronics", "Electronics"
        FOOD = "food", "Food"
        BEAUTY = "beauty", "Beauty"
        HOME = "home", "Home & Living"
        OTHER = "other", "Other"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name="brand"
    )

    logo = models.ImageField(
        upload_to="brands/logos/",
        blank=True,
        null=True
    )

    primary_color = models.CharField(
        max_length=7,
        default="#12bfae"
    )

    secondary_color = models.CharField(
        max_length=7,
        default="#0b1220"
    )

    banner = models.ImageField(
        upload_to="brands/banners/",
        blank=True,
        null=True
    )

    tagline = models.CharField(
        max_length=200,
        blank=True
    )

    storefront_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name} Brand"


class AutoReply(models.Model):

    class Trigger(models.TextChoices):
        FORM = "form", "Website Form"
        WHATSAPP = "whatsapp", "WhatsApp"
        CALL = "call", "Phone Call"

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name="auto_replies"
    )

    trigger = models.CharField(
        max_length=20,
        choices=Trigger.choices
    )

    message = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business.name} - {self.get_trigger_display()}"


class UserSettings(models.Model):

    class Theme(models.TextChoices):
        DARK = "dark", "Dark"
        LIGHT = "light", "Light"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_settings"
    )

                
    theme = models.CharField(
        max_length=10,
        choices=Theme.choices,
        default=Theme.DARK
    )

    accent_color = models.CharField(
        max_length=7,
        default="#12bfae"
    )

                   
    email_notifications = models.BooleanField(default=True)
    lead_notifications = models.BooleanField(default=True)
    followup_reminders = models.BooleanField(default=True)
    overdue_alerts = models.BooleanField(default=True)

                            
    automation_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} Settings"
