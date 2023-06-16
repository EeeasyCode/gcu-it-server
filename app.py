from flask import Flask, request, jsonify, send_file
import urllib.request
from urllib.parse import urlparse
import json
import re
from op import *
from flask_cors import CORS
import requests as rq
import time
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
app = Flask(__name__)
CORS(app)

@app.route("/download-kakao", methods=['GET'])
def download_kakao():
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

    gen_otp_data = {
        'locale': 'ko_KR',
        'tboxisuCd_finder_stkisu0_0': '035720/카카오',
        'isuCd': 'KR7035720002',
        'isuCd2': 'KR7035720002',
        'codeNmisuCd_finder_stkisu0_0': '카카오',
        'param1isuCd_finder_stkisu0_0': 'ALL',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'menuId': 'MDC0201020203',
        'url': 'url',
        'pdfJsDelay': '5000',
        'pdftemplet': 'mdc_pd'
    }
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
    otp = rq.post(gen_otp_url, gen_otp_data, headers=headers).text

    down_url = 'http://data.krx.co.kr/comm/fileDn/download_pdf/download.cmd'
    down_sector_KS = rq.post(down_url, {'code': otp}, headers=headers)

    with open('{}.pdf'.format('kakao'), 'wb') as f:
        f.write(down_sector_KS.content)
    time.sleep(1)
    return send_file('kakao.pdf', as_attachment=True)

@app.route("/download-samsung", methods=['GET'])
def download_samsung():
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'

    gen_otp_data = {
        'locale': 'ko_KR',
        'tboxisuCd_finder_stkisu0_0': '005930/삼성전자',
        'isuCd': 'KR7005930003',
        'isuCd2': '005930',
        'codeNmisuCd_finder_stkisu0_0': '삼성전자',
        'param1isuCd_finder_stkisu0_0': 'ALL',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'menuId': 'MDC0201020203',
        'url': 'url',
        'pdfJsDelay': '5000',
        'pdftemplet': 'mdc_pd'
    }
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
    otp = rq.post(gen_otp_url, gen_otp_data, headers=headers).text

    down_url = 'http://data.krx.co.kr/comm/fileDn/download_pdf/download.cmd'
    down_sector_KS = rq.post(down_url, {'code': otp}, headers=headers)

    with open('{}.pdf'.format('samsung'), 'wb') as f:
        f.write(down_sector_KS.content)
    time.sleep(1)
    return send_file('samsung.pdf', as_attachment=True)

@app.route("/news", methods=['POST'])
def keyword():
    req = request.get_json()

    text_ck = req['userRequest']['utterance']
    text = '정보를 찾을 수 없습니다.'
    print(text_ck)
    encText = urllib.parse.quote(text_ck)
    url = 'https://openapi.naver.com/v1/search/news?query=' + encText

    requests = urllib.request.Request(url)
    requests.add_header("X-Naver-Client-Id", client_id)
    requests.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(requests)
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        text = text_ck + "에 관련된 기사입니다.\n\n"
        json_data = json.loads(response_body.decode('utf-8'))

        pattern_punctuation = re.compile(r'<.*?>')
        first_title = pattern_punctuation.sub('', json_data["items"][0]['title'])
        second_title = pattern_punctuation.sub('', json_data["items"][1]['title'])
        third_title = pattern_punctuation.sub('', json_data["items"][2]['title'])
        pattern_punctuation = re.compile(r'&.*?;')
        first_title = pattern_punctuation.sub('', first_title)
        second_title = pattern_punctuation.sub('', second_title)
        third_title = pattern_punctuation.sub('', third_title)
        print(json_data['items'])
        text += '제목: ' + first_title + '\n' + '링크: ' + json_data["items"][0]['link'] + '\n\n'
        text += '제목: ' + second_title + '\n' + '링크: ' + json_data["items"][1]['link'] + '\n\n'
        text += '제목: ' + third_title + '\n' + '링크: ' + json_data["items"][2]['link'] + '\n\n'

    else:
        print("Error Code:" + rescode)

    # 답변 텍스트 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)


@app.route("/test", methods=['POST'])
def test():
    req = request.get_json()
    buy_rsi_value = req["buy_rsi_value"] if req["buy_rsi_value"] != "" else 35
    buy_mfi_value = req["buy_mfi_value"] if req["buy_mfi_value"] != "" else 35
    buy_macd_value = req["buy_macd_value"] if req["buy_macd_value"] != "" else -0.5

    sell_rsi_value = req["sell_rsi_value"] if req["sell_rsi_value"] != "" else 65
    sell_mfi_value = req["sell_mfi_value"] if req["sell_mfi_value"] != "" else 65
    sell_macd_value = req["sell_macd_value"] if req["sell_macd_value"] != "" else 0.6

    buy_value = {"rsi_val":buy_rsi_value, "mfi_val":buy_mfi_value, "macd_val":buy_macd_value}
    sell_value = {"rsi_val": sell_rsi_value, "mfi_val": sell_mfi_value, "macd_val": sell_macd_value}
    ticker = req["ticker"]
    start_date = req["start_date"]
    asset = req["asset"]
    if ticker == '' or start_date == '':
        res = {
            "error": "필수 입력 값을 다시 확인해주세요."
        }
        return jsonify(res)

    admin = stock_fn(asset)
    print(admin)
    data = return_dataframe(ticker, start_date)
    profit, rate = if_used(data, admin, buy_value, sell_value)

    res = {
        "profit": int(profit),
        "rate": int(rate)
    }

    return jsonify(res)


@app.route("/how", methods=['POST'])
def how():
    req = request.get_json()
    ticker = req["ticker"]
    stock_share = req["stock_share"]
    buy_date = req["buy_date"]
    ticker = yf.Ticker(ticker)
    df = ticker.history(start=buy_date)

    now_price = int(df['Close'].tail(1).values)
    past_price = int(df['Close'].head(1).values)
    profit = (now_price - past_price) * stock_share
    rate = round(now_price/past_price * 100 - 100, 1)
    res = {
        "now_price": now_price,
        "past_price": past_price,
        "profit": profit,
        "rate": rate
    }

    return jsonify(res)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001
            , threaded=True)
