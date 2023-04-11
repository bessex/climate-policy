import json
import os
import subprocess
import yaml

# Get the environment information as JSON
env_json = subprocess.run(['conda', 'env', 'export', '--json', '--no-builds'],
                          stdout=subprocess.PIPE, env=os.environ, shell=True).stdout

# Load the JSON data into a Python dictionary
env_dict = json.loads(env_json)

# Get the dependencies as a dictionary with package names as keys and versions as values
dependencies = env_dict['dependencies']
dependencies_dict = {}
for dependency in dependencies:
    if isinstance(dependency, dict) and 'pip' in dependency:
        dependencies_dict['pip'] = dependency['pip']
    else:
        package_name, package_version = dependency.split('=')
        dependencies_dict[package_name] = package_version

# Export the environment to YAML using the --from-history option
env_yaml = subprocess.run(['conda', 'env', 'export', '--from-history'],
                          stdout=subprocess.PIPE, env=os.environ, shell=True).stdout

# Load the YAML data into a Python dictionary
env_data = yaml.safe_load(env_yaml)

# Modify the YAML to include version compatibility for each dependency
dependencies_list = []

for dependency in env_data['dependencies']:
    if isinstance(dependency, dict) and 'pip' in dependency:
        continue
    dep_components = dependency.split('=')
    package_name = dep_components[0]
    if package_name[-1] in ['~', '>', '<', '='] or len(dep_components) > 1:
        dependencies_list.append(dependency)
        continue
    if package_name in dependencies_dict:
        version = '~=' + dependencies_dict[package_name]
    else:
        version = ''
    dependencies_list.append(package_name + version)

if 'pip' in dependencies_dict:
    pip_dependencies = {'pip': []}
    for pip_dependency in dependencies_dict['pip']:
        dep_components = pip_dependency.split('=')
        package_name = dep_components[0]
        if package_name[-1] in ['~', '>', '<', '=']:
            package_name = package_name[:-1]
        pip_dependencies['pip'].append(package_name)
    dependencies_list.append(pip_dependencies)

env_data['dependencies'] = dependencies_list

# Remove prefix from the YAML
env_data.pop('prefix', None)

# Output the modified YAML to the console
print(yaml.dump(env_data, default_flow_style=False, sort_keys=False), end='')