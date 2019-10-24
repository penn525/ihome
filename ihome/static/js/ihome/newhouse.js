function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

/**
 * 查询所有区域
 */
function get_areas() {
   $.ajax({
       type: "get",
       url: "/api/v1.0/areas",
       dataType: "json",
       success: function (rsp) {
           
       }
   }); 
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
})