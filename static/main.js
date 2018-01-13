// Nav buttons

var SECTIONS = ['prefarea', 'talkgroups', 'speccont', 'channels', 'generate','comments'];
var navi_buttons = Array.from(document.getElementsByClassName("navbutton"));
navi_buttons.forEach(function(button){
    var guzik=button;
    guzik.addEventListener("click", function(){
        navi_buttons.forEach(function(btn){btn.classList.remove('is-active');});
        guzik.classList.toggle('is-active');
        SECTIONS.forEach(function(section){
            document.getElementById(section).classList.add('is-hidden');
        });
        document.getElementById(guzik.getAttribute('section')).classList.toggle('is-hidden');
    });
});

// Prefix & area section
var prefix_checkboxes = Array.from(document.getElementsByClassName('prefix_selection'));
var area_checkboxes = Array.from(document.getElementsByClassName('area_selection'));
var prefix_sel_all = document.getElementById('prefix_all');
var area_sel_all = document.getElementById('area_all');

[ [prefix_sel_all, prefix_checkboxes], [area_sel_all, area_checkboxes]].forEach(function(data){
    var guzik=data[0];
    var set=data[1];
    guzik.addEventListener("click", function(){
        set.forEach(function(checkbox){
            checkbox.checked = guzik.checked;
        });
    });
});

// Channels
var services_group_checkboxes = Array.from(document.getElementsByClassName('service_checkbox_all'));
var service_checkboxes = Array.from(document.getElementsByClassName('service_checkbox'));
var pmr_checkboxes = Array.from(document.getElementsByClassName('pmr_checkbox'));

services_group_checkboxes.forEach(function(services_group_ckbox){
    var service = services_group_ckbox.getAttribute('service');
    services_group_ckbox.addEventListener("click", function(){
        var trigger = services_group_ckbox;
        console.log('klik');
        service_checkboxes.filter(ckbox => ckbox.getAttribute('service')==service).forEach(function(ckbox){
            ckbox.checked = trigger.checked;
        });
    });
});

var pmr_all_cb = document.getElementById('pmr_sel_all');
pmr_all_cb.addEventListener("click",function(){
    pmr_checkboxes.forEach(ckbox => ckbox.checked = pmr_all_cb.checked);
});

// Error Message
var error_modal = document.getElementById("error");
var error_dismiss = document.getElementById("alert_close");
var error_msg = document.getElementById("error_message");

error_dismiss.addEventListener("click", function(){
    error_modal.classList.toggle( "is-active");
});

// About
var about_modal = document.getElementById("about");
var about_dismiss = document.getElementById("about_close");

about_dismiss.addEventListener("click", function(){
    about_modal.classList.toggle( "is-active");
});
document.getElementById('about_btn').addEventListener("click",function(){about_modal.classList.toggle('is-active')});



// Storage
var priocals = document.getElementById("priocals");
var priosave = document.getElementById("priosave");
var ignocals = document.getElementById("ignocals");
var ignosave = document.getElementById("ignosave");
if (typeof(Storage) !== "undefined") {
    priocals.value = localStorage.getItem("gd77.priocals");
    if (priocals.value !== "") {
        priosave.checked = true;
    }
    ignocals.value = localStorage.getItem("gd77.ignocals");
    if (ignocals.value !== "") {
        ignosave.checked = true;
    }
}


//Generate!
var send = document.getElementById("submit");
send.addEventListener("click", function(){
    var tgs = Array.from(document.getElementsByClassName('tg_checkbox'));
    var speccontacts = Array.from(document.getElementsByClassName('speccontact'));
    var rep_bands = Array.from(document.getElementsByClassName('band_checkbox'));
    var rep_modes = Array.from(document.getElementsByClassName('mode_checkbox'));
    var rep_areas = Array.from(document.getElementsByClassName('rep_area_checkbox'));

    var payload = {
        contacts: {
            sp_prefix: prefix_checkboxes.filter(cb=>cb.checked).map(cb=>cb.value),
            sp_area: area_checkboxes.filter(cb=>cb.checked).map(cb=>cb.value),
            tgs: tgs.filter(cb=>cb.checked).map(cb=>cb.value),
            adds: speccontacts.filter(cb=>cb.checked).map(cb=>cb.value),
            prio: priocals.value,
            igno: ignocals.value
        },

        channels: {
            repeaters: {
                bands: rep_bands.filter(cb=>cb.checked).map(cb=>cb.value),
                modes: rep_modes.filter(cb=>cb.checked).map(cb=>cb.value),
                areas: rep_areas.filter(cb=>cb.checked).map(cb=>cb.value),
                digi_first: document.getElementsByClassName('digi_first_checkbox')[0].checked
            },
            services:[],
            pmr: []
        }
    };

    var service_checkboxes = Array.from(document.getElementsByClassName('service_checkbox'));
    var service_categories = Array.from(document.getElementsByClassName('service_checkbox_all')).map(cb=>cb.getAttribute('service'));

    services = {};
    service_categories.forEach(function(service_name){
        services[service_name] = service_checkboxes.filter(cb=>cb.getAttribute('service')===service_name && cb.checked).map(cb=>cb.value);
    });

    payload.channels.services = services;
    payload.channels.pmr = Array.from(document.getElementsByClassName('pmr_checkbox')).filter(cb=>cb.checked).map(cb=>cb.value);

    console.log(payload);
    // save prio list for later
    if (typeof(Storage) !== "undefined") {
        if (priosave.checked) {
            localStorage.setItem("gd77.priocals", priocals.value);
        }
        if (ignosave.checked) {
            localStorage.setItem("gd77.ignocals", ignocals.value);
        }
    } else {
        if (priosave.checked || ignosave.checked) {
            error_msg.innerText = "Sorry kolego/koleżanko. Twoja przeglądarka nie pozwala zapisać twojej listy kontaktów priorytetowych.";
            sel_toggle(error_modal, "is-active");
        }
    }
    window.open("/csv/" + msgpack.encode(payload).toString('hex'));
});