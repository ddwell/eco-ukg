
# coding: utf-8

# In[278]:

import subprocess,os
# result = subprocess.run( ['mkdir','da'], stdout=subprocess.PIPE )
# print(result.stdout.decode())


# In[276]:

pwd = 'C:\\Users\\ddwell\\Documents\\Ecology'

def _get_input_files(directory, extensions=['.csv']):    
    files_list = []    
    filenames_array = [filenames for root, dirnames, filenames in os.walk(directory)]
    files  = [val for sublist in filenames_array for val in sublist]    
    
    if len(extensions) <= 1:
        files_list = [os.path.join(directory,file) for file in files if file.endswith(extensions[0])]
    else:
        for file in files:
            for ext in extensions:
                if file.endswith(ext):
                    files_list.append(os.path.join(directory,file))
    return files_list
                

files = _get_input_files(os.path.join(pwd,'data'), extensions=['.txt'])
files


# ## Selenium

# In[152]:

import re
import os
from decimal import Decimal 
import numpy as np
import time,datetime
import dateutil.parser as dparser
from collections import Counter

import urllib.request
from bs4 import BeautifulSoup as BS
from selenium import webdriver


# In[114]:

path_to_chromedriver = 'C:\Games\chromedriver\chromedriver.exe' # change path as needed
browser = webdriver.Chrome(executable_path = path_to_chromedriver)


# In[115]:

pageURL = 'http://ceb-uk.kz/map/'
browser.get(pageURL)
browser.find_element_by_class_name('toggle-menu').click()


# In[309]:

def get_posts_info(content):
    posts_data = {}

    for post in content.find_all("div",{'class':'clear item'}):
        
        post_name = post.find('b').contents[0]
        post_id = re.findall(r'\d+', post_name)[0]
        
        post_info =  {post_id:{ 
            'post_name':post_name,
            'post_description':post.find("div",{'class':'lite'}).contents[0], 
            'post_address':post.find("div",{'class':'lite'}).contents[2].text}}

        posts_data.update(post_info)
        
    return posts_data

content = BS(browser.page_source, 'lxml')  
posts_data = get_posts_info(content)

with open('data/posts.json', 'w') as csvfile:
    csvfile.write(str(posts_data))


# In[118]:

content = BS(browser.page_source, 'lxml') 
text = content.find("span",{'id':'date'}).text


# In[119]:

timestamp = dparser.parse(text, fuzzy=True).strftime("%Y-%m-%d %H:%M:%S")
timestamp


# In[418]:

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
                post_measurements.update({param : measurement})

    return post_id,post_measurements

data_header, data_entry = [], []

for i,element in enumerate(browser.find_elements_by_class_name('clear')):
    element.click()
    content = BS(browser.page_source, 'lxml') 
    
    post_id, post_measurements = get_post_measurements(content)
    
    data_header.append( ','.join([post_id+'_'+x for x in post_measurements.keys()]) )
    data_entry.append( ','.join(post_measurements.values()) ) 
    
    delay = np.random.randint(3) + np.random.rand()
    time.sleep(delay)
    
    if i>=8:
        break  

print('timestamp,' + ',\t'.join(data_header))
print(str(timestamp)+','+ ',\t'.join(data_entry))


# In[134]:

# browser.find_element_by_class_name('toggle-menu').click()
browser.find_elements_by_tag_name('option')[-1].click()# class_name('switcher').click()


# In[122]:

content = BS(browser.page_source, 'lxml') 


# ## Extraction

# In[1]:

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

def getMeasurementsNow(spf = 1200.0, period = 60*60*24, pageURL = 'http://ceb-uk.kz/map/'):    
        
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

    except:
        print("\nprocess interrupted %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))) 


# In[15]:

path_to_chromedriver = os.path.join(os.path.abspath('chromedriver'), 'chromedriver.exe') 
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

pageURL = 'http://ceb-uk.kz/map/'
#browser.get(pageURL)
#browser.find_element_by_class_name('toggle-menu').click()

# try:
getMeasurementsNow(pageURL = pageURL)
# except:
browser.close()


# In[ ]:

pageURL = 'http://ceb-uk.kz/map/'
path_to_chromedriver = os.path.join(os.path.abspath('chromedriver'), 'chromedriver.exe') 

try:
    spf = 1200
    frametime = spf  
    starttime = 0
    while True:                  
        if frametime >= spf:        
            starttime = time.time() 
            
            browser = webdriver.Chrome(executable_path = path_to_chromedriver)
            delay = 2+np.random.randint(2) + np.random.rand()
            time.sleep(delay)
            try:
                getMeasurementsNow(pageURL = pageURL) 
                delay = 2+np.random.randint(2) + np.random.rand()
                time.sleep(delay)
                browser.close()
            except:
                browser.close()
            #servertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #print(servertime)

        #FIXED TIME STEP technique
        frametime = time.time() - starttime 
except(KeyboardInterrupt, SystemExit):    
    servertime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s process interrupted' % servertime)        


# #### with Tor

# In[33]:

os.environ["TBB_PATH"] = "C:\\Users\\ddwell\\Desktop\\Tor Browser\\" #Browser\\firefox.exe
environ.get('TBB_PATH')


# In[49]:

# os.environ["PATH"] =  os.environ["PATH"] + 'C:\\Users\\ddwell\\Documents\\eco-ukg\\chromedriver\\geckodriver.exe;'

os.environ["PATH"]


# In[ ]:

'C:\\Users\\ddwell\\Desktop\\Tor Browser\\Browser:C:\\Users\\ddwell\\Desktop\\Tor Browser\\Browser:C:\\Users\\ddwell\\Desktop\\Tor Browser\\Browser:C:\\ProgramData\\Anaconda3\\Library\\bin;C:\\ProgramData\\Anaconda3\\Library\\bin;C:\\ProgramData\\Anaconda3;C:\\ProgramData\\Anaconda3\\Library\\mingw-w64\\bin;C:\\ProgramData\\Anaconda3\\Library\\usr\\bin;C:\\ProgramData\\Anaconda3\\Library\\bin;C:\\ProgramData\\Anaconda3\\Scripts;C:\\ProgramData\\Anaconda3\\Library\\bin;C:\\Games\\Python35\\Lib\\site-packages\\PyQt5;C:\\Program Files (x86)\\Intel\\iCLS Client\\;C:\\Program Files\\Intel\\iCLS Client\\;C:\\Windows\\system32;C:\\Windows;C:\\Windows\\System32\\Wbem;C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\;C:\\Program Files (x86)\\Intel\\Intel(R) Management Engine Components\\DAL;C:\\Program Files\\Intel\\Intel(R) Management Engine Components\\DAL;C:\\Program Files (x86)\\Intel\\Intel(R) Management Engine Components\\IPT;C:\\Program Files\\Intel\\Intel(R) Management Engine Components\\IPT;C:\\ProgramData\\Anaconda3;C:\\ProgramData\\Anaconda3\\Scripts;C:\\ProgramData\\Anaconda3\\Library\\bin;C:\\Program Files (x86)\\Skype\\Phone\\;C:\\Program Files (x86)\\QuickTime Alternative\\QTSystem;C:\\Program Files\\Git\\cmd;C:\\Users\\ddwell\\AppData\\Local\\Microsoft\\WindowsApps;'


# In[48]:

from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver("C:\\Users\\ddwell\\Desktop\\Tor Browser\\" ) as driver: #os.path.join(os.path.abspath('browser'), 'firefox.exe')
    driver.get('https://check.torproject.org')
    
    browser = webdriver.Firefox(capabilities=firefox_capabilities)

