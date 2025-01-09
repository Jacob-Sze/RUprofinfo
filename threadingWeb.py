import asyncio
import requests
import selenium
import re
import time
from selenium import webdriver
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from decimal import Decimal
import urllib.parse
import threading
from threading import Lock

mutex = Lock()
professorStorage = list()
class Professors:
  def __init__(self, name, difficulty, quality):
    self.name = name
    self.dup = 1
    self.difficulty = Decimal(difficulty)
    self.quality = Decimal(quality)
    self.reviews = {}

class Review:
  def __init__(self, quality, difficulty, text):
    self.quality = quality
    self.difficutly = difficulty
    self.text = text   

def fetch_and_process_courses(subject_codes, semester, campus, level):
    base_url = "https://sis.rutgers.edu/oldsoc/courses.json"
    subArray = []
    seen_entries = set()

    for subject in subject_codes.split(","):
        subject = subject.strip()
        params = {
            "subject": subject,
            "semester": semester,
            "campus": campus,
            "level": level
        }
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            courses = response.json()

            for course in courses:
                course_number = course.get("courseNumber", "Unknown")
                subject_code = course.get("subject", "Unknown")

                if subject_code == "198" and course_number == "494":
                    continue
                
                for section in course.get("sections", []):
                    for instructor in section.get("instructors", []):
                        instructor_name = instructor.get("name", "Unknown")
                        entry = {
                            "courseCode": f"{subject_code},{course_number}",
                            "professor": instructor_name
                        }
                        tple = (entry["courseCode"], entry["professor"])
                        if tple not in seen_entries:
                            subArray.append(entry)
                            seen_entries.add(tple)
        else:
            print(f"Subject {subject} Error {response.status_code}")

    return subArray

def fetch_professors(professor):
    chrome_options = Options()
    chrome_options.add_argument("--headless")    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)
    name = professor.split(",")
    fullName = name[0]
    if(len(name) == 2):
        fullName = (name[1] + " " + fullName)[1:]
    link = "https://www.ratemyprofessors.com/search/professors/825?q=" + urllib.parse.quote(fullName)
    driver.get(link)
    button = driver.find_element(By.CLASS_NAME, "eAIiLw")
    button.click()
    ads = driver.find_elements(By.CLASS_NAME, "bx-close")
    if(len(ads) > 0):
        try:
            ads[0].click()
        except:
            ads
    cards = driver.find_elements(By.CLASS_NAME, "dLJIlx")
    nameList = driver.find_elements(By.CLASS_NAME, "cJdVEK")
    links = set()
    for i in range(0, len(cards)):
        if(len(name) == 2 and nameList[i].get_attribute('innerHTML').lower() == fullName.lower()):
            links.add(cards[i].get_attribute('href'))
        elif(len(name) == 1 and nameList[i].get_attribute('innerHTML').split(' ')[1].lower() == fullName.lower()):
            links.add(cards[i].get_attribute('href'))
        else:
            break
    if(len(links) == 0):
        return
    if(len(name)==1 and len(links)>= 2):
        return
    links = list(links)
    for i in range(0, len(links)):
        driver.get(link)
        ads = driver.find_elements(By.CLASS_NAME, "bx-close")
        if(len(ads) > 0):
            try:
                ads[0].click()
            except:
                ads
        while(True):
            try:
                driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.CLASS_NAME, "glImpo"))))
                driver.execute_script("arguments[0].click();", WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CLASS_NAME, "glImpo"))))
            except (TimeoutException, StaleElementReferenceException) as e:
                break
        quality = driver.find_elements(By.CLASS_NAME, "eWZmyX")
        reviews = driver.find_elements(By.CLASS_NAME, "gRjWel")
        difficulty = driver.find_elements(By.CLASS_NAME, "cDKJcc")
        avgQuality = driver.find_elements(By.CLASS_NAME, "liyUjw")
        avgDiff = driver.find_elements(By.CLASS_NAME, "kkESWs")
        if(len(avgDiff) < 2):
            continue
        if(len(avgQuality) < 1):
            continue
        avgQuality = avgQuality[0].get_attribute('innerHTML')
        avgDiff = avgDiff[1].get_attribute('innerHTML')
        reviewStorage = set()
        for i in range(0, len(reviews)):
            reviewStorage.add(Review(re.search(">...<", quality[i].get_attribute('innerHTML'))[0][1:4], difficulty[i].get_attribute('innerHTML'), reviews[i].get_attribute('innerHTML')))
        checker = -1
        for i in range(0, len(professorStorage)):
            if(professor == professorStorage[i].name):
                checker = i
                break
        with mutex:
            if(checker != -1):
                professorStorage[i].reviews = professorStorage[i].reviews.union(reviewStorage)
                professorStorage[i].dup += 1
                professorStorage[i].difficulty += Decimal(avgDiff)
                professorStorage[i].quality += Decimal(avgQuality)
            else:
                professorStorage.append(Professors(professor, avgDiff, avgQuality))
    driver.quit()
    return

def main():
    subject_codes = "010,011,016,013,014,035,020,047,050,067,070,074,078,080,081,082,090,098,115,117,119,133,122,125,126,136,140,146,155,158,160,165,175,180,190,185,192,189,193,195,198,202,203,206,207,219,216,220,300,364,332,355,351,354,353,358,359,356,370,382,015,373,573,374,375,381,522,360,377,387,211,390,400,420,440,447,450,460,470,490,489,501,505,510,508,512,506,533,535,540,547,557,554,555,556,558,560,565,563,567,574,575,550,617,580,590,595,607,615,620,624,628,630,632,635,640,650,652,667,670,680,685,690,691,692,694,700,701,705,709,711,713,723,715,721,718,720,725,730,745,750,762,776,775,787,790,810,830,843,832,833,851,840,860,902,888,861,904,910,920,940,955,960,959,799,956,965,966,973,974,967,971,975,988,991"  # Replace with the string of subject codes
    semester = "12025"
    campus = "NB"
    level = "UG"
    subArray = fetch_and_process_courses(subject_codes, semester, campus, level)
    array = set()
    for object in subArray:
        array.add(object["professor"])
    threadArray = list()
    for i in range(0, len(array)):
        threadArray.append(threading.Thread(target=fetch_professors, args=(array[i], )))
        threadArray[i].start()
    for i in range(0, len(array)):
        threadArray[i].join()
    with open("RUprof.txt", "w") as fp:
        json.dump(subArray, fp, indent=4)

if __name__ == '__main__':
    main()

