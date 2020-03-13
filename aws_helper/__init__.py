import sys
import os
import subprocess
from pathlib import Path
import configparser
from hashlib import sha1
import json


def read_cache_json(cache_key):
    home_path = str(Path.home())
    cache_json_path = os.path.join(home_path, '.aws', 'cli', 'cache', f'{cache_key}.json')
    with open(cache_json_path, 'r') as stream:
        cache_json = json.loads(stream.read())
    # print(json.dumps(cache_json, indent=4, sort_keys=True))
    return cache_json


def generate_cache_key(sso_start_url, sso_role_name, sso_account_id, **kwargs):
    args = {
        'startUrl': sso_start_url,
        'roleName': sso_role_name,
        'accountId': sso_account_id,
    }
    args = json.dumps(args, sort_keys=True, separators=(',', ':'))
    argument_hash = sha1(args.encode('utf-8')).hexdigest()
    return argument_hash


def get_indexed_arg(args, index):
    try:
        return args[index]
    except:
        pass
    return None


def parse_args(sys_args):
    # aws helper takes max two params, profile and debug
    # the rest should be passed on to the shell-exec
    # param 0 is probably the script itself
    for arg_index in [1, 2]:
        this_arg = get_indexed_arg(sys_args, arg_index)
        print(f'{arg_index}: {this_arg}')


def get_profile_name(cmd_args):
    profile_from_param = None
    profile_name_from_env = os.getenv('AWS_PROFILE', None)
    profile_param_length = 0

    if len(cmd_args) < 2:
        return profile_name_from_env, profile_param_length
    if cmd_args[1].lower().startswith('--profile'):
        if '=' in cmd_args[1]:
            profile_from_param = cmd_args[1].split('=')[1]
            profile_param_length = 1
        else:
            profile_from_param = cmd_args[2]
            profile_param_length = 2
    if profile_from_param:
        return profile_from_param, profile_param_length
    elif profile_name_from_env:
        return profile_name_from_env, profile_param_length
    else:
        return None, profile_param_length


def get_profile_details(profile_name):
    home_path = str(Path.home())
    config_file = os.path.join(home_path, '.aws', 'config')
    config = configparser.ConfigParser()
    config.read(config_file)
    section = f'profile {profile_name}'
    out_dict = {}
    try:
        profile_data = config[section]
    except KeyError:
        return None
    for key in profile_data:
        out_dict[key] = profile_data[key]
    return out_dict


def main():
    profile_name, profile_param_length = get_profile_name(sys.argv)
    if not profile_name:
        raise ValueError('no profile found')
    profile_details = get_profile_details(profile_name)
    if not profile_details:
        sys.exit('Profile not found')
    cache_key = generate_cache_key(**profile_details)
    cache_data = read_cache_json(cache_key)
    new_env_vars = {
        'AWS_ACCESS_KEY_ID': cache_data['Credentials']['AccessKeyId'],
        'AWS_SECRET_ACCESS_KEY': cache_data['Credentials']['SecretAccessKey'],
        'AWS_SESSION_TOKEN': cache_data['Credentials']['SessionToken'],
    }

    exec_env_vars = os.environ.copy()
    exec_env_vars.update(new_env_vars)
    if os.getenv('AWS_PROFILE'):
        del exec_env_vars['AWS_PROFILE']
    incoming_args = sys.argv[1+profile_param_length:]

    if not incoming_args:
        return

    process = subprocess.Popen(
        [' '.join(incoming_args)],
        stdout=subprocess.PIPE,
        universal_newlines=True,
        shell=True, env=exec_env_vars)

    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                print(output.strip())
            break


