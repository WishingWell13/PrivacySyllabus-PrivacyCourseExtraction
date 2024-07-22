import logging
import random
from ssl import SSLCertVerificationError
from time import sleep
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
from datetime import datetime
import time

now = datetime.now()
startTime = now.strftime("%Y-%m-%d-%I")
load_time_results = [] 
# List of universities to process
universityList = ['College Unbound', 'Salisbury University', 'Universal Technical Institute-Dallas Fort Worth', 'Texas Wesleyan University']

storageLocation = 'errorLoggingOneHop/localRun/'

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
    try:
        html_page = open("./courseListings/" + file, "r")
        soup = BeautifulSoup(html_page, "lxml")
    except Exception as e:
        print("Error while reading main course listing page for university - ", university)
        print(e)
    
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
                # Start timing to measure load time of each sublink (by Girma)
                start_time = time.time()
                # Open the sublink and read its content
                response = urllib.request.urlopen(subLink)
                webContent = response.read().decode('UTF-8')
                
                # End timing (by Girma)
                end_time = time.time()
                # Calculate load time
                load_time = end_time - start_time
                
                # Write the content to a new HTML file
                f = open("./courseListings/" + university + "/" + str(i) + '.html', 'w')
                f.write(webContent)
                f.close()
                print(f"Sublink for {university} loaded in {load_time:.2f} seconds")
                # logging.info(f"Sublink for {university} loaded in {load_time:.2f} seconds")
                # print("Successfully read and wrote content from link - ", subLink)
                # Append result to the list
                load_time_results.append({
                    "name": university,
                    "link": subLink,
                    "time": load_time
                })
            except HTTPError as error:
                dfGeneralErrorsList.append({"name": university, "link": subLink, "error": str(error)})
                continue
                # if('HTTP Error 404' in str(error)):
                #     df404.loc[len(df404.index)] = [university, subLink]
                # elif('HTTP Error 403' in str(error)):
                #     df403.loc[len(df403.index)] = [university, subLink]
                # elif('HTTP Error 429'  in str(error)):
                #     dfTooManyRequests.loc[len(dfTooManyRequests.index)] = [university, subLink]
                # else:
                #     logging.error('Data not retrieved because %s | URL: %s', error, subLink)
            except URLError as error:
                dfGeneralErrorsList.append({"name": university, "link": subLink, "error": error.reason})
                if isinstance(error.reason, socket.timeout):
                    logging.error(f'socket timed out - URL {subLink} | {error}') 
                    continue
                elif isinstance(error.reason, SSLCertVerificationError):
                    # dfBadCertificate.loc[len(dfBadCertificate.index)] = [university, subLink]
                    logging.error(f'SSL Certificate Error - URL {subLink}, {error.reason.strerror}')
                else:
                    logging.error(f'some other url error happened: {str(subLink)} | {str(error)} ' )
                    continue
            except Exception as error:
                dfGeneralErrorsList.append({"name": university, "link": subLink, "error": str(error)})
                print("Error while reading and writing content from link", subLink, error)
                continue

# Number of parallel threads
pool_size = 100  # your "parallelness"
pool = Pool(pool_size)

# Path to the directory containing the main HTML files for each university
path = './courseListings/'
fileList = os.listdir(path)
print("Number of universities to process: ", len(fileList))
print("First 5 universities: ", fileList[:5])

dfGeneralErrorsList = []
ct = 0


import sys
import atexit
import signal

# START SAVE ON KILL SECTION
# def exit_handler():
#     print("Exit Handler")
#     if(ct>5):
#         dfGeneralErrors = pd.DataFrame(pd.Series(dfGeneralErrorsList).tolist())
#         os.makedirs(storageLocation, exist_ok=True)
        
#         # Create a DataFrame from the results
#         df_load_times = pd.DataFrame(load_time_results)
#         # Ensure the directory exists
#         os.makedirs(os.path.dirname(storageLocation), exist_ok=True)
#         # Save the DataFrame to a CSV file
#         csv_filename = os.path.join(storageLocation, 'sublinkLoadTime.csv')
#         df_load_times.to_csv(csv_filename, index=False)

#         dfGeneralErrors.to_csv(storageLocation + f'generalErrorUniversities-{startTime}.csv', index = False)

# def kill_handler(*args):
#     print("Kill Handler")
#     sys.exit(0)

# atexit.register(exit_handler)
# signal.signal(signal.SIGINT, kill_handler)
# signal.signal(signal.SIGTERM, kill_handler)
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
    # sleep(random.random() + 0.1) # ADDED BY ANDY
    

allTimeoutFail = []
# Retrieve and print results for each university process
for university, process in processes:
    try:
        results.append(process.get(timeout = 300))
    except TimeoutError as e:
        print("TimeoutError : ", university)
        results.append(e)
        allTimeoutFail.append(university)
        dfGeneralErrorsList.append({"name":university, "link": "Unknown Exception", "error": str(e)})
    except Exception as e:
        print("Exception %s: %s", university, e)
        dfGeneralErrorsList.append({"name":university, "link": "Unknown Exception", "error": str(e)})
        
    ct += 1
    print(str(ct) + " / " + str(len(processes)) + " **************** University - " + university + "***********************")
    
    # Save progress every 25 iterations
    if(ct % 25 == 0):
                
        # Create a DataFrame from the results
        df_load_times = pd.DataFrame(load_time_results)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(storageLocation), exist_ok=True)
        # Save the DataFrame to a CSV file
        csv_filename = os.path.join(storageLocation, 'sublinkLoadTime.csv')
        df_load_times.to_csv(csv_filename, index=False)

        print("Saving progress.")
        
        dfGeneralErrors = pd.DataFrame(pd.Series(dfGeneralErrorsList).tolist())
        dfGeneralErrors.to_csv(storageLocation + f'generalErrorUniversities-{startTime}.csv', index = False)


print(str(ct) + " universities processed.")

dfAll = pd.read_csv('all-university-classification-dataset.csv')

# Close and join the pool
pool.close()

print("All processes closed")

pool.join()

print("All processes closed and joined.")

# Create a DataFrame from the results
df_load_times = pd.DataFrame(load_time_results)
# Ensure the directory exists
os.makedirs(os.path.dirname(storageLocation), exist_ok=True)
# Save the DataFrame to a CSV file
csv_filename = os.path.join(storageLocation, 'sublinkLoadTime.csv')
df_load_times.to_csv(csv_filename, index=False)

print(f"Load times have been saved to {csv_filename}")

dfGeneralErrors = pd.DataFrame(pd.Series(dfGeneralErrorsList).tolist())
dfGeneralErrors.to_csv(storageLocation + f'generalErrorUniversities-{startTime}.csv', index = False)

print("Final export successful")



def saveItems(generalErrorList = [], timeoutList = []):
    if generalErrorList != []:
        dfGeneralErrors = pd.DataFrame(pd.Series(generalErrorList).tolist())
        dfGeneralErrors.to_csv(storageLocation + f'generalErrorUniversities-{startTime}.csv', index = False)
    pass