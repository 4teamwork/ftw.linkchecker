from AccessControl.SecurityManagement import newSecurityManager
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.hooks import setSite
import AccessControl
from Products.CMFPlone.interfaces import IPloneSiteRoot


def get_plone_sites_information(app):
    plone_sites = [obj for obj in app.objectValues(
    ) if IPloneSiteRoot.providedBy(obj)]
    # create information dictionary for each plone site
    plone_sites_information = [{
        'id': plone_site.getId(),
        'path': '/'.join(plone_site.getPhysicalPath()),
        'title': plone_site.Title()
    } for plone_site in plone_sites]

    return plone_sites_information


def setup_plone(plone_site):
    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(plone_site.acl_users)
    newSecurityManager(plone_site, user)
    setSite(plone_site)


def get_relation_catalog_for_plone_site(app, PloneSiteId):
    plone_site = app.get(PloneSiteId)
    setup_plone(plone_site)

    return getUtility(ICatalog)


def catalog_lookup(relation_catalog):
    x = relation_catalog
    relations = list(x.findRelations())
    print(relations)


def main(app, *args):
    plone_sites_information = get_plone_sites_information(app)
    for site_info in plone_sites_information:
        relation_catalog = get_relation_catalog_for_plone_site(
            app,
            site_info['id']
        )
        catalog_lookup(relation_catalog)
