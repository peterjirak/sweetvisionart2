var delete_cookie = function(name) {
    document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
};

function deauthenticate(){
    delete_cookie('ACSID');
    delete_cookie('SACSID');
    delete_cookie('dev_appserver_login');
    window.location = '/';
}


//Action Handlers

window.onload = function() {
    logoutControls = document.getElementsByClassName('js-deauthenticate');

    for (let i=0; i < logoutControls.length; i++) {
        logoutControls[i].onclick = deauthenticate;
    }
};

