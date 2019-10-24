function getCookie (name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[ 1 ] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // 查询所有区域
    $.get("/api/v1.0/areas",
        function (rsp) {
            console.log(rsp)
            if ('0' == rsp.errno) {
                var areas = rsp.data
                // $.each(areas, function (index, area) { 
                //      $('#area-id').append(
                //          '<option value="' + area.aid + '">' + area.aname + '</option>'
                //      );
                // });

                // 使用js模板
                var html = template('areas-tmpl', { areas: areas })
                // 插入到对应html区域
                $('#area-id').html(html);
            } else {
                alert(rsp.errmsg)
            }
        },
        "json"
    );
})