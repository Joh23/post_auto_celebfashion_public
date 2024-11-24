import streamlit as st
import os
from pyairtable import Api

def get_api_key(key_name):
    return st.secrets.get(key_name) or os.environ.get(key_name)

AIRTABLE_API_KEY = get_api_key("AIRTABLE_API_KEY")
BASE_ID = 'appYlgoRy8QQ7YLJS'
TABLE_NAME = '셀럽패션'

api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

def fetch_all_records():
    records = table.all()
    return [{
        'id': record['id'],
        '핵심키워드': record['fields'].get('핵심키워드', ''),
        '블로그 글': record['fields'].get('블로그 글', ''),
        '이미지1': record['fields'].get('이미지1', [{}])[0].get('url', ''),
        '이미지2': record['fields'].get('이미지2', [{}])[0].get('url', ''),
        '이미지3': record['fields'].get('이미지3', [{}])[0].get('url', ''),
        '이미지4': record['fields'].get('이미지4', [{}])[0].get('url', ''),
        '아이템이미지1': record['fields'].get('아이템이미지1', [{}])[0].get('url', ''),
        '아이템이미지2': record['fields'].get('아이템이미지2', [{}])[0].get('url', ''),
        '아이템이미지3': record['fields'].get('아이템이미지3', [{}])[0].get('url', '')
    } for record in records]

def fetch_record_by_id(record_id):
    record = table.get(record_id)
    if record:
        return {
            'id': record['id'],
            '블로그 글': record['fields'].get('블로그 글', ''),
            '이미지1': record['fields'].get('이미지1', [{}])[0].get('url', ''),
            '이미지2': record['fields'].get('이미지2', [{}])[0].get('url', ''),
            '이미지3': record['fields'].get('이미지3', [{}])[0].get('url', ''),
            '이미지4': record['fields'].get('이미지4', [{}])[0].get('url', ''),
            '아이템이미지1': record['fields'].get('아이템이미지1', [{}])[0].get('url', ''),
            '아이템이미지2': record['fields'].get('아이템이미지2', [{}])[0].get('url', ''),
            '아이템이미지3': record['fields'].get('아이템이미지3', [{}])[0].get('url', '')
        }
    return None