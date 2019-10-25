$(document).ready(function () {
    $.ajax({
        type: "get",
        url: "/api/v1.0/user/auth",
        dataType: "json",
        success: function (rsp) {
            alert(rsp.errno)
            if ('0' == rsp.errno) {
                $('.auth-warn').hide();
                $('#houses-list').show();
            } else if ('4004' == rsp.errno) {
                $('.auth-warn').show();
                $('#houses-list').hide();
            } else if ('4101' == rsp.errno) {
                location.href = '/login.html'
            } else {
                alert(rsp.errmsg)
            }
        }
    });

})