from django_cron import CronJobBase, Schedule

from backend import settings
from ..models import MailRequest
from django.core.mail import send_mail

import sendgrid
import os
from sendgrid.helpers.mail import *

class MailCronJob(CronJobBase):
    RUN_EVERY_MINS: int = 1  # every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.MailCronJob'  # a unique code

    def do(self):
        mails_2_send = MailRequest.objects.filter(is_sent=False)
        for mail_2_send in mails_2_send:
            print("sending email to {}".format(mail_2_send.to_address))

            sg = sendgrid.SendGridAPIClient(apikey=settings.SEND_GRID_API_KEY)
            from_email = Email(mail_2_send.from_address)
            to_email = Email(mail_2_send.to_address)
            subject = mail_2_send.subject
            content = Content("text/plain", mail_2_send.body)
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)

            mail_2_send.mark_as_sent()
            mail_2_send.save(force_update=True)

