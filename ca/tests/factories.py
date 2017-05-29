import factory

from django.core.files.uploadedfile import SimpleUploadedFile

from ca import models

root_crt_all_fields = b"""-----BEGIN CERTIFICATE-----
MIIDkDCCAngCAQAwDQYJKoZIhvcNAQELBQAwgY0xCzAJBgNVBAYTAnJ1MRIwEAYD
VQQDDAkxMjcuMC4wLjExDzANBgNVBAgMBm1vc2NvdzEiMCAGCSqGSIb3DQEJARYT
bXIuYXJzMTU2QGdtYWlsLmNvbTERMA8GA1UECgwIU29mdC13YXkxETAPBgNVBAsM
CFNvZnQtd2F5MQ8wDQYDVQQHDAZtb3Njb3cwHhcNMTcwNTI5MTAyNjU1WhcNMTgw
NTI5MTAyNjU1WjCBjTELMAkGA1UEBhMCcnUxEjAQBgNVBAMMCTEyNy4wLjAuMTEP
MA0GA1UECAwGbW9zY293MSIwIAYJKoZIhvcNAQkBFhNtci5hcnMxNTZAZ21haWwu
Y29tMREwDwYDVQQKDAhTb2Z0LXdheTERMA8GA1UECwwIU29mdC13YXkxDzANBgNV
BAcMBm1vc2NvdzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOGpc1r8
vwXFuh3P8+NgeH3WM3sJn9VGDX5eB0XXOnu3gx9qJWmQ4JNdrWfMOYoeE4LgtBht
Ubk136rwXtql29KcmhbXExNUuRwf19eS12hP6S8SCDxCIqmW1vC1tzVrLg9g73vF
jv7LyZ8/UuYKB+Y4AeDbftM8W6/DfWkArtrpH1ECtf4Gm9I41KTiOnY74acFbbZM
/QBC1nukrCfP8SIzNOTy/KTWJD6A1EFreGRbbNDhcJh00+1u47iE90A9HjvlQVGx
XgrJ7wa6suuKSBri7NJ8HdgIPvu3eU7b0ZssRbesZ2Uo2CxyVDnislDwsJTJsgWJ
QDGcGkcm7/sgqwsCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAU+AInHxjy+kxk1cx
Iteb2QCuIGGPXRfAhpE2LlT0OiUXJBgeJUHe8J+0OOYIIpW8LRnbar3/XYzINS9b
d3VpBWGxex1tXIIgDKPHFs9U95Pln+y75ox6437Z65o/42UNbYw8M8YdodGSkePi
87i5M7TwTXCHEikBuIFDGqnNqcEFIJRG+3VcXNjRsw3i/QLELVqW4DncVeYS697x
Oh8PXz9F8u0FdH6TOkxx5cKSJu40Zw40thP76xhg5zlQgVEiymgnotuIEb1yL30R
C0o9EBLpTnNZJp0y3lW5p33f4X7khObg4FOnMw1YYL17ZQRHRH+kxJtbX+ltnZr4
Z4Yr7w==
-----END CERTIFICATE-----
"""

root_key_all_fields = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDhqXNa/L8Fxbod
z/PjYHh91jN7CZ/VRg1+XgdF1zp7t4MfaiVpkOCTXa1nzDmKHhOC4LQYbVG5Nd+q
8F7apdvSnJoW1xMTVLkcH9fXktdoT+kvEgg8QiKpltbwtbc1ay4PYO97xY7+y8mf
P1LmCgfmOAHg237TPFuvw31pAK7a6R9RArX+BpvSONSk4jp2O+GnBW22TP0AQtZ7
pKwnz/EiMzTk8vyk1iQ+gNRBa3hkW2zQ4XCYdNPtbuO4hPdAPR475UFRsV4Kye8G
urLrikga4uzSfB3YCD77t3lO29GbLEW3rGdlKNgsclQ54rJQ8LCUybIFiUAxnBpH
Ju/7IKsLAgMBAAECggEAIbTKyzNnYPhYxW0zU6osNTeSdvVID3YoO9DVq0Prs2EE
z+Nt9Sezs69RYGiry4qUhX8Ex4VEqLJ4VzMSJ/yQKhREG9dCPSfxglbrSYLgc+9D
uEksO7vxK32hW1D5LZx1w8xJ2SX4JuzPj97Ihh3Hcka5WRnQBsNEOqurhsyYUZAq
xLjOIUdE2eI4XFlr/xWyPfVRt6eD4aC+pjRCB29Lk4FM6kgyoOYgFghEOg8i2lGD
ONETMhE3Xgg3mlIJdZ5GRdhXMV6l2czVWgkKS4MWX/dna0CvuEqnD03Vwnp+tuLA
AQOcFvYhowFO56CEpJJ8w/Vq3bNvJlXw9eycRDA/SQKBgQD6rCNgIKxscVMqyG+S
jHtXYJIj0ahmRy0dBI4BcjCkKOHnqLsC0cTPFJr1YLwmHIxrIOK5MTv9vgW7b4Zm
JBGSu/gWbfRI2sdiqRr5SlTC7Ok471+E7gy48s6HmVj545Uk6QMsZG1AT/afeu8R
aifEE5UVuTEKjTyOf4TRJ341vQKBgQDmdTwm64QhEck66QhW/HVsce0WCOjOB8Jf
Ff1EcBN+K7BuVAOLOdnJYM64MM3yjZJzdyIZeAAuNKbpTCsOiwjYJcPfcwCZ2Asl
9WzF1AMTjHEF9eLNdBtJ8GiQNPfkoE2XmE0zFw+GXLT7GJAWc5UvzssKUNW3SFe4
CD1M2+/8ZwKBgE6VIi3jcEo6qIjT9u4pLg1xT7783d7aV1EueVoIsyjzTAZ0hdPX
cOw+GGnuHm2QK5D16T2HKrhcFq3ww2BH1F58oMRfSeKA+1p5iuQ1oibNYDuiBv7E
JabhL0+hChykdL/ycDU9cmZj6vuJ7WI3NioovWbm/HHDXwWJAlkTGWS9AoGAUkyT
iqKYsOaVIkCOBeJqXKviqvfLi6ghtas4ovQTQf+AJiZCjbm/GLdFm2lyYqhEII/u
0YGVLusGoFHfHnZwViBGbsm28TnB4XBfw9YOszB4PFSvBgfspt7/uF/yFudYTkbJ
avFVTfpVd0YyTpJAOK50u95aM/XVvZbTrVrtvQkCgYEA96afEKGmgkXUXPBEEf3d
HBqJlmf4nO4dbJxTV1vJ8mvwbN4ZTUSnWFREYU9AR1/3y6ZwpBXsmIZHNZ+0BIbb
fZQqN+qfJCDOKbvKoIOoPRGFofaRk0BRW2FXUnuQSxVBOmOG2pC4Gh+0Dn5ehH27
PKD8NjZOni8nP0uuArMJuX0=
-----END PRIVATE KEY-----
"""


class RootCrt(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RootCrt

    key = SimpleUploadedFile('rootCA.key', root_key_all_fields)
    crt = SimpleUploadedFile('rootCA.crt', root_crt_all_fields)
    country = 'ru'
    state = 'moscow'
    location = 'moscow'
    organization = 'Soft-way'