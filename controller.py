import sys
import logging

try:
    from Address import Address
    logging.debug('Address.py loaded successfully.')
except:
    print('Address.py is missing! Program will now exit. (Please ensure you have Address.py in the same directory as this python script.)')
    logging.critical('Address.py is missing! Program will now exit. (Please ensure you have Address.py in the same directory as this python script.)')
    sys.exit(1)


def read_single_address(positionToRead):
    logging.debug(f"Beginning function execution with positionToRead = {positionToRead}.")
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

def position_validator(position):
    logging.debug(f"Beginning function execution with position = {position}.")
    lastPosition = Address.get_last_position()
    if (lastPosition):
        logging.info(f"The address book is not empty - returning bool of {position} <= ({lastPosition} + 1).")
        return (position <= (lastPosition + 1))
    else:
        logging.info(f"The address book is empty - returning bool of {position} == 1.")
        return (position == 1)

def section_validator(section):
    logging.debug(f"Beginning function execution with section = {section}.")
    lastSection = Address.get_last_section()
    if (lastSection):
        logging.info(f"The address book is not empty - returning bool of {section} <= ({lastSection} + 1).")
        return (section <= (lastSection + 1))
    else:
        logging.info(f"The address book is empty - returning bool of {section} == 1.")
        return (section == 1)

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