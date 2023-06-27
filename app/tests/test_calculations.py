import pytest
from app.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds

@pytest.fixture
def zero_bank_account():
    return BankAccount()

@pytest.fixture
def fifty_bank_account():
    return BankAccount(50)

@pytest.mark.parametrize("num1, num2, result", [
    (3,5,8), 
    (5,6,11), 
    (7, 1, 8)
])
def test_add(num1, num2, result):
    assert add(num1,num2) == result

def test_substract():
    assert subtract(9,4) == 5

def test_multiply():
    assert multiply(4,4) == 16

def test_divide():
    assert divide(4,2) == 2

def test_bank_set_initial_amount(fifty_bank_account):
    assert fifty_bank_account.balance == 50

@pytest.mark.parametrize("deposited, withdrew, expected", [
    (200,100, 100), 
    (50,10,40), 
    (1200, 200, 1000)
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == expected

def test_insufficient_fund(fifty_bank_account):
    with pytest.raises(InsufficientFunds):
        fifty_bank_account.withdraw(100)


