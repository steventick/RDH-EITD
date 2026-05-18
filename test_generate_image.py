#!/usr/bin/env python3
"""
test_generate_image.py
Juanli Sun, Yan Ke, Minqing Zhang, Shijun Xiang 2025.

Contains methods to visualize and save stage-wise computational results as images during scheme implementation.
"""
from secrets import randbelow
import sys
import os
import cv2 as cv
import gmpy2 as gy
import numpy as np
from dj_mod.crypto import keygen
from dj_mod.utils import int_to_mpz, crm, inv_mod, pow_mod
from dj_mod.crypto import damgard_jurik_reduce,EncryptedNumber
import time
# from utils import calculate_psnr,calculate_ssim,calculate_nae,calculate_kl_divergence,calculate_cross_entropy

def main():
    # ------parameter set
    n_bits = 32  # changable
    threshold = 5  # changable
    n_shares = 7  # changable
    ve_len = 1  # FirEmb embedding level, [1,2 * n_bits - 8 - 1]
    rr_len2 = 1  # SecEmb embedding level, [1,14]
    print(f"Parameters:Len(N)={2 * n_bits},n={n_shares},k={threshold},FirEmbLevel={ve_len},SecEmbLevel={rr_len2}")

    # ------keygen starts.
    start_time = time.time()
    s = 1
    public_key, private_key_ring = keygen(n_bits=n_bits, s=s, threshold=threshold, n_shares=n_shares)
    end_time = time.time()
    print(f"ContentOwner-KeyGen: {end_time - start_time} s")
    # ------keygen done.

    # ------content owner:image encryption starts.
    # m = randbelow(public_key.n_s)
    start_time = time.time()
    project_root = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_root, 'data', 'img')
    filename = os.path.join(data_dir, 'man') #changable
    file_to_read = filename if filename.lower().endswith('.png') else filename + '.png'
    if not os.path.exists(file_to_read):
        print(f"ERROR: Image file '{file_to_read}' not found.")
        print(f"       Current working directory: {os.getcwd()}")
        print(f"       Please verify:")
        print(f"       1. The file exists at the specified path")
        print(f"       2. You have read permissions for this file")
        sys.exit(1)
    img = cv.imread(file_to_read, 0)
    h, w = img.shape[:2]
    pixelSequence = img.reshape([h * w, ])
    img_cipher = []

    # Convert encrypted ciphertext to image: e.g., N (1024-bit pub key), n_bits=512, ciphertext=2048 bits (bytes_per_c=256).
    bytes_per_c = n_bits // 2  # bytes_per_c = ciphertext len/8 = pub key len/4 = n_bits/2
    temp = int(pow(bytes_per_c, 0.5))  # Square root: calculate length/width multiplier vs original image
    h_cbytes = h * temp  # Ciphertext image height = original image height × multiplier
    w_cbytes = w * temp
    img_cipher_bytes = []
    for i in range(h * w):
        m = gy.mpz(pixelSequence[i])
        c = public_key.encrypt(m)  # encrypt each pixel
        img_cipher.append(c)
        # Visualize ciphertext as an image: convert it to a byte string first, then to [0,255] pixels.
        c_int = int(c.value)
        c_bytes = c_int.to_bytes(bytes_per_c, byteorder='big')  # Convert the ciphertext c (an integer) into a byte string.
        if len(c_bytes) < bytes_per_c:
            c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes  # Pad with leading zeros if insufficient, without affecting the integer value
        img_cipher_bytes.append(c_bytes)
    byte_list = [byte for item in img_cipher_bytes for byte in item]  # convert into byte list
    cipher_array = np.array(byte_list, dtype=np.uint8)  # convert each byte into int
    cv.imwrite(filename + '_enc.png', cipher_array.reshape(h_cbytes, w_cbytes))

    end_time = time.time()
    print(f"ContentOwner-Enc: {end_time - start_time} s")
    # ------content owner: image encryption done.

    # ------content owner: FirEmb starts
    start_time = time.time()
    img_embed_ma = []
    img_cipher_bytes = []
    ### Embed with VE from the first to the penultimate one.
    #When the plaintext pixel value m<128, it can be left-shifted by up to 120 bits;
    # when the pixel value satisfies 128≤m≤255, it can be left-shifted by up to 119 bits-
    # otherwise, the result may exceed N. However, these are ciphertext pixels,
    # and the corresponding plaintext values cannot be determined,
    # so decrement the num_shift by 1.
    num_shift = 2 * n_bits - 8 - 1
    ma = np.random.choice([0, 1], size=ve_len * (h * w - 1), replace=True)  # generate ma
    for i in range(h * w - 1):
        ma_piece = ma[(i) * ve_len:(i + 1) * ve_len]  # Slice ma by the embedding level.
        ma_str = ''.join(map(str, ma_piece))  # Turn into a string.
        ma_value = gy.mpz(ma_str, 2)  # Turn into mpz.
        c = img_cipher[i]  # The ciphertext is of EncryptNumber type.
        #The first ** stands for 2^{ve_len}; the second * (for EncryptNumber) denotes exponentiation,
        # and specifically exponentiation followed by modulo n^2.
        # The entire expression represents (c^{2^{ve_len}}).
        # WARNING: Expressing it as c2 = c ** (2 ** ve_len) % public_key.n ** 2 is WRONG!
        c2 = 2 ** ve_len * c
        gb = pow_mod(public_key.n + 1, ma_value, public_key.n ** 2)  # g^b
        # gb = quick_powermod(public_key.n + 1, ma2_value, public_key.n ** 2)
        c3value = c2.value * gb % public_key.n ** 2  # Left-shift ciphertext c via Paillier additive homomorphism, embedding b in the lower X bits.
        c3 = EncryptedNumber(value=c3value, public_key=public_key)
        img_embed_ma.append(c3)
        ############################# convert it into pixel
        c_int = int(c3.value)
        c_bytes = c_int.to_bytes(bytes_per_c, byteorder='big')
        if len(c_bytes) < bytes_per_c:
            c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes
        img_cipher_bytes.append(c_bytes)
        ############################## convertion done.
    ###Embed the last pixel using VE.
    c = img_cipher[h * w - 1]
    c2 = 2 ** 12 * c
    gb = pow_mod(public_key.n + 1, ve_len, public_key.n ** 2)
    # gb = quick_powermod(public_key.n + 1, ma2_value, public_key.n ** 2)
    c3value = c2.value * gb % public_key.n ** 2
    c3 = EncryptedNumber(value=c3value, public_key=public_key)
    img_embed_ma.append(c3)
    ############################# convert it into pixel
    c_int = int(c3.value)
    c_bytes = c_int.to_bytes(bytes_per_c, byteorder='big')
    if len(c_bytes) < bytes_per_c:
        c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes
    img_cipher_bytes.append(c_bytes)
    ############################# convertion done.
    byte_list = [byte for item in img_cipher_bytes for byte in item]
    cipher_array = np.array(byte_list, dtype=np.uint8)
    cv.imwrite(filename + '_emb_ma.png', cipher_array.reshape(h_cbytes, w_cbytes))
    ############################## Store ciphertext with embedded ma as image.
    end_time = time.time()
    print(f"ContentOwner-FirEmb: {end_time - start_time} s")
    # ------content owner:FirEmb done.

    # while True:
    #     user_input = input("Client operations done. Continue with server operations? Press 1 to proceed, other keys to exit: ")
    #     if user_input == '1':
    #         print("Continuing program execution...")
    #         break
    #     else:
    #         print("\nExiting program.")
    #         sys.exit()

    # ------Data Server:SecEmb starts.
    start_time = time.time()
    img_embed_ma_mb = []
    ##Reserve the last pixel; embed mb in the rest.
    img_cipher_bytes = []
    mb = np.random.choice([0, 1], size=rr_len2 * (h * w - 1), replace=True)  # generate mb
    for i in range(h * w - 1):
        mb_piece = mb[i * rr_len2:(i + 1) * rr_len2]
        mb_str = ''.join(map(str, mb_piece))
        mb_value = gy.mpz(mb_str, 2)
        c = img_embed_ma[i]
        cvalue = c.value
        while (cvalue % (2 ** rr_len2) != (mb_value)): #embedding with RR method
            r = gy.mpz(randbelow(public_key.n - 1)) + 1
            rn = pow_mod(r, public_key.n, public_key.n ** 2)
            # rn = quick_powermod(r, public_key.n, public_key.n ** 2)
            c1 = c.value * rn % public_key.n ** 2
            cvalue = c1
        c1 = EncryptedNumber(value=cvalue, public_key=public_key)
        img_embed_ma_mb.append(c1)
        ############################## convert it into pixel
        c_int = int(c1.value)
        c_bytes = c_int.to_bytes(bytes_per_c, byteorder='big')
        if len(c_bytes) < bytes_per_c:
            c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes
        img_cipher_bytes.append(c_bytes)
        ############################# convertion done.
    ###The last pixel uses the RR method to embed rr_len2.
    c = img_embed_ma[h * w - 1]
    cvalue = c.value
    while (cvalue % (2 ** 4) != (rr_len2)):
        r = gy.mpz(randbelow(public_key.n - 1)) + 1
        rn = pow_mod(r, public_key.n, public_key.n ** 2)
        # rn = quick_powermod(r, public_key.n, public_key.n ** 2)
        c1 = c.value * rn % public_key.n ** 2
        cvalue = c1
    c1 = EncryptedNumber(value=cvalue, public_key=public_key)
    img_embed_ma_mb.append(c1)
    ############################## convert it into pixel
    c_int = int(c1.value)
    c_bytes = c_int.to_bytes(bytes_per_c, byteorder='big')
    if len(c_bytes) < bytes_per_c:
        c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes
    img_cipher_bytes.append(c_bytes)
    ################################# convertion done.
    byte_list = [byte for item in img_cipher_bytes for byte in item]
    cipher_array = np.array(byte_list, dtype=np.uint8)
    cv.imwrite(filename + '_emb_mb.png', cipher_array.reshape(h_cbytes, w_cbytes))
    ################################## Store ciphertext with embedded mb as image.
    end_time = time.time()
    print(f"DataHider/Server-SecEmb: {end_time - start_time} s")
    # ------Data Server:SecEmb done.

    # ------Each Distributed Receiver: extraction of mb starts.
    ##Extract the length rr_len2 from the last pixel.
    start_time = time.time()
    c = img_embed_ma_mb[h * w - 1]
    rr_len2_ext = c.value % 2 ** 4
    assert np.array_equal(rr_len2, rr_len2_ext)  # Check if the embedded info in the last pixel matches the extracted one.
    ##Extract the embedded information mb from the other pixels.
    mb_ext = []
    for i in range(h * w - 1):
        c = img_embed_ma_mb[i]
        mb_value_ext = c.value % 2 ** rr_len2_ext
        mb_value_ext = bin(mb_value_ext)[2:].zfill(rr_len2_ext)
        mb_ext.append(mb_value_ext)
    mb_ext = np.array(list(''.join(mb_ext)), dtype=int)
    assert np.array_equal(mb, mb_ext)  # Check if the embedded valid info mb matches the extracted one.
    # print('extrac mb exactly!')
    end_time = time.time()
    print(f"Every Distributed Receiver-Ext1: {end_time - start_time} s")
    # ------Each Distributed Receiver: extraction of mb done.

    #-------Starting distributed partial decryption...
    start_time = time.time()
    img_cipher_bytes = []
    img_share_decryption_list = np.zeros((threshold, h * w), dtype=gy.mpz)  # Init a 2D array for k images (each pixel is a ciphertext value).

    for i in range(h * w):
        # Simulate a progress bar.
        # if i == 0:
        #     print('(0)', end='')
        # if (i + 1) % 512 == 0:
        #     print('.')
        #     print(f'({(i + 1) // 512})', end='')
        # else:
        #     print('.', end='')
        c = img_embed_ma_mb[i]
        # c_share_decryption = private_key_ring.decrypt(c)#original decryption, including share decryption and combining decryption together.
        c_share_decryption = private_key_ring.shareDecrypt(c) # share(partial) decryption.

        for img_index in range(threshold):
            img_share_decryption_list[img_index, i] = c_share_decryption[img_index] # Collect partial decryption results of threshold shares.

    ############################## Save threshold decryption results as ciphertext images
    for img_index in range(threshold):
        c_int_list = img_share_decryption_list[img_index]
        c_bytes_list = []
        for c_int in c_int_list:
            c_int_temp = int(c_int)
            c_bytes = c_int_temp.to_bytes(bytes_per_c, byteorder='big')
            if len(c_bytes) < bytes_per_c:
                c_bytes = b'\x00' * (bytes_per_c - len(c_bytes)) + c_bytes
            c_bytes_list.append(c_bytes)
        byte_array = np.concatenate([np.frombuffer(c_bytes, dtype=np.uint8) for c_bytes in c_bytes_list])
        reshaped_image = byte_array.reshape(h_cbytes, w_cbytes)
        cv.imwrite(filename + '_share_dec_' + str(img_index) + '.png', reshaped_image)
    ################################## Finish saving threshold decryption results as ciphertext images

    end_time = time.time()
    print(f"All Distributed Receiver-PartialDec: {end_time - start_time} s")
    #----------Partial decryption completed.

    # --------- Next, execute combining decryption.
    img_dec = []
    img_dec2 = []
    start_time = time.time()
    for i in range(h * w):
        c_list = []
        for img_index in range(threshold):  # normal combining decryption
        # for img_index in range(threshold-1): #Simulate malicious adversary to generate noise image, threshold=5
            c_list.append(img_share_decryption_list[img_index, i]) # Add partial decryption results of threshold shares to list
        # Simulate malicious adversary to generate one pixel in noise image
        # c_list.append(img_share_decryption_list[img_index,i])
        # Simulation done
        # Normal shares
        # for img_index in range(threshold): #Simulate malicious adversaries to generate noisy images.
        #     c_list.append(img_share_decryption_list[img_index,i])
        # Combining decryption of legitimate shares has finished.
        m_rec = private_key_ring.combiningDecrypt(c_list)  # Decrypted to extended plaintext (range: entire plaintext space)
        img_dec2.append(m_rec)
    end_time = time.time()
    print(f"Receiver-ComDec: {end_time - start_time} s")
    # --------Combining decryption done.

    ##-------Extract ma & recover plaintext image:
    # last pixel=embedding rate (Ve), others=data (VE)
    #----- Extract ma
    start_time = time.time()
    ma_ext = []
    ##Process last pixel first
    ia_last = img_dec2[h * w - 1]
    ve_len_ext = ia_last % 2 ** 12  # Data extracted in last pixel
    assert np.array_equal(ve_len, ve_len_ext)  # Compare embedded info in last pixel with extracted one (check consistency)
    for i in range(h * w - 1):
        ia = img_dec2[i]
        ma_value_ext = ia % 2 ** ve_len_ext
        ma_value_ext = bin(ma_value_ext)[2:].zfill(ve_len)
        ma_ext.append(ma_value_ext)
    ma_ext = np.array(list(''.join(ma_ext)), dtype=int)
    assert np.array_equal(ma, ma_ext)  # Compare embedded valid info ma with extracted one (check consistency)
    end_time = time.time()
    print(f"Receiver-Ext2: {end_time - start_time} s")
    #----- Extraction done

    #----- Recover image
    start_time = time.time()
    img_reconstructed = []
    m_ext_last = ia_last // 2 ** 12  # Recover last pixel first
    #Then recover other pixels
    for i in range(h * w - 1):
        ia = img_dec2[i]
        m_ext = ia // 2 ** ve_len_ext
        img_reconstructed.append(m_ext)
    img_reconstructed.append(m_ext_last)
    end_time = time.time()
    print(f"Receiver-Res: {end_time - start_time} s")
    #----- Recovery done


if __name__ == '__main__':
    main()
