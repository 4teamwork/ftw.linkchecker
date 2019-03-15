from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from plone.app.textfield import RichTextValue
from z3c.relationfield import RelationValue
from zope.component.hooks import setSite


def add_textarea_to_page(portal):
    setSite(portal)
    content_page = create(Builder('sl content page').titled(u'contentpage'))
    textarea_having_link = create(Builder('sl textblock')
                                  .within(content_page)
                                  .having(text=RichTextValue('...'))
                                  .titled('textarea'))
    return textarea_having_link


def add_archetype_link_to_plone_site(portal):
    fti = portal.portal_types.get('ftw.simplelayout.ContentPage')
    fti.allowed_content_types = tuple(
        list(fti.allowed_content_types) + ['Link'])
    page = create(Builder('sl content page'))
    link_to_delete = create(Builder('link').titled(u'test link')
                            .within(page)
                            .having(remoteUrl=portal.absolute_url()))
    link_which_stays = create(Builder('link').titled(u'test link')
                              .within(page)
                              .having(remoteUrl=portal.absolute_url()))

    create(Builder('link').titled(u'archetype link')
           .within(page)
           .having(remoteUrl=portal.absolute_url()))
    create(Builder('link').titled(u'archetype link').within(page).having(
        remoteUrl=portal.absolute_url() + '/ImWearingAnInvisibilityCloak'))
    create(Builder('link').titled(u'archetype link')
           .within(page)
           .having(remoteUrl=portal.absolute_url(),
                   relatedItems=link_which_stays.UID()))
    create(Builder('link').titled(u'archetype link')
           .within(page)
           .having(remoteUrl=portal.absolute_url(),
                   relatedItems=link_to_delete.UID()))

    # delete this obj, so the reference will be broken
    parent = link_to_delete.aq_parent
    parent.manage_delObjects([link_to_delete.getId()])


def set_up_test_environment(portal):
    """Set up two plone sites. Both plone sites having the same content.
    Plone sites have working and broken relations and external links.
    """

    setSite(portal)
    pages = [create(
        Builder('sl content page').titled(u'Page {}'.format(index)))
        for index in range(9)]

    # create broken relation value
    broken_rel = RelationValue(pages[2])
    broken_rel.to_id = None

    content_for_the_setup = [
        {
            'test_number': '1',
            'content_type': 'sl textblock',
            'within': pages[0],
            'title': '1',
            'int_url': None,
            'ext_url': portal.absolute_url(),
            'text': None,
            'textblock_within1': None,
            'textblock_url1': None,
            'textblock_within2': None,
            'textblock_url2': None,
        },
        {
            'test_number': '1',
            'content_type': 'sl textblock',
            'within': pages[0],
            'title': '0',
            'int_url': None,
            'ext_url': portal.absolute_url() + '/gibtsnicht',
            'text': None,
            'textblock_within1': None,
            'textblock_url1': None,
            'textblock_within2': None,
            'textblock_url2': None,
        },
        {
            'test_number': '2',
            'content_type': 'sl textblock',
            'within': pages[0],
            'title': 'default title',
            'int_url': RelationValue(pages[1]),
            'ext_url': None,
            'text': None,
            'textblock_within1': None,
            'textblock_url1': None,
            'textblock_within2': None,
            'textblock_url2': None,
        },
        {
            'test_number': '2',
            'content_type': 'sl textblock',
            'within': pages[0],
            'title': 'broken relation',
            'int_url': broken_rel,
            'ext_url': None,
            'text': None,
            'textblock_within1': None,
            'textblock_url1': None,
            'textblock_within2': None,
            'textblock_url2': None,
        },
        {
            'test_number': '3',
            'content_type': 'sl content page',
            'within': pages[3],
            'title': 'Content page on page 3',
            'int_url': None,
            'ext_url': None,
            'text': None,
            'textblock_within1': pages[3],
            'textblock_url1': 'content-page-on-page-3',
            'textblock_within2': pages[3],
            'textblock_url2': 'Idunnoexist',
        },
        {
            'test_number': '4',
            'content_type': 'sl content page',
            'within': pages[4],
            'title': 'Content page on page 4',
            'int_url': None,
            'ext_url': None,
            'text': None,
            'textblock_within1': pages[4],
            'textblock_url1': './content-page-on-page-4',
            'textblock_within2': pages[4],
            'textblock_url2': './Icantbefound',
        },
        {
            'test_number': '5',
            'content_type': 'sl content page',
            'within': pages[5],
            'title': 'Content page on page 5',
            'int_url': None,
            'ext_url': None,
            'text': None,
            'textblock_within1': pages[5],
            'textblock_url1': '/page-5',
            'textblock_within2': pages[5],
            'textblock_url2': '/Iwasnevercreated',
        },
        {
            'test_number': '6',
            'content_type': 'sl content page',
            'within': pages[6],
            'title': 'Content page on page 6',
            'int_url': None,
            'ext_url': None,
            'text': None,
            'textblock_within1': pages[6],
            'textblock_url1': portal.absolute_url(),
            'textblock_within2': pages[6],
            'textblock_url2': portal.absolute_url() + '/Sadnottoexist',
        },
    ]

    for content in content_for_the_setup:
        make_content_for_me(content['content_type'],
                            content['within'],
                            content['title'],
                            content['int_url'],
                            content['ext_url'],
                            content['text'],
                            content['textblock_within1'],
                            content['textblock_url1'],
                            content['textblock_within2'],
                            content['textblock_url2'], )


def make_content_for_me(content_type, within, title, int_url, ext_url, text,
                        textblock_within1, textblock_url1, textblock_within2,
                        textblock_url2):
    create(Builder(content_type)
           .within(within)
           .titled(title.decode('utf-8'))
           .having(internal_link=int_url,
                   external_link=ext_url,
                   text=text))

    if textblock_within1 and textblock_url1:
        add_link_into_textarea_without_using_the_browser(textblock_within1,
                                                         textblock_url1)

    if textblock_within2 and textblock_url2:
        add_link_into_textarea_without_using_the_browser(textblock_within2,
                                                         textblock_url2)


def add_link_into_textarea_without_using_the_browser(page, url):
    create(Builder('sl textblock')
           .within(page)
           .having(text=RichTextValue('<a href="%s">a link</a>' % url))
           .titled('A textblock link not using the browser'))
