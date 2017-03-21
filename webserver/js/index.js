import $ from 'jquery';
import 'select2';
import 'select2/dist/css/select2.css';

console.log("outside");
$(document).ready(() => {
    $('select').select2();
});
