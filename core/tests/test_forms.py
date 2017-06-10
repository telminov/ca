from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from core.tests import factories

root_crt_without_required_subj = b"""-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAOlwYLIJGowlMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAnJ1MRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTcwNTMwMDkwNDA0WhcNNDQxMDE1MDkwNDA0WjBF
MQswCQYDVQQGEwJydTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAsKy/7Gx5FMnuZcW/ZYrvVFeVUODYoO7L9LF6ST3dyYttehQMjosWMJrG
yWg2TxTbXmEC6ESvQfbvIKOM5AvR9jXd4+pLK5kUcc90X6J97weOui2mPL78rOmk
zaIc0fCdtOCBVmTpVTTa+bjDHKcC3rAOckxAafrXxzmbIcdsFNu11ai5hveaPokP
E3HjNUYyxG8+cvsYVcY6eZ4qaUQaXOtamBwq7BQx3qkAcCs2xMLsEevhelDShOef
hk4oBcOP8w2mww2aKhyUgaNoKhCT5AlwWV11s6RADE9E6Jcyd5cDUXJZb8DOSdM4
dVNxHAPuFbkapFsz7qy20bwd4vNBfQIDAQABo1AwTjAdBgNVHQ4EFgQUY+65I8yK
Jl36TYHnCKzpcsdYS70wHwYDVR0jBBgwFoAUY+65I8yKJl36TYHnCKzpcsdYS70w
DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAGZUyt3qJLbvV8WDBLvLL
XMyQWOlkPovGV9KA/es5tfCVeTuE5NCIZ8wtTNZ/09VA8lPOEmoPFdqHlfrURO1/
yqpJzSGXxlUbVOZJx67FN7q+gp0rvVd/6OsvNjbrdFPHC3RgU33E/qeBPgDhapDj
XzbIQcMFuUOIaSLg2B259Y6IOMGt4iAJHgwqSImjYrpcL8FbiWKon24DX65qncqf
IB2BXirAXlbj5EuLLfv0yik6vk1UCbdMH5CE0mCDbrTYWJpbPU7bKfiUFN5l7Wo2
R6ALVaDbdJI4fsWLT3mmHFcjoD6dZauIHNEqUEO5puI6iNbGxUPq/jaPVmAocO/+
iw==
-----END CERTIFICATE-----
"""

root_key_without_required_sub = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAsKy/7Gx5FMnuZcW/ZYrvVFeVUODYoO7L9LF6ST3dyYttehQM
josWMJrGyWg2TxTbXmEC6ESvQfbvIKOM5AvR9jXd4+pLK5kUcc90X6J97weOui2m
PL78rOmkzaIc0fCdtOCBVmTpVTTa+bjDHKcC3rAOckxAafrXxzmbIcdsFNu11ai5
hveaPokPE3HjNUYyxG8+cvsYVcY6eZ4qaUQaXOtamBwq7BQx3qkAcCs2xMLsEevh
elDShOefhk4oBcOP8w2mww2aKhyUgaNoKhCT5AlwWV11s6RADE9E6Jcyd5cDUXJZ
b8DOSdM4dVNxHAPuFbkapFsz7qy20bwd4vNBfQIDAQABAoIBAHNppkaP5dkKwM2D
DLEMvaNfQ49+EoWu+VVzyuqlm4jZqD6jckB745cExO81QKUQfu18eiW5GLQC19t+
e79NaW9paPZGS6zDZ3OhjegbgiDv0vEUeRAdw3pBdwNN733FrYBHWLZTXYnn6VRQ
ukSxZVKLuCQ6Y6nXz7W5j/nVCGnmtzhbevkdF+GidbpiEVbTUDKf9YCgvP+KH62u
zQHrwLxBWdY7QJ8zEmeDROuUTLDkN7lA5aCyuJ4DTQ66H5dSny2v/Ibv56/4hvt6
J4UlNPop2Hmeh0MskQmaHamxjXvRcr8Tg6/FIHMtlquLkFUm8j0n0VpmnGkk5Rau
f4DwfgECgYEA22BeWOH2fKCWoW8nFsmGWDfuDeZXP1EbkXsoLqEi04lFZCfdYDzp
dUANin2iqfpJ2tccvw+YTSH3xcRf5p7fUR/hb5nyrQl7Be5IIYNYPLeMvKP8ocKW
F9AvZYD5ksAXg0MBRQzedyWI5yTpNpwAChn/VVJk3pcdVtexQ3QmdB0CgYEAzitp
+ldpibyAOJv+YWdwsHDOWZ0tofTEHTcb6genLj0LddreGJJ9jpvYvMbsMWQev0zK
ybeqI10sTFzteemqNEBFJjVxzn0TLRuKtmD+Q/6wr2HolY1KyhQdJn3jeI3QfzdU
MYX3vwSiR2eywA6MzclLCXNmitNIZTGJLYd1xOECgYABvL6ih4+TJxZqSt4NYSUu
N6sr8wIH31WPjmEgFWiYMkMZavNm2rSimBJDYYFTRUcmc4Onw7DaE4XJzCdSRTnR
g6YeYyK32hZeUqfBlC+zs2Rq7gWHJmpX3+8wJ5hSYDEPeg1dhZ+RY/u0kOdD5nJd
oh0SiOeBl8LEuEqQFTBkxQKBgQDF9xfnAyJa2H7CXL9xJhMlyNvLXsqfddkOOIl8
OecE1ib3/rY+IAOh+PGvqs7HSlzf0cvyz4H2PRQ5Kw34fy8oxwHfA3iJDr5oFMco
ApCEF73uWfQsDiTfT1sCR+UxL/MhBK66cuoGKFvudptEIXSAcSW1KHMxIFmmmV8g
Ma8a4QKBgQCS+IKxOTVGCvJaw99mhGuAun+amKWy3LalXtBIsDcyn0/0TVJ9LZQt
QNITqfd43y2I2boK/9QIY68gmVBytfPz6tcGyqW/unfVa72FO2VKgoqc9NHB8G/+
rvRLUXTNxllTbnA0EmCgBDzSzNYBJ12fIAKL+6WK/YR4FvTxXcpkaA==
-----END RSA PRIVATE KEY-----
"""

site_crt_not_unique_cn = b"""-----BEGIN CERTIFICATE-----
MIIDkDCCAngCAQAwDQYJKoZIhvcNAQELBQAwgY0xCzAJBgNVBAYTAnJ1MRIwEAYD
VQQDDAkxMjcuMC4wLjExDzANBgNVBAgMBm1vc2NvdzEiMCAGCSqGSIb3DQEJARYT
bXIuYXJzMTU2QGdtYWlsLmNvbTERMA8GA1UECgwIU29mdC13YXkxETAPBgNVBAsM
CFNvZnQtd2F5MQ8wDQYDVQQHDAZtb3Njb3cwHhcNMTcwNTI5MTMwODMzWhcNMTkw
NTI5MTMwODMzWjCBjTEPMA0GA1UEBwwGbW9zY293MQswCQYDVQQGEwJydTERMA8G
A1UECgwIU29mdC13YXkxIjAgBgkqhkiG9w0BCQEWE21yLmFyczE1NkBnbWFpbC5j
b20xDzANBgNVBAgMBm1vc2NvdzERMA8GA1UECwwIU29mdC13YXkxEjAQBgNVBAMM
CTEyNy4wLjAuMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKkN4JvZ
3QuR1nxZVXy9LUQ5JslnT/3+iZ0WJydsDznpcVIFKV1pmy8WSL1NOE1XlHqqS3xk
9Odlu40NsqTBW/WtizKwv/WTc4RUPfbk46PBzkGiGZuThZ8EfvSA7d/ydHefD1l9
Mi1zBMg8LSGBFvqRwAQuPvCQIsarZe01tyie9gQ2FkvWbYaBiwKiTJZbdZhEPR7F
CgjlxdEVgXtsJ5JIUr2xHpR0Z5AeHhbXkD5nxcJfwk5XCVOa2NcMj+I12zgZJHJL
VEF8CHLy4od80HcJ2RKkwF5rurRAURGqrGs6Yu3O6qvFZjk54YmR9SJzq2AdIkx9
SR0gMnTXYPPe6tECAwEAATANBgkqhkiG9w0BAQsFAAOCAQEALEMKo0pNsej4SBZ0
NsKi+WbWgN7hRkMIsw+RmzPl+L+1jhDp6I48M5b65B+FsUlTdViM8gPN7AuW1uLv
Dq9ZNXHFLXeu0znegIryu857K5XJqUz8W/K01BWyZfgOfWpZsaYmMnMtsiI/j6l/
PU/cHWvYnuRaZuKxUcjRdBdKEdR16XC47KnJKt7eXucJOK0U4zXLfEQZQ2dUVAUt
NNcDUtvlz/BVCnz5v0aYRkW6k1K0wDgqcOIKsZGXm+55mazQXv96QQ2ylThioCaT
sZ/xLSK1cn4n1EXUzHn3sy0nz0wauQwYL09Wg6uesZBHgWceVAR7uKN0lmg6TY47
w6QCaw==
-----END CERTIFICATE-----
"""

site_key_not_unique_cn = b"""-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCpDeCb2d0LkdZ8
WVV8vS1EOSbJZ0/9/omdFicnbA856XFSBSldaZsvFki9TThNV5R6qkt8ZPTnZbuN
DbKkwVv1rYsysL/1k3OEVD325OOjwc5Bohmbk4WfBH70gO3f8nR3nw9ZfTItcwTI
PC0hgRb6kcAELj7wkCLGq2XtNbconvYENhZL1m2GgYsCokyWW3WYRD0exQoI5cXR
FYF7bCeSSFK9sR6UdGeQHh4W15A+Z8XCX8JOVwlTmtjXDI/iNds4GSRyS1RBfAhy
8uKHfNB3CdkSpMBea7q0QFERqqxrOmLtzuqrxWY5OeGJkfUic6tgHSJMfUkdIDJ0
12Dz3urRAgMBAAECggEARB9keEkliuj8vmUdTsPIvuos2BH6qQZuG8/2fStNQ2/v
izarQYoxz5qyOx4n5vq4yWlgO8NO8QQMvL1dVIjabri9E/Mnl2UQsq1jvt7jYHTT
kZ0ppoie2sJsCkj+EjVYe2+sNsp9ctUbgzjEkvC6+sPK1aRxFm1uphIhY6I2qXYl
PzPejE0wwImFPztGzizuPerrsDJrzBboOkAzNqTY8+bdxB2xWQWUq7yyUHzwHC3u
S2a4R8TTmnJb2L8b8A1axYnJigtNk5CTH/Zo4OjDyZ5iLV70AKwSni0ObJAZ7CnB
h2WOV8M3jZP3mIhLoE1C3COSlupA4KbAaUVISDds8QKBgQDWL/VaXEsXxTFR2MBf
Cs85C36rsDCn8HBsIKzrfmxBkNSv5MqMwPTWfwK3D6GN82Ob4/rdULrSPJx7g/4Q
Mzf4yn5kcSZLR7IkiFbxc4roe73T+T+PJmoXDNpyhVIw4LENw6HGwc2a1ZRrGNgA
8a7ftinykgan0CcVww0IBK1SRQKBgQDKDmJ4cl9dLuDTZuOunoBgiz+Oly9xb4ee
rWi3lA4uXw40b8S3AQ8pcrp3Hiw93AX9tfsouaqRYjeBgAuc9PUw48PNS86Ky2ml
GKYcpdkGhcxiqjKvROXzi/LZIhaZh+Itl/66w3+As5g6p5f05uxpeQ0ISjFha5vR
1IGjudBFHQKBgQCO2Wt8uYNHtjefi705Zh8wv47a+OZqizyfkOdjJG0VCYAgU6oX
V/WzPQBVkTJBVyt+4/0DL/15i/0dj7mZml9hKcREPwa4PHf+T4QVAueJCEZhoqGW
Wpt1BhiHOo3HlYPgVzKFOepjssCK8QXXE1l7UKYHZwbTU0tOA0mkqGHkNQKBgEAD
nKjiO1pPTsVLFJku+CceFq27MjmzBvl7oPCARJnmXZ65Rk5gVIhiI7c3ZPbYLUG7
FO5LHEHhJwqtIYDBjqjFkDQLb01Dsp2umHn9BSvu2djsaRBkOKIXVYH7LcPIbBzb
ycUryMpim7kBfcAGJSIpSrq0nr5plD0/IS9Y4CX1AoGBAKhECGpbeQBUXtvAqx3v
tc3tMYXmlG4D5+P2gvhhc0kTjawFHVkVIZdaLncPCbYfp74lxZnCN7L9gOV9nXyK
UI8MAatj7MfJeWXyGYZv0jefP1Qp2GSe8vs499rgejrQAE5lTtsveBgnrYZBQKit
nd9JKxdGrDkWBPgnzxE4m9mU
-----END PRIVATE KEY-----
"""


class RootCrtForm(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )

    def test_upload_random_file(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('has_root_key'), {'crt': SimpleUploadedFile('test.txt', b'test'),
                                                              'key': SimpleUploadedFile('tests.txt', b'test')})

        self.assertContains(response, 'Please load valid certificate and key')

    def test_upload_crt_without_required_subj(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('has_root_key'), {'crt': SimpleUploadedFile('rootCA.crt',
                                                                                        root_crt_without_required_subj),
                                                              'key': SimpleUploadedFile('rootCA.key',
                                                                                        root_key_without_required_sub)})

        self.assertContains(response,
                            'Please enter required field in certificate: Country, State, Location, Organization')


class CreateSiteCrtForm(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )
        factories.RootCrt.create()
        factories.SiteCrt.create()

    def test_create_crt_not_unique_cn(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('create_crt'), {'cn': '127.0.0.1', 'validity_period': '2019-05-30'})

        self.assertContains(response, 'Common name 127.0.0.1 not unique')


class LoadSiteCrtForm(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='Serega',
            password='passwd'
        )
        factories.RootCrt.create()
        factories.SiteCrt.create()

    def test_upload_random_files(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('upload_existing'), {'crt_file': SimpleUploadedFile('test.txt', b'test'),
                                                                 'key_file': SimpleUploadedFile('tests.txt', b'test')})

        self.assertContains(response, 'Please load valid certificate and key')

    def test_upload_crt_file_not_unique_cn(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('upload_existing'), {'crt_file': SimpleUploadedFile('site.crt',
                                                                                                site_crt_not_unique_cn),
                                                                 'key_file': SimpleUploadedFile('site.key',
                                                                                                site_key_not_unique_cn)})

        self.assertContains(response, 'Certificate with Common name 127.0.0.1 already exists in db')

    def test_upload_random_text(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('upload_existing'), {'crt_text': 'test', 'key_text': 'test'})

        self.assertContains(response, 'Please load valid certificate and key')

    def test_upload_crt_text_not_unique_cn(self):
        self.client.force_login(user=self.user)

        response = self.client.post(reverse('upload_existing'), {'crt_text': site_crt_not_unique_cn.decode(),
                                                                 'key_text': site_key_not_unique_cn.decode()})

        self.assertContains(response, 'Certificate with Common name 127.0.0.1 already exists in db')
