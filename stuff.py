
import random
import string
import math

MAXIMUM_LENGTH = 100_000 # Absolute maximum length of the generated data.
ALLOWED_CHARS = string.printable # All allowed characters.
PUNCTUATION_CHANCE = 0.9
NEW_DATA_CHANCE = 0.01 # Possibility of creating an entirely new string.
MAX_REPEAT_COUNT = 10_0000 # Maximum amount of repetitions
MAX_REPEAT_LENGTH = 10_0000 # Maximum length of the repeating stuff
MAX_REPEAT_TOKEN_LENGTH = 500 # Maximum length of the string which to repeat.
MAX_REPEAT_STRING_COUNT = 100 # Maximum amount of repeated strings, for example if we have three of these then this will generate a string like "ababababccccccccccccccqwertyqwertyqwerty" (three repeating substrings)
EXISTING_SUBSTRING_CHANCE = 0.95 # Change to get an existing substring from the string
MAX_SUBSTRING_LENGTH = 10
REPLACE_CHANCE = 0.3 # Chance to replace the original shit string. If not this, then the data will be inserted at a random index.

def distribution(c):
	return random.randrange(1,c*10)

def custom_mutator(data, max_size, seed, native_mutator):
	# Just call mutate and see what happens...
	if isinstance(data, bytearray):
		convert = True
		data = bytes(data)
	new_data = mutate(data)
	if convert:
		new_data = bytearray(new_data)
	if len(new_data) >= max_size:
		return new_data[:max_size] # Just add a cutoff
	return new_data


def chance() -> float: # Shorthand
	return random.random()

def c(const: float) -> bool: # Rolls a dice and returns true with a probability of "const"
	return chance() <= const

def rnum(n: int) -> int: # Shorthand
	if n == 0 or n == -1:
		return 0
	return random.randrange(0, n)

def stringmult(string: bytes, c: int) -> bytes: # Multiplies string by c times.
	count = random.randrange(MAX_REPEAT_COUNT) # min(math.floor(MAX_REPEAT_LENGTH/len(string)), c)
	assert isinstance(count, int)
	if len(string) * count > MAXIMUM_LENGTH:
		# Just truncate the count...
		count = math.floor(MAXIMUM_LENGTH / len(string))
	out = string * count
	assert len(out) <= MAXIMUM_LENGTH
	return out

def rand_ascii_string(n: int) -> bytes: # Generates n random ascii bytes (taken from string.printable)
	return bytes([ord(random.choice(string.printable)) for _ in range(n)]) # Create array of allowed bytes and convert to bytes

def generate_repeating(n: int) -> bytes: # Generate a random repeating string and repeat it n times
	#return stringmult(rand_ascii_string(rnum(MAX_REPEAT_TOKEN_LENGTH)), n)
	return stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), n)

def generate_new() -> bytes: # Generate a new ascii string.
	repeat_count = rnum(MAX_REPEAT_STRING_COUNT)
	out = b"" # Final generated string
	for i in range(repeat_count): # Generate "repeat_count" repeating strings.
		out += generate_repeating(rnum(MAX_REPEAT_COUNT))
		if len(out) >= MAXIMUM_LENGTH: # Don't waste time mutating inputs which are too large anyway...
			return out
	return out

def get_substr(data: bytes) -> bytes:
	rand_ind = min(rnum(len(data)), MAX_SUBSTRING_LENGTH)
	length = rnum(len(data[rand_ind:])-1)
	res = data[rand_ind:rand_ind+length]
	return res, rand_ind # Return the substring

def mutate_existing(data: bytes) -> bytes:
	substr, rand_ind = get_substr(data) if True else (None, None)
	if True and substr:
		# Just cut out the original string and then add the multiplied substring in there.
		rep_count = distribution(MAX_REPEAT_COUNT)
		multiplication = stringmult(substr, rep_count)
		data = data[:rand_ind] + multiplication + data[rand_ind+len(substr):]
		return data
	else:
		# Place somewhere else.
		place_index = rnum(len(data)-1)
		rep_count = distribution(MAX_REPEAT_COUNT)
		multiplication = stringmult(rand_ascii_string(distribution(MAX_REPEAT_TOKEN_LENGTH)), rep_count)
		data = data[place_index:] + multiplication + data[place_index:]
		return data
	return data

def mutate(data: bytes): # Main mutator entry point. Returns a mutated version of the data.
	if c(NEW_DATA_CHANCE): # Create new string.
		return generate_new()
	else: # Mutate existing.
		return mutate_existing(data)

def fuzz_count(buf):
	return 100

def fuzz(buf, add_buf, max_size): # For AFL and AFL++
	data = buf
	data = bytes(data) # Convert bytearray to bytes.
	data = mutate(data)
	if len(data) >= max_size:
		# print("Truncating returned fuzz data...\n")
		# print("Orig len is " + str(len(data)) + " . New len is " + str(max_size))
		data = data[:max_size] # Truncate
	data = bytearray(data) # Convert bytes back to bytearray.
	return data

def deinit(): # AFL and AFL++ complain if we do not have this for some reason...
	pass

if __name__=="__main__": # For testing only (well, fuzzing is testing, but you know what I mean :D )
	MAX_MUT_COUNT = 2000
	TEST_COUNT = 100000
	BRACE_COUNT = 100

	favored_count = 0
	tot_count = 0
	favored_count2 = 0
	while True:
		
		#print("tot_count == "+str(tot_count))
		mut_count = rnum(MAX_MUT_COUNT)
		#mut_count = 1
		res = b"paskaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"*100
		for _ in range(mut_count):
			#print("tot_count == "+str(tot_count))
			tot_count += 1
			res = mutate_existing(res)
			if len(res) > MAXIMUM_LENGTH: # Bounds check
				res = res[:MAXIMUM_LENGTH]
			print("len(res) == "+str(len(res)))

			if len(res) > 5_000_000:
				print("Works!")
				exit(0)

			if tot_count % 1_000_000 == 0:
				print(favored_count / tot_count)
				print("favored2: "+str(favored_count2 / tot_count))

	exit(0) # Return succesfully
