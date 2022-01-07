from numpy import int64
import requests
import pandas as pd
import zipfile
from io import BytesIO
from edinet_xbrl.edinet_xbrl_object import EdinetData, EdinetXbrlObject
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from bs4 import BeautifulSoup
import time
import re

def make_ref(df):
    #key,コンテキストID対応表を読み込み
    df = df.to_dict(orient='list')
    return df['key'] ,df['contextRef'],df['内容']

def download_xbrl_in_zip(securities_report_doc_list, number_of_lists,GetItemList_target , GetItemList_tag,GetItemList_tag_auditreport):
    company_info_lists = []
    #取得したい項目を読込
    df = GetItemList_target
    #辞書形式に変換
    df = df.to_dict(orient='list')
    save_explanations = df['内容']

    for index, doc_id in enumerate(securities_report_doc_list):
        print(doc_id, ":", index + 1, "/", number_of_lists)
        url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents/" + doc_id
        params = {"type": 1}
        res = requests.get(url, params=params, stream=True)

        if res.status_code == 200:
            #Zipファイルを取得する
            z = zipfile.ZipFile(BytesIO(res.content))

            #Zipに格納されているファイル一覧をリストに格納する
            lst = z.infolist()
            
            #XBRLファイルのみを抜き出す
            open_file = [s.filename for s in lst if '.xbrl' in s.filename and 'PublicDoc' in s.filename]

            #key,コンテキストID対応表を読み込み
            keys, context_refs, explanations = make_ref(GetItemList_tag)

            with z.open(open_file[0]) as myfile:
                #XBRLファイルの中身を取り出す
                xbrl_content = myfile.read().decode()
                parser = EdinetXbrlParser()
                xbrl_object = EdinetXbrlObject()
                parser_2 = BeautifulSoup(xbrl_content, 'html.parser')
                #企業ごとに各項目のデータを入れるリストを作成
                company_info_list = {}
                for node in parser_2.find_all():
                    parser.put_node(xbrl_object, node)
                edinet_xbrl_object = xbrl_object
                #EDINETコードを取得
                edinet_code_num = edinet_xbrl_object.get_data_by_context_ref('jpdei_cor:EDINETCodeDEI', 'FilingDateInstant').get_value()
                for (key,context_ref,explanation) in zip(keys,context_refs,explanations):
                    try:
                        key = key.replace("REPLACE",edinet_code_num)
                        company_info_list[explanation] = edinet_xbrl_object.get_data_by_context_ref(key, context_ref).get_value()
                    except Exception as e:
                        pass

            open_file = [s.filename for s in lst if '.xbrl' in s.filename and 'AuditDoc' in s.filename]
            #key,コンテキストID対応表を読み込み
            keys, context_refs, explanations = make_ref(GetItemList_tag_auditreport)

            with z.open(open_file[0]) as myfile:
                #XBRLファイルの中身を取り出す
                xbrl_content = myfile.read().decode()
                parser = EdinetXbrlParser()
                xbrl_object = EdinetXbrlObject()
                parser_2 = BeautifulSoup(xbrl_content, 'html.parser')
                #企業ごとに各項目のデータを入れるリストを作成
                for node in parser_2.find_all():
                    parser.put_node(xbrl_object, node)
                edinet_xbrl_object = xbrl_object

                #会社名,EDINETコードを取得
                for (key,context_ref,explanation) in zip(keys,context_refs,explanations):
                    try:
                        key = key.replace("REPLACE",edinet_code_num)
                        designated_data = edinet_xbrl_object.get_data_by_context_ref(key, context_ref).get_value()
                        designated_data = designated_data.replace(' ','')
                        designated_data = designated_data.replace('　','')
                        company_info_list[explanation] = designated_data
                    except:
                        pass
                # タグ等を削除（データクレンジング）
                company_info_list['事業の内容'] = re.sub('\n|\u3000|\xa0|なお、.*?。|<.*?>|３.*【事業の内容】|3.*【事業の内容】|\(.*?\)|\（.*?\）', '',company_info_list['事業の内容'])

            company_info_lists.append(company_info_list)
    
    save_df = pd.DataFrame(company_info_lists, columns = save_explanations)
    save_df = save_df.fillna({'当年度監査報酬（ネットワークファーム）':0,'前年度監査報酬（ネットワークファーム）':0})
    save_df = save_df.fillna(' ')

    return save_df