import requests
from bs4 import BeautifulSoup
import xlsxwriter
import datetime
import time

today_date = datetime.date.today()
today_date_str = today_date.strftime("%Y.%m.%d")

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('indeed.com_jobs.xlsx')
worksheet = workbook.add_worksheet()

column_titles = (
    'Job_ID', 'Job_Title', 'Company', 'Location', 'Salary', 'Job_Type', 'Posted', 'Job_Details_Link'
)
col = 0
row = 0
for title in column_titles:
    worksheet.write(row, col, title)
    col += 1

job_site_endpoint = "https://www.indeed.com"
page_number = 560
while True:
    print(page_number)

    URL = f'https://www.indeed.com/jobs?q=%22network%20engineer%22&sort=date&vjk=63164364e56632b8&start={page_number}'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("ul", class_="jobsearch-ResultsList")
    job_elements = None

    try:
        result_element = results[0]
        job_elements = result_element.select('div[class*="cardOutline tapItem"]')
    except Exception as e:
        time.sleep(1)
        continue

    #find pagination list
    results = soup.find_all("ul", class_="pagination-list")

    page_number += 10

    for job_element in job_elements:
        title_element = job_element.find("a", class_='jcs-JobTitle')
        title_text = title_element.text.strip()
        job_link = job_site_endpoint + title_element['href']

        company_element = job_element.find("span", class_='companyName')
        company_a_element = company_element.find("a")
        if company_a_element is not None:
            company_text = company_a_element.text.strip()
        else:
            company_text = company_element.text.strip()

        location_element = job_element.find("div", class_='companyLocation')
        location_text = ""
        for loc_item in location_element.contents:
            span_item = loc_item.find("span")
            if span_item != -1:
                if loc_item.has_attr('class') == True:
                    continue;
            location_text = loc_item.text.strip()
            if location_text is not None:
                break;

        salary_element = job_element.find("div", class_="heading6 tapItem-gutter metadataContainer noJEMChips salaryOnly")
        if salary_element is None:
            salary_text = 'NONE-Not Avail'
        else:
            salary_span_element = salary_element.find('span', class_='estimated-salary')
            if salary_span_element is None:
                salary_snippet_element = salary_element.find('div', class_='metadata salary-snippet-container')
                if salary_snippet_element is None:
                    salary_text = 'NONE-Not Avail'
                else:
                    salary_attr_element = salary_snippet_element.find('div', class_='attribute_snippet')
                    if salary_attr_element is None:
                        salary_text = 'NONE-Not Avail'
                    else:
                        salary_text = salary_attr_element.text.strip()
            else:
                salary_text = salary_span_element.text.strip()

        if salary_element is None:
            job_type_text = "None"
        else:
            try:
                job_type_element = salary_element.select('div.metadata:not(.salary-snippet-container):not(.estimated-salary-container)')[0].find("div", class_="attribute_snippet")
                job_type_text = job_type_element.contents[1].text.strip()
            except Exception as e:
                job_type_text = "None"

        page = requests.get(job_link)

        date_text = "None"
        soup = BeautifulSoup(page.content, "html.parser")
        meta_element = soup.find("div", class_="jobsearch-JobTab-content")
        try:
            if meta_element is not None:
                meta_element = meta_element.find("div", class_="jobsearch-JobMetadataFooter")
                print(job_link)
                if meta_element is not None:
                    for item in meta_element.contents:
                        if item.has_attr('class') == False:
                            date_text = item.text.strip()
        except Exception as e:
            date_text = "None"

        row += 1

        worksheet.write(row, 0, (f'{today_date_str}_{"%05d" % (row,)}'))
        worksheet.write(row, 1, title_text)
        worksheet.write(row, 2, company_text)
        worksheet.write(row, 3, location_text)
        worksheet.write(row, 4, salary_text)
        worksheet.write(row, 5, job_type_text)
        worksheet.write(row, 6, date_text)
        worksheet.write(row, 7, job_link)

    if len(results) > 0:
        result_element = results[0]
        last_page_element = result_element.select('li:last-child b[aria-current="true"]')
        print(last_page_element)
        if len(last_page_element) > 0:
            break
workbook.close()