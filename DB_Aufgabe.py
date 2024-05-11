from sqlalchemy import create_engine, Column, Integer, String, Date, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()
engine = create_engine('sqlite:///databas.db')
Session = sessionmaker(bind=engine)

# Association Table
schliessfach_person = Table('schliessfach_person', Base.metadata,
                            Column('schliessfach_sid', Integer, ForeignKey('schliessfach.sid')),
                            Column('person_pid', Integer, ForeignKey('person.pid'))
                            )


class Eigentümer(Base):
    __tablename__ = 'eigentümer'

    unternehmensname = Column(String, primary_key=True)
    laendercode = Column(String)

    def __init__(self, unternehmensname, laendercode):
        self.unternehmensname = unternehmensname
        self.laendercode = laendercode


class Person(Base):
    __tablename__ = 'person'

    pid = Column(Integer, primary_key=True)
    vorname = Column(String)
    nachname = Column(String)

    def __init__(self, pid, vorname, nachname):
        self.pid = pid
        self.vorname = vorname
        self.nachname = nachname


class Schliessfach(Base):
    __tablename__ = 'schliessfach'

    sid = Column(Integer, primary_key=True)
    erstellungsdatum = Column(Date)
    eigentümer_unternehmensname = Column(String, ForeignKey('eigentümer.unternehmensname'))
    eigentümer = relationship('Eigentümer')
    berechtigte = relationship('Person', secondary=schliessfach_person)

    def __init__(self, sid, erstellungsdatum):
        self.sid = sid
        self.erstellungsdatum = erstellungsdatum


def db_fill():
    session = Session()

    # Eigentümer
    eigentümer1 = Eigentümer("Unternehmen 1", "DE")
    eigentümer2 = Eigentümer("Unternehmen 2", "US")
    session.add_all([eigentümer1, eigentümer2])

    # Schließfächer
    schliessfach1 = Schliessfach(1, date.today())
    schliessfach1.eigentümer = eigentümer1

    schliessfach2 = Schliessfach(2, date.today())
    schliessfach2.eigentümer = eigentümer2

    schliessfach3 = Schliessfach(3, date.today())
    schliessfach3.eigentümer = eigentümer1

    schliessfach4 = Schliessfach(4, date.today())
    schliessfach4.eigentümer = eigentümer2

    person1 = Person(1, "Max", "Mustermann")
    person2 = Person(2, "John", "Doe")
    person3 = Person(3, "Jane", "Smith")

    schliessfach1.berechtigte = [person1, person2]
    schliessfach2.berechtigte = [person2]
    schliessfach3.berechtigte = [person1, person3]
    schliessfach4.berechtigte = [person3]

    session.add_all([schliessfach1, schliessfach2, schliessfach3, schliessfach4])
    session.add_all([person1, person2, person3])

    session.commit()
    session.close()


def menu():
    while True:
        print("\n--- Menü ---")
        print("1. Ausgabe aller Eigentümer")
        print("2. Ausgabe aller Schließfächer eines Eigentümers")
        print("3. Ausgabe aller Personen")
        print("4. Ausgabe aller Schließfächer eines Berechtigten")
        print("0. Beenden")

        choice = input("Wählen Sie eine Option: ")

        if choice == "1":
            show_all_eigentümer()
        elif choice == "2":
            show_schließfächer_of_eigentümer()
        elif choice == "3":
            show_all_personen()
        elif choice == "4":
            show_schließfächer_of_berechtigter()
        elif choice == "0":
            break
        else:
            print("Ungültige Eingabe!")


def show_all_eigentümer():
    session = Session()
    eigentümer = session.query(Eigentümer).all()
    session.close()

    for e in eigentümer:
        print(f"Unternehmensname: {e.unternehmensname}, Ländercode: {e.laendercode}")


def show_schließfächer_of_eigentümer():
    session = Session()
    unternehmensname = input("Geben Sie den Unternehmensnamen des Eigentümers ein: ")
    eigentümer = session.query(Eigentümer).filter_by(unternehmensname=unternehmensname).first()

    if eigentümer:
        schließfächer = session.query(Schliessfach).filter_by(eigentümer=eigentümer).all()

        for s in schließfächer:
            print(f"Schließfach-ID: {s.sid}, Erstellungsdatum: {s.erstellungsdatum}")
    else:
        print("Eigentümer nicht gefunden!")

    session.close()


def show_all_personen():
    session = Session()
    personen = session.query(Person).all()
    session.close()

    for p in personen:
        print(f"ID: {p.pid}, Vorname: {p.vorname}, Nachname: {p.nachname}")


def show_schließfächer_of_berechtigter():
    session = Session()
    personen_id = input("Geben Sie die Personen-ID des Berechtigten ein: ")
    person = session.query(Person).filter_by(pid=personen_id).first()

    if person:
        schließfächer = session.query(Schliessfach).join(Schliessfach.berechtigte).filter_by(pid=person.pid).all()

        for s in schließfächer:
            print(f"Schließfach-ID: {s.sid}, Erstellungsdatum: {s.erstellungsdatum}")
    else:
        print("Person nicht gefunden!")

    session.close()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    db_fill()
    menu()
