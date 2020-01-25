from Products.CMFDiffTool.utils import safe_utf8
import argparse
import json
import logging
import os


class Configuration(object):

    def __init__(self, args):
        self.config_file_path = ''
        self.log_file_path = ''
        self.sites = []

        self._parse_arguments(args)
        self._validate_args()
        self._extract_config()

    def _parse_arguments(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument("--config",
                            help="Path to linkchecker config file.")
        parser.add_argument("--log",
                            help="Path to linkchecker log file.")
        args, unknown = parser.parse_known_args()

        self.config_file_path = safe_utf8(args.config)
        self.log_file_path = safe_utf8(args.log)

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
        self.timeout_config = site_info.get('timeout_config', 1)
        self.upload_location = safe_utf8(site_info.get('upload_location', ''))
