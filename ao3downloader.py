import re
import sys
import json
import requests

session = requests.Session() #stores cookies so that we can login

username = sys.argv[1] #your username
password = ""
if len(sys.argv) > 2:
  password = sys.argv[2] #your password
currentPage = 1 #the page of bookmarks to start with

raw_series = input("Would you like to output the URLs of series? type y for yes\n")
series = (raw_series == 'y')

raw_metadata_q = input("Would you like metadata in addition to URLs? type y for yes\n")
metadata_q = (raw_metadata_q == 'y')

# a little function to make it easier to print metadata later
def print_with_metadata(url, metadata):
  print('title: ' + metadata['title'])
  print('url: '+ url)
  print('')


#login stuff
if (password != ''):
  # get an "authenticity token"
  authenticity_token = {}
  url_token = 'http://archiveofourown.org/token_dispenser.json'
  jsonThing = session.get(url_token)
  authenticity_token = jsonThing.json()['token']

  #log in
  url = 'https://archiveofourown.org/user_sessions/'
  data = {
    'user_session[login]': username,
    'user_session[password]': password,
    'authenticity_token': authenticity_token #if you don't pass this along nothing works
  }
  headers = {
    "Accept":"text/html,*/*",
    "Host":"archiveofourown.org",
    "Connection":"keep-alive",
    "User-Agent":"ozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Content-Type":"application/x-www-form-urlencoded"
  }
  print("Logging in")
  the_page = session.post(url=url,data=data,headers=headers)

  if ('users/'+username) not in the_page.url:
    print("Login error!")
  else:
    print("Logged in!")

#actually grab all the bookmarks!
print('fetching urls')
number_urls = 0

# finds things that look like
# <a href="/works/#"> where # is a number
p_works  = """<a href=\"/works/(\d+)\">([^<>]+)</a>\n\s*?by"""
p_series = """<a href=\"/series/(\d+)\">([^<>]+)</a>\n\s*?by"""

end = False
while not end:
  # gets the current page from your bookmarks
  res = session.get('http://archiveofourown.org/users/'+username+'/bookmarks?page='+str(currentPage))
  html = res.text
  matches = re.findall(p_works, html)


  #if there are no matches we've reached the end
  if len(matches) < 1:
      end = True
  for match in matches:
    if metadata_q:
      print_with_metadata('http://archiveofourown.org/works/' + match[0], {'title': match[1]})
    else:
      print('http://archiveofourown.org/works/' + match[0])
    number_urls += 1
  if(series):
    matches_s = re.findall(p_series, html)
    for match_s in matches_s:
      if metadata_q:
        print_with_metadata('http://archiveofourown.org/series/' + match_s[0], {'title': match_s[1]})
      else:
        print('http://archiveofourown.org/series/' + match_s[0])
      number_urls += 1

  currentPage += 1

print("Finished! with "+str(number_urls)+" urls")
