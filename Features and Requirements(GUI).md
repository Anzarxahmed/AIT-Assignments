# Features and Requirements for GUI(Vibe Coding).py

## Overview
This is a Streamlit-based ATM (Automated Teller Machine) system converted from a command-line Python application. It simulates banking operations with user authentication, account management, loans, and an admin panel.

## Features

### User Authentication
- Login with User ID and 4-digit PIN
- PIN hashing using SHA-256 for security
- Account locking after 3 failed attempts (locks for 2 minutes)
- Separate admin and regular user roles

### Account Management
- Support for Savings and Current accounts
- Balance checking in PKR (Pakistani Rupees)
- Deposits and withdrawals in multiple currencies (PKR, USD, EUR)
- Currency conversion to PKR for internal calculations
- Daily withdrawal limits:
  - PKR: 20,000
  - USD: 500
  - EUR: 600
- Minimum balance requirement for Savings accounts (1,000 PKR)

### Loan System
- Take loans in different currencies and durations (months/years)
- Interest calculation (3% per year)
- Loan payment with automatic full payment detection
- View current loans

### Transaction Logging
- Logs all transactions with timestamps
- View last 10 transactions per account
- Admin can view transactions for all users

### Admin Panel
- View all users
- View transactions for all accounts
- Freeze user accounts (locks for 1 year)

### User Interface
- Web-based GUI using Streamlit
- Responsive layout with columns and expanders
- Forms for input validation
- Sidebar for logout
- Success/error messages for user feedback

## Requirements

### Software Requirements
- Python 3.7 or higher
- Streamlit library (`pip install streamlit`)

### Hardware Requirements
- Standard computer with internet access (for web interface)
- Sufficient RAM for running Streamlit app

### Dependencies
- `datetime` (built-in)
- `hashlib` (built-in)
- `abc` (built-in)
- `streamlit` (external)

### Installation Instructions
1. Ensure Python is installed
2. Install Streamlit: `pip install streamlit`
3. Run the app: `streamlit run "GUI(Vibe Coding).py"`

### Usage Instructions
- Start the app and access via browser
- Login with provided credentials:
  - Admin: User ID "admin", PIN "9999"
  - User 1: User ID "101", PIN "1234" (Savings Account)
  - User 2: User ID "102", PIN "4321" (Current Account)
- Navigate through menus using buttons and forms

## Limitations
- Data is stored in memory (not persistent across restarts)
- No database integration
- Simplified loan interest calculation
- No multi-user concurrency handling (single session per user)

## Future Enhancements
- Persistent data storage (database)
- User registration
- Advanced loan management
- Email notifications
- Multi-language support