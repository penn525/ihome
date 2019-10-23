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
    $.ajax({
        type: "get",
        url: "/api/v1.0/users/auth",
        dataType: "json",
        success: function (rsp) {
            if (rsp.errno == '0') {
                $('.error-msg').hide();
                $('#real-name').val(rsp.data.real_name);
                $('#id-card').val(rsp.data.id_card);
            } else {
                $('.error-msg b').html(rsp.errmsg).parent().show();
            }
        }
    });
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
        type: "post",
        url: "/api/v1.0/users/auth",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",
        headers: {
            'X-CSRFToken': getCookie('csrf_token')
        },
        success: function (rsp) {
            $('.error-msg b').html(rsp.errmsg)
        }
    });
}
