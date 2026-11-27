import json
import os
import tempfile
from contextlib import nullcontext
from datetime import timedelta
from threading import Event
from unittest.mock import patch

from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase
from django.utils import timezone

from dashboard import views
from dashboard.Night_Execution import views as night_views
from dashboard.Region_CRs import views as region_views
from dashboard.forms import PasswordAuthForm, TwoFactorAuthForm
from dashboard.middleware import SessionIdleTimeoutMiddleware
from dashboard.task_modules.dependencies import playwright_common_methods_ as pcm
from dashboard.utils.niam_region import region_from_node_text
from dashboard.utils.selected_regions import (
    effective_regions,
    get_selected_regions,
    region_is_selected,
    set_selected_regions,
)
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


class SelectedRegionTests(SimpleTestCase):
    """Persistent selection is a session fact, not a lock or browser cache."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(id=9101, is_authenticated=True)

    def _request(self, method, data=None, content_type=None):
        request = self.factory.generic(
            method, "/api/region-selection/", data=data, content_type=content_type
        )
        request.user = self.user
        request.session = {"selected_regions": ["north"]}
        return request

    def test_post_replaces_exact_selection(self):
        request = self._request(
            "POST",
            data=json.dumps({"regions": ["west", "east", "invalid"]}),
            content_type="application/json",
        )

        response = views.region_selection(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)["regions"], ["west", "east"]
        )
        self.assertEqual(request.session["selected_regions"], ["west", "east"])

    def test_unchecking_every_region_clears_selection(self):
        request = self._request(
            "POST",
            data=json.dumps({"regions": []}),
            content_type="application/json",
        )

        views.region_selection(request)

        self.assertEqual(request.session["selected_regions"], [])

    def test_effective_regions_cannot_be_widened_by_query_string(self):
        request = self._request("GET")
        set_selected_regions(request, ["north", "west"])

        self.assertEqual(
            effective_regions(request, "north,south"), ["north"]
        )
        self.assertEqual(get_selected_regions(request), ["north", "west"])
        self.assertTrue(region_is_selected(request, "west"))
        self.assertFalse(region_is_selected(request, "south"))

    def test_idle_timeout_clears_locks_and_flushes_session(self):
        request = self.factory.get("/cr-planning/")
        request.user = SimpleNamespace(id=9102, is_authenticated=True)
        request.session = {
            "last_activity": (
                timezone.now() - timedelta(hours=2)
            ).isoformat(),
            "selected_regions": ["north"],
        }
        middleware = SessionIdleTimeoutMiddleware(lambda req: None)

        def fake_logout(req):
            req.user = SimpleNamespace(is_authenticated=False)
            req.session = {}

        with patch("dashboard.middleware.logout", side_effect=fake_logout), \
                patch("dashboard.middleware.RUN_REGISTRY.clear_all_for_user") as clear, \
                patch("dashboard.models.RegionLock") as lock_model:
            middleware(request)

        clear.assert_called_once_with(9102)
        lock_model.objects.using.assert_called_once_with("default")
        lock_model.objects.using.return_value.filter.return_value.delete\
            .assert_called_once_with()
        self.assertEqual(request.session, {})
        self.assertFalse(request.user.is_authenticated)


class NiamRegionDerivationTests(SimpleTestCase):
    def test_node_prefixes_map_to_expected_regions(self):
        self.assertEqual(region_from_node_text("MAH/MHNA2/MUM/MUC"), "west")
        self.assertEqual(region_from_node_text("AP/TNS/KER/KK/CH"), "south")
        self.assertEqual(region_from_node_text("WB/KO/NE"), "east")
        self.assertEqual(region_from_node_text("UWN/UPW/UPE/DL/GGN"), "north")

    def test_mixed_or_unknown_nodes_are_not_guessed(self):
        self.assertEqual(region_from_node_text("MAH/KOL"), "")
        self.assertEqual(region_from_node_text("UNKNOWN-123"), "")

    def test_cr_region_is_used_when_node_text_is_missing(self):
        row = SimpleNamespace(
            node_details="", node_name="", sr_or_change_number="CR0001"
        )
        with patch("dashboard.models.MasterCRDatabase") as master, \
                patch("dashboard.models.SelectedDateTable"):
            master.objects.using.return_value.filter.return_value\
                .values_list.return_value.first.return_value = "North"

            from dashboard.utils.niam_region import region_for_niam_row

            self.assertEqual(region_for_niam_row(row), "north")


class RegionReadOnlyEnforcementTests(SimpleTestCase):
    """Server-side gates reject edits even if the browser is bypassed."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(id=9201, is_authenticated=True)

    def test_region_cr_save_rejects_unselected_row(self):
        request = self.factory.post(
            "/region-crs/save/",
            data=json.dumps({
                "changes": [{"id": 7, "fields": {"activity_status": "Completed"}}]
            }),
            content_type="application/json",
        )
        request.user = self.user
        request.session = {"selected_regions": ["north"]}
        active_row = SimpleNamespace(pk=7, region="east")

        with patch.object(region_views, "_user_can_edit_region_crs", return_value=True), \
                patch.object(region_views.transaction, "atomic", return_value=nullcontext()), \
                patch.object(region_views.MasterCRDatabase, "objects") as objects:
            objects.using.return_value.select_for_update.return_value\
                .filter.return_value.first.return_value = active_row
            response = region_views.save_region_cr_details(request)

        body = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(body["ok"])
        self.assertIn("unselected region", body["errors"][0]["message"])

    def test_niam_save_rejects_unselected_row(self):
        request = self.factory.post(
            "/niam/save/",
            data=json.dumps({
                "date": "2026-11-27",
                "rows": [{"id": 12, "access_type": "READWRITE"}],
            }),
            content_type="application/json",
        )
        request.user = self.user
        request.session = {"selected_regions": ["north"]}

        with patch(
            "dashboard.Region_CRs.views._user_can_edit_region_crs",
            return_value=True,
        ), patch(
            "dashboard.task_modules.dependencies.extra_dependencies.niam_dropdown_options",
            return_value={},
        ), patch(
            "dashboard.views.region_for_niam_row", return_value="east"
        ), patch("dashboard.models.NIAMTicketGenerationTable.objects") as objects:
            objects.filter.return_value = [
                SimpleNamespace(pk=12, sr_or_change_number="CR0001", node_name="N1")
            ]
            response = views.save_niam_template_changes(request)

        body = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(body["ok"])
        self.assertIn("unselected region", body["errors"][0]["message"])
