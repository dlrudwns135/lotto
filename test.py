import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dateutil.rrule import rrule,WEEKLY
from datetime import date

def _db_connect():
    url=''
    port=''
    client = MongoClient(url, port)
    return client

def _init_lotto(url):
    now = date.today()
    diff_weeks_list = list(rrule(WEEKLY, dtstart=date(2002, 12, 7), until=now))
    end = 'true'
    i = 0;
    soup = []
    while end == 'true':
        # for i in range(0,10):
        use_url = url + '&nowPage=' + str(i + 1) + '&drwNoStart=1&drwNoEnd=' + str(len(diff_weeks_list))
        source_code = requests.get(use_url)
        plain_text = source_code.text
        use_soup = BeautifulSoup(plain_text, 'lxml')
        trs = use_soup.select('.tblType1.mt40 > tbody > tr')
        if (len(trs) != 12):
            end = 'false'
        soup.append(trs)
        i += 1
    return soup

def _parse_url(url):
    now = date.today()
    diff_weeks_list = list(rrule(WEEKLY, dtstart=date(2002, 12, 7), until=now))
    nowStage = len(diff_weeks_list)
    client = _db_connect()
    db = client.lotto
    cllct = db.lotto
    data_latest = cllct.find_one({'no':str(nowStage)})
    soup = []
    if data_latest is None:
        use_url = url + '&nowPage=1&drwNoStart=1&drwNoEnd=' + str(len(diff_weeks_list))
        source_code = requests.get(use_url)
        plain_text = source_code.text
        use_soup = BeautifulSoup(plain_text, 'lxml')
        trs = use_soup.select('.tblType1.mt40 > tbody > tr')
        soup.append(trs)
    client.close()
    return soup


def _parse_lotto(rawdata):
    data = []
    for i in range(0,len(rawdata)):
        for j in range(1,len(rawdata[i])-1):
            data_as = {};
            data_child = rawdata[i][j].select('td')[1].text.split(',')
            data_as.__setitem__('no',rawdata[i][j].select('td')[0].text)
            data_as.__setitem__('data', data_child)
            data.append(data_as)
    return data

if __name__ == '__main__':
    #soup = _init_lotto('http://www.nlotto.co.kr/gameResult.do?method=allWin')
    soup = _parse_url('http://www.nlotto.co.kr/gameResult.do?method=allWin')
    data = _parse_lotto(soup)
    if data != []:
        print(data)
        client = _db_connect()
        db = client.lotto
        cllct = db.lotto
        print(str(data))
        cllct.insert(data)
        # print(client)
