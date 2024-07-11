from bs4 import BeautifulSoup
import json
import os
import pandas as pd
import re
# Path to the directory containing HTML files of course listings
path = './courseListings/'

pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

# List all files in the specified directory
fileList = os.listdir(path)
uniName = []
content = []
contentType = []
titlePage = []

privacypolicyTitleUniName = []
privacypolicyTitleContent = []
privacypolicyTitleContentType = []
privacypolicyTitlePage = []
universitiesWithNoPrivacyRelatedContent = []
universitieClassificationWithNoPrivacyRelatedContent = []
count= 0

# Iterate through each file in the directory
for file in fileList:
	# Initialize lists to store university-level data
	universityLevelUniName = []
	universityLevelContent = []
	universityLevelContentType = []
	universityLevelTitlePage = []

	# Process only HTML files
	if(".html" not in file):
		continue

	# Extract university name from the file name
	university = file.split(".")[0]

	print("------------------------ " + university + " ------------------------")

	# Open and parse the HTML file
	html_page = open("./courseListings/" + file, "r")
	soup = BeautifulSoup(html_page, "html.parser")
	title = soup.find('title')

	ct = 0
	# Remove unwanted sections from the HTML content
	[x.extract() for x in soup.findAll('footer')]
	[x.extract() for x in soup.findAll('header')]
	[x.extract() for x in soup.findAll('nav')]
	[x.extract() for x in soup.findAll('style')]
	for x in soup.select("[class*=foot]"):
		x.extract()
	for x in soup.select("[class*=Foot]"):
		x.extract()
	for x in soup.select("[class*=nav]"):
		x.extract()
	for x in soup.select("[class*=gdpr]"):
		x.extract()
	for x in soup.select("[class*=GDPR]"):
		x.extract()
	for x in soup.select("[class*=Gdpr]"):
		x.extract()


	# Check if the page title contains privacy-related keywords
	if(title is not None and title.string is not None):
		if('privacy statement' in title.string.lower() or 'gdpr' in title.string.lower() or 'privacy notice' in title.string.lower()):
			for tag in soup.find_all(lambda tag: 'privacy' in tag.get_text(strip=True, separator=' ') or 'Privacy' in tag.get_text(strip=True, separator=' ')):
				if(tag.name == "script" or tag.string is None):
					continue
				privacypolicyTitleUniName.append(university)
				privacypolicyTitleContent.append(tag.string)
				privacypolicyTitleContentType.append("Main Link")
				privacypolicyTitlePage.append(title.string)
			continue

	# Extract privacy-related content from the main HTML file
	for tag in soup.find_all(lambda tag: 'privacy' in tag.get_text(strip=True, separator=' ') or 'Privacy' in tag.get_text(strip=True, separator=' ')):
		if(tag.name == "script" or tag.string is None):
			continue
		if("FERPA" in tag.string or "Family Educational Rights and Privacy act" in tag.string 
				or "Privacy Statement" in tag.string or "Terms of Use" in tag.string 
				or "Family Education Rights and Privacy Acts Policy" in tag.string 
				or "Family Education Rights and Privacy Act" in tag.string
				or "The Family Educational Rights & Privacy Act" in tag.string):
				continue
		# print("++++++++++ Tag Data ++++++++++++")
		if(tag.string in universityLevelContent or re.match(pattern, tag.string)):
			continue
		else:
			print(tag.string, title)
			if(ct == 0):
				universityLevelUniName.append(university)
				ct += 1
			else:
				universityLevelUniName.append(' ')
			universityLevelContent.append(tag.string)
			universityLevelContentType.append('Main Page')
			if(title is not None):
				universityLevelTitlePage.append(title.string)
			else:
				universityLevelTitlePage.append(' ')

	# Continue if the directory for sub-links does not exist
	if(not(os.path.exists(path + university + "/"))):
		continue

	# Process sub-link pages within the university's directory
	for subLink in os.listdir(path + university + "/"):

		subHtml_page = open("./courseListings/" + university + "/" + subLink, "r")

		soup = BeautifulSoup(subHtml_page, "html.parser")
		subLinkTitle = soup.find('title')

		# Remove unwanted sections from the sub-link HTML content
		[x.extract() for x in soup.findAll('footer')]
		[x.extract() for x in soup.findAll('header')]
		[x.extract() for x in soup.findAll('nav')]
		[x.extract() for x in soup.findAll('style')]
		for x in soup.select("[class*=foot]"):
			x.extract()
		for x in soup.select("[class*=nav]"):
			x.extract()
		for x in soup.select("[class*=gdpr]"):
			x.extract()
		for x in soup.select("[class*=GDPR]"):
			x.extract()
		for x in soup.select("[class*=Gdpr]"):
			x.extract()

		# Check if the sub-link page title contains privacy-related keywords
		if(subLinkTitle is not None and subLinkTitle.string is not None):
			if('privacy statement' in subLinkTitle.string.lower() or 'gdpr' in subLinkTitle.string.lower() or 'privacy notice' in subLinkTitle.string.lower()):
				for tag in soup.find_all(lambda tag: 'privacy' in tag.get_text(strip=True, separator=' ') or 'Privacy' in tag.get_text(strip=True, separator=' ')):
					if(tag.name == "script" or tag.string is None):
						continue
					privacypolicyTitleUniName.append(university)
					privacypolicyTitleContent.append(tag.string)
					privacypolicyTitleContentType.append("Sub Link")
					privacypolicyTitlePage.append(subLinkTitle.string)
				continue

		# Extract privacy-related content from sub-link HTML files
		for tag in soup.find_all(lambda tag: 'privacy' in tag.get_text(strip=True, separator=' ') or 'Privacy' in tag.get_text(strip=True, separator=' ')):
			if(tag.name == "script" or tag.string is None):
				continue
			if("FERPA" in tag.string or "Family Educational Rights and Privacy act" in tag.string 
				or "Privacy Statement" in tag.string or "Terms of Use" in tag.string 
				or "Family Education Rights and Privacy Acts Policy" in tag.string 
				or "Family Education Rights and Privacy Act" in tag.string
				or "The Family Educational Rights & Privacy Act" in tag.string):
				continue
			# print("++++++++++ Tag Data ++++++++++++")
			if(tag.string in universityLevelContent or re.match(pattern, tag.string)):
				continue
			else:
				print(tag.string, subLink, tag.name, subLinkTitle)
				if(ct == 0):
					universityLevelUniName.append(university)
					ct += 1
				else:
					universityLevelUniName.append(' ')
			universityLevelContent.append(tag.string)
			universityLevelContentType.append('Sub link Page')
			if(subLinkTitle is not None):
				universityLevelTitlePage.append(subLinkTitle.string)
			else:
				universityLevelTitlePage.append(' ')

	# If no privacy-related content was found, add the university to the list
	if(len(universityLevelContent) == 0):
		universitiesWithNoPrivacyRelatedContent.append(university)
		# universitieClassificationWithNoPrivacyRelatedContent.append(universityClassificationMapping[university])



	uniName += universityLevelUniName
	content += universityLevelContent
	contentType += universityLevelContentType
	titlePage += universityLevelTitlePage

# Create a DataFrame and save the extracted privacy-related content to a CSV file
df = pd.DataFrame({"University Name ": uniName, "Page ": contentType, 'title': titlePage, "Privacy related content ": content})
df.to_csv("./privacyContent.csv", index = False)

# Create a DataFrame and save the extracted privacy-related content from title pages to a CSV file
df = pd.DataFrame({"University Name ": privacypolicyTitleUniName, "Page ": privacypolicyTitleContentType, 'title': privacypolicyTitlePage, "Privacy related content ": privacypolicyTitleContent})
df.to_csv("./privacyRelatedTitleContent.csv", index = False)

# Create a DataFrame and save the list of universities with no privacy-related content to a CSV file
df = pd.DataFrame({"University Name ": universitiesWithNoPrivacyRelatedContent})
df.to_csv("./universitiesWithNoPrivacyRelatedContent.csv", index = False)


