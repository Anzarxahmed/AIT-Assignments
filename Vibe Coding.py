# ATM SIMULATION SYSTEM

import datetime
import hashlib
from abc import ABC, abstractmethod


# ======================================================
# CURRENCY CONVERTER
# ======================================================
class CurrencyConverter:
    RATES_TO_PKR = {"PKR": 1, "USD": 280, "EUR": 300}

    @classmethod
    def to_pkr(cls, amount, currency):
        currency = currency.upper()
        if currency not in cls.RATES_TO_PKR:
            raise ValueError("Unsupported currency.")
        return amount * cls.RATES_TO_PKR[currency]


# ======================================================
# USER CLASS
# ======================================================
class User:
    MAX_ATTEMPTS = 3
    LOCK_TIME_MINUTES = 2

    def __init__(self, user_id, name, pin, is_admin=False):
        self.user_id = user_id
        self.name = name
        self.is_admin = is_admin
        self.__pin_hash = self.__hash_pin(pin)
        self.failed_attempts = 0
        self.locked_until = None
        self.daily_withdrawals = {"PKR": 0, "USD": 0, "EUR": 0}
        self.last_withdrawal_date = datetime.date.today()

    def __hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    def is_locked(self):
        return (
            self.locked_until is not None
            and datetime.datetime.now() < self.locked_until
        )

    def verify_pin(self, pin):
        if self.is_locked():
            print("Account is locked. Try later.")
            return False
        if self.__pin_hash == self.__hash_pin(pin):
            self.failed_attempts = 0
            return True
        self.failed_attempts += 1
        if self.failed_attempts >= self.MAX_ATTEMPTS:
            self.locked_until = datetime.datetime.now() + datetime.timedelta(minutes=self.LOCK_TIME_MINUTES)
            print("Account locked for 2 minutes.")
        return False

    def change_pin(self, old_pin, new_pin):
        if len(new_pin) != 4 or not new_pin.isdigit():
            print("PIN must be 4 digits.")
            return False
        if self.verify_pin(old_pin):
            self.__pin_hash = self.__hash_pin(new_pin)
            print("PIN changed successfully.")
            return True
        else:
            print("Incorrect old PIN.")
            return False

    def reset_daily_withdrawals(self):
        if self.last_withdrawal_date != datetime.date.today():
            self.daily_withdrawals = {"PKR": 0, "USD": 0, "EUR": 0}
            self.last_withdrawal_date = datetime.date.today()


# ======================================================
# LOAN CLASS
# ======================================================
class Loan:
    def __init__(self, principal, currency, duration_years, start_date, interest_rate=0.03):
        self.principal = principal
        self.currency = currency
        self.duration_years = duration_years
        self.start_date = start_date
        self.interest_rate = interest_rate
        self.remaining_amount = principal * (1 + interest_rate * duration_years)

    def __str__(self):
        return (f"Loan: {self.principal} {self.currency}, "
                f"Duration: {self.duration_years:.2f} years, "
                f"Remaining: {self.remaining_amount:.2f} {self.currency}")


# ======================================================
# ABSTRACT ACCOUNT CLASS
# ======================================================
class Account(ABC):
    DAILY_LIMITS = {"PKR": 20000, "USD": 500, "EUR": 600}

    def __init__(self, balance_pkr):
        self._balance_pkr = balance_pkr
        self.transactions = []
        self.loans = []

    @property
    def balance(self):
        return self._balance_pkr

    def _log_transaction(self, message):
        timestamp = datetime.datetime.now()
        self.transactions.append(f"{timestamp} - {message}")

    def deposit(self):
        try:
            amount = float(input("Enter deposit amount: "))
            if amount <= 0:
                print("Deposit amount must be positive.")
                return
            currency = input("Enter currency (PKR/USD/EUR): ").upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            self._balance_pkr += amount_pkr
            self._log_transaction(f"Deposited {amount} {currency} (PKR {amount_pkr})")
            print(f"Deposit successful. PKR {amount_pkr} added.")
        except ValueError:
            print("Invalid input or unsupported currency.")

    @abstractmethod
    def withdraw(self, user: User):
        pass

    def take_loan(self):
        try:
            amount = float(input("Enter loan amount: "))
            if amount <= 0:
                print("Loan amount must be positive.")
                return
            currency = input("Enter currency (PKR/USD/EUR): ").upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            duration_type = input("Duration type (months/years): ").lower()
            duration = int(input(f"Enter number of {duration_type}: "))
            if duration <= 0:
                print("Duration must be positive.")
                return
            years = duration / 12 if duration_type == "months" else duration
            interest = amount_pkr * 0.03 * years

            # Create loan
            loan = Loan(principal=amount, currency=currency, duration_years=years,
                        start_date=datetime.date.today())
            self.loans.append(loan)
            self._balance_pkr += amount_pkr
            self._log_transaction(f"Loan taken: {amount} {currency} (PKR {amount_pkr}), Duration: {duration} {duration_type}, Interest: PKR {interest:.2f}")
            print(f"Loan granted! PKR {amount_pkr} added. Interest: PKR {interest:.2f}")
        except ValueError:
            print("Invalid input.")

    def check_loans(self):
        if not self.loans:
            print("No loans taken yet.")
        else:
            print("Current loans:")
            for idx, loan in enumerate(self.loans, 1):
                print(f"{idx}. {loan}")

    def pay_loan(self):
        if not self.loans:
            print("No loans to pay.")
            return
        self.check_loans()
        try:
            choice = int(input("Select loan number to pay: "))
            if choice < 1 or choice > len(self.loans):
                print("Invalid choice.")
                return
            loan = self.loans[choice - 1]
            amount = float(input(f"Enter amount to pay in {loan.currency}: "))
            if amount <= 0:
                print("Amount must be positive.")
                return
            amount_pkr = CurrencyConverter.to_pkr(amount, loan.currency)
            if amount_pkr > self._balance_pkr:
                print("Insufficient balance to pay this amount.")
                return
            if amount > loan.remaining_amount:
                amount = loan.remaining_amount
                amount_pkr = CurrencyConverter.to_pkr(amount, loan.currency)
            self._balance_pkr -= amount_pkr
            loan.remaining_amount -= amount
            self._log_transaction(f"Loan payment: {amount} {loan.currency} (PKR {amount_pkr})")
            print(f"Payment successful. Remaining loan: {loan.remaining_amount:.2f} {loan.currency}")
            if loan.remaining_amount <= 0:
                print("Loan fully paid!")
                self.loans.remove(loan)
        except ValueError:
            print("Invalid input.")


# ======================================================
# SAVINGS ACCOUNT
# ======================================================
class SavingsAccount(Account):
    MIN_BALANCE_PKR = 1000

    def withdraw(self, user: User):
        try:
            amount = float(input("Enter withdrawal amount: "))
            if amount <= 0:
                print("Withdrawal must be positive.")
                return
            currency = input("Enter currency (PKR/USD/EUR): ").upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            user.reset_daily_withdrawals()

            if user.daily_withdrawals[currency] + amount > Account.DAILY_LIMITS[currency]:
                print(f"Daily withdrawal limit exceeded for {currency}.")
                return
            if self._balance_pkr - amount_pkr < self.MIN_BALANCE_PKR:
                print("Minimum balance requirement not met.")
                return

            self._balance_pkr -= amount_pkr
            user.daily_withdrawals[currency] += amount
            self._log_transaction(f"Withdrew {amount} {currency} (PKR {amount_pkr})")
            print(f"Withdrawal successful. PKR {amount_pkr} deducted.")
        except ValueError:
            print("Invalid input.")


# ======================================================
# CURRENT ACCOUNT
# ======================================================
class CurrentAccount(Account):
    def withdraw(self, user: User):
        try:
            amount = float(input("Enter withdrawal amount: "))
            if amount <= 0:
                print("Withdrawal must be positive.")
                return
            currency = input("Enter currency (PKR/USD/EUR): ").upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            user.reset_daily_withdrawals()

            if user.daily_withdrawals[currency] + amount > Account.DAILY_LIMITS[currency]:
                print(f"Daily withdrawal limit exceeded for {currency}.")
                return
            if self._balance_pkr - amount_pkr < 0:
                print("Insufficient balance.")
                return

            self._balance_pkr -= amount_pkr
            user.daily_withdrawals[currency] += amount
            self._log_transaction(f"Withdrew {amount} {currency} (PKR {amount_pkr})")
            print(f"Withdrawal successful. PKR {amount_pkr} deducted.")
        except ValueError:
            print("Invalid input.")


# ======================================================
# ATM CLASS
# ======================================================
class ATM:
    def __init__(self):
        self.users = {}
        self.accounts = {}

    def add_user(self, user: User, account: Account):
        self.users[user.user_id] = user
        self.accounts[user.user_id] = account

    def login(self):
        print("\nType 'exit' to close the ATM.")
        user_id = input("User ID: ").strip()
        if user_id.lower() == "exit":
            print("Thank you for using the ATM.")
            exit()
        if user_id not in self.users:
            print("User not found.")
            return
        user = self.users[user_id]
        pin = input("PIN: ")
        if not user.verify_pin(pin):
            print("Login failed.")
            return
        if user.is_admin:
            self.admin_menu()
        else:
            self.user_menu(user)

    # ---------------- USER MENU ----------------
    def user_menu(self, user: User):
        account = self.accounts[user.user_id]
        while True:
            print(f"""
Welcome {user.name}
1. Check Balance (PKR)
2. Deposit
3. Withdraw
4. View Transactions
5. Change PIN
6. Take a Loan
7. Check Loans
8. Pay Loan
9. Logout
""")
            choice = input("Select option: ")

            if choice == "1":
                print(f"Balance: PKR {account.balance}")
            elif choice == "2":
                account.deposit()
            elif choice == "3":
                account.withdraw(user)
            elif choice == "4":
                if account.transactions:
                    for t in account.transactions[-10:]:
                        print(t)
                else:
                    print("No transactions found.")
            elif choice == "5":
                old_pin = input("Enter old PIN: ")
                new_pin = input("Enter new PIN: ")
                user.change_pin(old_pin, new_pin)
            elif choice == "6":
                account.take_loan()
            elif choice == "7":
                account.check_loans()
            elif choice == "8":
                account.pay_loan()
            elif choice == "9":
                print("Logged out.")
                break
            else:
                print("Invalid choice.")

    # ---------------- ADMIN MENU ----------------
    def admin_menu(self):
        while True:
            print("""
ADMIN PANEL
1. View Users
2. View Transactions (including loans)
3. Freeze User
4. Logout
""")
            choice = input("Select option: ")
            if choice == "1":
                for u in self.users.values():
                    print(u.user_id, "-", u.name)
            elif choice == "2":
                for uid, account in self.accounts.items():
                    print(f"\nTransactions for {self.users[uid].name} (UserID: {uid}):")
                    if account and account.transactions:
                        for t in account.transactions[-10:]:
                            print(t)
                    else:
                        print("No transactions found.")
            elif choice == "3":
                uid = input("User ID to freeze: ")
                if uid in self.users:
                    self.users[uid].locked_until = datetime.datetime.now() + datetime.timedelta(days=365)
                    print("User account frozen.")
                else:
                    print("User not found.")
            elif choice == "4":
                break
            else:
                print("Invalid option.")


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    atm = ATM()

    # Admin
    atm.add_user(User("admin", "Bank Admin", "9999", is_admin=True), None)

    # Users
    atm.add_user(User("101", "Anzar", "1234"), SavingsAccount(10000))
    atm.add_user(User("102", "Ali", "4321"), CurrentAccount(20000))

    while True:
        try:
            atm.login()
        except KeyboardInterrupt:
            print("\nATM session closed safely.")
            break

