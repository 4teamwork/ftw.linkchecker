from AccessControl.SecurityManagement import newSecurityManager
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component.hooks import setSite
import AccessControl


def get_plone_sites_information(app):

    """Get all PloneSites and their information
    """
    def get_plone_sites(app):
        for child in app.objectValues():
            if child.meta_type == 'Plone Site':
                yield child
            elif child.meta_type == 'Folder':
                for item in get_plone_sites(child):
                    yield item

    plone_sites = get_plone_sites(app)

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
    relations = list(relation_catalog.findRelations())
    print(relations)


def get_external_broken_links_in_plone_page(app, site_info):
    # this function needs to find all external links in the plone site
    # then run the script linkchecker from the branch mo/external_link_fetcher
    return {}


def get_broken_relations_in_plone_page(app, site_info):
    relation_catalog = get_relation_catalog_for_plone_site(
        app,
        site_info['id']
    )
    catalog_lookup(relation_catalog)


def create_excel_report_and_return_filepath(
        site_info, broken_internal, broken_external):
    # this function needs to create an excel report, safe it into a temp folder
    # it then returns the path to that file.
    # It makes use of the report generator from branch mo/excel_report_generator
    pass


def send_mail_with_excel_report_attached(email_address, path_to_report):
    # this function sends the previously generated excel report to the
    # responsible email address with a simple info body.
    # It makes use of the report mailer from branch mo/mail_sending
    pass


def create_and_send_mailreport_to_plone_site_responible_person(
        email_address, site_info, broken_internal, broken_external):
    path_to_report = create_excel_report_and_return_filepath(
        site_info, broken_internal, broken_external)
    send_mail_with_excel_report_attached(email_address, path_to_report)


def main(app, *args):
    plone_sites_information = get_plone_sites_information(app)
    for site_info in plone_sites_information:
        email_address = 'hugo.boss@4teamwork.ch'
        broken_internal = get_broken_relations_in_plone_page(app, site_info)
        broken_external = get_external_broken_links_in_plone_page(
            app, site_info)
        create_and_send_mailreport_to_plone_site_responible_person(
            email_address, site_info, broken_internal, broken_external)
