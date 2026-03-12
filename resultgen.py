from app import get_pdf, gen_matrix, get_info
from concurrent.futures import ThreadPoolExecutor

branch_code = { "Biomed": 111, "Biotech":112, "Chemical":113, "Civil":114, "CSE":115, "ECE":116, "EE":117, "IT":118, "Mech":119, "Meta":120, "Mining":121 }

def generate_branch_result(branch):
    start_roll = f"25{branch_code[branch]}001"
    end_roll = f"25{branch_code[branch]}120"
    data = []
    roll_list = [i for i in range(int(start_roll), int(end_roll))]
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(get_info, roll_list))
    data = [r for r in results if r]
    return data