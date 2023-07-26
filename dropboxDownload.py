import os
from urllib.request import urlretrieve
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

def getDownloadPath(absoluteUrl, downloadDirectory):
    path = downloadDirectory+'/'+os.path.basename(absoluteUrl) #getting path + filename
    #stripping last 5 chars
    if path.endswith('=0'):
        path = path[:len(path) - 5]
    print(path)
    return path

# getting pages with downloading links
def main(fileUrl, downloadDrectory):
    if fileUrl is not None:
        print('downloading...' + fileUrl)
        try:
            fileName = getDownloadPath(fileUrl, downloadDrectory)
            urlretrieve(fileUrl, fileName)
        except HTTPError as e:
            print('No page found: ', e.reason)
        except URLError as e:
            print('No page found: ', e.reason)

    print('Done!')
    return fileName

if __name__ == "__main__":
   main(fileUrl, directory)