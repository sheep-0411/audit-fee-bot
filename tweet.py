import time
import pandas as pd

def tweet(api,company_info_list):
    for index, row in company_info_list.iterrows():
        try:
            audit_fee_prior = int((int(row['前年度監査報酬']) + int(row['前年度監査報酬（ネットワークファーム）'])) / 1000000)
            audit_fee = int((int(row['当年度監査報酬']) + int(row['当年度監査報酬（ネットワークファーム）'])) / 1000000)

            kam_message = ''
            i = 1
            for kam in [row['KAM1'],row['KAM2'],row['KAM3'],row['KAM4'],row['KAM5']]:
                if kam != ' ':
                    kam_message = kam_message + 'KAM' + str(i) + ' ' + kam + '\n'
                    i = i + 1

            message = row['会社名'] + '\n' + row['所在地'] + '\n' + row['提出者業種'] + '\n' + '期末日 ' + row['期末日'] + '\n' + '提出日 ' + str(row['提出日']) + '\n' + '監査報酬 ' + str('{:,}'.format(audit_fee)) + '百万円' + '(前期' + str('{:,}'.format(audit_fee_prior)) + '百万円)' + '\n' + row['監査法人']

            api.update_status(status=message[:139])
            print(message)
            time.sleep(5)
            message = kam_message[:139]
            #リプライ対象のツイートを取得
            tweet = api.user_timeline(screen_name='audit_fee_bot', count=1, page=1)[0]
            print(tweet.id,tweet.user.screen_name)
            reply_text = message
            # テキスト(メッセージ)のみ
            api.update_status(status = reply_text, in_reply_to_status_id = tweet.id)
            print(reply_text)
            reply_text = '↓監査報酬データベース' + '\n' + 'https://audit-fee-app0711.herokuapp.com/' + '\n' + '↓有価証券報告書（EDINET）' + '\n' + 'https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63010CXW1E6A010DSPSch&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63011&PID=W1E63010&SESSIONKEY=1627132255934&lgKbn=2&pkbn=0&skbn=0&dskb=&dflg=0&iflg=0&preId=1&row=100&idx=0&syoruiKanriNo=&mul=' + row['EDINETコード'] + '&fls=on&cal=1&era=R&yer=&mon=&pfs=4'
            api.update_status(status = reply_text, in_reply_to_status_id = tweet.id)
            print(reply_text)
            time.sleep(5)
        except Exception as e:
            print(e)
