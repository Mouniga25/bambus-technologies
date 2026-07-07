"""
#odd or even 
number = int(input("Enter the number:"))
if (number %2==0):
    print("It is even number")
else:
    print("It is odd number")

"""


# reverse string 
"""
word = input("Enter the word:")
words = word[::-1]
print("word:",words)"""


"""
word = input("Enter the word:")
reversed =""
for i in word:
    reversed= i + reversed
print("string:",reversed)"""


#find largest number
"""
lst = [1,4,5,8,3]
largest_number = lst[0]
for i in lst:
    if i >largest_number:
        largest_number = i
print("largest number :",largest_number)
 """   


 #vowels word counting
"""
word = input("Enter the word:")
count = 0
lst = ['a','e','i','o','u']
for i in word:
    if i in lst:
        count +=1
print("count:",count)
"""


#fibonacci series
"""
number = int(input("Enter the number:"))
first_number = 0
second_number = 1
print(first_number,end=" ")
print(second_number,end=" ")
for i in range(1,number):
    value = first_number + second_number
    first_number=second_number
    second_number =value
    print(value,end=" ")"""

#palindrome
"""
word = input("Enter the word:")
res_word =""
for i in word:
    res_word =i + res_word 
if (word == res_word):
    print("palindrome")
else:
    print("not a palindrome")
"""

# prime number 
"""
number = int(input("enter the number:"))
count =0
for i in range(1, number+1):
    if(number % i == 0):
        count +=1

if count ==2:
    print(number,"it is prime")
else:
    print(number , "it is not a prime number")
    """ 
   

"""
import json
student = {"name":"mouni", "age":12,"city":"salem"}
show = json.dumps(student)
print(show)"""


