$(document).ready(function () {
    /**
     * 检查用户是否已经实名认证
     * 只有完成了实名认证才能发布新房源，才能查询自己的房源
     */
    $.ajax({
        type: "get",
        url: "/api/v1.0/user/auth",
        dataType: "json",
        success: function (rsp) {
            if ('0' == rsp.errno) {
                $('.auth-warn').hide();
                get_houses()
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

/** 查询我的房源 */
function get_houses () {
    $.get("/api/v1.0/user/houses",
        function (rsp) {
            if ('0' == rsp.errno) {
                html = template('houses-tmpl', { houses: rsp.data.houses })
                $('#houses-list').append(html)
            } else if ('4101' == rsp.errno) {
                location.href = '/login.html'
            } else {
                alert(rsp.errmsg)
            }
        },
        "json"
    );
}