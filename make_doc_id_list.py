import requests
import pandas as pd

def make_doc_id_list(day_list,public_company_list):
    securities_report_doc_list = []
    #Pythonのenumerate()関数を使うと、forループの中でリスト（配列）などのイテラブルオブジェクトの要素と同時にインデックス番号（カウント、順番）を取得できる。
    for index, day in enumerate(day_list):
        url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
        #EDINET_API仕様書参照。type2=提出書類一覧及びメタデータ
        params = {"date": day, "type": 2}
        res = requests.get(url, params=params)
        json_data = res.json()
        print(day)
        public_company_df = public_company_list
        for num in range(len(json_data["results"])):
            #ordinance_code=府令コード
            ordinance_code = json_data["results"][num]["ordinanceCode"]
            #form_code=様式コード
            form_code = json_data["results"][num]["formCode"]
            #edinetCode=提出者EDINETコード
            edinetCode = json_data["results"][num]["edinetCode"]
            #有価証券報告書の府令コード、様式コードを指定
            if ordinance_code == "010" and form_code == "030000" and edinetCode in public_company_df['EDINET_code'].values:
                # and edinetCode in ['E03521','E02889','E04806',"E04911","E05310"]
                # and edinetCode in edinetCodeList
                # and edinetCode == 'E00518'
                #docDescription=提出書類概要
                print(json_data["results"][num]["filerName"], json_data["results"][num]["docDescription"],
                      json_data["results"][num]["docID"])
                #取得した書類リストを作成する
                securities_report_doc_list.append(json_data["results"][num]["docID"])

    return securities_report_doc_list