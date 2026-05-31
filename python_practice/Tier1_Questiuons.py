#Question 1: FizzBuzz, Python style Print numbers 1-100. For multiples of 3, print "Fizz". For 5, print "Buzz".
#For both, "FizzBuzz"

# def FizzBuzz():
#     for i in range(1,101):
#         if i%3==0 and i%5==0:
#             print("FizzBuzz")
#         elif i%3==0:
#             print("Fizz")
#         elif i%5==0:
#             print("Buzz")
#         else:
#             print("Not a multiple of either 3 or 5 or both")

# FizzBuzz()


#Question2: 2. Word counter
#Given a string , return a dict of word → count

# s="the quick brown fox jumps over the lazy dog the fox is quick"

# words_lst=s.split(" ")
# word_count={}

# for word in words_lst:
#     if word_count.get(word)==None:
#         word_count[word]=1
#     else:
#         word_count[word]+=1

# print(word_count)


#Question3: Filter even squares
#Given nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], return a list of squares of even numbers only. 
#Expected: [4, 16, 36, 64, 100]

# nums= [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# even_squares = []
# #forLoop
# # for i in nums:
# #     if i%2==0:
# #         even_squares.append(i*i)

# # print(even_squares)

# #Now with list comprehension
# even_squares = [x*x for x in nums if x%2==0]

# print(even_squares)

#Question4: Reverse a string without [::-1]
#Then do it again with [::-1]

# s="the quick brown fox jumps over the lazy dog the fox is quick"

# reversed=""
# words= s.split(" ")

# for word in words[::-1]:
#     reversed=reversed+word+" "

# print(reversed.strip())

#Question5: Find the max key by value
#Given scores = {"Alice": 88, "Bob": 92, "Carol": 79, "Dave": 95}, 
#return the name with the highest score. Expected: "Dave"

scores = {"Alice": 88, "Bob": 92, "Carol": 79, "Dave": 95}

max_score=-1
name=""

for student in scores:
    if scores[student]> max_score:
        max_score=scores[student]
        name=student

print(name)