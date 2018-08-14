let user_select;
let value_input;
let qrcode;
let qrcode_hint;
let uid_text;

document.addEventListener('DOMContentLoaded', function() {
    user_select = document.querySelector('#user_user');
    value_input = document.querySelector('#amount');
    qrcode = document.querySelector('#qrcode');
    qrcode_hint = document.querySelector('#qrcode_hint');
    uid_text = document.querySelector('#uid');

    user_select.addEventListener('change', update_qr);
    value_input.addEventListener('change', update_qr);
    value_input.addEventListener('keyup', update_qr);
    user_select.addEventListener('keyup', update_qr);

    update_qr();
});

let urlNow = '';
let urlNext = '';
let lastUpdate = null;

function update_qr() {
    const uid = user_select.value;
    const name = user_select.options[user_select.selectedIndex].text;
    const amount = value_input.value;

    if (uid) {
        uid_text.textContent = uid;
    } else {
        uid_text.textContent = "??";
    }
    if (lastUpdate) {
        clearTimeout(lastUpdate);
        lastUpdate = null;
    }
    const url = '/tx.png?uid=' + encodeURIComponent(uid) +
        '&name=' + encodeURIComponent(name) +
        '&amount=' + encodeURIComponent(amount);

    if (name != '' && amount > 0) {
        qrcode.classList.remove('d-none')
        qrcode_hint.classList.add('d-none')

        if (url !== urlNow) {
            qrcode.src = '';
            urlNext = url;
            setTimeout(realUpdate, 500);
        }
    } else {
        qrcode.classList.add('d-none')
        qrcode_hint.classList.remove('d-none')
    }
}

function realUpdate() {
    if (urlNow === urlNext) {
        return;
    }

    qrcode.src = urlNext;
    urlNow = urlNext;
}
