#!/usr/bin/env python3

import json
import argparse
import requests
import time
import sys



# This call updates a named scan configuration
def obtain_token (name: str, password: str):
    # Define the maximum number of retry attempts
    max_retries = 5
    # Define the delay between retry attempts (in seconds)
    retry_delay = 2
    # Initialize a variable to keep track of the number of retries
    retry_count = 0

    url =  f"{TARGET_URL}/user/login"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    
    #Initialize  token value
    user_token = None
    
    payload = {f"user": name, "pass": password}

    while retry_count < max_retries:
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers) 
            if response.status_code != 200:
                raise Exception(f"Received status code {response.status_code}. Retrying...")
            else:
                user_token = response.json().get('token')
                break
        
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(retry_delay)
            else:  
                sys.exit (1) 

    return user_token


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
    parsed_cli = parser.parse_args()

    global quiet, debug, TARGET_URL

    quiet = parsed_cli.quiet
    debug = parsed_cli.debug
    user = parsed_cli.user_name
    password = parsed_cli.user_pass
    TARGET_URL = parsed_cli.target    

    user_token = obtain_token (user, password)
    # Uncomment this for integration with Azure DevOps
    #subprocess.Popen(["echo", "##vso[task.setvariable variable=PIXI_TOKEN;isoutput=true]{0}".format(scan_token)])
    # Uncomment this for integration with GitHub actions
    # Send to stdout
    print (user_token)

# -------------- Main Section ----------------------
if __name__ == '__main__':
    main()
