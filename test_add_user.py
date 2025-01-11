from models import add_user, get_user

# Test adding a new user
add_user('admin', 'securepassword', 'admin')

# Retrieve and print the user to verify
user = get_user('admin')
print(f"Username: {user.username}, Role: {user.role}")
