#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import traceback

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradeCreateModel import AlipayTradeCreateModel
from alipay.aop.api.request.AlipayTradeCreateRequest import AlipayTradeCreateRequest
from alipay.aop.api.response.AlipayTradeCreateResponse import AlipayTradeCreateResponse
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a',)
logger = logging.getLogger('')
if __name__ == '__main__':
    # 实例化客户端
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'http://openapi.alipaydev.com/gateway.do'
    alipay_client_config.app_id = '2021004125649036'
    alipay_client_config.app_private_key = 'MIIEpAIBAAKCAQEAkuUw+De9CwuhUQpBsVd8pqL8HP9yAMHgP5IOx+kudvsvQsB8eB562za6mABi9hD3oILEMFUOHv76FaUEu6hb2nSUCgQV5WBHpYHVrJ8RfuEqh9oHbvJ6MSmebv7XAa5U5xvWOiIsAjXCFkOw8rJxbH+K9vOUHIdCDw2G7uaMAUaYE4HgwfIqu6UnpEWNovieYA70cyw8s5EZJThnMzb0NYEwQzh3V2U+j1rz3vPYV83tnuz7gJE2Hu8qEEUPOFDBeO3k3GdI8CRs3hL8vlN2PzoWTHg6b6rLdCxhKsX2o9GYTumJek/1pEpOFxy/0Vf9IS3zTryL5zRx+wW0mhFonwIDAQABAoIBAQCH0FHLXTVyrekTVWlRfvLn2o9AfEk6PAaKoA78dDKanTif/fnW0U+DuIEiolDc8ukQRXcAvNMWg2ZTdsP+gPWT7+8jp41bCv6THoyhUlzJs4MwIbx3rsadB77NHt9JVZZ4KvuRuiB4Vp3BGgrTCXrm9rFUC/bnvYKtCjO0VAIj9mtwsYDfEXgYA9JJN3TCm1rOljgivEI8Cmm0rvOhgsv5QtY0/qGFb4l3zfuYw9NtSFkgBqbibzZr88Dhy7MCoV9OCRTEJq6UMDJKIjO5jIWxFjTsaW/HOXDUroyB0p/XQMlZ4IxWvuR+Hl1P6Ewn1FUho8mHRcS0Xjrr2xY0vtpZAoGBAMOVa5lHO4/nvfD3YalaqcVaqeDY+MHSl9RJZjJEzMf69ehTfghyYYzgRtgz0xuGmsxuGbDCpeLF+fh/KePkGoIdUVHuf0odfbEW3KRbwP955bW6Jf3AISyGNGckGfqde+B2NAIu0sgzIGnAD0WLYSCweznLn0JmrfKvMXw+oOdLAoGBAMBFiW5VXAN6Cz4KCbNXQEL4KqFdfMpv0+88edDq0l6j2/U54ElEarkgcqjt7i1gdX0UuOHmfZryRDETDJtXtWEp80ytMP6ajLbo4Oa5LF0eap8QVyDyROTbBLFeY4urAathVsI0rpL7xm1i9LPWUJPFmi+H0uywSuDZWcyDSMt9AoGAVTz/odOrn7Ht0+DcjURYDQzQUI//CenQBdLfWTUm0lkLZu9MVD4VSaJM/djIPozRVhr9001hoo2JvcUd6pX0/5PrZvu8Of7UUqOWEYNzf2QOur6f5BEh5BexKupO8CxGWrLpQ7JIZrvxemUbwsFV2TtQ2QVnKTc6xDOaK33X/jUCgYBnBdt5zysagc58U4yXF+1K9QaCqEExh3IcAl+TXf+SzmIRqA1RtOMqhwRpF/RDRCgv+WaHRKWQ3LdFRFvA8OIzSfMf5r0V72HusCGx/w6SZrXivTKyaJ4ZsnF1SIo2UE74sZN3RBs2jsnn2tobcn6Cb6MKTNDsGhpFGLFRMBdVUQKBgQC0RtlxQeyQPEXOywY/OFVkUQEvmo2K8DAwLGf8QYjkxgt/B+ULDPp4EY5q+Kj6NY+z4CyebzOW7fuaw9b2EjbbKP6eRZSV/T11oW4QzDGaw3uuCQg2iyIW1ftZHQmnXp55aALNBxNI8Tcgkfp+f+015NI+u63cJ3n+6UuiWeHJXA=='
    alipay_client_config.alipay_public_key = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAikL3BdmoK14KCqXsuJZCWpKQAcSUAYrGiHqvhUoo7loH7VE1D7Vtv5a4JKfY7xCOqyQBDQMX5jyMOyl3NbC9neUhmyMkGJNccChYLt6qZcsAbzx3aGjSCukgtCRpg5ebP81LccFjKhX8HUZufOKqaOdb7yI/ZrgjaBS+emilo9Q7+XDBYrWGFS1zdIF2103kr7oasxeIxSFXv787Pr605Vn3eBPjq0vYMTf9Q/ksc59WNOdVNurfZe1b+4CqM7du9Dw/b4B2aB1gq9AscF/MpMhkMUB/cFWoWPrDOl/OvrXvCgfsYCYZJjEIdt/hJKYnAIu9gnBCmXXd7TE1sbE1uQIDAQAB'
    client = DefaultAlipayClient(alipay_client_config, logger)
    # 构造请求参数对象
    model = AlipayTradeCreateModel()
    model.out_trade_no = "20150320010101001"
    model.total_amount = "30"
    model.subject = "Iphone6 16G"
    model.buyer_id = "2088******846880"
    request = AlipayTradeCreateRequest(biz_model=model)
    # 执行API调用
    response_content = False
    try:
        response_content = client.execute(request)
    except Exception as e:
        print(traceback.format_exc())
    if not response_content:
        print("failed execute")
    else:
        # 解析响应结果
        response = AlipayTradeCreateResponse()
        response.parse_response_content(response_content)
        # 响应成功的业务处理
        if response.is_success():
            # 如果业务成功，可以通过response属性获取需要的值
            print("get response trade_no:" + response.trade_no)
        # 响应失败的业务处理
        else:
            # 如果业务失败，可以从错误码中可以得知错误情况，具体错误码信息可以查看接口文档
            print(response.code + "," + response.msg + "," + response.sub_code + "," + response.sub_msg)
