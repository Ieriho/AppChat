import re

class Checker:
    """
    Provides user input and validation email, password and name
    """

    def check_email(self):
        while True:
            email_str = input('Input email: ')
            email_str = email_str.strip()
            pattern = r'^([\.a-z0-9_-]+)@([\.a-z-]+)\.([a-z\.]+)$'
            match = re.search(pattern, email_str)
            if match:
                return match.group()
            else:
                print('It seems, the email is wrong')

    def check_password(self):
        while True:
            password = input('Input password: ')

            if len(password) > 3 and len(password) < 15:
                repeat_pw = input('Enter password again (checking): ')
                if password == repeat_pw:
                    return password
                else:
                    print('Password is wrong, try again')
            else:
                print('Length of password must be between 3 and 15 characters')

    def check_name(self):
        while True:
            name = input('Input name: ')
            pattern = r'^[-_\w]{4,12}$'
            match = re.search(pattern, name)
            if match:
                return match.group()
            else:
                print('Length of name must be between 3 and 12 characters '
                      'and contain only letters, numbers and characters "_" or "-" ')
