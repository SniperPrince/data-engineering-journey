#Question1: . Filter and reshape a list of dicts
# pythonemployees = [
#     {"name": "Alice", "dept": "Eng", "salary": 90000},
#     {"name": "Bob", "dept": "Sales", "salary": 60000},
#     {"name": "Carol", "dept": "Eng", "salary": 120000},
#     {"name": "Dave", "dept": "HR", "salary": 55000},
#     {"name": "Eve", "dept": "Eng", "salary": 105000},
# ]
# Return a list of names of Engineering employees earning above 100000. Expected: ["Carol", "Eve"]

pythonemployees = [
    {"name": "Alice", "dept": "Eng", "salary": 90000},
    {"name": "Bob", "dept": "Sales", "salary": 60000},
    {"name": "Carol", "dept": "Eng", "salary": 120000},
    {"name": "Dave", "dept": "HR", "salary": 55000},
    {"name": "Eve", "dept": "Eng", "salary": 105000},
]
#using For Loop
# result = []
# for employee in pythonemployees:
#     if employee["dept"] == "Eng" and employee["salary"] > 100000:
#         result.append(employee["name"])

#using List Comprehension

# result = [employee["name"] for employee in pythonemployees if employee["dept"] == "Eng" and employee["salary"] > 100000]

# print(result)

#Question2: Group employees by department
#Same data. Return a dict like {"Eng": ["Alice", "Carol", "Eve"], "Sales": ["Bob"], "HR": ["Dave"]}

# dept_grouping ={}


# for employee in pythonemployees:
#     if not employee["dept"] in dept_grouping.keys():
#         dept_grouping[employee["dept"]]= [employee["name"]]
#     else:
#         dept_grouping.get(employee["dept"]).append(employee["name"])

# print(dept_grouping)

#Using default dict:
# from collections import defaultdict

# dept_grouping = defaultdict(list)

# for employee in pythonemployees:
#     dept_grouping[employee["dept"]].append(employee["name"])

# print(dict(dept_grouping))


#Question3: 8. Average salary per department
#Same data. Return {"Eng": 105000.0, "Sales": 60000.0, "HR": 55000.0}

# data_dict={}


# for employee in pythonemployees:
#     curr_dept=employee.get('dept')
#     curr_salary=employee.get('salary')
#     if employee.get('dept') in data_dict:
#         data_dict[curr_dept][0]+=curr_salary
#         data_dict[curr_dept][1]+=1

#     else:
#         data_dict[curr_dept] = [curr_salary,1]


# result = {}

# for dept,info in data_dict.items():
#     result[dept]=info[0]/info[1]

# print(result)

#Now same question using default dict

# from collections import defaultdict

# totals= defaultdict(int)
# counts =defaultdict(int)

# for employee in pythonemployees:

#     totals[employee['dept']] += employee['salary']
#     counts[employee["dept"]] += 1


# result = { dept : totals[dept]/counts[dept] for dept in totals} 
# print(result)


#Question4. Read CSV and process
# Create a CSV file sales.csv:
# date,product,amount
# 2026-05-01,Widget,100
# 2026-05-01,Gadget,250
# 2026-05-02,Widget,150
# 2026-05-02,Gadget,300
# 2026-05-03,Widget,200
# Read it with Python's csv module. Calculate total sales per product. Expected: {"Widget": 450, "Gadget": 550}

# import csv

# result_dict={}
# with open('sales.csv','r') as sales_info:

#     csv_reader = csv.DictReader(sales_info)
    
    
#     for line in csv_reader:
#         curr_prod=line.get('product')
#         if curr_prod in result_dict:
#             result_dict[curr_prod]= int(result_dict.get(curr_prod))+int(line.get('amount'))
#         else:
#             result_dict[curr_prod]= int(line.get('amount'))
        

# print(result_dict)

# Question5: JSON in/out
# Take the employees list from Q6. Write it to employees.json. Then read it back. Then write only the Engineering employees to eng_only.json
# import json
# from collections import defaultdict

# employee_names=[]
# for employee in pythonemployees:

#     if employee['name']  not in employee_names:
#         employee_names.append({employee['name']:{'Dept':employee['dept'],'Salary':employee['salary']}})


# print(employee_names)


# with open('employees.json','w') as f:
#     json.dump(employee_names,f,indent=2)
# eng_employees=[]
# with open('employees.json','r') as f:

#     data= json.load(f)

#     for employee in data:
#         for employee_info in employee.values():
#             if employee_info['Dept'] == 'Eng':
#                 eng_employees.append(employee)

# print(eng_employees)


# with open('eng_employees.json','w') as f:
#     json.dump(eng_employees,f,indent=2)
    

            
   


