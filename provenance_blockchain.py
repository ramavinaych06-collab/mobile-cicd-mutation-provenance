"""
provenance_blockchain.py
Cryptographic ledger for software provenance tracking in mobile release engineering.
"""

import hashlib
import json
import time
from typing import Any, Dict, List


class ProvenanceBlock:
    def __init__(self, index: int, timestamp: float, release_data: Dict[str, Any], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.release_data = release_data
        self.previous_hash = previous_hash
        self.block_hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "release_data": self.release_data,
            "previous_hash": self.previous_hash,
        }
        encoded = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()


class SoftwareProvenanceBlockchain:
    def __init__(self):
        self.chain: List[ProvenanceBlock] = [self._create_genesis_block()]

    def _create_genesis_block(self) -> ProvenanceBlock:
        return ProvenanceBlock(
            index=0,
            timestamp=time.time(),
            release_data={"genesis": "Mobile CI/CD Software Provenance Root"},
            previous_hash="0" * 64,
        )

    def get_latest_block(self) -> ProvenanceBlock:
        return self.chain[-1]

    def record_release(
        self,
        app_id: str,
        version: str,
        git_commit: str,
        artifact_hash: str,
        mutation_report: Dict[str, Any],
        release_gate_passed: bool,
    ) -> ProvenanceBlock:
        record = {
            "app_id": app_id,
            "version": version,
            "git_commit": git_commit,
            "artifact_sha256": artifact_hash,
            "mutation_score": mutation_report["mutation_score"],
            "mutants_evaluated": mutation_report["total_mutants_evaluated"],
            "release_gate_passed": release_gate_passed,
            "timestamp": time.time(),
        }
        new_block = ProvenanceBlock(
            index=len(self.chain),
            timestamp=time.time(),
            release_data=record,
            previous_hash=self.get_latest_block().block_hash,
        )
        self.chain.append(new_block)
        return new_block

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.block_hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.block_hash:
                return False
        return True
    