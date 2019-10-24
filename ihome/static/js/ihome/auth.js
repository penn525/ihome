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
    // 初始加载用户认证信息
    get_user_auth();

    $('#form-auth').submit(function (e) {
        e.preventDefault();
        set_user_auth();
    });
});

/**
 * 获取用户实名认证信息
 */
function get_user_auth() {
    $.get("/api/v1.0/user", function (rsp) {
            if ('0' == rsp.errno) {
                if (rsp.data.user.real_name && rsp.data.user.id_card) {
                    $('#real-name').val(rsp.data.user.real_name).prop('disabled', 'disabled')
                    $('#id-card').val(rsp.data.user.id_card).prop('disabled', 'disabled')
                    $('.error-msg').hide()
                    $('#form-auth>input[type=submit]').hide()
                }
            } else if ('4101' == rsp.errno) {
                location.href = '/login.html'
            } else {
                alert(rsp.data.errmsg)
            }
        },
        "json"
    );
    
}

/**
 * 设置用户实名认证信息
 */
function set_user_auth() {
    var real_name = $('#real-name').val()
    var id_card = $('#id-card').val()

    if (!real_name) {
        $('.error-msg b').html('请填写真是姓名')
    }

    if (!id_card) {
        $('.error-msg b').html('请填写身份证号码')
    }

    var data = {
        real_name: real_name,
        id_card: id_card
    }

    $.ajax({
        type: "put",
        url: "/api/v1.0/user/auth",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",
        headers: {
            'X-CSRFToken': getCookie('csrf_token')
        },
        success: function (rsp) {
            if ('0' == rsp.errno) {
                if (rsp.data.real_name && rsp.data.id_card) {
                    $('#real-name').val(rsp.data.real_name).prop('disabled', 'disabled')
                    $('#id-card').val(rsp.data.id_card).prop('disabled', 'disabled')
                    $('.error-msg').hide()
                    $('#form-auth>input[type=submit]').hide()
                    showSuccessMsg()
                }
            } else if ('4101' == rsp.errno) {
                location.href = '/login.html'
            } else {
                alert(rsp.data.errmsg)
            }
        }
    });
}