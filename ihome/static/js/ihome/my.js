function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};

function logout() {
    $.ajax({
        type: "delete",
        url: "/api/v1.0/session",
        dataType: "json",
        headers: {
            'X-CSRFToken': getCookie("csrf_token")
        },
        success: function (rsp) {
            if (0 == rsp.errno) {
                location.href = "/";
            }
        }
    });
}

$(document).ready(function () {})