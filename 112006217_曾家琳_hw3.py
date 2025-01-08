import os
import sys

def title():
    '''Welcome to Money Record!'''
print(title.__doc__)

class Categories:
    def __init__(self):
        '''
        self initialize 
        '''
        self.categories = self.initialize_categories()

    def initialize_categories(self):
        '''
        initialize categories in nested lists
        '''
        return ['expense', ['food', ['meal', 'snack', 'drink'], 'transportation', ['bus', 'railway']], 'income', ['salary', 'bonus']]

    def view_categories(self, categories, level=0):
        '''
        print all available categories
        '''
        if isinstance(categories, list):
            for category in categories:
                (lambda cat, lvl: self.view_categories(cat, lvl + 1) if isinstance(cat, list) else print('  ' * lvl + '- ' + cat))(category, level)
        else:
            print('  ' * level + '- ' + categories)

    def storage_for_categories(self, category, categories):
        '''
        determine whether a specific category exists within a nested list of categories
        '''
        if isinstance(categories, list):
            for subcategory in categories:
                if self.storage_for_categories(category, subcategory):
                    return True
        return categories == category

    def find_subcategories(self, category):
        '''
        find subcategories using a generator w12
        '''
        def find_subcategories_gen(category, categories, found=False):
            if isinstance(categories, list):
                for index, child in enumerate(categories):
                    yield from find_subcategories_gen(category, child, found)
                    if child == category and index + 1 < len(categories) and isinstance(categories[index + 1], list):
                        yield from find_subcategories_gen(category, categories[index + 1], True)
            else:
                if categories == category or found:
                    yield categories

        return list(find_subcategories_gen(category, self.categories))


class Record:
    def __init__(self, category, description, amount):
        '''
        initialize private var
        '''
        self._category = category
        self._description = description
        self._amount = amount

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def amount(self):
        return self._amount


class Records:
    def __init__(self, initial_amount, filename):
        '''
        self initialize private var inside class for user input data
        '''
        self._data_storage = {}
        self._key_counter = 0
        self._filename = filename
        self._start_money = initial_amount
        self._user_name = ""

    @property
    def start_money(self):
        return self._start_money

    @start_money.setter
    def start_money(self, value):
        self._start_money = value
    @property
    def user_name(self):
        pass
    
    @user_name.getter
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        self._user_name = value

    def store(self, record):
        '''
        store data record while keeping in track of counter for deletion
        '''
        self._data_storage[self._key_counter] = record
        self._start_money += record.amount
        self._key_counter += 1

    def view(self):
        '''
        print all curr inp data
        '''
        print(f"Current total money: {self._start_money} dollars.")
        print("=" * 40)
        print("Category       Description          Amount")
        print("=============== ==================== ======")
        records = [
            f"{record.category:<15} {record.description:<20} {record.amount:>6}"
            for record in self._data_storage.values()
        ]
        print("\n".join(records))
        print("===========================================")

    def add(self, input_data, categories):
        '''
        add new data 
        '''
        try:
            entries = input_data.split(',')
            for entry in entries:
                entry = entry.strip()
                category, desc, amount = entry.split(" ")
                amount = int(amount)
                if not categories.storage_for_categories(category, categories.categories):
                    print("The specified category is not in the category list.")
                    return
                record = Record(category, desc, amount)
                self.store(record)
        except ValueError:
            sys.stderr.write("Fail to add a record. Correct format should be (e.g., 'food breakfast -50').\n")

    def find(self, category, categories):
        '''
        find category or subcategory 
        '''
        if not categories.storage_for_categories(category, categories.categories):
            print("!!! category not found !!!")
            return
        
        subcategories = categories.find_subcategories(category)
        filtered_records = [record for record in self._data_storage.values() if record.category in subcategories]
        total = sum(record.amount for record in filtered_records)

        print(f"Records in category '{category}':")
        print("Category       Description          Amount")
        print("=============== ==================== ======")
        for record in filtered_records:
            print(f"{record.category:<15} {record.description:<20} {record.amount:>6}")
        print("===========================================")
        print(f"Total amount: {total}")
    
    def delete(self, key_del):
        '''
        delete certain data inp
        '''
        try:
            record = self._data_storage.pop(key_del)
            self._start_money -= record.amount
            print(f"Key {key_del} deleted.")
        except KeyError:
            sys.stderr.write("Key does not exist. Nothing was deleted.\n")

    def delete_all_data(self):
        '''
        rewrite all data with blank
        '''
        self._data_storage.clear()
        self._start_money = 0
        self._key_counter = 0
        self._user_name = ""
        with open(self._filename, 'w') as file:
            file.write("")
        print("All data deleted successfully.")

    def save(self):
        '''
        label method to ensure data is saved to file 
        '''
        try:
            lines = [f"{self._start_money}\n"]
            for key, record in self._data_storage.items():
                lines.append(f"{key} {record.category} {record.description} {record.amount}\n")
            lines.append(f"username: {self._user_name}\n")
            with open(self._filename, "w") as file:
                file.writelines(lines)
            print(f"Data saved to {self._filename}.")
        except Exception as e:
            sys.stderr.write(f"Error while saving to file: {e}\n")

    def initiate_file(self):
        '''
        to open file (if exist previously)
        '''
        try:
            if not os.path.exists(self._filename):
                print(f"No file found at {self._filename}")
                return

            with open(self._filename, "r") as file:
                total_money_line = file.readline().strip()
                if not total_money_line.isdigit():
                    sys.stderr.write("!!! - !!! Error: First line should be an integer representing total money.\n")
                    return
                self._start_money = int(total_money_line)

                remaining_lines = file.readlines()

            self._data_storage.clear()

            for record in remaining_lines:
                record = record.strip()
                if not record:
                    continue

                if record.startswith("username:"):
                    self._user_name = record.split(": ", 1)[1] if len(record) > 10 else ""
                else:
                    try:
                        key, category, desc, amount = record.split(" ", 3)
                        self._data_storage[int(key)] = Record(category, desc, int(amount))
                    except ValueError:
                        sys.stderr.write(f"!!! - !!! Error: File data format is incorrect at line: '{record}'\n")
                        return

            self._key_counter = len(self._data_storage)
        except FileNotFoundError:
            print(f"!!! - !!! File not found: {self._filename}")
        except PermissionError:
            sys.stderr.write(f"!!! - !!! Error: Permission denied when accessing {self._filename}.\n")
        except Exception as e:
            sys.stderr.write(f"!!! - !!! Error while reading file: {e}\n")
        finally:
            print(f"Data loaded from {self._filename}.")

    def change_username(self, new_username):
        '''
        change username 
        '''
        """Change the username."""
        self.user_name = new_username
        print(f"Username changed to: {self.user_name}")

# initialize categories and setup
call_categories = Categories()
categories = call_categories.categories
my_local_file = "records.txt"
call_records = Records(0, my_local_file)
call_records.initiate_file()

if call_records.start_money == 0:
    initial_amount = int(input(">>> Initial money is 0, How much money do you have? "))
    call_records.start_money = initial_amount

if call_records.user_name == "":
    user_name = input(">>> What is your name? ")
    call_records.user_name = user_name
else:
    print(f"Welcome back, {call_records.user_name}!")

# main interactive loop
while True:
    print("-" * 40)
    print("What do you want to do (add / view / delete / delete all / view categories / find / change username / exit)?")
    choice_input = input(">>> Enter code: ").strip()

    if choice_input not in ["a", "f", "v", "d", "da", "ca", "e", "vc"]:
        sys.stderr.write("!!! - !!! Invalid choice. Valid options: (a: add / v: view / d: delete / da: delete all / e: exit / ca: change name, f: find, vc: view categories)\n")
        continue

    if choice_input == "e":
        call_records.save()
        break
    elif choice_input == "f":
        category = input(">>> Which category do you want to find? ")
        call_records.find(category, call_categories)

    elif choice_input == "vc":
        call_categories.view_categories(categories)

    elif choice_input == "a":
        input_data = input(">>> Add expense/income records (e.g., 'meal breakfast -50'): ")
        call_records.add(input_data, call_categories)

    elif choice_input == "v":
        print("Here's your expense and income records: ")
        call_records.view()

    elif choice_input == "d":
        print("======= CHOOSE A KEY LIST TO DELETE =======")
        for index, (key, record) in enumerate(call_records._data_storage.items()):
            print(f"{index + 1}. Key: {key}, Category: {record.category}, Description: {record.description}, Amount: {record.amount}")

        if len(call_records._data_storage) == 0:
            print("!!! - !!! NO KEY AVAILABLE")
            continue

        while True:
            try:
                key_del = int(input(">>> Enter the key of the record you want to delete: "))
                call_records.delete(key_del)
                break
            except ValueError:
                sys.stderr.write("Error: Invalid key format. Please enter a valid number.\n")
                continue
    elif choice_input == "da":
        while True:
            confirmation = input(">>> Are you sure you want to delete all records? [(y) to proceed/(n) to CANCEL]: ").strip().lower()
            if confirmation == "y":
                call_records.delete_all_data()
                break
            elif confirmation == "n":
                print("Deletion canceled. Returning to the menu.")
                break
            else:
                print("!!! - !!! Invalid choice. Please enter 'y' to proceed or 'n' to cancel.")

    elif choice_input == "ca":
        new_username = input(">>> Enter your new username (press \"c\" to cancel): ").strip()
        if new_username.lower() != "c":
            call_records.change_username(new_username)
