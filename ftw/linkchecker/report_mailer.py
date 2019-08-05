from Testing.makerequest import makerequest
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from zope.component.hooks import setSite
import plone.api
import time


class MailSender(object):
    def __init__(self, portal=None):
        if not portal:
            self.app = globals()['app']
            self.app = makerequest(self.app)
            self.PLONE = self.app.get('Plone')
        if portal:
            self.PLONE = portal
        setSite(self.PLONE)

    def send_feedback(self, email_subject, email_message,
                      receiver_email_address, xlsx_file_content, file_name):
        """Send an email including an excel workbook attached.
        """
        mh = plone.api.portal.get_tool('MailHost')
        from_name = self.PLONE.getProperty('email_from_name', '')
        from_email = self.PLONE.getProperty('email_from_address', '')

        sender = 'Linkcheck Reporter'
        recipient = from_email

        msg = MIMEMultipart()
        msg['From'] = "%s <%s>" % (from_name, from_email)
        msg['reply-to'] = "%s <%s>" % (sender, recipient)
        msg['To'] = receiver_email_address
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = Header(email_subject, 'windows-1252')
        msg.attach(MIMEText(email_message.encode(
            'windows-1252'), 'plain', 'windows-1252'))
        part = MIMEBase('application', "octet-stream")
        part.set_payload(xlsx_file_content)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="' + file_name + '"'
        )
        msg.attach(part)

        mh.send(msg, mto=receiver_email_address,
                mfrom=from_email,
                immediate=True)
