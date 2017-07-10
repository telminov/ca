import datetime
import os
import subprocess
import re
import shutil
import tempfile

from django.utils import timezone
from django.conf import settings

from core import models


class CaError(Exception):
    """Error create certificate"""


class Ca:
    def generate_root_crt(self, data, recreation=False):
        directory = tempfile.mkdtemp()

        if not os.path.exists(os.path.join(directory, settings.ROOT_CRT_PATH)):
            os.mkdir(os.path.join(directory, settings.ROOT_CRT_PATH))

        self.path_root_key = os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.key')
        self.path_root_crt = os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.crt')

        self._create_pkey(self.path_root_key)
        validity_period = self.calculate_validity_period(data['validity_period'])
        if recreation:
            self._create_root_crt(self.generate_subj_recreation_root_crt(), validity_period)
            self._recreation_model_root_crt(directory)
            self._delete_files(self.path_root_crt)
        else:
            self._create_root_crt(self.generate_subj_root_crt(data), validity_period)
            obj = self._create_model_root_crt(data, directory)
            self._delete_files(self.path_root_crt)
            return obj

    def generate_site_crt(self, cn, validity_period, pk=None, alt_name='DNS'):
        directory = tempfile.mkdtemp()

        if not os.path.exists(os.path.join(directory, cn)):
            os.mkdir(os.path.join(directory, cn))

        self._create_root_files(directory)

        path = os.path.join(directory + '/' + cn + '/' + cn)
        self.path_root_key = os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.key')
        self.path_root_crt = os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.crt')

        self._create_pkey(path + '.key')
        self._create_config_crt(self.generate_subj_site_crt(cn), directory)
        self._create_extfile_crt(cn, alt_name, directory)
        self._create_req_crt(path)
        self._create_site_crt(path, self.calculate_validity_period(validity_period))
        if pk:
            obj = self._recreation_model_site_crt(cn, pk, self.calculate_validity_period(validity_period), directory)
        else:
            obj = self._create_model_site_crt(cn, self.calculate_validity_period(validity_period), directory)
        self._delete_files(path)
        return obj

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

    def _create_root_files(self, directory):
        obj = models.RootCrt.objects.get()
        os.mkdir(os.path.join(directory, settings.ROOT_CRT_PATH))
        with open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.key'), 'w+') as f:
            f.write(obj.key)
        with open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.crt'), 'w+') as f:
            f.write(obj.crt)

    def _delete_files(self, path):
        path_dir = os.path.dirname(os.path.dirname(path))
        shutil.rmtree(path_dir)

    def _eror_processing(self, p, path):
        if p.returncode:
            self._delete_files(path)
            raise CaError('Command:\n' + p.args + '\n' + 'Output:\n' + p.stderr)

    def _create_pkey(self, path):
        command_generate_key = 'openssl genrsa -out {path} 2048'.format(path=path)
        p = subprocess.run(command_generate_key, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        self._eror_processing(p, path)

    def _create_root_crt(self, data, validity_period):
        command_generate_root_crt = 'openssl req -x509 -new -key {path_key} -days {validity_period} -out {path_crt}'.format(
            path_key=self.path_root_key, path_crt=self.path_root_crt, validity_period=validity_period)

        command_subj_root_crt = ' -subj "'
        for key, value in data.items():
            if value not in ['', None] and key != 'validity_period':
                command_subj_root_crt += '/{key}={value}'.format(key=key, value=value)
        command_subj_root_crt += '"'

        p = subprocess.run(command_generate_root_crt + command_subj_root_crt, shell=True, stderr=subprocess.PIPE,
                                   universal_newlines=True)

        self._eror_processing(p, self.path_root_crt)

    def _create_extfile_crt(self, cn, alt_name, directory):
        ext = ['authorityKeyIdentifier=keyid,issuer\n', 'basicConstraints=CA:FALSE\n',
               'keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n',
               'subjectAltName = @alt_names\n', '\n', '[alt_names]\n', '{alt_name}.1 = {cn}\n'.format(alt_name=alt_name,
                                                                                                      cn=cn)]
        with open(os.path.join(directory, cn, cn + '.ext'), 'wb') as f:
            for x in ext:
                f.write(x.encode())

    def _create_config_crt(self, data, directory):
        config = ['[req]\n', 'default_bits = 2048\n', 'prompt = no\n', 'default_md = sha256\n',
                  'distinguished_name = dn\n', '\n', '[dn]\n']
        for key, value in data.items():
            if value not in ['', None] and key != 'validity_period':
                config.append('{key}={value}\n'.format(key=key, value=value))

        with open(os.path.join(directory, data['CN'], data['CN'] + '.cnf'), 'wb') as f:
            for x in config:
                f.write(x.encode())

    def _create_req_crt(self, path):
        command_generate_req = '/bin/bash -c "openssl req -new -key {path_key} -out {path_csr} -config <( cat {path_config} )"'.format(
            path_key=path + '.key', path_csr=path + '.csr', path_config=path + '.cnf')

        p = subprocess.run(command_generate_req, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        self._eror_processing(p, path)

    def _create_site_crt(self, path, validity_period):
        command_generate_crt = 'openssl x509 -req -in {path_csr} -CA {path_root_crt} -CAkey {path_root_key}' \
                               ' -CAcreateserial -out {path_crt} -days {validity_period} -extfile {path_ext}'.format(
            path_csr=path + '.csr', path_root_crt=self.path_root_crt, path_root_key=self.path_root_key, path_crt=path + '.crt',
            validity_period=validity_period, path_ext=path + '.ext')

        p = subprocess.run(command_generate_crt, shell=True, stderr=subprocess.PIPE, universal_newlines=True)

        self._eror_processing(p, path)

    def check_crt_and_key(self, crt, key):
        directory = tempfile.mkdtemp()
        path = os.path.join(directory, 'check')

        if not os.path.exists(path):
            os.mkdir(path)

        with open(os.path.join(path, 'crt.crt'), 'w+') as f:
            f.write(crt)
        with open(os.path.join(path, 'key.key'), 'w+') as f:
            f.write(key)

        p_crt = subprocess.run('openssl x509 -noout -modulus -in {}'.format(os.path.join(path, 'crt.crt')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        self._eror_processing(p_crt, os.path.join(path, 'crt.crt'))

        p_key = subprocess.run('openssl rsa -noout -modulus -in {}'.format(os.path.join(path, 'key.key')), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        self._eror_processing(p_key, os.path.join(path, 'key.key'))

        return (p_crt.stdout == p_key.stdout)

    def _create_model_root_crt(self, data, directory):
        key = open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.key'))
        crt = open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.crt'))
        root_crt = models.RootCrt.objects.create(
            key=key.read(),
            crt=crt.read(),
            country=data['country'],
            state=data['state'],
            location=data['location'],
            organization=data['organization'],
            organizational_unit_name=data['organizational_unit_name'],
            email=data['email']
        )
        key.close()
        crt.close()
        return root_crt

    def _recreation_model_root_crt(self, directory):
        key = open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.key'))
        crt = open(os.path.join(directory, settings.ROOT_CRT_PATH, 'rootCA.crt'))
        root_crt = models.RootCrt.objects.all().update(
            key=key.read(),
            crt=crt.read()
        )
        key.close()
        crt.close()
        return root_crt

    def _create_model_site_crt(self, cn, validity_period, directory):
        key = open(os.path.join(directory, cn, cn + '.key'))
        crt = open(os.path.join(directory, cn, cn + '.crt'))
        site_crt = models.SiteCrt.objects.create(
            key=key.read(),
            crt=crt.read(),
            cn=cn,
            date_end=timezone.now() + datetime.timedelta(days=validity_period),
        )
        key.close()
        crt.close()
        return site_crt

    def _recreation_model_site_crt(self, cn, pk, validity_period, directory):
        key = open(os.path.join(directory, cn, cn + '.key'))
        crt = open(os.path.join(directory, cn, cn + '.crt'))
        site_crt = models.SiteCrt.objects.filter(pk=pk).update(
            key=key.read(),
            crt=crt.read(),
            date_start=timezone.now(),
            date_end=timezone.now() + datetime.timedelta(days=validity_period)
        )
        key.close()
        crt.close()
        return site_crt
