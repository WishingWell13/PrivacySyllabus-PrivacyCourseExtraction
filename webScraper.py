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

# Path to chromedriver
path = "/Users/aishwaryamanjunath/Downloads/chromedriver-mac-x64/chromedriver.exe"

# Automatically install chromedriver
chromedriver_autoinstaller.install()

# List of universities to search for
universityList = ["Arizona State University Campus Immersion","Boston University","Brandeis University","California Institute of Technology","Carnegie Mellon University","Clemson University","Colorado State University-Fort Collins","Columbia University in the City of New York","Cornell University","Dartmouth College","Drexel University"]

# Load existing university link mappings from JSON file (if it exists)
f = open('universityLinkMapping.json')

universityWebPageNotFound = []

universityLinkMapping = json.load(f)

ct = 0
# Iterate through the list of universities
for university in universityList:
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
	searchBox = driver.find_element("name", "q")
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
		except ConnectionResetError:
			universityWebPageNotFound.append(university)
		except Exception:
			universityWebPageNotFound.append(university)
	except ConnectionResetError:
		universityWebPageNotFound.append(university)
	except Exception:
		universityWebPageNotFound.append(university)


	finally:
		# Quit the driver after each iteration to avoid resource leakage
		driver.quit()


with open('universityLinkMapping.json', 'w') as fp:
	json.dump(universityLinkMapping, fp)


if(len(universityWebPageNotFound) > 0):
	df = pd.DataFrame(universityWebPageNotFound, columns=["university name"])
	df.to_csv('universityWebPageNotFound.csv', index=False)

