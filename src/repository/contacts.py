from typing import List

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel

from datetime import datetime
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy import and_


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Note | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: NoteModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email, phone=body.phone, birthday_date = body.birthday_date, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: NoteUpdate
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Note | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday_date = body.birthday_date  
        db.commit()
    return contact


async def update_birthday(contact_id: int, birthday_date: datetime, user: User, db: Session) -> Contact | None:
    """
    Updates a birthday of single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param birthday_date: The data for the birthday.
    :type birthday_date: datetime
    :param user: The user to update the birthday for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Note | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.birthday_date = birthday_date
        db.commit()
        db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session)  -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Note | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(query: str, user: User, db: Session) -> List[Contact]:
    """
    Search contacts with the specified string.

    :param query: string query.
    :type query: str
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contacts, or None if it does not exist.
    :rtype: Note | None
    """
    return db.query(Contact).filter(and_(Contact.user_id == user.id, ((Contact.first_name.ilike(f"%{query}%")) | (Contact.last_name.ilike(f"%{query}%")) | (Contact.email.ilike(f"%{query}%"))))
    ).all()


async def get_upcoming_birthdays(user: User, db: Session) -> List[Contact]:
    """
    Return contacts whose birthday are in a week.

    :param user: The user to update the birthday for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contacts whose birthday are in a week.
    :rtype: Note | None
    """
    today = datetime.now().date()
    days_ahead = [(today + timedelta(days=i)).strftime('%m-%d') for i in range(8)]

    contacts = db.query(Contact).filter(and_(Contact.user_id == user.id, (func.to_char(Contact.birthday_date, 'MM-DD').in_(days_ahead)))
    ).all()
    return contacts