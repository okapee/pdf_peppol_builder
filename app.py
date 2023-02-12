from pathlib import Path
from flask import (
    Flask,
    request,
    render_template,
    send_file,
    make_response,
    send_from_directory,
)
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from logging.config import dictConfig

import random
import math
import json
import base64
import logging

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from datetime import datetime
from decimal import Decimal

MIMETYPE = "application/xml"

app = Flask(__name__)
bootstrap = Bootstrap(app)

print(f'pathlib: {Path.cwd() / "static/font" }')

font_path = Path.cwd() / "static/font/kokuri-subset.ttf"

# construct the Font object
pdfmetrics.registerFont(TTFont("kokuri", font_path))

file_path = ""
filename = ""

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/call_from_ajax", methods=["POST"])
def callfromajax():
    if request.method == "POST":
        encoded_string = ""
        global filename
        req = request.get_json()
        filename = f'output_{req["fileSpecNo"]}.pdf'
        file_path = f"./tmp/{filename}"
        invoiceNo = req["invoiceNo"]
        issueDate = req["issueDate"]
        issuer = req["issuer"]
        issuerAddress = req["issuerAddress"]
        issuerTel = req["issuerTel"]
        issueDate = req["issueDate"]
        amount = req["amount"]
        dueDate = req["dueDate"]
        dealDate = req["dealDate"]
        registerNo = req["registerNo"]
        bank = req["bank"]
        bBranch = req["bBranch"]
        accountType = req["accountType"]
        accountNo = req["accountNo"]
        accountName = req["accountName"]
        buyer = req["buyer"]

        # A4の新規PDFファイルを作成
        page = canvas.Canvas(f"/tmp/{filename}", pagesize=portrait(A4))
        app.logger.warning(f"page: {page}")

        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 18)

        detailAmount = 0
        # 明細取得
        for i, detail in enumerate(req['detail']):
            for j,value in enumerate(detail):
                print(f'({i},{j}): {value}')

                # 値がない場合、j=[0,1]は空文字を、j=[2,3]は数字の0を、j=4は10を挿入
                if j == 4 and value == '10%':
                    detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(detail[3] if str.isdigit(detail[3]) else 0) * 1.1
                elif j == 4 and value == '8%':
                    detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(detail[3] if str.isdigit(detail[3]) else 0) * 1.08
                elif j == 4:
                    detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(detail[3] if str.isdigit(detail[3]) else 0)

            page.drawCentredString(65, 450 - 25*i, f"{i+1}")
            # 税率が8%のときに商品名の横にアスタリスクを表示する
            if detail[4]=='8%':
                page.drawCentredString(190, 450 - 25*i, f'{detail[1]} *')
            else:
                page.drawCentredString(190, 450 - 25*i, f'{detail[1]}')
            page.drawCentredString(350, 450 - 25*i, detail[2])
            page.drawCentredString(430, 450 - 25*i, detail[3])
            page.drawCentredString(510, 450 - 25*i, str(math.floor(int(detail[2] if str.isdigit(detail[2]) else 0)*int(detail[3] if str.isdigit(detail[3]) else 0)*10) / 10))

        # 表示用請求金額
        dispAmount = ''

        if str.isdigit(amount):
            dispAmount = str(math.floor(int(amount)*10) / 10)
        elif detailAmount != 0:
            dispAmount = str(math.floor(detailAmount*10) / 10)
        else:
            dispAmount = '0'
        
        app.logger.warning(f"buyer: {buyer}")

        page.drawRightString(20 * cm, 28 * cm, f"発行日: {issueDate}")
        page.drawRightString(20 * cm, 27 * cm, f"請求書番号: {invoiceNo}")
        page.drawString(1 * cm, 23 * cm, f"{buyer} 御中")
        page.drawString(1 * cm, 22 * cm, f'ご請求金額: {dispAmount} 円')
        page.drawString(1 * cm, 21 * cm, f'お支払期限: {dueDate}')
        page.drawRightString(20 * cm, 23 * cm, f'{issuer}')
        page.drawRightString(20 * cm, 22 * cm, f'{issuerAddress}')
        page.drawRightString(20 * cm, 21 * cm, f'{issuerTel}')
        page.drawRightString(20 * cm, 20 * cm, f'登録番号: T-{registerNo}')

        # 指定座標が左端となるように文字を挿入 Ａ４サイズは、縦２９．７cm、横２１．０cm
        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 25)
        page.drawString(9 * cm, 25 * cm, "請求書")

        # 明細
        # This Block Consist of Costumer Details
        # roundRect 1&2: 左下隅の座標、 3: 幅、 4: 高さ、 5: 丸み
        page.roundRect(40, 80, 520, 100, 5, stroke=1, fill=0)
        page.setFont("kokuri", 15)

        # This Block Consist of Item Description
        page.roundRect(40, 200, 520, 300, 5, stroke=1, fill=0)
        page.line(40, 470, 560, 470)
        page.drawCentredString(65, 480, "No.")
        page.drawCentredString(190, 480, "品目")
        page.drawCentredString(350, 480, "単価")
        page.drawCentredString(430, 480, "数量")
        page.drawCentredString(510, 480, "税抜合計")
        #  Drawing table for Item Description
        page.line(90, 200, 90, 500)
        page.line(300, 200, 300, 500)
        page.line(400, 200, 400, 500)
        page.line(460, 200, 460, 500)

        page.drawString(
            50,
            150,
            f'振込先: {bank}銀行  {bBranch}支店  {accountType}  {accountNo}  {accountName}',
        )

        # PDFファイルとして保存
        page.save()

        # JPPINTのXMLファイルを組み立て

        # JPPINTファイル出力

        print(f"post_filename: {filename}")
        with open(f"/tmp/{filename}", "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        dict = {
            "invoice_no": "9999",
            "encoded_string": encoded_string.decode(),
        }  # 辞書
    return json.dumps(dict)
    # return "test"


@app.route("/pdfdownload", methods=["GET"])
def pdfdownload():
    downloadFile = f"/tmp/{filename}"

    return send_file(
        downloadFile,
        as_attachment=True,
        mimetype="application/xml",
    )

@app.route("/pintdownload", methods=["GET"])
def pintdownload():
    downloadFile = "/tmp/pint_min.xml"

    """
    XML ファイル ダウンロード
    """
    response = make_response()
    response.data = render_template("pint_min.xml")
    response.headers['Content-Type'] = 'application/xml'
    response.headers['Content-Disposition'] = 'attachment;filename=pint_min.xml'
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
