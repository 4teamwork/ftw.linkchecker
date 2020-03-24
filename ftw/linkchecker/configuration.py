from Products.CMFDiffTool.utils import safe_utf8
import argparse
import json
import logging
import os


class Configuration(object):

    def __init__(self, args):
        self.config_file_path = ''
        self.log_file_path = ''
        self.max_processes = None
        self.sites = []

        self._parse_arguments(args)
        self._validate_args()
        self._extract_config()

    def _parse_arguments(self, args):
        parser = argparse.ArgumentParser(
            usage='bin/instance check_links settings [-l logpath] [-p processes]')
        parser.add_argument('-c', '--command', help=argparse.SUPPRESS)
        parser.add_argument('settings',
                            help='Path of the linkchecker settings file.')
        parser.add_argument('-l', '--logpath',
                            help='Path of the linkchecker log file.')
        parser.add_argument('-p', '--processes', type=int,
                            help='Max. number of processes spawned.')
        args = parser.parse_args()

        self.config_file_path = safe_utf8(args.settings)
        self.log_file_path = safe_utf8(args.logpath)
        self.max_processes = int(args.processes)

    def _validate_args(self):
        if not self.config_file_path or not os.path.exists(
                self.config_file_path):
            logging.error('Config path is invalid (none given or broken).')
            exit()

    def _extract_config(self):
        with open(self.config_file_path) as f_:
            config = json.load(f_)

        for site_path, site_info in config.items():
            self.sites.append(PloneSiteConfiguration(site_path, site_info))


class PloneSiteConfiguration(object):

    def __init__(self, site_name, site_info):
        self.site_name = safe_utf8(site_name)
        self.email = [safe_utf8(email) for email in site_info.get('email', [])]
        self.base_uri = safe_utf8(site_info.get('base_uri', ''))
        self.timeout_config = int(site_info.get('timeout_config', 1))
        self.upload_location = safe_utf8(site_info.get('upload_location', ''))
