from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent
from OFS.interfaces import IApplication
from Testing.makerequest import makerequest
from ftw.linkchecker import LOGGER_NAME
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
import AccessControl
import logging


class PerSiteConfiguration():

    def __init__(self, plone_site, configuration):
        self.configuration = configuration
        self.max_processes = configuration.max_processes
        self.upload_path = ''
        self.logger = logging.getLogger(LOGGER_NAME)

        self.obj = None
        self._setup_plone(plone_site)
        self.configuration = self._get_config_for_portal()
        if self.configuration:
            self._set_upload_path()

    def _setup_plone(self, plone_site_obj):
        app = self._find_app(plone_site_obj)
        app = makerequest(app)
        setRequest(app.REQUEST)
        self.obj = app.unrestrictedTraverse(
            '/'.join(plone_site_obj.getPhysicalPath()))
        user = AccessControl.SecurityManagement.SpecialUsers.system
        user = user.__of__(self.obj.acl_users)
        newSecurityManager(self.obj, user)
        setSite(self.obj)

    def _find_app(self, plone_site_obj):
        parent = aq_parent(plone_site_obj)
        if IApplication.providedBy(parent):
            return parent
        else:
            return self._find_app(parent)

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
