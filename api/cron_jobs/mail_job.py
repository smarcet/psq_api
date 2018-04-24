from django_cron import CronJobBase, Schedule
from ..models import MailRequest
from django.core.mail import send_mail



class MailCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 1  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.MailCronJob'  # a unique code

    def do(self):
        mails_2_send = MailRequest.objects.filter(is_sent=False)
        for mail_2_send in mails_2_send:

            send_mail(
                subject=mail_2_send.subject,
                message=mail_2_send.body,
                from_email=mail_2_send.from_address,
                recipient_list=[mail_2_send.to_address, ],
                html_message=mail_2_send.body
            )

            mail_2_send.mark_as_sent()
            mail_2_send.save(force_update=True)

