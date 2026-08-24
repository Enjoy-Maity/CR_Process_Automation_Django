import os
from datetime import datetime
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

HOST_DOWNLOAD_DIR = os.getenv(
     "DJANGO_DOWNLOAD_DIR", 
    os.path.join(os.path.abspath(os.sep), "PS-Core-Automation")
)

SECRET_KEY = 'django-insecure-change-me'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dashboard.middleware.CustomExceptionMiddleware',
]

ROOT_URLCONF = 'cr_process_automation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cr_process_automation.wsgi.application'

DATABASES = {
    'default': { # Master Database
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.master.sqlite3',
        'OPTIONS': {
            'timeout' : 60,
            'transaction_mode': 'IMMEDIATE',
            'init_command': "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    },
    'replica' :{
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.replica.sqlite3",
        "OPTIONS": {
            "timeout": 30,
            "init_command": "PRAGMA journal_mode=WAL;",
        },
    }
}

DATABASE_ROUTERS = ['cr_process_automation.routers.CoWRouter',]

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)  # Create if it doesn't exist

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'ERROR',
    },
    'loggers': {
        'dashboard': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'


STATIC_URL = 'static/'
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# LOGIN_URL = '/admin/login/'
# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/admin/login/'

AUTH_USER_MODEL = "dashboard.UserManagement"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "cr_planning"
LOGOUT_REDIRECT_URL = "login"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # Update this URL if your Redis is hosted elsewhere (e.g., AWS ElastiCache)
        "LOCATION": "redis://127.0.0.1:6379/1", 
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Read the path from the environment, fallback to a local 'downloads' folder
HOST_DOWNLOAD_DIR = os.environ.get(
    'DJANGO_DOWNLOAD_DIR', 
    os.path.join(os.path.abspath(os.sep), "Automation", "PS_Core_Automation", "Task_Wise_Automation")
)

CR_WISE_STATUS_FIELDS = [
    "id", "sno", "execution_date", "cr_no", "activity_description", "region", "circle",
    "CR_Hygiene_Checks", "Install_Test_Plan_Downloads",
    "MOP_Attachment", "CR_Approvals", "NIAM_Ticket",
]

SELECTED_DATE_TABLE_FIELDS = [
    "id", "sno", "ms_project", "execution_date", "maintenance_window", "cr_no",
    "priority", "risk", "region", "circle", "activity_description", "node_details", "node_count",
    "bpms_cr_yes_no", "planning_status", "activity_executor",
    "auditor_name", "activity_status", "reason_for_rollback_cancel", "technical_validator",
    "service_affecting", "impact", "test_cases", "kpi_name", "kpi_spoc_night",
    "kpi_spoc_morning", "inter_domain_activity", "inter_domain_kpi_required",
    "inter_domain_measuring_kpis", "activity_type", "vendor", "protocol",
    "execution_type", "cli_availability", "team", "scheduled_start_date",
    "scheduled_end_date", "niam_ticket_required", "niam_node_type", "additional_info",
    # CoW metadata fields for context
    "is_active", "version", "parent_reference_id",
]


PLANNING_SHEET_COLUMNS = [
    "S.No.", "MS/Project", "Execution Date", "Maintainence Window", "CR No", "Priority", "Risk", "Region", 
    "Circle", "Node Details", "Node Count", "Activity Description", "BPMS CR (Yes/No)", "Planning Status", 
    "Activity Executor", "Auditor Name", "Activity Status", "Reason For Rollback/Cancel", "Technical Validator", 
    "Service Affecting", "Impact", "Test Cases", "KPI Name", "KPI SPOC (Night)", "KPI SPOC (Morning)", "Inter-Domain Activity", 
    "Inter-Domain KPI Required", "Inter-Domain Measuring KPIs", "Activity Type",	"Vendor", "Protocol", "Execution Type", 
    "CLI Availability", "Team",	"Scheduled Start Date+", "Scheduled End Date+", "NIAM Ticket Required (Yes/No)", 
    "NIAM Node Type", "Additional Info"
]


PL_TO_DB_COLUMNS_MAPPING = {
        "S.No.": "sno", "MS/Project": "ms_project", "Execution Date": "execution_date",
        "Maintainence Window": "maintenance_window", "CR No": "cr_no", "Priority": "priority",
        "Risk": "risk", "Region": "region", "Circle": "circle", "Node Details": "node_details",
        "Node Count": "node_count", "Activity Description": "activity_description",
        "BPMS CR (Yes/No)": "bpms_cr_yes_no", "Planning Status": "planning_status",
        "Activity Executor": "activity_executor", "Auditor Name": "auditor_name",
        "Activity Status": "activity_status", "Reason For Rollback/Cancel": "reason_for_rollback_cancel",
        "Technical Validator": "technical_validator", "Service Affecting": "service_affecting",
        "Impact": "impact", "Test Cases": "test_cases", "KPI Name": "kpi_name",
        "KPI SPOC (Night)": "kpi_spoc_night", "KPI SPOC (Morning)": "kpi_spoc_morning",
        "Inter-Domain Activity": "inter_domain_activity",
        "Inter-Domain KPI Required": "inter_domain_kpi_required",
        "Inter-Domain Measuring KPIs": "inter_domain_measuring_kpis",
        "Activity Type": "activity_type", "Vendor": "vendor", "Protocol": "protocol",
        "Execution Type": "execution_type", "CLI Availability": "cli_availability", "Team": "team",
        "Scheduled Start Date+": "scheduled_start_date", "Scheduled End Date+": "scheduled_end_date",
        "NIAM Ticket Required (Yes/No)": "niam_ticket_required", "NIAM Node Type": "niam_node_type",
        "Additional Info": "additional_info",
    }

DB_TO_PL_COLUMNS_MAPPING = {
    value : key for key, value in PL_TO_DB_COLUMNS_MAPPING.items()
}


BMC_REMEDY_IFRAME_MODAL_WATCHER_JS = r"""
(() => {
  if (window.__bmcModalWatcherInstalled) return;
  window.__bmcModalWatcherInstalled = true;

  window.__remedyModalState = {
    handled: false,
    type: null,
    message: null
  };

  function isRemedyModal(el) {
    if (!(el instanceof HTMLElement)) return false;
    const header = el.querySelector('.x-window-header, .x-window-header-text');
    const buttons = el.querySelectorAll('button');
    return header && buttons.length > 0;
  }

  function txt(el) {
    return (el.innerText || el.value || '').toLowerCase();
  }

  function record(type, message) {
    window.__remedyModalState.handled = true;
    window.__remedyModalState.type = type;
    window.__remedyModalState.message = message.slice(0, 300);
  }

  function handle(modal) {
    const text = txt(modal);

    // Confirm Save Request → YES
    if (
      text.includes("confirm save request") ||
      text.includes("do you want to save the current request")
    ) {
      //const yesBtn = [...modal.querySelectorAll('button')]
      //  .find(b => txt(b).includes('yes'));
      //if (yesBtn) {
      //  yesBtn.click();
      //  record("confirm_save", text);
      //  return;

      const noBtn = [...modal.querySelectorAll('button')]
        .find(b => txt(b).includes('no'));
      if (noBtn) {
        noBtn.click();
        record("confirm_save", text);
        return;
      }
    }

    // All other Remedy popups → OK
    const okBtn = [...modal.querySelectorAll('button')]
      .find(b => txt(b).includes('ok'));
    if (okBtn) {
      okBtn.click();
      record("error_or_info", text);
    }
  }

  const observer = new MutationObserver(muts => {
    for (const m of muts) {
      for (const n of m.addedNodes) {
        if (isRemedyModal(n)) handle(n);
      }
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();
"""


