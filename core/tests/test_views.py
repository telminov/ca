from OpenSSL import crypto

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from core.tests import factories
from core import models


class CrtExistsView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('root_crt_exists'))
        redirect_url = reverse('login') + '?next=' + reverse('root_crt_exists')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('root_crt_exists'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/root_already_exists.html')


class CrtNotExistsView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('root_crt_not_exists'))
        redirect_url = reverse('login') + '?next=' + reverse('root_crt_not_exists')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('root_crt_not_exists'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/root_not_exists.html')


class IndexRootCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('index_root'))
        redirect_url = reverse('login') + '?next=' + reverse('index_root')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index_root'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/index.html')

    def test_root_crt_exists(self):
        factories.RootCrt.create()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('index_root'))

        self.assertRedirects(response, reverse('root_crt_exists'))


class LoadRootCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('has_root_key'))
        redirect_url = reverse('login') + '?next=' + reverse('has_root_key')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('has_root_key'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/has_root_key.html')

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('has_root_key'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index_root')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Load root certificate', ''))

    # в первом приближении
    def test_success_url(self):
        self.client.force_login(user=self.user)
        crt = SimpleUploadedFile('rootCA.crt', factories.root_crt_all_fields)
        key = SimpleUploadedFile('rootCA.key', factories.root_key_all_fields)
        response = self.client.post(reverse('has_root_key'), {'crt': crt, 'key': key})

        self.assertRedirects(response, reverse('view_root_crt'))

    def test_root_crt_exists(self):
        factories.RootCrt.create()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('has_root_key'))

        self.assertRedirects(response, reverse('root_crt_exists'))


class ViewRootCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('has_root_key'))
        redirect_url = reverse('login') + '?next=' + reverse('has_root_key')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_root_crt'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/view_root_crt.html')

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_root_crt'))

        cert = crypto.load_certificate(crypto.FILETYPE_PEM, factories.root_crt_all_fields).get_subject()

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('View root certificate', ''))
        self.assertEqual(response.context['cert'], cert)
        self.assertEqual(str(response.context['crt_validity_period']), '2018-05-29 10:26:55')

    def test_initial_form(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_root_crt'))

        self.assertIn(factories.root_crt_all_fields.decode(), str(response.context['form']))
        self.assertIn(factories.root_key_all_fields.decode(), str(response.context['form']))

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_root_crt'))

        self.assertEqual(response.status_code, 404)


class RootCrtDeleteView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('delete_root_crt'))
        redirect_url = reverse('login') + '?next=' + reverse('delete_root_crt')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_root_crt'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/delete_root.html')

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_root_crt'))

        self.assertEqual(response.status_code, 404)

    # в первом приближении
    def test_delete(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('delete_root_crt'))

        self.assertEqual(models.RootCrt.objects.all().count(), 0)
        self.assertRedirects(response, reverse('index_root'))

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_root_crt'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('View certificate', reverse('view_root_crt')))
        self.assertEqual(response.context['breadcrumbs'][2], ('Delete root certificate', ''))


class GenerateRootCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )

    def test_auth(self):
        response = self.client.get(reverse('no_root_key'))
        redirect_url = reverse('login') + '?next=' + reverse('no_root_key')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('no_root_key'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/root_crt_managing/no_root_key.html')

    def test_root_crt_exists(self):
        factories.RootCrt.create()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('no_root_key'))

        self.assertRedirects(response, reverse('root_crt_exists'))

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('no_root_key'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index_root')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Generate root certificate', ''))

    # в первом приближеии
    def test_success_url(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('no_root_key'), {'C': 'ru', 'ST': 'moscow', 'L': 'moscow', 'O': 'soft-way',
                                                             'OU': 'soft-way', 'CN': '127.0.0.1',
                                                             'emailAddress': 'test44@gmail.com',
                                                             'validity_period': '2032-05-29'})

        self.assertEqual(models.RootCrt.objects.all().count(), 1)
        self.assertRedirects(response, reverse('view_root_crt'))


class SearchSiteCrt(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('index'))
        redirect_url = reverse('login') + '?next=' + reverse('index')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('index'))

        self.assertRedirects(response, reverse('root_crt_not_exists'))

    def test_context(self):
        factories.SiteCrt.create()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('index'))

        self.assertEqual(response.context['object'], models.RootCrt.objects.get())
        self.assertEqual(len(response.context['object_list']), 1)

    def test_search(self):
        factories.SiteCrt.create()
        factories.SiteCrt.create(cn='127.0.0.2')
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('index'), {'cn': '127.0.0.1'})

        self.assertEqual(len(response.context['object_list']), 1)


class CreateSiteCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('create_crt'))
        redirect_url = reverse('login') + '?next=' + reverse('create_crt')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('create_crt'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_crt.html')

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('create_crt'))

        self.assertRedirects(response, reverse('root_crt_not_exists'))

    def test_success_url(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('create_crt'), {'cn': '127.0.0.1', 'validity_period': '2019-05-29'})

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(models.SiteCrt.objects.get().cn, '127.0.0.1')

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('create_crt'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Create new certificate', ''))


class LoadSiteCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('upload_existing'))
        redirect_url = reverse('login') + '?next=' + reverse('upload_existing')

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('upload_existing'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/upload_existing.html')

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('upload_existing'))

        self.assertRedirects(response, reverse('root_crt_not_exists'))

    def test_context(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('upload_existing'))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('Load exists certificate', ''))

    # в первом приближении
    def test_form_valid_files(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('upload_existing'),
                                    {'crt_file': SimpleUploadedFile('test.crt', factories.site_crt_all_fields),
                                     'key_file': SimpleUploadedFile('test.key', factories.site_key_all_fields)})

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(models.SiteCrt.objects.all().count(), 1)

    def test_form_valid_text(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('upload_existing'), {'crt_text': factories.site_crt_all_fields.decode(),
                                                                 'key_text': factories.site_key_all_fields.decode()})

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(models.SiteCrt.objects.all().count(), 1)


class ViewSiteCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()
        factories.SiteCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('view_crt', kwargs={'pk': '1'}))
        redirect_url = reverse('login') + '?next=' + reverse('view_crt', kwargs={'pk': '1'})

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/view_crt.html')

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_crt', kwargs={'pk': '1'}))

        cert = crypto.load_certificate(crypto.FILETYPE_PEM, factories.site_crt_all_fields).get_subject()

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('View %s' % cert.CN, ''))
        self.assertEqual(response.context['cert'], cert)
        self.assertEqual(str(response.context['crt_validity_period']), '2019-05-29 13:08:33')

    def test_initial_form(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_crt', kwargs={'pk': '1'}))

        self.assertIn(factories.site_crt_all_fields.decode(), str(response.context['form']))
        self.assertIn(factories.site_key_all_fields.decode(), str(response.context['form']))

    def test_root_crt_not_exists(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('view_crt', kwargs={'pk': '2'}))

        self.assertEqual(response.status_code, 404)


class SiteCrtDeleteView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()
        factories.SiteCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('delete_crt', kwargs={'pk': '1'}))
        redirect_url = reverse('login') + '?next=' + reverse('delete_crt', kwargs={'pk': '1'})

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/delete_crt.html')

    def test_site_crt_not_exists(self):
        models.SiteCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.status_code, 404)

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_crt', kwargs={'pk': '1'}))

        self.assertRedirects(response, reverse('root_crt_not_exists'))

    # в первом приближении
    def test_delete(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('delete_crt', kwargs={'pk': '1'}))

        self.assertEqual(models.SiteCrt.objects.all().count(), 0)
        self.assertRedirects(response, reverse('index'))

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('delete_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('View %s' % models.SiteCrt.objects.get().cn,
                                                              reverse('view_crt', kwargs={'pk': 1})))
        self.assertEqual(response.context['breadcrumbs'][2], ('Delete %s' % models.SiteCrt.objects.get().cn, ''))


class RecreationSiteCrtView(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd',
        )
        factories.RootCrt.create()
        factories.SiteCrt.create()

    def test_auth(self):
        response = self.client.get(reverse('recreation_crt', kwargs={'pk': '1'}))
        redirect_url = reverse('login') + '?next=' + reverse('recreation_crt', kwargs={'pk': '1'})

        self.assertRedirects(response, redirect_url)

    def test_smoke(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('recreation_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/recreation_crt.html')

    def test_root_crt_not_exists(self):
        models.RootCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('recreation_crt', kwargs={'pk': '1'}))

        self.assertRedirects(response, reverse('root_crt_not_exists'))

    def test_site_crt_not_exists(self):
        models.SiteCrt.objects.all().delete()
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('recreation_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.status_code, 404)

    def test_context(self):
        self.client.force_login(user=self.user)

        response = self.client.get(reverse('recreation_crt', kwargs={'pk': '1'}))

        self.assertEqual(response.context['breadcrumbs'][0], ('Home', reverse('index')))
        self.assertEqual(response.context['breadcrumbs'][1], ('View %s' % models.SiteCrt.objects.get().cn,
                         reverse('view_crt', kwargs={'pk': '1'})))
        self.assertEqual(response.context['breadcrumbs'][2], ('Recreation certificate', ''))

    # в первом приближении
    def test_recreation(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('recreation_crt', kwargs={'pk': '1'}), {'validity_period': '2020-05-29'})

        self.assertRedirects(response, reverse('view_crt', kwargs={'pk': '1'}))
        self.assertEqual(str(models.SiteCrt.objects.get().date_end)[:10], '2020-05-29')
