''' Import required modules '''
from data import data, User, valid_email, user_with_email, user_with_token, user_email_list
from error import InputError, AccessError

def auth_login(email, password):
    '''
    Logs a user in
    Input: email (str), password (str)
    Output: u_id (int) and token (str) as a dict
    '''
    user = user_with_email(email)
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email format')
    elif user is None:
        # Unregistered email
        raise InputError('Unregistered email')
    elif not user.verify_password(password):
        # Incorrect password
        raise InputError('Incorrect password')

    # Update token
    user.token = user.generate_token()

    return {
        'u_id': user.u_id,
        'token': user.token,
    }


def auth_logout(token):
    '''
    Logs a user out
    Input: token (str)
    Output: is_success (bool) as a dict
    '''
    user = user_with_token(token)
    # Check for valid token
    if user is None:
        raise AccessError('Invalid token')

    # Invalidate user token - session stuff in future iterations?
    user.token = ''

    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
    '''
    Registers a user
    Input: email (str), password (str), name_first (str), name_last (str)
    Output: u_id generated (int) and token generated (str) as a dict
    '''
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email')
    elif email in user_email_list():
        # Email in use
        raise InputError('Email already taken')
    elif len(password) < 6:
        # Password length
        raise InputError('Password too short')
    elif len(name_first) not in range(1, 51):
        # name_first length
        raise InputError('First name should be between 1 and 50 characters inclusive')
    elif name_first.isspace():
        # name_first invalid
        raise InputError('First name cannot be empty')
    elif len(name_last) not in range(1, 51):
        # name_last length
        raise InputError('Last name should be between 1 and 50 characters inclusive')
    elif name_last.isspace():
        # name_last invalid
        raise InputError('Last name cannot be empty')

    # Register new user
    new_user = User(email, password, name_first, name_last)
    data['users'].append(new_user)

    return {
        'u_id': new_user.u_id,
        'token': new_user.token,
    }
