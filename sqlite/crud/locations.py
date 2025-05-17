from sqlalchemy.orm import Session
from sqlalchemy import or_

from sqlite import models
from sqlite.schemas import LocationCreateOrUpdateClass


def get_all_locations(db: Session):
    """Get all locations from the database"""
    return db.query(models.LocationModel)


def get_location_by_id(location_id: int, db: Session):
    """Get a single location by id from the database"""
    return (
        db.query(models.LocationModel)
        .filter(models.LocationModel.id == location_id)
        .first()
    )


def get_location_by_bluetooth_address(bluetooth_address: str, db: Session):
    """Get a single location by bluetooth address from the database"""
    return (
        db.query(models.LocationModel)
        .filter(models.LocationModel.bluetooth_address == bluetooth_address)
        .first()
    )


def get_location_by_coordinates(coordinates: str, db: Session):
    """Get a single location by coordinates from the database"""
    return (
        db.query(models.LocationModel)
        .filter(models.LocationModel.coordinates == coordinates)
        .first()
    )


def get_location(bluetooth_address: str, coordinates: str, db: Session):
    (
        """Get a single location by both bluetooth address and coordinates"""
        + """ from the database"""
    )
    return (
        db.query(models.LocationModel)
        .filter(
            or_(
                models.LocationModel.bluetooth_address == bluetooth_address,
                models.LocationModel.coordinates == coordinates,
            )
        )
        .first()
    )


def create_location(location: LocationCreateOrUpdateClass, db: Session):
    """Create a new location in the database"""
    db_location = models.LocationModel(**location.__dict__)
    db.add(db_location)
    db.commit()

    return db_location


def update_location(
    location: LocationCreateOrUpdateClass,
    db_location: models.LocationModel,
    db: Session,
):
    """Update a location in the database"""
    db_location.update(location=location)
    db.commit()

    return db_location


def delete_location(db_location: models.LocationModel, db: Session):
    """Delete a location from the database"""
    db.delete(db_location)
    db.commit()

    return {"detail": "Deleted successfully"}
