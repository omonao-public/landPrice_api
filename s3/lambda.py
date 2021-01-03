import json
import requests
import xml.etree.ElementTree as et
import boto3
import pandas as pd
import io

def get_location_gc(address):
  url_gc = 'https://www.geocoding.jp/api?q={addr}'.format(addr=address)
  res_gc = requests.get(url_gc)
  xml_result = et.fromstring(res_gc.text)
  
  lat = xml_result[2][0].text
  lng = xml_result[2][1].text
  return float(lat), float(lng)

    
def lambda_handler(event, context):
    lat, lng = get_location_gc(event.get('address', ''))
    if lat * lng == 0:
        return {'statusCode': 404, 'body': 'lat, lng is not defined'}
     
    url_rm = 'https://api.rakumachi.jp/land_price?lat={lat}&lng={lng}'.format(lat=lat, lng=lng)
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
    headers = { 'User-Agent' : user_agent }
    res_rm = requests.get(url_rm, headers=headers)
    
    result = json.loads(res_rm.text)
    
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='calc-chika', Key='citycode.csv')
    value = response['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(value), encoding='utf-8')
    df.columns = ['city_code', 'prefecture', 'city', 'prefecture_kana', 'city_kana']
    
    response = s3_client.get_object(Bucket='calc-chika', Key='citycode_2.csv')
    value = response['Body'].read().decode('utf-8')
    df_2 = pd.read_csv(io.StringIO(value), encoding='utf-8', header=None, names=['city_code', 'city', 'city_kana'])
    
    for i, r in enumerate(result['values']):
        city_code = str(r['city_code'])
        tgt = df[[str(cc).startswith(city_code) for cc in df['city_code']]]
        if len(tgt) > 0:
            result['values'][i]['city_name'] = tgt.iloc[0]['prefecture'] + tgt.iloc[0]['city']
        else:
            tgt = df_2[[str(cc).startswith(city_code) for cc in df_2['city_code']]]
            if len(tgt) > 0:
                result['values'][i]['city_name'] = tgt.iloc[0]['city']
            
    
    return result['values']
