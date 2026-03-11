import unittest

from app.domain.case import Case, CaseStatus
from app.domain.errors import InvalidStateTransition


class CaseDomainTests(unittest.TestCase):
    def test_create_normalizes_measure_type_and_sets_open_status(self):
        case = Case.create(
            member_id="member-123",
            measure_type=" statin ",
            year=2026,
            current_pdc=0.72,
        )

        self.assertEqual(case.member_id, "member-123")
        self.assertEqual(case.measure_type, "STATIN")
        self.assertEqual(case.status, CaseStatus.OPEN)

    def test_archive_requires_closed_status(self):
        case = Case.create(
            member_id="member-123",
            measure_type="statin",
            year=2026,
            current_pdc=0.72,
        )

        with self.assertRaises(InvalidStateTransition):
            case.archive()
