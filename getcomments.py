from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import re
import csv
import calendar
import time


def login(uname,passw):
	browser = webdriver.Chrome("chromedriver") 
	url = "http://m.facebook.com/"
	browser.get(url) #navigate to the page
	username = browser.find_element_by_id("m_login_email") #username form field
	password = browser.find_element_by_xpath("//input[@name='pass']") #password form field

	username.send_keys(uname)
	password.send_keys(passw)

	submitButton = browser.find_element_by_id("u_0_5")
	submitButton.click() 

	#notNowButton = browser.find_element_by_link_text("Not Now")
	#notNowButton.click()

	wait_time = 50 # a very long wait time
	element = WebDriverWait(browser, wait_time).\
		until(EC.element_to_be_clickable((By.LINK_TEXT, 'Not Now')))
	element.click()
	return browser,True

def get_mobile_link(link):
	newLink=""
	if "m.facebook.com" in link:
		return link
	elif "www.facebook.com" in link:
		newLink = link.replace("www.facebook.com","m.facebook.com")
		return newLink
	else:
		newLink = link.replace("facebook.com","m.facebook.com")
		return newLink

def get_comments(browser,link):
#browser.get("https://m.facebook.com/home.php?_rdr")
	#convert link to 
	link = get_mobile_link(link)
	browser.get(link) #navigate to page behind login
	
	clickcounter=0
	while True:
		if clickcounter > 100:
			break
		try:
			viewMore = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View more comments')]]")))
			viewMore.click()
			clickcounter += 1
		except Exception as e:
			try:
				viewMore = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View more comments')]]")))
				viewMore.click()
				clickcounter += 1
			except Exception as e2:
				print(e2)
				break

	while True:
		try:
			viewMore = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View previous comments')]]")))
			viewMore.click()
		except Exception as e:
			try:
				viewMore = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View previous comments')]]")))
				viewMore.click()
			except Exception as e2:
				print(e2)
				break
	#view replies
	while True:
		try:
			viewReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., ' replied')]]")))
			viewReplies.click()
		except Exception as e3:
			try:
				viewReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., ' replied')]]")))
				viewReplies.click()
			except Exception as e4:
				print(e4)
				break

	#view more replies
	while True:
		try:
			viewNextReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View next replies')]]")))
			viewNextReplies.click()
		except Exception as e5:
			try:
				viewNextReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View next replies')]]")))
				viewNextReplies.click()
			except Exception as e6:
				print(e6)
				break


	#view more replies
	while True:
		try:
			viewPrevReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View previous replies')]]")))
			viewPrevReplies.click()
		except Exception as e7:
			try:
				viewPrevReplies = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.XPATH, "//a[text()[contains(., 'View previous replies')]]")))
				viewPrevReplies.click()
			except Exception as e8:
				print(e8)
				break



	innerHTML = browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string
	soup = BeautifulSoup(innerHTML,'html.parser')
	#comments = soup.find_all('div',{"data-sigil":"comment-body"})
	#for comm in comments:
	#	print(comm.text)


	firstLevelComments = soup.find_all('div',{"data-sigil":"comment"})
	count=1
	commentlist = []
	
	#get date of post
	postDate = soup.find('div',{"data-sigil":"m-feed-voice-subtitle"})
	postDate = postDate.find('abbr').text
	#post id
	postID = re.findall(r"(?<=story_fbid\=)\d+", link)[0]
	postFilename = "./downloads/"+postID+"-post.csv"
	postAuthor = soup.h3.strong.text
	#get timestamp
	curr_time = calendar.timegm(time.gmtime())
	postDateTS = ''
	postDate = str(postDate)
	if "mins" in postDate:
		minsPassed = re.match(r'\d+',postDate).group()
		secondsPassed = 60 * int(minsPassed)
		postDateTS = curr_time - secondsPassed
		postDate = time.strftime("%B %d at %I:%M %p", time.gmtime(postDateTS))
	elif "hrs" in postDate:
		hrsPassed = re.match(r'\d+', postDate).group()
		secondsPassed = 60 * 60 * int(hrsPassed)
		postDateTS = curr_time - secondsPassed
		postDate = time.strftime("%B %d at %I:%M %p", time.gmtime(postDateTS))
	elif "Yesterday" in postDate:
		postDateTS = curr_time - (60*60*24)
		yesterdayTime = postDate.replace("Yesterday", "")
		postDate = time.strftime("%B %d", time.gmtime(postDateTS))
		postDate += yesterdayTime
	


	#get text of post
		#get div that contains the text
	postText = soup.find('div',{"class":"story_body_container"})
	postText = postText.find('div',{"class": "_5rgt _5nk5"})
	
	postTextPs = postText.findAll('p')
	postText = ''
	for element in postTextPs:
		postText += '\n' + ''.join(element.findAll(text = True))
	
	postText = postText.replace("\n"," ")
	postText = postText.replace("\t"," ")
	with open(postFilename, 'w', encoding='utf-8',) as the_file:
		the_file.write('id,date,author,text\n')
		the_file.write(postID)
		the_file.write(',')
		the_file.write(postDate)
		the_file.write(',')
		the_file.write(postAuthor)
		the_file.write(',')
		the_file.write(postText)
		the_file.write('\n')
	the_file.close()
	postObj = {"id" : postID, "date" : postDate, "author" : postAuthor, "text" : postText}
	for fl in firstLevelComments:
	#	print(count)
		ogComment = {}
		countStr = str(count)
		ogComment["id"] = postID +'-'+ countStr
		ogCommentIndex = count
		ogComment["replied_by_author"] = False 
		ogComment["parent_comment_id"] = 0 #zero means that it is a top level comment
		
		message = fl.find("div",{"data-sigil":"comment-body"})
		ogComment["text"] = message.text
	#	print(message.text)
		#get author
		author = message.previous_sibling
		try:
			ogComment["author"] = author.text
		except:
			ogComment["author"] = message.text
			ogComment["text"] = "***Replied sticker/image***"

		##find the replies of comment
		replies = fl.find_all('div',{"data-sigil":"comment inline-reply"})
		ogComment["no_of_replies"] = len(replies)
		
		if len(replies) == 0:
			commentlist.append(ogComment)
			count += 1
		## handle the case of a comment thread
		else:
			ogComment["no_of_replies"] = len(replies)
			#process the comment thread
			for reply in replies:
				count += 1
				replyComment = {}
				countStr = str(count)
				replyComment["id"] = postID +'-'+ countStr
				replyComment["replied_by_author"] = False 
				replyComment["parent_comment_id"] = ogComment["id"]
				replyMessage = reply.find("div",{"data-sigil":"comment-body"})
				replyComment["text"] = replyMessage.text
				replyAuthor = replyMessage.previous_sibling
				try:
					replyComment["author"] = replyAuthor.text
				except:
					replyComment["author"] = replyMessage.text
					replyComment["text"] ="***Replied sticker/image***"
				#check if author replied
				if (replyComment["author"] == postAuthor):
					ogComment["replied_by_author"] = True
				replyComment["no_of_replies"] = 0
				commentlist.append(replyComment)
			commentlist.insert( (ogCommentIndex - 1), ogComment)
			count += 1

	#for comm in commentlist:
	#	print(comm)

	#post1 = csv.writer(open("output.csv","w",encoding="utf-8"))

	#for commentObj in commentlist:
	#	for key,val in commentObj.items():
	#		post1.writerow([key,val])
	keys = commentlist[0].keys()
	commentsFilename = "./downloads/"+ postID + "-comments.csv"
	with open(commentsFilename, 'w', encoding="utf-8", newline="") as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(commentlist)
		
	return postObj, commentlist