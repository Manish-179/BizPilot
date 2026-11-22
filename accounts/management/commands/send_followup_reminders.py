
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from accounts.models import Lead, UserSettings


class Command(BaseCommand):
    help = "Send automatic BizPilot follow-up reminders and overdue alerts"

    def handle(self, *args, **options):
        now = timezone.now()

        reminder_count = 0
        overdue_count = 0
        skipped_count = 0

                               
                                                                  
        def get_preferences(owner):
            try:
                return owner.user_settings
            except UserSettings.DoesNotExist:
                return None

        def notifications_allowed(owner):
            preferences = get_preferences(owner)

            if preferences is None:
                return True

            return (
                preferences.automation_enabled
                and preferences.email_notifications
            )

                                                      
        due_leads = Lead.objects.filter(
            follow_up_at__isnull=False,
            follow_up_at__lte=now,
            follow_up_completed=False,
            reminder_sent_at__isnull=True,
        ).select_related(
            "business",
            "business__owner",
            "business__owner__user_settings",
        )

        for lead in due_leads:
            owner = lead.business.owner
            preferences = get_preferences(owner)

            if not notifications_allowed(owner):
                skipped_count += 1
                continue

            if (
                preferences is not None
                and not preferences.followup_reminders
            ):
                skipped_count += 1
                continue

            if not owner.email:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped reminder for {lead.name}: "
                        "account owner has no email."
                    )
                )
                continue

            subject = f"BizPilot: Follow-up due for {lead.name}"

            message = (
                f"Hello {owner.get_full_name() or owner.username},\n\n"
                f"A follow-up is due for your lead: {lead.name}.\n\n"
                f"Business: {lead.business.name}\n"
                f"Phone: {lead.phone}\n"
                f"Follow-up time: {lead.follow_up_at}\n\n"
                "Please contact this lead and update its status "
                "in your BizPilot dashboard.\n\n"
                "Regards,\nBizPilot"
            )

            try:
                sent = send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [owner.email],
                    fail_silently=False,
                )

                if sent == 1:
                    lead.reminder_sent_at = now
                    lead.save(update_fields=["reminder_sent_at"])
                    reminder_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Reminder sent for lead: {lead.name}"
                        )
                    )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Reminder failed for {lead.name}: {error}"
                    )
                )

                                                                  
        overdue_cutoff = now - timedelta(hours=24)

        overdue_leads = Lead.objects.filter(
            follow_up_at__isnull=False,
            follow_up_at__lte=overdue_cutoff,
            follow_up_completed=False,
            reminder_sent_at__isnull=False,
            overdue_alert_sent_at__isnull=True,
        ).select_related(
            "business",
            "business__owner",
            "business__owner__user_settings",
        )

        for lead in overdue_leads:
            owner = lead.business.owner
            preferences = get_preferences(owner)

            if not notifications_allowed(owner):
                skipped_count += 1
                continue

            if (
                preferences is not None
                and not preferences.overdue_alerts
            ):
                skipped_count += 1
                continue

            if not owner.email:
                skipped_count += 1
                continue

            subject = f"BizPilot: Overdue follow-up for {lead.name}"

            message = (
                f"Hello {owner.get_full_name() or owner.username},\n\n"
                f"The follow-up for {lead.name} is overdue.\n\n"
                f"Business: {lead.business.name}\n"
                f"Phone: {lead.phone}\n"
                f"Scheduled follow-up: {lead.follow_up_at}\n\n"
                "This follow-up has been pending for at least 24 hours. "
                "Please contact the lead or mark the follow-up completed "
                "in your BizPilot dashboard.\n\n"
                "Regards,\nBizPilot"
            )

            try:
                sent = send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [owner.email],
                    fail_silently=False,
                )

                if sent == 1:
                    lead.overdue_alert_sent_at = now
                    lead.save(update_fields=["overdue_alert_sent_at"])
                    overdue_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Overdue alert sent for lead: {lead.name}"
                        )
                    )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Overdue alert failed for {lead.name}: {error}"
                    )
                )

                          
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("BizPilot reminder task finished.")
        )
        self.stdout.write(f"Due reminders sent: {reminder_count}")
        self.stdout.write(f"Overdue alerts sent: {overdue_count}")
        self.stdout.write(f"Skipped: {skipped_count}")
