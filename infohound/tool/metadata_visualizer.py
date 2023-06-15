import sqlite3
import json
import os

db_location = "data_info.db"

con = sqlite3.connect(db_location)
cur = con.cursor()
i = 0
for row in cur.execute("SELECT url, metadata FROM Files WHERE metadata IS NOT NULL"):
	info = json.loads(row[1])
	file_name = row[0].split("/")[-1]
	#if info["File:FileType"] == "HTML":
	#	print(row[0])
	
	if info["File:FileType"] == "PDF":
		print(file_name)
		if "PDF:Creator" in info:
			print(" - Creator: " + info["PDF:Creator"]) 
		if "PDF:Author" in info:
			print(" - Author: " + info["PDF:Author"])
		if "PDF:PDFVersion" in info:
			print(" - PDF Version: " + str(info["PDF:PDFVersion"])) 
		if "PDF:Producer" in info:
			print(" - Producer: " + info["PDF:Producer"])
		if "PDF:Company" in info and info["PDF:Company"] != '':
			print(" - Company: " + info["PDF:Company"])
		print("\n")
	if info["File:FileType"] in ["DOC","DOCX","XLS","XLSX"]:
		print(file_name)
		if "PDF:Producer" in info:
			print(" - Producer: " + info["PDF:Producer"])
		if "FlashPix:Author" in info:
			print(" - Author: " + info["FlashPix:Author"]) 
		if "FlashPix:Tag_AuthorEmailDisplayName" in info:
			print(" - Author Email Display Name: " + str(info["FlashPix:Tag_AuthorEmailDisplayName"])) 
		if "FlashPix:Tag_AuthorEmail" in info:
			print(" - Author Email: " + info["FlashPix:Tag_AuthorEmail"]) 
		if "FlashPix:Hyperlinks" in info:
			print(" - Hyperlinks: " + str(info["FlashPix:Hyperlinks"])) 
		if "FlashPix:Company" in info:
			print(" - Company: " + str(info["FlashPix:Company"])) 
		if "FlashPix:LastModifiedBy" in info:
			print(" - Las modified by: " + str(info["FlashPix:LastModifiedBy"]))
		print("\n")
	
con.close()