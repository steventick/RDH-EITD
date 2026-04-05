# Attribution & Modifications

This directory contains a modified version of the **damgard-jurik** homomorphic encryption library.

**Original Source & License**
*   **Project:** damgard-jurik
*   **Copyright:** (c) 2019 Nicholas Boucher, Luka Govedič, Pasapol Saowakon, Kyle Swanson
*   **License:** A permissive license. The **full original license text** must be preserved and is available in [`dj_mod/LICENSE`](dj_mod/LICENSE).

**Summary of Modifications**
We have modified the original library to implement the RDH-EITD scheme described in our paper "*Reversible Data Hiding in Encrypted Images with Dual-Phase Embedding based on Multi-Key Threshold Decryption*".
Key changes include:
*   Modified key generation function in `crypto.py` to ensure n reaches its maximum possible bit length.
*   Added share decryption in `crypto.py`.
*   Added combining decryption in `crypto.py`.

These modifications are released under the terms of the MIT License.