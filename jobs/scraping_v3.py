import json
import os
import csv

from bs4 import BeautifulSoup
from django.conf import settings


def parseHTML(htmlTxt, results):
    soup = BeautifulSoup(htmlTxt, "html.parser")
    job_title = soup.find(
        'h1',
        {
            'class': 'top-card-layout__title'
        }
    ).text
    apply_url = soup.find(
        'link', {
            'rel': 'canonical'
        }
    ).get('href')

    script = soup.find('script', {'type': 'application/ld+json'})
    if script:
        script_dict = json.loads(script.text)
        try:
            company_name = script_dict['hiringOrganization']['name']
        except:
            company_name = ''
        try:
            locations = script_dict['jobLocation']['address']['addressLocality']
        except:
            locations = ''
    else:
        company_name = ''
        locations = ''
    about_role = soup.find(
        'div',
        class_='show-more-less-html__markup'
    )

    results.append(
        [
            job_title,
            company_name,
            locations,
            apply_url,
            about_role
        ]
    )

    return results


def parse_html_to_csv(files):
    myFiles = files
    headers = ["job_title", "company_name", "locations", "apply_url", "about_role"]
    results = [headers]
    for file in myFiles:
        print(file)
        htmlTxt = file.read().decode("utf-8")
        results = parseHTML(htmlTxt, results)

    if not os.path.exists(settings.CSV_OUTPUT_FILE):
        os.makedirs(settings.CSV_OUTPUT_FILE)

    with open('{}/linkedincrawlData.csv'.format(settings.CSV_OUTPUT_FILE), 'w', newline="",
              encoding='utf-8') as out:
        writer = csv.writer(out)
        for r in results:
            try:
                writer.writerow(r)
            except:
                "Pass Here"
