import sys
import os
import subprocess
from pathlib import Path
import configparser
from hashlib import sha1
import json
import warnings
from datetime import datetime
import pytz


def read_cache_json(cache_key):
    home_path = str(Path.home())
    cache_json_path = os.path.join(home_path, '.aws', 'cli', 'cache', f'{cache_key}.json')
    with open(cache_json_path, 'r') as stream:
        cache_json = json.loads(stream.read())
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


def is_external_process_mode():
    if os.getenv('EXTERNAL_PROCESS_MODE', None):
        return True
    return False


def check_cache_expiry(cache_expiry_string):
    cache_expiry = datetime.strptime(cache_expiry_string, '%Y-%m-%dT%H:%M:%SUTC')
    cache_expiry = pytz.utc.localize(cache_expiry)

    current_time = datetime.utcnow()
    current_time = pytz.utc.localize(current_time)

    if current_time > cache_expiry:
        return True #cache is expired
    return False


def generate_process_cred_json(credential_data):
    return {
        'Version': 1,
        'AccessKeyId': credential_data['Credentials']['AccessKeyId'],
        'SecretAccessKey': credential_data['Credentials']['SecretAccessKey'],
        'SessionToken': credential_data['Credentials']['SessionToken'],
        'Expiration': credential_data['Credentials']['Expiration']
    }


def call_sts_get_caller_identity(profile_name):
    # Altho we have an sso session, we might not have the cli cache. The first aws call generates it, so we call get-caller-identity.
    # This only happens if the cache file is missing, as it takes a few moments.
    sts_call_result = subprocess.check_output(f'aws sts get-caller-identity --profile {profile_name}', shell=True, universal_newlines=True)
    try:
        sts_call_data = json.loads(sts_call_result)
        logged_in_arn = sts_call_data['Arn']
        print(f'AWSHELPER: Generated cli cache. Logged in as {logged_in_arn}')
    except:
        print(f'AWSHELPER: Unable to make aws call. You may have to run "aws sso login --profile {profile_name}"')
        exit(1)
    return


def main():
    profile_name, profile_param_length = get_profile_name(sys.argv)
    if not profile_name:
        raise ValueError('no profile found')
    profile_details = get_profile_details(profile_name)

    if not profile_details:
        sys.exit('Profile not found')

    cache_key = generate_cache_key(**profile_details)
    cache_data = None
    try:
        cache_data = read_cache_json(cache_key)
    except Exception:
        print(f'AWSHELPER: Credentials file not found. Executing "aws sts get-caller-identity --profile {profile_name}" to generate it')
        call_sts_get_caller_identity(profile_name)

    if not cache_data:
        try:
            cache_data = read_cache_json(cache_key)
        except Exception:
            sys.exit(f'AWSHELPER: Unable to read cache file generated by aws cli. You might not be logged in (run "aws sso login --profile {profile_name}" to log in, or "aws configure sso --profile {profile_name}" for first-time setup')

    if check_cache_expiry(cache_data['Credentials']['Expiration']):
        print(f'AWSHELPER: Credentials cache has expired. Executing "aws sts get-caller-identity --profile {profile_name}" to attempt to refresh it')
        call_sts_get_caller_identity(profile_name)
        cache_data = read_cache_json(cache_key)

    if is_external_process_mode():
        print(json.dumps(generate_process_cred_json(cache_data), indent=4, sort_keys=True))
        exit(0)
    new_env_vars = {
        'AWS_ACCESS_KEY_ID': cache_data['Credentials']['AccessKeyId'],
        'AWS_SECRET_ACCESS_KEY': cache_data['Credentials']['SecretAccessKey'],
        'AWS_SESSION_TOKEN': cache_data['Credentials']['SessionToken'],
        'AWSHELPER_ENABLED': 'YES',
        'AWSHELPER_PROFILE': profile_name

    }

    exec_env_vars = os.environ.copy()
    exec_env_vars.update(new_env_vars)
    if os.getenv('AWS_PROFILE'):
        del exec_env_vars['AWS_PROFILE']
    incoming_args = sys.argv[1+profile_param_length:]

    if not incoming_args:
        return

    run_args = ' '.join(incoming_args)
    process = subprocess.Popen(
        run_args,
        stdout=sys.stdout,
        stdin=sys.stdin,
        stderr=sys.stderr,
        shell=True, env=exec_env_vars, universal_newlines=True)

    while True:
        return_code = process.poll()
        if return_code is not None:
            exit(return_code)


if __name__ == "__main__":
    main()