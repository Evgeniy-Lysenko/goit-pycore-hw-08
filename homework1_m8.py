# Модуль 7 система для управління адресною книгою.
from collections import UserDict
from datetime import date, datetime, timedelta 
import pickle

class Field: # class for working with fields
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field): # class for working with names
    def __init__(self, value):
        if not value:
            raise ValueError("Name is required")
        super().__init__(value)


class Phone(Field): # class for working with phone numbers
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
   
    def __str__(self):
        return self.value
        
class Record: # class for working with records
    def __init__(self, name): 
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday): # add birthday to the record self.birthday = add_birthday
        self.birthday = Birthday(birthday)
        
    def add_phone(self, phone): # add phone to the record
        self.phones.append(Phone(phone))

    def remove_phone(self, phone): # remove phone from the record
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone not found")

    def edit_phone(self, old_phone, new_phone): # edit phone in the record
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Old phone not found")
        phone_obj.value = Phone(new_phone).value

    def find_phone(self, phone): # find phone in the record
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday if self.birthday else 'Not set'}"


class AddressBook(UserDict): # class for working with address book
    def add_record(self, record): # add record to the address book
        self.data[record.name.value] = record

    def find(self, name): # find record in the address book
        return self.data.get(name)

    def delete(self, name): # delete record from the address book
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")
    
    def find_next_weekday(self, start_date, weekday): # find next weekday
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)


    def adjust_for_weekend(self, birthday): # adjust birthday for weekend
        if birthday.weekday() >= 5:
            return  self.find_next_weekday(birthday, 0)  # 0 - понеділок
        return birthday

    def get_upcoming_birthdays(self, days=7): # get upcoming birthdays
        upcoming_birthdays = []
        today = date.today()    
        for contact_b in self.data.values():
            if not contact_b.birthday:
                continue
            
            birthday_date = datetime.strptime(contact_b.birthday.value, "%d.%m.%Y").date()

            birthday_this_year = birthday_date.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1) # Перевірка, чи не буде припадати день народження вже наступного року

            if 0 <= (birthday_this_year - today).days <= days:
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)
                congratulation_date_str = birthday_this_year.strftime("%d.%m.%Y")
                
                upcoming_birthdays.append({"name": contact_b.name.value, "birthday": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self): # string representation of the address book
        return "\n".join(str(record) for record in self.data.values())




def input_error(func): # decorator for error handling
    def inner(*args, **kwargs): # inner function to wrap the original function
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format."
        except AttributeError:
            return "Contact not found."

    return inner


def parse_input(user_input): # parse the input
    cmd, *args = user_input.split() # split the input into command and arguments
    cmd = cmd.strip().lower() # remove leading and trailing whitespace and convert to lowercase
    return cmd, args

@input_error
def add_contact(args, book: AddressBook): # add contact
    if len(args) < 2:
        raise ValueError("Name and phone are required")
    name = args[0]
    phone = args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook): # change contact phone
    if len(args) < 3:
        raise ValueError("Name old phone and new phone are required")
    name, old_phone, new_phone = args[0], args[1], args[2]
    record = book.find(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def add_birthday(args, book: AddressBook): # add birthday
    if len(args) < 2:
        raise ValueError("Name and birthday are required")
    name, birthday = args[0], args[1]
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."
 
@input_error    
def contact_phone(args, book: AddressBook):# get contact phone
    if len(args) < 1:
        raise ValueError("Name is required")   
    name = args[0]
    record = book.find(name)
    if not record.phones:
        return "No phones found for this contact."
    return "; ".join(p.value for p in record.phones) # return all phones

@input_error  
def show_birthday(args, book: AddressBook): # get contact birthday
    if len(args) < 1:
        raise ValueError("Name is required")
    name = args[0]
    record = book.find(name)
    if not record.birthday:
        return "Birthday not set for this contact."
    return str(record.birthday)

def all_contacts(book: AddressBook): # get all contacts
    if not book.data: # check if contacts dictionary is empty
       return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values()) # return all sorted contacts

@input_error
def birthdays(book: AddressBook): # get upcoming birthdays
    result = book.get_upcoming_birthdays()
    if not result:
        return "No upcoming birthdays."
    return "\n".join(
    f"{item['name']} - congratulations day: {item['birthday']}"
    for item in result
)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print ("Адресна книга  не знайдена. Будет створена нова.")
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def help_command(): # help command
    return ("Available commands:\n"
            "__________________________________________\n"
            "hello - Greet the bot\n"
            "add <name> <phone> - Add a contact\n"
            "change <name> <old_phone> <new_phone> - Change contact's phone number\n"
            "phone <name> - Get contact's phone numbers\n"
            "all - Show all contacts\n"
            "add-birthday <name> <birthday> - Add birthday to a contact\n"
            "show-birthday <name> - Show birthday of a contact\n"
            "birthdays - Show upcoming birthdays\n"
            "close/exit - Exit the bot")


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command (For help, type 'h' or '?'): ").strip() # get user input
        if not user_input: # check for empty input
            print("Please enter a command. ")
            continue

        command, args = parse_input(user_input) # parse the input

        if command in ["close", "exit", "q"]: # exit commands
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello": # hello command
            print("How can I help you?")
        elif command in ["?", "h"]: # help command
            print(help_command()) # print help message
        elif command == "add": # add command
            print(add_contact(args, book))
        elif command == "change": # change command
            print(change_contact(args, book))
        elif command == "phone": # phone command
            print(contact_phone(args, book))
        elif command == "all": # all command
            print(all_contacts(book))
        elif command == "add-birthday": # add birthday command
            print(add_birthday(args, book))
        elif command == "show-birthday": # show birthday command
            print(show_birthday(args, book))
        elif command == "birthdays" : # show upcoming birthdays command
            print(birthdays(book))

        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()


