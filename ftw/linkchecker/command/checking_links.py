from zope.component.hooks import setSite
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.globalrequest import setRequest
import AccessControl
from zc.relation.interfaces import ICatalog
from zope.component import getUtility


def main(plone, *args):

    # Set up request for debug / bin/instance run mode.
    app = makerequest(plone)
    setRequest(app.REQUEST)

    houptding = app.restrictedTraverse('/')

    # here all pages need to be found
    # for now there is only 'Plone'
    # later on we need to iterate through
    # each page and send reports to different people

    MINI_SITE = houptding.get('Plone')

    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(MINI_SITE.acl_users)
    newSecurityManager(MINI_SITE, user)

    setSite(MINI_SITE)

    relation_catalog = getUtility(ICatalog)


if __name__ == '__main__':
    main()
