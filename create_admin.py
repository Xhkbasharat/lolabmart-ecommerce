import getpass

from app import app, db, User


def create_admin():

    print("\n===== LolabMart Admin Setup =====\n")

    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip().lower()

    if not username or not email:
        print("Username and email are required.")
        return

    if len(username) < 3 or len(username) > 80:
        print("Username must contain 3 to 80 characters.")
        return

    if "@" not in email or len(email) > 120:
        print("Please enter a valid email address.")
        return

    with app.app_context():

        existing = User.query.filter(
            (User.username == username)
            | (User.email == email)
        ).first()

        if existing:
            print("This username or email is already registered.")
            return

        password = getpass.getpass("Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if len(password) < 12:
            print("Admin password must be at least 12 characters.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        admin = User(
            username=username,
            email=email,
            role="admin"
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("\nAdmin account created successfully.")
        print("You can now log in to LolabMart.")


if __name__ == "__main__":
    create_admin()
