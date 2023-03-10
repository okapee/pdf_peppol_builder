from pathlib import Path
from flask import (
    Flask,
    request,
    render_template,
    Response,
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

# encoded_string = ""
# invoiceNo = ""
# issueDate = ""
# issuer = ""
# issuerAddress = ""
# issuerTel = ""
# issueDate = ""
# amount = ""
# dueDate = ""
# dealDate = ""
# registerNo = ""
# bank = ""
# bBranch = ""
# accountType = ""
# accountNo = ""
# accountName = ""
# buyer = ""
# buyerNo = ""

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

        # A4?????????PDF?????????????????????
        page = canvas.Canvas(f"/tmp/{filename}", pagesize=portrait(A4))
        app.logger.warning(f"page: {page}")

        # ?????????????????????(???1???????????????????????????2??????????????????)
        page.setFont("kokuri", 14)

        detailAmount = 0
        eightPerAmount = 0
        tenPerAmount = 0

        # ????????????
        for i, detail in enumerate(req["detail"]):
            for j, value in enumerate(detail):
                print(f"({i},{j}): {value}")

                # ?????????????????????j=[0,1]??????????????????j=[2,3]????????????0??????j=4???10?????????
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

            # ?????????????????????????????????
            taxTenAmount = tenPerAmount * 0.1
            taxEightAmount = eightPerAmount * 0.08

            page.drawCentredString(65, 450 - 25 * i, f"{i+1}")
            # ?????????8%???????????????????????????????????????????????????????????????
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

        # ?????????????????????
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
        page.drawRightString(20 * cm, 28 * cm, f"?????????: {issueDate}")
        page.drawRightString(20 * cm, 27 * cm, f"???????????????: {invoiceNo}")
        page.drawString(1 * cm, 21 * cm, f"{buyer} ??????")
        page.drawString(1 * cm, 20 * cm, f"???????????????: {dispAmount} ???")
        page.drawString(1 * cm, 19 * cm, f"???????????????: {dueDate}")

        page.setFont("kokuri", 16)
        page.drawRightString(20 * cm, 22 * cm, f"{issuer}")
        page.drawRightString(20 * cm, 21 * cm, f"{issuerAddress}")
        page.drawRightString(20 * cm, 20 * cm, f"{issuerTel}")
        page.drawRightString(20 * cm, 19 * cm, f"????????????: T-{registerNo}")

        # ?????????????????????????????????????????????????????? ????????????????????????????????????cm??????????????????cm
        # ?????????????????????(???1???????????????????????????2??????????????????)
        page.setFont("kokuri", 26)
        page.drawString(9 * cm, 25 * cm, "?????????")

        # ??????
        # This Block Consist of Costumer Details
        # roundRect 1&2: ????????????????????? 3: ?????? 4: ????????? 5: ??????
        page.roundRect(40, 80, 520, 100, 5, stroke=1, fill=0)
        page.setFont("kokuri", 14)

        # This Block Consist of Item Description
        page.roundRect(40, 200, 520, 300, 5, stroke=1, fill=0)
        page.line(40, 470, 560, 470)
        page.drawCentredString(65, 480, "No.")
        page.drawCentredString(190, 480, "??????")
        page.drawCentredString(350, 480, "??????")
        page.drawCentredString(430, 480, "??????")
        page.drawCentredString(510, 480, "????????????")
        #  Drawing table for Item Description
        page.line(90, 200, 90, 500)
        page.line(300, 200, 300, 500)
        page.line(400, 200, 400, 500)
        page.line(460, 200, 460, 500)

        page.drawString(
            50,
            150,
            f"?????????: {bank}??????  {bBranch}??????  {accountType}  {accountNo}  {accountName}",
        )

        # PDF???????????????????????????
        page.save()

        # JPPINT???XML???????????????????????????

        # JPPINT??????????????????

        print(f"post_filename: {filename}")
        with open(f"/tmp/{filename}", "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        dict = {
            "encoded_string": encoded_string.decode(),
        }  # ??????
    return json.dumps(dict)
    # return "test"


@app.route("/xml/show", methods=["POST"])
def xml_show():
    """
    XML ???????????????
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

    app.logger.info(f"issuer: {issuer}, buyer: {buyer}")

    detailAmount = 0
    eightPerAmount = 0
    tenPerAmount = 0

    app.logger.info(f'????????????: {req["detail"]}')

    # ????????????
    for i, detail in enumerate(req["detail"]):
        for j, value in enumerate(detail):
            print(f"({i},{j}): {value}")

            # ?????????????????????j=[0,1]??????????????????j=[2,3]????????????0??????j=4???10?????????
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
                detailAmount += int(detail[2] if str.isdigit(detail[2]) else 0) * int(
                    detail[3] if str.isdigit(detail[3]) else 0
                )

    # ?????????????????????????????????
    taxTenAmount = tenPerAmount * 0.1
    taxEightAmount = eightPerAmount * 0.08
    taxAmount = taxTenAmount + taxEightAmount

    # ?????????????????????
    dispAmount = ""

    if str.isdigit(amount):
        dispAmount = str(math.floor(int(amount) * 10) / 10)
    elif detailAmount != 0:
        dispAmount = str(math.floor(detailAmount * 10) / 10)
    else:
        dispAmount = "0"

    taxExclusiveAmount = float(dispAmount) - taxAmount

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
            taxExclusiveAmount=taxExclusiveAmount,
            lines=req["detail"],
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
    XML ???????????? ??????????????????
    """
    response = make_response()
    response.data = render_template("pint_min.xml")
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = "attachment;filename=pint_min.xml"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
