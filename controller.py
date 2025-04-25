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
            'errorType': 'ADDRESS_NOT_FOUND',
            'position':  positionToRead
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
    except KeyError as e:
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD',
            'missingField': str(e)
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
    except KeyError as e:
        return {
            'success':     False,
            'errorType':   'MISSING_FIELD',
            'missingField': str(e)
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
            'errorType': 'ADDRESS_NOT_FOUND',
            'position':  positionToDelete
        }