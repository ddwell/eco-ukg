import re
import os
from decimal import Decimal 
import numpy as np
import time, datetime
import dateutil.parser as dparser
from collections import Counter

import urllib.request
from bs4 import BeautifulSoup as BS
from selenium import webdriver

def get_post_measurements(content):    
    popup = content.find("div",{'class':'leaflet-popup-content-wrapper'})
    post_name = popup.find("div",{'class':'popup'}).find('b').contents[0]
    post_id = re.findall(r'\d+', post_name)[0]
    post_measurements = {}
    for row in popup.find("div",{'class':'leaflet-popup-content'}).find_all("div",{'class':'indicators'}):
        for indicator in row.find_all("div",{'class':'clear'}):
            if indicator is not None:
                param = indicator.find('b').text[:-1]
                measurement = indicator.contents[3][:-4].strip()
                if 'обслуж' in measurement:
                    measurement = '-1'
                post_measurements.update({param : measurement})
    return post_id,post_measurements

def get_weather_measurements(content):    
    weather_data = []
    for post in content.find("div",{'id':'data'}).find_all("div",{'class':'popup'}):
        if not 'обслуж' in post.text:
            wind = post.find('span').attrs['title']
            extData = [i.text for i in post.find_all("strong")]
            extData.append(re.search('(?<=\().*?(?=\))', wind).group()[:-1])
            weather_data += extData[1:]
        else:
            weather_data += ['-1']*6
    return weather_data

def getMeasurementsNow(browser, spf = 1200.0, period = 60*60*24,pageURL = 'http://ceb-uk.kz/map/'):    
        
    outfilename = os.path.join(os.path.abspath('data'),time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.csv')
    
    if not os.path.exists(outfilename):
        mode = 'w+'
    elif os.stat(outfilename).st_size > 0:
        mode = 'a'        
    else:
        mode = 'w'
        
    with open(outfilename, mode) as csvfile:
        print("<%s>" % outfilename)         
        if mode == 'w+' or mode =='w':
            csvfile.write('servertime,timestamp,1_CO,1_CxHy,1_HCl,1_HCOH,1_NO2,1_SO2,2_CO,2_CxHy,2_HCl,2_HCOH,2_NO2,2_SO2,3_CO,3_CxHy,3_HCl,3_HCOH,3_NO2,3_SO2,4_CO,4_CxHy,4_HCl,4_HCOH,4_NO2,4_SO2,5_CO,5_CxHy,5_HCl,5_HCOH,5_NO2,5_SO2,6_CO,6_CxHy,6_HCl,6_HCOH,6_NO2,6_SO2,7_CO,7_CxHy,7_HCl,7_HCOH,7_NO2,7_SO2,8_Cl2,8_CO,8_CxHy,8_HCOH,8_NO2,8_SO2,9_CO,9_CxHy,9_HCOH,9_HF,9_NO2,9_SO2,11_temp, 11_atmp, 11_windspeed, 11_humi, 11_precipitation, 11_winddirection, 12_temp, 12_atmp, 12_windspeed, 12_humi, 12_precipitation, 12_winddirection')
            csvfile.write('\n')     

    try:
        browser.get(pageURL)
        
        delay = 1 + np.random.randint(2) + np.random.rand()
        time.sleep(delay)
        
        browser.find_element_by_class_name('toggle-menu').click()

        delay = 1 + np.random.randint(2) + np.random.rand()
        time.sleep(delay)
                
        content = BS(browser.page_source, 'lxml') 

        data_entry = []
        for i,element in enumerate(browser.find_elements_by_class_name('clear')):
            element.click()
            content = BS(browser.page_source, 'lxml') 

            post_id, post_measurements = get_post_measurements(content)
            data_entry.append( ','.join(post_measurements.values()) ) 

            delay = np.random.randint(2) + np.random.rand()
            time.sleep(delay)
            if i>=8:
                break 

        browser.find_elements_by_tag_name('option')[-1].click()
        content = BS(browser.page_source, 'lxml') 
        data_entry_weather = get_weather_measurements(content)                

        content = BS(browser.page_source, 'lxml') 
        text = content.find("span",{'id':'date'}).text

        servertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        timestamp = dparser.parse(text, fuzzy=True).strftime("%Y-%m-%d %H:%M:%S")
        line = servertime+','+timestamp+',' +','.join(data_entry+data_entry_weather)

        with open(outfilename, 'a') as csvfile:
            csvfile.write(line)
            csvfile.write('\n')
            
        print("%s, %s" % (servertime, timestamp)  )
        
        browser.find_element_by_class_name('toggle-menu').click()

        delay = 1 + np.random.randint(10) + np.random.rand()

    except(KeyboardInterrupt, SystemExit):
        print("\nprocess interrupted %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) 

        
        
        
path_to_chromedriver = os.path.join(os.path.abspath('chromedriver'), 'chromedriver.exe')


try:
    spf = 1200
    frametime = spf  
    starttime = 0
    while True:                  
        if frametime >= spf:        
            starttime = time.time() 
            
            browser = webdriver.Chrome(executable_path = path_to_chromedriver)
            
            getMeasurementsNow(pageURL = pageURL, browser = browser)
            
            browser.close()
            #servertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #print(servertime)

        #FIXED TIME STEP technique
        frametime = time.time() - starttime 
except:    
    servertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s process interrupted' % servertime)     