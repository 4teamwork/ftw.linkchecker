from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Testing.makerequest import makerequest
from ftw.linkchecker import linkchecker
from ftw.linkchecker import report_generating
from ftw.linkchecker import report_mailer
from ftw.linkchecker import setup_logger
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.command.broken_link import BrokenLink
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from urlparse import urljoin
from urlparse import urlparse
from z3c.relationfield.interfaces import IRelation
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IURI
import AccessControl
import argparse
import json
import os
import re


def count_parent_pointers(path_segments):
    if not path_segments:
        return 0
    if path_segments[0] != '..':
        return 0
    for index, segment in enumerate(path_segments):
        if segment == '..':
            continue
        else:
            break
    return index + 1


def create_path_even_there_are_parent_pointers(obj, url):
    portal_path_segments = api.portal.get().getPhysicalPath()
    current_path_segments = obj.aq_parent.getPhysicalPath()
    destination_path_segments = filter(len, url.split('/'))
    destination_path = '/'.join(destination_path_segments)
    portal_path = '/'.join(portal_path_segments)

    number_of_parent_pointers = count_parent_pointers(
        destination_path_segments)
    if number_of_parent_pointers >= len(current_path_segments) - len(
            portal_path_segments):
        new_path = portal_path + '/' + destination_path.lstrip('../')
        return new_path
    else:
        if url.startswith('/'):
            output_path = portal_path + url
        else:
            # XXX: < plone5, relative paths are appended to the basepath having a
            # slash at the end. For plone5 support we need to look at this again.
            output_path = urljoin(
                '/'.join(list(obj.aq_parent.getPhysicalPath()) + ['']), url)

        return output_path


def _get_plone_sites(obj):
    for child in obj.objectValues():
        if child.meta_type == 'Plone Site':
            yield child
        elif child.meta_type == 'Folder':
            for item in _get_plone_sites(child):
                yield item


def setup_plone(app, plone_site_obj):
    app = makerequest(app)
    setRequest(app.REQUEST)
    plone_site_obj = app.unrestrictedTraverse(
        '/'.join(plone_site_obj.getPhysicalPath()))
    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(plone_site_obj.acl_users)
    newSecurityManager(plone_site_obj, user)
    setSite(plone_site_obj)


def get_total_fetching_time_and_broken_link_objs():
    portal_catalog = api.portal.get_tool('portal_catalog')
    brains = portal_catalog.unrestrictedSearchResults()
    link_objs = []
    for brain in brains:
        link_objs.extend(find_links_on_brain_fields(brain))

    external_link_objs = []
    internal_link_objs = []
    for link_obj in link_objs:
        if link_obj.is_internal and link_obj.is_broken:
            internal_link_objs.append(link_obj)
        elif not link_obj.is_internal:
            external_link_objs.append(link_obj)

    external_link_objs_and_total_time = linkchecker.work_through_urls(
        external_link_objs)

    external_link_objs, total_time = external_link_objs_and_total_time

    broken_ext_links = filter(lambda link_obj: link_obj.is_broken,
                              external_link_objs)

    internal_link_objs.extend(broken_ext_links)

    return [total_time, internal_link_objs]


def find_links_on_brain_fields(brain):
    obj = brain.getObject()
    link_objs = []

    if not queryUtility(IDexterityFTI, name=obj.portal_type):
        # is not dexterity
        for field in obj.Schema().fields():
            content = field.getRaw(obj)
            # if there is a string having a valid scheme it will be embedded
            # into a href, so we can use the same method as for the dexterity
            # strings and do not need to change the main use case.
            if isinstance(content, basestring):
                if urlparse(content).scheme:
                    content = 'href="%s"' % content
            extract_and_append_link_objs(content, obj, link_objs)

    if queryUtility(IDexterityFTI, name=obj.portal_type):
        for name, field, schemata in iter_fields(obj.portal_type):
            storage = schemata(obj)
            fieldvalue = getattr(storage, name)
            if not fieldvalue:
                continue

            if IRelation.providedBy(field):
                if fieldvalue.isBroken():
                    link = BrokenLink()
                    link.complete_information_for_broken_relation_with_broken_relation_obj(
                        obj, field)
                    link_objs.append(link)

            elif IURI.providedBy(field):
                link = BrokenLink()
                link.complete_information_with_external_path(obj,
                                                             fieldvalue)
                link_objs.append(link)

            elif IRichText.providedBy(field):
                content = fieldvalue.raw
                extract_and_append_link_objs(content, obj, link_objs)

    return link_objs


def extract_and_append_link_objs(content, obj, link_objs):
    links_and_relations_from_rich_text = extract_links_and_relations(
        content, obj)
    append_to_link_and_relation_information_for_different_link_types(
        links_and_relations_from_rich_text,
        link_objs, obj)


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


def extract_links_and_relations(content, obj):
    if not isinstance(content, basestring):
        return [[], [], []]
    # find links in page
    links_and_paths = extract_links_in_string(content, obj)
    # find and add broken relations to link_and_relation_information
    relation_uids = extract_relation_uids_in_string(content)

    links = links_and_paths[0]
    paths = links_and_paths[1]
    return [links, relation_uids, paths]


def extract_links_in_string(input_string, obj):
    # search for href and src
    regex = r"(href=['\"]?([^'\" >]+))|(src=['\"]?([^'\" >]+))"
    raw_results = re.findall(regex, input_string)

    output_urls = []
    output_paths = []
    for url in raw_results:
        # use actual link in findall tuple.

        url = url[1]

        if url.startswith('mailto:'):
            continue
        elif url.startswith('resolveuid/'):
            continue
        elif not urlparse(url).scheme:
            path = create_path_even_there_are_parent_pointers(obj, url)
            output_paths.append(path)
        else:
            output_urls.append(url)

    broken_paths = []
    # only append broken paths
    for path in output_paths:
        try:
            # unrestricted traverse needs utf-8 encoded string
            # but we want unicode in the end.
            api.portal.get().unrestrictedTraverse(path.encode('utf-8'))
        except Exception:
            broken_paths.append(path)

    return [output_urls, broken_paths]


def extract_relation_uids_in_string(input_string):
    regex = re.compile('^[./]*resolve[Uu]id/([^/]*)/?(.*)$')
    return re.findall(regex, input_string)


def append_to_link_and_relation_information_for_different_link_types(
        links_and_relations_from_rich_text, link_and_relation_information,
        obj):
    links = links_and_relations_from_rich_text[0]
    uids = links_and_relations_from_rich_text[1]
    paths = links_and_relations_from_rich_text[2]

    for ext_link in links:
        link = BrokenLink()
        link.complete_information_with_external_path(obj, ext_link)
        link_and_relation_information.append(link)

    for uid in uids:
        link = BrokenLink()
        link.complete_information_with_internal_uid(obj, uid)
        link_and_relation_information.append(link)

    for path in paths:
        link = BrokenLink()
        link.complete_information_with_internal_path(obj, path)
        link_and_relation_information.append(link)


def create_and_send_mailreport_to_plone_site_responible_person(
        email_address, link_objs, plone_site_obj,
        total_time_fetching_external):
    xlsx_file = create_excel_report_and_return_filepath(
        link_objs)
    send_mail_with_excel_report_attached(email_address, plone_site_obj,
                                         total_time_fetching_external,
                                         xlsx_file)


def create_excel_report_and_return_filepath(link_objs):
    file_i = report_generating.ReportCreator()
    file_i.append_report_data(report_generating.LABELS,
                              BOLD &
                              CENTER &
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)
    file_i.append_report_data(link_objs,
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)

    file_i.add_general_autofilter()
    file_i.cell_width_autofitter()
    file_i.safe_workbook()
    xlsx_file = file_i.get_workbook()
    return xlsx_file


def send_mail_with_excel_report_attached(email_address, plone_site_obj,
                                         total_time_fetching_external,
                                         xlsx_file):
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
        email_subject, email_message, email_address, xlsx_file)


def get_configs(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",
                        help="Path to linkchecker config file.")
    parser.add_argument("--log",
                        help="Path to linkchecker log file.")
    args, unknown = parser.parse_known_args()
    path_to_config_file = args.config
    path_to_log_file = args.log

    if not os.path.isfile(path_to_config_file):
        exit()

    with open(path_to_config_file) as f_:
        site_administrator_emails = json.load(f_)

    return site_administrator_emails, path_to_log_file


def main(app, *args):
    configurations = get_configs(args)
    logger = setup_logger(configurations[1])
    logger.info('Linkchecker instance started as expected.')

    plone_site_objs = list(_get_plone_sites(app))
    site_administrator_emails = configurations[0]

    logger.info(
        'Found site administrators email addresses for: %s' % ', '.join(
            site_administrator_emails))

    for plone_site_obj in plone_site_objs:
        setup_plone(app, plone_site_obj)

        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        email_address = site_administrator_emails[portal_path]

        total_time_and_link_objs = get_total_fetching_time_and_broken_link_objs()

        time_for_fetching_external_links = total_time_and_link_objs[0]
        link_objs = total_time_and_link_objs[1]

        logger.info(
            'Finished going through all brains of "{}" and fetching for '
            'external Links. Total time fetching for external Links: '
            '{}ms. In total there were {} links validated.'.format(
                plone_site_obj.title,
                time_for_fetching_external_links,
                link_objs[0].counter))

        create_and_send_mailreport_to_plone_site_responible_person(
            email_address, link_objs, plone_site_obj,
            time_for_fetching_external_links)
