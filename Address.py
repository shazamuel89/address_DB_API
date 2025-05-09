'''

INF360 - Programming in Python

Final Project

I, Samuel Heinrich, affirm that the work submitted for this assignment is entirely my own. I have not engaged in any form of academic dishonesty, including but not limited to cheating, plagiarism, or the use of
unauthorized materials. This includes, but is not limited to, the use of resources such as Chegg, MyCourseHero, StackOverflow, ChatGPT, or other AI assistants, except where explicitly permitted by the instructor.
I have neither provided nor received unauthorized assistance and have accurately cited all sources in adherence to academic standards. I understand that failing to comply with this integrity statement may result in
consequences, including disciplinary actions as determined by my course instructor and outlined in institutional policies. By signing this statement, I acknowledge my commitment to upholding the principles of
academic integrity.

'''


# shelve is the module that allows the program to store the address data in a permanent database location
import shelve
import logging

class Address:
    DB_FILE = 'address_book.db' # Setting filename where database is stored

    def __init__(
        self,
        addressNumber = None,
        street = None,
        unit = None,
        names = None,
        position = None,
        section = None,
        isBusiness = None,
        isCBU = None,
        isVacant = None
    ):
        # Set all string type values to all uppercase for simplicity
        self.addressNumber = addressNumber
        self.street = street.upper()
        self.unit = unit.upper() if unit else unit
        self.names = [name.upper() for name in names]
        self.position = position
        self.section = section
        self.isBusiness = isBusiness
        self.isCBU = isCBU
        self.isVacant = isVacant
    

    '''
    read() is a static method that retrieves the data for all existing addresses and returns them in a list of dictionaries.
    If the address book is empty, it returns None.
    '''
    @staticmethod
    def read():
        logging.debug("Beginning function execution.")
        lastPosition = Address.get_last_position()
        if (lastPosition):
            logging.info("Since the address book is not empty, getting each address into a list and returning the list.")
            addressBookToReturn = []
            for position in range(1, lastPosition + 1):
                addressBookToReturn.append(Address.read_single(position))
            return addressBookToReturn
        else:
            logging.info("Since the address book is empty, returning None.")
            return None


    '''
    read_single() is a static method that retrieves the data for an address and returns it in a dictionary.
    It takes an int for positionToRead, which is the position value of the address to be read.
    If no address is found, it returns None.
    '''
    @staticmethod
    def read_single(positionToRead):
        logging.debug(f"Beginning function execution with positionToRead = {positionToRead}.")
        with shelve.open(Address.DB_FILE) as addressBook:
            if (str(positionToRead) in addressBook):
                logging.info(f"Since an address was found at position {positionToRead}, returning the address data.")
                address = addressBook[str(positionToRead)]
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
                logging.info(f"Since no address was found at position {positionToRead}, returning None.")
                return None


    '''
    create() is a method that inserts an address entry into the address book.
    The calling object is what is stored in the actual database, so the object's properties must be set to the desired values before calling this method.
    After inserting the address entry, it reads the new entry from the address book and returns it to confirm the successful operation.
    '''
    def create(self):
        logging.debug(f"Beginning function execution with self = {self}.")
        lastPosition = Address.get_last_position()
        if (not lastPosition):
            logging.debug("Since address book is empty, setting position to 1.")
            self.position = 1
        elif (self.position > lastPosition):
            logging.debug(f"Since the position {self.position} is beyond the last position {lastPosition}, setting the position to 1 after the last position.")
            self.position = lastPosition + 1
        Address.shift_positions(self.position, 'forward')
        lastSection = Address.get_last_section()
        if (not lastSection):
            logging.debug("Since address book is empty, setting section to 1.")
            self.section = 1
        elif (self.section > lastSection):
            logging.debug(f"Since the section {self.section} is beyond the last section {lastSection}, setting the section to 1 after the last section.")
            self.section = lastSection + 1
        with shelve.open(Address.DB_FILE) as addressBook:
            addressBook[str(self.position)] = self
        return Address.read_single(self.position)


    '''
    update() is a method that updates an existing address entry in the address book.
    The calling object is what is stored in the actual database, so the object's properties must be set to the desired values before calling this method.
    It takes an int for initialPosition.
    Depending on where the update is moving the address relative to its initial position, it deletes the original entry and inserts the new entry in an order that will be compatible with the shifting after each operation.
    After updating the address entry, it reads the updated entry from the address book and returns it to confirm the successful operation.
    If 
    '''
    def update(self, initialPosition):
        logging.debug(f"Beginning function execution with self = {self}, initialPosition = {initialPosition}.")
        if (self.position < initialPosition):
            logging.debug("Since the address is being moved to a lower position, deleting the address at the initial position first, because shifting the addresses back won't affect the updated address's new position.")
            Address.delete(initialPosition)
            self.create()
            return Address.read_single(self.position)
        elif (self.position > initialPosition):
            logging.debug("Since the address is being moved to a higher position, inserting the updated address first so that shifting the addresses back won't affect the updated address's position.")
            self.create()
            Address.delete(initialPosition)
            return Address.read_single(self.position - 1) # Although updated address's position is now one less than desired position due to shifting, addresses are still in the desired order
        else:
            logging.debug("Since the updated address is remaining in the same position, the order of deletion and insertion doesn't matter.")
            Address.delete(initialPosition)
            self.create()
            return Address.read_single(self.position)


    '''
    delete() is a static method that deletes an address entry from the address book.
    It takes an int for positionToDelete.
    Before deleting the address entry, it saves its data and then returns it after the deletion to provide a 'pop' like functionality.
    If the address entry cannot be found, it returns None.
    '''
    @staticmethod
    def delete(positionToDelete):
        logging.debug(f"Beginning function execution with positionToDelete = {positionToDelete}.")
        lastPosition = Address.get_last_position()
        if (lastPosition is None):
            logging.info("Since address book is empty, returning None.")
            return None
        if (positionToDelete > (lastPosition)):
            logging.info("Since the position to delete is beyond the last position, returning None.")
            return None
        logging.info(f"Since an address exists at position {positionToDelete}, deleting the address at position {positionToDelete}.")
        addressToDelete = Address.read_single(positionToDelete)
        Address.shift_positions(positionToDelete, direction = 'backward')
        return addressToDelete


    '''
    shift_positions() is a static method that shifts the address entries in the address book 1 spot according to the parameters.
    It takes an int for startPosition which is the initial position value of the address which is adjacent to either the address being deleted or the address to be inserted.
    It also takes an optional string for direction, which is 'forward' by default for an insert, and the alternative is meant to be 'backward' for a deletion.
    '''
    @staticmethod
    def shift_positions(startPosition, direction = 'forward'):
        logging.debug(f"Beginning function execution with startPosition = {startPosition}, direction = {direction}.")
        sortedKeys = Address.get_sorted_keys()
        if (not sortedKeys):
            logging.info("Since the address book is empty, returning.")
            return
        keysToShift = []
        for key in sortedKeys:
            if (key >= startPosition):
                keysToShift.append(key)
        if (not keysToShift):
            logging.info("Since there are no keys needing to be shifted, returning.")
            return
        if (direction == 'forward'):
            logging.debug("Since the shift direction is 'forward', reversing the list of addresses to shift.")
            keysToShift = list(reversed(keysToShift))
        logging.debug(f"The keys that will be shifted are: {keysToShift}")
        with shelve.open(Address.DB_FILE, writeback = True) as addressBook:
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
                logging.debug(f"Overwriting the address at position {keyToFill} with the address at position {keyToMove}.")
                addressBook[keyToFill] = addressBook[keyToMove]
            for key in addressBook: # After shifting the addresses, make sure the position value of each address matches its key in the address book, since they should be stored in position order.
                addressBook[key].position = int(key)


    '''
    get_sorted_keys() is a static method that returns a list that contains each key from the address book, each converted to an int, and in numeric order.
    Since the address book uses keys that are the position value for each address, they should all be numeric strings.
    '''
    @staticmethod
    def get_sorted_keys():
        logging.debug("Beginning function execution.")
        with shelve.open(Address.DB_FILE) as addressBook:
            numericKeys = []
            for key in addressBook.keys():
                numericKeys.append(int(key))
            return sorted(numericKeys)


    '''
    get_last_position() is a static method that returns the position number of the last address in the address book.
    If the address book is empty, it returns None.
    '''
    @staticmethod
    def get_last_position():
        logging.debug("Beginning function execution.")
        sortedKeys = Address.get_sorted_keys()
        if (sortedKeys):
            logging.info(f"Since the address book is not empty, returning the last position number: {max(sortedKeys)}.")
            return max(sortedKeys)
        else:
            logging.info("Since the address book is empty, returning None.")
            return None
    

    '''
    get_last_section() is a static method that returns the section number of the last address in the address book.
    If the address book is empty, it returns None.
    '''
    @staticmethod
    def get_last_section():
        logging.debug("Beginning function execution.")
        lastPosition = Address.get_last_position()
        if (not lastPosition):
            logging.info("Since address book is empty, returning None.")
            return None
        with shelve.open(Address.DB_FILE) as addressBook:
            logging.info(f"Since address book is not empty, returning the last section number: {addressBook[str(lastPosition)].section}.")
            return addressBook[str(lastPosition)].section