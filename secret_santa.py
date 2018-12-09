
import argparse
import json
import sqlite3
from random import shuffle


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
    secret_santas = {}
    sqlite_conn = None

    def get(self, ss_name):
        """ for a given name, return the person to gift
        """
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
                santa text NOT NULL,
                gifted text NOT NULL
                )
            """)

        # Clear out the old table
        c.execute("DELETE FROM santas")
        conn.commit()
        c = conn.cursor()

        id = 1
        for santa in self.secret_santas:
            sql = 'INSERT INTO "santas" VALUES({}, "{}","{}")'.format(id, santa, self.secret_santas[santa])
            c.execute(sql)
            id += 1

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
            c.execute("SELECT * FROM santas")
        except Error as e:
            raise SecretSantaSQLNotInitialized(e)

        rows = c.fetchall()

        for row in rows:
            self.secret_santas[row[1]] = row[2]

        conn.close()

    def assign_santas(self):
        """ Assign the random Santas - Extend this function to add more rules about Santa assignments
        """
        gifteds = list(self.secret_santas.keys())

        shuffle(gifteds)

        for santa in self.secret_santas:
            gifted = gifteds[0]

            # Make sure  you can't give to yourself
            if santa == gifted:
                if len(gifteds) < 2:
                    raise RetrySantaAssignments("Ran out of Santas")
                else:
                    gifted = gifteds[1]

            self.secret_santas[santa] = gifted

            gifteds.remove(gifted)

    def assign_santas_with_retry(self):
        """Retry Santa assignments until we get a good one, or we've tried 100 times
        """
        MAX_RETRIES = 100
        for attempt in range(MAX_RETRIES):
            try:
                self.assign_santas()
            except RetrySantaAssignments:
                pass
            else:
                return

        raise TooManySantaAssignmentRetries("Santa Assignment #{} failed".format(MAX_RETRIES))

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
            self.secret_santas[santa] = ""

        if len(self.secret_santas.keys()) < 2:
            raise NotEnoughSantas("Not enough Santas in the input file '{}'".format(filename))

    def dump(self):
        """ List all the Secret Santas and who they are buying for
        """
        for santa in self.secret_santas:
            print("{} buys for {}".format(santa, self.secret_santas[santa]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--santa", help="name of the Santa that wants to know who to buy for")
    parser.add_argument("--dump", action="store_true", help="list all Secret Santas")
    parser.add_argument("--init", help="initialize the Secret Santas from a JSON file")
    args = parser.parse_args()

    ss = SecretSanta()

    if args.init:
        ss.initialize(args.init)

        try:
            ss.assign_santas_with_retry()
        except TooManySantaAssignmentRetries as e:
            print(e.msg)
            exit()

        ss.save()
        ss.dump()
        exit()

    try:
        ss.load()
    except SecretSantaSQLNotInitialized:
        print("You must initialize the Secret Santa database using the --init option.")
        exit()

    if args.dump:
        ss.dump()
    else:
        santa = args.santa
        try:
            gifted = ss.get(santa)
            print("{} buys for {}".format(santa, gifted))
        except:
            print("Santa '{}' not found in Secret Santa list.".format(santa))




