# print('Hello World')

courses =['Physics','Maths','History']

# for idx,item in enumerate(courses,start=1):
#     print(idx,item)


# courses_tup=('History','Maths','Art')
# print(courses_tup[2])

# lst1=['Physics','Maths','History']
# lst2=lst1

# # both Lisst get changed , thats the problem with mutability
# lst1[0]='Science'
 
# print(lst1)
# print(lst2)


# courses_str='- '.join(courses)
# print(courses_str)


# new_lst=courses_str.split('- ')
# print(new_lst)

students={'name':'Candy','age': 24, 'courses': ['Maths','Science']}

# print(students['name'])

# print(students.get('phone_num'))
# print(students.keys())
# print(students.values())
# print(students.items())
# students.update({'name': 'Candy Singh','age' : 26,'phone_num': '633704844'})

# print(students)


# for key,val in students.items():
#     print(key,val)

# del students['age']

# age=students.pop('age')
# print(students)
# print(age)

# def hello_func(greetings):
#     return f'{greetings} Miss'


# print(hello_func('Hello'))


# def hello_func(greetings,name):
#     return f'{greetings}, {name}'
# #will give error as only 1 argument
# print(hello_func('Hi'))


# def hello_func(greetings,name='You'):
#     return f'{greetings},{name}'

# #not give error as we have default value for name 
# print(hello_func('Hi'))

# def hello_func(greetings,name='You'):
#     return f'{greetings},{name}'
 
#  #Here name is Postional keyword arguments
# print(hello_func('Hi','Candy'))

#when we dont knwo how many arguments and keyword arguments we will paas
#heere args is a tuple and kwargs is a dict
# def student_info(*args,**kwargs):
#     print(args)
#     print(kwargs)

# student_info('Maths','Art',name='candy',age=22)

#Now if we want to pass list then how 

# def student_info(*args,**kwargs):
#     print(args)
#     print(kwargs)

# courses=['Maths','Art']
# info= {'name':'candy','age':22}

# student_info(courses,info) #this will go as *args only try to run it.
# student_info(*courses,**info) #this is correct both of them will now unpack and go individually




