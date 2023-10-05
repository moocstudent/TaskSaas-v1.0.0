def encrypt(plaintext, key):
    """
    将明文使用给定的密钥进行加密
    :param plaintext: 明文
    :param key: 密钥
    :return: 密文
    """
    ciphertext = ""
    for i in range(len(plaintext)):
        # 获取字符的ASCII码并进行异或运算
        # chr(ord(plaintext[i]) ^ ord(key[i % len(key)])) 表示将密钥进行循环使用
        # 使用format()函数将异或运算的结果转化为16进制字符串，长度不足2位时前面补0
        ciphertext += format(ord(plaintext[i]) ^ ord(key[i % len(key)]), '02x')
    return ciphertext


def decrypt(ciphertext, key):
    """
    将密文使用给定的密钥进行解密
    :param ciphertext: 密文
    :param key: 密钥
    :return: 明文
    """
    plaintext = ""
    # 将16进制字符串按两位一组转换为ASCII码并进行异或运算
    for i in range(0, len(ciphertext), 2):
        plaintext += chr(int(ciphertext[i:i+2], 16) ^ ord(key[(i//2) % len(key)]))
    return plaintext

