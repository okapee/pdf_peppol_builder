from zengin_code import Bank
import pandas as pd

banks = []
bankCodes = []
bankNames = []
bankHiras = []
bankKanas = []
bankRomas = []
branches = []
branchBankCode = []
branchCodes = []
branchNames = []
branchHiras = []
branchKanas = []
branchRomas = []

# Excelファイルを読み込む
df = pd.read_excel("code6_20200727.xlsx", sheet_name="2020年07月27日現在")

# D列の3行目以降のデータを抽出し、値があるセルだけをリスト化する
filtered_list = df.iloc[1:, 3].dropna().tolist()

allCodeList = [str(value).zfill(4) for value in filtered_list]

for code in allCodeList:
    try:
        bank = Bank[code]
        bankCodes.append(code)
        bankNames.append(bank.name)
        bankHiras.append(bank.hira)
        bankKanas.append(bank.kana)
        bankRomas.append(bank.roma)
        branches = bank.branches

        for branchCode in branches:
            branch = branches[branchCode]
            branchBankCode.append(code)
            branchCodes.append(branchCode)
            branchNames.append(branch.name)
            branchHiras.append(branch.hira)
            branchKanas.append(branch.kana)
            branchRomas.append(branch.roma)
    except Exception as e:
        continue

# print(f"bankCode: {len(bankCodes)}, bankName: {len(bankNames)}, bankHira: {len(bankHiras)}, bankKana: {len(bankKanas)}, bankRoma: {len(bankRomas)}")

# 各リストからデータフレームを作成
bank_data = {
    "bankCode": bankCodes,
    "bankName": bankNames,
    "bankHira": bankHiras,
    "bankKana": bankKanas,
    "bankRoma": bankRomas,
}
bank_df = pd.DataFrame(bank_data)

branch_data = {
    "branchBankCode": branchBankCode,
    "branchCode": branchCodes,
    "branchName": branchNames,
    "branchHira": branchHiras,
    "branchKana": branchKanas,
    "branchRoma": branchRomas,
}
branch_df = pd.DataFrame(branch_data)

# データフレームを表示
# print(bank_df)
print(branch_df)

# Excelにデータフレームを出力
# bank_df.to_excel("bank.xlsx", index=False)
bank_df.to_csv("bank.csv", index=False)
branch_df.to_csv("branch.csv", index=False)