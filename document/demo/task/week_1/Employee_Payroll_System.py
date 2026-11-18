import json
class Employee:
    def __init__(self,Employee_id,name,salary):
        self.Employee_id = Employee_id
        self.name = name 
        self.salary=salary
    def show_salary(self):
        print("salary:",self.salary)
    def detail(self):
        employee_detail = {"id ": self.Employee_id, "name": self.name, "salary":self.salary}
        with open("employees_details.json","w") as emp_details:
            json.dump(employee_detail,emp_details)
            print("data is stored")
Employee_id= int(input("Enter the your emplyee_id:"))
name = input("Enter the your name:")
salary = int(input("Enter the salary:"))
Employees = Employee(Employee_id, name, salary)
Employees.detail()
Employees.show_salary()


