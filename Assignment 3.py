# # 📝 Practice Question 1: Student Grades
# class Student:
#     def __init__(self):
#         self.__grade = None
    
#     def get_grade(self):
#         return self.__grade
    
#     def set_grade(self, grade):
#         if 0 <= grade <= 100:
#             self.__grade = grade
#         else:
#             print("Invalid grade")

#     def is_passed(self):
#         if self.__grade is not None and self.__grade >= 50:
#             return "Passed"
#         else:
#             return "Failed"


# student = Student()

# student.set_grade(120)
# student.set_grade(85)

# print("Grade:", student.get_grade())
# print("Status:", student.is_passed())


# 📝 Practice Question 2: Product Price
# class Product:
#     def __init__(self):
#         self.__price = 0

#     def get_price(self):
#         return self.__price

#     def set_price(self, amount):
#         if amount > 0:
#             self.__price = amount
#         else:
#             print("Invalid price")

#     def apply_discount(self, percent):
#         if 0 < percent < 100:
#             discount = (percent / 100) * self.__price
#             self.__price -= discount
#         else:
#             print("Invalid discount percentage")

# p = Product()

# p.set_price(-50)

# p.set_price(200)
# print("Price:", p.get_price())

# p.apply_discount(20)
# print("Price after discount:", p.get_price())



# 📝 Practice Question 3: Employee Salary
# class Employee:
#     def __init__(self):
#         self.__salary = 0

#     def get_salary(self):
#         return self.__salary

#     def set_salary(self, amount):
#         if amount >= 0:
#             self.__salary = amount
#         else:
#             print("Invalid salary")

#     def increase_salary(self, percent):
#         if percent > 0:
#             self.__salary += (percent / 100) * self.__salary

# emp = Employee()

# emp.set_salary(-1000)

# emp.set_salary(5000)
# print("Salary after setting:", emp.get_salary())

# emp.increase_salary(10)
# print("Salary after increment:", emp.get_salary())


# 📝 Practice Question 4: Car Speed
# class Car:
#     def __init__(self):
#         self.__speed = 0

#     def get_speed(self):
#         return self.__speed

#     def set_speed(self, value):
#         if value >= 0:
#             self.__speed = value
#         else:
#             print("Invalid speed")

#     def accelerate(self, amount):
#         if amount > 0:
#             self.__speed += amount

#     def brake(self, amount):
#         if amount > 0:
#             self.__speed -= amount
#             if self.__speed < 0:
#                 self.__speed = 0

# car = Car()

# car.set_speed(-20)

# car.set_speed(50)
# print("Speed after setting:", car.get_speed())

# car.accelerate(30)
# print("Speed after acceleration:", car.get_speed())

# car.brake(60)
# print("Speed after braking:", car.get_speed())

# print("Final speed:", car.get_speed())


# 📝 Practice Question 5: Bank Account Management
# class BankAccount:
#     def __init__(self):
#         self.__balance = 0

#     def get_balance(self):
#         return self.__balance

#     def set_balance(self, amount):
#         if amount >= 0:
#             self.__balance = amount
#         else:
#             print("Invalid balance amount")

#     def deposit(self, amount):
#         if amount > 0:
#             self.__balance += amount

#     def withdraw(self, amount):
#         if amount <= self.__balance:
#             self.__balance -= amount

# account = BankAccount()

# account.set_balance(-100)

# account.deposit(500)
# print("Balance after deposit:", account.get_balance())

# account.withdraw(300)
# print("Balance after withdrawal:", account.get_balance())

# print("Final balance:", account.get_balance())