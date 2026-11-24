from functools import wraps

from address_book import AddressBook, Record


def input_error(usage):
    expected_count = len(usage.split()) - 1

    def decorate(handler):
        @wraps(handler)
        def wrapper(args, book):
            if len(args) != expected_count:
                return f"Usage: {usage}"
            try:
                return handler(args, book)
            except KeyError as error:
                return f"Contact '{error.args[0]}' was not found."
            except ValueError as error:
                return str(error)

        return wrapper

    return decorate


@input_error("add <name> <phone>")
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error("change <name> <old-phone> <new-phone>")
def change_contact(args, book):
    name, old_phone, new_phone = args
    book[name].edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error("phone <name>")
def show_phone(args, book):
    record = book[args[0]]
    return ", ".join(map(str, record.phones)) or f"No phones for {record.name}."


@input_error("all")
def show_all(args, book):
    return "\n".join(map(str, book.values())) or "The address book is empty."


@input_error("add-birthday <name> <DD.MM.YYYY>")
def add_birthday(args, book):
    name, birthday = args
    book[name].add_birthday(birthday)
    return "Birthday saved."


@input_error("show-birthday <name>")
def show_birthday(args, book):
    record = book[args[0]]
    if record.birthday is None:
        return f"No birthday set for {record.name}."
    return f"{record.name}: {record.birthday}"


@input_error("birthdays")
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    return "\n".join(
        f"{entry['congratulation_date']}: {entry['name']}" for entry in upcoming
    ) or "No birthdays in the next seven days."


def parse_input(user_input):
    command, *args = user_input.split() or [""]
    return command.lower(), *args


def main():
    book = AddressBook()
    handlers = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }

    print("Welcome to the assistant bot!")
    while True:
        try:
            command, *args = parse_input(input("Enter a command: "))
        except (EOFError, KeyboardInterrupt):
            print("\nGood bye!")
            break

        if command in ("close", "exit"):
            if args:
                print(f"Usage: {command}")
                continue
            print("Good bye!")
            break
        if command == "hello":
            print("Usage: hello" if args else "How can I help you?")
        elif command in handlers:
            print(handlers[command](args, book))
        elif command:
            print("Invalid command.")


if __name__ == "__main__":
    main()
