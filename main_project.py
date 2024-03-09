from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle
from colorama import Fore, Style


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        number_pattern = r"\b\d{10}\b"
        if re.match(number_pattern, value):
            super().__init__(value)
        else:
            count_figures = len(value)
            print(f"Number - {value} - incorrect, it has {count_figures} figures")
            self.value = None
            if self.value is None:
                exit()

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            date_pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')
            if date_pattern.match(value):
                self.value = datetime.strptime(value, "%d.%m.%Y").date()

        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class BirthdayBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_birthday(self, name, birthday):
        if isinstance(birthday, Birthday):
            self.data[name] = birthday
            return f"Birthday was successfully added for '{name}'"
        else:
            return f"Invalid birthday format for '{name}'. Please provide a valid Birthday object."

    def find_birthday(self, name):
        return self.data.get(name, None)

    def remove_birthday(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            return f"Birthday for {name} not found in Birthday book."

    def show_all_birthdays(self):
        if not self.data:
            return "There are no birthdays in the Birthday book."

        result = "\n>>> All Birthdays:\n"
        for name, birthday in self.data.items():
            result += f"'name': {name}, 'birthday': {birthday}\n"

        return result

    def get_upcoming_birthdays(self):
        dict_with_dates_for_ones = {}
        current_day = datetime.now().date()
        current_week_start = current_day - timedelta(days=current_day.weekday())  # Start of the current week

        for name, birthday in self.data.items():

            formatted_date_birthday = datetime(current_day.year, birthday.value.month, birthday.value.day).date()

            difference = formatted_date_birthday - current_day

            if 0 <= difference.days < 7 and formatted_date_birthday.weekday() in [0, 1, 2, 3, 4]:
                dict_with_dates_for_ones[name] = formatted_date_birthday.strftime("%Y.%m.%d")
            elif difference.days < 0 and formatted_date_birthday.weekday() not in [5, 6]:
                continue
            else:  # If it falls on Saturday or Sunday
                days_until_monday = 7 - formatted_date_birthday.weekday()
                formatted_date_birthday += timedelta(days=days_until_monday)
                dict_with_dates_for_ones[name] = formatted_date_birthday.strftime("%Y.%m.%d")

        return dict_with_dates_for_ones


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.book = None

    def add_phone(self, phone):
        try:
            phone_instance = Phone(phone)
            if len(self.phones) == 0 or phone_instance not in self.phones:
                self.phones.append(phone_instance)
                return f"Contact '{self.name}' added."
        except ValueError as e:
            return str(e)

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, phone_old, phone_new):
        old_number = Phone(phone_old)
        new_number = Phone(phone_new)
        if old_number.value in [phone.value for phone in self.phones] and new_number not in self.phones:
            idx = [phone.value for phone in self.phones].index(old_number.value)
            self.phones[idx] = new_number
            return f"Contact '{self.name}' changed."
        else:
            return f"Such number {phone_old} isn't in Address book"

    def show_all(self):
        if self.phones:
            result = f"👤Contact:{self.name}"
            for phone in self.phones:
                result += f"  📲Phone: {phone}"

            return result

        else:
            return f"No phones for contact '{self.name}'."

    def __str__(self):
        return f"👤 Contact name: {self.name.value}, 📲 phone: {'; '.join(map(str, self.phones))}"


class AddressBook(UserDict):
    def __init__(self, data=None):
        if data is None:
            data = {}
        super().__init__(data)

    def add_record(self, record):
        self.data[record.name.value] = record
        print(f"Contact {record.name.value} added.")

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            return f"Record for {name} not found in Address book."

    def get_upcoming_birthdays(self, birthday_book):
        return birthday_book.get_upcoming_birthdays()


def save_data(book):
    path_book = "addressbook.pkl"
    with open(path_book, 'wb') as file:
        pickle.dump(book.data, file)


def load_data():
    path_book = "addressbook.pkl"
    try:
        with open(path_book, "rb") as f:
            data = pickle.load(f)
            return AddressBook(data)
    except FileNotFoundError:
        return AddressBook()


def print_address_book_data(address_book):
    if address_book.data:
        print(f"{Fore.GREEN}\n\tAddress Book:{Style.RESET_ALL}")
        for name, record in address_book.data.items():
            print(record.show_all())
            print(f"{Fore.GREEN}{'-' * 40}{Style.RESET_ALL}")
    else:
        print("No records found in the address book.")


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            error_messages = {
                KeyError: "Contact not found.",
                ValueError: "Invalid input.",
                IndexError: "Invalid input. Please provide the name."
            }
            return error_messages.get(type(e), "An error occurred.")

    return inner


def main():
    address_book = load_data()
    birthday_book = BirthdayBook()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("\nEnter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            save_data(address_book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            record_instance = Record(args[0])
            result = record_instance.add_phone(args[1])
            if result.startswith("Contact"):
                record_instance.book = address_book.data
                address_book.add_record(record_instance)
                save_data(address_book)

        elif command == "change":
            record_instance = address_book.find(args[0])
            if record_instance is not None:
                print(record_instance.edit_phone(args[1], args[2]))
                save_data(address_book)
            else:
                print(f"Record for {args[0]} not found in Address book.")

        elif command == "phone":
            record_instance = address_book.find(args[0])
            if record_instance is not None:
                print(record_instance)
            else:
                print(f"Record for {args[0]} not found in Address book.")

        elif command == "all":
            print_address_book_data(address_book)


        elif command == "del":
            address_book.delete(args[0])
            save_data(address_book)

        elif command == "add-birthday":
            try:
                record_name, birthday = args
            except ValueError:
                print("Invalid input for 'add-birthday' command. Please provide both the name and birthday.")
                continue  # Restart the loop to get another user input
            record = address_book.find(record_name)
            if record is None:
                print(f"Contact '{record_name}' not found.")
            else:
                birthday_instance = Birthday(birthday)
                birthday_book.add_birthday(record_name, birthday_instance)
                print(f"Birthday for '{record_name}' added.")

        elif command == "show-birthday":
            record_name = args[0]
            record = address_book.find(record_name)
            if record is None:
                print(f"Contact '{record_name}' not found.")
            elif isinstance(record, str):
                print(f"Invalid contact name: '{record_name}'.")
            else:
                birthday = birthday_book.find_birthday(record_name)
                if birthday is None:
                    print(f"No birthday found for '{record_name}'.")
                else:
                    print(f"Birthday day for '{record_name}' ---> {birthday}")

        elif command == "birthdays":
            print(birthday_book.show_all_birthdays())
            print(f"{Fore.MAGENTA}>>> List of upcoming birthdays this week:{Style.RESET_ALL}")
            upcoming_birthdays = address_book.get_upcoming_birthdays(birthday_book)
            for name, congrat in upcoming_birthdays.items():
                print(f"* 🎂 {name}, {congrat}")

        else:
            print("Invalid command.")

    save_data(address_book)


if __name__ == "__main__":
    main()
