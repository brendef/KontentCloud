function statusChangeCallback(response) {
    console.log("statusChangeCallback()");

    if (response.status === "connected") {
        window.location.href = "/search";
    }
}

function checkLoginState() {
    console.log("checkLoginState()");

    FB.getLoginStatus(function (response) {
        statusChangeCallback(response);
    });
}

function facebookLogout() {
    console.log("facebookLogout()");

    FB.logout(function (response) {
        console.log(response);
    });
}