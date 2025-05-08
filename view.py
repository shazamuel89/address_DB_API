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

'''
This class defines the properties of a field/attribute/column for a table in a database, including the key/name, the input prompt, the data type,
the simple constraints within the scope of the view, the more specific constraints within the scope of the controller/database, and whether or not the field is optional.
'''
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

# The inputCodes are strings that the user can type in certain situations to execute a certain action, such as cancelling the current operation or skipping an input entry.
inputCodes = {
    'CANCEL':   '-1',
    'SKIP':     '-2',
}

# These outputStrings are strings that will be printed or displayed at certain points in the program.
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

# These errorOutputs are strings that will be printed or displayed when an error occurs, and the error type matches a key in this dictionary.
errorOutputs = {
    'ADDRESS_NOT_FOUND':    "There is no address entry with that position! Please try again.",
    'ADDRESS_BOOK_EMPTY':   "There are no existing address entries yet! Please choose another option.",
    'MISSING_FIELD':        "A field is missing data!",
    'INVALID_INPUT':        "That is not a valid input. Please try again.",
    'INVALID_SECTION':      "The section number is invalid because it is not within the sections of the address before or after it.",
}

# This is where the properties for each of the fields/attributes/columns for the table in the database are defined.
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

'''
print_all_addresses() prints a formatted version of the entire address book to the console.
If the address book is empty or the read fails for some other reason, then a relevant error message is printed to the console.
'''
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

'''
get_input_for_address_create() controls the process of retrieving input for a new address entry.
It returns a dictionary where each key is the field name, and each value is the input received for the field.
The input will be completely validated and converted to the correct data type before it returns the full data of the new address entry.
If the user decides to cancel the creation, it returns None. 
'''
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
            userInput = convert_input(userInput, field.dataType)
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
    if (isinstance(data, str) and (data.upper() == inputCodes['CANCEL'])):
        logging.info(f"User entered the cancel code - returning None to cancel the creation.")
        return None
    logging.info(f"Final result of data after calling validate_context(): {data}")
    return data

'''
get_input_for_address_update() controls the process of retrieving input for an updated address entry.
It receives an int for the positionToUpdate.
It returns a dictionary where each key is the field name, and each value is the input received for the field.
The input will be completely validated and converted to the correct data type before it returns the full data of the updated address entry.
If the user decides to cancel the creation, it returns None.
If by some chance the positionToUpdate does not match an existing address entry, then it returns False.
'''
def get_input_for_address_update(positionToUpdate):
    logging.debug(f"Beginning function execution with positionToUpdate = {positionToUpdate}.")
    try:
            positionToUpdate = int(positionToUpdate)
    except ValueError as err:
        logging.warning(f"Returning False since an error occurred when attempting to convert {positionToUpdate} to an int: {err}")
        print(errorOutputs['INVALID_INPUT'])
        return False
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
            userInput = convert_input(userInput, field.dataType)
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
    if (isinstance(data, str) and (data.upper() == inputCodes['CANCEL'])):
        logging.info(f"User entered the cancel code - returning None to cancel the creation.")
        return None
    logging.info(f"Final result of data after calling validate_context(): {data}")
    return data

'''
get_input_for_field() controls the receiving of input for a specific field.
It receives a Field object for the field.
It runs different code for the input if the dataType of the field is a list or a single item.
It also checks for the inputCodes that the user may input.
It returns the user's input, but it does not validate the input since that is the job of a separate function.
'''
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

'''
convert_input() attempts to convert the input to the correct dataType.
It receives a string for userInput and a data_type for dataType.
If the dataType is list, then it first attempts to convert the userInput to the list type, and then attempts to convert each item in the list to the correct type.
If the dataType is bool, then it converts a '1' to True and a '0' to False.
For any other dataType, it simply attempts to convert it as normal.
If it fails to convert the userInput, then it returns None.
Otherwise, it returns the converted userInput.
'''
def convert_input(userInput, dataType):
    logging.debug(f"Beginning function execution with userInput = {userInput}, dataType = {dataType}.")
    if not (isinstance(dataType, type) or (isinstance(dataType, tuple) and len(dataType) == 2 and isinstance(dataType[0], type) and issubclass(dataType[0], list) and isinstance(dataType[1], type))):
        logging.warning(f"Returning None since the argument for dataType, {dataType}, was invalid.")
        return None
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

'''
validate_field() runs the validator functions, if they exist, for the field that are defined in the view and the controller scope.
It takes a Field object for the field, and the value for userInput is assumed to be of the correct data type for the field, since this should occur after executing convert_input().
If any of the validators fail, it returns False, otherwise it returns True.
'''
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

'''
validate_context() checks the data received for an address entry against the context of where it is being inserted with the position and section inputs.
It must be executed only after all of the data for that entry has been received.
Thus, if a field needs to be re-entered, it must be validated here.
The function receives a dictionary containing the address entry's information for data.
It also receives an optional string which is by default 'create', but the alternative is 'update'.
It also receives an optional int for initialPosition, which is by default set to None and is only used if the method is 'update'.
If the user enters the inputCode for cancel, then it returns the cancel code instead of the data dictionary.
It returns the dictionary containing the data for the address entry once the input finally passes the context validation.
'''
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
        if (sectionInput.upper() == inputCodes['CANCEL']):
            logging.info("Since the user entered a value that matches the code for CANCEL, returning the code they entered to signal to the calling function their intention.")
            return sectionInput
        logging.info(f"User input: {sectionInput}")
        sectionInput = convert_input(sectionInput, sectionField.dataType)
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

'''
get_existing_address_choice() gets user input for a position number for an existing address.
If the user enters the inputCode for cancel, then it returns None.
If the position is invalid or not found, it restarts the input loop.
If the address is found, then it returns the position number as an int.
'''
def get_existing_address_choice():
    logging.debug("Beginning function execution.")
    while True:
        choice = input(outputStrings['CHOOSE_EXISTING_ADDRESS'])
        logging.info(f"User input: {choice}")
        if (choice.upper() == inputCodes['CANCEL']):
            logging.info("User entered the cancel code - returning None to cancel the operation.")
            return None
        try:
            choice = int(choice)
        except ValueError as err:
            logging.warning(f"Restarting input loop since an error occurred when attempting to convert {choice} to an int: {err}")
            print(errorOutputs['INVALID_INPUT'])
            continue
        if (controller.read_single_address(choice)['success']):
            logging.info(f"The address entry was found, so returning {choice}.")
            return choice
        logging.debug(f"No address entry was found at {choice}, so restarting loop.")
        print(errorOutputs['ADDRESS_NOT_FOUND'])

'''
output_address() returns a formatted string that contains the information for an address entry.
It receives a dictionary containing the address's data for addressData.
'''
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

'''
output_address_book() returns a formatted string containing the data for all of the addresses in the address book.
If the address book is empty, it simply returns an empty dictionary.
It receives a list of dictionaries where each dictionary contains the data for an address in the address book.
'''
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

'''
clear_console() simply clears the console of all text, using the method that is correct for the current operating system.
'''
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