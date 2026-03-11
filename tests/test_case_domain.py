import unittest
from uuid import uuid4

from app.domain.case import Case, CaseStatus
from app.domain.errors import InvalidStateTransition


class CaseDomainTests(unittest.TestCase):
    def test_create_sets_open_status_and_case_metadata(self):
        case = Case.create(
            member_id=uuid4(),
            referral_id=uuid4(),
            case_summary="Needs adherence outreach",
            priority="high",
        )

        self.assertEqual(case.status, CaseStatus.OPEN)
        self.assertIsNotNone(case.opened_at)
        self.assertEqual(case.case_summary, "Needs adherence outreach")
        self.assertEqual(case.priority, "high")

    def test_archive_requires_closed_status(self):
        case = Case.create(
            member_id=uuid4(),
            referral_id=uuid4(),
        )

        with self.assertRaises(InvalidStateTransition):
            case.archive()

    def test_close_sets_closed_reason(self):
        case = Case.create(
            member_id=uuid4(),
            referral_id=uuid4(),
        )
        case.start()
        case.close(closed_reason="Rescued")

        self.assertEqual(case.status, CaseStatus.CLOSED)
        self.assertEqual(case.closed_reason, "Rescued")
