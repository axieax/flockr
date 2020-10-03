# Test file for channel.py
from channel import channel_invite, channel_details, channel_leave, channel_join, channel_addowner, channel_removeowner, channel_messages
from channels import channels_create
from auth import auth_register
from error import InputError, AccessError
from other import clear
import pytest

def test_channel_addowner():
    clear()
    owner = auth_register('bobsmith@gmail.com', 'password', 'Bob', 'Smith')
    channel = channels_create(owner['token'], 'Test channel', True)
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')
    
    # Checking if someone can be added (verified if they can be immediately removed)
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])
    
    # Addding someone who is already the owner
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    with pytest.raises(InputError):
        channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_addowner(owner['token'], channel['channel_id'] + 100, user['u_id'])
    
    # Authorised user is not the owner
    with pytest.raises(AccessError):
        channel_addowner(user['token'], channel['channel_id'], user['u_id'])


def test_channel_removeowner():
    clear()
    owner = auth_register('bobsmith@gmail.com', 'password', 'Bob', 'Smith')
    channel = channels_create(owner['token'], 'Test channel', True)
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')

    # Checking if someone can be removed (Add then remove)
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    # Removing someone who is already removed (no longer an owner)
    with pytest.raises(InputError):
        channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])
    
    # Authorised user is not an owner
    with pytest.raises(AccessError):
        channel_removeowner(user['token'], channel['channel_id'], owner['u_id'])

    # Addding someone to be removed
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_removeowner(owner['token'], channel['channel_id'] + 100, user['u_id'])

    # Authorised user can remove owner (since they are now another owner)
    channel_removeowner(user['token'], channel['channel_id'], owner['u_id'])


def test_channel_invite():
    clear()
    user1 = auth_register('user1@gmail.com', 'password1', 'John', 'Smith')
    user2 = auth_register('user2@gmail.com', 'password2', 'Steve', 'Jackson') 
    # User 1 creates a new channel, and invites User 2
    test_channel1 = channels_create(user1['token'], 'Test Channel 1', True)
    channel_invite(user1['token'], test_channel1['channel_id'], user2['u_id'])

    # Checking if User 2 is a member of the channel (whether they can access channel details)
    channel_details(user2['token'], test_channel1['channel_id'])
    
    test_channel2 = channels_create(user1['token'], 'Test Channel 2', True)

    # Channel ID does not refer to a valid channel
    with pytest.raises(InputError):
        channel_invite(user1['token'], test_channel2['channel_id'] + 100, user2['u_id'])

    # User ID does not refer to a valid user
    with pytest.raises(InputError):
        channel_invite(user1['token'], test_channel2['channel_id'], user2['u_id'] + 100)

    # Authorised user is not a member of the channel
    with pytest.raises(AccessError):
        user3 = auth_register('user3@gmail.com', 'password3', 'Jim', 'Johnson')
        channel_invite(user3['token'], test_channel2['channel_id'], user2['u_id'])


def test_channel_join():
    clear()
    owner = auth_register('petermichaels@gmail.com', 'password', 'Peter', 'Michaels')
    channel1 = channels_create(owner['token'], 'Channel 1', True)
    user = auth_register('kimwilliams@gmail.com', 'password', 'Kim', 'Williams')

    # Checking if a user can join a channel (verified if they can leave the channel)
    channel_join(user['token'], channel1['channel_id'])
    channel_leave(user['token'], channel1['channel_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_join(user['token'], channel1['channel_id'] + 100)

    # Channel ID is a private channel (authorised user is not a global owner)
    channel2 = channels_create(owner['token'], 'Channel 2', False)
    with pytest.raises(AccessError):
        channel_join(user['token'], channel2['channel_id'])


def test_channel_leave():
    clear()
    owner = auth_register('petermichaels@gmail.com', 'password', 'Peter', 'Michaels')
    channel = channels_create(owner['token'], 'Test Channel', True)
    user = auth_register('kimwilliams@gmail.com', 'password', 'Kim', 'Williams')

    # Checking if a user can leave (verified if not able to access channel details)
    channel_join(user['token'], channel['channel_id'])
    channel_details(user['token'], channel['channel_id'])
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(user['token'], channel['channel_id'])
    
    # Channel ID is not a valid channel
    channel_join(user['token'], channel['channel_id'])
    with pytest.raises(InputError):
        channel_leave(user['token'], channel['channel_id'] + 100)
    
    # Authorised user is not a member of the channel (leaving channel twice)
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_leave(user['token'], channel['channel_id'])

    # Checking if an owner can leave (verified if not able to access channel details
    # and not able to further remove owners)
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_leave(owner['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])
    
    clear()


def test_channel_details():
    clear()
    owner = auth_register('liambrown@gmail.com', 'password', 'Liam', 'Brown')
    channel = channels_create(owner['token'], 'Test Channel', True)
    user = auth_register('victorzhang@gmail.com', 'password', 'Victor', 'Zhang')

    # Checking if member of channel can check channel details
    channel_join(user['token'], channel['channel_id'])
    channel_details(user['token'], channel['channel_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_details(user['token'], channel['channel_id'] + 100)

    # Authorised user is not a member of the channel
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(user['token'], channel['channel_id'])


# It is not feasible to do valid testing for channel_messages during iteration one
def test_channel_messages():
    pass
    # clear()
    # # Standard error check
    # user = auth_register('testing@gmail.com', 'password', 'Test', 'User')
    # channel = channels_create(user['token'], 'Test Channel', True)
    # message_send(user['token'], channel['channel_id'], 'Test message')
    # # Invalid channel_id
    # with pytest.raises(InputError):
    #     channel_messages(user['token'], channel['channel_id'] + 100, 0)
    # # Invalid token
    # with pytest.raises(AccessError):
    #     channel_messages('', channel['channel_id'], 0)
    # # Random user
    # random_user = auth_register('test@gmail.com', 'password', 'Test', 'Mee')
    # with pytest.raises(AccessError):
    #     channel_messages(random_user['token'], channel['channel_id'], 0)
    # # Invalid start index - unable to be tested in iteration one
    # with pytest.raises(InputError):
    #     channel_messages(user['token'], channel['channel_id'], 0)