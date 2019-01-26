from bs4 import BeautifulSoup
import urllib.request
import os
import re
from pdf2image import convert_from_path

"""
Here is a script that scrapes the Mutopia Project at mutopiaproject.org for sheet music. The jpg files will be saved
to a directory located at the path provided by the user at the bottom.
"""


class SheetMusicScraper:

    def __init__(self):
        self.jpgs = []
        self.names = []
        self.composers = []

    def scrape(self, path):
        """
        Scrape mutopiaproject.org for all of its sheet music in pdf format and save it to the path provided
        :param path: the path at which to save the pdf files
        """
        if not os.path.exists(path):
            print("Path does not exist")
            print("Creating directory...")
            os.mkdir(path)
            print("Complete.")
        else:
            print("Path exists! Saving data there.")

        print("Scraping data...")
        for i in range(0, 2111, 10):
            if i % 100 == 0:
                print("Sheet Music Page:", i)
            url = "http://www.mutopiaproject.org/cgibin/make-table.cgi?startat=" + str(i) + "&searchingfor=" \
                "&Composer=&Instrument=&Style=&collection=&id=&solo=&recent=&timelength=1&timeunit=week&lilyversion=" \
                "&preview="
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup(page, 'html.parser')
            box = soup.findAll('table', attrs={"class": "table-bordered result-table"})
            box = str(box)
            count = 0
            while True:
                try:
                    ex = re.search(r'(<td><a href).*Letter \.pdf', box)
                    pdf_link = ex.group(0)[13:-13]
                    self.jpgs.append(pdf_link)
                    ex = re.search(r'<tr><td>(.*)</td>', box)
                    name = ex.group(1)
                    self.names.append(name)
                    try:
                        ex = re.search(r'<td>by (.*) \(', box)
                        composer = ex.group(1)
                    except:
                        print("Anonymous composer!")
                        composer = "Anonymous"
                    self.composers.append(composer)
                    box = box[box.index("Letter .pdf file")+24:]
                    if count == 0:
                        print("Name:", name)
                        print("Composer:", composer, "\n")
                    count += 1
                except:
                    break

        # Now that we have the list of links that download the pdfs, we must request them and save them
        num = 0
        if (len(self.jpgs) == len(self.names)) and (len(self.jpgs) == len(self.composers)):
            print("Length check: Passed :)")
            num = len(self.jpgs)
        else:
            print("Length check: Failed :(")
            print("JPGs Length:", len(self.jpgs))
            print("Names Length:", len(self.names))
            print("Composers Length:", len(self.composers))
            exit(0)
        print("Saving files to given directory...")
        for i in range(num):
            res = urllib.request.urlopen(self.jpgs[i])
            # Make a directory for each composer, because why not.
            if not os.path.exists(path + self.composers[i]):
                os.mkdir(path + self.composers[i])
            # check if a '/' is in the filename. Replace it with some arbitrary character to avoid confusion
            if '/' in self.names[i]:
                self.names[i] = self.names[i].replace('/', ':')
            file = open(path + self.composers[i] + '/' + self.names[i] + '.pdf', 'wb')  # must save as pdf first
            file.write(res.read())
            file.close()
            # Now convert saved pdf to jpg
            pages = convert_from_path(path + self.composers[i] + '/' + self.names[i] + '.pdf', 500)
            page_count = 1
            for page in pages:
                page.save(path + self.composers[i] + '/' + self.names[i] + 'Page' + str(page_count) + '.jpg', 'JPEG')
                page_count += 1
        print("Saving complete.")
        print("Script execution complete!")


if __name__ == "__main__":
    sheet_scraper = SheetMusicScraper()
    path = input("Enter the path at which you'd like the dataset to be saved:\n")
    if not path.endswith('/'):
        path += '/'
    sheet_scraper.scrape(path)
