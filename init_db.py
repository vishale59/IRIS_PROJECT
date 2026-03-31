"""Initialize the MySQL database schema for the IRIS Job Portal."""

from app import app, bootstrap_database, reset_database


def main() -> None:
    reset_database()
    with app.app_context():
        bootstrap_database()
        print("MySQL database reset and tables created successfully.")


if __name__ == "__main__":
    main()
