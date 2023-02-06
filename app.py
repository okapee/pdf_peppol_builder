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

# font_path = Path(__file__).parent / "static" / "font" / "kokuri-subset.ttf"
# custom_font = TrueTypeFont.true_type_font_from_file(font_path)

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

# Cloud SQLに接続し、テーブルを作成する(テーブルは予めコンソールから作成しておくこと!)
# connection = pymysql.connect(host='34.84.231.41', user='root', password='Gn4+*5biC8=1nACI', db='peppol-builder')
# with connection.cursor() as cursor:
#     print(cursor.execute("show databases;"))
#     sql = '''
#     CREATE TABLE aiueo (
#        student_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#        first_name VARCHAR(50) NULL,
#        last_name VARCHAR(50) NULL,
#        birthday DATE NULL,
#        gender ENUM('F','M')
#     )'''
#     cursor.execute(sql)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/call_from_ajax", methods=["POST"])
def callfromajax():
    if request.method == "POST":
        encoded_string = ""
        global filename
        req = request.get_json()
        # app.logger.warning(f'filename: {request.json["fileSpecNo"]}')
        filename = f'output_{req["fileSpecNo"]}.pdf'
        file_path = f"./tmp/{filename}"
        app.logger.warning(f"file_path: {file_path}")
        app.logger.warning(f"filename: {filename}")
        invoiceNo = req["invoiceNo"]
        issueDate = req["issueDate"]
        issuer = req["issuer"]

        # 明細取得


        detail1 = req['detail1']
        # detailList = request.form['detail1[]']

        # app.logger.warning(f"invoice_no: {invoiceNo}, issueDate: {issueDate}")
        app.logger.warning(f"detail1: {detail1}")

        # output_path = Path.cwd() / "tmp" / filename

        # A4の新規PDFファイルを作成
        page = canvas.Canvas(f"/tmp/{filename}", pagesize=portrait(A4))
        app.logger.warning(f"page: {page}")

        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 18)

        amount = str(int(detail1[2])*int(detail1[3]) / 1.1) if req["amount"] == "" else req["amount"]

        page.drawRightString(20 * cm, 28 * cm, f"発行日: {issueDate}")
        page.drawRightString(20 * cm, 27 * cm, f"請求書番号: {invoiceNo}")
        page.drawString(1 * cm, 23 * cm, f"{issuer} 御中")
        page.drawString(1 * cm, 22 * cm, f'ご請求金額: {amount} 円')
        page.drawString(1 * cm, 21 * cm, f'お支払期限: {req["dueDate"]}')
        page.drawRightString(20 * cm, 22 * cm, f'{req["issuerAddress"]}')
        page.drawRightString(20 * cm, 21 * cm, f'{req["issuerTel"]}')

        # 指定座標が左端となるように文字を挿入 Ａ４サイズは、縦２９．７cm、横２１．０cm
        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 25)
        page.drawString(10 * cm, 25 * cm, "請求書")

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

        page.drawCentredString(65, 450, "1")
        page.drawCentredString(190, 450, detail1[1])
        page.drawCentredString(350, 450, detail1[2])
        page.drawCentredString(430, 450, detail1[3])
        app.logger.warn(f'detail1 type: {detail1[2]}')
        page.drawCentredString(510, 450, str(int(detail1[2])*int(detail1[3])))

        page.drawString(
            50,
            150,
            f'振込先: {req["bank"]}銀行  {req["bBranch"]}支店  {req["accountType"]}  {req["accountNo"]}  {req["accountName"]}',
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

    # return send_file(
    #     downloadFile,
    #     as_attachment=True,
    #     mimetype="text/xml",
    # )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
