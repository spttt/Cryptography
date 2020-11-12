
import base64
import hashlib
import binascii
from Crypto.Cipher import AES


def adjust_parity_bit(bytestocheck):
    res = b''
    for x in bytestocheck:
        if(bin(x).count('1') % 2 == 0):
            x = x ^ 1
        res += x.to_bytes(1, 'big')
    return res


cipher_base64 = '9MgYwmuPrjiecPMx61O6zIuy3MtIXQQ0E59T3xB6u0Gyf1gYs2i3K9Jxaa0zj4gTMazJuApwd6+jdyeI5iGHvhQyDHGVlAuYTgJrbFDrfB22Fpil2NfNnWFBTXyf7SDI'
cipher_bytes = base64.b64decode(cipher_base64)

MRZ_line2 = b'12345678<8<<<1110182<1111167<<<<<<<<<<<<<<<4'
Number_and_check = MRZ_line2[:10]
Birth_and_check = MRZ_line2[13:20]
Expiry_and_check = MRZ_line2[21:28]
mrz_information = Number_and_check + Birth_and_check + Expiry_and_check
# b'12345678<811101821111167'

K_seed = hashlib.sha1(mrz_information).hexdigest()[:32]
D_hex = K_seed + '00000001'
Hash_D = hashlib.sha1(binascii.a2b_hex(D_hex)).digest()
# b'\xeb\x86E\xd9\x7f\xf7%\xa9\x98\x95*\xa3\x81\xc50y\t\x96%6'

K_a = Hash_D[:8]
K_b = Hash_D[8:16]

K_a_adjust = adjust_parity_bit(K_a)
K_b_adjust = adjust_parity_bit(K_b)
key = K_a_adjust + K_b_adjust
print(key)

IV = b'\x00'*16

m = AES.new(key, AES.MODE_CBC, IV).decrypt(cipher_bytes)
print(m)

# b'Herzlichen Glueckwunsch. Sie haben die Nuss geknackt. Das Codewort lautet: Kryptographie!\x01\x00\x00\x00\x00\x00\x00'
