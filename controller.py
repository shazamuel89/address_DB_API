'''

INF360 - Programming in Python

Final Project

I, Samuel Heinrich, affirm that the work submitted for this assignment is entirely my own. I have not engaged in any form of academic dishonesty, including but not limited to cheating, plagiarism, or the use of
unauthorized materials. This includes, but is not limited to, the use of resources such as Chegg, MyCourseHero, StackOverflow, ChatGPT, or other AI assistants, except where explicitly permitted by the instructor.
I have neither provided nor received unauthorized assistance and have accurately cited all sources in adherence to academic standards. I understand that failing to comply with this integrity statement may result in
consequences, including disciplinary actions as determined by my course instructor and outlined in institutional policies. By signing this statement, I acknowledge my commitment to upholding the principles of
academic integrity.

'''


import sys
import logging

try:
    from Address import Address
    logging.debug('Address.py loaded successfully.')
except:
    print('Address.py is missing! Program will now exit. (Please ensure you have Address.py in the same directory as this python script.)')
    logging.critical('Address.py is missing! Program will now exit. (Please ensure you have Address.py in the same directory as this python script.)')
    sys.exit(1)


'''
read_all_addresses() returns a dictionary where the value for 'success' is True if the address book is not empty and False if it is empty.
The other item in the returned dictionary is either 'result' if 'success' is True, or 'errorType' if 'success' is False.
'result' is a list of dictionaries, each containing an address's data, and 'errorType' is a key from the errorOutputs dictionary defined in the view file.
'''
def read_all_addresses():
    logging.debug("Beginning function execution.")
    addresses = Address.read()
    if (addresses):
        logging.info("Since addresses is not empty, returning success response.")
        return {
            'success': True,
            'result':  addresses
        }
    else:
        logging.info("Since addresses is empty, returning failure response.")
        return {
            'success':  False,
            'errorType': 'ADDRESS_BOOK_EMPTY'
        }


'''
read_single_address() returns a dictionary where the value for 'success' is True if the address is found and False if not.
The other item in the returned dictionary is either 'result' if 'success' is True, or 'errorType' if 'success' is False.
'result' is a dictionary containing the address's data, and 'errorType' is a key from the errorOutputs dictionary defined in the view file.
It takes an int for positionToRead which is the position value of the address that will be read from the address book.
'''
def read_single_address(positionToRead):
    logging.debug(f"Beginning function execution with positionToRead = {positionToRead}.")
    try:
        positionToRead = int(positionToRead)
    except ValueError as err:
        logging.warning(f"Returning failure response since an error occurred when attempting to convert {positionToRead} to an int: {err}")
        return {
            'success': False,
            'errorType': 'INVALID_INPUT'
        }
    address = Address.read_single(positionToRead)
    if (address):
        logging.info("Since address exists, returning success response.")
        return {
            'success': True,
            'result':  address
        }
    else:
        logging.info("Since address does not exist, returning failure response.")
        return {
            'success':   False,
            'errorType': 'ADDRESS_NOT_FOUND'
        }


'''
create_address() returns a dictionary where the value for 'success' is True if the address is created successfully and False if not.
The other item in the returned dictionary is either 'result' if 'success' is True, or 'errorType' if 'success' is False.
'result' is a dictionary containing the created address's data, and 'errorType' is a key from the errorOutputs dictionary defined in the view file.
It takes a dictionary containing the address's data for addressData.
'''
def create_address(addressData):
    logging.debug(f"Beginning function execution with addressData = {addressData}.")
    try:
        address = Address(
            addressData['addressNumber'],
            addressData['street'],
            addressData['unit'],
            addressData['names'],
            addressData['position'],
            addressData['section'],
            addressData['isBusiness'],
            addressData['isCBU'],
            addressData['isVacant']
        )
    except KeyError:
        logging.warning("A key is missing from the addressData dictionary passed to this function - returning failure array.")
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD'
        }
    createdAddress = address.create()
    logging.info("The address entry was inserted into the database - returning success response.")
    return {
        'success': True,
        'result':  createdAddress
    }


'''
update_address() returns a dictionary where the value for 'success' is True if the address is updated successfully and False if not.
The other item in the returned dictionary is either 'result' if 'success' is True, or 'errorType' if 'success' is False.
'result' is a dictionary containing the updated address's data, and 'errorType' is a key from the errorOutputs dictionary defined in the view file.
It takes a dictionary containing the address's data for addressData and an int for initialPosition.
'''
def update_address(addressData, initialPosition):
    logging.debug(f"Beginning function execution with addressData = {addressData}, initialPosition = {initialPosition}.")
    try:
        address = Address(
            addressData['addressNumber'],
            addressData['street'],
            addressData['unit'],
            addressData['names'],
            addressData['position'],
            addressData['section'],
            addressData['isBusiness'],
            addressData['isCBU'],
            addressData['isVacant']
        )
    except KeyError:
        logging.warning("A key is missing from the addressData dictionary passed to this function - returning failure array.")
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD'
        }
    try:
        initialPosition = int(initialPosition)
    except ValueError as err:
        logging.warning("Returning the failure response since an error occurred when attempting to convert {positionToDelete} to the an int: {err}")
        return {
            'success': False,
            'errorType': 'INVALID_INPUT'
        }
    updatedAddress = address.update(initialPosition)
    logging.info("The address entry was updated in the database - returning success response.")
    return {
        'success': True,
        'result':  updatedAddress
    }


'''
delete_address() returns a dictionary where the value for 'success' is True if the address is deleted successfully and False if not.
The other item in the returned dictionary is either 'result' if 'success' is True, or 'errorType' if 'success' is False.
'result' is a dictionary containing the deleted address's data, and 'errorType' is a key from the errorOutputs dictionary defined in the view file.
It takes an int for positionToDelete.
'''
def delete_address(positionToDelete):
    logging.debug(f"Beginning function execution with positionToDelete = {positionToDelete}.")
    try:
        positionToDelete = int(positionToDelete)
    except ValueError as err:
        logging.warning("Returning the failure response since an error occurred when attempting to convert {positionToDelete} to the an int: {err}")
        return {
            'success': False,
            'errorType': 'INVALID_INPUT'
        }
    deletedAddress = Address.delete(positionToDelete)
    if (deletedAddress):
        logging.info("The address entry was deleted from the database - returning success response.")
        return {
            'success': True,
            'result':  deletedAddress
        }
    else:
        logging.info("The address entry was not found in the database - returning failure response.")
        return {
            'success':   False,
            'errorType': 'ADDRESS_NOT_FOUND'
        }


'''
names_validator() is the controller's more specific validator function for the names field, which is a list of strings.
It receives a list of strings for names.
If the list of names contains more than 10 names, or if any of the names are longer than 30 characters, it returns False, otherwise it returns True.
'''
def names_validator(names):
    logging.debug(f"Beginning function execution with names = {names}.")
    if (len(names) > 10):
        logging.info(f"The names array has more than 10 items - returning False.")
        return False
    for item in names:
        if (len(item) > 30):
            logging.info(f"The name {item} has more than 30 characters - returning False.")
            return False
    logging.info("The names array's length and length of the individual names was successfully validated - returning True.")
    return True


'''
position_validator() is the controller's more specific validator function for the position field, which is an int.
It receives an int for position.
If the address book is not empty, then it returns True if position is less than or equal to the position number after the last existing position, False otherwise.
If the address book is empty, then it returns True if position is equal to 1, False otherwise.
'''
def position_validator(position):
    logging.debug(f"Beginning function execution with position = {position}.")
    lastPosition = Address.get_last_position()
    if (lastPosition):
        logging.info(f"The address book is not empty - returning bool of {position} <= ({lastPosition} + 1).")
        return (position <= (lastPosition + 1))
    else:
        logging.info(f"The address book is empty - returning bool of {position} == 1.")
        return (position == 1)


'''
section_validator() is the controller's more specific validator function for the section field, which is an int.
It receives an int for section.
If the address book is not empty, then it returns True if section is less than or equal to the section number after the last existing section, False otherwise.
If the address book is empty, then it returns True if section is equal to 1, False otherwise.
'''
def section_validator(section):
    logging.debug(f"Beginning function execution with section = {section}.")
    lastSection = Address.get_last_section()
    if (lastSection):
        logging.info(f"The address book is not empty - returning bool of {section} <= ({lastSection} + 1).")
        return (section <= (lastSection + 1))
    else:
        logging.info(f"The address book is empty - returning bool of {section} == 1.")
        return (section == 1)


'''
validate_section_context_create() checks if the given section number is within the section numbers of the addresses in the positions before and after the address being created.
It accounts for the new address being the only address, being the first address, being the last address, and being inserted between 2 existing addresses.
It receives a dictionary of the address's data, just before it is actually created, for data.
It returns True if the section number is valid, and False if not.
'''
def validate_section_context_create(data):
    logging.debug(f"Beginning function execution with data = {data}.")
    sectionInput = data['section']
    lastSection = Address.get_last_section()
    if (not lastSection):
        logging.info(f"Since address book is empty, we are inserting into the first section - returning bool of {sectionInput} == 1.")
        return (sectionInput == 1)
    previousAddress = Address.read_single(data['position'] - 1)
    nextAddress = Address.read_single(data['position']) # For create, the address that WILL be next is the one in the current position to insert
    if (not previousAddress):
        logging.info(f"Since there is no address in the position below our insert, we are inserting into the first section - returning bool of {sectionInput} == 1.")
        return (sectionInput == 1)
    if (not nextAddress):
        logging.info(f"Since we are inserting after the last address, {sectionInput} must be either the last section or 1 after the last section - returning {(sectionInput == lastSection) or (sectionInput == (lastSection + 1))}.")
        return ((sectionInput == lastSection) or (sectionInput == (lastSection + 1)))
    # At this point, we know that address is being inserted between 2 existing addresses (for create)
    logging.info(f"Since address is being inserted between 2 existing addresses, {sectionInput} must be equal to the section of either the previous address or the next address - returning {(sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section'])}.")
    return ((sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section']))


'''
validate_section_context_update() checks if the given section number is within the section numbers of the addresses in the positions before and after the position that the address will be in after it is updated.
It accounts for the updated address being the only address, being the first address, being the last address, and being inserted between 2 existing addresses.
It also accounts for remaining in the same position, or being moved to a position that is next to its previous position, since its existing pre-update data still exists in the address book.
It receives a dictionary of the address's data, just before it is actually updated, for data.
It returns True if the section number is valid, and False if not.
'''
def validate_section_context_update(data, initialPosition):
    logging.debug(f"Beginning function execution with data = {data}, initialPosition = {initialPosition}.")
    sectionInput = data['section']
    lastSection = Address.get_last_section()
    # Address book is not empty if we are doing an update
    if (initialPosition == data['position']):
        logging.debug("The update is leaving the address in the same position - retrieving the addresses in the previous and next positions.")
        previousAddress = Address.read_single(data['position'] - 1)
        nextAddress = Address.read_single(data['position'] + 1)
    elif (initialPosition == (data['position'] - 1)):
        logging.debug("The update is moving the address to the next position (which will end up leaving it in the same place after shifting) - retrieving the addresses in the previous and next positions.")
        previousAddress = Address.read_single(data['position'] - 2) # The address that will be before it after the update is the one that is 2 positions behind
        nextAddress = Address.read_single(data['position']) # The address that will be next is the one that is in the position being inserted into
    else:
        logging.debug("The address is being moved to a position where it will not be adjacent to the initial address before the update - retrieving the addresses in the previous and next positions.")
        previousAddress = Address.read_single(data['position'] - 1) # The address that will be before it is the one that is in the previous position
        nextAddress = Address.read_single(data['position']) # The address that will be next is the one that is in the current position to insert
    if (not previousAddress):
        logging.info(f"Since the address is being moved to the first position, returning the bool of {sectionInput} == 1.")
        return (sectionInput == 1)
    if (not nextAddress):
        logging.info(f"Since the address is being moved to the last position, returning the bool of {sectionInput} == {lastSection}.")
        return (sectionInput == lastSection)
    logging.info(f"Since the address is being moved to a position between 2 existing addresses, {sectionInput} must be equal to the section of either the previous address or the next address - returning {(sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section'])}.")
    return ((sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section']))


'''
fieldValidators is a dictionary that contains the controller's more specific validators for each field in the address book database.
These do not include basic checks that are checked in the view's validators, such as being positive or not empty.
'''
fieldValidators = {
    'addressNumber':    lambda x: x <= 999999,
    'street':           lambda x: len(x) <= 50,
    'unit':             lambda x: len(x) <= 4,
    'names':            names_validator,
    'position':         position_validator,
    'section':          section_validator,
    'isBusiness':       None,
    'isCBU':            None,
    'isVacant':         None,
}