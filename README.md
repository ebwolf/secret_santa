Eric Wolf ebwolf@gmail.com

Programming Challenge: Secret Santa, Part 3

Usage:

  secret_santa --santa <santa_name> --year <year> 
           Returns the person that <santa_name> should buy for in the given year
  
  secret_santa --init <filename> --year <year> 
           Reads a JSON file describing the family for the given year
  
  secret_santa --dump --year <year>
           Lists every Secret Santa and person they are buying for

  secret_santa --assign --year <year>
           Creates a new Secret Santa assignment for the given year

NOTES: 

1. I used a very crude method of assigning Secret Santas and just relied on brute
force with retries to make it work. The assignment of Secret Santas only runs once a year.
My tests ensure that this brute force method isn't too intensive with a dataset of 10 family
members. Essentially, 1000 executes are completed in less than 1 second. Significantly larger
 data sets may require a better algorithm.
 
2. Repeat assignments are only tested backwards in time but the program allows you to specify a year.
Therefore, if you --init for --year 2016, then --assign for year --2019, then assign for --years
2017 and 2018, there will be no checks for repeats in 2020 unless you reassign.

3. The "test_data_stress.json" file will fail in the third year because there are only 2 possible 
assignments for one of the Santas and the combination of the no-family member and no repeat in 3 years
rules. I didn't have time to write a validation during initialization for enough members of other 
families to guarantee the 3-year rule can be met for each Secret Santa.

4. The database is not meant to be backwards compatible. Please delete "secret_santa.sqlite" if you
test run the code between parts. That is, delete the database completely after running Part 1
and before running Part 2. Again, delete the database completely after running Part 2 and before
running Part 3. If I spent more time, I would encode a version in the database.

Assumptions:

  1. Minimal UI (command line)
  2. Stateful (each time you enter the same Santa name, you get the same person to buy for)
  3. There must be at least two people in the initial set (for Part 1)
  4. All names will be unique
     * Capitalization will always be consistent. e.g., "Rudolph"
     * Names will be in ASCII (no Unicode or Punycode)
  5. Number of Santa assignments will be small, so complexity is not a concern
     * Stress tests are written to prove out this assumption (1000 iterations < 1 second)
  6. No method of adding family members in future years was specified
     * Family members remain constant

Requirements:

Part One:
  1. Each person draws another person at random to buy for
  2. A person cannot be their own Secret Santa

Part Two:
  1. A person cannot be Secret Santa for the same person within the last three years
  2. There must be at least four people in the intial set

Part Three:
  1. A person cannot be Secret Santa for someone in their immediate family
     * Immediate family includes: spouse, parents, children
     * A person can be part of two families (a parent in one family and a child in another)
     * Families will be static and managed as a separate table.
     * For each Santa, there must be at least three non-Family members in the pool
  2. JSON data will be a list of lists, each inner list provides a Santa and two family IDs
     * If I had more time, I'd create an SQL relation between the Santas table and a families table
     * A santa can belong to two families because a Santa can be a child of one Santa (Grandfather) 
       and a parent of another (grandchild)