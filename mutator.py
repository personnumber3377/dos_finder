
import random
import string

MAXIMUM_LENGTH = 100_000 # Absolute maximum length of the generated data.

ALLOWED_CHARS = string.printable # All allowed characters.

NEW_DATA_CHANCE = 0.01 # Possibility of creating an entirely new string.

MAX_REPEAT_COUNT = 100_00 # Maximum amount of repetitions

MAX_REPEAT_COUNT_LINEAR = 1000

MIN_REPEAT_COUNT_LINEAR = 200

MAX_REPEAT_TOKEN_LENGTH = 5 # Maximum length of the string which to repeat.

MAX_REPEAT_STRING_COUNT = 10 # Maximum amount of repeated strings, for example if we have three of these then this will generate a string like "ababababccccccccccccccqwertyqwertyqwerty" (three repeating substrings)

EXISTING_SUBSTRING_CHANCE = 0.95 # Change to get an existing substring from the string


MAX_SUBSTRING_LENGTH = 10

REPLACE_CHANCE = 0.3 # Chance to replace the original shit string. If not this, then the data will be inserted at a random index.

def f(x: float) -> float: # Function (for now this is "(x + 0.1) ** 10") (this is assumed to be growing in the period 0 <= x <= 1)
	return (x + 0.6) ** 3 + max(MIN_REPEAT_COUNT_LINEAR, round(MAX_REPEAT_COUNT_LINEAR * x))

THING = f(1.0) # Precalculated


def dist_function(x: float) -> float: # Distribution. x is assumed to be between 0 <= x <= 1
	assert 0 <= x <= 1
	return f(x) / THING # Random value divided by maximum value. (Maximum is assumed to be at x = 1)




def distribution(c: int) -> int: # Returns a random number (max is c and minimum is zero). This function is biased against small numbers (the probability of generating a relatively small number is high, whileas the probability of generating a comparatively large number is small.)
	return round(c * dist_function(chance()))


def chance() -> float: # Shorthand
	return random.random()

def c(const: float) -> bool: # Rolls a dice and returns true with a probability of "const"
	return chance() <= const

def rnum(n: int) -> int: # Shorthand
	if n == 0:
		return 0
	return random.randrange(0, n)

def stringmult(string: bytes, c: int) -> bytes: # Multiplies string by c times.
	return (string * c)[:MAXIMUM_LENGTH] # Just automatically truncate the string

def rand_ascii_string(n: int) -> bytes: # Generates n random ascii bytes (taken from string.printable)
	return bytes([ord(random.choice(ALLOWED_CHARS)) for _ in range(n)]) # Create array of allowed bytes and convert to bytes

def generate_repeating(n: int) -> bytes: # Generate a random repeating string and repeat it n times
	#return stringmult(rand_ascii_string(rnum(MAX_REPEAT_TOKEN_LENGTH)), n)
	return stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), n)

def generate_new() -> bytes: # Generate a new ascii string.
	repeat_count = rnum(MAX_REPEAT_STRING_COUNT)

	out = b"" # Final generated string

	for i in range(repeat_count): # Generate "repeat_count" repeating strings.

		out += generate_repeating(rnum(MAX_REPEAT_COUNT))

	return out

def get_substr(data: bytes) -> bytes:
	rand_ind = min(rnum(len(data)), MAX_SUBSTRING_LENGTH)
	#length = distribution(len(data[rand_ind:])-1) # The length should be based on a certain distribution
	length = rnum(len(data[rand_ind:])-1)
	#print("length == "+str(length))
	res = data[rand_ind:rand_ind+length]
	#print("res == "+str(res))
	return res, rand_ind # Return the substring






def mutate_existing(data: bytes) -> bytes:

	# Mutation count:

	# Get a random substring and then multiply it and then put it into a random place.

	# substr, rand_ind = get_substr(data) if c(EXISTING_SUBSTRING_CHANCE) else (None, None)

	substr, rand_ind = get_substr(data) if True else (None, None)

	if True and substr:
		# Just cut out the original string and then add the multiplied substring in there.
		#assert substr in data # Sanity checking

		rep_count = distribution(MAX_REPEAT_COUNT)
		#print("stringmult(substr, distribution(MAX_REPEAT_COUNT)) == "+str(stringmult(substr, rep_count)))
		#print("substr == "+str(substr))
		#print("rep_count == "+str(rep_count))
		multiplication = stringmult(substr, rep_count)
		#print("multiplication == "+str(multiplication))
		#if b"("*1000 in multiplication:
		#	print("!!!")
		#	data = data[place_index:] + multiplication + data[place_index:]
		#	print("data == "+str(data))
		#	exit(0)

		data = data[:rand_ind] + multiplication + data[rand_ind+len(substr):]
		#print("data == "+str(data))

		return data
	else:
		# Place somewhere else.

		#assert substr in data # Sanity checking
		place_index = rnum(len(data)-1)
		#assert place_index != -1
		#data = data.replace(substr, b"") # Remove the data
		rep_count = distribution(MAX_REPEAT_COUNT)
		#print("stringmult(substr, distribution(MAX_REPEAT_COUNT)) == "+str(stringmult(substr, rep_count)))
		#print("substr == "+str(substr))
		#print("rep_count == "+str(rep_count))

		multiplication = stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), rep_count)

		#print("multiplication == "+str(multiplication))

		'''
		if b"("*1000 in multiplication:
			print("!!!")
			data = data[place_index:] + multiplication + data[place_index:]
			print("data == "+str(data))
			exit(0)
		'''

		data = data[place_index:] + multiplication + data[place_index:]

		return data



	return data




def mutate(data: bytes): # Main mutator entry point. Returns a mutated version of the data.

	if c(NEW_DATA_CHANCE): # Create new string.
		return generate_new()
	else: # Mutate existing.
		return mutate_existing(data)


if __name__=="__main__": # For testing only (well, fuzzing is testing, but you know what I mean :D )
	#print("random.choice(ALLOWED_CHARS) == "+str(random.choice(ALLOWED_CHARS)))
	#print(rand_ascii_string(10)) # Generate a random string

	MAX_MUT_COUNT = 10

	#while True:

	TEST_COUNT = 100000

	for _ in range(TEST_COUNT):

		#mut_count = rnum(MAX_MUT_COUNT)
		mut_count = 1
		res = b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		for _ in range(mut_count):
			#print("len(res) == "+str(len(res)))
			res = mutate_existing(res)
			if len(res) > MAXIMUM_LENGTH: # Bounds check
				res = res[:MAXIMUM_LENGTH]

		#print(mutate_existing(b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"))
		#print(res)
		#print("len(res) == "+str(len(res)))
		if b"("*1000 in res and b")"*1000 in res:
			print(res)
			break
	exit(0) # Return succesfully


