# # Implementing Inheritance in Python
# class Employee:
#     def __init__(self, name, salary):
#         self.name = name
#         self.salary = salary

#     def display_info(self):
#         print("Name:", self.name)
#         print("Salary:", self.salary)

# class Manager(Employee):
#     def role(self):
#         print("Role: Manager")

# class Developer(Employee):
#     def role(self):
#         print("Role: Developer")

# class Designer(Employee):
#     def role(self):
#         print("Role: Designer")


# class Intern(Employee):
#     def role(self):
#         print("Role: Intern")


# m = Manager("Ali", 80000)
# d = Developer("Sara", 60000)
# ds = Designer("Usman", 55000)
# i = Intern("Ayesha", 20000)

# m.display_info()
# m.role()
# print()

# d.display_info()
# d.role()
# print()

# ds.display_info()
# ds.role()
# print()

# i.display_info()
# i.role()


# Implementing abstraction in Python

from abc import ABC, abstractmethod
import math

class Calculator(ABC):

    @abstractmethod
    def add(self, a, b):
        pass

    @abstractmethod
    def subtract(self, a, b):
        pass

    @abstractmethod
    def multiply(self, a, b):
        pass

    @abstractmethod
    def divide(self, a, b):
        pass

    @abstractmethod
    def modulus(self, a, b):
        pass

    @abstractmethod
    def power(self, a, b):
        pass

    @abstractmethod
    def sqrt(self, a):
        pass


class BasicCalculator(Calculator):

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            return "Error: Division by zero"
        return a / b

    def modulus(self, a, b):
        return a % b

    def power(self, a, b):
        return a ** b

    def sqrt(self, a):
        if a < 0:
            return "Error: Negative number"
        return math.sqrt(a)


calc = BasicCalculator()

while True:
    print("\n--- Calculator Menu ---")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Modulus")
    print("6. Power")
    print("7. Square Root")
    print("8. Exit")

    choice = input("Enter your choice (1-8): ")
    print()

    if choice == '8':
        print("Exiting calculator...")
        break

    try:
        if choice == '7':
            num = float(input("Enter number: "))
            print("Square Root =", calc.sqrt(num))

        elif choice in ['1', '2', '3', '4', '5', '6']:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
            print()

            if choice == '1':
                print("Addition =", calc.add(a, b))
            elif choice == '2':
                print("Subtraction =", calc.subtract(a, b))
            elif choice == '3':
                print("Multiplication =", calc.multiply(a, b))
            elif choice == '4':
                print("Division =", calc.divide(a, b))
            elif choice == '5':
                print("Modulus =", calc.modulus(a, b))
            elif choice == '6':
                print("Power =", calc.power(a, b))

        else:
            print("Invalid choice! Please try again.")

    except ValueError:
        print("Invalid input! Please enter numeric values only.")

    