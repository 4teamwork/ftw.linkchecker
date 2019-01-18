from ftw.builder import Builder
from ftw.builder import create
from plone.app.textfield import RichTextValue
from zope.component.hooks import setSite


def set_up_test_environment(portal):
    """Set up two plone sites. Both plone sites having the same content.
    Plone sites have working and broken relations and external links.
    """
    broken_link = portal.absolute_url() + '/gibtsnicht'
    working_link = portal.absolute_url()

    setSite(portal)
    pages = [create(
        Builder('sl content page').titled(u'Page {}'.format(index)))
        for index in range(9)]

    # Test 1 setup
    for index, url in enumerate([broken_link, working_link]):
        add_sl_textblock_having_external_link(pages[0], url,
                                              index)

    # Test 3 setup
    create(Builder('sl content page')
           .within(pages[3])
           .titled(u'Content page on page 3'))
    add_link_into_textarea_without_using_the_browser(
        pages[3],
        'content-page-on-page-3')
    add_link_into_textarea_without_using_the_browser(
        pages[3],
        'Idunnoexist')
    # Test 4 setup
    create(Builder('sl content page')
           .within(pages[4])
           .titled(u'Content page on page 4'))
    add_link_into_textarea_without_using_the_browser(
        pages[4],
        './content-page-on-page-4')
    add_link_into_textarea_without_using_the_browser(
        pages[4],
        './Icantbefound')
    # Test 5 setup
    create(Builder('sl content page')
           .within(pages[5])
           .titled(u'Content page on page 5'))
    add_link_into_textarea_without_using_the_browser(
        pages[5],
        '/page-5')
    add_link_into_textarea_without_using_the_browser(
        pages[5],
        '/Iwasnevercreated')
    # Test 6 setup
    create(Builder('sl content page')
           .within(pages[6])
           .titled(u'Content page on page 6'))
    valid_uid = 'resolveuid/' + pages[8].UID()
    broken_uid = 'resolveuid/99999999999999999999999999999999'
    add_link_into_textarea_without_using_the_browser(
        pages[6],
        valid_uid)
    add_link_into_textarea_without_using_the_browser(
        pages[6],
        broken_uid)
    # Test 7 setup
    create(Builder('sl content page')
           .within(pages[7])
           .titled(u'Content page on page 7'))
    add_link_into_textarea_without_using_the_browser(
        pages[7],
        portal.absolute_url())
    add_link_into_textarea_without_using_the_browser(
        pages[7],
        portal.absolute_url() + '/Sadnottoexist')


def add_sl_textblock_having_external_link(current_page, link, index):
    create(Builder('sl textblock')
           .within(current_page)
           .having(external_link=link)
           .titled(str(index).decode("utf-8")))


def add_link_into_textarea_without_using_the_browser(page, url):
    create(Builder('sl textblock')
           .within(page)
           .having(text=RichTextValue('<a href="%s">a link</a>' % url))
           .titled('A textblock link not using the browser'))
