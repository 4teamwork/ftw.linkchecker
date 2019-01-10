from Acquisition import aq_parent
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.linkchecker.tests import builders
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_SITE_ID
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import pushGlobalRegistry
from plone.app.testing.helpers import login, logout
from plone.app.testing.layers import PloneFixture
from plone.testing import z2
from plone.testing import zca, security
from plone.testing import zodb
from zope.configuration import xmlconfig
import contextlib
from plone.app.testing.interfaces import (
    DEFAULT_LANGUAGE,
    TEST_USER_ID,
    TEST_USER_NAME,
    TEST_USER_PASSWORD,
    TEST_USER_ROLES,
    SITE_OWNER_NAME,
)

SECOND_PLONE_SITE_ID = 'plone2'
SECOND_PLONE_SITE_TITLE = u"Plone site Two"


class PloneFixtureChild(PloneFixture):
    def __init__(self):
        super(PloneFixture, self).__init__()

    # overwrite setUp() to also call self.setUpDefaultContent_AdditionalPage()
    def setUp(self):
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'),
                                               name='PloneFixture')
        self.setUpZCML()
        with z2.zopeApp() as app:
            self.setUpProducts(app)
            self.setUpDefaultContent(app)
            self.setUpDefaultContent_AdditionalPage(app)

    def setUpDefaultContent_AdditionalPage(self, app):
        z2.login(app['acl_users'], SITE_OWNER_NAME)
        from Products.CMFPlone.factory import addPloneSite
        # Set up the second page with another ID here.
        addPloneSite(app, SECOND_PLONE_SITE_ID,
                     title=SECOND_PLONE_SITE_TITLE,
                     setup_content=False,
                     default_language=DEFAULT_LANGUAGE,
                     extension_ids=self.extensionProfiles,
                     )
        app[SECOND_PLONE_SITE_ID]['portal_workflow'].setDefaultChain('')
        pas = app[SECOND_PLONE_SITE_ID]['acl_users']
        pas.source_users.addUser(
            TEST_USER_ID,
            TEST_USER_NAME,
            TEST_USER_PASSWORD)
        for role in TEST_USER_ROLES:
            pas.portal_role_manager.doAssignRoleToPrincipal(TEST_USER_ID,
                                                            role)
        z2.logout()


PLONE_FIXTURE = PloneFixtureChild()


class LinkcheckerLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.linkchecker')
        z2.installProduct(app, 'ftw.simplelayout')

    def setUp(self):
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'),
                                               name=self.__name__)
        name = self.__name__ if self.__name__ is not None else 'not-named'
        contextName = "PloneSandboxLayer-%s" % name
        self['configurationContext'] = configurationContext = (
            zca.stackConfigurationContext(self.get('configurationContext'),
                                          name=contextName))
        ########################
        # call ploneSite() twice (for both pages)
        #########################
        for plone_site_id in [PLONE_SITE_ID, SECOND_PLONE_SITE_ID]:
            with self.ploneSite(plone_site_id) as portal:
                from zope.site.hooks import setSite, setHooks
                setHooks()
                setSite(None)
                pushGlobalRegistry(portal)
                security.pushCheckers()
                from Products.PluggableAuthService.PluggableAuthService import (
                    MultiPlugins)
                preSetupMultiPlugins = MultiPlugins[:]
                self.setUpZope(portal.getPhysicalRoot(), configurationContext)
                setSite(portal)
                self.setUpPloneSite(portal)
                setSite(None)
            self.snapshotMultiPlugins(preSetupMultiPlugins)

    @contextlib.contextmanager
    def ploneSite(self, plone_site_id, db=None, connection=None, environ=None):
        from zope.site.hooks import setSite, getSite, setHooks
        setHooks()
        site = getSite()
        with z2.zopeApp(db, connection, environ) as app:
            portal = app[plone_site_id]
            setSite(portal)
            login(portal, TEST_USER_NAME)
            try:
                yield portal
            finally:
                logout()
                if site is not portal:
                    setSite(site)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.linkchecker:default')
        applyProfile(portal, 'ftw.simplelayout.contenttypes:default')


LINKCHECKER_FIXTURE = LinkcheckerLayer()
LINKCHECKER_FUNCTIONAL = FunctionalTesting(
    bases=(LINKCHECKER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.linkchecker:functional")
