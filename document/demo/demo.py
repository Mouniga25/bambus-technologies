"""a='mmouni'
b={'m': 1 , 'o': 2, 'u': 3, 'n':4, 'i':5, 'g': 6 ,'a':7}
for i in a:
    set ={}
    count = 0
    if (i in b):
        count = count+1
        print(i, end = " ")
        print(count)"""

a = input()
b = {}
for i in a:
    if i in b:
        b[i] += 1
    else:
        b[i] = 1
print(b)


"""a = [1,5,2,8,3,2,9]
#print(set(a))
b = []
for i in a:
    if (i != b):
         b.append(i)
b = set(b)
print(list(b))"""
        


"""for i in range(2000, 3201):
    if (i%7==0 and i%5 !=0):
        print(i, end=",")
print(".......")
"""


"""a = int(input())
count = 1
for i in range(a):
    if (a != 0):
        count = count * a
    a -= 1
print(count)
"""

"""
a = int(input())
d ={}
for i in range(0,a+1):
    d[i] = i*i
print(d)"""



"""a = input()
b = a[::-1]
print(a)
print(b)"""



"""b = int(input())
l =[]
for i in range(b):
    a = input()
    l.append(a)
print(l)
print(tuple(l)) 
"""


# b = input()
# print(b)
# print(b.split(","))


















