import io
import qrcode
import random
import re
import string
import urllib.parse
from decimal import Decimal

recipient = "flipdot e.V."
iban = "DE07520503530001147713"


# bic = "HELADEF1KAS"

def make_sepa_qr(amount, name, uid, pixel_width=10, border=4, color="black", bg="white"):
    info = "".join(random.choices(string.ascii_lowercase, k=12))
    url = tx_url(uid, name, info, amount)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=pixel_width,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color=bg)
    img_data = io.BytesIO()
    img.save(img_data, format='PNG')
    img_data.seek(0)
    return img_data


def tx_url(uid, name, info, amount):
    name = re.sub(r'[^a-zA-Z0-9 ]', '_', str(name))
    info = re.sub(r'[^a-zA-Z0-9 ]', '_', info)

    # make int
    amount = "{:.0f}".format(Decimal(amount))
    reason = "drinks {uid} {name} {info}".format(uid=uid, name=name, info=info)
    return "bank://singlepaymentsepa?" + urllib.parse.urlencode({
        'name': recipient,
        'iban': iban,
        'amount': amount,
        'reason': reason,
        'currency': 'EUR'
    })
