import csv
import glob
import os
import re

from bs4 import BeautifulSoup
from django.conf import settings


def liParseHelper(tags):
    result = "<ul>"
    for tag in tags:
        if ("</li>" in tag):
            tag = tag.replace("</li>", "")
            result += ("<li>" + tag + "</li>")
        elif (tag):
            result += ("<li>" + tag + "</li>")
    result += "</ul>"
    return result


def addJobContacts(soup, row):
    job_contacts = []
    if (soup.select('.company-contact-name')):
        job_contact = []
        name = soup.select('.company-contact-name')[0].text
        mail = soup.find_all(href=re.compile('mailto:'))[0].text
        job_contacts.append(name)
        job_contacts.append(mail)
        job_contacts.append('')

    if (soup.select('.recruiters-hm-info')):
        recruiters = soup.select('.recruiters-hm-info')
        for recruiter in recruiters:
            name = str(recruiter.select('.comp-links-flex > div > p')[0]).split('<p')[1][1:] if recruiter.select(
                '.comp-links-flex > div p') else ""
            title = recruiter.select('.comp-links-flex > div p')[1].text if recruiter.select(
                '.comp-links-flex > div p') else ""
            mail = recruiter.find_all(href=re.compile('mailto:'))[0].text if recruiter.find_all(
                href=re.compile('mailto:')) else ""
            job_contacts.append(name)
            job_contacts.append(mail)
            job_contacts.append(title)

    for contact in job_contacts:
        row.append(contact)
    return row


def parseHTML(htmlTxt, results):
    row = []
    soup = BeautifulSoup(htmlTxt, "html.parser")
    company_name = soup.select('.redeemed-company-name')[0].text if soup.select('.redeemed-company-name') else ""
    job_title = soup.select('.listing-title')[0].text if soup.select('.listing-title') else ""
    regions = soup.select('.listing-regions')[0].text if soup.select('.listing-regions') else ""
    cities = soup.select('.listing-cities')[0].text if soup.select('.listing-cities') else ""
    if cities in regions:
        locations = regions
    else:
        locations = regions + " " + cities
    # about_role = soup.select('.listing-specs-grid-container > p')[0].text if soup.select('.listing-specs-grid-container > p') else ""
    about_role = ""
    if soup.select('.listing-specs-grid-container > p'):
        about_role_str = str(soup.select('.listing-specs-grid-container > p')[0])
        about_role = about_role_str.split('<div')[0] + '</p>'

    functions = ""
    if (soup.select('#functions-text > li')):
        functionTags = str(soup.select('#functions-text > li')[0]).split('<li>')
        functions = liParseHelper(functionTags)
        # functions = str(soup.select('#functions-text')[0])

    skills = ""
    if (soup.find_all(text=re.compile('Skills:'))):
        skillSpan = soup.find_all(text=re.compile('Skills:'))
        skillsTags = str(skillSpan[0].parent.parent.parent.select('li')[0]).split("<li>")
        skills = liParseHelper(skillsTags)
        # skills = str(skillSpan[0].parent.parent.parent)

    known_requirements = ""
    if (soup.select('#listing-known-requirements li')):
        known_requirementTags = str(soup.select('#listing-known-requirements li')[0]).split("<li>")
        known_requirements = liParseHelper(known_requirementTags)
        # known_requirements = str(soup.select('#listing-known-requirements')[0])

    travel = soup.select('#travel-percent > span')[0].text if soup.select('#travel-percent > span') else ""
    about_company = soup.select('#listing-company-description > p')[0].text if soup.select(
        '#listing-company-description > p') else ""
    industry = soup.select('#company-industry')[0].text if soup.select('#company-industry') else ""
    company_type = soup.select('#listing-type')[0].text if soup.select('#listing-type') else ""
    company_age = soup.select('#compAge > span')[0].text if soup.select('#compAge > span') else ""
    employees = soup.select('#emp-count')[0].text if soup.select('#emp-count') else ""

    row.append(company_name)
    row.append(job_title)
    row.append(locations)
    row.append(about_role)
    row.append(functions)
    row.append(skills)
    row.append(known_requirements)
    row.append(travel)
    row.append(about_company)
    row.append(industry)
    row.append(company_type)
    row.append(company_age)
    row.append(employees)

    row = addJobContacts(soup, row)
    results.append(row)

    return results


def parse_html_to_csv(files):
    myFiles = files
    headers = ["company_name", "job_title", "locations", "about_role", "functions", "skills", "known_requirements",
               "travel", "about_company", "industry", "company_type", "company_age", "employees", "job_contact_name",
               "job_contact_email", "job_contact_title", "job_contact_name2", "job_contact_email2",
               "job_contact_title2", "job_contact_name3", "job_contact_email3", "job_contact_title3",
               "job_contact_name4", "job_contact_email4", "job_contact_title4"]
    results = [headers]

    print("File parsed:")
    for file in myFiles:
        htmlTxt = file.read().decode("utf-8")
        results = parseHTML(htmlTxt, results)

    if not os.path.exists(settings.CSV_OUTPUT_FILE):
        os.makedirs(settings.CSV_OUTPUT_FILE)

    with open('{}/crawlData.csv'.format(settings.CSV_OUTPUT_FILE), 'w', newline="", encoding='utf-8') as out:
        writer = csv.writer(out)
        for r in results:
            try:
                writer.writerow(r)
            except:
                "Pass Here"
