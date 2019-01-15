from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.linkchecker import linkchecker
from ftw.linkchecker import report_generating
from ftw.linkchecker import report_mailer
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from os.path import abspath
from os.path import dirname
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from urlparse import urlparse
from z3c.relationfield.interfaces import IRelation
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IURI
import AccessControl
import json
import os
import re
import time


def get_plone_sites_information(app):
    plone_site_objs = [obj for obj in app.objectValues(
    ) if IPloneSiteRoot.providedBy(obj)]

    return plone_site_objs


def setup_plone(app, plone_site_obj):
    plone_site = app.get(plone_site_obj.getId())
    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(plone_site.acl_users)
    newSecurityManager(plone_site, user)
    setSite(plone_site)


def get_broken_relations_and_links():
    portal_catalog = api.portal.get_tool('portal_catalog')
    brains = portal_catalog.unrestrictedSearchResults()
    site_links_and_relations = []
    for brain in brains:
        site_links_and_relations.extend(find_links_on_brain_fields(brain))

    external_links = [[x[0], x[1], x[2]] for x in site_links_and_relations
                      if x[0] == 'external']
    broken_relations = [[x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], ] for
                        x in site_links_and_relations
                        if x[0] == 'internal']

    external_link_data = linkchecker.work_through_urls(
        external_links)

    # create complete link and rel data list
    complete_link_and_relation_data = []
    for external_link in external_link_data[1]:
        complete_link_and_relation_data.append(external_link)
    for broken_relation in broken_relations:
        complete_link_and_relation_data.append(broken_relation)

    return [external_link_data[0], complete_link_and_relation_data]


def extract_links_in_string(inputString, obj):
    # search for href and src
    regex = r"(href=['\"]?([^'\" >]+))|(src=['\"]?([^'\" >]+))"
    raw_results = re.findall(regex, inputString)
    # we want to exclude links starting with @@
    return [url[1] for url in raw_results if not url[1].startswith('@@')]

    output_urls = []
    output_paths = []
    for url in raw_results:
        # use actual link in findall tuple.
        url = url[1]
        if url.startswith('/'):
            # handle links on plone site root
            if url.startswith('//'):
                url = url[1:]
            path = '/'.join(api.portal.get().getPhysicalPath()) + url
            output_paths.append(path)
        elif not urlparse(url).scheme:
            # handle relative links and views
            path = '/'.join(
                obj.aq_parent.getPhysicalPath()) + '/' + url.lstrip('./')
            output_paths.append(path)
        else:
            # add all the other cases
            output_urls.append(url)

    return [output_urls, output_paths]


def extract_relation_uids_in_string(input_string):
    regex = "resolveuid/\w{32}"
    uids_long_form = re.findall(regex, input_string)
    uids = []
    for uid in uids_long_form:
        uids.append(uid.split('/')[1])
    return uids


def get_broken_relation_information(uids_or_origin_path, obj,
                                    is_broken=None):
    information_of_broken_relations = []

    for uid_or_path in uids_or_origin_path:
        if is_broken:
            origin_path = uid_or_path
        if not is_broken:
            if api.content.get(UID=uid_or_path):
                continue
            else:
                origin_path = obj.absolute_url_path(),
        information_of_broken_relations.append([
            'internal',
            origin_path,
            'Unknown location',
            'Not specified',
            'Not specified',
            'Not specified',
            'Not specified',
            'Not specified',
        ])
    return information_of_broken_relations


def extract_links_and_relations(content, obj):
    if not isinstance(content, basestring):
        return
    # find links in page
    links_and_paths = extract_links_in_string(content, obj)
    # find and add broken relations to link_and_relation_information
    relation_uids = extract_relation_uids_in_string(content)

    links = links_and_paths[0]
    paths = links_and_paths[1]
    return [links, relation_uids, paths]


def append_information_for_links_uids_paths(link_and_relation_information, obj,
                                            relation_uids=None,
                                            relation_paths=None,
                                            external_links=None):
    # If there are any uids
    if relation_uids:
        broken_relations1 = get_broken_relation_information(
            relation_uids,
            obj)
        link_and_relation_information.extend(broken_relations1)
    # It there are any relation paths
    # They need to be tested with obj.isBroken() and come along with
    # is_broken=True. Otherwise it will fail!
    if relation_paths:
        broken_relations2 = get_broken_relation_information(relation_paths,
                                                            obj,
                                                            is_broken=True)
        link_and_relation_information.extend(broken_relations2)
    # If there are external_links
    if external_links:
        for link in external_links:
            link_and_relation_information.append([
                'external',
                obj.absolute_url_path(),
                link,
            ])

    return link_and_relation_information


def extract_relation_uids_in_string(input_string):
    regex = "resolveuid/\w{32}"
    uids_long_form = re.findall(regex, input_string)
    uids = []
    for uid in uids_long_form:
        uids.append(uid.split('/')[1])
    return uids


def get_broken_relation_information_by_uids(relation_uids, obj):
    information_of_broken_relations = []
    for relation_uid in relation_uids:
        if not api.content.get(UID=relation_uid):
            information_of_broken_relations.append([
                'internal',
                obj.absolute_url_path(),
                'Unknown location',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
            ])
    return information_of_broken_relations


def add_link_info_to_links(content, link_and_relation_information, obj):
    if not isinstance(content, basestring):
        return
    # find links in page
    links = extract_links_in_string(content)
    # find and add broken relations to link_and_relation_information
    relation_uids = extract_relation_uids_in_string(content)
    broken_relations = get_broken_relation_information_by_uids(relation_uids,
                                                               obj)
    link_and_relation_information.extend(broken_relations)

    if not links:
        # only continue if there are any links
        return

    for link in links:
        link_and_relation_information.append([
            'external',
            obj.absolute_url_path(),
            link,
        ])
    return link_and_relation_information


def extract_relation_uids_in_string(input_string):
    regex = "resolveuid/\w{32}"
    uids_long_form = re.findall(regex, input_string)
    uids = []
    for uid in uids_long_form:
        uids.append(uid.split('/')[1])
    return uids


def get_broken_relation_information_by_uids(relation_uids, obj):
    information_of_broken_relations = []
    for relation_uid in relation_uids:
        if not api.content.get(UID=relation_uid):
            information_of_broken_relations.append([
                'internal',
                obj.absolute_url_path(),
                'Unknown location',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
            ])
    return information_of_broken_relations


def add_link_info_to_links(content, link_and_relation_information, obj):
    if not isinstance(content, basestring):
        return
    # find links in page
    links = extract_links_in_string(content)
    # find and add broken relations to link_and_relation_information
    relation_uids = extract_relation_uids_in_string(content)
    broken_relations = get_broken_relation_information_by_uids(relation_uids,
                                                               obj)
    link_and_relation_information.extend(broken_relations)

    if not links:
        # only continue if there are any links
        return

    for link in links:
        link_and_relation_information.append([
            'external',
            obj.absolute_url_path(),
            link,
        ])
    return link_and_relation_information


def extract_relation_uids_in_string(input_string):
    regex = "resolveuid/\w{32}"
    uids_long_form = re.findall(regex, input_string)
    uids = []
    for uid in uids_long_form:
        uids.append(uid.split('/')[1])
    return uids


def get_broken_relation_information_by_uids(relation_uids, obj):
    information_of_broken_relations = []
    for relation_uid in relation_uids:
        if not api.content.get(UID=relation_uid):
            information_of_broken_relations.append([
                'internal',
                obj.absolute_url_path(),
                'Unknown location',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
                'Not specified',
            ])
    return information_of_broken_relations


def add_link_info_to_links(content, link_and_relation_information, obj):
    if not isinstance(content, basestring):
        return
    # find links in page
    links = extract_links_in_string(content)
    # find and add broken relations to link_and_relation_information
    relation_uids = extract_relation_uids_in_string(content)
    broken_relations = get_broken_relation_information_by_uids(relation_uids,
                                                               obj)
    link_and_relation_information.extend(broken_relations)

    if not links:
        # only continue if there are any links
        return

    for link in links:
        link_and_relation_information.append([
            'external',
            obj.absolute_url_path(),
            link,
        ])
    return link_and_relation_information


def find_links_on_brain_fields(brain):
    obj = brain.getObject()
    link_and_relation_information = []

    if not queryUtility(IDexterityFTI, name=obj.portal_type):
        # is not dexterity
        for field in obj.Schema().fields():
            content = field.getRaw(obj)
            links_and_relations_from_rich_text = extract_links_and_relations(
                content, obj)
            links = links_and_relations_from_rich_text[0]
            uids = links_and_relations_from_rich_text[1]
            paths = links_and_relations_from_rich_text[2]
            append_information_for_links_uids_paths(
                link_and_relation_information, obj,
                external_links=links)
            append_information_for_links_uids_paths(
                link_and_relation_information, obj,
                relation_uids=uids)
            append_information_for_links_uids_paths(
                link_and_relation_information, obj,
                relation_paths=paths)

    if queryUtility(IDexterityFTI, name=obj.portal_type):
        for name, field, schemata in iter_fields(obj.portal_type):
            storage = schemata(obj)
            fieldvalue = getattr(storage, name)
            if not fieldvalue:
                continue

            if IRelation.providedBy(field):
                if fieldvalue.isBroken():
                    append_information_for_links_uids_paths(
                        link_and_relation_information, obj,
                        relation_paths=[fieldvalue.from_path])

            elif IURI.providedBy(field):
                append_information_for_links_uids_paths(
                    link_and_relation_information, obj,
                    external_links=[fieldvalue])

            elif IRichText.providedBy(field):
                orig_text = fieldvalue.raw
                links_and_relations_from_rich_text = extract_links_and_relations(
                    orig_text, obj)
                links = links_and_relations_from_rich_text[0]
                uids = links_and_relations_from_rich_text[1]
                paths = links_and_relations_from_rich_text[2]
                append_information_for_links_uids_paths(
                    link_and_relation_information, obj,
                    external_links=links)
                append_information_for_links_uids_paths(
                    link_and_relation_information, obj,
                    relation_uids=uids)
                append_information_for_links_uids_paths(
                    link_and_relation_information, obj,
                    relation_paths=paths)

    return link_and_relation_information


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
        email_address, broken_relations_and_links, plone_site_obj,
        total_time_fetching_external):
    path_to_report = create_excel_report_and_return_filepath(
        broken_relations_and_links)
    send_mail_with_excel_report_attached(email_address, path_to_report,
                                         plone_site_obj,
                                         total_time_fetching_external)


def create_excel_report_and_return_filepath(broken_relations_and_links):
    # make sure every element is a string
    broken_relations_and_links = map(lambda item: map(str, item),
                                     broken_relations_and_links)
    filename = 'linkchecker_report_{}.xlsx'.format(
        time.strftime('%Y_%b_%d_%H%M%S', time.gmtime()))
    current_path = os.path.dirname(os.path.abspath(__file__))
    path_of_excel_workbook_generated = current_path + '/reports/' + filename

    file_i = report_generating.ReportCreator(path_of_excel_workbook_generated)
    file_i.append_report_data(report_generating.LABELS,
                              BOLD &
                              CENTER &
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)
    if broken_relations_and_links:
        file_i.append_report_data(broken_relations_and_links,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)

    file_i.add_general_autofilter()
    file_i.cell_width_autofitter()
    file_i.safe_workbook()
    return path_of_excel_workbook_generated


def send_mail_with_excel_report_attached(email_address, path_to_report,
                                         plone_site_obj,
                                         total_time_fetching_external):
    email_subject = 'Linkchecker Report'
    email_message = '''
    Dear Site Administrator, \n\n
    Please check out the linkchecker report attached to this mail.\n\n
    It took {}ms to fetch the external links for this report.\n\n
    Friendly regards,\n
    your 4teamwork linkcheck reporter\n\n\n
    '''.format(total_time_fetching_external)
    plone_site_path = '/'.join(plone_site_obj.getPhysicalPath())
    portal = api.content.get(plone_site_path)
    report_mailer_instance = report_mailer.MailSender(portal)
    report_mailer_instance.send_feedback(
        email_subject, email_message, email_address, path_to_report)


def main(app, *args):
    plone_site_objs = get_plone_sites_information(app)

    path_site_administrator_emails = os.path.join(
        dirname(dirname(abspath(__file__))), 'site_administrator_emails.json')
    with open(path_site_administrator_emails) as f_:
        site_administrator_emails = json.load(f_)

    for plone_site_obj in plone_site_objs:
        plone_site_id = plone_site_obj.getId()
        email_address = site_administrator_emails[plone_site_id]

        setup_plone(app, plone_site_obj)
        broken_relations_and_links_info = get_broken_relations_and_links()
        broken_relations_and_links = broken_relations_and_links_info[1]
        total_time_fetching_external = broken_relations_and_links_info[0]
        create_and_send_mailreport_to_plone_site_responible_person(
            email_address, broken_relations_and_links, plone_site_obj,
            total_time_fetching_external)
