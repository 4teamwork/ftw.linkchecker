from ftw.builder import Builder
from ftw.builder import create
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPClientError
from ftw.testbrowser.exceptions import InsufficientPrivileges
from parameterized import parameterized


class TestDashboardPermissions(FunctionalTestCase):

    @browsing
    def test_dashboard_context_sensitivity(self, browser):
        self.grant(self.portal, 'Manager')
        folder = create(Builder('folder').titled(u'My Folder'))
        browser.login()

        # It is expected that we can call the dashboard view on a
        # plone site root without any HTTPClient errors.
        try:
            browser.open(self.portal, view='linkchecker-dashboard')
        except HTTPClientError:
            self.fail('The dashboard can\'t be called on a plone site root.')

        # It is expected that we can not call the dashboard view on a
        # site other than a plone site root.
        try:
            browser.open(folder, view='linkchecker-dashboard')
        except HTTPClientError:
            pass
        except Exception as e:
            raise(e)
        else:
            self.fail('The dashboard was callable on a non plone site root.')

    @parameterized.expand([
        ('Manager', 'can view'),
        ('Reviewer', 'can view'),
        ('Site Administrator', 'can view'),
        ('Member', 'can not view'),
        ('Reader', 'can not view'),
        ('Editor', 'can not view'),
        ('Contributor', 'can not view')])
    @browsing
    def test_dashboard_permissions(self, role, expectation, browser):
        self.grant(self.portal, role)
        browser.login()

        test_state = None
        try:
            browser.open(self.portal, view='linkchecker-dashboard')
            test_state = 'can view'
        except InsufficientPrivileges:
            test_state = 'can not view'

        self.assertEqual(
            expectation, test_state,
            'It is expected that a {} {} the linkchecker-dashboard.'.format(
                role, expectation))
