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

$(document).ready(function () {
    $.ajax({
        type: "get",
        url: "/api/v1.0/users",
        dataType: "json",
        success: function (rsp) {
            if (rsp.errno == '0') {
                console.log(rsp.data)
                user = rsp.data.user
                $('#user-avatar').attr('src', user.avatar_url)
                $('#user-name').html(user.name)
                $('#user-mobile').html(user.mobile)
            } else {
                alert('用户未登录')
            }
        }
    });
});
