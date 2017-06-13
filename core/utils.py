import datetime
import os
import subprocess
import re
from OpenSSL import crypto

from django.utils import timezone
from django.conf import settings

from core import models

CA_KEY_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.key')
CA_CERT_FILE = os.path.join(settings.ROOT_CRT_PATH, 'rootCA.crt')
PATH_ROOT_KEY = os.path.relpath(os.path.join(settings.MEDIA_ROOT, CA_KEY_FILE))
PATH_ROOT_CRT = os.path.relpath(os.path.join(settings.MEDIA_ROOT, CA_CERT_FILE))


class CaError(Exception):
    """Error create certificate"""


class Ca:
    def generate_root_crt(self, data, recreation=False):
        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, settings.ROOT_CRT_PATH))

        self._create_pkey(PATH_ROOT_KEY)
        validity_period = self.calculate_validity_period(data['validity_period'])
        if recreation:
            self._create_root_crt(self.generate_subj_recreation_root_crt(), validity_period)
        else:
            self._create_root_crt(self.generate_subj_root_crt(data), validity_period)
            self._create_model_root_crt(data)

    def generate_site_crt(self, cn, validity_period, pk=None, alt_name='DNS'):
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, cn)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, cn))

        path = os.path.relpath(settings.MEDIA_ROOT + '/' + cn + '/' + cn)
        self._create_pkey(path + '.key')
        self._create_config_crt(self.generate_subj_site_crt(cn))
        self._create_extfile_crt(cn, alt_name)
        self._create_req_crt(path)
        self._create_site_crt(path, self.calculate_validity_period(validity_period))
        if pk:
            self._recreation_model_site_crt(cn, pk, self.calculate_validity_period(validity_period))
        else:
            self._create_model_site_crt(cn, self.calculate_validity_period(validity_period))

    @staticmethod
    def get_type_alt_names(cn):
        ip_regexp = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        return re.search(ip_regexp, cn)

    @staticmethod
    def calculate_validity_period(date):
        now = datetime.datetime.now()
        validity_period = datetime.datetime.combine(date, now.time()) - now
        return validity_period.days

    @staticmethod
    def write_cert_site(cert, key, cn):
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, cn)):
            os.mkdir(os.path.join(settings.MEDIA_ROOT, cn))

        with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.crt'), 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.key'), 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    @staticmethod
    def generate_subj_root_crt(data):
        options = {
            'C': data['country'],
            'ST': data['state'],
            'L': data['location'],
            'O': data['organization'],
            'OU': data['organizational_unit_name'],
            'CN': data['common_name'],
            'emailAddress': data['email'],
        }
        return options

    @staticmethod
    def generate_subj_recreation_root_crt():
        root = models.RootCrt.objects.get()
        options = {
            'C': root.country,
            'ST': root.state,
            'L': root.location,
            'O': root.organization,
            'OU': root.organizational_unit_name,
            'emailAddress': root.email,
        }
        return options

    @staticmethod
    def generate_subj_site_crt(cn):
        root = models.RootCrt.objects.get()
        options = {
            'C': root.country,
            'ST': root.state,
            'L': root.location,
            'O': root.organization,
            'OU': root.organizational_unit_name,
            'CN': cn,
            'emailAddress': root.email,
        }
        return options

    def _create_pkey(self, path):
        command_generate_key = 'openssl genrsa -out {path} 2048'.format(path=path)
        p = subprocess.run(command_generate_key, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        if p.returncode:
            raise CaError('Command:\n' + p.args + '\n' + 'Output:\n' + p.stderr)

    def _create_root_crt(self, data, validity_period):
        command_generate_root_crt = 'openssl req -x509 -new -key {path_key} -days {validity_period} -out {path_crt}'.format(
            path_key=PATH_ROOT_KEY, path_crt=PATH_ROOT_CRT, validity_period=validity_period)

        command_subj_root_crt = ' -subj "'
        for key, value in data.items():
            if value not in ['', None] and key != 'validity_period':
                command_subj_root_crt += '/{key}={value}'.format(key=key, value=value)
        command_subj_root_crt += '"'

        p = subprocess.run(command_generate_root_crt + command_subj_root_crt, shell=True, stderr=subprocess.PIPE,
                                   universal_newlines=True)
        if p.returncode:
            raise CaError('Command:\n' + p.args + '\n' + 'Output:\n' + p.stderr)

    def _create_extfile_crt(self, cn, alt_name):
        ext = ['authorityKeyIdentifier=keyid,issuer\n', 'basicConstraints=CA:FALSE\n',
               'keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n',
               'subjectAltName = @alt_names\n', '\n', '[alt_names]\n', '{alt_name}.1 = {cn}\n'.format(alt_name=alt_name,
                                                                                                      cn=cn)]
        with open(os.path.join(settings.MEDIA_ROOT, cn, cn + '.ext'), 'wb') as f:
            for x in ext:
                f.write(x.encode())

    def _create_config_crt(self, data):
        config = ['[req]\n', 'default_bits = 2048\n', 'prompt = no\n', 'default_md = sha256\n',
                  'distinguished_name = dn\n', '\n', '[dn]\n']
        for key, value in data.items():
            if value not in ['', None] and key != 'validity_period':
                config.append('{key}={value}\n'.format(key=key, value=value))

        with open(os.path.join(settings.MEDIA_ROOT, data['CN'], data['CN'] + '.cnf'), 'wb') as f:
            for x in config:
                f.write(x.encode())

    def _create_req_crt(self, path):
        command_generate_req = '/bin/bash -c "openssl req -new -key {path_key} -out {path_csr} -config <( cat {path_config} )"'.format(
            path_key=path + '.key', path_csr=path + '.csr', path_config=path + '.cnf')

        p = subprocess.run(command_generate_req, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        if p.returncode:
            raise CaError('Command:\n' + p.args + '\n' + 'Output:\n' + p.stderr)

    def _create_site_crt(self, path, validity_period):
        command_generate_crt = 'openssl x509 -req -in {path_csr} -CA {path_root_crt} -CAkey {path_root_key}' \
                               ' -CAcreateserial -out {path_crt} -days {validity_period} -extfile {path_ext}'.format(
            path_csr=path + '.csr', path_root_crt=PATH_ROOT_CRT, path_root_key=PATH_ROOT_KEY, path_crt=path + '.crt',
            validity_period=validity_period, path_ext=path + '.ext')

        p = subprocess.run(command_generate_crt, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        if p.returncode:
            raise CaError('Command:\n' + p.args + '\n' + 'Output:\n' + p.stderr)

    def _create_model_root_crt(self, data):
        root_crt = models.RootCrt.objects.create(
            key=CA_KEY_FILE,
            crt=CA_CERT_FILE,
            country=data['country'],
            state=data['state'],
            location=data['location'],
            organization=data['organization'],
            organizational_unit_name=data['organizational_unit_name'],
            email=data['email']
        )
        return root_crt

    def _create_model_site_crt(self, cn, validity_period):
        site_crt = models.SiteCrt.objects.create(
            key=os.path.join(cn, cn + '.key'),
            crt=os.path.join(cn, cn + '.crt'),
            cn=cn,
            date_end=timezone.now() + datetime.timedelta(days=validity_period),
        )
        return site_crt

    def _recreation_model_site_crt(self, cn, pk, validity_period):
        site_crt = models.SiteCrt.objects.filter(pk=pk).update(
            key=os.path.join(cn, cn + '.key'),
            crt=os.path.join(cn, cn + '.crt'),
            date_start=timezone.now(),
            date_end=timezone.now() + datetime.timedelta(days=validity_period)
        )
        return site_crt