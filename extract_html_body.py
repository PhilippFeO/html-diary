# Extract the <body> of the submitted diary entry (html file)
# argv[1]   diary entry as html file; body is extracted from this file
# argv[2]   index of (line) "which" past is parsed, s. past_dates.txt
# argv[3]   formatted date for heading according to argv[2]

# TODO: Add "vor 6 Monaten" <29-04-2023>


from sys import argv
from bs4 import BeautifulSoup

with open(argv[1]) as fp:
    soup = BeautifulSoup(fp, 'html.parser')

# "which" past is submitted as second argument
# craft heading according to chosen past
period = int(argv[2])
match period:
    case 0:
        heading = f"...vier Wochen, {argv[3]}"
    case 1:
        heading = f"...einem Jahr, {argv[3]}"

# Format past adapted headings
h2 = f"<h2>{heading}</h2>"
# Extract description in pre-tag
pre = soup.find('pre')
pre = f"<pre>{str(pre.contents[0]).strip()}</pre>"
# Extract images/fotos
imgs = soup.find_all('img')
imgs = (f"{str(img)}\n<br/>" for img in imgs)
# Extract videos
videos = soup.find_all('video')
videos = (f"{str(video)}\n<br/>" for video in videos)

# Join all html elements
html_body = "".join((h2, pre, *imgs, *videos))
print(html_body)

# In case generated html should be saved formatted
# soup = BeautifulSoup(html_body, 'html.parser')
# print(soup.prettify())
