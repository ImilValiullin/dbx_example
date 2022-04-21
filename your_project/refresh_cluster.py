import sys
import json
import logging
import subprocess
import configparser
from pathlib import Path

cluster_id = sys.argv[1]

file_log = logging.FileHandler(str(__file__).replace('py', 'log'))
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')


def main(cluster_id=None):
    def get_credentials():
        ini_reader = configparser.ConfigParser()
        print(f'databrickscfg path: {str(Path.home().joinpath(".databrickscfg"))}')
        ini_reader.read(str(Path.home().joinpath(".databrickscfg")))
        return ini_reader['default']['host'], ini_reader['default']['token']

    def run_bash(bash_command):
        out = subprocess.run(bash_command, capture_output=True, shell=True)
        return out.stdout.decode("utf8")

    def get_cluster_id(path_json):
        with open(path_json, 'r') as f:
            json_str = f.read()
        deployment_json = json.loads(json_str)
        return list(deployment_json.values())[0]['jobs'][0]['existing_cluster_id']

    def json_parser_libs(json_str):
        libs_dict = []
        libs_json = json.loads(json_str)
        for lib_dirt in libs_json['library_statuses']:
            for type_lib in lib_dirt["library"]:
                lib = ''
                if "package" in lib_dirt["library"][type_lib]:
                    lib = lib_dirt["library"][type_lib]["package"]
                else:
                    lib = lib_dirt["library"][type_lib]
                libs_dict.append([type_lib, lib])
        return libs_dict

    def get_libs_list(host, token, cluster_id):
        command = f"curl --netrc --get -H 'Authorization: Bearer {token}' {host}/api/2.0/libraries/cluster-status --data cluster_id={cluster_id}"
        out_str = run_bash(command)
        if "library_statuses" not in out_str:
            return None
        else:
            libs = json_parser_libs(out_str)
            logging.info(f'Total libs: {len(libs)}')
        return libs

    def remove_lib(list_libs, host, token, cluster_id):
        for libs_info in list_libs:
            lib_type = libs_info[0]
            lib = libs_info[1]
            logging.info(f'Remove {lib_type}: {lib}')
            if lib_type == 'pypi':
                command = 'curl --netrc --request POST -H "Authorization: Bearer ' + token + '" ' + host + '/api/2.0/libraries/uninstall --data \'{ "cluster_id": "' + cluster_id + '", "libraries": [ { "' + \
                          libs_info[0] + '": { "package" : "' + libs_info[1] + '"} } ]}\''
            else:
                command = 'curl --netrc --request POST -H "Authorization: Bearer ' + token + '" ' + host + '/api/2.0/libraries/uninstall --data \'{ "cluster_id": "' + cluster_id + '", "libraries": [ { "' + \
                          libs_info[0] + '": "' + libs_info[1] + '" } ]}\''
            run_bash(command)

    def terminate_cluster(host, token, cluster_id):
        command = 'curl --netrc -X POST -H "Authorization: Bearer ' + token + '" ' + host + '/api/2.0/clusters/delete --data \'{ "cluster_id": "' + cluster_id + '" }\''
        run_bash(command)

    if cluster_id is None:
        cluster_id = get_cluster_id('./conf/deployment.json')

    logging.info(f'Cluster Id: {cluster_id}')
    # get_credentials
    logging.info('Get credentials.')
    host, token = get_credentials()

    # get list of libs
    logging.info('Get list libs')
    libs_list = get_libs_list(host, token, cluster_id)

    if libs_list == None:
        logging.info('List of libs is empty!')
        logging.info('Done!')
        return True

    # remove libs
    logging.info('Start remove libs')
    remove_lib(libs_list, host, token, cluster_id)
    logging.info('Finish remove libs')

    # remove libs
    logging.info('Terminate cluster')
    terminate_cluster(host, token, cluster_id)

    logging.info('Done!')


if __name__ == "__main__":
    main(cluster_id)
