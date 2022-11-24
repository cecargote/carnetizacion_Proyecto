from sqlalchemy.orm import Session

from schemas.person import PersonCreate
from db.models.person import Person


def create_new_person(person: PersonCreate,db: Session):
    person_object = Person(**person.dict())
    db.add(person_object)
    db.commit()
    db.refresh(person_object)
    return person_object

def retreive_person(ci: str, db: Session):
    item = db.query(Person).filter(Person.ci == ci).first()
    return item

def list_persons(db: Session):
    persons = db.query(Person).all()
    return persons

def update_person_by_ci(ci: str, person: PersonCreate, db: Session):
    exist_person = db.query(Person).filter(Person.ci == ci)
    if not exist_person.first():
        return 0
    exist_person.update(person.__dict__)
    db.commit()
    return 1