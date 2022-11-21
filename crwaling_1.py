# -*- encoding:utf-8 -*-
import requests
import sys
import time
import traceback
import logging
import os
import csv
import pymongo

from bs4 import BeautifulSoup


reload(sys)
sys.setdefaultencoding('utf-8')

def all_league_urls(base_url):
    try:
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'html.parser')
        soup.find_all('section')[3].find_all('div')[0].find_all('option')[-1].decompose()
        all_league_urls = soup.find_all('section')[3].find_all('div')[0].find_all('option')
    except Exception as e:
        print(e.message)
    return all_league_urls

#url완성하기
def all_url(url):
    url = 'https://www.espn.com/soccer/table/_/league/%s' % (url)
    return url

#현재 페이지의 리그 이름
def current_page_league_name(soup):
    current_page_league_names = soup.find('div', class_='Table__Title')
    return current_page_league_names

def find_league_name_rank(soup):
    return soup.find_all('div',class_='flex')[1]

def game(all_league_urls):
    for all_league_url in all_league_urls[6:11]:
        try:
            urls = all_league_url['value']
            urls = all_url(urls)
            res = requests.get(urls)
            soup = BeautifulSoup(res.text,'html.parser')
            league_name = current_page_league_name(soup)
            if league_name == None:
                pass
            else:
                league_names = str(league_name.get_text())
                temps_2.append(league_names)
                find_temp = find_league_name_rank(soup)
                temp_head = find_temp.find('thead',class_='Table__header-group Table__THEAD').get_text()
                head = find_temp.find('thead',class_='Table__header-group Table__THEAD')
                temp_bodys = head.parent.parent.find('tbody').find_all('tr')
                temp_scores = soup.find_all('div',class_='flex')[1].find_all('tbody')[1].find_all('tr')
                #team_score
                for temp_score in temp_scores:
                    spans = temp_score.find_all('span')
                    if spans != [] and spans[0]['class'][0] != 'fw-medium' :
                        GP = str(spans[0].get_text())
                        W = str(spans[1].get_text())
                        D = str(spans[2].get_text())
                        L = str(spans[3] .get_text())
                        F = str(spans[4] .get_text())
                        A = str(spans[5] .get_text())
                        GD = str(spans[6] .get_text())
                        P = str(spans[7] .get_text())
                        result = {
                            'GP' : GP,
                            'W' : W,
                            'D' : D,
                            'L' : L,
                            'F' : F,
                            'A' : A,
                            'GD' : GD,
                            'P' : P,
                            'league_name' : league_names
                        }
                        temps_0.append(result)
                #team_rank_name
                if temp_head != '':
                    group = str(head.parent.parent.find_all('tr')[0].get_text())
                    if group != 'Group' and group[0] == '2':
                        for temp_body in temp_bodys:
                            temp_span = temp_body.find_all('span')
                            rank = str(temp_span[0].get_text())
                            team = str(temp_span[3].get_text())
                            temp_1 = {
                                'rank' : rank,
                                'team' : team,
                                'season' : group
                            }
                            temps_1.append(temp_1)
                    elif group[0] != '2':
                        for temp_body in temp_bodys:
                            temp_span = temp_body.find_all('span')
                            rank = str(temp_span[0].get_text())
                            team = str(temp_span[3].get_text())
                            temp_1 = {
                                'rank' : rank,
                                'team' : team,
                                'division season' : group
                            }
                            temps_1.append(temp_1)
                else:
                    for temp_body in temp_bodys:
                        if temp_body.find('span',class_='hide-mobile') != None:
                            team = str(temp_body.find('span',class_='hide-mobile').get_text())
                            temp_2 = {
                                'team' : team
                            }
                        temp_spans = temp_body.find_all('span')
                        if temp_spans != []:
                            temp_span = temp_body.find_all('span')[0]
                            temp_rank = str(temp_spans[0].get_text())
                            if temp_rank.upper().find('GROUP') == 0:
                                group = temp_rank
                            elif temp_span['class'][0] == 'fw-medium' and temp_rank[0] != 'G':
                                division_season = temp_rank
                                group = ''
                            else:
                                rank = temp_rank
                                temp_2['group'] = str(group)
                                temp_2['rank'] = str(rank)
                                temp_2['division_season'] = str(division_season)
                                temps_1.append(temp_2)
        except Exception as e:
            print(e.message+"\n"+traceback.format_exc()+'\n'+urls)

def list_merge():
    for index in range(0,len(temps_1)):
        try:
            temp_info.append(dict(temps_0[index], **temps_1[index]))
            for temp_2 in temps_2:
                if temp_2 == temp_info[index]['league_name']:
                    result = {
                        temp_2 : {
                            'info' : str(temp_info[index])
                        }
                    }
                    info.append(result)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(len(temps_1),len(temps_0))


def print_info():
    for idx in info:
        print(idx)

try:
    base_url = 'https://www.espn.com/soccer/standings/_/league/usa.1'
    temps_0 = []
    temps_1 = []
    temps_2 = []
    temp_info = []
    info = []

    #로그 생성
    logger = logging.getLogger()
    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(mesege)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler('crwaling.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    game(all_league_urls(base_url))
    list_merge()
    print_info()
except Exception as e:
    print(e)