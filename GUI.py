import datetime
import hashlib
from abc import ABC, abstractmethod
import streamlit as st


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
            return False, "Account is locked. Try later."
        if self.__pin_hash == self.__hash_pin(pin):
            self.failed_attempts = 0
            return True, ""
        self.failed_attempts += 1
        if self.failed_attempts >= self.MAX_ATTEMPTS:
            self.locked_until = datetime.datetime.now() + datetime.timedelta(minutes=self.LOCK_TIME_MINUTES)
            return False, "Account locked for 2 minutes."
        return False, "Incorrect PIN."

    def change_pin(self, old_pin, new_pin):
        if len(new_pin) != 4 or not new_pin.isdigit():
            return False, "PIN must be 4 digits."
        success, msg = self.verify_pin(old_pin)
        if success:
            self.__pin_hash = self.__hash_pin(new_pin)
            return True, "PIN changed successfully."
        else:
            return False, msg

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

    def deposit(self, amount, currency):
        try:
            if amount <= 0:
                return "Deposit amount must be positive."
            currency = currency.upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            self._balance_pkr += amount_pkr
            self._log_transaction(f"Deposited {amount} {currency} (PKR {amount_pkr})")
            return f"Deposit successful. PKR {amount_pkr} added."
        except ValueError:
            return "Invalid input or unsupported currency."

    @abstractmethod
    def withdraw(self, amount, currency, user):
        pass

    def take_loan(self, amount, currency, duration_type, duration):
        try:
            if amount <= 0:
                return "Loan amount must be positive."
            currency = currency.upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            if duration <= 0:
                return "Duration must be positive."
            years = duration / 12 if duration_type == "months" else duration
            interest = amount_pkr * 0.03 * years

            # Create loan
            loan = Loan(principal=amount, currency=currency, duration_years=years,
                        start_date=datetime.date.today())
            self.loans.append(loan)
            self._balance_pkr += amount_pkr
            self._log_transaction(f"Loan taken: {amount} {currency} (PKR {amount_pkr}), Duration: {duration} {duration_type}, Interest: PKR {interest:.2f}")
            return f"Loan granted! PKR {amount_pkr} added. Interest: PKR {interest:.2f}"
        except ValueError:
            return "Invalid input."

    def get_loans(self):
        return self.loans

    def pay_loan(self, loan_index, amount):
        if not self.loans:
            return "No loans to pay."
        if loan_index < 0 or loan_index >= len(self.loans):
            return "Invalid loan selection."
        loan = self.loans[loan_index]
        if amount <= 0:
            return "Amount must be positive."
        amount_pkr = CurrencyConverter.to_pkr(amount, loan.currency)
        if amount_pkr > self._balance_pkr:
            return "Insufficient balance to pay this amount."
        if amount > loan.remaining_amount:
            amount = loan.remaining_amount
            amount_pkr = CurrencyConverter.to_pkr(amount, loan.currency)
        self._balance_pkr -= amount_pkr
        loan.remaining_amount -= amount
        self._log_transaction(f"Loan payment: {amount} {loan.currency} (PKR {amount_pkr})")
        message = f"Payment successful. Remaining loan: {loan.remaining_amount:.2f} {loan.currency}"
        if loan.remaining_amount <= 0:
            message += " Loan fully paid!"
            self.loans.remove(loan)
        return message

    def get_transactions(self):
        return self.transactions[-10:]


# ======================================================
# SAVINGS ACCOUNT
# ======================================================
class SavingsAccount(Account):
    MIN_BALANCE_PKR = 1000

    def withdraw(self, amount, currency, user):
        try:
            if amount <= 0:
                return "Withdrawal must be positive."
            currency = currency.upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            user.reset_daily_withdrawals()

            if user.daily_withdrawals[currency] + amount > Account.DAILY_LIMITS[currency]:
                return f"Daily withdrawal limit exceeded for {currency}."
            if self._balance_pkr - amount_pkr < self.MIN_BALANCE_PKR:
                return "Minimum balance requirement not met."

            self._balance_pkr -= amount_pkr
            user.daily_withdrawals[currency] += amount
            self._log_transaction(f"Withdrew {amount} {currency} (PKR {amount_pkr})")
            return f"Withdrawal successful. PKR {amount_pkr} deducted."
        except ValueError:
            return "Invalid input."


# ======================================================
# CURRENT ACCOUNT
# ======================================================
class CurrentAccount(Account):
    def withdraw(self, amount, currency, user):
        try:
            if amount <= 0:
                return "Withdrawal must be positive."
            currency = currency.upper()
            amount_pkr = CurrencyConverter.to_pkr(amount, currency)
            user.reset_daily_withdrawals()

            if user.daily_withdrawals[currency] + amount > Account.DAILY_LIMITS[currency]:
                return f"Daily withdrawal limit exceeded for {currency}."
            if self._balance_pkr - amount_pkr < 0:
                return "Insufficient balance."

            self._balance_pkr -= amount_pkr
            user.daily_withdrawals[currency] += amount
            self._log_transaction(f"Withdrew {amount} {currency} (PKR {amount_pkr})")
            return f"Withdrawal successful. PKR {amount_pkr} deducted."
        except ValueError:
            return "Invalid input."


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

    def login(self, user_id, pin):
        if user_id not in self.users:
            return None, "User not found."
        user = self.users[user_id]
        success, msg = user.verify_pin(pin)
        if success:
            return user, ""
        else:
            return None, msg

    def get_users(self):
        return [(u.user_id, u.name) for u in self.users.values()]

    def get_all_transactions(self):
        return {uid: account.get_transactions() if account else [] for uid, account in self.accounts.items()}

    def freeze_user(self, uid):
        if uid in self.users:
            self.users[uid].locked_until = datetime.datetime.now() + datetime.timedelta(days=365)
            return "User account frozen."
        else:
            return "User not found."


# ======================================================
# STREAMLIT APP
# ======================================================
def main():
    st.title("ATM System")

    if 'atm' not in st.session_state:
        st.session_state.atm = ATM()
        # Admin
        st.session_state.atm.add_user(User("admin", "Bank Admin", "9999", is_admin=True), None)
        # Users
        st.session_state.atm.add_user(User("101", "Anzar", "1234"), SavingsAccount(10000))
        st.session_state.atm.add_user(User("102", "Ali", "4321"), CurrentAccount(20000))

    if 'user' not in st.session_state:
        st.session_state.user = None

    atm = st.session_state.atm

    if st.session_state.user is None:
        st.header("Login")
        user_id = st.text_input("User ID")
        pin = st.text_input("PIN", type="password")
        if st.button("Login"):
            user, msg = atm.login(user_id, pin)
            if user:
                st.session_state.user = user
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(msg)
    else:
        user = st.session_state.user
        st.sidebar.header(f"Welcome {user.name}")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

        if user.is_admin:
            admin_menu(atm)
        else:
            user_menu(atm, user)


def user_menu(atm, user):
    account = atm.accounts[user.user_id]

    st.header("User Menu")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check Balance"):
            st.info(f"Balance: PKR {account.balance}")

        if st.button("View Transactions"):
            transactions = account.get_transactions()
            if transactions:
                for t in transactions:
                    st.write(t)
            else:
                st.write("No transactions found.")

        if st.button("Check Loans"):
            loans = account.get_loans()
            if loans:
                for idx, loan in enumerate(loans, 1):
                    st.write(f"{idx}. {loan}")
            else:
                st.write("No loans taken yet.")

    with col2:
        with st.expander("Deposit"):
            with st.form("deposit_form"):
                amount = st.number_input("Amount", min_value=0.0)
                currency = st.selectbox("Currency", ["PKR", "USD", "EUR"])
                submitted = st.form_submit_button("Deposit")
                if submitted:
                    msg = account.deposit(amount, currency)
                    st.success(msg)

        with st.expander("Withdraw"):
            with st.form("withdraw_form"):
                amount = st.number_input("Amount", min_value=0.0)
                currency = st.selectbox("Currency", ["PKR", "USD", "EUR"])
                submitted = st.form_submit_button("Withdraw")
                if submitted:
                    msg = account.withdraw(amount, currency, user)
                    if "successful" in msg:
                        st.success(msg)
                    else:
                        st.error(msg)

        with st.expander("Change PIN"):
            with st.form("change_pin_form"):
                old_pin = st.text_input("Old PIN", type="password")
                new_pin = st.text_input("New PIN", type="password")
                submitted = st.form_submit_button("Change PIN")
                if submitted:
                    success, msg = user.change_pin(old_pin, new_pin)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

        with st.expander("Take a Loan"):
            with st.form("loan_form"):
                amount = st.number_input("Amount", min_value=0.0)
                currency = st.selectbox("Currency", ["PKR", "USD", "EUR"])
                duration_type = st.selectbox("Duration Type", ["months", "years"])
                duration = st.number_input("Duration", min_value=1, step=1)
                submitted = st.form_submit_button("Take Loan")
                if submitted:
                    msg = account.take_loan(amount, currency, duration_type, duration)
                    st.success(msg)

        with st.expander("Pay Loan"):
            loans = account.get_loans()
            if loans:
                loan_options = [f"{idx+1}. {str(loan)}" for idx, loan in enumerate(loans)]
                selected_loan = st.selectbox("Select Loan", loan_options)
                loan_index = loan_options.index(selected_loan)
                amount = st.number_input("Amount to Pay", min_value=0.0)
                if st.button("Pay Loan"):
                    msg = account.pay_loan(loan_index, amount)
                    st.success(msg)
            else:
                st.write("No loans to pay.")


def admin_menu(atm):
    st.header("Admin Panel")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("View Users"):
            users = atm.get_users()
            for uid, name in users:
                st.write(f"{uid} - {name}")

        if st.button("View All Transactions"):
            all_trans = atm.get_all_transactions()
            for uid, trans in all_trans.items():
                st.subheader(f"Transactions for {uid}")
                if trans:
                    for t in trans:
                        st.write(t)
                else:
                    st.write("No transactions.")

    with col2:
        with st.expander("Freeze User"):
            uid = st.text_input("User ID to Freeze")
            if st.button("Freeze"):
                msg = atm.freeze_user(uid)
                st.success(msg)


if __name__ == "__main__":
    main()