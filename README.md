Eric Wolf
Programming Challenge: Secret Santa

Usage:
  secret_santa --santa <santa_name>  - Returns the person that <santa_name> should buy for
  secret_santa --init <filename>     - Reads a JSON file describing the family for the given year
  secret_santa --dump                - Lists every Secret Santa and person they are buying for

Assumptions:
  1. Minimal UI (command line)
  2. Stateful (each time you enter the same Santa name, you get the same person to buy for)
  3. There must be at least two people in the initial set (for Part 1)
  4. All names will be unique
     a. Capitalization will always be consistent "Rudolph"
     b. Names will be in ASCII (no Unicode or Punycode)
  5. Number of Santa assignments will be small, so complexity is not a concern

Requirements:

Part One:
  1. Each person draws another person at random to buy for
  2. A person cannot be their own Secret Santa

Part Two:
  1. A person cannot be Secret Santa for the same person within the last three years
  2. There must be at least four people in the intial set

Part Three:
  1. A person cannot be Secret Santa for someone in their immediate family
     a. Immediate family includes: spouse, parents, children
     b. A person can be part of two families (a parent in one family and a child in another)