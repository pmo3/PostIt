import urllib2
from bs4 import BeautifulSoup

htmlFile = urllib2.urlopen("http://www.goodreads.com/quotes")
soup = BeautifulSoup(htmlFile)

def findQuote():
	quoteObj = soup.find_all('div', {'class':'stacked mediumText'})[0]
	quote = quoteObj.get_text()[1:-1].encode("utf-8")
	authorObj = quoteObj.next_sibling.next_sibling
	author = authorObj.find_all('a')[0].get_text().encode('utf-8')
	return [quote, author]

