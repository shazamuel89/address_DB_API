from Address import Address

def read_single_address(positionToRead):
    address = Address.read_single(positionToRead)
    if (address):
        return {
            'success': True,
            'result':  address
        }
    else:
        return {
            'success':   False,
            'errorType': 'ADDRESS_NOT_FOUND'
        }


def read_all_addresses():
    addresses = Address.read()
    if (addresses):
        return {
            'success': True,
            'result':  addresses
        }
    else:
        return {
            'success':  False,
            'errorType': 'ADDRESS_BOOK_EMPTY'
        }


def create_address(addressData):
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
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD'
        }
    createdAddress = address.create()
    return {
        'success': True,
        'result':  createdAddress
    }


def update_address(addressData, initialPosition):
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
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD'
        }
    updatedAddress = address.update(initialPosition)
    return {
        'success': True,
        'result':  updatedAddress
    }


def delete_address(positionToDelete):
    deletedAddress = Address.delete(positionToDelete)
    if (deletedAddress):
        return {
            'success': True,
            'result':  deletedAddress
        }
    else:
        return {
            'success':   False,
            'errorType': 'ADDRESS_NOT_FOUND'
        }


def names_validator(names):
    if (len(names) > 10):
        return False
    for item in names:
        if (len(item) > 30):
            return False
    return True


def position_validator(position):
    lastPosition = Address.get_last_position()
    if (lastPosition):
        return (position <= (lastPosition + 1))
    else:
        return (position == 1)


def section_validator(section):
    lastSection = Address.get_last_section()
    if (lastSection):
        return (section <= (lastSection + 1))
    else:
        return (section == 1)


def validate_section_context_create(data):
    sectionInput = data['section']  # Get the user inputted section number
    lastSection = Address.get_last_section()    # Get the last section number
    if (not lastSection):   # If address book is empty
        return (sectionInput == 1)  # The section number must be 1
    previousAddress = Address.read_single(data['position'] - 1) # Get the previous address
    nextAddress = Address.read_single(data['position']) # For create, the address that WILL be next is the one in the current position to insert
    if (not previousAddress):   # If we are inserting into the first position
        return (sectionInput == 1)  # Then the section number must be 1
    if (not nextAddress):   # If we are inserting after the last position
        return ((sectionInput == lastSection) or (sectionInput == (lastSection + 1)))   # Then section input must be equal to either the last section or the next section after the last section
    # At this point, we know that address is being inserted between 2 existing addresses (for create)
    return ((sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section']))   # Verify that the section input is equal to either the previous address's section or the next address's section


def validate_section_context_update(data, initialPosition):
    sectionInput = data['section']  # Get the user inputted section number
    lastSection = Address.get_last_section()    # Get the last section number
    # Address book is not empty if we are doing an update
    if (initialPosition == data['position']):   # If the update is leaving the address in the same position
        previousAddress = Address.read_single(data['position'] - 1) # The address that will be before it is the one that is in the previous position
        nextAddress = Address.read_single(data['position'] + 1) # The address that will be next is the one that is in the next position
    elif (initialPosition == (data['position'] - 1)):   # If the update is moving the address to the next position (which won't actually change anything due to shifting and removing the address at the previous position before the update)
        previousAddress = Address.read_single(data['position'] - 2) # The address that will be before it after the update is the one that is 2 positions behind
        nextAddress = Address.read_single(data['position']) # The address that will be next is the one that is in the position being inserted into
    else:
        previousAddress = Address.read_single(data['position'] - 1) # The address that will be before it is the one that is in the previous position
        nextAddress = Address.read_single(data['position']) # The address that will be next is the one that is in the current position to insert
    if (not previousAddress):   # If the updated address is in the first position
        return (sectionInput == 1)  # The section inputted must be 1
    if (not nextAddress):   # If the updated address is in the last position
        return (sectionInput == lastSection)    # The section inputted must be the last section
    return ((sectionInput == previousAddress['section']) or (sectionInput == nextAddress['section']))  # The section inputted must be equal to either the previous address's section or the next address's section


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