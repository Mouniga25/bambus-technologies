#task 1 Bank Management System
class BankAccount:
    def __init__(self,account_number,holder_name,balance):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance= balance

    def deposit(self):
        amount = int(input("Enter the deposit amount:"))
        print("before balance", self.balance)
        if (amount >=0):
            self.balance += amount
            print("after balance:",self.balance)
        else:
              print("check your amount and give me the valid amount")
    def withdraw(self):
        amount = int(input("Enter the withdraw amount:"))
        print("before withdraw:", self.balance)
        if(amount >= 0 and self.balance >=0 and self.balance >= amount):
            self.balance -= amount
            print("after withdraw:", self.balance)
        else:
            print("please check your balance")
    def check_balance(self):
        print("check the balance:", self.balance)
bank = BankAccount(1234,"mouni",1000)
while True:
    print("1.deposit")
    print("2.witdraw")
    print("3.check the balance")
    print("4.exit")
    choice = input("Enter your choice:")
    if choice =='1':
        bank.deposit()
    elif choice =='2':
        bank.withdraw()
    elif choice == '3':
        bank.check_balance()
    elif choice == '4':
        print("thank you") 
        break
    else:
        print("check your choice")
