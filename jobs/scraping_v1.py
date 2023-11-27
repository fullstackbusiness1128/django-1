import csv
import glob
import os

from bs4 import BeautifulSoup
from django.conf import settings


def parseHTML(htmlTxt, results):
    row = []
    soup = BeautifulSoup(htmlTxt, "html.parser")
    job_title = soup.select('.KLsYvd')[0].text.strip() if soup.select('.KLsYvd') else ""
    company_name = soup.select('.nJlQNd')[0].text if soup.select('.nJlQNd') else ""
    regions = soup.select('.sMzDkb')[1].text if soup.select('.sMzDkb') else ""
    locations = regions
    apply_url = soup.select('.pMhGee')[0].attrs['href'] if soup.select('.pMhGee') else ""
    about_role = soup.select('.HBvzbc')[0] if soup.select('.HBvzbc') else ""

    row.append(job_title)
    row.append(company_name)
    row.append(locations)
    row.append(apply_url)
    row.append(about_role)

    results.append(row)

    return results


def parse_html_to_csv(files):
    myFiles = files
    headers = ["job_title", "company_name", "locations", "apply_url", "about_role"]
    results = [headers]

    print("File parsed:")
    for file in myFiles:
        print(file)
        htmlTxt = file.read().decode("utf-8")
        results = parseHTML(htmlTxt, results)

    if not os.path.exists(settings.CSV_OUTPUT_FILE):
        os.makedirs(settings.CSV_OUTPUT_FILE)

    with open('{}/extractedData.csv'.format(settings.CSV_OUTPUT_FILE), 'w', newline="",
              encoding='utf-8') as out:
        writer = csv.writer(out)
        for r in results:
            try:
                writer.writerow(r)
            except:
                "Pass Here"
