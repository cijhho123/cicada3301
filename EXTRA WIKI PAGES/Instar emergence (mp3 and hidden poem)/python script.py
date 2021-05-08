gem3 = (
	(79, ("ING")),
)

gem2 = (
	(5, ("TH")),
	(41, ("EO")),
	(79, ("NG")),
	(83, ("OE")),
	(101, ("AE")),
	(107, ("IA", "IO")),
	(109, ("EA")),
)

gem = (
	(2, ("F")),
	(3, ("U", "V")),
	(7, ("O")),
	(11, ("R")),
	(13, ("C", "K")),
	(17, ("G")),
	(19, ("W")),
	(23, ("H")),
	(29, ("N")),
	(31, ("I")),
	(37, ("J")),
	(43, ("P")),
	(47, ("X")),
	(53, ("S", "Z")),
	(59, ("T")),
	(61, ("B")),
	(67, ("E")),
	(71, ("M")),
	(73, ("L")),
	(89, ("D")),
	(97, ("A")),
	(103, ("Y")),	
)

def enc_2(c, arr):
	for g in arr:
		if c.upper() in g[1]:
			return g[0]

def enc(s):
	sum = 0

	i = 0
	while i < len(s):
		if i < len(s) - 2:
			c = s[i] + s[i + 1] + s[i + 2]
			o = enc_2(c, gem3)
			if o > 0:
				print("{0}, {1}".format(c, o))
				sum += o
				i += 3
				continue
	
		if i < len(s) - 1:
			c = s[i] + s[i + 1]
			o = enc_2(c, gem2)
			if o > 0:
				print("{0}, {1}".format(c, o))
				sum += o
				i += 2
				continue
	
		o = enc_2(s[i], gem)
		if o > 0:
			print("{0}, {1}".format(s[i], o))
			sum += o
		
		i += 1
			
	return sum

sum = 0
for line in ["Like the instar, tunneling to the surface",
	"We must shed our own circumferences;",
	"Find the divinity within and emerge."
]:
	o = enc(line)
	print(o)
	if sum == 0:
		sum = o
	else:
		sum *= o
	
print(sum)