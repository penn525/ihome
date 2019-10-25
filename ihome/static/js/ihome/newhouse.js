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

                // art template 使用js模板
                var html = template('areas-tmpl', { areas: areas })
                // 插入到对应html区域
                $('#area-id').html(html);
            } else {
                alert(rsp.errmsg)
            }
        },
        "json"
    );

    /* 提交房源基本信息 */
    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        var data = {}
        $('#form-house-info').serializeArray().map(function (x) { data[ x.name ] = x.value })

        var facilities = []
        $(':checked[name=facility]').map(function () { facilities.push($(this).val()) })

        data.facilities = facilities

        $.ajax({
            type: "post",
            url: "/api/v1.0/house/info",
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json",
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if ('0' == rsp.errno) {
                    $('#form-house-info').hide()
                    $('#form-house-image').show()
                    $('#house-id').val(rsp.data.house_id)
                } else if ('4101' == rsp.errno) {
                    location.href = '/login.html'
                } else {
                    alert(rsp.errmsg)
                }
            }
        });

    });

    /* 上传房屋图像 */
    $('#form-house-image').submit(function (e) {
        e.preventDefault()
        $(this).ajaxSubmit({
            type: "post",
            url: "/api/v1.0/house/image",
            dataType: "json",
            cache: false,
            headers: {
                'X-CSRFToken': getCookie('csrf_token')
            },
            success: function (rsp) {
                if ('0' == rsp.errno) {
                    $('.house-image-cons').append('<img src="' + rsp.data.image_url + '" />')
                    $('#form-house-image .form-group').empty().html(
                        '<label for="house-image">选择图片</label>' +
                        '<input type="file" accept="image/*" name="house_image" id="house-image">'
                    )
                } else if ('4101' == rsp.errno) {
                    location.href = '/login.html'
                } else {
                    alert(rsp.errmsg)
                }
            }
        });
    })
})