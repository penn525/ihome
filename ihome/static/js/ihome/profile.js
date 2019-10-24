function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {});
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    /**
     * 获取用户名
     */
    $.get("/api/v1.0/user", function (rsp) {
            console.log(rsp)
            if (rsp.errno == '0') {
                $("#user-avatar").attr('src', rsp.data.user.avatar_url)
                $("#user-name").val(rsp.data.user.name)
            } else if ('4001' == rsp.errno) {
                $('.error-msg b').html(rsp.errmsg).parent().show()
            } else if ('4101' == rsp.errno) {
                location.href = '/login.html'
            }
        },
        "json"
    );

    /**
     * 设置用户头像
     */
    $('#form-avatar').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url: '/api/v1.0/user/avatar',
            method: 'post',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if ('0' == rsp.errno) {
                    $('.error-msg').hide()
                    $("#user-avatar").attr('src', rsp.data.avatar_url)
                    showSuccessMsg()
                } else if ('4001' == rsp.errno) {
                    $('.error-msg b').html(rsp.errmsg).parent().show()
                } else if ('4101' == rsp.errno) {
                    location.href = '/login.html'
                }
            }
        })
    });

    /**
     * 设置用户名称
     */
    $("#form-name").submit(function (e) {
        e.preventDefault();
        var name = $('#user-name').val();
        if (!name) {
            $('.error-msg b').html('请填写用户名').parent().show();
            return;
        }
        var req_data = {
            'name': name
        };
        var req_json = JSON.stringify(req_data);
        $.ajax({
            type: "put",
            url: "/api/v1.0/user/name",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if ('0' == rsp.errno) {
                    $('.error-msg').hide()
                    showSuccessMsg()
                } else if ('4001' == rsp.errno) {
                    $('.error-msg b').html(rsp.errmsg).parent().show()
                } else if ('4101' == rsp.errno) {
                    location.href = '/login.html'
                }
            }
        });
    });

});