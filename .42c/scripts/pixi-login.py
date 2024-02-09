#!/usr/bin/env python3

import sys
import time
import json
import argparse
import urllib.error
import urllib.request
import subprocess

# Obtain a JWT token using login to PhtoManager app. 
# API comes with pre-loaded users we use from the 42c-scan workflow.
def obtain_token(name: str, password: str, target_url: str, quiet: bool, debug: bool):
    
    # Define the maximum number of retry attempts
    max_retries = 5
    # Define the delay between retry attempts (in seconds)
    retry_delay = 2
    # Initialize a variable to keep track of the number of retries
    retry_count = 0
    url = f"{target_url}/user/login"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    payload = {f"user": name, "pass": password}

    while True:
        if 0 < max_retries <= retry_count:
            break

        try:
            request = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            response = urllib.request.urlopen(request)
        except:
            time.sleep(retry_delay)
            retry_count += 1
            continue

        if response.code != 200:
            raise Exception(f"Received status code {response.status_code}. Retrying...")
        else:
            return json.loads(response.read()).get('token')

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Pixi API Login'
    )
    parser.add_argument('-u', "--user-name",
                        default="UserName",
                        help="PixiApp User", required=True)
    parser.add_argument('-p', "--user-pass",
                        help="PixiApp Password", required=True)
    parser.add_argument('-t', '--target',
                        required=False,
                        default='http://localhost:8090/api',
                        help="Default is http://localhost:8090/api",
                        type=str)
    parser.add_argument('-q', "--quiet",
                        default=False,
                        action="store_true",
                        help="Quiet output. If invalid config, prints config error report file name")
    parser.add_argument('-d', '--debug',
                        default=False,
                        action="store_true",
                        help="debug level")
    parser.add_argument ('-c','--cicd',
                         required=True,
                         help="One of GITHUB/AZURE")
    parsed_cli = parser.parse_args()

    quiet = parsed_cli.quiet
    debug = parsed_cli.debug
    user = parsed_cli.user_name
    password = parsed_cli.user_pass
    cicd_platform = parsed_cli.cicd 

    user_token = obtain_token(user, password, target_url=parsed_cli.target, quiet=quiet, debug=debug)
    # Uncomment this for integration with Azure DevOps
    # subprocess.Popen(["echo", "##vso[task.setvariable variable=PIXI_TOKEN;isoutput=true]{0}".format(scan_token)])
    # Uncomment this for integration with GitHub actions
    # Send to stdout
    if not user_token:
        print("Error: Unable to obtain token")
        sys.exit(1)

    else:
        match cicd_platform:
            case "GITHUB":
                print(user_token)
            case "AZURE":
                subprocess.Popen(["echo", "##vso[task.setvariable variable=PIXI_TOKEN;isoutput=true]{0}".format(user_token)])  
            case _:
                print ("Unsupported CICD option")

# -------------- Main Section ----------------------
if __name__ == '__main__':
    main()