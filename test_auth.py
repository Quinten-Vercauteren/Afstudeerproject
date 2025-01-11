from auth import create_user, authenticate_user

# Test creating a new user
create_user('admin', 'securepassword', 'admin')

# Test authenticating the user
user = authenticate_user('admin', 'securepassword')
if user:
    print(f"Authenticated user: {user.username}, Role: {user.role}")
else:
    print("Authentication failed")
