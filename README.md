Eric Wolf
Programming Challenge: Secret Santa, Part 2

Usage:

  secret_santa --santa <santa_name> --year <year> 
           Returns the person that <santa_name> should buy for in the given year
  
  secret_santa --init <filename> --year <year> 
           Reads a JSON file describing the family for the given year
  
  secret_santa --dump --year <year>
           Lists every Secret Santa and person they are buying for

  secret_santa --assign --year <year>
           Creates a new Secret Santa assignment for the given year

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