# Imports for built in modules
import sys
import os
import logging

# Logging configuration
''' Format example:
myFile.py   at line 17  (DEBUG):
    lookup_address()    -   No address was found at position 7.
'''
logging.basicConfig(filename='logFile.txt', level=logging.DEBUG, format='%(filename)s\tat line %(lineno)s\t(%(levelname)s):\n\t%(funcName)s()\t-\t%(message)s\n')

# Imports for custom modules
try:
    import controller
    logging.debug("controller.py loaded successfully.")
except:
    print("controller.py is missing! Program will now exit. (Please ensure you have controller.py in the same directory as this python script.)")
    logging.critical("controller.py is missing! Program will now exit. (Please ensure you have controller.py in the same directory as this python script.)")
    sys.exit(1)


# Classes
class Field:
    def __init__(self, key, prompt, dataType, viewValidator, controllerValidator, isRequired):
        self.key = key
        self.prompt = prompt
        self.dataType = dataType
        self.viewValidator = viewValidator
        self.controllerValidator = controllerValidator
        self.isRequired = isRequired
        logging.info(f"Created field object with properties:\n\t\tkey: {key}\n\t\tprompt: {prompt}\n\t\tdataType: {dataType}\n\t\tviewValidator: {viewValidator}\n\t\tcontrollerValidator: {controllerValidator}\n\t\tisRequired: {isRequired}")


# Global variables
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
    'MENU': '''
Please type a number corresponding to the following options:
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
    logging.debug("Beginning function execution.")
    addressesRead = controller.read_all_addresses()
    if (addressesRead['success']):
        logging.info("Since the addresses read was a success, returning True.")
        print(output_address_book(addressesRead['result']))
        return True
    else:
        logging.warning(f"Since the addresses read was a failure, returning False. Error info: {errorOutputs[addressesRead['errorType']]}")
        print(errorOutputs[addressesRead['errorType']])
        return False

def get_input_for_address_create():
    logging.debug("Beginning function execution.")
    data = {}
    for field in addressFields:
        while True:
            userInput = get_input_for_field(field)
            logging.info(f"userInput is {userInput}")
            if ((isinstance(userInput, str)) and (userInput.upper() == inputCodes['CANCEL'])):
                logging.info(f"User entered the cancel code - returning None to cancel the creation.")
                return None
            validInput = True
            if ((not userInput) and (not field.isRequired)):
                logging.debug(f"Since userInput is empty, and this field is not required, setting {field.key} to None and moving on to the next field.")
                data[field.key] = None
                break
            userInput = convert_input(field.dataType, userInput)
            logging.info(f"Result of calling convert_input(): {userInput}")
            if (userInput is None):
                logging.debug("userInput could not be converted, so setting validInput to False.")
                validInput = False
            elif (not validate_field(field, userInput)):
                logging.debug("userInput could not be validated on the field's constraints, so setting validInput to False.")
                validInput = False
            if (not validInput):
                logging.debug("Since the userInput was not valid, restarting input loop.")
                print(errorOutputs['INVALID_INPUT'])
                continue
            logging.info(f"Setting {field.key} to {userInput}.")
            data[field.key] = userInput
            break
    data = validate_context(data, method = 'create')
    logging.info(f"Final result of data after calling validate_context(): {data}")
    return data

def get_input_for_address_update(positionToUpdate):
    logging.debug(f"Beginning function execution with positionToUpdate = {positionToUpdate}.")
    findAddressToUpdate = controller.read_single_address(positionToUpdate)
    if (not findAddressToUpdate['success']):
        logging.debug("Since the address to update was not found, returning False")
        return False
    data = findAddressToUpdate['result']
    logging.info(f"Current information of the address that is about to be updated: {data}")
    for field in addressFields:
        while True:
            userInput = get_input_for_field(field)
            logging.info(f"userInput is {userInput}")
            if ((isinstance(userInput, str)) and (userInput.upper() == inputCodes['CANCEL'])):
                logging.info("User entered the cancel code - returning None to cancel the update.")
                return None
            if ((isinstance(userInput, str)) and (userInput.upper() == inputCodes['SKIP'])):
                logging.debug("User entered the skip code - breaking the loop for this field's input.")
                break
            validInput = True
            if ((not userInput) and (not field.isRequired)):
                logging.debug(f"Since userInput is empty, and this field is not required, setting {field.key} to None and moving on to the next field.")
                data[field.key] = None
                break
            userInput = convert_input(field.dataType, userInput)
            logging.info(f"Result of calling convert_input(): {userInput}")
            if (userInput is None):
                logging.debug("userInput could not be converted, so setting validInput to False.")
                validInput = False
            elif (not validate_field(field, userInput)):
                logging.debug("userInput could not be validated on the field's constraints, so setting validInput to False.")
                validInput = False
            if (not validInput):
                logging.debug("Since the userInput was not valid, restarting input loop.")
                print(errorOutputs['INVALID_INPUT'])
                continue
            logging.info(f"Setting {field.key} to {userInput}.")
            data[field.key] = userInput
            break
    data = validate_context(data, method = 'update', initialPosition = positionToUpdate)
    logging.info(f"Final result of data after calling validate_context(): {data}")
    return data

def get_input_for_field(field):
    logging.debug(f"Beginning function execution with field = {field}.")
    if (isinstance(field.dataType, tuple)):
        logging.debug(f"{field}'s data type is list, so getting input for a list.")
        userInput = []
        while True:
            item = input(field.prompt)
            logging.info(f"User input for the list item: {item}")
            if (item == ''):
                logging.debug("Since the user entered an empty string, assume they are done entering inputs for the list and break from input loop.")
                break
            item = item.strip()
            if ((item.upper() == inputCodes['CANCEL']) or (item.upper() == inputCodes['SKIP'])):
                logging.info("Since the user entered a value that matches either the code for CANCEL or SKIP, returning the code they entered to signal to the calling function their intention.")
                return item
            userInput.append(item)
            logging.info(f"The input list is now {userInput}")
    else:
        logging.debug(f"{field}'s data type is not a list, so getting input for a single value.")
        userInput = input(field.prompt)
        logging.info(f"User input for {field} is {userInput}")
        userInput = userInput.strip()
    logging.info(f"Returning {userInput}")
    return userInput

def convert_input(dataType, userInput):
    logging.debug(f"Beginning function execution with dataType = {dataType}, userInput = {userInput}.")
    try:
        if (isinstance(dataType, tuple)):
            logging.debug("Data type is list.")
            newInput = dataType[0]()
            for item in userInput:
                newInput.append(dataType[1](item))
        elif (dataType is bool):
            logging.debug("Data type is bool.")
            if (userInput == '1'):
                logging.debug("Converting input to True.")
                newInput = True
            elif (userInput == '0'):
                logging.debug("Converting input to False.")
                newInput = False
            else:
                logging.debug("Input which is for a bool was neither 1 nor 0, so the input is invalid.")
                raise ValueError
        else:
            logging.debug("Data type is not list or bool.")
            newInput = dataType(userInput)
    except ValueError as err:
        logging.warning(f"Returning None since an error occurred when attempting to convert {userInput} to the datatype {dataType}: {err}")
        return None
    logging.info(f"Returning {newInput}")
    return newInput

def validate_field(field, userInput):
    logging.debug(f"Beginning function execution with field = {field}, userInput = {userInput}.")
    if (field.viewValidator and not field.viewValidator(userInput)):
        logging.info("Since the view validator exists, and it failed to validate the input, returning False.")
        return False
    if (field.controllerValidator and not field.controllerValidator(userInput)):
        logging.info("Since the controller validator exists, and it failed to validate the input, returning False.")
        return False
    logging.info("Since either the validators did not exist, or they successfully validated the input, returning True.")
    return True

def validate_context(data, method = 'create', initialPosition = None):
    logging.debug(f"Beginning function execution with data = {data}, method = {method}, initialPosition = {initialPosition}.")
    for field in addressFields:
        if (field.key == 'section'):
            logging.debug("Section field was located.")
            sectionField = field
            break
    if (method == 'create'):
        logging.debug("Method is 'create', so function to call is validate_section_context_create().")
        validate_section_context = controller.validate_section_context_create
    else:
        logging.debug("Method is 'update', so function to call is validate_section_context_update().")
        validate_section_context = lambda data: controller.validate_section_context_update(data, initialPosition = initialPosition)
    if (validate_section_context(data)):
        logging.info("The section context was validated successfully, so returning the data.")
        return data
    logging.debug("The section context failed to validate successfully.")
    print(errorOutputs['INVALID_SECTION'])
    while True:
        sectionInput = input(sectionField.prompt).strip()
        logging.info(f"User input: {sectionInput}")
        sectionInput = convert_input(sectionField.dataType, sectionInput)
        if (not sectionInput):
            logging.debug("User entered an empty string, so restart input loop.")
            print(errorOutputs['INVALID_INPUT'])
            continue
        data['section'] = sectionInput
        if (not validate_section_context(data)):
            logging.debug("The section context failed to validate successfully.")
            print(errorOutputs['INVALID_SECTION'])
            continue
        break
    logging.info("The context was successfully validated, so returning data.")
    return data

def get_existing_address_choice():
    logging.debug("Beginning function execution.")
    while True:
        choice = input(outputStrings['CHOOSE_EXISTING_ADDRESS'])
        logging.info(f"User input: {choice}")
        if (choice.upper() == inputCodes['CANCEL']):
            logging.info("User entered the cancel code - returning None to cancel the operation.")
            return None
        if (controller.read_single_address(choice)['success']):
            logging.info(f"The address entry was found, so returning {choice}.")
            return choice
        logging.debug(f"No address entry was found at {choice}, so restarting loop.")
        print(errorOutputs['ADDRESS_NOT_FOUND'])

def output_address(addressData):
    logging.debug("Beginning function execution.")
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
    logging.debug("Beginning function execution.")
    if (not addressesData):
        return {}
    separator = '-' * 50
    addressBookString = ''
    for address in addressesData:
        addressBookString += output_address(address)
        addressBookString += '\n' + separator + '\n'
    return addressBookString

def clear_console():
    logging.debug("Beginning function execution.")
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')


# Beginning execution of main program
logging.debug("Beginning main program execution.")
print(outputStrings['INTRODUCTION'])
while (True):
    choice = input(outputStrings['MENU']).strip()
    logging.info(f"The user's choice is {choice}.")
    match choice:
        case '1': # Read address entries
            logging.debug("The user chose to read the address entries.")
            print_all_addresses()
        case '2': # Create a new address entry
            logging.debug("The user chose to create a new address entry.")
            clear_console()
            print(outputStrings['BEGIN_CREATE'])
            addressData = get_input_for_address_create()
            logging.info(f"The address data received from the creation is: {addressData}")
            if (not addressData):
                logging.debug("Since the user decided to cancel the creation, restarting main loop.")
                print(outputStrings['CANCEL_CREATE'])
                continue
            addressCreate = controller.create_address(addressData)
            if (addressCreate['success']):
                logging.debug("The address creation was a success.")
                print(outputStrings['ADDRESS_CREATED'])
                print(output_address(addressCreate['result']))
            else:
                logging.warning(f"The address creation was a failure. Error info: {errorOutputs[addressCreate['errorType']]}")
                print(errorOutputs[addressCreate['errorType']])
        case '3': # Update an existing address entry
            logging.debug("The user chose to update an existing address entry.")
            clear_console()
            addressBookRead = print_all_addresses()
            if (not addressBookRead):
                logging.debug("The address book read was a failure.")
                continue
            print(outputStrings['BEGIN_UPDATE'])
            positionToUpdate = get_existing_address_choice()
            logging.info(f"The position to update is {positionToUpdate}.")
            if (not positionToUpdate):
                logging.debug("The user has cancelled the update, so restarting main loop.")
                print(outputStrings['CANCEL_UPDATE'])
                continue
            findAddressToUpdate = controller.read_single_address(positionToUpdate)
            if (findAddressToUpdate['success'] == False):
                logging.warning(f"The address to update was not able to be found. Error info: {errorOutputs[findAddressToUpdate['errorType']]}")
                print(errorOutputs[findAddressToUpdate['errorType']])
                continue
            print(output_address(findAddressToUpdate['result']))
            addressData = get_input_for_address_update(positionToUpdate)
            if (not addressData):
                logging.debug("The user has cancelled the update, so restarting main loop.")
                print(outputStrings['CANCEL_UPDATE'])
                continue
            addressUpdate = controller.update_address(addressData, positionToUpdate)
            if (addressUpdate['success']):
                logging.debug("The address update was a success.")
                print(outputStrings['ADDRESS_UPDATED'])
                print(output_address(addressUpdate['result']))
            else:
                logging.warning(f"The address update was a failure. Error info: {errorOutputs[addressUpdate['errorType']]}")
                print(errorOutputs[addressUpdate['errorType']])
        case '4': # Delete an existing address entry
            logging.debug("The user chose to delete an existing address entry.")
            clear_console()
            addressBookRead = print_all_addresses()
            if (not addressBookRead):
                logging.debug("The address book read was a failure.")
                continue
            print(outputStrings['BEGIN_DELETE'])
            positionToDelete = get_existing_address_choice()
            logging.info(f"The position to delete is {positionToDelete}.")
            if (not positionToDelete):
                logging.debug("The user has cancelled the deletion, so restarting main loop.")
                print(outputStrings['CANCEL_DELETE'])
                continue
            findAddressToDelete = controller.read_single_address(positionToDelete)
            if (findAddressToDelete['success'] == False):
                logging.warning(f"The address to delete was not able to be found. Error info: {errorOutputs[findAddressToDelete['errorType']]}")
                print(errorOutputs[findAddressToDelete['errorType']])
                continue
            print(output_address(findAddressToDelete['result']))
            confirmation = input(outputStrings['CONFIRM_DELETE'])
            if (not (confirmation.upper() == 'Y')):
                logging.debug("The user has cancelled the deletion, so restarting main loop.")
                print(outputStrings['CANCEL_DELETE'])
                continue
            addressDelete = controller.delete_address(positionToDelete)
            if (addressDelete['success']):
                logging.debug("The address deletion was a success.")
                print(outputStrings['ADDRESS_DELETED'])
                print(output_address(addressDelete['result']))
            else:
                logging.warning(f"The address deletion was a failure. Error info: {errorOutputs[addressDelete['errorType']]}")
                print(errorOutputs[addressDelete['errorType']])
        case '5': # Exit program
            logging.debug("The user chose to exit the program.")
            exitInput = input(outputStrings['CONFIRM_EXIT'])
            if (exitInput.strip().upper() == 'Y'):
                logging.debug("The user confirmed their choice to exit the program.")
                break
        case _:
            logging.debug("The user entered an invalid input.")
            print(errorOutputs['INVALID_INPUT'])
            continue
logging.debug("Program has completed execution.")