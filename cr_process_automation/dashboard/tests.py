import json
import os
import tempfile
from threading import Event
from unittest.mock import patch

from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase

from dashboard import views
from dashboard.Night_Execution import views as night_views
from dashboard.forms import PasswordAuthForm, TwoFactorAuthForm
from dashboard.task_modules.dependencies import playwright_common_methods_ as pcm
from dashboard.utils.task_runtime import RUN_REGISTRY


class AuthRoutingTests(SimpleTestCase):
    """Regression tests for concurrent ITSM password/OTP handling."""

    def tearDown(self):
        RUN_REGISTRY.clear("auth-test-user-1", 991)
        RUN_REGISTRY.clear("auth-test-user-2", 991)

    def test_run_key_routes_submission_to_exact_run(self):
        first = RUN_REGISTRY.begin("auth-test-user-1", 991)
        second = RUN_REGISTRY.begin("auth-test-user-2", 991)

        self.assertIs(
            RUN_REGISTRY.get("auth-test-user-1", 991, first["run_key"]), first
        )
        self.assertIsNone(
            RUN_REGISTRY.get("auth-test-user-1", 991, second["run_key"])
        )
        self.assertIsNone(
            RUN_REGISTRY.get("auth-test-user-2", 991, first["run_key"])
        )

    def test_each_run_gets_its_own_events(self):
        first = RUN_REGISTRY.begin("auth-test-user-1", 991)
        second = RUN_REGISTRY.begin("auth-test-user-1", 991)

        self.assertNotEqual(first["run_key"], second["run_key"])
        self.assertIsNot(first["pwd_event"], second["pwd_event"])
        self.assertIsNot(first["otp_event"], second["otp_event"])

    def test_auth_forms_require_run_key(self):
        self.assertFalse(TwoFactorAuthForm({
            "task_id": "1", "two_factor_code": "123456"
        }).is_valid())
        self.assertTrue(TwoFactorAuthForm({
            "task_id": "1", "two_factor_code": "123456", "run_key": "abc"
        }).is_valid())
        self.assertFalse(PasswordAuthForm({
            "task_id": "1", "password": "secret"
        }).is_valid())

    def test_itsm_session_file_is_scoped_to_run_key(self):
        with tempfile.TemporaryDirectory() as root:
            legacy = os.path.join(root, "itsm_session_file.json")
            with patch.dict(
                os.environ,
                {"PROJECT_ROOT": root, "ITSM_SESSION_FILE": legacy},
            ):
                self.assertEqual(pcm.get_itsm_session_file_path({}), legacy)
                self.assertEqual(
                    pcm.get_itsm_session_file_path("abc-123"),
                    os.path.join(root, "itsm_session_abc-123.json"),
                )
                self.assertEqual(
                    pcm.get_itsm_session_file_path({"run_key": "bad/key!123"}),
                    os.path.join(root, "itsm_session_badkey123.json"),
                )


class ConcurrentAuthSubmissionTests(SimpleTestCase):
    """Two simultaneous users must never cross-submit password/OTP secrets."""

    TASK_ID = 1
    FIRST_USER_ID = 9911
    SECOND_USER_ID = 9912

    def setUp(self):
        self.factory = RequestFactory()
        self.first_run = RUN_REGISTRY.begin(self.FIRST_USER_ID, self.TASK_ID)
        self.second_run = RUN_REGISTRY.begin(self.SECOND_USER_ID, self.TASK_ID)
        for runtime in (self.first_run, self.second_run):
            runtime["otp_required"] = True
            runtime["password_required"] = True

    def tearDown(self):
        RUN_REGISTRY.clear(self.FIRST_USER_ID, self.TASK_ID)
        RUN_REGISTRY.clear(self.SECOND_USER_ID, self.TASK_ID)

    def _post(self, view, user_id, path, data):
        request = self.factory.post(path, data)
        request.user = SimpleNamespace(id=user_id, is_authenticated=True)
        return view(request, self.TASK_ID)

    def test_two_users_can_submit_their_own_otp(self):
        path = f"/api/task/submit-otp/{self.TASK_ID}/"
        first = self._post(views.submit_otp, self.FIRST_USER_ID, path, {
            "otp": "111111", "run_key": self.first_run["run_key"]
        })
        second = self._post(views.submit_otp, self.SECOND_USER_ID, path, {
            "otp": "222222", "run_key": self.second_run["run_key"]
        })

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(self.first_run["otp"], "111111")
        self.assertEqual(self.second_run["otp"], "222222")
        self.assertTrue(self.first_run["otp_event"].is_set())
        self.assertTrue(self.second_run["otp_event"].is_set())

    def test_two_users_can_submit_their_own_password(self):
        path = f"/api/task/submit-password/{self.TASK_ID}/"
        first = self._post(views.submit_password, self.FIRST_USER_ID, path, {
            "password": "first-secret", "run_key": self.first_run["run_key"]
        })
        second = self._post(views.submit_password, self.SECOND_USER_ID, path, {
            "password": "second-secret", "run_key": self.second_run["run_key"]
        })

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(self.first_run["password"], "first-secret")
        self.assertEqual(self.second_run["password"], "second-secret")
        self.assertTrue(self.first_run["pwd_event"].is_set())
        self.assertTrue(self.second_run["pwd_event"].is_set())

    def test_other_users_run_key_is_rejected(self):
        path = f"/api/task/submit-otp/{self.TASK_ID}/"
        response = self._post(views.submit_otp, self.FIRST_USER_ID, path, {
            "otp": "333333", "run_key": self.second_run["run_key"]
        })

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(self.first_run["otp"])
        self.assertFalse(self.first_run["otp_event"].is_set())


class NightAuthOwnershipTests(SimpleTestCase):
    """Night Execution auth jobs must only be changed by their owner."""

    JOB_ID = "night-auth-test-job"

    def setUp(self):
        self.runtime = {
            "run_key": self.JOB_ID,
            "user_id": 8001,
            "otp_required": True,
            "otp": None,
            "otp_event": Event(),
        }
        with night_views._JOBS_LOCK:
            night_views._JOBS[self.JOB_ID] = {
                "runtime": self.runtime,
                "logs": [],
                "payload": None,
                "done": False,
            }

    def tearDown(self):
        with night_views._JOBS_LOCK:
            night_views._JOBS.pop(self.JOB_ID, None)

    def test_other_user_cannot_submit_night_otp(self):
        request = RequestFactory().post(
            "/night-execution/submit-otp/",
            data=json.dumps({"job_id": self.JOB_ID, "otp": "123456"}),
            content_type="application/json",
        )
        request.user = SimpleNamespace(id=8002, is_authenticated=True)

        response = night_views.submit_night_otp(request)

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(self.runtime["otp"])
        self.assertFalse(self.runtime["otp_event"].is_set())
