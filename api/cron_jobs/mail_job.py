from django_cron import Schedule

from ..cron_jobs import NonOverlappingCronJob
from backend import settings
from ..models import MailRequest
import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *
from django.db import transaction


class MailCronJob(NonOverlappingCronJob):

    RUN_EVERY_MINS = 1  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.MailCronJob'  # a unique code

    @transaction.atomic
    def _run(self):
        mails_2_send = MailRequest.objects.filter(is_sent=False)
        for mail_2_send in mails_2_send:
            try:
                self.logger.info("sending email to {}".format(mail_2_send.to_address))

                sg = sendgrid.SendGridAPIClient(apikey=settings.SEND_GRID_API_KEY)
                from_email = Email(mail_2_send.from_address)

                if settings.DEBUG:
                    to_email = Email(settings.DEBUG_EMAIL)
                else:
                    to_email = Email(mail_2_send.to_address)

                subject = mail_2_send.subject
                content = Content("text/html", mail_2_send.body)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
                print(response.status_code)
                print(response.body)
                print(response.headers)

                mail_2_send.mark_as_sent()
                mail_2_send.save(force_update=True)

            except Exception as exc:
                self.logger.error("MailCronJob - error", exc)

