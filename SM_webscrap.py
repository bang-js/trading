from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os, shutil

###################################################
# KRX에서 전종목시세 (KOSDAQ) 자동 검색 및 다운로드
# 다운받은 파일을 download에서 해당 폴더로 옮기고 이름 변경
###################################################

# Chrome 브라우저 옵션 설정
chrome_options = webdriver.ChromeOptions()

###############
# 현재 Python 파일이 위치한 디렉터리 저장
current_directory = os.path.dirname(os.path.abspath(__file__))
# 오늘 날짜 설정
today_date = datetime.now().strftime('%Y%m%d_%H%M')
# 새로운 폴더의 전체 경로 생성
folder_path_gen = os.path.join(current_directory, f'webscrap_result_{today_date}')
# 새로운 폴더 생성 (이름: webscrap_result_오늘날짜_현재시각)
os.makedirs(folder_path_gen)
###############

# 다운로드 받을 파일 위치를 지정
prefs = {'download.default_directory': folder_path_gen}
chrome_options.add_experimental_option('prefs', prefs)

# Chrome 드라이버 생성
browser = webdriver.Chrome(chrome_options=chrome_options)
# browser = webdriver.Chrome("chromedriver.exe")

# url 열기 
browser.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201010101")
time.sleep(0.5)

dates = ['20100104', '20110103', '20120102', '20130102', '20140102', '20150102', '20160104', \
    '20170102', '20180102', '20190102', '20200102', '20210104', '20220103']

for date in dates :
    # 주식-종목시세-전종목시세 
    browser.find_element_by_xpath('//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]/div/div[1]/ul/li[2]/a').click()
    time.sleep(0.5)
    browser.find_element_by_xpath('//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]/div/div[1]/ul/li[2]/ul/li[1]/a').click()
    time.sleep(0.5)
    browser.find_element_by_xpath('//*[@id="jsMdiMenu"]/div[4]/ul/li[1]/ul/li[2]/div/div[1]/ul/li[2]/ul/li[1]/ul/li[1]/a').click()
    time.sleep(0.5)

    # KOSDAQ 선택
    time.sleep(5)
    browser.find_element_by_xpath('//*[@id="MDCSTAT015_FORM"]/div[1]/div/table/tbody/tr[1]/td/label[3]').click()
    time.sleep(0.5)

    # 기간 설정
    elem = browser.find_element_by_xpath('/html/body/div[2]/section[2]/section/section/div/div[2]/form/div[1]/div/table/tbody/tr[2]/td/div/div/input')  
    elem.click()
    elem.send_keys(Keys.CONTROL, 'a')
    elem.send_keys(date) 	

    # 조회 클릭
    browser.find_element_by_xpath('/html/body/div[2]/section[2]/section/section/div/div[2]/form/div[1]/div/table/tbody/tr[2]/td/a').click() 
    time.sleep(5)

    # 추출 클릭
    browser.find_element_by_xpath('//*[@id="MDCSTAT015_FORM"]/div[2]/div[1]/p[2]/button[2]').click()
    # CSV 클릭
    browser.find_element_by_xpath('//*[@id="ui-id-1"]/div/div[2]/a').click()
    time.sleep(10) # 다운로드대기

    ## 파일 이름 수정
    # 방금 전 다운받은 최신 파일 선택
    latest_modified_file = max([folder_path_gen + '\\' + f for f in os.listdir(folder_path_gen)], key=os.path.getctime) # 최신 파일 선택
    # 파일 이름 변경
    new_name = f'data_{date}.csv'
    new_file_path = os.path.join(folder_path_gen, new_name)
    os.rename(os.path.join(folder_path_gen, latest_modified_file), new_file_path)
    print(f"rename the file: {new_name}")

    #새로고침
    browser.refresh()

