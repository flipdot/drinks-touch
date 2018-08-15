import $ from 'jquery';
import 'select2';
import 'select2/dist/css/select2.css';

let user_select;
let value_input;
let qrcode;
let qrcode_hint;
let uid_text;

document.addEventListener('DOMContentLoaded', function() {
    $('select').select2();

    user_select = $('#user_user');
    value_input = document.querySelector('#amount');
    qrcode = document.querySelector('#qrcode');
    qrcode_hint = document.querySelector('#qrcode_hint');
    uid_text = document.querySelector('#uid');

    $('select').on('select2:select', update_qr);
    value_input.addEventListener('onchange', update_qr);
    value_input.addEventListener('keyup', update_qr);

    update_qr();
});

let urlNow = '';
let urlNext = '';
let lastUpdate = null;

function update_qr() {
    const uid = user_select.val();
    const name = user_select.find(':selected').text();
    const amount = value_input.value;

    if (uid) {
        uid_text.textContent = uid;
    } else {
        uid_text.textContent = "<uid>";
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
