from numpy import int64
import tweepy
from dotenv import find_dotenv, load_dotenv
import os
import datetime
from make_day_list import make_day_list
from make_doc_id_list import make_doc_id_list
from download_xbrl_in_zip import download_xbrl_in_zip
import pandas as pd

# Googleスプレッドシートとの連携に必要なライブラリ
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from tweet import tweet

# 設定
file_name = 'audit-fee-bot'

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# .envファイルを探して読み込む
load_dotenv(find_dotenv())

# 辞書オブジェクト。認証に必要な情報をHerokuの環境変数から呼び出している
credential = {
"type": "service_account",
"project_id": os.environ['SHEET_PROJECT_ID'],
"private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
"private_key": os.environ['SHEET_PRIVATE_KEY'],
"client_email": os.environ['SHEET_CLIENT_EMAIL'],
"client_id": os.environ['SHEET_CLIENT_ID'],
"auth_uri": "https://accounts.google.com/o/oauth2/auth",
"token_uri": "https://oauth2.googleapis.com/token",
"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
"client_x509_cert_url":  os.environ['SHEET_CLIENT_X509_CERT_URL']
}
# スプレッドシートにアクセス
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credential, scope)
gc = gspread.authorize(credentials)
sh = gc.open(file_name)

# 環境変数から認証情報を取得する。(Twitter)
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

# 認証情報を設定する。
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# シートの選択　シートの番号でも名前でもよい
wks1 = sh.worksheet('public_company_list')
wks2 = sh.worksheet('(Target)GetItemList')
wks3 = sh.worksheet('(Tag)GetItemList')
wks4 = sh.worksheet('(Tag_auditreport)GetItemList')

wks5 = sh.worksheet('save_data')
wks6 = sh.worksheet('date')

# シートから全部から読み込み
def get_records(wks):
    record = pd.DataFrame(wks.get_all_records())
    return record

df1 = get_records(wks1)
df2 = get_records(wks2)
df3 = get_records(wks3)
df4 = get_records(wks4)
df5 = get_records(wks5)
df6 = get_records(wks6)

def main():
    #取得したい期間を設定する
    start_date = datetime.datetime.strptime(df6['start_date'][0], '%Y/%m/%d').date()
    end_date = datetime.datetime.strptime(df6['end_date'][0], '%Y/%m/%d').date()
    #指定した期間を1日ごとにリスト化する
    day_list = make_day_list(start_date, end_date)
    print(day_list)
    #ドキュメントを検索する
    securities_report_doc_list = make_doc_id_list(day_list,df1)
    print(securities_report_doc_list)
    #取得する書類の総数
    number_of_lists = len(securities_report_doc_list)
    print("number_of_lists：", len(securities_report_doc_list))
    print("get_list：", securities_report_doc_list)
    #データを取得する
    get_df = download_xbrl_in_zip(securities_report_doc_list, number_of_lists,df2,df3,df4)
    tweet(api,get_df)
    save_df = pd.concat([df5,get_df],join='inner',axis=0,sort=False,ignore_index=True)

    # 列名とデータを連結して書き込み
    # ,value_input_option='USER_ENTERED'を加えることで数値型の入力が可能
    wks5.update([save_df.columns.values.tolist()] + save_df.values.tolist(),value_input_option='USER_ENTERED')
if __name__ == "__main__":
    main()