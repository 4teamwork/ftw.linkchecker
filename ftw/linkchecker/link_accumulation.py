from Products.Archetypes.Field import ComputedField
from Products.Archetypes.Field import ReferenceField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Field import TextField
from ftw.linkchecker import LOGGER_NAME
from ftw.linkchecker.link import Link
from ftw.linkchecker.status_checker import StatusChecker
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from urlparse import urljoin
from urlparse import urlparse
from z3c.relationfield.interfaces import IRelation
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IURI
import logging
import re


class Accumulator(object):
    """Helper class to accumulate link objects in a Plone site.

    The Accumulator collects all brains within a Plone site. By making use
    of the LinkOnFieldSeeker Link objects are collected. The collected Link
    objects are then checked to be valid or broken.
    """

    def __init__(self, site_config):
        self.time_external_routine = 0
        self.internal_broken_link_objs = []
        self.external_broken_link_objs = []

        self._site_config = site_config
        self._logger = logging.getLogger(LOGGER_NAME)
        self._external_link_objs = []

    def discover_broken_links(self):
        self._all_links = self._get_all_links()
        self._separate_links_to_internal_external()

        status_checker = StatusChecker(
            self._external_link_objs, self._site_config.configuration.timeout_config)
        status_checker.work_through_urls()

        self.external_broken_link_objs = status_checker.broken_external_links
        self.time_external_routine = status_checker.total_time

    def _get_all_links(self):
        portal_catalog = api.portal.get_tool('portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults()
        link_seeker = LinkOnFieldSeeker()
        link_objs = []
        for brain in brains:
            link_objs.extend(link_seeker.find_links_on_brain_fields(brain))

        return link_objs

    def _separate_links_to_internal_external(self):
        for link_obj in self._all_links:
            if link_obj.is_internal and link_obj.is_broken:
                self.internal_broken_link_objs.append(link_obj)
                self._logger.info(
                    'Found broken link object pointing to {}'.format(
                        link_obj.link_origin))
            elif not link_obj.is_internal:
                self._external_link_objs.append(link_obj)


class LinkOnFieldSeeker(object):
    """Seek for link-like patterns in likely fields on objects.

    The main functionality of this class is delegated to either an
    ArchetypeSeeker or a DexteritySeeker which do most of the work.

    Including what we gain from delegating, these steps are done:
      - Differentiate between Archetype/Dexterity objects
      - Collect all fields in the Plone schema objects
      - Filter fields which have the capability of holding text
      - Search the text within the fields for link-like text parts
      - Collect the link-like text parts
      - Instantiate Link objects for the matches
    """

    def find_links_on_brain_fields(self, brain):
        obj = brain.getObject()
        link_objs = []

        seeker = self._construct_seeker(brain)
        seeker.append_links(obj, link_objs)

        return link_objs

    def _construct_seeker(self, obj):
        """Get type specific seeker instance.
        """
        if queryUtility(IDexterityFTI, name=obj.portal_type):
            return DexteritySeeker()
        else:
            return ArchetypeSeeker()


class BaseSeeker(object):
    """Base class for searching link-like strings.

    This base class is meant to be inherited by a more specific class.
    On its own its more of a set of helper tools to find link-like strings in
    text, completing Plone paths and sorting links by external url and internal
    reference (path or uid).
    """

    def _extract_and_append_link_objs(self, content, obj, link_objs):
        links_and_relations_from_rich_text = self._extract_links_and_relations(
            content, obj)
        self._append_to_link_and_relation_information_for_different_link_types(
            links_and_relations_from_rich_text,
            link_objs, obj)

    def _extract_links_and_relations(self, content, obj):
        if not isinstance(content, basestring):
            return [[], [], []]
        # find links in page
        links_and_paths = self._extract_links_in_string(content, obj)
        # find and add broken relations to link_and_relation_information
        relation_uids = self._extract_relation_uids_in_string(content)

        links = links_and_paths[0]
        paths = links_and_paths[1]
        return [links, relation_uids, paths]

    def _extract_links_in_string(self, input_string, obj):
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
                path = self._create_path_even_if_there_are_parent_pointers(
                    obj, url)
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

    def _extract_relation_uids_in_string(self, input_string):
        regex = re.compile('resolveuid/(\w{32})', flags=re.IGNORECASE)

        return re.findall(regex, input_string)

    def _append_to_link_and_relation_information_for_different_link_types(
            self, links_and_relations_from_rich_text,
            link_and_relation_information,
            obj):
        links = links_and_relations_from_rich_text[0]
        uids = links_and_relations_from_rich_text[1]
        paths = links_and_relations_from_rich_text[2]

        for ext_link in links:
            link = Link()
            link.complete_information_with_external_path(obj, ext_link)
            link_and_relation_information.append(link)

        for uid in uids:
            link = Link()
            link.complete_information_with_internal_uid(obj, uid)
            link_and_relation_information.append(link)

        for path in paths:
            link = Link()
            link.complete_information_with_internal_path(obj, path)
            link_and_relation_information.append(link)

    def _create_path_even_if_there_are_parent_pointers(self, obj, url):
        portal_path_segments = api.portal.get().getPhysicalPath()
        current_path_segments = obj.aq_parent.getPhysicalPath()
        destination_path_segments = filter(len, url.split('/'))
        destination_path = '/'.join(destination_path_segments)
        portal_path = '/'.join(portal_path_segments)

        number_of_parent_pointers = self._count_parent_pointers(
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
                    '/'.join(list(
                        obj.aq_parent.getPhysicalPath()) + ['']), url)

            return output_path

    def _count_parent_pointers(self, path_segments):
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


class ArchetypeSeeker(BaseSeeker):
    """Specific implementation of the BaseSeeker for AT objects.

    Using the BaseSeeker class the ArchetypeSeeker iterates the fields of
    a Archetype type object schema. If the field is one likely containing any
    links (text fields, reference fields etc.) it is searched for link-like
    strings.
    The strings are sorted by UIDs, external links or internal links and then
    as a link object (holding additional information) appended to a list.
    """

    def append_links(self, obj, link_objs):
        plausible_fields = (
            TextField,
            ReferenceField,
            ComputedField,
            StringField)
        for field in obj.Schema().fields():
            if not isinstance(field, plausible_fields):
                continue
            content = field.getRaw(obj)
            if isinstance(field, ReferenceField):
                uid = content
                try:
                    uid_from_relation = obj['at_ordered_refs']['relatesTo']
                except Exception:
                    uid_from_relation = []
                uid.extend(uid_from_relation)
                self._append_to_link_and_relation_information_for_different_link_types(
                    [[], uid, []], link_objs, obj)

            if not isinstance(content, basestring):
                continue
            # if there is a string having a valid scheme it will be embedded
            # into a href, so we can use the same method as for the dexterity
            # strings and do not need to change the main use case.
            scheme = urlparse(content).scheme
            if scheme and scheme in ['http', 'https']:
                content = 'href="%s"' % content
            self._extract_and_append_link_objs(content, obj, link_objs)

        return link_objs


class DexteritySeeker(BaseSeeker):
    """Specific implementation of the BaseSeeker for DX objects.

    Using the BaseSeeker class the DexteritySeeker iterates the fields of
    a Dexterity type object schema. If the field is one likely containing any
    links (text fields, reference fields etc.) it is searched for link-like
    strings.
    The strings are sorted by UIDs, external links or internal links and then
    as a link object (holding additional information) appended to a list.
    """

    def append_links(self, obj, link_objs):
        for name, field, schemata in self._iter_fields(obj.portal_type):
            storage = schemata(obj)
            fieldvalue = getattr(storage, name)
            if not fieldvalue:
                continue

            if IRelation.providedBy(field):
                if fieldvalue.isBroken():
                    link = Link()
                    link.complete_information_for_broken_relation_with_broken_relation_obj(
                        obj, field)
                    link_objs.append(link)

            elif IURI.providedBy(field):
                link = Link()
                link.complete_information_with_external_path(obj,
                                                             fieldvalue)
                link_objs.append(link)

            elif IRichText.providedBy(field):
                content = fieldvalue.raw
                self._extract_and_append_link_objs(content, obj, link_objs)

        return link_objs

    def _iter_fields(self, portal_type):
        for schemata in self._iter_schemata_for_protal_type(portal_type):
            for name, field in getFieldsInOrder(schemata):
                if not getattr(field, 'readonly', False):
                    yield (name, field, schemata)

    def _iter_schemata_for_protal_type(self, portal_type):
        if queryUtility(IDexterityFTI, name=portal_type):
            # is dexterity
            fti = getUtility(IDexterityFTI, name=portal_type)

            yield fti.lookupSchema()
            for schema in getAdditionalSchemata(portal_type=portal_type):
                yield schema
