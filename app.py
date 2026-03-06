import requests
import urllib3
from bs4 import BeautifulSoup
import re
import pdfplumber
import io

urllib3.disable_warnings()

def get_pdf(rollno):
    url = "https://mis.nitrr.ac.in/publishedresult.aspx"

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
    viewstate = soup1.find("input", {"name": "__VIEWSTATE"})["value"]
    eventvalidation = soup1.find("input", {"name": "__EVENTVALIDATION"})["value"]
    viewstategenerator = soup1.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]

    payload2 = {
        "ddlSession":"121",
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

    response3 = session.post(url, data=payload2, verify=False)

    html = response3.text
    pattern = re.compile(
        r"http://mis\.nitrr\.ac\.in/Reports/commonreportForCBCS\.aspx\?[^\s\"']+"
    )

    matches = pattern.findall(html)

    pdf_link = None
    
    for url in matches:
        pdf_link = url
    
    if pdf_link is None:
        print("No PDF found for:", rollno)
        return None

    response4 = session.get(pdf_link, verify=False)
    pdf_file = io.BytesIO(response4.content) 

    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[0].extract_table()
    return page

def gen_matrix(page):
    matrix = list()
    for row in page:
        if row[0].isnumeric():
            element = [row[2], row[3], row[4], row[5]]
            matrix.append(element)
    return matrix

page = get_pdf("25116111")
matrix = gen_matrix(page)
print(matrix)