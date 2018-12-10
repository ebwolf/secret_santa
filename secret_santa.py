
import argparse
import json
import sqlite3
import pprint
from random import shuffle


MINIMUM_SECRET_SANTAS = 4
MAX_ASSIGNMENT_RETRIES = 500

class Error(Exception):
    """Base class for other exceptions"""
    pass

class MissingSantasKey(Error):
    """Raised when Santas key missing from JSON"""
    pass

class NotEnoughSantas(Error):
    """Raised when not enough Santas in the input file"""
    pass

class SecretSantaSQLNotInitialized(Error):
    """Secret Santa SQLite Database has not been initialized"""
    pass

class NotInSecretSantaList(Error):
    """Name is not found in the Secret Santa list"""
    pass

class RetrySantaAssignments(Error):
    """Simplify Santa assignment difficulties trough retries"""
    pass

class TooManySantaAssignmentRetries(Error):
    """Santa Assignment retried too many times"""
    pass

class SecretSanta:
    secret_santas_years = {}
    secret_santas = {}
    families = {}
    candidates = []
    year = ""
    valid_years = []

    def get(self, ss_name):
        """ for a given name, return the person to gift
        """
        if self.year not in self.valid_years:
            raise NotInSecretSantaList("{} is not a valid year. You may need to make assignments.".format(self.year))

        self.secret_santas = self.secret_santas_years[self.year].copy()

        if ss_name not in self.secret_santas:
            raise NotInSecretSantaList("'{}' is not in the Secret Santa list.".format(ss_name))

        return self.secret_santas[ss_name]

    def save(self):
        """ Write the Secret Santa list to SQLite for persistent storage
        """
        # Create the database connection, this will create the file if it doesn't exist
        conn = sqlite3.connect("secret_santa.sqlite")

        # Create the table
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS santas (
                id integer PRIMARY KEY AUTOINCREMENT,
                year text NOT NULL,
                santa text NOT NULL,
                gifted text NOT NULL
                )
            """)

        # Clear out the old table
        c.execute("DELETE FROM santas")
        conn.commit()
        c = conn.cursor()

        id = 1
        for year in self.secret_santas_years:
            self.secret_santas = self.secret_santas_years[year].copy()

            for santa in self.secret_santas:
                sql = 'INSERT INTO "santas" VALUES({}, {}, "{}","{}")'\
                    .format(id, year, santa, self.secret_santas[santa])
                c.execute(sql)
                id += 1

        # Create the table
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id integer PRIMARY KEY AUTOINCREMENT,
                santa text NOT NULL,
                family integer NOT NULL
                )
            """)

        # Clear out the old table
        c.execute("DELETE FROM families")
        conn.commit()
        c = conn.cursor()

        # Write the families to SQLite
        famidx = 1
        for famnum in self.families:
            family = self.families[famnum]
            for fammbr in family:
                sql = 'INSERT INTO "families" VALUES({}, "{}", {})'\
                    .format(id, fammbr, famidx)
                c.execute(sql)
                id += 1
            famidx += 1

        conn.commit()
        conn.close()

    def load(self):
        """ Read the Secret Santas from SQLite
        """
        try:
            conn = sqlite3.connect("secret_santa.sqlite")
        except Error as e:
            raise SecretSantaSQLNotInitialized(e)

        c = conn.cursor()

        try:
            c.execute("SELECT DISTINCT year FROM santas")
        except Error as e:
            raise SecretSantaSQLNotInitialized(e)

        rows = c.fetchall()

        # Initialize Secret Santa lists for each year in the database
        for row in rows:
            self.valid_years.append(row[0])
            self.secret_santas_years[row[0]] = {}

        # Get all the Santas
        try:
            c.execute("SELECT * FROM santas")
        except Error as e:
            raise SecretSantaSQLNotInitialized(e)

        rows = c.fetchall()

        for row in rows:
            row_year = row[1]
            self.secret_santas_years[row_year][row[2]] = row[3]

        # Load the families
        try:
            c.execute("Select * FROM families")
        except Error as e:
            raise SecretSantaSQLNotInitialized(e)

        rows = c.fetchall()

        # Load each family from the database
        for row in rows:
            if row[2] not in self.families:
                self.families[row[2]] = []

            if row[1] not in self.families[row[2]]:
                self.families[row[2]].append(row[1])

        conn.close()

    def find_gifted(self, santa):
        """ Find someone for this Santa to give to
        """
        candidates = self.candidates.copy()

        # 1. Remove this Santa
        if santa in candidates:
            candidates.remove(santa)

            if len(candidates) == 0:
                raise RetrySantaAssignments("Ran out of candidates")

        # 2. Remove candidates given to in the prior two years
        prior_year = str(int(self.year)-1)

        if prior_year in self.valid_years:
            prior_gifted = self.secret_santas_years[prior_year][santa]

            if prior_gifted in candidates:
                candidates.remove(prior_gifted)
                if len(candidates) == 0:
                    raise RetrySantaAssignments("Ran out of candidates")

        prior_year = str(int(prior_year) - 1)

        if prior_year in self.valid_years:
            prior_gifted = self.secret_santas_years[prior_year][santa]
            if prior_gifted in candidates:
                candidates.remove(prior_gifted)
                if len(candidates) == 0:
                    raise RetrySantaAssignments("Ran out of candidates")

        if len(candidates) == 0:
            raise RetrySantaAssignments("Ran out of candidates")

        # 3. Remove candidates in the same families
        for famidx in self.families:
            if santa in self.families[famidx]:
                for fammbr in self.families[famidx]:
                    if fammbr in candidates:
                        candidates.remove(fammbr)

        if len(candidates) == 0:
            raise RetrySantaAssignments("Ran out of candidates")

        return candidates[0]

    def assign_santas(self):
        """ Assign the random Santas - Extend this function to add more rules about Santa assignments
        """
        self.candidates = list(self.secret_santas.keys())

        shuffle(self.candidates)

        for santa in self.secret_santas:
            gifted = self.find_gifted(santa)
            self.secret_santas[santa] = gifted
            self.candidates.remove(gifted)

    def assign_santas_with_retry(self):
        """Retry Santa assignments until we get a good one, or we've tried 100 times
        """
        for attempt in range(MAX_ASSIGNMENT_RETRIES):
            try:
                self.assign_santas()
            except RetrySantaAssignments:
                pass
            else:
                return

        pprint.pprint(self.secret_santas)
        raise TooManySantaAssignmentRetries("Santa Assignment #{} failed".format(MAX_ASSIGNMENT_RETRIES))

    def reassign_santas(self, year):
        """Reassign Santas for the specified year
        """
        for santa in self.secret_santas:
            self.secret_santas[santa] = ""

        try:
            self.assign_santas_with_retry()
        except Exception as error:
            print(error)
        else:
            self.secret_santas_years[year] = self.secret_santas.copy()
            return

    def initialize(self, filename):
        """ Initialize the Secret Santa database from a JSON file
        """
        # open filename and init the secret_santas list
        with open(filename) as json_data:
            json_slist = json.load(json_data)
            json_data.close()

        if json_slist.get('santas') is None:
            raise MissingSantasKey("Input file {} does not contain the 'santas' key".format(filename))

        santas = json_slist['santas']

        for santa in santas:
            self.secret_santas[santa[0]] = ""

            # Save the Santa in the families
            if santa[1] not in self.families:
                self.families[santa[1]] = []

            if santa[2] not in self.families:
                self.families[santa[2]] = []

            if santa[0] not in self.families[santa[1]]:
                self.families[santa[1]].append(santa[0])

            if santa[0] not in self.families[santa[2]]:
                self.families[santa[2]].append(santa[0])

        if len(self.secret_santas.keys()) < MINIMUM_SECRET_SANTAS:
            raise NotEnoughSantas("Not enough Santas in the input file '{}'".format(filename))

        self.valid_years.append(self.year)

    def dump(self):
        """ List all the Secret Santas and who they are buying for
        """
        if self.year not in self.valid_years:
            raise NotInSecretSantaList("{} is not a valid year. You may need to make assignemnts.".format(self.year))

        self.secret_santas = self.secret_santas_years[self.year].copy()

        print("Listing all Secret Santa assignemnts for {}".format(self.year))
        for santa in self.secret_santas:
            print("{} buys for {}".format(santa, self.secret_santas[santa]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--santa", help="name of the Santa that wants to know who to buy for")
    parser.add_argument("--year", required=True, help="year of inquiry / assignment / initialization")
    parser.add_argument("--init", help="initialize the Secret Santas from a JSON file")
    parser.add_argument("--assign", action="store_true", help="used with --year to re-assign Santas for that year")
    parser.add_argument("--dump", action="store_true", help="list all Secret Santas")
    args = parser.parse_args()

    ss = SecretSanta()

    ss.year = args.year

    # Initialize the Secret Santas
    if args.init:
        ss.initialize(args.init)

        try:
            ss.assign_santas_with_retry()
        except TooManySantaAssignmentRetries as e:
            print(e.msg)
            exit()

        ss.secret_santas_years[ss.year] = ss.secret_santas.copy()

        ss.save()
        ss.dump()
        exit()

    try:
        ss.load()
    except SecretSantaSQLNotInitialized:
        print("You must initialize the Secret Santa database using the --init option.")
        exit()

    # Assign a new set of Secret Santas for the specified year
    if args.assign:
        ss.secret_santas = ss.secret_santas_years[ss.valid_years[0]].copy()
        ss.reassign_santas(ss.year)
        ss.valid_years.append(ss.year)
        ss.save()

        try:
            ss.dump()
        except Exception as error:
            print(error)
        exit()

    if args.dump:
        # Display all of the Secret Santa assignments
        try:
            ss.dump()
        except Exception as error:
            print(error)
    else:
        # Display the Secret Santa assignment for one person
        santa = args.santa
        try:
            gifted = ss.get(santa)
            print("{} buys for {}".format(santa, gifted))
        except Exception as error:
            print(error)




