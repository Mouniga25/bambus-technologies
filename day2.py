"""values = 4576
final =''
while values:
    temp = values % 10
    values = values//10 
    final +=str(temp)
print(final)"""

"""
student = {'mouni': 100, 'jack':80, 'rose':50}
print(student)
student.update({'rose':60})
print(student)
student.pop('rose')
print(student)
student.update({'tom':50})
print(student)"""

"""lst = [1,7,8,6,2,8,0,10,8,6,5,90]
print(lst)
lst = set(lst)
print(list(lst))"""

"""
lst = [1,7,8,6,8]
lst1 = []
for i in lst:
    if i not in lst1:
        lst1.append(i)
print(lst1)
for i in range(len(lst1)):
    for j in range(len(lst1)):
        if lst1[i] < lst1[j]:
            lst1[i],lst1[j] =lst1[j],lst1[i]
print(lst1)"""

"""first_val = [1,2,3,4]
second_val =[3,4,5,6]
final =[]
for i in first_val:
    if i in second_val:
        final.append(i)
print(final)"""


"""
nums = {1, 2, 4, 6, 7, 10, 15, 20}
full = set(range(1, 21))
missing = full - nums
print(sorted(missing))"""


"""
lst_student={}
while True:
    print("1.add")
    print("2.delete")
    print("3.show")
    print("4.exit")
    val = int(input('enter the input'))
    if(val==1):
        student= input("enter the name:")
        stu_age=int(input("enter the age:"))
        lst_student[student]=stu_age
        print(lst_student)
        print("added")   
    elif(val ==2):
        student_name=input("enter the name:")
        lst_student.pop(student_name)
        print("deleted")
    elif(val==3):
        print("student details",end=" ")
        print(lst_student)
    else:
        print("check your input")
        break
"""
# file handing 0
"""
val = open("example1.txt")
print(val.read())
"""
"""
with open("example1.txt", "a+") as final_val:
    final_val.write("it is an porgramming language")
with open("example1.txt") as final_val:
    print(final_val.read())
"""

"""
with open("demo.txt") as val:
    for i in val:
        print(i)
        value = i.strip().split(",")
        print(value)
        with open(f'{value[0]}.pdf',"a") as final:
            for j in range(1,len(value)):
                final.write(value[j]+ "\n")  """













