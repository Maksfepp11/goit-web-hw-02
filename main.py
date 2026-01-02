import pickle
from collections import UserDict
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod


class View(ABC):
    @abstractmethod
    def show_message(self, message: str):
        pass

    @abstractmethod
    def show_contacts(self, contacts: str):
        pass

    @abstractmethod
    def show_help(self):
        pass


class ConsoleView(View):
    def show_message(self, message: str):
        print(message)

    def show_contacts(self, contacts: str):
        print(contacts)

    def show_help(self):
        print("""
Available commands:
hello
add <name> <phone>
change <name> <old_phone> <new_phone>
phone <name>
all
add-birthday <name> <DD.MM.YYYY>
show-birthday <name>
birthdays
close / exit
""")


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must contain exactly 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def date_obj(self):
        return datetime.strptime(self.value, "%d.%m.%Y").date()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, ph in enumerate(self.phones):
            if ph.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone not found")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(ph.value for ph in self.phones)
        bday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{bday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self, days=7):
        result = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.date_obj().replace(year=today.year)
                if bday < today:
                    bday = bday.replace(year=today.year + 1)

                if 0 <= (bday - today).days <= days:
                    if bday.weekday() == 5:
                        bday += timedelta(days=2)
                    elif bday.weekday() == 6:
                        bday += timedelta(days=1)

                    result.append({
                        "name": record.name.value,
                        "congratulation_date": bday.strftime("%d.%m.%Y")
                    })
        return result

    def __str__(self):
        if not self.data:
            return "Address book is empty"
        return "\n".join(str(r) for r in self.data.values())


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def parse_input(user_input):
    parts = user_input.split()
    return parts[0].lower(), parts[1:]


def main():
    book = load_data()
    view = ConsoleView()

    view.show_message("Welcome to the assistant bot!")
    view.show_help()

    while True:
        command, args = parse_input(input(">>> "))

        try:
            if command in ("exit", "close"):
                save_data(book)
                view.show_message("Good bye!")
                break

            elif command == "hello":
                view.show_message("How can I help you?")

            elif command == "add":
                name, phone = args
                record = book.find(name)
                if not record:
                    record = Record(name)
                    book.add_record(record)
                record.add_phone(phone)
                view.show_message("Contact added.")

            elif command == "change":
                name, old_phone, new_phone = args
                record = book.find(name)
                if not record:
                    raise ValueError("Contact not found")
                record.edit_phone(old_phone, new_phone)
                view.show_message("Phone updated.")

            elif command == "phone":
                name = args[0]
                record = book.find(name)
                if not record:
                    raise ValueError("Contact not found")
                view.show_message("; ".join(p.value for p in record.phones))

            elif command == "all":
                view.show_contacts(str(book))

            elif command == "add-birthday":
                name, bday = args
                record = book.find(name)
                if not record:
                    raise ValueError("Contact not found")
                record.add_birthday(bday)
                view.show_message("Birthday added.")

            elif command == "show-birthday":
                name = args[0]
                record = book.find(name)
                if not record or not record.birthday:
                    view.show_message("No birthday set.")
                else:
                    view.show_message(record.birthday.value)

            elif command == "birthdays":
                upcoming = book.get_upcoming_birthdays()
                if not upcoming:
                    view.show_message("No upcoming birthdays.")
                else:
                    for u in upcoming:
                        view.show_message(f"{u['name']}: {u['congratulation_date']}")

            else:
                view.show_message("Invalid command.")

        except Exception as e:
            view.show_message(f"Error: {e}")


if __name__ == "__main__":
    main()
