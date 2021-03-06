from cms.cms_toolbars import PlaceholderToolbar
from cms.test_utils.testcases import CMSTestCase
from cms.toolbar.utils import get_object_edit_url, get_object_preview_url

from djangocms_versioning.cms_config import VersioningCMSConfig
from djangocms_versioning.helpers import version_list_url
from djangocms_versioning.test_utils.factories import (
    BlogPostVersionFactory,
    FancyPollFactory,
    PageVersionFactory,
    PollVersionFactory,
    UserFactory,
)
from djangocms_versioning.test_utils.polls.cms_config import PollsCMSConfig
from djangocms_versioning.test_utils.test_helpers import (
    find_toolbar_buttons,
    get_toolbar,
    toolbar_button_exists,
)


class VersioningToolbarTestCase(CMSTestCase):

    def _get_publish_url(self, version, versionable=PollsCMSConfig.versioning[0]):
        """Helper method to return the expected publish url
        """
        admin_url = self.get_admin_url(
            versionable.version_model_proxy, 'publish', version.pk)
        return admin_url

    def _get_edit_url(self, version, versionable=PollsCMSConfig.versioning[0]):
        """Helper method to return the expected edit redirect url
        """
        admin_url = self.get_admin_url(
            versionable.version_model_proxy, 'edit_redirect', version.pk)
        return admin_url

    def test_publish_in_toolbar_in_edit_mode(self):
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, edit_mode=True)

        toolbar.post_template_populate()
        publish_button = find_toolbar_buttons('Publish', toolbar.toolbar)[0]

        self.assertEqual(publish_button.name, 'Publish')
        self.assertEqual(publish_button.url, self._get_publish_url(version))
        self.assertFalse(publish_button.disabled)
        self.assertListEqual(
            publish_button.extra_classes,
            ['cms-btn-action', 'cms-versioning-js-publish-btn'])

    def test_publish_not_in_toolbar_in_preview_mode(self):
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, preview_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Publish', toolbar.toolbar))

    def test_publish_not_in_toolbar_in_structure_mode(self):
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, structure_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Publish', toolbar.toolbar))

    def test_dont_add_publish_for_models_not_registered_with_versioning(self):
        # User objects are not registered with versioning, so attempting
        # to populate a user toolbar should not attempt to add a publish
        # button
        toolbar = get_toolbar(UserFactory(), edit_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Publish', toolbar.toolbar))

    def test_url_for_publish_uses_version_id_not_content_id(self):
        """Regression test for a bug. Make sure than when we generate
        the publish url, we use the id of the version record, not the
        id of the content record.
        """
        # All versions are stored in the version table so increase the
        # id of version id sequence by creating a blogpost version
        BlogPostVersionFactory()
        # Now create a poll version - the poll content and version id
        # will be different.
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, user=self.get_superuser(), edit_mode=True)
        toolbar.post_template_populate()
        publish_button = find_toolbar_buttons('Publish', toolbar.toolbar)[0]

        self.assertEqual(publish_button.url, self._get_publish_url(version))

    def test_edit_in_toolbar_in_preview_mode(self):
        version = PageVersionFactory(content__template="")
        toolbar = get_toolbar(version.content, user=self.get_superuser(), preview_mode=True)

        toolbar.post_template_populate()
        edit_button = find_toolbar_buttons('Edit', toolbar.toolbar)[0]

        self.assertEqual(edit_button.name, 'Edit')
        self.assertEqual(edit_button.url, self._get_edit_url(version, VersioningCMSConfig.versioning[0]))
        self.assertFalse(edit_button.disabled)
        self.assertListEqual(
            edit_button.extra_classes,
            ['cms-btn-action', 'cms-versioning-js-edit-btn'])

    def test_edit_not_in_toolbar_in_edit_mode(self):
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, user=self.get_superuser(), edit_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Edit', toolbar.toolbar))

    def test_edit_not_in_toolbar_in_structure_mode(self):
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, user=self.get_superuser(), structure_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Edit', toolbar.toolbar))

    def test_dont_add_edit_for_models_not_registered_with_versioning(self):
        # User objects are not registered with versioning, so attempting
        # to populate a user toolbar should not attempt to add a edit
        # button
        toolbar = get_toolbar(UserFactory(), user=self.get_superuser(), preview_mode=True)

        toolbar.post_template_populate()

        self.assertFalse(
            toolbar_button_exists('Edit', toolbar.toolbar))

    def test_url_for_edit_uses_version_id_not_content_id(self):
        """Regression test for a bug. Make sure than when we generate
        the edit url, we use the id of the version record, not the
        id of the content record.
        """
        # All versions are stored in the version table so increase the
        # id of version id sequence by creating a blogpost version
        BlogPostVersionFactory()
        # Now create a page version - the page content and version id
        # will be different.
        version = PageVersionFactory(content__template="")
        toolbar = get_toolbar(version.content, user=self.get_superuser(), preview_mode=True)
        edit_url = self._get_edit_url(version, VersioningCMSConfig.versioning[0])

        toolbar.post_template_populate()

        edit_button = find_toolbar_buttons('Edit', toolbar.toolbar)[0]
        self.assertEqual(edit_button.url, edit_url)

    def test_default_cms_edit_button_is_replaced_by_versioning_edit_button(self):
        """
        The versioning edit button is available on the toolbar
        when versioning is installed and the model is versionable.
        """
        pagecontent = PageVersionFactory(content__template="")
        url = get_object_preview_url(pagecontent.content)
        edit_url = self._get_edit_url(pagecontent.content, VersioningCMSConfig.versioning[0])

        with self.login_user_context(self.get_superuser()):
            response = self.client.post(url)

        found_button_list = find_toolbar_buttons('Edit', response.wsgi_request.toolbar)

        # Only one edit button exists
        self.assertEqual(len(found_button_list), 1)
        # The only edit button that exists is the versioning button
        self.assertEqual(found_button_list[0].url, edit_url)

    def test_default_cms_edit_button_is_used_for_non_versioned_model(self):
        """
        The default cms edit button is present for a default model
        """
        unversionedpoll = FancyPollFactory()
        url = get_object_preview_url(unversionedpoll)
        edit_url = get_object_edit_url(unversionedpoll)

        with self.login_user_context(self.get_superuser()):
            response = self.client.post(url)

        found_button_list = find_toolbar_buttons('Edit', response.wsgi_request.toolbar)

        # Only one edit button exists
        self.assertEqual(len(found_button_list), 1)
        # The only edit button that exists is the standard cms button
        self.assertEqual(found_button_list[0].url, edit_url)

    def test_default_edit_button_from_cms_exists(self):
        """
        The default toolbar Edit button exists.
        """
        pagecontent = PageVersionFactory(content__template="")
        edit_url = self._get_edit_url(pagecontent.content, VersioningCMSConfig.versioning[0])

        toolbar = get_toolbar(
            pagecontent.content,
            user=self.get_superuser(),
            toolbar_class=PlaceholderToolbar,
            preview_mode=True,
        )
        toolbar.post_template_populate()
        found_button_list = find_toolbar_buttons('Edit', toolbar.toolbar)

        # The only edit button that exists is the default cms button and not the versioning edit button
        self.assertEqual(len(found_button_list), 1)
        self.assertNotEqual(found_button_list[0].url, edit_url)

    def test_version_menu_for_non_version_content(self):
        # User objects are not registered with versioning, so attempting
        # to populate toolbar shouldn't contain a version menu
        toolbar = get_toolbar(UserFactory(), edit_mode=True)
        toolbar.post_template_populate()
        version_menu = toolbar.toolbar.get_menu('version')
        self.assertIsNone(version_menu)

    def test_version_menu_for_version_content(self):
        # Versioned item should have versioning menu
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, preview_mode=True)
        toolbar.post_template_populate()
        version_menu = toolbar.toolbar.get_menu('version')
        self.assertEqual(version_menu.get_items()[0].name, 'Manage Versions...')

    def test_version_menu_for_none_version(self):
        # Version menu shouldnt be generated if version is None
        version = None
        toolbar = get_toolbar(version, preview_mode=True)
        toolbar.post_template_populate()
        version_menu = toolbar.toolbar.get_menu('version')
        self.assertIsNone(version_menu)

    def test_version_menu_and_url_for_version_content(self):
        # Versioned item should have versioning menu and url should be version list url
        version = PollVersionFactory()
        toolbar = get_toolbar(version.content, preview_mode=True)
        toolbar.post_template_populate()
        version_menu = toolbar.toolbar.get_menu('version')
        self.assertIsNotNone(version_menu)
        self.assertEqual(version_menu.get_items()[0].url, version_list_url(version.content))
