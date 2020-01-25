from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent
from Testing.makerequest import makerequest
from ftw.linkchecker import LOGGER_NAME
from plone import api
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
import AccessControl
import logging


class PloneSite():

    def __init__(self, plone_site, configuration):
        self.configuration = configuration
        self.upload_path = ''
        self.logger = logging.getLogger(LOGGER_NAME)

        self._setup_plone(plone_site)
        self.obj = plone_site
        self.configuration = self._get_config_for_portal()
        if self.configuration:
            self._set_upload_path()

    def _setup_plone(self, plone_site_obj):
        setRequest(aq_parent(plone_site_obj).REQUEST)
        user = AccessControl.SecurityManagement.SpecialUsers.system
        user = user.__of__(plone_site_obj.acl_users)
        newSecurityManager(plone_site_obj, user)
        setSite(plone_site_obj)

    def _get_config_for_portal(self):
        try:
            site_config = [site_config for site_config
                           in self.configuration.sites
                           if site_config.site_name == '/'.join(
                               self.obj.getPhysicalPath())][0]
        except IndexError:
            site_config = []

        return site_config

    def _set_upload_path(self):
        try:
            self.obj.unrestrictedTraverse(
                path=self.configuration.upload_location)
            self.upload_path = self.configuration.upload_location
        except KeyError:
            return
