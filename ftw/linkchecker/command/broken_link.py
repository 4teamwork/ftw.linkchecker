from plone import api


class BrokenLink(object):
    table_attrs = [
        'is_internal',
        'link_origin',
        'link_target',
        'status_code',
        'content_type',
        'response_time',
        'header_location',
        'error_message',
    ]

    def __init__(self):
        self.is_broken = None
        self.is_internal = None
        self.link_origin = 'Unknown origin'
        self.link_target = 'Unknown target'
        self.status_code = 'Unknown status code'
        self.content_type = 'Unknown content type'
        self.response_time = 'Unknown response time'
        self.header_location = 'Unknown header location'
        self.error_message = 'No error occurred'

    def __iter__(self):
        for attr in self.table_attrs:
            value = getattr(self, attr, '')
            yield value if isinstance(value, basestring) else ''

    def __len__(self):
        return len(self.table_attrs)

    def complete_information_with_internal_path(self, obj_having_path, path):
        # relation not broken if possible to traverse to
        try:
            api.portal.get().unrestrictedTraverse(path)
            self.is_broken = False
        except KeyError:
            self.is_broken = True
            self.is_internal = True
            self.link_origin = '/'.join(obj_having_path.getPhysicalPath())
            self.link_target = path

    def complete_information_with_external_path(self, obj_having_path, url):
        self.is_internal = False
        self.link_origin = '/'.join(obj_having_path.getPhysicalPath())
        self.link_target = url

    def complete_information_with_internal_uid(self, obj_having_uid, uid):
        if not api.content.get(UID=uid):
            self.is_broken = True
            self.is_internal = True
            self.link_origin = '/'.join(obj_having_uid.getPhysicalPath())
        else:
            self.is_broken = False

    def complete_information_for_broken_relation_with_broken_relation_obj(
            self,
            obj_having_broken_relation):
        self.is_broken = True
        self.is_internal = True
        self.link_origin = '/'.join(
            obj_having_broken_relation.getPhysicalPath())
