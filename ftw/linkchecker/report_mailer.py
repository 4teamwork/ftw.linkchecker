from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from Testing.makerequest import makerequest
from zope.component.hooks import setSite
import plone.api


app = globals()['app']
app = makerequest(app)

PLONE = app.get('Plone')
setSite(PLONE)


def send_feedback(email_subject, email_message, receiver_email_address, report_path):
    """Send an email including an excel workbook attached.
    """
    mh = plone.api.portal.get_tool('MailHost')
    from_name = PLONE.getProperty('email_from_name', '')
    from_email = PLONE.getProperty('email_from_address', '')

    sender = 'Linkcheck Reporter'
    recipient = from_email
    file_name = report_path.rsplit('/', 1)[1]

    msg = MIMEMultipart()
    msg['From'] = "%s <%s>" % (from_name, from_email)
    msg['reply-to'] = "%s <%s>" % (sender, recipient)
    msg['To'] = receiver_email_address
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = Header(email_subject, 'windows-1252')
    msg.attach(MIMEText(email_message.encode(
        'windows-1252'), 'plain', 'windows-1252'))
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(report_path, "rb").read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        'attachment; filename="' + file_name + '"'
    )
    msg.attach(part)

    mh.send(msg, mto=receiver_email_address,
            mfrom=from_email,
            immediate=True)
