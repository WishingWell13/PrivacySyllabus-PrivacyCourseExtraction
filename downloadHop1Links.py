import logging
from ssl import SSLCertVerificationError
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import urllib.request
from urllib.error import HTTPError, URLError
import socket
import os
import shutil
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import TimeoutError
import pandas as pd

# List of universities to process
universityList = ['College Unbound', 'Salisbury University', 'Universal Technical Institute-Dallas Fort Worth', 'Texas Wesleyan University']

storageLocation = 'errorLoggingOneHop/'

# Load the mapping of universities to their main course listing URLs from a JSON file
with open('universityLinkMapping.json', 'r') as fp:
    universityLinkMapping = json.load(fp)

# try:
# 	# universityList = pd.read_csv('all-university-classification-dataset.csv')['name'].to_list()
#     universityList = pd.read_csv('UniversitiesWithNoPrivacyCourses.csv')['name'].to_list()
#     universityList.append(pd.read_csv('UniversityWithPrivacyCourses.csv')['name'].to_list())
#     universityList.append(pd.read_csv('ErrorUniversities.csv')['name'].to_list()[:3])
#     print(universityList)
# except:
# 	print("No all university list found.")
# 	pass

def worker(university, file):
    """
    Worker function to process each university.
    Reads the main course listing page and extracts all links.
    Downloads the content of each link and saves it as an HTML file.
    """
    print("Starting University - " + university)
    os.mkdir("./courseListings/" + university)
    # Open and parse the main course listing page
    html_page = open("./courseListings/" + file, "r")
    soup = BeautifulSoup(html_page, "lxml")
    
    
    # Iterate through all anchor tags (links) on the page
    for i, link in enumerate(soup.findAll('a')):
        subLink = link.get('href')
        if subLink is not None:
            # Adjust the link if it is not a complete URL
            if "www" in subLink:
                subLink = "https://" + subLink[subLink.find("www") : ]
            elif "http" not in subLink:
                if(university not in universityLinkMapping):
                    # print("Key not found in universityLinkMapping for :", university)
                    continue
                parseResult = urlparse(universityLinkMapping[university])
                baseUrl = parseResult.scheme + "://" + parseResult.netloc
                # Combine base URL with the relative link
                if(len(baseUrl) > 0 and len(subLink) > 0 and (baseUrl[::-1] == '/' or subLink[0] == '/')):
                    subLink = baseUrl + subLink
                else:
                    subLink = baseUrl + "/" + subLink

            try:
                # Open the sublink and read its content
                response = urllib.request.urlopen(subLink)
                webContent = response.read().decode('UTF-8')
                # Write the content to a new HTML file
                f = open("./courseListings/" + university + "/" + str(i) + '.html', 'w')
                f.write(webContent)
                f.close()
                # print("Successfully read and wrote content from link - ", subLink)
            except HTTPError as error:
                dfGeneralErrorsList.append({"name":university, "link": "Unknown Exception", "error": error.strerror})
                # if('HTTP Error 404' in str(error)):
                #     df404.loc[len(df404.index)] = [university, subLink]
                # elif('HTTP Error 403' in str(error)):
                #     df403.loc[len(df403.index)] = [university, subLink]
                # elif('HTTP Error 429'  in str(error)):
                #     dfTooManyRequests.loc[len(dfTooManyRequests.index)] = [university, subLink]
                # else:
                #     logging.error('Data not retrieved because %s | URL: %s', error, subLink)
            except URLError as error:
                dfGeneralErrorsList.append({"name": university, "link": subLink, "error": str(error)})
                if isinstance(error.reason, socket.timeout):
                    logging.error('socket timed out - URL %s', subLink) 
                    logging.error('%s', error.strerror)
                # elif isinstance(error.reason, SSLCertVerificationError):
                #     dfBadCertificate.loc[len(dfBadCertificate.index)] = [university, subLink]
                else:
                    logging.error('some other error happened: %s | %s', error.reason, subLink)
            except Exception as error:
                dfGeneralErrorsList.append({"name": university, "link": subLink, "error": str(error)})
                print("Error while reading and writing content from link - ", subLink)
                continue
                

# Number of parallel threads
pool_size = 100  # your "parallelness"
pool = Pool(pool_size)

# Path to the directory containing the main HTML files for each university
path = './courseListings/'
fileList = os.listdir(path)

# df404 = pd.DataFrame(columns=['name', 'link'])
# df403 = pd.DataFrame(columns=['name', 'link'])
# dfTooManyRequests = pd.DataFrame(columns=['name', 'link'])
# seriesTimeout = pd.DataFrame(columns=['name', 'link'])
# dfBadCertificate = pd.DataFrame(columns=['name', 'link'])

dfGeneralErrorsList = []

import sys
import atexit
import signal

# START SAVE ON KILL SECTION
def exit_handler():
    # df404.to_csv(storageLocation + '404Universities.csv', index = False)
    # df403.to_csv(storageLocation + '403Universities.csv', index = False)
    # dfTooManyRequests.to_csv(storageLocation + 'tooManyRequestUniversities.csv', index = False)
    # dfBadCertificate.to_csv(storageLocation + 'badCertificateUniversities.csv', index = False)
    
    dfGeneralErrors = pd.DataFrame(dfGeneralErrorsList)
    dfGeneralErrors.to_csv(storageLocation + 'generalErrorUniversities.csv', index = False)

def kill_handler(*args):
    sys.exit(0)

atexit.register(exit_handler)
signal.signal(signal.SIGINT, kill_handler)
signal.signal(signal.SIGTERM, kill_handler)
# END SAVE ON KILL SECTION    

processes = []
results = []
# Iterate through each file in the directory
for file in fileList:
    if(".html" not in file):
        print(file + " is not an HTML file.")
        continue
    university = file.split(".html")[0]
    if(university in universityList):
        continue
    if(os.path.isdir(path + "/" + university)):
        shutil.rmtree("./courseListings/" + university)
    # Add the process to the pool
    processes.append((university, pool.apply_async(worker, (university, file, ))))
    

ct = 0
allTimeoutFail = []
# Retrieve and print results for each university process
for university, process in processes:
    try:
        results.append(process.get(timeout = 60))
    except TimeoutError as e:
        print("TimeoutError : ", university)
        results.append(e)
        allTimeoutFail.append(university)
        dfGeneralErrorsList.append({"name":university, "link": "Unknown Exception", "error": str(e)})
    except Exception as e:
        print("Exception %s: %s", university, e)
        dfGeneralErrorsList.append({"name":university, "link": "Unknown Exception", "error": str(e)})
        
    ct += 1
    print(str(ct) + " **************** University - " + university + "***********************")
    
    # Save progress every 25 iterations
    if(ct % 25 == 0):
        print("Saving progress.")
        # df404.to_csv(storageLocation + '404Universities.csv', index = False)
        # df403.to_csv(storageLocation + '403Universities.csv', index = False)
        # dfTooManyRequests.to_csv(storageLocation + 'tooManyRequestUniversities.csv', index = False)
        # dfBadCertificate.to_csv(storageLocation + 'badCertificateUniversities.csv', index = False)
        
        dfGeneralErrors = pd.DataFrame(dfGeneralErrorsList)
        dfGeneralErrors.to_csv(storageLocation + 'generalErrorUniversities.csv', index = False)

print(results)

print(str(ct) + " universities processed.")

dfAll = pd.read_csv('all-university-classification-dataset.csv')
dfTimeout = dfAll[dfAll['name'].isin(allTimeoutFail)]
dfTimeout.to_csv(storageLocation + 'TimeoutUniversities.csv', index = False)

# df404.to_csv(storageLocation + '404Universities.csv', index = False)
# df403.to_csv(storageLocation + '403Universities.csv', index = False)
# dfTooManyRequests.to_csv(storageLocation + 'tooManyRequestUniversities.csv', index = False)
# dfBadCertificate.to_csv(storageLocation + 'badCertificateUniversities.csv', index = False)

dfGeneralErrors = pd.DataFrame(dfGeneralErrorsList)
dfGeneralErrors.to_csv(storageLocation + 'generalErrorUniversities.csv', index = False)

# Close and join the pool
pool.close()
pool.join()

print("All processes closed and joined.")