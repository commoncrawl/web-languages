import glob
import logging
import markdown
import os
import re

from bs4 import BeautifulSoup


LOGGING_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
LOG_LEVEL = 'INFO'
logging.basicConfig(level=LOG_LEVEL, format=LOGGING_FORMAT)


def get_markdown_clean(path):
    """Read markdown from file and convert it into a form that the Python Markdown parser is able to parse"""
    md = open(path, encoding='utf-8').read()
    # strip trailing instructions and supportive information
    md = re.sub(r'^(?:## Instructions|Informative links \(in English\)|Additional Information|Scripts|Thank you to these people who have helped create this document):.*', '', md, flags=re.DOTALL|re.MULTILINE)
    # fix lists
    md = re.sub(r'^- ', '\n* ', md)
    # convert bare URLs into links
    md = re.sub(r' (https?://\S+)(?=\s|$)', r' <\1>', md)
    return md


web_languages_folders = [
    'living',
    'constructed',
    'extinct',
    'historical'
]

web_languages_files = []

for folder in web_languages_folders:
    for path in glob.iglob(os.path.join(folder, '*.md')):
        if path.endswith('README.md'):
            # skip READMEs
            continue
        web_languages_files.append(path)

logging.info('Extracting links from %d markdown files', len(web_languages_files))


total_links = 0

for path in web_languages_files:
    md = get_markdown_clean(path)
    html = markdown.markdown(md, stripTopLevelTags=False)
    soup = None
    try:
        soup = BeautifulSoup(html, 'lxml')
    except Exception as e:
        logging.error('Error in converted HTML from <%s>: %s', path, e)
        continue
    links = [link['href'] for link in soup.find_all('a', href=True)]
    print('### {} links from {}'.format(len(links), path))
    total_links += len(links)
    for link in links:
        print(link)


logging.info('Extracted %d links from %d markdown files', total_links, len(web_languages_files))
