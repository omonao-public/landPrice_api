import json
import requests
import xml.etree.ElementTree as et


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
    return result['values']
