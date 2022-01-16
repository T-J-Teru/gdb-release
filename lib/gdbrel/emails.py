from gdbrel.utils import query, indent

from email.mime.text import MIMEText
from email.utils import getaddresses
from smtplib import SMTP

SEND_QUERY = """\
Please confirm the following email to be sent:

%(email_as_string)s

"""


class Email(object):
    def __init__(self, email_from, email_to, email_subject, email_body):
        self.email_from = email_from
        self.email_to = email_to
        self.email_subject = email_subject
        self.email_body = email_body

    def __to_mime(self):
        e_msg = MIMEText(self.email_body)
        # Create the email's header.
        e_msg['From'] = self.email_from
        e_msg['To'] = self.email_to
        # Bcc the sender as well, to handle the case where the Release Manager
        # is using GMail, where emails sent to mailing-lists are not displayed
        # in the INBOX, even if a member of the mailing-list.  With the Bcc,
        # it should always be shown.
        e_msg['Bcc'] = self.email_from
        e_msg['Subject'] = self.email_subject

        return e_msg

    def as_string(self):
        e_msg = self.__to_mime()
        return e_msg.as_string()

    def send_after_confirmation(self, smtp_server='localhost'):
        send_query = SEND_QUERY % \
            {'email_as_string': indent(self.as_string(), '| ')}
        query(send_query)

        e_msg = self.__to_mime()
        email_recipients = [addr[1] for addr
                            in getaddresses(e_msg.get_all('To', [])
                                            + e_msg.get_all('Cc', [])
                                            + e_msg.get_all('Bcc', []))]
        s = SMTP(smtp_server)
        s.sendmail(self.email_from, email_recipients, e_msg.as_string())
        s.quit()
