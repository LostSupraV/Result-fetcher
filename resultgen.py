from app import get_pdf, gen_matrix
from concurrent.futures import ThreadPoolExecutor

def process_result(rollno):
    pdf = get_pdf(rollno)
    if not pdf:
        return None
    else:
        matrix = gen_matrix(pdf)
        return matrix[-1][0]

roll_numbers = [str(i) for i in range(25116001, 25116113)]

with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(process_result, roll_numbers))

print(results)