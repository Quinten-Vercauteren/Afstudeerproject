from auth import create_user, authenticate_user

# Test creating a new user with the role of manager
create_user('manager_user', 'securepassword', 'manager')

# Test authenticating the user
user = authenticate_user('manager_user', 'securepassword')
if user:
    print(f"Authenticated user: {user.username}, Role: {user.role}")
else:
    print("Authentication failed")
