import getopt

# args = '-a -b -cfoo -d bar a1 a2'.split()
# print(args)

# optlist, args = getopt.getopt(args, 'abc:d:')
# print(optlist)
# print(args)

s = '--condition=foo --testing --output-file abc.def -x a1 a2'
args_long = s.split()
print(args_long)

opt_long_list, args_long = getopt.getopt(args_long, 'x', ['condition=', 'output-file=', 'testing'])

print(opt_long_list)
print(args_long)