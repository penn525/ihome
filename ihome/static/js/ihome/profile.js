function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    /**
     * 设置用户头像
     */
    $('#form-avatar').submit(function (e) { 
        e.preventDefault();
        $(this).ajaxSubmit({
            url: '/api/v1.0/users/avatar',
            method: 'post',
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) { 
                if (rsp.errno == 0) {
                    $("#user-avatar").attr('"src', rsp.data.avatar_url)
                } else {
                    alert(rsp.errmsg)
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
        var req_data = {'name': name};
        var req_json = JSON.stringify(req_data);
        $.ajax({
            type: "post",
            url: "/api/v1.0/users/name",
            data: req_json,
            contentType: "application/json",
            dataType: "json",
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if (rsp.errno == "0") {
                    console.log(1)
                    $('.error-msg').hide()
                } else {
                    console.log(2)
                    $('.error-msg b').html(rsp.errmsg).parent().show()
                } 
            }
        });
    });

});
