from parse_it import ParseIt


parser = ParseIt(config_location="./none.yaml", config_type_priority=['cli_args', 'yaml'])


print(parser.read_all_configuration_variables())
