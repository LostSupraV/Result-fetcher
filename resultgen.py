from app import get_pdf, gen_matrix
from concurrent.futures import ThreadPoolExecutor

def process_result(rollno):
    pdf = get_pdf(rollno)
    if not pdf:
        return None
    else:
        matrix = gen_matrix(pdf)
        sum=0
        for row in matrix:
            prt = int(row[2])*int(row[3])
            sum+=prt
        spi = sum/24
        return spi

roll_numbers = [str(i) for i in range(25116091, 25116113)]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_result, roll_numbers))

print(results)