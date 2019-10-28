function hrefBack () {
    history.go(-1);
}

function decodeQuery () {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[ values[ 0 ] ] = values[ 1 ];
        return result;
    }, {});
}

$(document).ready(function () {
    house_id = decodeQuery()[ 'id' ]
    $.get("/api/v1.0/house/" + house_id,
        function (resp) {
            if ('0' == resp.errno) {
                var house = resp.data.house_info
                // console.log(house)
                $('.swiper-container').html(template('house-image-tmpl', { image_urls: house.image_urls, price: house.price }))
                $('.detail-con').html(template('house-detail-tmpl', { house: house, fas: house.facilities }))

                // 预订按钮是否显示
                if (house.uid != resp.data.user_id) {
                    $('.book-house').attr('href', '/booking.html?hid=' + house.hid)
                    $('.book-house').show()
                } else {
                    $('.book-house').hide()
                }

                // 设置幻灯片对象，开启幻灯片滚动
                var mySwiper = new Swiper('.swiper-container', {
                    loop: true,
                    autoplay: 2000,
                    autoplayDisableOnInteraction: false,
                    pagination: '.swiper-pagination',
                    paginationClickable: true
                });
            } else {
                alert(resp.errmsg)
            }
        },
        "json"
    );

    var mySwiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    })
    $(".book-house").show();
})