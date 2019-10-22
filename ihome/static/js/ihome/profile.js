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
});
