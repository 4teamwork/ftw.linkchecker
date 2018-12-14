import os
import time
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.linkchecker import linkchecker
from ftw.linkchecker import report_generating
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.schema import getFieldsInOrder
import AccessControl
import re

from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE


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
    external_link_data = linkchecker.work_through_urls(in_field_links)
    return external_link_data


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
        email_address, broken_internal, broken_external):
    path_to_report = create_excel_report_and_return_filepath(broken_internal,
                                                             broken_external)
    send_mail_with_excel_report_attached(email_address, path_to_report)


def create_excel_report_and_return_filepath(broken_internal, broken_external):
    filename = 'linkchecker_report_{}.xlsx'.format(
        time.strftime('%Y_%b_%d_%H%M%S', time.gmtime()))
    current_path = os.path.dirname(os.path.abspath(__file__))
    path_of_excel_workbook_generated = current_path + '/reports/' + filename
    broken_external = [[
        str('external link'),
        str(link_dict['origin']),
        str(link_dict['destination']),
        str(link_dict['status code']),
        str(link_dict['content type']),
        str(link_dict['time']),
        str(link_dict['header location']),
        str(link_dict['error'])]
        for link_dict in broken_external[1]
    ]
    file_i = report_generating.ReportCreator(path_of_excel_workbook_generated)
    file_i.append_report_data(report_generating.LABELS,
                              BOLD &
                              CENTER &
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)
    if broken_external:
        file_i.append_report_data(broken_external,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
    if broken_internal:
        file_i.append_report_data(broken_internal,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
    file_i.add_general_autofilter()
    file_i.cell_width_autofitter()
    file_i.safe_workbook()
    return path_of_excel_workbook_generated


def send_mail_with_excel_report_attached(email_address, path_to_report):
    pass


def main(app, *args):
    plone_sites_information = get_plone_sites_information(app)
    for site_info in plone_sites_information:
        email_address = 'hugo.boss@4teamwork.ch'

        setup_plone(app, site_info)

        broken_internal = get_broken_relations_in_plone_page()
        broken_external = get_external_broken_links_in_plone_page(site_info)

        create_and_send_mailreport_to_plone_site_responible_person(
            email_address, broken_internal, broken_external)
