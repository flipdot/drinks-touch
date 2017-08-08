# coding=utf-8
import smtplib
import threading
from email.mime.text import MIMEText

import time

import logging

from env import is_pi
from users.users import Users

# lower and we send mails every x days!
minimum_balance = -5
remind_mail_every_x_hours = 24 * 7

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
            mail_msg = "Du hast das folgende Getränk getrunken {drink_name}\n\nVerbleibendes Guthaben: EUR {balance}" \
                .format(drink_name=drink['name'], balance=balance)
            send_notification_newthread(user_email,
                                        "[fd-noti] Getränk getrunken", mail_msg)
    except Exception as e:
        logging.error(e)
        pass

def send_lowbalances():
    if not is_pi():
        return
    now = time.time()
    for user in Users.get_all():
        try:
            user_email = user['email']
            if not user_email:
               continue

            balance = Users.get_balance(user['id'])
            if balance >= minimum_balance:
                # set time to okay
                user["last_emailed"] = time.time()
                Users.save(user)
                continue
            diff = now - user['last_emailed']
            last_emailed_hours = diff / 60 / 60
            last_emailed_days = last_emailed_hours/ 24
            if last_emailed_hours > remind_mail_every_x_hours:
                print user['name'], "last emailed", last_emailed_days, "days (", \
                    last_emailed_hours, "hours) ago. Mailing now."
                mail_msg = "Du hast seit mehr als {limit_days} Stunden ein " \
                           "Guthaben unter EUR {limit}!\n\n" \
                           "Dein Guthaben betraegt: EUR {balance}\n\n" \
                           "Zum aufladen geh (im Space-Netz) auf http://drinks-touch.fd/" \
                           .format(limit_days=remind_mail_every_x_hours/24,
                                   limit=minimum_balance, balance=balance)
                send_notification(user_email, "[fd-noti] Negatives Guthaben",
                                  mail_msg)
                user["last_emailed"] = time.time()
                Users.save(user)
        except Exception as e:
            logging.error(e)
            continue

def send_summaries():
    if not is_pi():
        return
    now = time.time()
    #TODO