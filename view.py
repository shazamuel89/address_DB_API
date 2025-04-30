# Import statements
import controller
import sys
import os


# Classes
class Field:
    def __init__(self, key, prompt, dataType, viewValidator, controllerValidator, isRequired):
        self.key = key
        self.prompt = prompt
        self.dataType = dataType
        self.viewValidator = viewValidator
        self.controllerValidator = controllerValidator
        self.isRequired = isRequired


# Initialized variables
inputCodes = {
    'CANCEL':   '-1',
    'SKIP':     '-2',
}

outputStrings = {
    'INTRODUCTION': '''
Welcome to the Address API!
This tool is meant to be used for the storing and managing of the information for addresses on a mail route.
In this program, you can read existing address entries, create new address entries, update existing address entries, and delete existing address entries.
These address entries are saved to your local computer, and they can be retrieved after exiting this program.
''',
    'MENU': '''Please type a number corresponding to the following options:
1 - Read address entries
2 - Create a new address entry
3 - Update an existing address entry
4 - Delete an existing address entry
5 - Exit program
>>> ''',
    'BEGIN_CREATE':             "You have chosen to create a new address entry. (If at any time you would like to cancel the creation, enter -1.)",
    'BEGIN_UPDATE':             "You have chosen to update an existing address entry. (If at any time you would like to cancel the update, enter -1. If you would like to leave the address's field unchanged, enter -2.)",
    'BEGIN_DELETE':             "You have chosen to delete an existing address entry. (If you would like to cancel the deletion, enter -1.)",
    'CHOOSE_EXISTING_ADDRESS':  "Please enter the position number of an address from the above list: >>> ",
    'CANCEL_CREATE':            "The creation was cancelled.",
    'CANCEL_UPDATE':            "The update was cancelled.",
    'CANCEL_DELETE':            "The deletion was cancelled.",
    'CONFIRM_DELETE':           "Are you sure you want to delete this entry? (y/n): >>> ",
    'CONFIRM_EXIT':             "Are you sure you want to exit? (y/n): >>> ",
    'ADDRESS_CREATED':          "Address created:",
    'ADDRESS_UPDATED':          "Address updated:",
    'ADDRESS_DELETED':          "Address Deleted:",
}

errorOutputs = {
    'ADDRESS_NOT_FOUND':    "There is no address entry with that position! Please try again.",
    'ADDRESS_BOOK_EMPTY':   "There are no existing address entries yet! Please choose another option.",
    'MISSING_FIELD':        "A field is missing data!",
    'INVALID_INPUT':        "That is not a valid input. Please try again.",
    'INVALID_SECTION':      "The section number is invalid because it is not within the sections of the address before or after it.",
}

addressFields = [
    Field(
        'addressNumber',
        "Please enter the address number: >>> ",
        int,
        lambda x: 0 < x,
        controller.fieldValidators['addressNumber'],
        True
    ),
    Field(
        'street',
        "Please enter the street name including the street suffix (St, Rd, Ln, etc.): >>> ",
        str,
        lambda x: 0 < len(x),
        controller.fieldValidators['street'],
        True
    ),
    Field(
        'unit',
        "Please enter the apt/lot/unit number (if N/A, then simply press the enter key without typing anything): >>> ",
        str,
        lambda x: 0 < len(x),
        controller.fieldValidators['unit'],
        False
    ),
    Field(
        'names',
        "Please enter one name that receives mail here (you must provide at least one name, and if you are finished entering names, simply press the enter key without typing anything): >>> ",
        (list, str),
        lambda x: (len(x) > 0) and all(len(item) > 0 for item in x),
        controller.fieldValidators['names'],
        True
    ),
    Field(
        'position',
        "Please enter a positive number representing the position of this address in the route order: >>> ",
        int,
        lambda x: 0 < x,
        controller.fieldValidators['position'],
        True
    ),
    Field(
        'section',
        "Please enter a positive number representing the route's section that this address is on: >>> ",
        int,
        lambda x: 0 < x,
        controller.fieldValidators['section'],
        True
    ),
    Field(
        'isBusiness',
        "Is this a business or a residential address? Enter 1 for BUSINESS, and 0 for RESIDENTIAL: >>> ",
        bool,
        None,
        controller.fieldValidators['isBusiness'],
        True
    ),
    Field(
        'isCBU',
        "Is this address's mail delivered to a CBU (Centralized Box Unit)? Enter 1 for YES, and 0 for NO: >>> ",
        bool,
        None,
        controller.fieldValidators['isCBU'],
        True
    ),
    Field(
        'isVacant',
        "Is this address currently vacant? Enter 1 for YES, and 0 for NO: >>> ",
        bool,
        None,
        controller.fieldValidators['isVacant'],
        True
    ),
]


# Functions
# This function returns a dictionary containing the data for a new address entry
# It gets input from the user for each field and uses controller functions to validate the input before moving on to the next field
def print_all_addresses():
    addressesRead = controller.read_all_addresses()
    if (addressesRead['success']):
        print(output_address_book(addressesRead['result']))
        return True
    else:
        print(errorOutputs[addressesRead['errorType']])
        return False


def get_input_for_address_create():
    data = {}
    for field in addressFields:
        while True:
            userInput = get_input_for_field(field)
            if (userInput == -1):
                return None
            validInput = True
            if ((not userInput) and (not field.isRequired)):
                data[field.key] = None
                break
            userInput = convert_input(field.dataType, userInput)
            if (not userInput):
                validInput = False
            if (not validate_field(field, userInput)):
                validInput = False
            if (not validInput):
                print(errorOutputs['INVALID_INPUT'])
                continue
            data[field.key] = userInput
            break
    data = validate_context(data, method = 'create')
    return data


def get_input_for_address_update(positionToUpdate):
    findAddressToUpdate = controller.read_single_address(positionToUpdate)
    if (not findAddressToUpdate['success']):
        return False
    data = findAddressToUpdate['result']
    for field in addressFields:
        while True:
            userInput = get_input_for_field(field)
            if (userInput.upper() == inputCodes['CANCEL']):
                return None
            if (userInput.upper() == inputCodes['SKIP']):
                break
            validInput = True
            if ((not userInput) and (not field.isRequired)):
                data[field.key] = None
                break
            userInput = convert_input(field.dataType, userInput)
            if (userInput is None):
                validInput = False
            if (not validate_field(field, userInput)):
                validInput = False
            if (not validInput):
                print(errorOutputs['INVALID_INPUT'])
                continue
            data[field.key] = userInput
            break
    data = validate_context(data, method = 'update', initialPosition = positionToUpdate)
    return data


def get_input_for_field(field):
    if (isinstance(field.dataType, tuple)):
        userInput = []
        while True:
            item = input(field.prompt)
            if (item == ''):
                break
            item = item.strip()
            if ((item.upper() == inputCodes['CANCEL']) or (item.upper() == inputCodes['SKIP'])):
                return item
            userInput.append(item)
    else:
        userInput = input(field.prompt) # Outputting the prompt for this field and getting the user's input
        userInput = userInput.strip()   # Stripping whitespace from the user input
    return userInput


def convert_input(dataType, userInput):
    try:
        if (isinstance(dataType, tuple)):
            newInput = dataType[0]()
            for item in userInput:
                newInput.append(dataType[1](item))
        elif (dataType is bool):
            if (userInput == '1'):
                newInput = True
            elif (userInput == '0'):
                newInput = False
            else:
                raise ValueError
        else:
            newInput = dataType(userInput)   # Converting the user input to the correct datatype
    except ValueError:
        return None
    return newInput


def validate_field(field, userInput):
    if (field.viewValidator and not field.viewValidator(userInput)):
        return False
    if (field.controllerValidator and not field.controllerValidator(userInput)):
        return False
    return True


def validate_context(data, method = 'create', initialPosition = None):
    for field in addressFields:
        if (field.key == 'section'):
            sectionField = field
            break
    if (method == 'create'):
        validate_section_context = controller.validate_section_context_create
    else:
        validate_section_context = lambda data: controller.validate_section_context_update(data, initialPosition = initialPosition)
    if (validate_section_context(data)):
        return data
    print(errorOutputs['INVALID_SECTION'])
    while True:
        sectionInput = input(sectionField.prompt).strip()
        sectionInput = convert_input(sectionField.dataType, sectionInput)
        if (not sectionInput):
            print(errorOutputs['INVALID_INPUT'])
            continue
        data['section'] = sectionInput
        if (not validate_section_context(data)):
            print(errorOutputs['INVALID_SECTION'])
            continue
        break
    return data


def get_existing_address_choice():
    while True:
        choice = input(outputStrings['CHOOSE_EXISTING_ADDRESS'])
        if (choice.upper() == inputCodes['CANCEL']):
            return None
        if (controller.read_single_address(choice)['success']):
            return choice
        print(errorOutputs['ADDRESS_NOT_FOUND'])


def output_address(addressData):
    leftWidth = 20
    rightWidth = 30
    separator = '_'
    addressString = ''
    for key, value in addressData.items():
        if (value == None):
            addressString += (key.ljust(leftWidth, separator) + "N/A".rjust(rightWidth, separator) + '\n')
        elif (isinstance(value, list)):
            listString = '/'.join(str(item) for item in value)
            addressString += (key.ljust(leftWidth, separator) + listString.rjust(rightWidth, separator) + '\n')
        else:
            addressString += (key.ljust(leftWidth, separator) + str(value).rjust(rightWidth, separator) + '\n')
    return addressString


def output_address_book(addressesData):
    if (not addressesData):
        return {}
    separator = '-' * 50
    addressBookString = ''
    for address in addressesData:
        addressBookString += output_address(address)
        addressBookString += '\n' + separator + '\n'
    return addressBookString


def clear_console():
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')


# Beginning execution of main program
print(outputStrings['INTRODUCTION'])
while (True):
    choice = input(outputStrings['MENU']).strip()
    match choice:
        case '1': # Read address entries
            print_all_addresses()
        case '2': # Create a new address entry
            clear_console()
            print(outputStrings['BEGIN_CREATE'])
            addressData = get_input_for_address_create()
            if (not addressData):
                print(outputStrings['CANCEL_CREATE'])
                continue
            addressCreate = controller.create_address(addressData)
            if (addressCreate['success']):
                print(outputStrings['ADDRESS_CREATED'])
                print(output_address(addressCreate['result']))
            else:
                print(errorOutputs[addressCreate['errorType']])
        case '3': # Update an existing address entry
            clear_console()
            addressBookRead = print_all_addresses()
            if (not addressBookRead):
                continue
            print(outputStrings['BEGIN_UPDATE'])
            positionToUpdate = get_existing_address_choice()
            if (not positionToUpdate):
                print(outputStrings['CANCEL_UPDATE'])
                continue
            findAddressToUpdate = controller.read_single_address(positionToUpdate)
            if (findAddressToUpdate['success'] == False):
                print(errorOutputs[findAddressToUpdate['errorType']])
                continue
            print(output_address(findAddressToUpdate['result']))
            addressData = get_input_for_address_update(positionToUpdate)
            if (not addressData):
                print(outputStrings['CANCEL_UPDATE'])
                continue
            addressUpdate = controller.update_address(addressData, positionToUpdate)
            if (addressUpdate['success']):
                print(outputStrings['ADDRESS_UPDATED'])
                print(output_address(addressUpdate['result']))
            else:
                print(errorOutputs[addressUpdate['errorType']])
        case '4': # Delete an existing address entry
            clear_console()
            addressBookRead = print_all_addresses()
            if (not addressBookRead):
                continue
            print(outputStrings['BEGIN_DELETE'])
            positionToDelete = get_existing_address_choice()
            if (not positionToDelete):
                print(outputStrings['CANCEL_DELETE'])
                continue
            findAddressToDelete = controller.read_single_address(positionToDelete)
            if (findAddressToDelete['success'] == False):
                print(errorOutputs[findAddressToDelete['errorType']])
                continue
            print(output_address(findAddressToDelete['result']))
            confirmation = input(outputStrings['CONFIRM_DELETE'])
            if (not (confirmation.upper() == 'Y')):
                print(outputStrings['CANCEL_DELETE'])
                continue
            addressDelete = controller.delete_address(positionToDelete)
            if (addressDelete['success']):
                print(outputStrings['ADDRESS_DELETED'])
                print(output_address(addressDelete['result']))
            else:
                print(errorOutputs[addressDelete['errorType']])
        case '5': # Exit program
            exitInput = input(outputStrings['CONFIRM_EXIT'])
            if (exitInput.strip().upper() == 'Y'):
                break
        case _:
            print(errorOutputs['INVALID_INPUT'])
            continue