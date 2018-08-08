import $ from 'jquery';
import 'select2';
import 'select2/dist/css/select2.css';


var user_select;
var value_input;
var qrcode;
$(document).ready(() => {
    $('select').select2();

    user_select = $('#user_user');
    value_input = $('#amount');
    qrcode = $('#qrcode')
    user_select.change(update_qr);
    value_input.change(update_qr);
    value_input.keyup(update_qr);
    user_select.keyup(update_qr);
});

var urlNow = "";
var urlNext = "";
var lastUpdate = null;
function update_qr() {
    if (lastUpdate) {
        clearTimeout(lastUpdate);
        lastUpdate = null;
    }
    const name = user_select.find(':selected').text();
    const uid = user_select.val();
    const amount = value_input.val();
    let url = "/tx.png?uid=" + encodeURIComponent(uid) +
        "&name=" + encodeURIComponent(name) +
        "&amount=" + encodeURIComponent(amount);

    if (url !== urlNow) {
        qrcode.attr('src', "");
        urlNext = url;
        setTimeout(realUpdate, 500);
    }
}
function realUpdate() {
    if (urlNow === urlNext) {
        return;
    }
    qrcode.attr('src', urlNext);
    urlNow = urlNext;
}
