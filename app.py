from pathlib import Path
from datetime import datetime
from flask import (
    Flask,
    request,
    render_template,
    Response,
    send_file,
    make_response,
    send_from_directory,
    redirect,
    flash,
    session,
)
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from flask_login import LoginManager, UserMixin
from logging.config import dictConfig

import random
import math
import json
import base64
import logging
import psycopg2

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MIMETYPE = "application/xml"

app = Flask(__name__)
bootstrap = Bootstrap(app)

font_path = Path.cwd() / "static/font/kokuri-subset.ttf"

# construct the Font object
pdfmetrics.registerFont(TTFont("kokuri", font_path))

file_path = ""
filename = ""
encoded_string = ""

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


@app.route("/login")
def login():
    conn = psycopg2.connect("postgresql://flaskuser:okazaki0608@localhost")


@app.route("/call_from_ajax", methods=["POST"])
def callfromajax():
    if request.method == "POST":
        app.logger.warning("---/call_from_ajax---")
        # encoded_string = ""
        global encoded_string
        global filename
        req = request.get_json()
        app.logger.warning('fileSpecNo: ' + req["fileSpecNo"])
        filename = f'output_{req["fileSpecNo"]}.pdf'
        file_path = f"./tmp/{filename}"
        taxAmount = 0
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
        buyerNo = req["buyerNo"]

        # A4の新規PDFファイルを作成
        page = canvas.Canvas(f"/tmp/{filename}", pagesize=portrait(A4))
        app.logger.warning(f"page: {page}")

        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 14)

        detailAmount = 0
        eightPerAmount = 0
        tenPerAmount = 0

        # 明細取得
        for i, detail in enumerate(req["detail"]):
            for j, value in enumerate(detail):
                print(f"({i},{j}): {value}")

                # 値がない場合、j=[0,1]は空文字を、j=[2,3]は数字の0を、j=4は10を挿入
                if j == 4 and value == "10%":
                    detailAmount += (
                        int(detail[2] if str.isdigit(detail[2]) else 0)
                        * int(detail[3] if str.isdigit(detail[3]) else 0)
                        * 1.1
                    )
                    tenPerAmount += (
                        int(detail[2] if str.isdigit(detail[2]) else 0)
                        * int(detail[3] if str.isdigit(detail[3]) else 0)
                        * 1.1
                    )
                elif j == 4 and value == "8%":
                    detailAmount += (
                        int(detail[2] if str.isdigit(detail[2]) else 0)
                        * int(detail[3] if str.isdigit(detail[3]) else 0)
                        * 1.08
                    )
                    eightPerAmount += (
                        int(detail[2] if str.isdigit(detail[2]) else 0)
                        * int(detail[3] if str.isdigit(detail[3]) else 0)
                        * 1.08
                    )
                elif j == 4:
                    detailAmount += int(
                        detail[2] if str.isdigit(detail[2]) else 0
                    ) * int(detail[3] if str.isdigit(detail[3]) else 0)

            # 消費税額合計を算出する
            taxTenAmount = tenPerAmount * 0.1
            taxEightAmount = eightPerAmount * 0.08

            page.drawCentredString(65, 450 - 25 * i, f"{i+1}")
            # 税率が8%のときに商品名の横にアスタリスクを表示する
            if detail[4] == "8%":
                page.drawCentredString(190, 450 - 25 * i, f"{detail[1]} *")
            else:
                page.drawCentredString(190, 450 - 25 * i, f"{detail[1]}")
            page.drawCentredString(350, 450 - 25 * i, detail[2])
            page.drawCentredString(430, 450 - 25 * i, detail[3])
            page.drawCentredString(
                510,
                450 - 25 * i,
                str(
                    math.floor(
                        int(detail[2] if str.isdigit(detail[2]) else 0)
                        * int(detail[3] if str.isdigit(detail[3]) else 0)
                        * 10
                    )
                    / 10
                ),
            )

        # 表示用請求金額
        dispAmount = ""

        if str.isdigit(amount):
            dispAmount = str(math.floor(int(amount) * 10) / 10)
        elif detailAmount != 0:
            dispAmount = str(math.floor(detailAmount * 10) / 10)
        else:
            dispAmount = "0"

        # taxExclusiveAmount = float(dispAmount) - taxAmount
        app.logger.warning(f"buyer: {buyer}")

        page.setFont("kokuri", 18)
        page.drawRightString(20 * cm, 28 * cm, f"発行日: {issueDate}")
        page.drawRightString(20 * cm, 27 * cm, f"請求書番号: {invoiceNo}")
        page.drawString(1 * cm, 21 * cm, f"{buyer} 御中")
        page.drawString(1 * cm, 20 * cm, f"ご請求金額: {dispAmount} 円")
        page.drawString(1 * cm, 19 * cm, f"お支払期限: {dueDate}")

        page.setFont("kokuri", 16)
        page.drawRightString(20 * cm, 22 * cm, f"{issuer}")
        page.drawRightString(20 * cm, 21 * cm, f"{issuerAddress}")
        page.drawRightString(20 * cm, 20 * cm, f"{issuerTel}")
        page.drawRightString(20 * cm, 19 * cm, f"登録番号: T-{registerNo}")

        # 指定座標が左端となるように文字を挿入 Ａ４サイズは、縦２９．７cm、横２１．０cm
        # フォントの設定(第1引数：フォント、第2引数：サイズ)
        page.setFont("kokuri", 26)
        page.drawString(9 * cm, 25 * cm, "請求書")

        # 明細
        # This Block Consist of Costumer Details
        # roundRect 1&2: 左下隅の座標、 3: 幅、 4: 高さ、 5: 丸み
        page.roundRect(40, 80, 520, 100, 5, stroke=1, fill=0)
        page.setFont("kokuri", 14)

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
            f"振込先: {bank}銀行  {bBranch}支店  {accountType}  {accountNo}  {accountName}",
        )

        # PDFファイルとして保存
        page.save()

        # JPPINTのXMLファイルを組み立て

        # JPPINTファイル出力

        print(f"post_filename: {filename}")
        with open(f"/tmp/{filename}", "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        dict = {
            "encoded_string": encoded_string.decode(),
        }  # 辞書
    return json.dumps(dict)
    # return "test"
    # return "test"


@app.route("/xml/show", methods=["POST"])
def xml_show():
    # global encoded_string
    """
    XML データ表示
    """
    req = request.get_json()
    taxAmount = 0
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
    buyerNo = req["buyerNo"]

    app.logger.info(f"global encoded_string: {encoded_string}")

    # issueDateのフォーマットを整形
    issueDate = datetime.strptime(issueDate, '%Y/%m/%d').date() if issueDate else datetime.today().date()
    # issueDate = d.strftime('%Y/%m/%d')

    app.logger.info(f"issuer: {issuer}, buyer: {buyer}")

    detailAmount = 0
    eightPerAmount = 0
    tenPerAmount = 0

    app.logger.info(f'明細配列: {req["detail"]}')

    # 明細取得
    for i, detail in enumerate(req["detail"]):
        for j, value in enumerate(detail):
            print(f"({i},{j}): {value}")

            # 値がない場合、j=[0,1]は空文字を、j=[2,3]は数字の0を、j=4は10を挿入
            if j == 4 and value == "10%":
                detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )
                tenPerAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )
            elif j == 4 and value == "8%":
                detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )
                eightPerAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )
            elif j == 4:
                detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )

    # 消費税額合計を算出する
    taxTenAmount = math.floor(tenPerAmount * 0.1)
    taxEightAmount = math.floor(eightPerAmount * 0.08)
    taxAmount = taxTenAmount + taxEightAmount

    # 表示用請求金額
    dispAmount = ""

    # 請求額は小数点第二位まで
    # if str.isdigit(amount):
    #     dispAmount = str(round(int(amount), 2))
    # elif detailAmount != 0:
    #     dispAmount = str(round(detailAmount + taxAmount, 2))
    # else:
    #     dispAmount = "0"

    # dispAmountとdetailAmountの値が異なる場合、detailAmountを優先する
    if amount == str(detailAmount):
        pass
    else:
        dispAmount = str(round(detailAmount + taxAmount, 2))

    # taxExclusiveAmount = float(dispAmount) - taxAmount

    return Response(
        render_template(
            "pint_min.xml",
            invoiceNo=invoiceNo,
            issueDate=issueDate,
            registerNo=registerNo,
            issuer=issuer,
            buyerNo=buyerNo,
            buyer=buyer,
            taxAmount=taxAmount,
            tenPerAmount=tenPerAmount,
            taxTenAmount=taxTenAmount,
            eightPerAmount=eightPerAmount,
            taxEightAmount=taxEightAmount,
            dispAmount=dispAmount,
            taxExclusiveAmount=detailAmount,
            lines=req["detail"],
            encoded_string=encoded_string,
        ),
        mimetype="application/xml",
    )


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
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = "attachment;filename=pint_min.xml"
    return response


if __name__ == "__main__":
    # 環境変数を設定する.
    # import os
    # os.environ["PYTHON_ENV"] = "local"
    app.run(host="0.0.0.0", port=8888, debug=True)
