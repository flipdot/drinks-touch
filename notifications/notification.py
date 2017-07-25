import smtplib
from email.mime.text import MIMEText


with open('mail_pw', 'r') as pw:
    mail_pw = pw.read().replace('\n', '')

def send_notification(to_address, subject, message):
    msg = MIMEText(message)

    fromMail = "flipdot-noti@vega.uberspace.de"

    msg['Subject'] = subject
    msg['From'] = fromMail
    msg['To'] = to_address

    s = smtplib.SMTP()
    s.connect(host='vega.uberspace.de', port=587)
    s.ehlo()
    s.starttls()
    s.login(user=fromMail, password=mail_pw)
    s.sendmail(fromMail, [to_address], msg.as_string())
    s.quit()