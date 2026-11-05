"""
Zone registry for Pramana Mode 3 Smart Gate.

Zones are product configuration, not legal sources. Every zone must reference
existing, retrieval-eligible, verbatim corpus chunks. Historical references are
kept separate and must point to chunks that are explicitly marked as
superseded.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional

from backend.services.corpus_loader import CorpusManager

ZONES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus",
    "zones.json",
)

SUPPORTED_LANGUAGES = ("id", "en")
ZONE_CATEGORIES = {"entry_point", "temple", "public_area"}
ZONE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ZoneNotFoundError(LookupError):
    """Raised when a zone ID is not present in the registry."""


class ZoneRegistry:
    _instance: Optional["ZoneRegistry"] = None

    def __init__(
        self,
        file_path: str = ZONES_PATH,
        corpus_mgr: Optional[CorpusManager] = None,
    ):
        self.file_path = file_path
        self.corpus_mgr = corpus_mgr or CorpusManager.get_instance()
        self.metadata: Dict[str, Any] = {}
        self.zones: List[Dict[str, Any]] = []
        self._index: Dict[str, Dict[str, Any]] = {}
        self.load()

    @classmethod
    def get_instance(cls) -> "ZoneRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Zone registry not found at: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)

        self._validate(data)
        self.metadata = data.get("metadata", {})
        self.zones = data["zones"]
        self._index = {zone["id"]: zone for zone in self.zones}

    def _validate(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Zone registry root must be a JSON object.")

        zones = data.get("zones")
        metadata = data.get("metadata")
        if not isinstance(metadata, dict) or not metadata:
            raise ValueError("Zone registry must contain non-empty 'metadata'.")
        if not isinstance(zones, list) or not zones:
            raise ValueError("Zone registry must contain a non-empty 'zones' list.")

        seen_ids = set()
        for index, zone in enumerate(zones):
            if not isinstance(zone, dict):
                raise ValueError(f"Zone at index {index} must be a JSON object.")

            zone_id = zone.get("id")
            if not isinstance(zone_id, str) or not ZONE_ID_PATTERN.match(zone_id):
                raise ValueError(f"Zone at index {index} has an invalid id.")
            if zone_id in seen_ids:
                raise ValueError(f"Duplicate zone id: {zone_id}")
            seen_ids.add(zone_id)

            self._validate_localized(zone_id, zone, "name")
            self._validate_localized(zone_id, zone, "location_note")
            self._validate_localized(zone_id, zone, "scope_note")

            if zone.get("category") not in ZONE_CATEGORIES:
                raise ValueError(
                    f"Zone '{zone_id}' has unknown category "
                    f"'{zone.get('category')}'."
                )

            checks = zone.get("practical_checks")
            if not isinstance(checks, list) or not checks:
                raise ValueError(
                    f"Zone '{zone_id}' must have a non-empty "
                    "'practical_checks' list."
                )
            for check_index, check in enumerate(checks):
                if not isinstance(check, dict):
                    raise ValueError(
                        f"Zone '{zone_id}' check {check_index} must be an object."
                    )
                self._validate_localized_values(
                    zone_id,
                    f"practical_checks[{check_index}]",
                    check,
                )

            current_ids = zone.get("regulation_ids")
            if not isinstance(current_ids, list) or not current_ids:
                raise ValueError(
                    f"Zone '{zone_id}' must have a non-empty 'regulation_ids' list."
                )
            self._validate_regulation_ids(
                zone_id, current_ids, role="current", require_verbatim=True
            )

            historical_ids = zone.get("historical_regulation_ids", [])
            if not isinstance(historical_ids, list):
                raise ValueError(
                    f"Zone '{zone_id}' must have a "
                    "'historical_regulation_ids' list."
                )
            self._validate_regulation_ids(
                zone_id, historical_ids, role="historical", require_verbatim=False
            )
            if set(current_ids) & set(historical_ids):
                raise ValueError(
                    f"Zone '{zone_id}' lists the same chunk as current and "
                    "historical."
                )

            for field in ("rules_version", "last_verified_date"):
                value = zone.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(
                        f"Zone '{zone_id}' must have a non-empty '{field}'."
                    )

    @staticmethod
    def _validate_localized(
        zone_id: str, container: Dict[str, Any], field: str
    ) -> None:
        ZoneRegistry._validate_localized_values(
            zone_id,
            f"field '{field}'",
            container.get(field),
        )

    @staticmethod
    def _validate_localized_values(
        zone_id: str, label: str, value: Any
    ) -> None:
        if not isinstance(value, dict):
            raise ValueError(
                f"Zone '{zone_id}' {label} must be a localized object."
            )
        for language in SUPPORTED_LANGUAGES:
            text = value.get(language)
            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"Zone '{zone_id}' {label} is missing '{language}'."
                )

    def _validate_regulation_ids(
        self,
        zone_id: str,
        regulation_ids: List[Any],
        role: str,
        require_verbatim: bool,
    ) -> None:
        seen = set()
        for reg_id in regulation_ids:
            if not isinstance(reg_id, str) or not reg_id.strip():
                raise ValueError(
                    f"Zone '{zone_id}' has an invalid {role} regulation id."
                )
            if reg_id in seen:
                raise ValueError(
                    f"Zone '{zone_id}' lists duplicate {role} chunk '{reg_id}'."
                )
            seen.add(reg_id)

            reg = self.corpus_mgr.get_by_id(reg_id)
            if not reg:
                raise ValueError(
                    f"Zone '{zone_id}' references unknown {role} chunk "
                    f"'{reg_id}'."
                )

            document = self.corpus_mgr.get_document_for_regulation(reg_id)
            if not document or not document.get("retrieval_eligible"):
                raise ValueError(
                    f"Zone '{zone_id}' references non-retrievable {role} chunk "
                    f"'{reg_id}'."
                )

            if require_verbatim and not reg.get("is_verbatim"):
                raise ValueError(
                    f"Zone '{zone_id}' requires verbatim {role} chunk, but "
                    f"'{reg_id}' has text_status '{reg.get('text_status')}'."
                )

            if role == "historical":
                if not reg.get("superseded_by") and reg.get("status") != (
                    "Disempurnakan"
                ):
                    raise ValueError(
                        f"Zone '{zone_id}' historical chunk '{reg_id}' is not "
                        "marked as superseded."
                    )

    def get_all(self) -> List[Dict[str, Any]]:
        return self.zones

    def get_zone(self, zone_id: str) -> Optional[Dict[str, Any]]:
        if not zone_id:
            return None
        return self._index.get(zone_id)

    def get_zone_or_raise(self, zone_id: str) -> Dict[str, Any]:
        zone = self.get_zone(zone_id)
        if not zone:
            raise ZoneNotFoundError(f"Zona '{zone_id}' tidak ditemukan.")
        return zone
