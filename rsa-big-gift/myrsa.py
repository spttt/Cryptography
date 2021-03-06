import binascii
import gmpy2
import time
import itertools


def decrypt_by_p_q(n, e, c, p, q):  # 已知p,q，返回明文bytes
    phi = (p-1)*(q-1)
    d = gmpy2.invert(e, phi)
    m = gmpy2.powmod(c, d, n)
    return binascii.a2b_hex(hex(m)[2:])


def analyse_ptbytes(ptbytes):  # m恢复明文分片
    flags = ptbytes[0:8]
    number = int.from_bytes(ptbytes[8:12], 'big')
    massage = ptbytes[-8:]
    return (flags, number, massage)


def Fermat_factorize(input_N, time_limit):    # 费马分解法 分解N得p,q
    start_time = time.time()
    x = gmpy2.iroot(input_N, 2)[0]
    while(time.time()-start_time < time_limit):
        x += 1
        if (gmpy2.iroot(x**2 - input_N, 2)[1] == True):
            y = gmpy2.iroot(x**2 - input_N, 2)[0]
            p = x + y
            q = x - y
            return (p, q)
    return None


def Fermat_factorize_break():  # 费马分解法 尝试所有密文
    ptbytes = {}
    for i in range(21):
        res = Fermat_factorize(N[i], 0.1)
        if(res != None):
            print('Frame', i, '    成功')
            # print(res)
            p, q = res
            ptbytes[i] = decrypt_by_p_q(N[i], e[i], c[i], p, q)
        else:
            print('Frame', i, '超时')
    return ptbytes


def Pollard_p_1(input_N, time_limit):  # Pollard p-1分解法 分解N得p,q
    start_time = time.time()
    B = 2**20
    a = 2
    for i in range(2, B+1):
        if(time.time()-start_time > time_limit):
            break
        a = pow(a, i, input_N)
        p = gmpy2.gcd(a-1, input_N)
        if (1 < p and p < input_N):
            q = input_N//p
            return (p, q)
    return None
# p, q = Pollard_p_1(N[1], 1)
# decrypt_by_p_q(N[1], e[1], c[1], p, q)
# p, q = Pollard_p_1(N[6], 10)
# decrypt_by_p_q(N[2], e[2], c[2], p, q)


def Pollard_p_1_break():  # Pollard p-1分解法 尝试所有密文
    ptbytes = {}
    for i in range(21):
        res = Pollard_p_1(N[i], 10)
        if(res != None):
            print('Frame', i, '    成功')
            # print(res)
            p, q = res
            ptbytes[i] = decrypt_by_p_q(N[i], e[i], c[i], p, q)
        else:
            print('Frame', i, '超时')
    return ptbytes


def is_relatively_prime(m_list):  # 判断两两互素
    for (m1, m2) in itertools.combinations(m_list, 2):
        if(gmpy2.gcd(m1, m2) != 1):
            return False
    return True


def chinese_remainder_theorem(items):  # 中国剩余定理
    M = 1
    m_list = []
    for (a, m) in items:
        m_list.append(m)
        M *= m
    if(is_relatively_prime(m_list) == False):
        print("不两两互素")
        return None
    result = 0
    for (a, m) in items:
        result += a * (M//m) * gmpy2.invert(M//m, m)
    return (result % M)
# chinese_remainder_theorem(([2, 3], [3, 5], [2, 7]))


def find_suitable_e():
    index = {}
    for i in range(0, 21):
        if(e.count(e[i]) > 1):
            if(e[i] not in index):
                index[e[i]] = []
            index[e[i]].append(i)
            # print(i, e[i], e.count(e[i]))
    # index = {65537: [1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 19], 5: [3, 8, 12, 16, 20], 3: [7, 11, 15]}
    for i in index:
        print(i, index[i])
        n_list = []
        for j in index[i]:
            n_list.append(N[j])
        if(is_relatively_prime(n_list)):
            print("互素")
        else:
            print("不互素")


def low_encrypt_e(e, index, length):
    for choice in itertools.combinations(index, length):
        c_m_list = []
        for i in choice:
            c_m_list.append((c[i], N[i]))
        res = chinese_remainder_theorem(c_m_list)
        res = gmpy2.iroot(res, e)
        try:
            print(choice, binascii.a2b_hex(hex(res[0])[2:]))
        except:
            print(choice, "格式错误")


def find_same_modulus():    # 寻找公共模数
    for i in range(21):
        if(N.count(N[i]) > 1):
            print(i, N[i], N.count(N[i]))


def same_modulus_break(e1, e2, c1, c2, n):  # 公共模数攻击
    gcd, x, y = gmpy2.gcdext(e1, e2)
    m = pow(c1, x, n) * pow(c2, y, n) % n
    return binascii.a2b_hex(hex(m)[2:])

    # ################################################################
#  gmpy2.gcdext(3, 5)


def find_same_factor():
    for n1, n2 in itertools.combinations(range(21), 2):
        if(gmpy2.gcd(N[n1], N[n2]) > 1 and N[n1] != N[n2]):
            print(n1, n2)


if __name__ == "__main__":
    N = []
    e = []
    c = []
    for i in range(21):
        with open("data/Frame"+str(i), "r") as f:
            tmp = f.read()
            N.append(int(tmp[0:256], 16))
            e.append(int(tmp[256:512], 16))
            c.append(int(tmp[512:768], 16))
    # print(N)
    # print(e)
    # print(c)

    Frame_dict = {}

    print("\n\n（1）Fermat 分解")
    ptbytes = Fermat_factorize_break()
    # ptbytes = {10: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00will get'}
    print(ptbytes)
    Frame_dict.update(ptbytes)

    print("\n\n（2）Pollard p-1 分解")
    ptbytes = Pollard_p_1_break()
    # ptbytes = {2: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 That is',
    #            6: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 "Logic ',
    #            19: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00instein.'}
    print(ptbytes)
    Frame_dict.update(ptbytes)

    print("\n\n（3）低加密指数攻击")
    find_suitable_e()
    low_encrypt_e(5, [3, 8, 12, 16, 20], 3)
    for i in [3, 8, 12, 16, 20]:
        Frame_dict[i] = b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f'
    low_encrypt_e(3, [7, 11, 15], 2)  # 格式错误

    print("\n\n（4）公共模数攻击")
    find_same_modulus()  # 0和4
    ptbytes = same_modulus_break(e[0], e[4], c[0], c[4], N[0])
    print(ptbytes)
    Frame_dict[0] = ptbytes
    Frame_dict[4] = ptbytes
    # b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00My secre'

    print("\n\n（5）因数碰撞法")
    find_same_factor()  # 1和18
    fac_1_18 = gmpy2.gcd(N[1], N[18])
    ptbytes = decrypt_by_p_q(N[1], e[1], c[1], N[1]//fac_1_18, fac_1_18)
    print(ptbytes)
    # b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00. Imagin'
    Frame_dict[1] = ptbytes
    ptbytes = decrypt_by_p_q(N[18], e[18], c[18], N[18]//fac_1_18, fac_1_18)
    print(ptbytes)
    # b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00m A to B'
    Frame_dict[18] = ptbytes

    print("\n\n")
    # print(Frame_dict)

    print("\n\n转化明文格式")
    massage_dict = {}
    for d in Frame_dict:
        flags, number, massage = analyse_ptbytes(Frame_dict[d])
        massage_dict[number] = massage
    print(sorted(massage_dict.items(), key=lambda item: item[0]))
    # print(massage_dict)

    print("\n\n（6）猜测明文")
    m = []
    m_original = b'My secret is a famous saying of Albert Einstein. That is "Logic will get you from A to B. Imagination will take you everywhere."'
    for i in range(len(m_original)//8):
        m_o = m_original[8*i:8*i+8]
        print(i, m_o)
        # massage_dict[i] = m_original[8*i:8*i+8]
        m_bytes = flags + i.to_bytes(4, "big") + b'\x00'*44 + m_o
        m.append(int.from_bytes(m_bytes, "big"))
    # print(sorted(massage_dict.items(), key=lambda item: item[0]))
    for i in range(21):
        if(i not in Frame_dict):
            for j in range(16):
                if(gmpy2.powmod(m[j], e[i], N[i]) == c[i]):
                    Frame_dict[i] = m[j].to_bytes(64, 'big')
                    break
            else:
                print("can't find Frame", i)

    print("\n\n验证")
    for i in range(21):
        m_int = int.from_bytes(Frame_dict[i], 'big')
        assert(gmpy2.powmod(m_int, e[i], N[i]) == c[i])


# # 附
# Frame_dict = {10: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00will get',
#               2: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 That is',
#               6: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 "Logic ',
#               19: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00instein.',
#               3: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f',
#               8: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f',
#               12: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f',
#               16: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f',
#               20: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t is a f',
#               0: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00My secre',
#               4: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00My secre',
#               1: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00. Imagin',
#               18: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00m A to B',
#               5: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ation wi',
#               7: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00amous sa',
#               9: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ll take ',
#               11: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ying of ',
#               13: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00you ever',
#               14: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 you fro',
#               15: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Albert E',
#               17: b'\x98vT2\x10\xab\xcd\xef\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ywhere."'}

# for i in range(21):
#     flags, number, massage = analyse_ptbytes(Frame_dict[i])
#     print(i, flags, "   ", number, "   ", massage)
