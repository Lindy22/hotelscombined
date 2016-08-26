import sys
#import httplib2
import urllib3
import psycopg2
import psycopg2.extras
import lxml.etree
import time
import datetime
import threading
#import psycopg2_bulk_insert
#import psycopg2_etl_utils
#import nike_etl
import uuid
import decimal
import pickle
import ConfigParser
import re
import json
import random
import os
import codecs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import selenium



feed_code=-99
bookmaker_code=-99
#nike_etl.feed_code=feed_code
#nike_etl.bookmaker_code=bookmaker_code
aodds_uuid=uuid.UUID('8f01ed84-8e1e-4397-a258-c2bc9a03645d')
#nike_etl.aodds_uuid=aodds_uuid

##http="http://"
##hostname="http://theahl.com/stats/schedule.php?view=season&team_id=-1&season_id=48&home_away=&division_id="
htmlparser=lxml.etree.HTMLParser()
seasons_list = {}
##event_url_match=http+hostname+gamedate

def get_url(httpcon, url):
    headers = {}
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Accept-Language"] = "cs,en-us;q=0.7,en;q=0.3"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0"
    #headers["Cookie"]="op_cookie-test=ok;op_oddsportal=cv704mv1ek2l60ijve9iq9hn62;op_user_cookie=32830896;D_UID=739B93C4-5FB3-34AB-A4B5-0C2C36C3347E"
    res=httpcon.urlopen("GET", url, headers=headers)
    
    if res.status!=200:
        print res.status
        raise Exception("Unable to get_url "+url)
    #print res.data
    return res.data


city = "Tokio"
page_size_reg = re.compile('(pageSize=[0-9]{1,3})+')


def get_events(httpcon,main_url,city):
    price_dict_three={}
    hotels_dict_three={}
    price_dict_four={}
    hotels_dict_four={}
    price_dict_five={}
    hotels_dict_five={}
##    page=get_url(httpcon,main_url)
##    q=lxml.etree.fromstring(page,htmlparser)
##    print type(q), len(q)
##    print ''.join(q[1].itertext())
    browser = webdriver.Firefox()
    browser.get(main_url)
    destination = browser.find_element_by_id('hc_f_id_where_1')
    destination.send_keys(city)
    time.sleep(2)
    browser.find_element_by_xpath('//ul[@id="ui-id-1"]/li[1]/a').click()
    time.sleep(2)
    checkIn_month = Select(browser.find_element_by_xpath('//div[@id="HC_DateSelection_checkin_1"]/div[@class="hc_f_t_s3 hc_f_month"]/label/select'))
    checkIn_month.select_by_value("2016-9")
    checkIn_day = Select(browser.find_element_by_xpath('//div[@id="HC_DateSelection_checkin_1"]/div[@class="hc_f_t_s3 hc_f_day"]/label/select'))
    checkIn_day.select_by_value("19")
    checkOut_month = Select(browser.find_element_by_xpath('//div[@id="HC_DateSelection_checkout_1"]/div[@class="hc_f_t_s3 hc_f_month"]/label/select'))
    checkOut_month.select_by_value("2016-9")
    checkOut_day = Select(browser.find_element_by_xpath('//div[@id="HC_DateSelection_checkout_1"]/div[@class="hc_f_t_s3 hc_f_day"]/label/select'))
    checkOut_day.select_by_value("22")
    browser.find_element_by_xpath('//a[@data-element="moreOptions"]').click()
    time.sleep(2)
    browser.find_element_by_id('hc_f_filter_star_3').click()
    browser.find_element_by_id('hc_f_filter_star_4').click()    
    browser.find_element_by_id('hc_f_filter_star_5').click()
    browser.find_element_by_xpath('//a[@class="hc_f_btn_v15"]').click()
    time.sleep(10)
    browser.find_element_by_xpath('//li[@data-field="MinRate"]/a').click()
    time.sleep(2)
    actual_url = browser.current_url
##    print actual_url
    page_size = str(page_size_reg.findall(actual_url)[0].encode('utf-8')).strip(" []''""")
    new_page_size = '500'
##    print page_size
##    .split('=')[1]
##    print actual_url.replace(page_size,'pageSize=%s' % new_page_size)
    new_url = actual_url.replace(page_size,'pageSize=%s' % new_page_size)
    browser.get(new_url)
    browser.refresh()
    time.sleep(5)  
    page_source=browser.page_source
    root = lxml.etree.fromstring(page_source,htmlparser)
    number_of_hotels = int(root.xpath('count(//div[@id="hc_sr"]/div)'))
    print number_of_hotels
    mouse = webdriver.ActionChains(browser)
      
    for i in range(1,number_of_hotels):
##        print i
        was_price_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/div[@class="hc_sri_result_promotedDeal"]/p[@class="hc_hotel_wasPrice"]/text()' % i)
        price_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/div[@class="hc_sri_result_promotedDeal"]/p[@class="hc_hotel_price"]/text()' % i)
        stars_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/p[contains(@class,"hc-hotelrating")]/@title' % i)
        name_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a/text()' % i)  
        no_of_nights_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/div[@class="hc_sri_result_promotedDeal"]/p[@class="hc_hotel_numberOfNights"]/strong/text()' % i)
        rating_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/p[@class="hc_hotel_userRating"]/a/text()' % i)
        reviews_xpath = root.xpath('//div[@id="hc_sr"]/div[%s]/div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/p[@class="hc_hotel_numberOfReviews"]/span/text()' % i)
##        print no_of_nights_xpath
        if len(price_xpath) > 0:
            price = int(price_xpath[1].encode('utf-8').replace('\xc2\xa0','').strip(' '))
        else:
            continue
        if len(stars_xpath) > 0:
            stars = stars_xpath[0].encode('cp1250')
        else:
            stars = 'bez hvìzdièek'
        if len(name_xpath) > 0:
            hotel_name = name_xpath[0].encode('utf-8')
        else:
            hotel_name = 'Bez názvu'
        if len(rating_xpath) > 0:
            rating = rating_xpath[0].encode('cp1250')
        else:
            rating = 'Bez hodnocení'
        if len(reviews_xpath) > 0:
            reviews = int(reviews_xpath[0].encode('utf-8').replace('\xc2\xa0','').strip(' '))
        else:
            reviews = 'Nehodnoceno'
        if len(was_price_xpath) > 0:
            was_price = int(was_price_xpath[2].encode('utf-8').replace('\xc2\xa0','').strip(' '))
        else:
            was_price = 'Neuvedeno'
        if len(no_of_nights_xpath) > 0:
            no_of_nights = no_of_nights_xpath[0]
        else:
            no_of_nights = 'Neni uveden pocet noci'
        
##        print link_xpath
##        sys.exit(0)
##        link = main_url + link_xpath[0]
        if stars == '(3 hvìzdièky)':
            hotels_list_three = str(price) + ';' + str(was_price) + ';' + hotel_name + ';' + stars + ';' + rating + ';' + str(reviews) + ';' + str(no_of_nights)
            hotels_dict_three[i] = hotels_list_three
            price_dict_three[i] = price
        elif stars == '(4 hvìzdièky)':
            hotels_list_four = str(price) + ';' + str(was_price) + ';' + hotel_name + ';' + stars + ';' + rating + ';' + str(reviews) + ';' + str(no_of_nights)
            hotels_dict_four[i] = hotels_list_four
            price_dict_four[i] = price
        elif stars == '(5 hvìzdièek)':
            hotels_list_five = str(price) + ';' + str(was_price) + ';' + hotel_name + ';' + stars + ';' + rating + ';' + str(reviews) + ';' + str(no_of_nights)
            hotels_dict_five[i] = hotels_list_five
            price_dict_five[i] = price
##        hotels_list = str(price) + ';' + hotel_name + ';' + stars + ';' + rating + ';' + str(reviews)
##        hotels_dict[i] = hotels_list
##        price_dict[i] = int(price_xpath[1].encode('utf-8').replace('\xc2\xa0','').strip(' '))
##        print stars_xpath[0].encode('cp1250')
##        print name_xpath[0].encode('utf-8')
##        print rating_xpath[0].encode('cp1250')
##        print int(reviews_xpath[0].encode('utf-8').replace('\xc2\xa0','').strip(' '))
 
    if len(price_dict_three) > 0:
        min_price_three = min(price_dict_three,key=price_dict_three.get)
        price_list_sorted_three = sorted(price_dict_three,key=price_dict_three.get)
        for minimum_three in range(0,5): #max length is len(hotels_dict)
            output_three = hotels_dict_three[price_list_sorted_three[minimum_three]].split(';',7)
            a_element = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_three[2])
            mouse.move_to_element(a_element).context_click().perform()
            link_xpath = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_three[2]).get_attribute("href")
##            print link_xpath
            
            print 'Cena: ' + output_three[0] + ' Kè'
            print 'Pùvodni cena: ' + output_three[1] + ' Kè'
            print 'Poèet nocí: ' + output_three[6]
            print 'Jméno hotelu: ' + output_three[2]
            print 'Poèet hvìzdièek: ' + output_three[3]
            print 'Hodnocení: ' + output_three[4]
            print 'Poèet hodnocení: ' + output_three[5]
            print 'Odkaz na hotel: ' + link_xpath
            print '------------------------------------------------------------------------------------------------------------------------'
        print '********************************************************************************************************************************************'
    if len(price_dict_four) > 0:
        min_price_four = min(price_dict_four,key=price_dict_four.get)
        price_list_sorted_four = sorted(price_dict_four,key=price_dict_four.get)
        for minimum_four in range(0,10): #max length is len(hotels_dict)
            output_four = hotels_dict_four[price_list_sorted_four[minimum_four]].split(';',7)
            a_element = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_four[2])
            mouse.move_to_element(a_element).context_click().perform()
            link_xpath = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_four[2]).get_attribute("href")

            print 'Cena: ' + output_four[0] + ' Kè'
            print 'Pùvodni cena: ' + output_four[1] + ' Kè'
            print 'Poèet nocí: ' + output_four[6]
            print 'Jméno hotelu: ' + output_four[2]
            print 'Poèet hvìzdièek: ' + output_four[3]
            print 'Hodnocení: ' + output_four[4]
            print 'Poèet hodnocení: ' + output_four[5]
            print 'Odkaz na hotel: ' + link_xpath
            print '----------------------------------------------------------------------------------------------------------------------'
        print '********************************************************************************************************************************************'
    if len(price_dict_five) > 0:
        min_price_five = min(price_dict_five,key=price_dict_five.get)
        price_list_sorted_five = sorted(price_dict_five,key=price_dict_five.get)
        for minimum_five in range(0,5): #max length is len(hotels_dict)
            output_five = hotels_dict_five[price_list_sorted_five[minimum_five]].split(';',7)
            a_element = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_five[2])
            mouse.move_to_element(a_element).context_click().perform()
            link_xpath = browser.find_element_by_xpath('//div[@class="hc_m_outer"]/div[@class="hc_m_content"]/div[@class="hc_hotel hc_sri_result"]/h3/a[@title="%s"]' % output_five[2]).get_attribute("href")
            print 'Cena: ' + output_five[0] + ' Kè'
            print 'Pùvodni cena: ' + output_five[1] + ' Kè'
            print 'Poèet nocí: ' + output_three[6]
            print 'Jméno hotelu: ' + output_five[2]
            print 'Poèet hvìzdièek: ' + output_five[3]
            print 'Hodnocení: ' + output_five[4]
            print 'Poèet hodnocení: ' + output_five[5]
            print 'Odkaz na hotel: ' + link_xpath
            print '-----------------------------------------------------------------------------------------------------------------------'
        print '********************************************************************************************************************************************'
    browser.close()
        
##    print min_price 
##    print price_list_sorted
##        print price_dict[i]
##        print price_dict
##        print sorted(price_dict.values())
##radit podle ceny za noc a k tomu mit prirazene informace o nazvu hotelu, poctu hvezdicek, hodnoceni hotelu a poctu hodnoceni hotelu
##mozna udelat tri ruzne sekce: serazene 3* hotely podle ceny za noc a to stejne zvlast pro 4* a 5* tzn. tri oddelene vystupy
## 3* hotely:
## Jméno: Astory
## cena za noc: 1500
## hodnoceni: 4.0
## pocet hodnoceni: 2532
## a to stejne pro ostatni kategorie 4* a 5*
   
httpcon = urllib3.PoolManager()
####[get_events(httpcon,http+hostname+j) for j in gamedate_list]
url = "http://www.hotelscombined.com"
get_events(httpcon,url,city)
##get_links()
