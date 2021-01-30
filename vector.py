EPSILON = 1e-8

def check_vectors(a, b):
	if type(a) != list or type(b) != list:
		raise TypeError("Invalid vectors!")
	if len(a) != len(b):
		raise ValueError("Vector dimension mismatch!")

def check_vector_scalar(a, x):
	if type(a) != list:
		raise TypeError("Invalid vector!")
	if type(x) != int and type(x) != float and type != complex:
		raise TypeError("Invalid scalar!")

def eq(a, b):
	check_vectors(a, b)

	for i in range(len(a)):
		if abs(b[i] - a[i]) > EPSILON:
			return False
	return True

def add(a, b):
	check_vectors(a, b)

	c = [0.0 for i in range(len(a))]
	for i in range(len(a)):
		c[i] = a[i] + b[i]
	return c

def sub(a, b):
	check_vectors(a, b)

	c = [0.0 for i in range(len(a))]
	for i in range(len(a)):
		c[i] = a[i] - b[i]
	return c

def scalar_mult(a, x):
	check_vector_scalar(a, x)

	c = [0.0 for i in range(len(a))]
	for i in range(len(a)):
		c[i] = a[i] * x
	return c

def scalar_div(a, x):
	check_vector_scalar(a, x)

	c = [0.0 for i in range(len(a))]
	for i in range(len(a)):
		c[i] = a[i]/x
	return c