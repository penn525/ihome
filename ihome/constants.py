# 图片验证码的redis有效期， 秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期， 秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的时间间隔， 秒
SEND_SMS_CODE_INTERVAL = 60

# 限制登录的尝试次数， 次
LOGIN_ERROR_MAX_TIMES = 3

# 限制多长时间后可以继续尝试， 秒
LOGIN_ERROR_FORBID_TIME = 300

# 七牛文件域名
QINIU_URL_DOMAIN = 'http://pztl5gcjf.bkt.clouddn.com/'

# 区域redis缓存时间
AREA_INFO_REDIS_CACHE_EXPIRES = 1800

# 主页房屋最大数量
HOME_PAGE_MAX_HOUSE = 5

# 主页房屋资源redis缓存时间
HOME_PAGE_REDIS_CACHE_EXPIRES = 1800

# 房屋详情展示用户评论数量
HOUSE_DETAIL_COMMENTS_DISPLAY_COUNT = 20

# 房屋详情缓存时间
HOUSE_DETAIL_REDIS_CACHE_EXPIRES = 1800
