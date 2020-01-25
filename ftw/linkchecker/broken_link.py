from plone import api
from plone.api.portal import get_tool
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.dexterity.utils import safe_utf8
from urlparse import urlparse
from zope.component import getUtility


class BrokenLink(object):
    table_attrs = [
        'is_internal',
        'link_origin',
        'link_target',
        'status_code',
        'content_type',
        'response_time',
        'error_message',
        'creator',
        'source_state'
    ]

    def __init__(self):
        self.is_broken = None
        self.is_internal = None
        self.link_origin = 'Unknown origin'
        self.link_target = 'Unknown target'
        self.status_code = 'Unknown status code'
        self.content_type = 'Unknown content type'
        self.response_time = 'Unknown response time'
        self.error_message = 'No error occurred'
        self.creator = 'Unknown creator'
        self.source_state = ''

    def __iter__(self):
        for attr in self.table_attrs:
            value = getattr(self, attr, '')
            yield value if isinstance(value, basestring) else ''

    @staticmethod
    def get_review_state(obj):
        wftool = api.portal.get_tool('portal_workflow')
        workflows = wftool.getChainFor(obj)
        reference_obj = obj

        if len(workflows) < 1:
            # no workflow assigned, use parents workflow
            reference_obj = obj.aq_parent
            workflows = wftool.getChainFor(reference_obj)

        try:
            workflow = workflows[0]
        except IndexError:
            # neither obj nor its parent have a workflow assigned
            workflow = None

        if workflow:
            try:
                review_state = wftool.getStatusOf(
                    workflow, reference_obj)['review_state']
            except KeyError:
                review_state = 'No review_state found'
            except TypeError:
                review_state = 'No workflow status found'
        else:
            review_state = 'No workflow found'

        return review_state

    def complete_information_with_internal_path(self, obj_having_path, path):
        # relation not broken if possible to traverse to
        try:
            path = urlparse(
                safe_utf8(path).rstrip('/view').rstrip('/download')).path
            storage = getUtility(IRedirectionStorage)
            path = storage.get(path, path)
            api.portal.get().unrestrictedTraverse(path)
            self.is_broken = False
            self.is_internal = True
        except Exception:
            self.is_broken = True
            self.is_internal = True
            self.link_origin = '/'.join(obj_having_path.getPhysicalPath())
            self.source_state = self.get_review_state(obj_having_path)
            self.link_target = path
            self.creator = obj_having_path.Creator()

    def complete_information_with_external_path(self, obj_having_path, url):
        self.is_internal = False
        self.link_origin = '/'.join(obj_having_path.getPhysicalPath())
        self.source_state = self.get_review_state(obj_having_path)
        self.link_target = url
        self.creator = obj_having_path.Creator()

    def complete_information_with_internal_uid(self, obj_having_uid, uid):
        portal_catalog = get_tool('portal_catalog')
        if not list(portal_catalog.unrestrictedSearchResults(UID=uid)):
            self.is_broken = True
            self.is_internal = True
            self.link_origin = '/'.join(obj_having_uid.getPhysicalPath())
            self.source_state = self.get_review_state(obj_having_uid)
            self.link_target = uid
            self.creator = obj_having_uid.Creator()
        else:
            self.is_broken = False
            self.is_internal = True

    def complete_information_for_broken_relation_with_broken_relation_obj(
            self,
            obj_having_broken_relation, field):
        self.is_broken = True
        self.is_internal = True
        self.link_origin = '/'.join(
            obj_having_broken_relation.getPhysicalPath())
        self.source_state = self.get_review_state(
            obj_having_broken_relation)
        self.link_target = 'Broken link in field: ' + str(field)
        self.creator = obj_having_broken_relation.Creator()
