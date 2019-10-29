#!/usr/bin/env python3
import cloudscraper
import time, os, sys, json
from tinydb import TinyDB, Query

class Manga:
	def __init__(self, title, author, total_chapters, chapters_read, manga_id):
		self.title = title
		self.author = author
		self.total_chapters = total_chapters
		self.chapters_read = chapters_read
		self.manga_id = manga_id

def createDatabase():
	# Create database
	if not os.path.exists('db.json'):
		open('db.json', 'a').close()

def addManga(manga_id):
	db = TinyDB('db.json')
	scraper = cloudscraper.create_scraper()
	try:
		manga_scrap = scraper.get("https://mangadex.org/api/manga/{}/".format(manga_id))
		manga = json.loads(manga_scrap.text)
	except (json.decoder.JSONDecodeError, ValueError) as err:
		print("CloudFlare error: {}".format(err))
		exit(1)

	# Fetch manga info
	newManga = Manga(manga['manga']['title'], manga['manga']['author'], 0, 0, manga_id)
	
	# Test if the manga already exist in the database
	f = open('db.json', 'r')

	if db.search(Query().manga_id==manga_id) !='[]' and f.read() != '{"_default": {}}':
		print('{} already exist in the the database'.format(newManga.title))
	else:
	# Add manga to the database
		db.insert({
				'title': newManga.title,
				'author': newManga.author,
				'total_chapters': newManga.total_chapters,
				'chapters-read': newManga.chapters_read,
				'manga_id': newManga.manga_id
				})
	

def dlmanga(manga_id):
	# Download chapters from a manga
	
	lang="gb"

	# Create the scraper
	scraper = cloudscraper.create_scraper()
	try:
		manga_scrap = scraper.get("https://mangadex.org/api/manga/{}/".format(manga_id))
		manga = json.loads(manga_scrap.text)
	except (json.decoder.JSONDecodeError, ValueError) as err:
		print("CloudFlare error: {}".format(err))
		exit(1)
	
	title = manga['manga']['title']
	print(title)

	# Chapters to download
	requested_chapters = []
	chap_list = input("Enter chapter(s) to download: ").strip()
	chap_list = [s for s in chap_list.split(',')]
	for s in chap_list:
		if "-" in s:
			r = [int(float(n)) for n in s.split('-')]
			s = list(range(r[0], r[1]+1))
		else:
			s = [float(s)]
		requested_chapters.extend(s)


	# Get list of chapters to download
	chapters=[]
	chap_selected=[]
	for chapter_id in manga['chapter']:
		if manga["chapter"][chapter_id]["chapter"]=="":
			chapter_num = 0
		else:
			chapter_num = float(manga["chapter"][chapter_id]["chapter"])
		if chapter_num in chap_selected:
			pass
		else:
			if chapter_num in requested_chapters and manga['chapter'][chapter_id]['lang_code'] == lang:
				chapters.append([chapter_id, chapter_num])
				chap_selected.append(chapter_num)
	chapters.sort()
	
	# Get image list of each chapter
	print()
	for chapter_id in chapters:
		dest_folder = os.path.join(os.getcwd(), "download", title, "{}".format(chapter_id[1]))
		if os.path.exists(dest_folder):
			print('Chapter n°{} is already downloaded'.format(chapter_id[1]))
			pass
		else:
			print("Downloading chapter {}...".format(chapter_id[1]))
			r = scraper.get("https://mangadex.org/api/chapter/{}/".format(chapter_id[0]))
			chapter = json.loads(r.text)

			# Get URLs
			images=[]
			server = chapter['server']
			hash = chapter['hash']
			for page in chapter['page_array']:
				images.append("{}{}/{}".format(server, hash, page))

			# Check if chapter is already downloaded and download images
			i=0
			for url in images:
				i+=1
				filename = os.path.basename(url)
				dest_folder = os.path.join(os.getcwd(), "download", title, "{}".format(chapter_id[1]))
				if not os.path.exists(dest_folder):
					os.makedirs(dest_folder)
				outtfile = os.path.join(dest_folder, filename)

				r = scraper.get(url)
				with open(outtfile, 'wb') as f:
					f.write(r.content)
				print("Download image {}".format(i))

				# Rename
				old_name='{}\{}'.format(dest_folder, filename)
				new_name='{}\{}.png'.format(dest_folder, i)

				os.rename(old_name, new_name)

				time.sleep(1)
	print('\nDone')

if __name__=='__main__':
	createDatabase()
	addManga(16617)
	dlmanga(16617)