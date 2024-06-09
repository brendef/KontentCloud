function readCookie(name) {
    let value = null;

    let cookies = document.cookie.split('; ');

    cookies.forEach(function (cookie) {
        let pair = cookie.split('=');
        if (pair[0] === name) {
            value = pair[1];
        }
    });

    return value
}

function logout() {
    document.cookie = 'tokenTtl=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
    document.cookie = 'longToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
    location.reload();
}