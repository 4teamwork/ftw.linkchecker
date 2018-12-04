from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.schema import getFieldsInOrder
import AccessControl
import re


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


def setup_plone(app, site_info):
    plone_site = app.get(site_info['id'])
    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(plone_site.acl_users)
    newSecurityManager(plone_site, user)
    setSite(plone_site)


def get_broken_relations_in_plone_page():
    relation_catalog = getUtility(ICatalog)
    catalog_lookup(relation_catalog)
    # there's need to also check another catalog


def catalog_lookup(relation_catalog):
    x = relation_catalog
    relations = list(x.findRelations())
    relations_info = []
    for relation in relations:
        if relation.isBroken():
            rel_info = {
                'origin': relation.from_path,
                'title': relation.from_object.Title()
            }
        relations_info.append(rel_info)
    return relations_info


def get_external_broken_links_in_plone_page(site_info):
    portal_catalog = api.portal.get_tool('portal_catalog')
    query = {'path': site_info['path'], 'portal_type': 'Document'}
    brains = portal_catalog.unrestrictedSearchResults(query)
    links_on_a_plone_site = []
    for brain in brains:
        links_on_a_plone_site.append(find_links_on_brain_fields(brain))

    in_field_links = [j for sub in links_on_a_plone_site for j in sub]
    # check these links and validate
    # this feature is developed in branch mo/external_link_fetcher
    # presumably called: work_through_urls(in_field_links)


def extract_links_in_string(inputString):
    # Explanation for the following regex pattern can be found in this post:
    # https://stackoverflow.com/questions/839994/extracting-a-url-in-python/50790119#50790119
    regex = ur"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
    return re.findall(regex, inputString)


def find_links_on_brain_fields(brain):
    obj = brain.getObject()
    links_from_dexterity = []
    links_from_non_dexterity = []

    if not queryUtility(IDexterityFTI, name=obj.portal_type):
        # is not dexterity
        for field in obj.Schema().fields():
            content = field.getRaw(obj)
            if not isinstance(content, basestring):
                continue

            links = extract_links_in_string(content)
            if not links:
                # only continue if there are any links
                continue
            links_from_non_dexterity = []
            for link in links:
                links_from_non_dexterity.append({
                    'origin': obj.absolute_url_path(),
                    'destination': link,
                })

    if queryUtility(IDexterityFTI, name=obj.portal_type):
        for name, field, schemata in iter_fields(obj.portal_type):
            if not IRichText.providedBy(field):
                continue

            storage = schemata(obj)
            textfield = getattr(storage, name)
            if not textfield:
                continue

            orig_text = textfield.raw

            if not isinstance(orig_text, basestring):
                continue

            links = extract_links_in_string(orig_text)
            if not links:
                # only continue if there are any links
                continue
            links_from_dexterity = []
            for link in links:
                links_from_dexterity.append({
                    'origin': obj.absolute_url_path(),
                    'destination': link,
                })

    urls_info_two_dim_list = [links_from_non_dexterity, links_from_dexterity]
    urls_info_dicts = [j for sub in urls_info_two_dim_list for j in sub]
    return urls_info_dicts


def iter_fields(portal_type):
    for schemata in iter_schemata_for_protal_type(portal_type):
        for name, field in getFieldsInOrder(schemata):
            if not getattr(field, 'readonly', False):
                yield (name, field, schemata)


def iter_schemata_for_protal_type(portal_type):

    if queryUtility(IDexterityFTI, name=portal_type):
        # is dexterity
        fti = getUtility(IDexterityFTI, name=portal_type)

        yield fti.lookupSchema()
        for schema in getAdditionalSchemata(portal_type=portal_type):
            yield schema


def create_and_send_mailreport_to_plone_site_responible_person(
        email_address, site_info, broken_internal, broken_external):
    path_to_report = create_excel_report_and_return_filepath(
        site_info, broken_internal, broken_external)
    send_mail_with_excel_report_attached(email_address, path_to_report)


def create_excel_report_and_return_filepath(
        site_info, broken_internal, broken_external):
    # this function needs to create an excel report, safe it into a temp folder
    # it then returns the path to that file.
    # It makes use of the report generator from branch
    # mo/excel_report_generator
    pass


def send_mail_with_excel_report_attached(email_address, path_to_report):
    # this function sends the previously generated excel report to the
    # responsible email address with a simple info body.
    # It makes use of the report mailer from branch mo/mail_sending
    pass


def main(app, *args):
    plone_sites_information = get_plone_sites_information(app)
    for site_info in plone_sites_information:
        email_address = 'hugo.boss@4teamwork.ch'

        setup_plone(app, site_info)

        broken_internal = get_broken_relations_in_plone_page()
        broken_external = get_external_broken_links_in_plone_page(site_info)

        create_and_send_mailreport_to_plone_site_responible_person(
            email_address, site_info, broken_internal, broken_external)
