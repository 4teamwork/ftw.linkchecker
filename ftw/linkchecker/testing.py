from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.linkchecker.tests import builders
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing.layers import PloneFixture
from plone.testing import z2
from plone.testing import zodb
from zope.configuration import xmlconfig
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

    # overwrite setUp to also call self.setUpSecondPage()
    def setUp(self):
        self['zodbDB'] = zodb.stackDemoStorage(self.get('zodbDB'),
                                               name='PloneFixture')
        self.setUpZCML()
        with z2.zopeApp() as app:
            self.setUpProducts(app)
            self.setUpDefaultContent(app)
            self.setUpSecondPage(app)

    def setUpSecondPage(self, app):
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

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.linkchecker:default')


LINKCHECKER_FIXTURE = LinkcheckerLayer()
LINKCHECKER_FUNCTIONAL = FunctionalTesting(
    bases=(LINKCHECKER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.linkchecker:functional")
