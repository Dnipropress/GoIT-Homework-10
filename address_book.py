from collections import UserDict
from datetime import date, datetime, timedelta
import calendar
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if re.fullmatch(r"[0-9]{10}", value) is None:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            if re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", value) is None:
                raise ValueError
            parsed = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from None
        super().__init__(parsed)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        return next((entry for entry in self.phones if entry.value == phone), None)

    def remove_phone(self, phone):
        entry = self.find_phone(phone)
        if entry is None:
            raise ValueError(f"Phone number {phone} was not found.")
        self.phones.remove(entry)

    def edit_phone(self, old_phone, new_phone):
        entry = self.find_phone(old_phone)
        if entry is None:
            raise ValueError(f"Phone number {old_phone} was not found.")
        self.phones[self.phones.index(entry)] = Phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(map(str, self.phones)) or "none"
        birthday = str(self.birthday) if self.birthday else "not set"
        return f"{self.name} | Phones: {phones} | Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self[record.name.value] = record

    def find(self, name):
        return self.get(name)

    def delete(self, name):
        del self[name]

    def get_upcoming_birthdays(self, today=None):
        today = date.today() if today is None else today
        window = [today + timedelta(days=offset) for offset in range(7)]
        upcoming = []
        for record in self.values():
            if record.birthday is None:
                continue
            month = record.birthday.value.month
            day = record.birthday.value.day
            for candidate in window:
                anniversary_day = day
                if (month, day) == (2, 29) and not calendar.isleap(candidate.year):
                    anniversary_day = 28
                if (candidate.month, candidate.day) != (month, anniversary_day):
                    continue
                if candidate.weekday() >= 5:
                    candidate += timedelta(days=7 - candidate.weekday())
                upcoming.append((candidate, record.name.value))
                break

        return [
            {"name": name, "congratulation_date": day.strftime("%d.%m.%Y")}
            for day, name in sorted(upcoming)
        ]
