import controller

outputStrings = {
    'introPrompt': '''
Welcome to the Address API!
This tool is meant to be used for the storing and managing of the information for addresses on a mail route.
In this program, you can read existing address entries, create new address entries, update existing address entries, and delete existing address entries.
These address entries are saved to your local computer, and they can be retrieved after exiting this program.
''',
    'menuPrompt': '''Please type a number corresponding to the following options:
1 - Read address entries
2 - Create a new address entry
3 - Update an existing address entry
4 - Delete an existing address entry
5 - Exit program
>>> ''',
'invalidChoicePrompt':          "That is not a valid choice. Please try again.",
'exitConfirm':                  "Are you sure you want to exit? (y/n): >>> ",
'invalidInputPrompt':           "That is not a valid input. Please try again.",
'createPrompt':                 "You have chosen to create a new address entry.",
'updatePrompt':                 "You have chosen to update an existing address entry.",
'deletePrompt':                 "You have chosen to delete an existing address entry.",
'positionToUpdatePrompt':       "Please enter the position of the address entry you would like to update: >>> ",
'positionToDeletePrompt':       "Please enter the position of the address entry you would like to delete: >>> ",
'addressNotFoundPrompt':        "There is no address entry with that position! Please try again.",
'inputIsRequiredPrompt':        "This input is required. Please try again.",
'addressCreatedPrompt':         "Address created:",
'addressUpdatedPrompt':         "Address updated:",
'addressDeletedPrompt':         "Address Deleted:"
}

errorOutputs = {
    'ADDRESS_BOOK_EMPTY': "There are no existing address entries yet! Please choose another option.",

}

def output_address(addressData):
    return {}

def output_address_book(addressesData):
    return {}

def clear_console():
    return {}

print(outputStrings['introPrompt'])

while (True):
    choice = input(outputStrings['menuPrompt'])
    match choice:
        case 1: # Read address entries
            addressesRead = controller.read_all_addresses()
            if (addressesRead['success']):
                print(output_address_book(addressesRead['result']))
            else:
                print(errorOutputs[addressesRead['errorType']])
        case 2: # Create a new address entry
            clear_console()
            # Somehow get input for the address
            addressData = {}
            addressCreate = controller.create_address(addressData)
            if (addressCreate['success']):
                print(output_address(addressCreate['result']))
            else:
                print(errorOutputs[addressCreate['errorType']])
        case 3: # Update an existing address entry
            clear_console()
            # Get user choice for position of address to update
            positionToUpdate = 0
            print(output_address(controller.read_single_address(positionToUpdate)))
            # Somehow get input for the address
            addressData = {}
            addressUpdate = controller.update_address(addressData, positionToUpdate)
            if (addressUpdate['success']):
                print(output_address(addressUpdate['result']))
            else:
                print(errorOutputs[addressUpdate['errorType']])
        case 4: # Delete an existing address entry
            clear_console()
            # Get user choice for position to delete
            positionToDelete = 0
            print(output_address(controller.read_single_address(positionToDelete)))
            # Confirm user wants to delete
            addressDelete = controller.delete_address(positionToDelete)
            if (addressDelete['success']):
                print(output_address(addressDelete['result']))
            else:
                print(errorOutputs[addressDelete['errorType']])
        case 5: # Exit program
            exitInput = input(exitConfirm)
            if (exitInput.strip().lower() == 'y'):
                break
save_data(addressesList, dataFile)