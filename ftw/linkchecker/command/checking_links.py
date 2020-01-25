from ftw.linkchecker import LOGGER_NAME
from ftw.linkchecker import setup_logger
from ftw.linkchecker.accumulator import Accumulator
from ftw.linkchecker.configuration import Configuration
from ftw.linkchecker.plone_site import PloneSite
from ftw.linkchecker.report_generating import ReportHandler
import logging


def _get_plone_sites(obj):
    for child in obj.objectValues():
        if child.meta_type == 'Plone Site':
            yield child
        elif child.meta_type == 'Folder':
            for item in _get_plone_sites(child):
                yield item


def check_links(app, args):
    # Retrieve configuration and setup logging
    configuration = Configuration(args)
    setup_logger(configuration.log_file_path)
    logger = logging.getLogger(LOGGER_NAME)

    logger.info('Linkchecker instance started as expected.')

    # Collect all sites in an installation
    plone_sites = list(_get_plone_sites(app))
    if not plone_sites:
        logger.error(
            'There were no pages found, please validate your pages paths.')
        exit()

    for plone_site in plone_sites:
        # Init a PloneSite object handling the context
        site = PloneSite(app, plone_site, configuration)

        # Accumulate broken links in PloneSite
        accumulator = Accumulator(site)
        accumulator.discover_broken_links()

        logger.info(
            'Finished going through all brains of "{}" and fetching for '
            'external Links. Total time fetching for external Links: '
            '{}ms.'.format(site.configuration.site_name,
                           accumulator.time_external_routine))

        # Send and Upload report
        report_handler = ReportHandler(site, accumulator)
        report_handler.send_report()
        report_handler.upload_report()


def main(app, *args):
    check_links(app, args)
