from parse_it import ParseIt


parser = ParseIt(config_location="./seotesting_config.yaml", config_type_priority=['cli_args', 'yaml'])

config = parser.read_all_configuration_variables()

print(config['modules'].keys())
