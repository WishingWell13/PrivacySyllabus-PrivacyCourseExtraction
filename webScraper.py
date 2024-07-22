from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import json
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from requests.exceptions import ConnectionError
from selenium import webdriver
import chromedriver_autoinstaller

import sys
import atexit
import signal

print('Begin')

# Used to store files
def jsonStuff(connectionResetCount, noElementCount):
    with open('universityLinkMapping.json', 'w') as fp:
        json.dump(universityLinkMapping, fp)
    
    with open('counts.txt', 'w') as fp2:
        fp2.write("No of universities network error - " + str(connectionResetCount) + "\n")
        fp2.write("No of universities no elemnet error - " + str(noElementCount) + "\n")


# Path to chromedriver (NOT USED?)
path = "/Users/aishwaryamanjunath/Downloads/chromedriver-mac-x64/chromedriver.exe"

# Automatically install chromedriver
try:
    chromedriver_autoinstaller.install()
except:
    print('autoinstall failed, skipping')
    pass

# List of universities to search for
universityList = ["Arizona State University Campus Immersion","Boston University","Brandeis University","California Institute of Technology","Carnegie Mellon University","Clemson University","Colorado State University-Fort Collins","Columbia University in the City of New York","Cornell University","Dartmouth College","Drexel University"]

# Load existing university link mappings from JSON file (if it exists)

universityLinkMapping = {}
try:
    f = open('universityLinkMapping.json')
    universityLinkMapping = json.load(f)
    f.close()
except FileNotFoundError:
    print("No existing university link mappings found.")
    pass

try:
    universityList = pd.read_excel('unique_universities.xlsx')['name'].to_list()
    # universityList = pd.read_csv('all-university-classification-dataset.csv')['name'].to_list()
    # universityList = pd.read_csv('ErrorUniversities.csv')['name'].to_list()
except FileNotFoundError as e:
    print("No all university list found.")
    pass
except Exception as e:
    print("Error while reading university list.")
    print(e)
    pass


universityWebPageNotFound = []

ct = 0
inOrd = 0
noElementCount = 0
connectionResetCount = 0

# START SAVE ON KILL SECTION
def exit_handler():
    jsonStuff(connectionResetCount, noElementCount)

def kill_handler(*args):
    sys.exit(0)

atexit.register(exit_handler)
signal.signal(signal.SIGINT, kill_handler)
signal.signal(signal.SIGTERM, kill_handler)
# END SAVE ON KILL SECTION

# Iterate through the list of universities
for university in universityList:
    inOrd += 1
    # Skip universities that are already in the mapping
    if(university in universityLinkMapping):
        continue

    ct += 1
    # Save progress every 50 iterations
    if(ct % 50 == 0):
        with open('universityLinkMapping.json', 'w') as fp:
            json.dump(universityLinkMapping, fp)

    # Initialize the WebDriver for Chrome
    driver = webdriver.Chrome()

    # Open Google search page
    driver.get("https://www.google.com/")
    driver.implicitly_wait(10) # Wait implicitly for elements to be ready

    # Locate the search box, enter the search query, and submit
    # Wait for the results to load
    searchBox = driver.find_element("name", "q") # This should return a textarea element, can use the inspect tool to verify
    driver.implicitly_wait(10)  
    searchBox.send_keys(university + " undergraduate computer science courses 2022-2023")
    driver.implicitly_wait(10)
    searchBox.send_keys(Keys.ENTER)
    driver.implicitly_wait(10)

    try:
        # Try to find the first search result link
        elem1= driver.find_element("xpath", "//div[@class='yuRUbf']//a")
        driver.implicitly_wait(10)

        # elem1.click()
        # driver.implicitly_wait(10)
        link = elem1.get_attribute('href')
        print(f"Link {inOrd} / {len(universityList)}")
        print(link)
        universityLinkMapping[university] = link

        # Navigate to the found link and save the page source
        driver.get(link)
        pageSource = driver.page_source
        fileToWrite = open("./courseListings/" + university + ".html", "w")
        fileToWrite.write(pageSource)
        fileToWrite.close()

    except NoSuchElementException:
        try:
            # If the first attempt fails, retry the search
            print("In Exception - ")
            driver.get("https://www.google.com/")
            driver.implicitly_wait(5)

            searchBox = driver.find_element("name", "q")
            driver.implicitly_wait(5)

            searchBox.send_keys(university + " undergraduate computer science courses 2022-2023")
            driver.implicitly_wait(5)

            searchBox.send_keys(Keys.ENTER)
            driver.implicitly_wait(5)

            # Attempt to find an alternate search result link
            elem1= driver.find_element("xpath", '//*[@id="rso"]/div[1]/div/block-component/div/div[1]/div/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div[1]/a')
            driver.implicitly_wait(5)

            # elem1.click()
            # driver.implicitly_wait(10)
            link = elem1.get_attribute('href')
            print(link)
            universityLinkMapping[university] = link

            # Navigate to the found link and save the page source
            driver.get(link)
            pageSource = driver.page_source
            fileToWrite = open("./courseListings/" + university + ".html", "w")
            fileToWrite.write(pageSource)
            fileToWrite.close()
            # fileToRead = open(university + ".html", "r")
            # print(fileToRead.read())
            # fileToRead.close()
        except NoSuchElementException:
            universityWebPageNotFound.append(university)
            noElementCount += 1
        except ConnectionResetError:
            print("Connection reset on second attempt error for university - ", university)
            universityWebPageNotFound.append(university)
            connectionResetCount += 1
        except Exception:
            universityWebPageNotFound.append(university)
    except ConnectionResetError:
        print("Connection reset error on first attempt for university - ", university)
        universityWebPageNotFound.append(university)
        connectionResetCount += 1
    except Exception:
        universityWebPageNotFound.append(university)


    finally:
        # Quit the driver after each iteration to avoid resource leakage
        driver.quit()


jsonStuff(connectionResetCount, noElementCount)


if(len(universityWebPageNotFound) > 0):
    df = pd.DataFrame(universityWebPageNotFound, columns=["university name"])
    df.to_csv('universityWebPageNotFound.csv', index=False)
    print("Universities with web page not found saved to universityWebPageNotFound.csv")
    
print('End')


