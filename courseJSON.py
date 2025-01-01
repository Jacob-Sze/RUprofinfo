import requests
import json

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

subject_codes = "010,011,016,013,014,035,020,047,050,067,070,074,078,080,081,082,090,098,115,117,119,133,122,125,126,136,140,146,155,158,160,165,175,180,190,185,192,189,193,195,198,202,203,206,207,219,216,220,300,364,332,355,351,354,353,358,359,356,370,382,015,373,573,374,375,381,522,360,377,387,211,390,400,420,440,447,450,460,470,490,489,501,505,510,508,512,506,533,535,540,547,557,554,555,556,558,560,565,563,567,574,575,550,617,580,590,595,607,615,620,624,628,630,632,635,640,650,652,667,670,680,685,690,691,692,694,700,701,705,709,711,713,723,715,721,718,720,725,730,745,750,762,776,775,787,790,810,830,843,832,833,851,840,860,902,888,861,904,910,920,940,955,960,959,799,956,965,966,973,974,967,971,975,988,991"  # Replace with the string of subject codes
semester = "12025"
campus = "NB"
level = "UG"

subArray = fetch_and_process_courses(subject_codes, semester, campus, level)

with open("RUprof.txt", "w") as fp:
    json.dump(subArray, fp, indent=4)
