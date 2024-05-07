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