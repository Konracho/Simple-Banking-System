import random
import sqlite3

def connect_to_tadabase():
    conn = sqlite3.connect('card.s3db')
    return conn

def main_menu():
    print(f"1. Create an account\n"
          f"2. Log into account\n"
          f"0. Exit")
    change = int(input())
    if change == 0:
        exit()
    else:
        return change

def generate_card(card_pin):
    account_identifier = str(random.randint(100000000, 999999999))
    BIN = 400000  # Bank Identification Number
    card_number = f"{BIN}{account_identifier}"  # 6 + 9
    checksum = alg_luhn(card_number)
    card_number = f"{BIN}{account_identifier}{checksum}"   # 6 + 9 + 1
    print(f"Your card has been created\n"
          f"Your card number:\n"
          f"{card_number}")
    pin = f"{random.randint(1000, 9999, )}"
    print(f"Your card PIN:\n"
          f"{pin}")
    card_pin[card_number] = pin

    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO card (number, pin) VALUES (?, ?)", (card_number, pin))
    cursor.execute("UPDATE card SET id = id + 1")
    # cursor.execute("UPDATE card SET balance = balance + 100")
    conn.commit()
    conn.close()
    return card_pin, conn

def alg_luhn(card_number):
    sum_Luna = 0
    card_number_list = list(map(int, card_number))
    for i in range(0, len(card_number_list)):
        if i % 2 == 0:
            card_number_list[i] *= 2
        if card_number_list[i] > 9:
            card_number_list[i] = card_number_list[i] - 9
        sum_Luna += card_number_list[i]
        card_number_list[i] = str(card_number_list[i])
    checksum = 10 - (sum_Luna % 10)
    if checksum == 10:
        checksum = 0
    return checksum

def log_in():
    print(f"Enter your card number:")
    login = input()
    print(f"Enter your PIN:")
    pin = input()
    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT number, pin 
        FROM card 
        WHERE number = ? AND pin = ?""", (login, pin)
                   )
    result = cursor.fetchone()
    conn.close()
    if result:
        print('You have successfully logged in!')
        log_inside(login)

    else:
        print(f"Wrong card number or PIN!")
        main_menu()
        return

def errors_transfer(login, card_transfer):
    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM card")
    result = cursor.fetchall()
    if card_transfer[15] != str(alg_luhn(card_transfer[0: -1])):
        print(f"Probably you made a mistake in the card number. Please try again!")
        log_inside(login)

    cursor.execute("SELECT * FROM card WHERE number = ?", (card_transfer,))
    if cursor.fetchone() is not None:
        conn.close()
        print(f"Enter how much money you want to transfer:")
    else:
        print(f"Such a card does not exist.")
        log_inside(login)
    if card_transfer == login:
        print(f"You can't transfer money to the same account!")
        log_inside(login)

def log_inside(login):
    print(f"1. Balance\n"
          f"2. Add income\n"
          f"3. Do transfer\n"
          f"4. Close account\n"
          f"5. Log out\n"
          f"0. Exit")
    change_inside = int(input())

    if change_inside == 1:
        conn = connect_to_tadabase()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT balance 
            FROM card 
            WHERE number = ?""", (login, )
                       )
        result = cursor.fetchone()
        print("Balance:", result[0])
        conn.commit()
        conn.close()
        log_inside(login)

    elif change_inside == 2:
        print(f"Enter income:")
        add_income = int(input())
        conn = connect_to_tadabase()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE card 
            SET balance = balance + ? 
            WHERE number = ?""", (add_income, login)
                       )
        cursor.execute("""
            SELECT balance
            FROM card
            WHERE number = ?""", (login,))
        result = cursor.fetchone()
        print(f"Income was added!")
        conn.commit()
        conn.close()
        log_inside(login)

    elif change_inside == 3:
        print(f"Transfer\nEnter card number:")
        card_transfer = input()

        errors_transfer(login, card_transfer)

        money_transfer = int(input())

        errors_transfer(login, card_transfer)

        conn = connect_to_tadabase()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM card WHERE number = ?", (login,))
        balance_now = cursor.fetchone()

        if balance_now[0] >= money_transfer:
            cursor.execute("""
                UPDATE card 
                SET balance = balance + ? 
                WHERE number = ?""", (money_transfer, card_transfer)
                           )
            cursor.execute("""
                UPDATE card
                SET balance = balance - ?
                WHERE number = ?""", (money_transfer, login)
                           )
            conn.commit()
            conn.close()
            log_inside(login)
        else:
            print(f"Not enough money!")
            conn.close()
            log_inside(login)

    elif change_inside == 4:
        conn = connect_to_tadabase()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM card WHERE number = ?", (login,))

        conn.commit()
        conn.close()
    elif change_inside == 5:
        print(f"You have successfully logged out!")
        return
    elif change_inside == 0:
        print(f"Bye!")
        exit()

def main():
    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS card  (
            id INTEGER DEFAULT 0,
            number TEXT, 
            pin TEXT, 
            balance INTEGER DEFAULT 0
            )""")

    conn.commit()
    conn.close()
    card_pin = dict()
    change = main_menu()
    while change != 0:
        if change == 1:
            generate_card(card_pin)

        elif change == 2:
            log_in()

        change = main_menu()
    else:
        print(f"Bye!")
        exit()

main()

def print_BD():
    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM card ORDER BY id")
    resalt = cursor.fetchall()
    for i in resalt:
        print(i)

# print_BD()

def del_from_BD():
    conn = connect_to_tadabase()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM card")
    conn.commit()
    conn.close()
#
# del_from_BD()