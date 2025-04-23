import shelve

class Address:
    DB_FILE = 'address_book.db' # Setting filename constant for database access

    def __init__(self, addressNumber = None, street = None, unit = None, names = None, position = None, section = None, isBusiness = None, isCBU = None, isVacant = None):
        self.addressNumber = addressNumber
        self.street = street
        self.unit = unit
        self.names = names
        self.position = position
        self.section = section
        self.isBusiness = isBusiness
        self.isCBU = isCBU
        self.isVacant = isVacant
    
    
    @staticmethod
    def read_single(position):
        with shelve.open(Address.DB_FILE) as addressBook:
            if (position in addressBook):
                address = addressBook[str(position)]
                return {
                    'addressNumber': address.addressNumber,
                    'street':        address.street,
                    'unit':          address.unit,
                    'names':         address.names,
                    'position':      address.position,
                    'section':       address.section,
                    'isBusiness':    address.isBusiness,
                    'isCBU':         address.isCBU,
                    'isVacant':      address.isVacant,
                }
            else:
                return None

    
    @staticmethod
    def read():
        lastPosition = Address.get_last_position()
        if (lastPosition):
            addressBookToReturn = []
            for position in range(1, lastPosition):
                addressBookToReturn.append(Address.read_single(position))
        else:
            return None

    
    def create(self):   # Beginning create() execution
        lastPosition = Address.get_last_position()  # Calling get_last_position() to get the last address's position number
        if (lastPosition is None): # Checking if address book is empty by checking existence of lastPosition
            lastPosition = 0    # Since address book is empty, setting lastPosition to 0 so the address's position can be set to 1
        if (self.position > (lastPosition)):    # Checking if the given position is beyond the existing last position
            self.position = lastPosition + 1    # Since the given position is beyond the existing last position, setting address's position to be the next number after the last position
        
        Address.shift_positions(self.position, 'forward')   # Calling shift_positions() to shift all addresses after the address to be inserted to the next position
        
        lastSection = Address.get_last_section()    # Calling get_last_section() to get the last section number used
        if (self.section > lastSection):    # Checking if the given section is beyond the existing last section
            self.section = (lastSection + 1)    # Since the given section is beyond the existing last section, setting the address's section to be the next number after the last section

        with shelve.open(Address.DB_FILE) as addressBook: # Finally ready to open address book to insert the new address
            addressBook[str(self.position)] = self  # Assigning the address object to the address book using its position as the key
        
        return Address.read_single(self.position)   # Calling read_single() to return the newly created address entry from the address book to confirm that the creation succeeded

    
    def update(self, initialPosition):   # Beginning update() execution
        if (self.position < initialPosition):   # Checking if the updated address is being moved to a lower position
            Address.delete(initialPosition) # Deleting the address at the initial position first because shifting the higher positions back won't affect the lower position of the updated address
            self.create()   # Inserting the updated address into the new position
            return Address.read_single(self.position)   # Returning address's data to confirm that the update was successful
        elif (self.position > initialPosition): # Checking if the updated address is being moved to a higher position
            self.create()   # Inserting the updated address first to get it into the desired spot between other addresses
            Address.delete(initialPosition) # Deleting the address at the initial position; although updated address's position is now one less than desired position, addresses are still in the desired order
            return Address.read_single(self.position - 1)   # Returning address's data at the decremented position to confirm that the update was successful
        else:
            Address.delete(initialPosition) # Since updated address's position is the same as its initial position, deletion and creation order don't matter; deleting the address at the initial position
            self.create()   # Inserting the updated address at the same position
            return Address.read_single(self.position)   # Returning address's data to confirm that the update was successful

    
    @staticmethod
    def delete(positionToDelete):   # Beginning delete() execution
        lastPosition = Address.get_last_position()  # Calling get_last_position() to get the last address's position number
        if (lastPosition is None): # Checking if address book is empty by checking existence of lastPosition
            return None # Returning None from delete() to indicate that address book is empty and there is no entry to delete
        if (positionToDelete > (lastPosition)): # Checking if the given position is beyond the existing last position
            return None # Returning none from delete() to indicate that given position is beyond the last address's position

        addressToDelete = Address.read_single(positionToDelete) # Getting address's data saved into a dictionary before deleting
        Address.shift_positions(positionToDelete, direction = 'backward')   # Calling shift_positions() to shift addresses after deleted address back 1 position to overwrite address being deleted
        return addressToDelete  # Returning the deleted address's data to the controller

    
    @staticmethod
    def get_sorted_keys():
        with shelve.open(Address.DB_FILE) as addressBook:
            numericKeys = []
            for key in addressBook.keys():
                numericKeys.append(int(key))
            return numericKeys.sort()

    
    @staticmethod
    def get_last_position():
        sortedKeys = Address.get_sorted_keys()
        if (sortedKeys):
            return max(sortedKeys)
        else:
            return None
    
    
    @staticmethod
    def get_last_section():
        lastPosition = Address.get_last_position()  # Getting a number representing the last address's position
        if (not lastPosition):  # Checking if address book is empty
            return 1            # Since address book is empty, returning 1 for the last section number
        with shelve.open(Address.DB_FILE) as addressBook: # Since address book is not empty, opening address book
            return addressBook[str(lastPosition)].section   # Returning the section number of the last address

    
    @staticmethod
    def shift_positions(startPosition, direction = 'forward'):
        sortedKeys = Address.get_sorted_keys()
        if (not sortedKeys):  # This verifies that entries exist in address book
            return
        keysToShift = []
        for key in sortedKeys:
            if (key >= startPosition):
                keysToShift.append(key)
        if (not keysToShift):  # This verifies that entries still exist that need to be shifted
            return
        if (direction == 'forward'):
            keysToShift = list(reversed(keysToShift))
        with shelve.open('address_book', writeback = True) as addressBook:
            for position in keysToShift:
                if (direction == 'forward'):
                    keyToFill = str(position + 1)
                    keyToMove = str(position)
                else:
                    keyToFill = str(position)
                    keyToMove = str(position + 1)
                    if (keyToMove not in addressBook):
                        del addressBook[keyToFill]
                        break
                addressBook[keyToFill] = addressBook[keyToMove]
            for key in addressBook:
                addressBook[key].position = int(key)