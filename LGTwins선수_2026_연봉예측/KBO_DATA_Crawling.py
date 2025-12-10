import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    return webdriver.Chrome(options=options)

def get_all_player_data():
    driver = setup_driver()
    base_url = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"
    
    TEAM_LIST = ["LG","한화","SSG","삼성","NC","KT","롯데","KIA","두산","키움"]

    try:
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        
        # 연도 선택: 2025 (최신)
        year_select = Select(wait.until(EC.element_to_be_clickable((By.ID, "cphContents_cphContents_cphContents_ddlSeason_ddlSeason"))))
        year_select.select_by_visible_text("2025")
        time.sleep(2)
        
        # 리그 선택: KBO 정규시즌
        league_select = Select(driver.find_element(By.ID, "cphContents_cphContents_cphContents_ddlSeries_ddlSeries"))
        league_select.select_by_visible_text("KBO 정규시즌")
        time.sleep(2)
        
        # "기록보기" 버튼 클릭
        # record_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='기록보기']")))
        # record_btn.click()
        # time.sleep(3)
        
        for team in TEAM_LIST:
            all_data = []
            current_page= 1
            # 팀 선택: 
            league_select = Select(driver.find_element(By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
            league_select.select_by_visible_text(team)
            time.sleep(2)
            crawling_flag = True
            while crawling_flag: 
                # 현재 페이지 테이블 데이터 추출
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.select_one('div.record_result table')
                print("--data--")
                if table:
                    rows = table.find('tbody').find_all('tr')
                    for row in rows:
                        cols = [col.get_text(strip=True) for col in row.find_all(['th', 'td'])]
                        if len(cols) >= 12:  # 유효 데이터 행
                            all_data.append(cols)
                    
                # 3. 다음 페이지 버튼 찾기 (class="on"이 아닌 숫자 버튼)
                try:
                    # next_buttons = driver.find_elements(By.CSS_SELECTOR,"a[id*='btnNo']:not(.on)")
                    next_btn_id = f"cphContents_cphContents_cphContents_ucPager_btnNo{current_num+1}"
                    next_btn = driver.find_element(By.ID, next_btn_id)
                    if next_buttons:
                        next_btn = next_buttons[0]
                        driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(2)
                        print ("next btn : " , next_btn)
                    else :
                        crawling_flag=False
                except:
                    break
                # DataFrame 생성 (컬럼명은 페이지 thead 기준)
                columns = ['순위', '선수명', '팀명', 'AVG', 'G', 'PA', 'AB', 'R', 'H', 
                        '2B', '3B', 'HR', 'TB', 'RBI', 'SAC', 'SF', 'BB', 'HBP', 'SO', 'GDP', 'TB%']
                df = pd.DataFrame(all_data, columns=columns[:len(all_data[0])] if all_data else columns)

            # CSV 저장
            output_file = "./Data/kbo_2025_hitter_"+team+".csv"
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"완료! {team}팀 {len(df)}명의 선수 데이터가 {output_file}에 저장되었습니다.[web:3][web:5]")
    finally:
        driver.quit()
    
    # return all_data

# 실행
print("KBO 타자 기록 크롤링 시작...")
get_all_player_data()

print("모든 팀 크롤링 완료")

# # DataFrame 생성 (컬럼명은 페이지 thead 기준)
# columns = ['순위', '선수명', '팀명', 'AVG', 'G', 'PA', 'AB', 'R', 'H', 
#            '2B', '3B', 'HR', 'TB', 'RBI', 'SAC', 'SF', 'BB', 'HBP', 'SO', 'GDP', 'TB%']
# df = pd.DataFrame(raw_data, columns=columns[:len(raw_data[0])] if raw_data else columns)

# # CSV 저장
# output_file = './Data/kbo_2025_hitter_all.csv'
# df.to_csv(output_file, index=False, encoding='utf-8-sig')
# print(f"완료! {len(df)}명의 선수 데이터가 {output_file}에 저장되었습니다.[web:3][web:5]")
