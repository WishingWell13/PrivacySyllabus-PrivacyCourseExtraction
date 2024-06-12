from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import urllib.request
import os
import shutil
from multiprocessing.pool import ThreadPool as Pool
from multiprocessing import TimeoutError

# List of universities to process
universityList = ['College Unbound', 'Salisbury University', 'Universal Technical Institute-Dallas Fort Worth', 'Texas Wesleyan University']

# Load the mapping of universities to their main course listing URLs from a JSON file
with open('universityLinkMapping.json', 'r') as fp:
	universityLinkMapping = json.load(fp)


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
		    		print("Key not found in universityLinkMapping for :", university)
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
		    	f.close
		    except Exception:
		    	continue
		    	# print("Error while reading and writing content from link - ", subLink)

# Number of parallel threads
pool_size = 100  # your "parallelness"
pool = Pool(pool_size)

# Path to the directory containing the main HTML files for each university
path = './courseListings/'
fileList = os.listdir(path)

processes = []
results = []
# Iterate through each file in the directory
for file in fileList:
	if(".html" not in file):
		continue
	university = file.split(".html")[0]
	if(university in universityList):
		continue
	if(os.path.isdir(path + "/" + university)):
		shutil.rmtree("./courseListings/" + university)
	# Add the process to the pool
	processes.append((university, pool.apply_async(worker, (university, file, ))))

ct = 0
# Retrieve and print results for each university process
for university, process in processes:
	try:
		results.append(process.get(timeout = 60))
	except TimeoutError as e:
		print("TimeoutError : ", university)
		results.append(e)
	ct += 1
	print(str(ct) + " **************** University - " + university + "***********************")

print(results)
# Close and join the pool
pool.close()
pool.join()
	