import requests, argparse, re, urllib, logging, os, sys
from bs4 import BeautifulSoup


# http://dl3.uploadfdl.com/files/Serial/SpongeBob/S01/1080p x265 10bit/

'''
	django url validation regex:
	print(re.match(regex, "http://www.example.com") is not None)   # True
	print(re.match(regex, "example.com") is not None)              # False
'''
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


'''
	Setting up the command line parsers here
'''

parser = argparse.ArgumentParser(description='Enter URL of page to download videos from the page')
parser.add_argument('url', help='url of the webpage')
parser.add_argument('ext', help='extension of the file in that webpage')


'''
	logging config
'''
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def get_abs_url(start, append):
	if start.endswith('/'):
		start = start[:-1]
	if append.startswith('/'):
		append = append[:-1]
	return f'{start}/{append}'

def save_file(file_url, fname):
	r = requests.get(file_url, stream=True)

	file = open(fname, 'wb')
	logging.info(f'Downloading file: {fname}')
	for chunk in r.iter_content(chunk_size=1024):
		# writing one chunk at a time to file 
		if chunk: 
			file.write(chunk)



def main():
	args = parser.parse_args()
	# print(args.url)
	if re.match(regex, args.url) is None:
		raise Exception('Invalid URL')
	web_page = requests.get(args.url)
	if web_page.status_code is not 200:
		raise Exception(f'The GET request to URL failed with a status_code of {web_page.status_code}')
	
	res_soup = BeautifulSoup(web_page.text, 'html.parser') 
	file_links = list()
	for link in res_soup.find_all('a'):
		href = link.get('href')
		if href.endswith(args.ext):
			file_name = urllib.parse.unquote(href)
			if os.path.isfile(file_name):
				logging.info(f'File already downloaded, skipping file: {file_name}')
				continue 
			save_file(get_abs_url(args.url, href), file_name)
			file_links.append(get_abs_url(args.url, href))

if __name__ == '__main__':
	main()