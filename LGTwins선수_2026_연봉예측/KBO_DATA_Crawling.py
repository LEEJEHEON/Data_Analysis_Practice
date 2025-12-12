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

def get_all_player_data(year,Position,Page):
    driver = setup_driver()
    base_url = "https://www.koreabaseball.com/Record/Player/"+Position+"/"
    base_url = base_url + Page + ".aspx"
    print ("base_url :", base_url)
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
        
        for team in TEAM_LIST:
            all_data = []
            current_num = 1
            # 팀 선택: 
            league_select = Select(driver.find_element(By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam"))
            league_select.select_by_visible_text(team)
            time.sleep(2)
            # 페이지 선택(초기화) : 
            next_btn_id = f"cphContents_cphContents_cphContents_ucPager_btnNo{current_num}"
            next_btn = driver.find_element(By.ID, next_btn_id)
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)

            crawling_flag = True
            while crawling_flag:  
                # 현재 페이지 테이블 데이터 추출
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.select_one('div.record_result table')
                if table:
                    rows = table.find('tbody').find_all('tr')
                    for row in rows:
                        cols = [col.get_text(strip=True) for col in row.find_all(['th', 'td'])]
                        all_data.append(cols)
                # 3. 다음 페이지 버튼 클릭
                try:
                    next_btn_id = f"cphContents_cphContents_cphContents_ucPager_btnNo{current_num+1}"
                    next_btn = driver.find_element(By.ID, next_btn_id)
                    if next_btn:
                        driver.execute_script("arguments[0].click();", next_btn)
                        time.sleep(2)
                        current_num += 1
                    else :
                        crawling_flag=False
                except:
                    break
                
            # DataFrame 생성 (컬럼명은 페이지 thead 기준)
            if Position =='HitterBasic' :
                if Page == 'Basic1':
                    columns = ['순위', '선수명', '팀명', 'AVG', 'G', 'PA', 'AB', 'R', 'H', 
                                '2B', '3B', 'HR', 'TB', 'RBI', 'SAC', 'SF', 'BB', 'HBP', 'SO', 'GDP', 'TB%']
                elif Page == 'Basic2':
                    columns = ['순위', '선수명', '팀명', 'AVG', 'BB', 'IBB', 'HBP', 'SO', 'GDP', 'SLG', 'OBP', 'OPS', 'MH', 'RISP', 'PH-BA']
                elif Page == 'Detail1':
                    columns = ['순위', '선수명', '팀명', 'AVG', 'XBH', 'GO', 'AO', 'GO/AO', 'GW RBI', 'BB/K', 'P/PA', 'ISOP', 'XR', 'GPA']
            elif Position =='PitcherBasic' :
                if Page == 'Basic1':
                    columns = ['순위', '선수명', '팀명', 'ERA', 'G', 'W', 'L', 'SV', 'HLD', 'WPCT', 'IP', 'H', 'HR', 'BB', 'HBP','SO','R','ER','WHIP']
                elif Page == 'Basic2':
                    columns = ['순위', '선수명', '팀명', 'ERA', 'CG', 'SHO', 'QS', 'BSV', 'TBF', 'NP', 'AVG', '2B', '3B', 'SAC', 'SF','IBB','WP','BK']
                elif Page == 'Detail1':
                    columns = ['순위', '선수명', '팀명', 'ERA', 'GS', 'Wgs', 'Wgr', 'GF', 'SVO', 'TS', 'GDP', 'GO', 'AO', 'GO/AO']
            elif Position =='Defense' :
                columns = ['순위', '선수명', '팀명', 'POS', 'G', 'GS', 'IP', 'E', 'PKO', 'PO', 'A', 'DP', 'FPCT', 'PB', 'SB','SB','CS','CS%']
            elif Position =='Runner' :
                columns = ['순위', '선수명', '팀명', 'G', 'SBA', 'SB', 'CS', 'SB%', 'OOB', 'PKO']


            df = pd.DataFrame(all_data, columns=columns[:len(all_data[0])] if all_data else columns)
            # CSV 저장
            output_file = "./Data/"+team+"/kbo_"+year+"_"+Position+"_"+team+"_"+Page+".csv"

            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            #print(f"완료! {team}팀 {len(df)}명의 선수 데이터가 {output_file}에 저장되었습니다.[web:3][web:5]")
    finally:
        driver.quit()
    
print("KBO 타자 기록 크롤링 시작...")

# 타자 첫번째 기록
get_all_player_data("2025","HitterBasic","Basic1")
print( "Hitter Basic1 완료 ")

# 타자 두번째 기록
get_all_player_data("2025","HitterBasic","Basic2")
print( " Hitter Basic2 완료 ")

# 타자 상세 기록
get_all_player_data("2025","HitterBasic","Detail1")
print( "Hitter Detail1 완료 ")

print("KBO 타자 기록 크롤링 종료")

# 투수
print("KBO 투수 기록 크롤링 시작...")

# 투수 첫번째 기록
get_all_player_data("2025","PitcherBasic","Basic1")
print( " Pitcher Basic1 완료 ")

# 투수 두번째 기록
get_all_player_data("2025","PitcherBasic","Basic2")
print( " Pitcher Basic2 완료 ")


# 투수 상세 기록
get_all_player_data("2025","PitcherBasic","Detail1")
print( " Pitcher Detail1 완료 ")


print("KBO 투수 기록 크롤링 종료")

# 수비 기록
get_all_player_data("2025","Defense","Basic")
print( "Defense 완료 ")

# 주루 기록
get_all_player_data("2025","Runner","Basic")
print( "Runner 완료 ")

print("모든 팀 크롤링 완료")
