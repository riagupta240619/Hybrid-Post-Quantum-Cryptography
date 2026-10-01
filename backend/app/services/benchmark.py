from __future__ import annotations

import os
import statistics
import time
from dataclasses import dataclass
from typing import Callable
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pqcrypto.kem.ml_kem_768 import decaps, encaps, keygen as kem_keygen
from pqcrypto.sign.ml_dsa_65 import keygen as sig_keygen, sign, verify

@dataclass
class BenchResult:
    mode: str
    iterations: int
    payload_bytes: int
    keygen_ms: float
    encapsulation_ms: float
    encryption_ms: float
    signing_ms: float
    verification_ms: float
    decapsulation_ms: float
    decryption_ms: float
    total_ms: float
    package_bytes: int

class BenchmarkService:
    def _measure(self, fn: Callable[[], object], n: int) -> tuple[float, object]:
        samples=[]; last=None
        for _ in range(n):
            start=time.perf_counter_ns(); last=fn(); samples.append((time.perf_counter_ns()-start)/1e6)
        return statistics.median(samples), last

    @staticmethod
    def _hkdf(a: bytes, b: bytes, info: bytes) -> bytes:
        return HKDF(algorithm=hashes.SHA384(), length=32, salt=None, info=info).derive(a+b)

    def run(self, iterations: int, payload_bytes: int) -> list[BenchResult]:
        payload=os.urandom(payload_bytes)
        return [self._run_classical(iterations,payload), self._run_pqc(iterations,payload), self._run_hybrid(iterations,payload)]

    def _run_classical(self,n:int,payload:bytes)->BenchResult:
        keygen,_=self._measure(lambda:(X25519PrivateKey.generate(),Ed25519PrivateKey.generate()),n)
        recipient_x=X25519PrivateKey.generate(); recipient_ep=recipient_x.public_key(); signer=Ed25519PrivateKey.generate(); signer_pub=signer.public_key()
        enc_times=[]; aes_times=[]; sig_times=[]; verify_times=[]; decap_times=[]; dec_times=[]; package_bytes=0
        for _ in range(n):
            t=time.perf_counter_ns(); eph=X25519PrivateKey.generate(); shared=eph.exchange(recipient_ep); enc_times.append((time.perf_counter_ns()-t)/1e6)
            key=self._hkdf(shared,b"",b"PQShield classical benchmark")
            nonce=os.urandom(12); t=time.perf_counter_ns(); ct=AESGCM(key).encrypt(nonce,payload,b""); aes_times.append((time.perf_counter_ns()-t)/1e6)
            signed=nonce+ct; t=time.perf_counter_ns(); sig=signer.sign(signed); sig_times.append((time.perf_counter_ns()-t)/1e6); package_bytes=len(signed)+len(sig)
            t=time.perf_counter_ns(); Ed25519PublicKey.from_public_bytes(signer_pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).verify(sig,signed); verify_times.append((time.perf_counter_ns()-t)/1e6)
            t=time.perf_counter_ns(); eph_shared=recipient_x.exchange(eph.public_key()); decap_times.append((time.perf_counter_ns()-t)/1e6)
            key2=self._hkdf(eph_shared,b"",b"PQShield classical benchmark"); t=time.perf_counter_ns(); AESGCM(key2).decrypt(nonce,ct,b""); dec_times.append((time.perf_counter_ns()-t)/1e6)
        total=statistics.median([a+b+c+d+e+f for a,b,c,d,e,f in zip(enc_times,aes_times,sig_times,verify_times,decap_times,dec_times)])
        return BenchResult("classical",n,len(payload),keygen,statistics.median(enc_times),statistics.median(aes_times),statistics.median(sig_times),statistics.median(verify_times),statistics.median(decap_times),statistics.median(dec_times),total,package_bytes)

    def _run_pqc(self,n:int,payload:bytes)->BenchResult:
        keygen,_=self._measure(lambda:(kem_keygen(),sig_keygen()),n)
        kem_pub,kem_priv=kem_keygen(); sig_pub,sig_priv=sig_keygen(); enc_times=[]; aes_times=[]; sig_times=[]; verify_times=[]; decap_times=[]; dec_times=[]; package_bytes=0
        for _ in range(n):
            t=time.perf_counter_ns(); ct_kem,shared=encaps(kem_pub); enc_times.append((time.perf_counter_ns()-t)/1e6)
            nonce=os.urandom(12); t=time.perf_counter_ns(); ct=AESGCM(shared).encrypt(nonce,payload,b""); aes_times.append((time.perf_counter_ns()-t)/1e6)
            signed=ct_kem+nonce+ct; t=time.perf_counter_ns(); sig=sign(sig_priv,signed); sig_times.append((time.perf_counter_ns()-t)/1e6); package_bytes=len(signed)+len(sig)
            t=time.perf_counter_ns(); verify(sig_pub,signed,sig); verify_times.append((time.perf_counter_ns()-t)/1e6)
            t=time.perf_counter_ns(); shared2=decaps(kem_priv,ct_kem); decap_times.append((time.perf_counter_ns()-t)/1e6)
            t=time.perf_counter_ns(); AESGCM(shared2).decrypt(nonce,ct,b""); dec_times.append((time.perf_counter_ns()-t)/1e6)
        total=statistics.median([a+b+c+d+e+f for a,b,c,d,e,f in zip(enc_times,aes_times,sig_times,verify_times,decap_times,dec_times)])
        return BenchResult("pqc",n,len(payload),keygen,statistics.median(enc_times),statistics.median(aes_times),statistics.median(sig_times),statistics.median(verify_times),statistics.median(decap_times),statistics.median(dec_times),total,package_bytes)

    def _run_hybrid(self,n:int,payload:bytes)->BenchResult:
        keygen,_=self._measure(lambda:(X25519PrivateKey.generate(),kem_keygen(),sig_keygen()),n)
        recipient_x=X25519PrivateKey.generate(); recipient_ep=recipient_x.public_key(); kem_pub,kem_priv=kem_keygen(); sig_pub,sig_priv=sig_keygen(); enc_times=[]; aes_times=[]; sig_times=[]; verify_times=[]; decap_times=[]; dec_times=[]; package_bytes=0
        for _ in range(n):
            eph=X25519PrivateKey.generate(); t=time.perf_counter_ns(); shared_x=eph.exchange(recipient_ep); ct_kem,shared_pq=encaps(kem_pub); enc_times.append((time.perf_counter_ns()-t)/1e6)
            key=self._hkdf(shared_x,shared_pq,b"PQShield hybrid key combiner v1"); nonce=os.urandom(12); t=time.perf_counter_ns(); ct=AESGCM(key).encrypt(nonce,payload,b""); aes_times.append((time.perf_counter_ns()-t)/1e6)
            signed=eph.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)+ct_kem+nonce+ct; t=time.perf_counter_ns(); sig=sign(sig_priv,signed); sig_times.append((time.perf_counter_ns()-t)/1e6); package_bytes=len(signed)+len(sig)
            t=time.perf_counter_ns(); verify(sig_pub,signed,sig); verify_times.append((time.perf_counter_ns()-t)/1e6)
            t=time.perf_counter_ns(); shared_x2=recipient_x.exchange(X25519PublicKey.from_public_bytes(eph.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw))); shared_pq2=decaps(kem_priv,ct_kem); decap_times.append((time.perf_counter_ns()-t)/1e6)
            key2=self._hkdf(shared_x2,shared_pq2,b"PQShield hybrid key combiner v1"); t=time.perf_counter_ns(); AESGCM(key2).decrypt(nonce,ct,b""); dec_times.append((time.perf_counter_ns()-t)/1e6)
        total=statistics.median([a+b+c+d+e+f for a,b,c,d,e,f in zip(enc_times,aes_times,sig_times,verify_times,decap_times,dec_times)])
        return BenchResult("hybrid",n,len(payload),keygen,statistics.median(enc_times),statistics.median(aes_times),statistics.median(sig_times),statistics.median(verify_times),statistics.median(decap_times),statistics.median(dec_times),total,package_bytes)
