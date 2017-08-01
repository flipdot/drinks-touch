# coding=utf-8
import smtplib
import threading
from email.mime.text import MIMEText

from datetime import datetime

from users.users import Users

with open('mail_pw', 'r') as pw:
    mail_pw = pw.read().replace('\n', '')

def send_notification_newthread(to_address, subject, message):
    send_thread = threading.Thread(
        target=send_notification,
        args=(to_address, subject, message)
    )
    send_thread.daemon = True
    send_thread.start()

def send_notification(to_address, subject, message):
    msg = MIMEText(message,_charset='utf-8')

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

def send_drink(user, drink, balance):
    try:
        user_email = user['email']
        if user_email:
            mail_msg = "Du hast das folgende Getränk getrunken {drink_name}\n\nVerbleibendes Guthaben: {balance}" \
                .format(drink_name=drink['name'], balance=balance)
            send_notification_newthread(user_email,
                                        "[fd-noti] Getränk getrunken", mail_msg)
    except Exception as e:
        logging.error(e)
        pass
