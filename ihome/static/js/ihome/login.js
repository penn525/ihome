function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
    });
    $(".form-login").submit(function (e) {
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }

        var req_data = {
            mobile: mobile,
            password: passwd
        }
        var req_json = JSON.stringify(req_data)
        $.ajax({
            type: "post",
            url: "/api/v1.0/sessions",
            data: req_json,
            dataType: "json",
            contentType: "application/json",
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if (rsp.errno == 0) {
                    location.href = '/'
                } else {
                    // alert(rsp.errmsg)
                    $('#password-err span').html(rsp.errmsg)
                    $('#password-err').show()
                }
            }
        });
    });
})