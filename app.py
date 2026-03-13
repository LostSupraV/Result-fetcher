import requests
import urllib3
from bs4 import BeautifulSoup
import re
import pdfplumber
import io

urllib3.disable_warnings()

url = "https://mis.nitrr.ac.in/publishedresult.aspx"

def is_decimal(s):
    pattern = "^\d+\.\d+$"
    return bool(re.findall(pattern, s)) or s.isnumeric()

def start_session(rollno):
    global url
    session = requests.Session()

    # First request (get hidden fields)
    response1 = session.get(url, verify=False)
    soup = BeautifulSoup(response1.text, 'html.parser')

    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]

    # Form data
    payload1 = {
        "__EVENTTARGET":"",
        "__EVENTARGUMENT":"", 
        "__LASTFOCUS":"",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__VIEWSTATEENCRYPTED":"",
        "__EVENTVALIDATION": eventvalidation,
        "txtRegno": str(rollno),   # safer as string
        "ddlDegreename": "0",
        "txtVerifiyCode":"",
        "btnimgShow" :"Show"
    }

    # Submit form
    response2 = session.post(url, data=payload1, verify=False)
    soup1 = BeautifulSoup(response2.text, 'html.parser')
    return session, soup1

def get_pdf(rollno):
    try:
        global url
        session, soup = start_session(rollno)
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
        viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]

        payload2 = {
            "ddlSession":"120",
            "ddlSemester":"1",
            "btnCBCSTabulation":"CBCS Result",
            "ddlDegreename":"0",
            "txtVerifiyCode":"",
            "__EVENTTARGET":"",
            "__EVENTARGUMENT":"",
            "__LASTFOCUS":"",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__VIEWSTATEENCRYPTED":"",
            "__EVENTVALIDATION": eventvalidation,
        }

        # Get pdf_link
        response3 = session.post(url, data=payload2, verify=False)

        html = response3.text
        pattern = re.compile(
            r"http://mis\.nitrr\.ac\.in/Reports/commonreportForCBCS\.aspx\?[^\s\"']+"
        )

        matches = pattern.findall(html)

        pdf_link = None
        
        for link in matches:
            pdf_link = link
        
        if not pdf_link:
            return None

        response4 = session.get(pdf_link, verify=False)
        pdf_file = io.BytesIO(response4.content) 

        with pdfplumber.open(pdf_file) as pdf:
            page = pdf.pages[0].extract_table()
        return page, soup
    except:
        return None

def gen_matrix(page):
    matrix = list()
    for row in page:
        if row[0].isnumeric():
            element = [row[2], row[3], row[4], row[5]]
            matrix.append(element)
    result_row = list()
    data = page[-1][0].split()
    if not is_decimal(data[4]):
        result_row.append("--")
        result_row.append("--")
        matrix.append(result_row)
        return matrix
    result_row.append(data[4])
    result_row.append(data[7])
    matrix.append(result_row)
    return matrix

def verify_roll(rollno):
    _,soup = start_session(rollno)
    name = soup.find(id="lblSName").text
    return bool(name)

def get_info(rollno):
    x = get_pdf(rollno)
    if not x:
        return None
    page, soup = x
    name_tag = soup.find(id="lblSName")
    matrix = gen_matrix(page)
    return (rollno, name_tag.text.title(),matrix[-1][0].strip(), matrix[-1][1].strip())

def get_profile(rollno):
    x = get_pdf(rollno)
    if not x:
        return None
    pdf,soup = get_pdf(rollno)
    matrix = gen_matrix(pdf)
    name_tag = soup.find(id="lblSName")
    enroll = soup.find(id="lblSEnrollNo")
    branch = soup.find(id="lblSBranch")
    if name_tag:
        name,enrollment, branch =  (name_tag.text.title(), enroll.text, branch.text.title())
    spi, cpi = matrix[-1]
    subjects = matrix[0:len(matrix)-1]
    return {
        "name":name,
        "enrollment":enrollment,
        "branch":branch,
        "spi":spi,
        "cpi":cpi,
        "subjects":subjects,
    }