import time
import logging
from flask import Flask, request, jsonify
from config import DakaPay
from wxpay import WxPay, get_nonce_str, dict_to_xml, xml_to_dict


app = Flask(__name__)


@app.route('/')
def index():
    '''

    :return:
    '''
    return jsonify({'errcode': 0, 'errmsg': 'ok'})


@app.route('/wxpay/pay')
def create_pay():
    '''
    请求支付
    :return:
    '''
    data = {
        'appid': DakaPay["appid"],
        'mch_id': DakaPay["mch_id"],
        'nonce_str': get_nonce_str(),
        'body': '测试'.encode(),                      # 商品描述
        'out_trade_no': str(int(time.time())),       # 商户订单号
        'total_fee': '1',
        'spbill_create_ip': DakaPay["spbill_create_ip"],
        'notify_url': DakaPay["notify_url"],
        'attach': {"openId":"fasgasgasgasg"},
        'trade_type': DakaPay["trade_type"],
        'openid': "fafasgasgas"
    }

    wxpay = WxPay(DakaPay["merchant_key"], **data)
    pay_info = wxpay.get_pay_info()
    if pay_info:
        return jsonify(pay_info)
    return jsonify({'errcode': 40001, 'errmsg': '请求支付失败'})

def saveDakaPrePay():
    pass

@app.route('/wxpay/notify', methods=['POST'])
def wxpay():
    '''
    支付回调通知
    :return:
    '''
    if request.method == 'POST':
        logging.info(xml_to_dict(request.data))
        result_data = {
            'return_code': 'SUCCESS',
            'return_msg': 'OK'
        }
        return dict_to_xml(result_data), {'Content-Type': 'application/xml'}


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=6111,
        debug=True
    )
