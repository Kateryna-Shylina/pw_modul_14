from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

from datetime import datetime

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for the authenticated user with pagination options.

    :param skip: The number of contacts to skip (default is 0).
    :type skip: int
    :param limit: The maximum number of contacts to return (default is 100).
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: A list of contacts for the authenticated user.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a specific contact by ID for the authenticated user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The contact with the specified ID.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for the authenticated user.

    :param body: The data for the new contact.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates a contact by ID for the authenticated user.

    :param body: The updated data for the contact.
    :type body: ContactModel
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The updated contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a contact by ID for the authenticated user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The deleted contact.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contact


@router.patch("/{contact_id}/birthday", response_model=ContactResponse)
async def update_contact_birthday(contact_id: int, birthday_date: datetime, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates the birthday of a contact by ID for the authenticated user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param birthday_date: The new birthday date for the contact.
    :type birthday_date: datetime
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: The updated contact with the new birthday.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found.
    """
    contact = await repository_contacts.update_birthday(contact_id, birthday_date, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(query: str, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Searches contacts by a query string for the authenticated user.

    :param query: The search query (can be part of the first name, last name, or email).
    :type query: str
    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: A list of contacts matching the search query.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.search_contacts(query, current_user, db)
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_birthdays(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts whose birthdays are within the next week for the authenticated user.

    :param db: The database session.
    :type db: Session
    :param current_user: The authenticated user.
    :type current_user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_upcoming_birthdays(current_user, db)
    return contacts


