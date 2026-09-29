--
-- PostgreSQL database dump
--

\restrict i44dPgArMsOzMp0FiXwysf0qwWCXQkgLMaJs12n8Upehhh1TDC3EXijPHPVMUFE

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.selected_date_table DROP CONSTRAINT IF EXISTS selected_date_table_parent_reference_id_1f12c27e_fk_selected_;
ALTER TABLE IF EXISTS ONLY public.master_cr_database DROP CONSTRAINT IF EXISTS master_cr_database_parent_reference_id_00ca09ec_fk_master_cr;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_dashboard;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_user_permissions DROP CONSTRAINT IF EXISTS dashboard_usermanage_usermanagement_id_b0b733b3_fk_dashboard;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_groups DROP CONSTRAINT IF EXISTS dashboard_usermanage_usermanagement_id_3d81d927_fk_dashboard;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_user_permissions DROP CONSTRAINT IF EXISTS dashboard_usermanage_permission_id_55bf0ab7_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_groups DROP CONSTRAINT IF EXISTS dashboard_usermanage_group_id_bf06518f_fk_auth_grou;
ALTER TABLE IF EXISTS ONLY public.dashboard_taskrun DROP CONSTRAINT IF EXISTS dashboard_taskrun_triggered_by_id_5a8e4505_fk_dashboard;
ALTER TABLE IF EXISTS ONLY public.dashboard_taskrun DROP CONSTRAINT IF EXISTS dashboard_taskrun_task_id_18965367_fk_dashboard;
ALTER TABLE IF EXISTS ONLY public.dashboard_tasklog DROP CONSTRAINT IF EXISTS dashboard_tasklog_run_id_388392fe_fk_dashboard_taskrun_id;
ALTER TABLE IF EXISTS ONLY public.cr_wise_status DROP CONSTRAINT IF EXISTS cr_wise_status_parent_reference_id_90e13541_fk_cr_wise_s;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
DROP INDEX IF EXISTS public.unique_active_selected_table_cr_no;
DROP INDEX IF EXISTS public.unique_active_master_cr_no;
DROP INDEX IF EXISTS public.unique_active_cr_wise_status_no;
DROP INDEX IF EXISTS public.selected_date_table_parent_reference_id_1f12c27e;
DROP INDEX IF EXISTS public.master_cr_database_parent_reference_id_00ca09ec;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.dashboard_usermanagement_username_5ccd2c4b_like;
DROP INDEX IF EXISTS public.dashboard_usermanagement_u_usermanagement_id_b0b733b3;
DROP INDEX IF EXISTS public.dashboard_usermanagement_u_permission_id_55bf0ab7;
DROP INDEX IF EXISTS public.dashboard_usermanagement_groups_usermanagement_id_3d81d927;
DROP INDEX IF EXISTS public.dashboard_usermanagement_groups_group_id_bf06518f;
DROP INDEX IF EXISTS public.dashboard_usermanagement_employee_signum_da849a28_like;
DROP INDEX IF EXISTS public.dashboard_usermanagement_email_93b9650d_like;
DROP INDEX IF EXISTS public.dashboard_taskrun_triggered_by_id_5a8e4505;
DROP INDEX IF EXISTS public.dashboard_taskrun_task_id_18965367;
DROP INDEX IF EXISTS public.dashboard_tasklog_run_id_388392fe;
DROP INDEX IF EXISTS public.dashboard_flagtable_source_id_4ee10c22_like;
DROP INDEX IF EXISTS public.cr_wise_status_parent_reference_id_90e13541;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
ALTER TABLE IF EXISTS ONLY public.selected_date_table DROP CONSTRAINT IF EXISTS selected_date_table_pkey;
ALTER TABLE IF EXISTS ONLY public.master_cr_database DROP CONSTRAINT IF EXISTS master_cr_database_pkey;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement DROP CONSTRAINT IF EXISTS dashboard_usermanagement_username_key;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_user_permissions DROP CONSTRAINT IF EXISTS dashboard_usermanagement_usermanagement_id_permis_0210ac3a_uniq;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_groups DROP CONSTRAINT IF EXISTS dashboard_usermanagement_usermanagement_id_group__bb8ef0b2_uniq;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_user_permissions DROP CONSTRAINT IF EXISTS dashboard_usermanagement_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement DROP CONSTRAINT IF EXISTS dashboard_usermanagement_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement_groups DROP CONSTRAINT IF EXISTS dashboard_usermanagement_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement DROP CONSTRAINT IF EXISTS dashboard_usermanagement_employee_signum_key;
ALTER TABLE IF EXISTS ONLY public.dashboard_usermanagement DROP CONSTRAINT IF EXISTS dashboard_usermanagement_email_key;
ALTER TABLE IF EXISTS ONLY public.dashboard_taskrun DROP CONSTRAINT IF EXISTS dashboard_taskrun_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_tasklog DROP CONSTRAINT IF EXISTS dashboard_tasklog_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_flagtable DROP CONSTRAINT IF EXISTS dashboard_flagtable_source_id_key;
ALTER TABLE IF EXISTS ONLY public.dashboard_flagtable DROP CONSTRAINT IF EXISTS dashboard_flagtable_pkey;
ALTER TABLE IF EXISTS ONLY public.dashboard_automationtask DROP CONSTRAINT IF EXISTS dashboard_automationtask_sequence_no_key;
ALTER TABLE IF EXISTS ONLY public.dashboard_automationtask DROP CONSTRAINT IF EXISTS dashboard_automationtask_pkey;
ALTER TABLE IF EXISTS ONLY public.cr_wise_status DROP CONSTRAINT IF EXISTS cr_wise_status_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
DROP TABLE IF EXISTS public.selected_date_table;
DROP TABLE IF EXISTS public.master_cr_database;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.dashboard_usermanagement_user_permissions;
DROP TABLE IF EXISTS public.dashboard_usermanagement_groups;
DROP TABLE IF EXISTS public.dashboard_usermanagement;
DROP TABLE IF EXISTS public.dashboard_taskrun;
DROP TABLE IF EXISTS public.dashboard_tasklog;
DROP TABLE IF EXISTS public.dashboard_flagtable;
DROP TABLE IF EXISTS public.dashboard_automationtask;
DROP TABLE IF EXISTS public.cr_wise_status;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: cr_wise_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cr_wise_status (
    id bigint NOT NULL,
    sno integer,
    execution_date date,
    maintenance_window character varying(50),
    cr_no character varying(50) NOT NULL,
    risk character varying(100),
    activity_description text,
    bpms_cr_yes_no character varying(10),
    circle character varying(50),
    region character varying(50),
    technical_validator character varying(100),
    "CR_Hygiene_Checks" character varying(100),
    "Install_Test_Plan_Downloads" character varying(100),
    "MOP_Attachment" character varying(100),
    "CR_Approvals" character varying(100),
    "NIAM_Ticket" character varying(100),
    is_active boolean NOT NULL,
    version integer NOT NULL,
    parent_reference_id bigint
);


--
-- Name: cr_wise_status_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.cr_wise_status ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.cr_wise_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_automationtask; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_automationtask (
    id bigint NOT NULL,
    sequence_no integer NOT NULL,
    name character varying(255) NOT NULL,
    upload_required boolean NOT NULL,
    download_required boolean NOT NULL,
    current_status character varying(30) NOT NULL,
    active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT dashboard_automationtask_sequence_no_check CHECK ((sequence_no >= 0))
);


--
-- Name: dashboard_automationtask_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_automationtask ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_automationtask_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_flagtable; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_flagtable (
    id bigint NOT NULL,
    source_id character varying(50) NOT NULL,
    status boolean NOT NULL,
    version integer NOT NULL
);


--
-- Name: dashboard_flagtable_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_flagtable ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_flagtable_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_tasklog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_tasklog (
    id bigint NOT NULL,
    level character varying(20) NOT NULL,
    message text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    run_id bigint NOT NULL
);


--
-- Name: dashboard_tasklog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_tasklog ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_tasklog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_taskrun; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_taskrun (
    id bigint NOT NULL,
    status character varying(30) NOT NULL,
    uploaded_template character varying(100),
    output_file character varying(100),
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone,
    task_id bigint NOT NULL,
    triggered_by_id bigint
);


--
-- Name: dashboard_taskrun_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_taskrun ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_taskrun_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_usermanagement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_usermanagement (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    email character varying(254) NOT NULL,
    employee_name character varying(150),
    employee_signum character varying(100),
    role character varying(20) NOT NULL
);


--
-- Name: dashboard_usermanagement_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_usermanagement_groups (
    id bigint NOT NULL,
    usermanagement_id bigint NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: dashboard_usermanagement_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_usermanagement_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_usermanagement_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_usermanagement_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_usermanagement ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_usermanagement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dashboard_usermanagement_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_usermanagement_user_permissions (
    id bigint NOT NULL,
    usermanagement_id bigint NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: dashboard_usermanagement_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dashboard_usermanagement_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dashboard_usermanagement_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: master_cr_database; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.master_cr_database (
    id bigint NOT NULL,
    sno integer,
    ms_project character varying(100),
    execution_date date,
    maintenance_window character varying(50),
    cr_no character varying(50) NOT NULL,
    priority character varying(50),
    risk character varying(100),
    region character varying(50),
    circle character varying(50),
    node_details text,
    node_count integer,
    activity_description text,
    bpms_cr_yes_no character varying(10),
    planning_status character varying(50),
    activity_executor character varying(100),
    auditor_name character varying(100),
    activity_status character varying(100),
    reason_for_rollback_cancel text,
    technical_validator character varying(100),
    service_affecting character varying(10),
    impact text,
    test_cases text,
    kpi_name text,
    kpi_spoc_night character varying(100),
    kpi_spoc_morning character varying(100),
    inter_domain_activity character varying(10),
    inter_domain_kpi_required character varying(10),
    inter_domain_measuring_kpis text,
    activity_type character varying(200),
    vendor character varying(50),
    protocol character varying(100),
    execution_type character varying(50),
    cli_availability character varying(10),
    team character varying(100),
    scheduled_start_date timestamp with time zone,
    scheduled_end_date timestamp with time zone,
    niam_ticket_required character varying(10),
    niam_node_type character varying(100),
    additional_info text,
    is_active boolean NOT NULL,
    version integer NOT NULL,
    parent_reference_id bigint
);


--
-- Name: master_cr_database_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.master_cr_database ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.master_cr_database_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: selected_date_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.selected_date_table (
    id bigint NOT NULL,
    sno integer,
    ms_project character varying(100),
    execution_date date,
    maintenance_window character varying(50),
    cr_no character varying(50) NOT NULL,
    priority character varying(50),
    risk character varying(100),
    region character varying(50),
    circle character varying(50),
    node_details text,
    node_count integer,
    activity_description text,
    bpms_cr_yes_no character varying(10),
    planning_status character varying(50),
    activity_executor character varying(100),
    auditor_name character varying(100),
    activity_status character varying(100),
    reason_for_rollback_cancel text,
    technical_validator character varying(100),
    service_affecting character varying(10),
    impact text,
    test_cases text,
    kpi_name text,
    kpi_spoc_night character varying(100),
    kpi_spoc_morning character varying(100),
    inter_domain_activity character varying(10),
    inter_domain_kpi_required character varying(10),
    inter_domain_measuring_kpis text,
    activity_type character varying(200),
    vendor character varying(50),
    protocol character varying(100),
    execution_type character varying(50),
    cli_availability character varying(10),
    team character varying(100),
    scheduled_start_date timestamp with time zone,
    scheduled_end_date timestamp with time zone,
    niam_ticket_required character varying(10),
    niam_node_type character varying(100),
    additional_info text,
    is_active boolean NOT NULL,
    version integer NOT NULL,
    parent_reference_id bigint
);


--
-- Name: selected_date_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.selected_date_table ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.selected_date_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add automation task	6	add_automationtask
22	Can change automation task	6	change_automationtask
23	Can delete automation task	6	delete_automationtask
24	Can view automation task	6	view_automationtask
25	Can add flag table	8	add_flagtable
26	Can change flag table	8	change_flagtable
27	Can delete flag table	8	delete_flagtable
28	Can view flag table	8	view_flagtable
29	Can add user	13	add_usermanagement
30	Can change user	13	change_usermanagement
31	Can delete user	13	delete_usermanagement
32	Can view user	13	view_usermanagement
33	Can add task run	12	add_taskrun
34	Can change task run	12	change_taskrun
35	Can delete task run	12	delete_taskrun
36	Can view task run	12	view_taskrun
37	Can add task log	11	add_tasklog
38	Can change task log	11	change_tasklog
39	Can delete task log	11	delete_tasklog
40	Can view task log	11	view_tasklog
41	Can add cr wise status	7	add_crwisestatus
42	Can change cr wise status	7	change_crwisestatus
43	Can delete cr wise status	7	delete_crwisestatus
44	Can view cr wise status	7	view_crwisestatus
45	Can add master cr database	9	add_mastercrdatabase
46	Can change master cr database	9	change_mastercrdatabase
47	Can delete master cr database	9	delete_mastercrdatabase
48	Can view master cr database	9	view_mastercrdatabase
49	Can add selected date table	10	add_selecteddatetable
50	Can change selected date table	10	change_selecteddatetable
51	Can delete selected date table	10	delete_selecteddatetable
52	Can view selected date table	10	view_selecteddatetable
\.


--
-- Data for Name: cr_wise_status; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cr_wise_status (id, sno, execution_date, maintenance_window, cr_no, risk, activity_description, bpms_cr_yes_no, circle, region, technical_validator, "CR_Hygiene_Checks", "Install_Test_Plan_Downloads", "MOP_Attachment", "CR_Approvals", "NIAM_Ticket", is_active, version, parent_reference_id) FROM stdin;
1	1	2026-09-12	00:00:00 - 06:00:00	CRQ000005578508	2-Significant/Large	New Private APN entry in Ericsson DNS (Non-Live) in KOL DNS	No	KO	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
2	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
3	3	2026-09-12	00:00:00 - 06:00:00	CRQ000005576882	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
4	4	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	2-Significant/Large	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes			Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
5	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
6	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
7	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	6
8	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	5
9	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	2
10	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	7
11	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	8
12	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	9
13	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	10
14	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	11
15	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	12
16	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	13
17	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	14
18	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	15
19	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	6	16
20	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	6	17
21	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	6	18
22	6	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	2-Significant/Large	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	UPE	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	7	19
23	5	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	7	20
24	2	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	7	21
25	1	2026-09-15	23:00:00 - 07:00:00	CRQ000005581184	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes		North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
26	2	2026-09-15	23:00:00 - 07:00:00	CRQ000005581091	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes		North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
27	3	2026-09-15	00:00:00 - 06:00:00	CRQ000005580439	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
28	4	2026-09-15	00:00:00 - 06:00:00	CRQ000005580438	1-Extensive/Widespread	M2M APN sugslloyd.iot Gateway Change in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
29	5	2026-09-15	00:00:00 - 06:00:00	CRQ000005580375	2-Significant/Large	M2M-CR for non-live M2M APN(sugslloyd.iot.m2m) DNS entry in DL DNS with Cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
30	6	2026-09-15	23:00:00 - 06:00:00	CRQ000005579815	1-Extensive/Widespread	Traffic diversion from Ericsson MMEs & Revertback for vIPWorks DNS 2.13 Update in APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
31	7	2026-09-15	00:00:00 - 06:00:00	CRQ000005579756	2-Significant/Large	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes			Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
32	8	2026-09-15	00:00:00 - 06:00:00	CRQ000005579521	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in PCCSM	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
33	9	2026-09-15	00:00:00 - 06:00:00	CRQ000005579518	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
34	10	2026-09-15	00:00:00 - 06:00:00	CRQ000005579516	1-Extensive/Widespread	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
35	11	2026-09-15	00:00:00 - 06:00:00	CRQ000005579503	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in PCGUP05, ROBKGPEPG02	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
36	12	2026-09-15	00:00:00 - 06:00:00	CRQ000005579280	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
37	13	2026-09-15	00:00:00 - 06:00:00	CRQ000005579274	2-Significant/Large	IR IMSI definition in Nokia MME	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
38	14	2026-09-15	23:00:00 - 06:00:00	CRQ000005579268	1-Extensive/Widespread	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
39	15	2026-09-15	23:00:00 - 06:00:00	CRQ000005579259	2-Significant/Large	BRM and SP backup for IPWorks version update to 2.13 in AP DNS APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
40	16	2026-09-15	23:00:00 - 07:00:00	CRQ000005579249	1-Extensive/Widespread	CR for PWS & CTUM learning Implementation in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
41	17	2026-09-15	00:00:00 - 06:00:00	CRQ000005579241	1-Extensive/Widespread	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
42	18	2026-09-15	23:00:00 - 07:00:00	CRQ000005579226	1-Extensive/Widespread	RMC value changes and revert back NE E// MMEs for NEGUWRHCC01ERMME02 update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
43	19	2026-09-15	00:00:00 - 06:00:00	CRQ000005579212	1-Extensive/Widespread	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
44	20	2026-09-15	23:00:00 - 07:00:00	CRQ000005579204	1-Extensive/Widespread	CMM gParm modify for traffic offload in Nokia CMMs as part of in UWMORCK02NCMM03	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
45	21	2026-09-15	00:00:00 - 06:00:00	CRQ000005579197	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
46	22	2026-09-15	00:00:00 - 06:00:00	CRQ000005579193	2-Significant/Large	Test number routing & Test APN configuration in PCCSM12 for Gi DNS Testing	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
47	23	2026-09-15	00:00:00 - 06:00:00	CRQ000005579184	1-Extensive/Widespread	IR S6a traffic routing from H-DRA to Oracle DSR in CMM-1&2	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
48	24	2026-09-15	00:00:00 - 06:00:00	CRQ000005579182	1-Extensive/Widespread	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
49	25	2026-09-15	23:00:00 - 06:00:00	CRQ000005579180	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
50	26	2026-09-15	23:00:00 - 06:00:00	CRQ000005579173	1-Extensive/Widespread	vIPWorks Version Update  to 2.13 in AP DNS APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
51	27	2026-09-15	23:00:00 - 06:00:00	CRQ000005579169	2-Significant/Large	S/W Package Loading for IPWorks version update to 2.13 in APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
52	28	2026-09-15	00:00:00 - 06:00:00	CRQ000005579166	1-Extensive/Widespread	Network Name configuration in all ROB MME and PCCMM	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
53	29	2026-09-15	23:00:00 - 07:00:00	CRQ000005579165	1-Extensive/Widespread	CR_MME Update from 1.84 to 1.91 in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
54	30	2026-09-15	00:00:00 - 06:00:00	CRQ000005579161	2-Significant/Large	Integration of GMLC & SMLC with new PCCMME10.	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
55	31	2026-09-15	00:00:00 - 06:00:00	CRQ000005579154	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
56	32	2026-09-15	23:00:00 - 07:00:00	CRQ000005579150	2-Significant/Large	CR_Package loading for MME 1.91 Update in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
57	33	2026-09-15	00:00:00 - 06:00:00	CRQ000005579140	2-Significant/Large	PBI000000269790:Alarm_Certificate Management, the Certificate is to Expire	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
58	34	2026-09-15	00:00:00 - 06:00:00	CRQ000005579137	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
59	35	2026-09-15	00:00:00 - 06:00:00	CRQ000005579125	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
60	36	2026-09-15	00:00:00 - 06:00:00	CRQ000005579121	1-Extensive/Widespread	M2M APN migration in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
61	37	2026-09-15	00:00:00 - 06:00:00	CRQ000005579119	1-Extensive/Widespread	SOS APN Routing Removal from GGSN02	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
62	38	2026-09-15	00:00:00 - 06:00:00	CRQ000005579114	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
63	39	2026-09-15	00:00:00 - 06:00:00	CRQ000005579108	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
64	40	2026-09-15	23:00:00 - 06:00:00	CRQ000005579101	1-Extensive/Widespread	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
65	41	2026-09-15	00:00:00 - 06:00:00	CRQ000005578993	1-Extensive/Widespread	PCCSM09 addition in DNS for 5G SA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
66	42	2026-09-15	00:00:00 - 06:00:00	CRQ000005578982	1-Extensive/Widespread	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
67	43	2026-09-15	00:00:00 - 06:00:00	CRQ000005578981	2-Significant/Large	PBI000000269363: 3 Learning implementation in UWN81NAAA01	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
68	44	2026-09-15	23:00:00 - 07:00:00	CRQ000005578971	2-Significant/Large	CR_Pre/Post BRM Backup for NEGUWRHCC01ERMME02 SW update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
69	45	2026-09-15	00:00:00 - 06:00:00	CRQ000005578964	1-Extensive/Widespread	TNSERRHCK10ERPCCSM12 || NRF registration & whitelisting at NRF end	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
70	46	2026-09-15	00:00:00 - 06:00:00	CRQ000005578952	1-Extensive/Widespread	TOPON wtg changes in PB Nokia DNS for HR GPOD1 entries removal & cache clear in MME.	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
71	47	2026-09-15	00:00:00 - 06:00:00	CRQ000005578912	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
72	48	2026-09-15	00:00:00 - 06:00:00	CRQ000005578795	1-Extensive/Widespread	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
73	49	2026-09-15	00:00:00 - 06:00:00	CRQ000005578775	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
74	50	2026-09-15	00:00:00 - 06:00:00	CRQ000005578589	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
75	51	2026-09-15	00:00:00 - 06:00:00	CRQ000005578539	1-Extensive/Widespread	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-2	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
76	52	2026-09-15	23:00:00 - 07:00:00	CRQ000005578494	1-Extensive/Widespread	Subscribers movement in E\\\\ MMEs via Pool Move for NEGUWRHCC01ERMME02  update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
77	53	2026-09-15	00:00:00 - 06:00:00	CRQ000005578485	1-Extensive/Widespread	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
78	54	2026-09-15	00:00:00 - 06:00:00	CRQ000005578452	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
79	55	2026-09-15	00:00:00 - 06:00:00	CRQ000005578415	1-Extensive/Widespread	IMSI purging from all DL SPG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
80	56	2026-09-15	00:00:00 - 06:00:00	CRQ000005578393	1-Extensive/Widespread	CR for MIP6 FQDN Definition at DNS end for CP08 and 09 With Cache clear	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
81	57	2026-09-15	00:00:00 - 06:00:00	CRQ000005578392	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
82	58	2026-09-15	23:00:00 - 07:00:00	CRQ000005578374	1-Extensive/Widespread	CMM gParam modify for traffic Balancing in HR Nokia CMMs as part of HRLUDCK02NCMM02 upgrade	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
83	59	2026-09-15	23:00:00 - 07:00:00	CRQ000005578366	1-Extensive/Widespread	Pre-post RC wt changes in HR CMM's/AMF's  for HRLUDCK02NCMM02 offloading/revert during upgrade	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
84	60	2026-09-15	00:00:00 - 06:00:00	CRQ000005578355	2-Significant/Large	Gateway IP change for APN  & Non live APN defn in Nokia  DNS	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
85	61	2026-09-15	00:00:00 - 06:00:00	CRQ000005578351	2-Significant/Large	Gateway IP change for APN  & Non live APN defn in Cisco  DNS	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
86	62	2026-09-15	00:00:00 - 06:00:00	CRQ000005578346	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
87	63	2026-09-15	00:00:00 - 06:00:00	CRQ000005578313	1-Extensive/Widespread	IMSI purging from all DL WMG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
88	64	2026-09-15	00:00:00 - 06:00:00	CRQ000005577456	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
89	65	2026-09-15	00:00:00 - 06:00:00	CRQ000005577389	1-Extensive/Widespread	UNUSSED APN deletion in Nokia CP02,CP05 & CP06	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
90	66	2026-09-15	00:00:00 - 06:00:00	CRQ000005577305	1-Extensive/Widespread	S10 Entry of MPBHPEMME01 remove from MAH DNSs	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
91	67	2026-09-15	00:00:00 - 06:00:00	CRQ000005576956	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
92	68	2026-09-15	00:00:00 - 06:00:00	CRQ000005576953	2-Significant/Large	BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Yes	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
93	69	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
94	70	2026-09-15	00:00:00 - 06:00:00	CRQ000005575963	1-Extensive/Widespread	PCCSM05 & PCGUP05 LBO Traffic Loading Balancing from GUJ Ericsson DNSs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
95	71	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	1-Extensive/Widespread	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
96	72	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	1-Extensive/Widespread	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
97	73	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	1-Extensive/Widespread	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
98	74	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
99	74	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	UPW	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	98
100	73	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	1-Extensive/Widespread	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	97
101	72	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	1-Extensive/Widespread	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	UPE	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	96
102	71	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	1-Extensive/Widespread	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	GJ	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	95
103	74	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	UPW	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	99
104	73	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	1-Extensive/Widespread	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	100
105	72	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	1-Extensive/Widespread	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	UPE	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	101
106	71	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	1-Extensive/Widespread	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	GJ	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	102
107	1	2026-09-15	23:00:00 - 07:00:00	CRQ000005581184	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes		North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	25
108	2	2026-09-15	23:00:00 - 07:00:00	CRQ000005581091	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes		North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	26
109	3	2026-09-15	00:00:00 - 06:00:00	CRQ000005580439	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	27
110	4	2026-09-15	00:00:00 - 06:00:00	CRQ000005580438	1-Extensive/Widespread	M2M APN sugslloyd.iot Gateway Change in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	28
111	5	2026-09-15	00:00:00 - 06:00:00	CRQ000005580375	2-Significant/Large	M2M-CR for non-live M2M APN(sugslloyd.iot.m2m) DNS entry in DL DNS with Cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	29
112	6	2026-09-15	23:00:00 - 06:00:00	CRQ000005579815	1-Extensive/Widespread	Traffic diversion from Ericsson MMEs & Revertback for vIPWorks DNS 2.13 Update in APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	30
113	7	2026-09-15	00:00:00 - 06:00:00	CRQ000005579756	2-Significant/Large	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes			Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	31
114	8	2026-09-15	00:00:00 - 06:00:00	CRQ000005579521	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in PCCSM	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	32
115	9	2026-09-15	00:00:00 - 06:00:00	CRQ000005579518	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	33
116	10	2026-09-15	00:00:00 - 06:00:00	CRQ000005579516	1-Extensive/Widespread	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	34
117	11	2026-09-15	00:00:00 - 06:00:00	CRQ000005579503	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in PCGUP05, ROBKGPEPG02	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	35
118	12	2026-09-15	00:00:00 - 06:00:00	CRQ000005579280	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	36
119	13	2026-09-15	00:00:00 - 06:00:00	CRQ000005579274	2-Significant/Large	IR IMSI definition in Nokia MME	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	37
120	14	2026-09-15	23:00:00 - 06:00:00	CRQ000005579268	1-Extensive/Widespread	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	38
121	15	2026-09-15	23:00:00 - 06:00:00	CRQ000005579259	2-Significant/Large	BRM and SP backup for IPWorks version update to 2.13 in AP DNS APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	39
122	16	2026-09-15	23:00:00 - 07:00:00	CRQ000005579249	1-Extensive/Widespread	CR for PWS & CTUM learning Implementation in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	40
123	17	2026-09-15	00:00:00 - 06:00:00	CRQ000005579241	1-Extensive/Widespread	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	2	41
124	18	2026-09-15	23:00:00 - 07:00:00	CRQ000005579226	1-Extensive/Widespread	RMC value changes and revert back NE E// MMEs for NEGUWRHCC01ERMME02 update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	42
125	19	2026-09-15	00:00:00 - 06:00:00	CRQ000005579212	1-Extensive/Widespread	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	43
126	20	2026-09-15	23:00:00 - 07:00:00	CRQ000005579204	1-Extensive/Widespread	CMM gParm modify for traffic offload in Nokia CMMs as part of in UWMORCK02NCMM03	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	44
127	21	2026-09-15	00:00:00 - 06:00:00	CRQ000005579197	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	45
128	22	2026-09-15	00:00:00 - 06:00:00	CRQ000005579193	2-Significant/Large	Test number routing & Test APN configuration in PCCSM12 for Gi DNS Testing	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	46
129	23	2026-09-15	00:00:00 - 06:00:00	CRQ000005579184	1-Extensive/Widespread	IR S6a traffic routing from H-DRA to Oracle DSR in CMM-1&2	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	47
130	24	2026-09-15	00:00:00 - 06:00:00	CRQ000005579182	1-Extensive/Widespread	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	48
131	25	2026-09-15	23:00:00 - 06:00:00	CRQ000005579180	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	49
132	26	2026-09-15	23:00:00 - 06:00:00	CRQ000005579173	1-Extensive/Widespread	vIPWorks Version Update  to 2.13 in AP DNS APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	50
133	27	2026-09-15	23:00:00 - 06:00:00	CRQ000005579169	2-Significant/Large	S/W Package Loading for IPWorks version update to 2.13 in APVIJEDNS03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	51
134	28	2026-09-15	00:00:00 - 06:00:00	CRQ000005579166	1-Extensive/Widespread	Network Name configuration in all ROB MME and PCCMM	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	52
135	29	2026-09-15	23:00:00 - 07:00:00	CRQ000005579165	1-Extensive/Widespread	CR_MME Update from 1.84 to 1.91 in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	53
136	30	2026-09-15	00:00:00 - 06:00:00	CRQ000005579161	2-Significant/Large	Integration of GMLC & SMLC with new PCCMME10.	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	54
137	31	2026-09-15	00:00:00 - 06:00:00	CRQ000005579154	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	2	55
138	32	2026-09-15	23:00:00 - 07:00:00	CRQ000005579150	2-Significant/Large	CR_Package loading for MME 1.91 Update in NEGUWRHCC01ERMME02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	56
139	33	2026-09-15	00:00:00 - 06:00:00	CRQ000005579140	2-Significant/Large	PBI000000269790:Alarm_Certificate Management, the Certificate is to Expire	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	57
140	34	2026-09-15	00:00:00 - 06:00:00	CRQ000005579137	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	58
141	35	2026-09-15	00:00:00 - 06:00:00	CRQ000005579125	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	59
142	36	2026-09-15	00:00:00 - 06:00:00	CRQ000005579121	1-Extensive/Widespread	M2M APN migration in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	60
143	37	2026-09-15	00:00:00 - 06:00:00	CRQ000005579119	1-Extensive/Widespread	SOS APN Routing Removal from GGSN02	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	61
144	38	2026-09-15	00:00:00 - 06:00:00	CRQ000005579114	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	62
145	39	2026-09-15	00:00:00 - 06:00:00	CRQ000005579108	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	63
146	40	2026-09-15	23:00:00 - 06:00:00	CRQ000005579101	1-Extensive/Widespread	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	64
147	41	2026-09-15	00:00:00 - 06:00:00	CRQ000005578993	1-Extensive/Widespread	PCCSM09 addition in DNS for 5G SA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	2	65
148	42	2026-09-15	00:00:00 - 06:00:00	CRQ000005578982	1-Extensive/Widespread	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	2	66
149	43	2026-09-15	00:00:00 - 06:00:00	CRQ000005578981	2-Significant/Large	PBI000000269363: 3 Learning implementation in UWN81NAAA01	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	67
150	44	2026-09-15	23:00:00 - 07:00:00	CRQ000005578971	2-Significant/Large	CR_Pre/Post BRM Backup for NEGUWRHCC01ERMME02 SW update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	68
151	45	2026-09-15	00:00:00 - 06:00:00	CRQ000005578964	1-Extensive/Widespread	TNSERRHCK10ERPCCSM12 || NRF registration & whitelisting at NRF end	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	69
152	46	2026-09-15	00:00:00 - 06:00:00	CRQ000005578952	1-Extensive/Widespread	TOPON wtg changes in PB Nokia DNS for HR GPOD1 entries removal & cache clear in MME.	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	70
153	47	2026-09-15	00:00:00 - 06:00:00	CRQ000005578912	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	71
154	48	2026-09-15	00:00:00 - 06:00:00	CRQ000005578795	1-Extensive/Widespread	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	2	72
155	49	2026-09-15	00:00:00 - 06:00:00	CRQ000005578775	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	73
156	50	2026-09-15	00:00:00 - 06:00:00	CRQ000005578589	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	74
157	51	2026-09-15	00:00:00 - 06:00:00	CRQ000005578539	1-Extensive/Widespread	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-2	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	75
158	52	2026-09-15	23:00:00 - 07:00:00	CRQ000005578494	1-Extensive/Widespread	Subscribers movement in E\\\\ MMEs via Pool Move for NEGUWRHCC01ERMME02  update	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	76
159	53	2026-09-15	00:00:00 - 06:00:00	CRQ000005578485	1-Extensive/Widespread	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	77
160	54	2026-09-15	00:00:00 - 06:00:00	CRQ000005578452	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	78
161	55	2026-09-15	00:00:00 - 06:00:00	CRQ000005578415	1-Extensive/Widespread	IMSI purging from all DL SPG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	79
162	56	2026-09-15	00:00:00 - 06:00:00	CRQ000005578393	1-Extensive/Widespread	CR for MIP6 FQDN Definition at DNS end for CP08 and 09 With Cache clear	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	80
163	57	2026-09-15	00:00:00 - 06:00:00	CRQ000005578392	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	81
164	58	2026-09-15	23:00:00 - 07:00:00	CRQ000005578374	1-Extensive/Widespread	CMM gParam modify for traffic Balancing in HR Nokia CMMs as part of HRLUDCK02NCMM02 upgrade	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	82
165	59	2026-09-15	23:00:00 - 07:00:00	CRQ000005578366	1-Extensive/Widespread	Pre-post RC wt changes in HR CMM's/AMF's  for HRLUDCK02NCMM02 offloading/revert during upgrade	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	83
166	60	2026-09-15	00:00:00 - 06:00:00	CRQ000005578355	2-Significant/Large	Gateway IP change for APN  & Non live APN defn in Nokia  DNS	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	84
167	61	2026-09-15	00:00:00 - 06:00:00	CRQ000005578351	2-Significant/Large	Gateway IP change for APN  & Non live APN defn in Cisco  DNS	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	85
168	62	2026-09-15	00:00:00 - 06:00:00	CRQ000005578346	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	86
169	63	2026-09-15	00:00:00 - 06:00:00	CRQ000005578313	1-Extensive/Widespread	IMSI purging from all DL WMG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	87
170	64	2026-09-15	00:00:00 - 06:00:00	CRQ000005577456	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	88
171	65	2026-09-15	00:00:00 - 06:00:00	CRQ000005577389	1-Extensive/Widespread	UNUSSED APN deletion in Nokia CP02,CP05 & CP06	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	89
172	66	2026-09-15	00:00:00 - 06:00:00	CRQ000005577305	1-Extensive/Widespread	S10 Entry of MPBHPEMME01 remove from MAH DNSs	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	90
173	67	2026-09-15	00:00:00 - 06:00:00	CRQ000005576956	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	91
174	68	2026-09-15	00:00:00 - 06:00:00	CRQ000005576953	2-Significant/Large	BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Yes	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	92
175	69	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	93
176	70	2026-09-15	00:00:00 - 06:00:00	CRQ000005575963	1-Extensive/Widespread	PCCSM05 & PCGUP05 LBO Traffic Loading Balancing from GUJ Ericsson DNSs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	2	94
177	71	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	1-Extensive/Widespread	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	4	106
178	72	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	1-Extensive/Widespread	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	4	105
179	73	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	1-Extensive/Widespread	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	4	104
180	74	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	4	103
181	1	2026-09-16	00:00:00 - 06:00:00	CRQ000005581678	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
182	2	2026-09-16	00:00:00 - 06:00:00	CRQ000005581101	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
183	3	2026-09-16	00:00:00 - 06:00:00	CRQ000005580869	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
184	4	2026-09-16	00:00:00 - 06:00:00	CRQ000005580868	1-Extensive/Widespread	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
185	5	2026-09-16	00:00:00 - 06:00:00	CRQ000005580865	1-Extensive/Widespread	PBI000000269790: learning for Alarm_Certificate Management Certificate is to Expire in AP SAPC Pair1	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
186	6	2026-09-16	00:00:00 - 06:00:00	CRQ000005580864	1-Extensive/Widespread	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
187	7	2026-09-16	00:00:00 - 06:00:00	CRQ000005580849	1-Extensive/Widespread	New SMF ID &GW HN definition in CCPC Pair-3&4	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
188	8	2026-09-16	00:00:00 - 06:00:00	CRQ000005580821	1-Extensive/Widespread	TOPON wtg changes in HR Nokia DNS for HR GPOD1 entries removal & cache clear in MME	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
189	9	2026-09-16	00:00:00 - 06:00:00	CRQ000005580817	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
190	10	2026-09-16	00:00:00 - 06:00:00	CRQ000005580810	1-Extensive/Widespread	M2M APN migration in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
191	11	2026-09-16	00:00:00 - 06:00:00	CRQ000005580808	1-Extensive/Widespread	SOS APN Routing Removal from GGSN02	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
192	12	2026-09-16	00:00:00 - 06:00:00	CRQ000005580804	1-Extensive/Widespread	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
193	13	2026-09-16	00:00:00 - 06:00:00	CRQ000005580803	2-Significant/Large	CR for Non-Live M2M APN definition in NOKIA DNS	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
194	14	2026-09-16	00:00:00 - 06:00:00	CRQ000005580796	1-Extensive/Widespread	PBI000000269790: Alarm_Certificate Management, the Certificate is to Expire in KK SAPC Pair2	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
195	15	2026-09-16	00:00:00 - 06:00:00	CRQ000005580792	2-Significant/Large	Multiple M2M Private APN Entry in Ericsson DNS (Non-Live)	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
196	16	2026-09-16	00:00:00 - 06:00:00	CRQ000005580791	1-Extensive/Widespread	SBc interface integration for CBC in KKMANGEMME04	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
197	17	2026-09-16	00:00:00 - 06:00:00	CRQ000005580788	1-Extensive/Widespread	CR for Gx event trigger suppression in Nokia JAICMG01 and CP02	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
198	18	2026-09-16	00:00:00 - 06:00:00	CRQ000005580775	1-Extensive/Widespread	CCAF Link Delete Create in KGPEPG02	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
199	19	2026-09-16	00:00:00 - 06:00:00	CRQ000005580772	2-Significant/Large	Test number routing in A2CP02  towards ASBC-31	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
200	20	2026-09-16	00:00:00 - 06:00:00	CRQ000005580761	1-Extensive/Widespread	CR for License Loading in KL SAPC Pair-1	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
201	21	2026-09-16	00:00:00 - 06:00:00	CRQ000005580752	2-Significant/Large	CR_to remove local-plmn-csr-apn in ASGHERIWMG01	No	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
202	22	2026-09-16	00:00:00 - 06:00:00	CRQ000005580731	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules_E// EPG & E// PCCSM	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
203	23	2026-09-16	00:00:00 - 06:00:00	CRQ000005580713	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
204	24	2026-09-16	00:00:00 - 06:00:00	CRQ000005580594	2-Significant/Large	Test number routing towards A2CP02,CMG-1&cisco SPG from all CMM	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
205	25	2026-09-16	00:00:00 - 06:00:00	CRQ000005580564	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPG & PCCSM11	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
206	26	2026-09-16	00:00:00 - 06:00:00	CRQ000005580560	1-Extensive/Widespread	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
207	27	2026-09-16	00:00:00 - 06:00:00	CRQ000005580557	1-Extensive/Widespread	CR_Gi DNS migration in NEJORRHCK04ERPCCSM02 Day 1	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
208	28	2026-09-16	00:00:00 - 06:00:00	CRQ000005580555	1-Extensive/Widespread	Top On Weightage for LBO PCCSM16 Go Live in MME	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
209	29	2026-09-16	00:00:00 - 06:00:00	CRQ000005580547	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
210	30	2026-09-16	00:00:00 - 06:00:00	CRQ000005580543	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
211	31	2026-09-16	00:00:00 - 06:00:00	CRQ000005580542	1-Extensive/Widespread	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
212	32	2026-09-16	23:00:00 - 06:00:00	CRQ000005580532	1-Extensive/Widespread	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
213	33	2026-09-16	23:00:00 - 07:00:00	CRQ000005580502	1-Extensive/Widespread	Pre post sub balancing Sub balancing in PB GW's  as a part of  PBLUDNA2CP04 Upgrade	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
214	34	2026-09-16	00:00:00 - 06:00:00	CRQ000005580492	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
215	35	2026-09-16	00:00:00 - 06:00:00	CRQ000005580475	1-Extensive/Widespread	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
216	36	2026-09-16	00:00:00 - 06:00:00	CRQ000005580472	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules_KL Nokia & Cisco GW	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
217	37	2026-09-16	00:00:00 - 06:00:00	CRQ000005580461	1-Extensive/Widespread	CR for NF ID whitelisting in the NRF for the New non-live KLPOLCK06NCMM05	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
218	38	2026-09-16	00:00:00 - 06:00:00	CRQ000005580458	2-Significant/Large	JIO new test IMSI routing in HR CMM's for ICR testing for HR circle	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
219	39	2026-09-16	00:00:00 - 06:00:00	CRQ000005580457	1-Extensive/Widespread	GPL correction in ASGUWCC01EREPG05	No	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
220	40	2026-09-16	00:00:00 - 06:00:00	CRQ000005580441	1-Extensive/Widespread	PCCSM09 addition in DNS for 5G SA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
221	41	2026-09-16	00:00:00 - 06:00:00	CRQ000005580436	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
222	42	2026-09-16	00:00:00 - 06:00:00	CRQ000005580422	1-Extensive/Widespread	Top On Weightage for PCCSM16 Go-Live in DNS	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
223	43	2026-09-16	00:00:00 - 06:00:00	CRQ000005580416	2-Significant/Large	CR to check the UPW & HR. inter PLMN reachability from DL AMF/SMF/MME/LPG	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
224	44	2026-09-16	00:00:00 - 06:00:00	CRQ000005580396	1-Extensive/Widespread	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
225	45	2026-09-16	00:00:00 - 06:00:00	CRQ000005580392	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
226	46	2026-09-16	00:00:00 - 06:00:00	CRQ000005580390	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
227	47	2026-09-16	23:00:00 - 07:00:00	CRQ000005580360	1-Extensive/Widespread	TOPON wtg changes in PB Nokia DNS to offload/revert PBLUDNA2CP04 for Upgrade & cache clear in MME	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
228	48	2026-09-16	00:00:00 - 06:00:00	CRQ000005580338	1-Extensive/Widespread	TAC LAC Modification in Eric MME's for CSFB optimization	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
229	49	2026-09-16	00:00:00 - 06:00:00	CRQ000005580190	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
230	50	2026-09-16	00:00:00 - 06:00:00	CRQ000005580186	1-Extensive/Widespread	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
231	51	2026-09-16	00:00:00 - 06:00:00	CRQ000005580177	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
232	52	2026-09-16	00:00:00 - 06:00:00	CRQ000005580174	1-Extensive/Widespread	S10 Entry of MP MME remove in GUJ DNSs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
233	53	2026-09-16	00:00:00 - 06:00:00	CRQ000005580170	1-Extensive/Widespread	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
234	54	2026-09-16	00:00:00 - 06:00:00	CRQ000005579899	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
235	55	2026-09-16	00:00:00 - 06:00:00	CRQ000005579892	1-Extensive/Widespread	CR for SBC wtg optimization in MAN SPG2	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
236	56	2026-09-16	00:00:00 - 06:00:00	CRQ000005579878	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules in EPGs	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
237	57	2026-09-16	00:00:00 - 06:00:00	CRQ000005579587	1-Extensive/Widespread	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
238	58	2026-09-16	00:00:00 - 06:00:00	CRQ000005579504	1-Extensive/Widespread	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-1	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
239	59	2026-09-16	00:00:00 - 06:00:00	CRQ000005579252	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
240	60	2026-09-16	00:00:00 - 06:00:00	CRQ000005579246	1-Extensive/Widespread	M2M APN Gateway Change in DNS	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
241	61	2026-09-16	23:00:00 - 07:00:00	CRQ000005579228	1-Extensive/Widespread	CMM gParm modify for traffic offload in Nokia CMMs as per UEGANCK04NCMM07 Upgrade	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
242	62	2026-09-16	00:00:00 - 06:00:00	CRQ000005578916	1-Extensive/Widespread	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
243	63	2026-09-16	00:00:00 - 06:00:00	CRQ000005578904	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
244	64	2026-09-16	23:00:00 - 07:00:00	CRQ000005578771	1-Extensive/Widespread	CMM gParam modify for traffic Balancing in Nokia CMMs as part of Jaipur CMM09 Upgrade	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
245	65	2026-09-16	00:00:00 - 06:00:00	CRQ000005578546	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	KO	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
246	66	2026-09-16	00:00:00 - 06:00:00	CRQ000005578388	1-Extensive/Widespread	5G home Traffic Balancing from GUJ DNSs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
247	67	2026-09-16	23:00:00 - 07:00:00	CRQ000005578360	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
248	68	2026-09-16	23:00:00 - 07:00:00	CRQ000005577478	1-Extensive/Widespread	BPMS - RC Value Change Nokia CMM - Pre-Post - E2E	Yes	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
249	69	2026-09-16	23:00:00 - 07:00:00	CRQ000005577474	2-Significant/Large	BRM and SP backup for MUMCHAEDNS01 before and after activity	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
250	70	2026-09-16	23:00:00 - 07:00:00	CRQ000005577445	2-Significant/Large	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in MUMCHAEDNS01	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
251	71	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	1-Extensive/Widespread	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
252	72	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	2-Significant/Large	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
253	73	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
254	74	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	1-Extensive/Widespread	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
255	75	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	2-Significant/Large	CR for Non-Live M2M APN definition in CISCO DNS	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
256	76	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	2-Significant/Large	Test IMSI routing in MAN MME1 towards DSR5/6	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
257	76	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	2-Significant/Large	Test IMSI routing in MAN MME1 towards DSR5/6	No	DL	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	256
258	75	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	2-Significant/Large	CR for Non-Live M2M APN definition in CISCO DNS	No	UPW	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	255
259	74	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	1-Extensive/Widespread	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	CH	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	254
260	73	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	253
261	76	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	2-Significant/Large	Test IMSI routing in MAN MME1 towards DSR5/6	No	DL	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	3	257
262	75	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	2-Significant/Large	CR for Non-Live M2M APN definition in CISCO DNS	No	UPW	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	3	258
263	74	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	1-Extensive/Widespread	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	CH	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	3	259
264	73	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	260
265	73	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	264
266	72	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	2-Significant/Large	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	MU	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	252
267	71	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	1-Extensive/Widespread	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	MU	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	251
268	73	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	265
269	72	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	2-Significant/Large	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	MU	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	3	266
270	71	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	1-Extensive/Widespread	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	MU	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	t	3	267
271	1	2026-09-17	00:00:00 - 06:00:00	CRQ000005583437	1-Extensive/Widespread	M2M CR for new source IP pool addition in MUM M2M EPG FOR M2M gprsnac.com apn	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
272	2	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
273	3	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
274	4	2026-09-17	00:00:00 - 06:00:00	CRQ000005583423	2-Significant/Large	Multiple IR definition in PB Nokia CMM	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
275	5	2026-09-17	00:00:00 - 06:00:00	CRQ000005583421	2-Significant/Large	M2M CR for new source IP pool addition in MUM M2M EPG FOR M2M gprsnac.com apn	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
276	6	2026-09-17	23:00:00 - 07:00:00	CRQ000005583419	1-Extensive/Widespread	TOPON changes for 2G in Cisco SGSN for KLCALNA2CP03 upgrade and revert	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
277	7	2026-09-17	00:00:00 - 06:00:00	CRQ000005583345	1-Extensive/Widespread	PBI000000268674:Learning RPC portmapper Service Detection Vulnerability in PB CMM01_LTMT2	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
278	8	2026-09-17	00:00:00 - 06:00:00	CRQ000005583315	1-Extensive/Widespread	CR_EPLMN definition in AS MMEs with PCCMM for 4G	No	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
279	9	2026-09-17	23:00:00 - 07:00:00	CRQ000005583314	1-Extensive/Widespread	CR for subscriber clear in KL GGSN Nodes post KLCALNA2CP03 upgrade	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
280	10	2026-09-17	00:00:00 - 06:00:00	CRQ000005583302	1-Extensive/Widespread	PBI000000269790: learning for Alarm_Certificate Management Certificate is to Expire in AP SAPC Pair2	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
281	11	2026-09-17	00:00:00 - 06:00:00	CRQ000005583168	2-Significant/Large	New ICR Test number definition in ROB MME&PCCMM	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
282	12	2026-09-17	00:00:00 - 06:00:00	CRQ000005583167	1-Extensive/Widespread	CCAF Link Delete Create in ROBSILCC01EREPGCP03	No	WB	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
283	13	2026-09-17	00:00:00 - 06:00:00	CRQ000005583160	1-Extensive/Widespread	PDP flushing in all GGSN for Home IMSI series migration from SAPC to CCPC and SAPC	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
284	14	2026-09-17	00:00:00 - 06:00:00	CRQ000005583153	1-Extensive/Widespread	SMF 5G SA traffic weightage distribution for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
285	15	2026-09-17	00:00:00 - 06:00:00	CRQ000005583150	2-Significant/Large	Multiple IR definition in PB CISCO MMEs.	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
286	16	2026-09-17	00:00:00 - 06:00:00	CRQ000005583143	2-Significant/Large	Volte IR launch (Polkomtel_Poland) definition in HP NOKIA CMM's	No	HP	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
287	17	2026-09-17	23:00:00 - 07:00:00	CRQ000005583138	1-Extensive/Widespread	TOPON changes for 5G,4G & IMS in DNS Nodes for KLCALNA2CP03 upgrade and revert with cacheclear	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
288	18	2026-09-17	00:00:00 - 06:00:00	CRQ000005583129	2-Significant/Large	Static test IMSI routing in TN E// MMEs & PCCMMs for new Node PCCSM12	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
289	19	2026-09-17	00:00:00 - 06:00:00	CRQ000005583123	1-Extensive/Widespread	CR_PCF Priority change in NESA CCPC Pair 2 (Jorhat Prefer)	No	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
290	20	2026-09-17	00:00:00 - 06:00:00	CRQ000005583116	1-Extensive/Widespread	Migration of HR imsi (404960969) towards PB new OCDRA03_04 for S6a traffic from HR CMM02	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
291	21	2026-09-17	00:00:00 - 06:00:00	CRQ000005583113	1-Extensive/Widespread	PBI000000269910-Learning-CBC timers and buffers size change in Ericsson-AP MME & PCCMMs	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
292	22	2026-09-17	00:00:00 - 06:00:00	CRQ000005582884	1-Extensive/Widespread	SBc interface integration for CBC in KKMANGEMME04	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
293	23	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	2-Significant/Large	CR for New IR Definition in MME & PCCMM	No	BH	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
294	24	2026-09-17	00:00:00 - 06:00:00	CRQ000005582864	2-Significant/Large	M2M CR FOr Multiple M2M APN Gateway IP change from MUM Eric DNS	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
295	25	2026-09-17	23:00:00 - 07:00:00	CRQ000005582856	1-Extensive/Widespread	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
296	26	2026-09-17	00:00:00 - 06:00:00	CRQ000005582850	1-Extensive/Widespread	SOS APN Routing Removal from GGSN02	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
297	27	2026-09-17	00:00:00 - 06:00:00	CRQ000005582845	1-Extensive/Widespread	New FWA MDU UE IP POOL ADDITION in PBLUDNA2CP02/ U03/U04 for testing	No	PB	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
298	28	2026-09-17	00:00:00 - 06:00:00	CRQ000005582840	2-Significant/Large	MIP6 FQDN Definition for odbsvna2cp03 in Nokia DNS with Cache clear	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
299	29	2026-09-17	00:00:00 - 06:00:00	CRQ000005582839	2-Significant/Large	MIP6 FQDN Definition for odbsvna2cp03 in Cisco DNS with Cache clear	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
300	30	2026-09-17	23:00:00 - 07:00:00	CRQ000005582831	1-Extensive/Widespread	CMM-1,2,3 for traffic balancing with Gpara change Post CMM-4 upgrade	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
301	31	2026-09-17	23:00:00 - 07:00:00	CRQ000005582829	2-Significant/Large	4G/5G RC change in CMM-1,2,3 for sw upgrade in CMM-4	No	OR	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
335	65	2026-09-17	00:00:00 - 06:00:00	CRQ000005576881	2-Significant/Large	CR for 5G location Retrieval Enable in Nokia AAA	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	6	268
302	32	2026-09-17	00:00:00 - 06:00:00	CRQ000005582555	1-Extensive/Widespread	New_Learning: Alarm_Certificate Management, the Certificate is to Expire SAPC Pair 1 nodes	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
303	33	2026-09-17	00:00:00 - 06:00:00	CRQ000005582539	1-Extensive/Widespread	CR_IMS paging profile optimization in ASJORRHCK04ERPCCMM07	No	AS	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
304	34	2026-09-17	00:00:00 - 06:00:00	CRQ000005582538	1-Extensive/Widespread	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
305	35	2026-09-17	00:00:00 - 06:00:00	CRQ000005582534	1-Extensive/Widespread	Gi-DNS IP change in test apn in NEJORRHCK04ERPCCSM02	No	NE	East	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
306	36	2026-09-17	00:00:00 - 06:00:00	CRQ000005582417	1-Extensive/Widespread	IMEI TAC -35418669 routed from CFWA-11/12 CMG to CFWA-UPF03	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
307	37	2026-09-17	00:00:00 - 06:00:00	CRQ000005582290	1-Extensive/Widespread	Home Gy Traffic addition in APVIJRHCK01ERPCCSM05 towards Uppal & Siruseri  CAF (with Dlb0,1 & Dlb2)	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
308	38	2026-09-17	00:00:00 - 06:00:00	CRQ000005582267	2-Significant/Large	Learning-Vulnerability mitigation in CMM(Elasticsearch Unrestricted Access Information Disclosure)	No	UPW	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
309	39	2026-09-17	00:00:00 - 06:00:00	CRQ000005581700	1-Extensive/Widespread	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-1	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
310	40	2026-09-17	00:00:00 - 06:00:00	CRQ000005581682	2-Significant/Large	Activity for Test Number routing at Nokia CMM end	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
311	41	2026-09-17	00:00:00 - 06:00:00	CRQ000005581681	1-Extensive/Widespread	CR for DSR Test Number Routing in RAJ-UDP-B2C-vSPG-01	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
312	42	2026-09-17	00:00:00 - 06:00:00	CRQ000005581639	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
313	43	2026-09-17	00:00:00 - 06:00:00	CRQ000005581637	1-Extensive/Widespread	Support CR for Subs Purging for Activity revert SM3 Home/LBO Postpaid GxGy migration towards DSR3/4	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
314	44	2026-09-17	00:00:00 - 06:00:00	CRQ000005581627	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
315	45	2026-09-17	23:00:00 - 07:00:00	CRQ000005581618	2-Significant/Large	BRM and SP backup for CHNSIREDNS03 before and after activity	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
316	46	2026-09-17	23:00:00 - 07:00:00	CRQ000005581617	1-Extensive/Widespread	Traffic diversion from CHN E// MMEs & rollback for IPWorks DNS 2.13 Update in CHNSIREDNS03	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
317	47	2026-09-17	23:00:00 - 07:00:00	CRQ000005581616	1-Extensive/Widespread	vIPWorks Version Update to 2.11 to 2.13 in CHN E// DNS CHNSIREDNS03	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
318	48	2026-09-17	23:00:00 - 07:00:00	CRQ000005581615	2-Significant/Large	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in CHNSIREDNS03	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
319	49	2026-09-17	00:00:00 - 06:00:00	CRQ000005581279	1-Extensive/Widespread	CR for complete imsi 40410 migration towards DSR5/6 in PCCMM5 and purging regards rollback	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
320	50	2026-09-17	00:00:00 - 06:00:00	CRQ000005581276	1-Extensive/Widespread	CR for MAN PCCSM3 Home/LBO Postpaid GxGy migration towards DSR3/4	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
321	51	2026-09-17	00:00:00 - 06:00:00	CRQ000005581267	1-Extensive/Widespread	CR for IR PLMN IMS PGW wtg changes in EDNS/cache clear regard DL IRGW1 traffic optimization	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
322	52	2026-09-17	00:00:00 - 06:00:00	CRQ000005581117	1-Extensive/Widespread	New IP Pool for airtelfwamdu of CP02 CMG ( UP05 / UP06) for Go Live	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
323	53	2026-09-17	00:00:00 - 06:00:00	CRQ000005581094	2-Significant/Large	M2M-CR for non-live M2M APN(sweetfhv.m2mm) DNS entry in DL DNS with Cache clear	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
324	54	2026-09-17	00:00:00 - 06:00:00	CRQ000005581083	1-Extensive/Widespread	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
325	55	2026-09-17	23:00:00 - 07:00:00	CRQ000005581082	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
326	56	2026-09-17	00:00:00 - 06:00:00	CRQ000005581041	1-Extensive/Widespread	Non-Live SMF (SM07) Instance ID Registration De-registration through NF Screening	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
327	57	2026-09-17	00:00:00 - 06:00:00	CRQ000005580798	2-Significant/Large	New multiple operator launch for VOLTE/5G IR launch in KKMMEs/PCCMMs	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
328	58	2026-09-17	00:00:00 - 06:00:00	CRQ000005580797	1-Extensive/Widespread	SGs pool addition for LAC- 26671,2,3,4,21791,2,3,5,6,7 (Hubli/MLR Pool VLRs) in KKMMEs-Ph-24	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
329	59	2026-09-17	00:00:00 - 06:00:00	CRQ000005579589	1-Extensive/Widespread	Unused TAC related configuration deletion in Cisco & Nokia  DNS	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
330	60	2026-09-17	00:00:00 - 06:00:00	CRQ000005579241	1-Extensive/Widespread	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	3	123
331	61	2026-09-17	00:00:00 - 06:00:00	CRQ000005579154	2-Significant/Large	Cache Clear in MPCG E//MMEs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	3	137
332	62	2026-09-17	00:00:00 - 06:00:00	CRQ000005578993	1-Extensive/Widespread	PCCSM09 addition in DNS for 5G SA Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	3	147
333	63	2026-09-17	00:00:00 - 06:00:00	CRQ000005578982	1-Extensive/Widespread	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	3	148
334	64	2026-09-17	00:00:00 - 06:00:00	CRQ000005578795	1-Extensive/Widespread	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	3	154
336	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
337	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
338	68	2026-09-17	00:00:00 - 06:00:00	CRQ000005566714	1-Extensive/Widespread	Support CR :blocking / Unblocking  the traffic from all Huawei /Nokia GGSNs to OCC-3	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
339	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	337
340	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	336
341	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	339
342	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	340
343	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	341
344	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	4	342
345	23	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	2-Significant/Large	CR for New IR Definition in MME & PCCMM	No	BH	East	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	293
346	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	343
347	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	5	344
348	23	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	2-Significant/Large	CR for New IR Definition in MME & PCCMM	No	BH	East	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	345
349	3	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MU	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	273
350	2	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	272
351	3	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MU	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	349
352	2	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	350
353	67	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	1-Extensive/Widespread	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	t	6	346
354	66	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	1-Extensive/Widespread	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	t	6	347
355	23	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	2-Significant/Large	CR for New IR Definition in MME & PCCMM	No	BH	East	Enjoy Maity	Success	Pending	Pending	Pending	 	t	4	348
356	3	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MU	West	Enjoy Maity	Success	Pending	Pending	Pending	 	t	4	351
357	2	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	MH	West	Enjoy Maity	Success	Pending	Pending	Pending	 	t	4	352
362	5	2026-09-30	00:00:00 - 06:00:00	CRQ000005597711	1-Extensive/Widespread	New ASBC81 Go-live with AP Ericsson EPGs	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
363	6	2026-09-30	00:00:00 - 06:00:00	CRQ000005597707	1-Extensive/Widespread	CR for NF ID whitelisting in the NRF for the New non-live KLPOLCK06NCMM05	No	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
364	7	2026-09-30	23:00:00 - 07:00:00	CRQ000005597523	1-Extensive/Widespread	BPMS - Ericsson MME Update - E2E version 1.91	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
365	8	2026-09-30	00:00:00 - 06:00:00	CRQ000005597150	1-Extensive/Widespread	CR for RC value change in MUM Eric MME for 4G & 5G traffic loading on PCCMM04	No	MU	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
366	9	2026-09-30	23:00:00 - 06:00:00	CRQ000005597111	1-Extensive/Widespread	N8 UDM HTTP2 to NAS 5G-MM CC Mapping Alignment to CC27 in HR AMF	No	HR	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
367	10	2026-09-30	00:00:00 - 06:00:00	CRQ000005596922	2-Significant/Large	RJ Circle_MPS cell update for migration	No			Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
368	11	2026-09-30	23:00:00 - 07:00:00	CRQ000005596793	1-Extensive/Widespread	BPMS - Ericsson MME Update Precheck - E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
369	12	2026-09-30	23:00:00 - 07:00:00	CRQ000005596790	1-Extensive/Widespread	BPMS-Ericsson MME Update Pre Subs.clear & RC change - E2E	Yes	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
359	2	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	1-Extensive/Widespread	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
360	3	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	2-Significant/Large	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
361	4	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	1-Extensive/Widespread	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
370	13	2026-09-30	00:00:00 - 06:00:00	CRQ000005596788	1-Extensive/Widespread	KKASBC80 traffic opening from KK Ericsson GWs 3,5,6,7,8,9	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
371	14	2026-09-30	00:00:00 - 06:00:00	CRQ000005596787	2-Significant/Large	jiobhometerv6 APN creation in KKMGRNM2MCP01/ KKMGRNM2MCP01U01	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
372	15	2026-09-30	00:00:00 - 06:00:00	CRQ000005596786	2-Significant/Large	PBI000000269920: Learning-Vulnerability mitigation in E// MMEs(SSH Weak MAC/KEY )	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
373	16	2026-09-30	00:00:00 - 06:00:00	CRQ000005596784	1-Extensive/Widespread	SGs pool addition for LAC- 26761,2,21812,4,5,26591,2,3,4,5 (Hubli/MLR Pool VLRs) in KKMMEs-Ph-26	No	KK	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
374	17	2026-09-30	23:00:00 - 07:00:00	CRQ000005596770	2-Significant/Large	System and User backup for IPWorks version update 2.11 to 2.13 in TNSIREDNS03	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
375	18	2026-09-30	23:00:00 - 07:00:00	CRQ000005596766	1-Extensive/Widespread	Traffic diversion from TN E// MMEs & Revertback for IPWorks DNS 2.13 Update in TNSIREDNS03	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
376	19	2026-09-30	00:00:00 - 06:00:00	CRQ000005596756	1-Extensive/Widespread	Domain whitelisting in data expire and throttle rules_GJCHANA2CP01U01	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
377	20	2026-09-30	00:00:00 - 06:00:00	CRQ000005596748	2-Significant/Large	CR for New PCCSM7 host & p2p config in DL SAPC PAIR1	No	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
378	21	2026-09-30	00:00:00 - 06:00:00	CRQ000005596719	2-Significant/Large	New APN creation in  CHSIRNM2MCP02/ CHSIRNM2MCP02UP02 -etplgedv6	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
380	23	2026-09-30	00:00:00 - 06:00:00	CRQ000005596668	1-Extensive/Widespread	PBI000000269910:Buffer size increase in CHN MMEs to resolve issue with large number of cells for CBC	No	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
381	24	2026-09-30	00:00:00 - 06:00:00	CRQ000005596667	1-Extensive/Widespread	New Prepaid South CCAF config and test number routing in TNC_PCCSM	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
382	25	2026-09-30	23:00:00 - 07:00:00	CRQ000005596665	1-Extensive/Widespread	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in TNSIREDNS03	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
384	27	2026-09-30	00:00:00 - 06:00:00	CRQ000005596632	1-Extensive/Widespread	etplgedv6 APN Creation in MHKHRNM2MCP02_MHKHRNM2MCP02UP02	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
385	28	2026-09-30	00:00:00 - 06:00:00	CRQ000005596626	1-Extensive/Widespread	PBI000000269790:learning for Alarm_Certificate Management Certificate is to Expire in SAPC Pair-2	No	RJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
386	29	2026-09-30	00:00:00 - 06:00:00	CRQ000005596602	1-Extensive/Widespread	4G/5G home & FWA MDU Traffic Balancing from GUJ DNSs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
387	30	2026-09-30	00:00:00 - 06:00:00	CRQ000005596596	2-Significant/Large	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
388	31	2026-09-30	23:00:00 - 07:00:00	CRQ000005596589	1-Extensive/Widespread	TNSIREDNS03_ vIPWorks Version Update from 2.11 to 2.13 in TNSIREDNS03	No	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
389	32	2026-09-30	23:00:00 - 07:00:00	CRQ000005596540	2-Significant/Large	Software Package loading for MAHPUNEMME02 1.91 update	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
390	33	2026-09-30	23:00:00 - 07:00:00	CRQ000005596535	1-Extensive/Widespread	RMC value changes in E//MMEs for MAHPUNEMME02 Ver. Update from 1.84 to 1.91	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
391	34	2026-09-30	00:00:00 - 06:00:00	CRQ000005596508	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
392	35	2026-09-30	23:00:00 - 07:00:00	CRQ000005596461	1-Extensive/Widespread	PWS & CTUM learning Implementation in MAHPUNEMME02	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
393	36	2026-09-30	23:00:00 - 07:00:00	CRQ000005596458	1-Extensive/Widespread	Subscribers movement in E//MMEs via Pool Move operation for MAHPUNEMME02 SW update	No	MH	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
394	37	2026-09-30	00:00:00 - 06:00:00	CRQ000005596440	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	JK	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
395	38	2026-09-30	00:00:00 - 06:00:00	CRQ000005596426	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
396	39	2026-09-30	00:00:00 - 06:00:00	CRQ000005596300	2-Significant/Large	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	KL	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
397	40	2026-09-30	00:00:00 - 06:00:00	CRQ000005596099	1-Extensive/Widespread	FWA MDU Traffic Loading & Balancing from GUJ MMEs	No	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
398	41	2026-09-30	00:00:00 - 06:00:00	CRQ000005596035	1-Extensive/Widespread	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
399	42	2026-09-30	00:00:00 - 06:00:00	CRQ000005595985	1-Extensive/Widespread	Junk NB-IOT TACs deletion from Nokia CMMs ( 4000 / 4011)	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
400	43	2026-09-30	00:00:00 - 06:00:00	CRQ000005595924	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
401	44	2026-09-30	00:00:00 - 06:00:00	CRQ000005595914	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
402	45	2026-09-30	23:00:00 - 06:00:00	CRQ000005595557	2-Significant/Large	MAH_2G_MPS CELL DATA UPLOAD ACTIVITY	No			Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
403	46	2026-09-30	23:00:00 - 07:00:00	CRQ000005595334	1-Extensive/Widespread	DNS weightages change in Nokia DNS & VAR DNS for Gangaganj Nokia CP05 CMG upgrade	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
383	26	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
404	47	2026-09-30	23:00:00 - 07:00:00	CRQ000005595150	1-Extensive/Widespread	Subscribers offloading  & balancing  from UPE All GGSN for Gangaganj Nokia CP05 CMG	No	UPE	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
405	48	2026-09-30	00:00:00 - 06:00:00	CRQ000005595109	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	DL	North	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
406	49	2026-09-30	00:00:00 - 06:00:00	CRQ000005594425	1-Extensive/Widespread	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes	CH	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
407	50	2026-09-30	00:00:00 - 06:00:00	CRQ000005594403	2-Significant/Large	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
408	51	2026-09-30	00:00:00 - 06:00:00	CRQ000005594171	1-Extensive/Widespread	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes	TN	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
410	53	2026-09-30	00:00:00 - 06:00:00	CRQ000005590783	1-Extensive/Widespread	New ASBC-33 Go-Live from E//PGWs	No	MP	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	t	1	\N
358	1	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	1-Extensive/Widespread	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
411	1	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	1-Extensive/Widespread	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	AP	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	358
412	2	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	1-Extensive/Widespread	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	AP	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	359
413	3	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	2-Significant/Large	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	AP	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	360
414	4	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	1-Extensive/Widespread	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	AP	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	361
379	22	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
409	52	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	2-Significant/Large	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	GJ	West	Enjoy Maity	Pending	Pending	Pending	Pending	 	f	1	\N
419	22	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	379
420	52	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	2-Significant/Large	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	GJ	West	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	409
421	26	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	TN	South	Enjoy Maity	Success	Pending	Pending	Pending	 	f	2	383
415	1	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	1-Extensive/Widespread	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	AP	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	411
425	1	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	1-Extensive/Widespread	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	AP	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	415
416	2	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	1-Extensive/Widespread	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	AP	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	412
426	2	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	1-Extensive/Widespread	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	AP	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	416
417	3	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	2-Significant/Large	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	AP	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	413
427	3	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	2-Significant/Large	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	AP	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	417
418	4	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	1-Extensive/Widespread	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	AP	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	414
428	4	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	1-Extensive/Widespread	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	AP	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	418
422	22	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	419
429	22	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	AP	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	422
423	52	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	2-Significant/Large	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	GJ	West	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	420
430	52	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	2-Significant/Large	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	GJ	West	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	423
424	26	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	TN	South	Enjoy Maity	Unsuccess	Pending	Pending	Pending	 	f	3	421
431	26	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	2-Significant/Large	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	TN	South	Enjoy Maity	Unsuccess	Success	Pending	Pending	 	t	4	424
\.


--
-- Data for Name: dashboard_automationtask; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_automationtask (id, sequence_no, name, upload_required, download_required, current_status, active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dashboard_flagtable; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_flagtable (id, source_id, status, version) FROM stdin;
\.


--
-- Data for Name: dashboard_tasklog; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_tasklog (id, level, message, created_at, run_id) FROM stdin;
\.


--
-- Data for Name: dashboard_taskrun; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_taskrun (id, status, uploaded_template, output_file, started_at, completed_at, task_id, triggered_by_id) FROM stdin;
\.


--
-- Data for Name: dashboard_usermanagement; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_usermanagement (id, password, last_login, is_superuser, username, first_name, last_name, is_staff, is_active, date_joined, email, employee_name, employee_signum, role) FROM stdin;
1	pbkdf2_sha256$1500000$6mKb74mxZki9RxlOnqEJ2Q$qRFn65JDRsGIjiSF2OjS5Dwac83xnyHytUKwqcAifDU=	2026-09-29 11:08:56.840015+00	t	enjoy	Enjoy	Maity	t	t	2026-09-11 14:21:07+00	enjoy.maity@ericsson.com	Enjoy Maity	emaienj	Admin
\.


--
-- Data for Name: dashboard_usermanagement_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_usermanagement_groups (id, usermanagement_id, group_id) FROM stdin;
\.


--
-- Data for Name: dashboard_usermanagement_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_usermanagement_user_permissions (id, usermanagement_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-09-11 14:24:21.739+00	1	enjoy (Admin)	2	[{"changed": {"fields": ["First name", "Last name", "Employee name", "Employee signum"]}}]	13	1
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	contenttypes	contenttype
5	sessions	session
6	dashboard	automationtask
7	dashboard	crwisestatus
8	dashboard	flagtable
9	dashboard	mastercrdatabase
10	dashboard	selecteddatetable
11	dashboard	tasklog
12	dashboard	taskrun
13	dashboard	usermanagement
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-09-29 11:08:02.680254+00
2	contenttypes	0002_remove_content_type_name	2026-09-29 11:08:02.692618+00
3	auth	0001_initial	2026-09-29 11:08:02.757679+00
4	auth	0002_alter_permission_name_max_length	2026-09-29 11:08:02.764469+00
5	auth	0003_alter_user_email_max_length	2026-09-29 11:08:02.778063+00
6	auth	0004_alter_user_username_opts	2026-09-29 11:08:02.787475+00
7	auth	0005_alter_user_last_login_null	2026-09-29 11:08:02.797792+00
8	auth	0006_require_contenttypes_0002	2026-09-29 11:08:02.803818+00
9	auth	0007_alter_validators_add_error_messages	2026-09-29 11:08:02.814205+00
10	auth	0008_alter_user_username_max_length	2026-09-29 11:08:02.822577+00
11	auth	0009_alter_user_last_name_max_length	2026-09-29 11:08:02.832354+00
12	auth	0010_alter_group_name_max_length	2026-09-29 11:08:02.843055+00
13	auth	0011_update_proxy_permissions	2026-09-29 11:08:02.852799+00
14	auth	0012_alter_user_first_name_max_length	2026-09-29 11:08:02.863034+00
15	dashboard	0001_initial	2026-09-29 11:08:03.132899+00
16	admin	0001_initial	2026-09-29 11:08:03.168732+00
17	admin	0002_logentry_remove_auto_add	2026-09-29 11:08:03.180453+00
18	admin	0003_logentry_add_action_flag_choices	2026-09-29 11:08:03.192063+00
19	sessions	0001_initial	2026-09-29 11:08:03.214933+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
7g56rjxg0cerk3l68n6nh0swzcej8fzs	.eJxVjDEKwzAMAP-iuRgrdoOVsXvfYCRbadIWG-JkCv17CWRo17vjdoi8rVPcmi5xzjAAwuWXCaeXlkPkJ5dHNamWdZnFHIk5bTP3mvV9O9u_wcRtggGsIitqQLEdcq-SQ0pjp4kZFa1XISJBEXJ6tWP2LgkJBRTvOuotfL4RIzim:1x5krO:6-_xsvO6O0kJ5kpjdBCorw4ZPGzVyU19NIvMQofI-5U	2026-09-27 14:07:10.232+00
7v1c1pp0iz7k3g2j4id12ix62f50d9n4	.eJxVjDEKwzAMAP-iuRgrdoOVsXvfYCRbadIWG-JkCv17CWRo17vjdoi8rVPcmi5xzjAAwuWXCaeXlkPkJ5dHNamWdZnFHIk5bTP3mvV9O9u_wcRtggGsIitqQLEdcq-SQ0pjp4kZFa1XISJBEXJ6tWP2LgkJBRTvOuotfL4RIzim:1xBVhg:twCr_isNtE3LATX_MRQ44FIKXoCnX8nfiEDR6I_Fpkk	2026-10-13 11:08:56.846132+00
\.


--
-- Data for Name: master_cr_database; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.master_cr_database (id, sno, ms_project, execution_date, maintenance_window, cr_no, priority, risk, region, circle, node_details, node_count, activity_description, bpms_cr_yes_no, planning_status, activity_executor, auditor_name, activity_status, reason_for_rollback_cancel, technical_validator, service_affecting, impact, test_cases, kpi_name, kpi_spoc_night, kpi_spoc_morning, inter_domain_activity, inter_domain_kpi_required, inter_domain_measuring_kpis, activity_type, vendor, protocol, execution_type, cli_availability, team, scheduled_start_date, scheduled_end_date, niam_ticket_required, niam_node_type, additional_info, is_active, version, parent_reference_id) FROM stdin;
1	1	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005578508	Medium	2-Significant/Large	East	KO		2	New Private APN entry in Ericsson DNS (Non-Live) in KOL DNS	No						Enjoy Maity	No						No	No		M2M : Migration of Private APN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
2	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR		11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
3	3	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005576882	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
4	4	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	Low	2-Significant/Large				105	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes						Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
5	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP		6	Domain whitelisting in data expire and throttle rules in EPGs	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
6	6	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	Low	2-Significant/Large	North	UPE		3	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No						Enjoy Maity	No						No	Yes	ERIC DRA KPIs	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
7	3	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005576882	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	planned					Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
8	4	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	Low	2-Significant/Large	South	TN		105	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes	planned					Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
9	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP		6	Domain whitelisting in data expire and throttle rules in EPGs	No	planned					Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
10	6	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	Low	2-Significant/Large	North	UPE		3	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	planned					Enjoy Maity	No						No	Yes	ERIC DRA KPIs	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
11	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR		11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	planned					Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
12	4	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	Low	2-Significant/Large	South	TN		105	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes	discussed					Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
13	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP	MPJBLCC02EREPGUP06,\nMPJBLRHCK01ERPCCSM06,\nMPJBLRHCK02ERPCCSM07,\nMPJBLRHCK02ERPCGUP07,\nMPJBLRHCK03ERPCCSM08,\nMPJBLRHCK03ERPCGUP08	6	Domain whitelisting in data expire and throttle rules in EPGs	No	planned					Enjoy Maity	Yes	SA in worst case Data services may impacted for 20-30 min	Testing: Basic testing to be done Node MPGVPRHCK01ERPCCSM01, MPGVPERCE01EREPGUP02, MPRPRERCE01EREPGCP03, MPRPRERCE01EREPGUP03, MPBHPCC02EREPG04, MPJBLCC01EREPGCP05 MPJBLCC01EREPGUP05 KPI GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GX_CCR_I SR_Combained GX_CCR_T SR_Combained GX_CCR_U SR_Combained GY_CCR_I SR_Combained GY_CCR_T SR_Combained GY_CCR_U SR_Combained				No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	9
14	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP	MPJBLCC02EREPGUP06,\nMPJBLRHCK01ERPCCSM06,\nMPJBLRHCK02ERPCCSM07,\nMPJBLRHCK02ERPCGUP07,\nMPJBLRHCK03ERPCCSM08,\nMPJBLRHCK03ERPCGUP08	6	Domain whitelisting in data expire and throttle rules in EPGs	No	planned					Enjoy Maity	Yes	SA in worst case Data services may impacted for 20-30 min	Testing: Basic testing to be done Node MPGVPRHCK01ERPCCSM01, MPGVPERCE01EREPGUP02, MPRPRERCE01EREPGCP03, MPRPRERCE01EREPGUP03, MPBHPCC02EREPG04, MPJBLCC01EREPGCP05 MPJBLCC01EREPGUP05 KPI GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GX_CCR_I SR_Combained GX_CCR_T SR_Combained GX_CCR_U SR_Combained GY_CCR_I SR_Combained GY_CCR_T SR_Combained GY_CCR_U SR_Combained				No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	9
15	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03,\nCK02.RH.AMB.HR,\nPBAMBCK02ERCCPCVOICE02,\nPBAMBCK02ERCCPCVOICE01	11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	planned					Enjoy Maity	Yes	SA,in worst case LTE/Volte/5G SA service may impact for 30 min	Normal Testing will done				No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	11
16	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03,\nCK02.RH.AMB.HR,\nPBAMBCK02ERCCPCVOICE02,\nPBAMBCK02ERCCPCVOICE01	11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	planned					Enjoy Maity	Yes	SA,in worst case LTE/Volte/5G SA service may impact for 30 min	Normal Testing will done				No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	11
50	22	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579193	Medium	2-Significant/Large	East	BH		2	Test number routing & Test APN configuration in PCCSM12 for Gi DNS Testing	No						Enjoy Maity	No						No	No		APN Creation/Deletion/Modification	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
51	23	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579184	High	1-Extensive/Widespread	East	OR		2	IR S6a traffic routing from H-DRA to Oracle DSR in CMM-1&2	No						Enjoy Maity	Yes						No	No		LBO Migration  related Changes	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
17	6	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	Low	2-Significant/Large	North	UPE	UEGANNA2CP02U06,\nUEGANNA2CP02,\nUEGANNA2CP02U05	3	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	planned					Enjoy Maity	No	NSA	Nodes- UEGANNA2CP02 2401:4900:24:1c00::bc0 UEGANNA2CP02U05 2401:4900:24:1c00::bca UEGANNA2CP02U06 2401:4900:24:1c00::bcc UEGANNA2CP02U07 2401:4900:24:1c00::bce "UEGANNA2CP02U19\t2401:4900:24:1c00::f00"  GGSN GX SR _Combained GGSN GY SR _Combained GGSN Bearer Creation SR _Combained GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR SMF KPIs / PDU Session Management Create Success Rate_5G_SA_Nokia Npcf SM Policy Control Create Success Rate Npcf SM Policy Control Update Success Rate PDU Throughput_Gbps_DNN_N3  Airtelfwamdu kpis Active EPS Bearers_APN_Max_APN_Airtelfwamdu (Y) Session_Activation_SR_APN_Airtelfwamdu (Y) 4G/Volte data testing Need to be done. IMS / BNG KPIs				No	Yes	ERIC DRA KPIs	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	10
18	6	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	Low	2-Significant/Large	North	UPE	UEGANNA2CP02U06,\nUEGANNA2CP02,\nUEGANNA2CP02U05	3	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	planned					Enjoy Maity	No	NSA	Nodes- UEGANNA2CP02 2401:4900:24:1c00::bc0 UEGANNA2CP02U05 2401:4900:24:1c00::bca UEGANNA2CP02U06 2401:4900:24:1c00::bcc UEGANNA2CP02U07 2401:4900:24:1c00::bce "UEGANNA2CP02U19\t2401:4900:24:1c00::f00"  GGSN GX SR _Combained GGSN GY SR _Combained GGSN Bearer Creation SR _Combained GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR SMF KPIs / PDU Session Management Create Success Rate_5G_SA_Nokia Npcf SM Policy Control Create Success Rate Npcf SM Policy Control Update Success Rate PDU Throughput_Gbps_DNN_N3  Airtelfwamdu kpis Active EPS Bearers_APN_Max_APN_Airtelfwamdu (Y) Session_Activation_SR_APN_Airtelfwamdu (Y) 4G/Volte data testing Need to be done. IMS / BNG KPIs				No	Yes	ERIC DRA KPIs	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	2	10
19	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP	MPJBLCC02EREPGUP06,\nMPJBLRHCK01ERPCCSM06,\nMPJBLRHCK02ERPCCSM07,\nMPJBLRHCK02ERPCGUP07,\nMPJBLRHCK03ERPCCSM08,\nMPJBLRHCK03ERPCGUP08	6	Domain whitelisting in data expire and throttle rules in EPGs	No	planned					Enjoy Maity	Yes	SA in worst case Data services may impacted for 20-30 min	Testing: Basic testing to be done Node MPGVPRHCK01ERPCCSM01, MPGVPERCE01EREPGUP02, MPRPRERCE01EREPGCP03, MPRPRERCE01EREPGUP03, MPBHPCC02EREPG04, MPJBLCC01EREPGCP05 MPJBLCC01EREPGUP05 KPI GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GX_CCR_I SR_Combained GX_CCR_T SR_Combained GX_CCR_U SR_Combained GY_CCR_I SR_Combained GY_CCR_T SR_Combained GY_CCR_U SR_Combained				No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	3	14
20	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP	MPJBLCC02EREPGUP06,\nMPJBLRHCK01ERPCCSM06,\nMPJBLRHCK02ERPCCSM07,\nMPJBLRHCK02ERPCGUP07,\nMPJBLRHCK03ERPCCSM08,\nMPJBLRHCK03ERPCGUP08	6	Domain whitelisting in data expire and throttle rules in EPGs	No	planned					Enjoy Maity	Yes	SA in worst case Data services may impacted for 20-30 min	Testing: Basic testing to be done Node MPGVPRHCK01ERPCCSM01, MPGVPERCE01EREPGUP02, MPRPRERCE01EREPGCP03, MPRPRERCE01EREPGUP03, MPBHPCC02EREPG04, MPJBLCC01EREPGCP05 MPJBLCC01EREPGUP05 KPI GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GX_CCR_I SR_Combained GX_CCR_T SR_Combained GX_CCR_U SR_Combained GY_CCR_I SR_Combained GY_CCR_T SR_Combained GY_CCR_U SR_Combained				No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	3	14
21	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03,\nCK02.RH.AMB.HR,\nPBAMBCK02ERCCPCVOICE02,\nPBAMBCK02ERCCPCVOICE01	11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	planned					Enjoy Maity	Yes	SA,in worst case LTE/Volte/5G SA service may impact for 30 min	Normal Testing will done				No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	3	16
22	2	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005577326	High	1-Extensive/Widespread	North	HR	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03,\nCK02.RH.AMB.HR,\nPBAMBCK02ERCCPCVOICE02,\nPBAMBCK02ERCCPCVOICE01	11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No	planned					Enjoy Maity	Yes	SA,in worst case LTE/Volte/5G SA service may impact for 30 min	Normal Testing will done				No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	3	16
23	1	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005578508	Medium	2-Significant/Large	East	KO		2	New Private APN entry in Ericsson DNS (Non-Live) in KOL DNS	No	planned					Enjoy Maity	No						No	No		M2M : Migration of Private APN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	1	\N
24	4	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	Low	2-Significant/Large	South	TN		105	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes	planned					Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				f	1	\N
25	3	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005576882	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes	discussed					Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	1	\N
26	6	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005543609	Low	2-Significant/Large	North	UPE	UEGANNA2CP02U06,\nUEGANNA2CP02,\nUEGANNA2CP02U05	3	Lock / unlock IP  for new IP Pool testing MG Wise for airtelfwamdu in UEGANNA2CP02(UPF05/06)	No	discussed					Enjoy Maity	No	NSA	Nodes- UEGANNA2CP02 2401:4900:24:1c00::bc0 UEGANNA2CP02U05 2401:4900:24:1c00::bca UEGANNA2CP02U06 2401:4900:24:1c00::bcc UEGANNA2CP02U07 2401:4900:24:1c00::bce "UEGANNA2CP02U19\t2401:4900:24:1c00::f00"  GGSN GX SR _Combained GGSN GY SR _Combained GGSN Bearer Creation SR _Combained GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR SMF KPIs / PDU Session Management Create Success Rate_5G_SA_Nokia Npcf SM Policy Control Create Success Rate Npcf SM Policy Control Update Success Rate PDU Throughput_Gbps_DNN_N3  Airtelfwamdu kpis Active EPS Bearers_APN_Max_APN_Airtelfwamdu (Y) Session_Activation_SR_APN_Airtelfwamdu (Y) 4G/Volte data testing Need to be done. IMS / BNG KPIs				No	Yes	ERIC DRA KPIs	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	2	10
27	5	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005574908	Low	1-Extensive/Widespread	West	MP	MPJBLCC02EREPGUP06,\nMPJBLRHCK01ERPCCSM06,\nMPJBLRHCK02ERPCCSM07,\nMPJBLRHCK02ERPCGUP07,\nMPJBLRHCK03ERPCCSM08,\nMPJBLRHCK03ERPCGUP08	6	Domain whitelisting in data expire and throttle rules in EPGs	No	discussed					Enjoy Maity	Yes	SA in worst case Data services may impacted for 20-30 min	Testing: Basic testing to be done Node MPGVPRHCK01ERPCCSM01, MPGVPERCE01EREPGUP02, MPRPRERCE01EREPGCP03, MPRPRERCE01EREPGUP03, MPBHPCC02EREPG04, MPJBLCC01EREPGCP05 MPJBLCC01EREPGUP05 KPI GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GX_CCR_I SR_Combained GX_CCR_T SR_Combained GX_CCR_U SR_Combained GY_CCR_I SR_Combained GY_CCR_T SR_Combained GY_CCR_U SR_Combained				No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	3	14
28	4	MS	2026-09-12	00:00:00 - 06:00:00	CRQ000005575594	Low	2-Significant/Large	South	TN		105	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes	discussed					Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-11 18:30:00+00	2026-09-12 00:30:00+00				t	1	\N
29	1	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005581184	High	1-Extensive/Widespread	North			5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
30	2	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005581091	High	1-Extensive/Widespread	North			5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
31	3	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580439	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
32	4	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580438	Low	1-Extensive/Widespread	West	MP		3	M2M APN sugslloyd.iot Gateway Change in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
33	5	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580375	High	2-Significant/Large	North	DL		2	M2M-CR for non-live M2M APN(sugslloyd.iot.m2m) DNS entry in DL DNS with Cache clear	No						Enjoy Maity	No						Yes	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
34	6	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579815	High	1-Extensive/Widespread	South	AP		10	Traffic diversion from Ericsson MMEs & Revertback for vIPWorks DNS 2.13 Update in APVIJEDNS03	No						Enjoy Maity	Yes						Yes	No		Traffic diversions	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
35	7	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579756	Low	2-Significant/Large				250	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes						Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
36	8	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579521	Critical	1-Extensive/Widespread	East	BH		10	Domain whitelisting in data expire and throttle rules in PCCSM	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
37	9	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579518	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
38	10	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579516	Critical	1-Extensive/Widespread	South	AP		3	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
39	11	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579503	Critical	1-Extensive/Widespread	East	WB		3	Domain whitelisting in data expire and throttle rules in PCGUP05, ROBKGPEPG02	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
40	12	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579280	High	1-Extensive/Widespread	West	RJ		11	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
41	13	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579274	Medium	2-Significant/Large	East	OR		4	IR IMSI definition in Nokia MME	No						Enjoy Maity	No						No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
42	14	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579268	High	1-Extensive/Widespread	East	WB		4	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				VAS	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
43	15	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579259	High	2-Significant/Large	South	AP		3	BRM and SP backup for IPWorks version update to 2.13 in AP DNS APVIJEDNS03	No						Enjoy Maity	No						Yes	No		Patch Update Prerequisite	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
44	16	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579249	High	1-Extensive/Widespread	East	NE		1	CR for PWS & CTUM learning Implementation in NEGUWRHCC01ERMME02	No						Enjoy Maity	Yes						Yes	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
45	17	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579241	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
46	18	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579226	High	1-Extensive/Widespread	East	NE		6	RMC value changes and revert back NE E// MMEs for NEGUWRHCC01ERMME02 update	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in MME due to Software Update	Ericsson/Nokia/DELL				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
47	19	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579212	High	1-Extensive/Widespread	West	MU		1	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No						Enjoy Maity	Yes						No	No		Subs. purging M2M	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
48	20	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579204	Critical	1-Extensive/Widespread	North	UPW		5	CMM gParm modify for traffic offload in Nokia CMMs as part of in UWMORCK02NCMM03	No						Enjoy Maity	Yes						Yes	Yes	RAN KPI	Parameter Definition/Changes MME/GGSN/EPDG/WMG	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
49	21	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579197	Critical	1-Extensive/Widespread	West	RJ		13	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
52	24	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579182	High	1-Extensive/Widespread	West	MH		3	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
53	25	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579180	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
54	26	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579173	Critical	1-Extensive/Widespread	South	AP		3	vIPWorks Version Update  to 2.13 in AP DNS APVIJEDNS03	No						Enjoy Maity	Yes						Yes	Yes	IMS/DRA KPI	Software Update in DNS	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
55	27	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579169	High	2-Significant/Large	South	AP		3	S/W Package Loading for IPWorks version update to 2.13 in APVIJEDNS03	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Nokia/HP/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
56	28	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579166	Critical	1-Extensive/Widespread	East	WB		6	Network Name configuration in all ROB MME and PCCMM	No						Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
57	29	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579165	High	1-Extensive/Widespread	East	NE		4	CR_MME Update from 1.84 to 1.91 in NEGUWRHCC01ERMME02	No						Enjoy Maity	Yes						Yes	Yes		Software Update in MME (CiscO///21.28.M41)	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
58	30	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579161	High	2-Significant/Large	East	BH		4	Integration of GMLC & SMLC with new PCCMME10.	No						Enjoy Maity	No						No	No		MME Integration in SMPC	Ericsson				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
59	31	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579154	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
60	32	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579150	Medium	2-Significant/Large	East	NE		4	CR_Package loading for MME 1.91 Update in NEGUWRHCC01ERMME02	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
61	33	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579140	High	2-Significant/Large	North	UPW		2	PBI000000269790:Alarm_Certificate Management, the Certificate is to Expire	No						Enjoy Maity	No						No	Yes	IMS/DRA KPI	New Learning implementation in SAPC	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
62	34	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579137	Critical	1-Extensive/Widespread	North	UPW		10	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
63	35	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579125	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
64	36	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579121	Low	1-Extensive/Widespread	West	MP		3	M2M APN migration in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
65	37	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579119	Low	1-Extensive/Widespread	West	MP		5	SOS APN Routing Removal from GGSN02	No						Enjoy Maity	Yes						No	No		APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
66	38	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579114	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
67	39	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579108	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
68	40	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579101	Critical	1-Extensive/Widespread	West	RJ		2	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Ericsson				VAS	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				f	1	\N
69	41	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578993	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 5G SA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
70	42	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578982	Low	1-Extensive/Widespread	West	MP		3	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No						Enjoy Maity	Yes						Yes	No		Top-on Implementation	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
71	43	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578981	Medium	2-Significant/Large	North	UPW		5	PBI000000269363: 3 Learning implementation in UWN81NAAA01	No						Enjoy Maity	No						No	No		Learning implementation in CPAR	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
72	44	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578971	Medium	2-Significant/Large	East	NE		3	CR_Pre/Post BRM Backup for NEGUWRHCC01ERMME02 SW update	No						Enjoy Maity	No						Yes	No		Backup	Ericsson/Nokia/Dell/HP				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
73	45	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578964	High	1-Extensive/Widespread	South	TN		8	TNSERRHCK10ERPCCSM12 || NRF registration & whitelisting at NRF end	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
74	46	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578952	High	1-Extensive/Widespread	North	PB		8	TOPON wtg changes in PB Nokia DNS for HR GPOD1 entries removal & cache clear in MME.	No						Enjoy Maity	Yes						No	No		Top-On Weightage Changes  in DNS	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
75	47	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578912	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
76	48	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578795	Low	1-Extensive/Widespread	West	MP		5	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
228	29	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580547	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
77	49	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578775	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
78	50	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578589	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
79	51	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578539	Low	1-Extensive/Widespread	North	UPE		4	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-2	No						Enjoy Maity	No						No	Yes	IMS , Nokia , Eric DRA KPIs	FQDN Configuration in PCRF	Ericsson				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
80	52	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578494	High	1-Extensive/Widespread	East	NE		6	Subscribers movement in E\\\\ MMEs via Pool Move for NEGUWRHCC01ERMME02  update	No						Enjoy Maity	Yes						Yes	No		Subs.  Purging due to Software Update	Ericsson/Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
81	53	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578485	Critical	1-Extensive/Widespread	North	DL		2	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
82	54	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578452	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
83	55	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578415	Critical	1-Extensive/Widespread	North	DL		47	IMSI purging from all DL SPG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No						Enjoy Maity	Yes						Yes	Yes	IMS,OR DRA, SCP KPI	Subs. Purging due to Other Dependent Activities	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
84	56	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578393	Critical	1-Extensive/Widespread	West	RJ		24	CR for MIP6 FQDN Definition at DNS end for CP08 and 09 With Cache clear	No						Enjoy Maity	Yes						No	No		New Nokia CMG related Configuration	Cisco/Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
85	57	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578392	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
86	58	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578374	High	1-Extensive/Widespread	North	HR		5	CMM gParam modify for traffic Balancing in HR Nokia CMMs as part of HRLUDCK02NCMM02 upgrade	No						Enjoy Maity	Yes						Yes	No		Subs. offloading from  MME	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
87	59	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578366	High	1-Extensive/Widespread	North	HR		5	Pre-post RC wt changes in HR CMM's/AMF's  for HRLUDCK02NCMM02 offloading/revert during upgrade	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
88	60	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578355	Low	2-Significant/Large	North	UPE		12	Gateway IP change for APN  & Non live APN defn in Nokia  DNS	No						Enjoy Maity	No						Yes	No		DNS entry addition of new APN-M2M	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
89	61	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578351	Low	2-Significant/Large	North	UPE		12	Gateway IP change for APN  & Non live APN defn in Cisco  DNS	No						Enjoy Maity	No						Yes	No		DNS entry addition of new APN-M2M	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
90	62	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578346	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
91	63	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578313	Critical	1-Extensive/Widespread	North	DL		2	IMSI purging from all DL WMG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No						Enjoy Maity	Yes						Yes	Yes	IMS,OR DRA, SCP KPI	Subs. Purging due to Other Dependent Activities	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
92	64	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577456	Medium	2-Significant/Large	East	BH		9	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
93	65	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577389	Low	1-Extensive/Widespread	North	UPE		15	UNUSSED APN deletion in Nokia CP02,CP05 & CP06	No						Enjoy Maity	No						No	No		APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
94	66	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577305	High	1-Extensive/Widespread	West	MH		3	S10 Entry of MPBHPEMME01 remove from MAH DNSs	No						Enjoy Maity	Yes						Yes	Yes		S10 Entry Addition/Deletion/Modification in DNS	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
95	67	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005576956	Medium	2-Significant/Large	East	BH		5	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
96	68	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005576953	Medium	2-Significant/Large	East	OR		4	BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
97	69	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	High	1-Extensive/Widespread	North	UPW		5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	Yes		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
98	70	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575963	Low	1-Extensive/Widespread	West	GJ		2	PCCSM05 & PCGUP05 LBO Traffic Loading Balancing from GUJ Ericsson DNSs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
99	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ		6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No						Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
100	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE		3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No						Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
101	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH		8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
102	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW		8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
103	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ		6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	planned					Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
104	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE		3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	planned					Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
105	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH		8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	planned					Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
106	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW		8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	planned					Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
107	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW	UWMORNCMM02,\nUWNOINCMM01,\nUWNOINDNSN02,\nUWNOINDNSN01,\nUWMORCK02NCMM03,\nUWMORCK03NCMM04,\nUWGNGCK01NCMM05,\nUWGNGCK02NCMM06	8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	planned					Enjoy Maity	Yes	SA-M2M services for migrated APN may be impacted for 30 min	Normal testing				No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	106
108	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW	UWMORNCMM02,\nUWNOINCMM01,\nUWNOINDNSN02,\nUWNOINDNSN01,\nUWMORCK02NCMM03,\nUWMORCK03NCMM04,\nUWGNGCK01NCMM05,\nUWGNGCK02NCMM06	8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	planned					Enjoy Maity	Yes	SA-M2M services for migrated APN may be impacted for 30 min	Normal testing				No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	106
109	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03	8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	planned					Enjoy Maity	Yes	Impact-SA in worst case 30 Mins Voice/Data services may be impacted	Testing: Basic MO/MT Volte call & data Testing will perform				No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	105
110	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH	BASTION01.CK04.RH.MAN.HR,\nBASTION01.CK01.RH.SER.TN,\nDLMANRHCK04ERCCRCR01,\nCHSERRHCK01ERCCRCR02,\nBASTION.CK03.RH.INT.KO,\nBASTION.CK02.RH.CHD.MU,\nMUCHDRHCK02ERCCRCR04,\nKOINTRHCK03ERCCRCR03	8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	planned					Enjoy Maity	Yes	Impact-SA in worst case 30 Mins Voice/Data services may be impacted	Testing: Basic MO/MT Volte call & data Testing will perform				No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	105
111	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE	UEVARNCMM02,\nUEGANNCMM01,\nUEGANCK02NCMM05	3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	planned					Enjoy Maity	Yes	SA, In worst case voice and data services may be impacted for 30 mins	Nodes- UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5 SA, In worst case voice and data services may be impacted for 30 mins KPI & Testing - UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5  ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session -ERAB_Modification_SR_E AMF: UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 Initial Registration Success Rate_5G_SA_Nokia Inter AMF Mobility Registration Success Rate_5G_SA_Nokia Registered Subscriber__5G_SA_Nokia Service Request Success Rate_5G_SA_Nokia Basic testing to be done				No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	104
112	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE	UEVARNCMM02,\nUEGANNCMM01,\nUEGANCK02NCMM05	3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	planned					Enjoy Maity	Yes	SA, In worst case voice and data services may be impacted for 30 mins	Nodes- UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5 SA, In worst case voice and data services may be impacted for 30 mins KPI & Testing - UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5  ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session -ERAB_Modification_SR_E AMF: UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 Initial Registration Success Rate_5G_SA_Nokia Inter AMF Mobility Registration Success Rate_5G_SA_Nokia Registered Subscriber__5G_SA_Nokia Service Request Success Rate_5G_SA_Nokia Basic testing to be done				No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	104
126	5	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580375	High	2-Significant/Large	North	DL		2	M2M-CR for non-live M2M APN(sugslloyd.iot.m2m) DNS entry in DL DNS with Cache clear	No						Enjoy Maity	No						Yes	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	33
127	6	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579815	High	1-Extensive/Widespread	South	AP		10	Traffic diversion from Ericsson MMEs & Revertback for vIPWorks DNS 2.13 Update in APVIJEDNS03	No						Enjoy Maity	Yes						Yes	No		Traffic diversions	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	34
128	7	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579756	Low	2-Significant/Large				250	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Yes						Enjoy Maity	No						No	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	35
113	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ	GUJRAJEMME03,\nGUJCHAEMME04,\nGUJCHAEMME02,\nGUJRAJEMME01,\nGJCHARHCK01ERPCCMM05,\nGJRAJRHCK01ERPCCMM06	6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	planned					Enjoy Maity	Yes	SA (5-10 Min Volte / Data service may impact in worst case)	Testing/KPI :Pre & post testing required. GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 KPI - -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined - ERAB Modification SR ( Ericsson and Nokia both )  5G(NSA) KPIs - Node level - 5G SAU ( Eric , Nokia ) & attached-dcnr-subscriber (Cisco) - 5G Active Session ( Eric - MME & PCCMM ) - ERAB_Modification_SR_E (MME & PCCMM) GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 KPI - GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Nodes: GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 Google team aligned				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	103
114	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ	GUJRAJEMME03,\nGUJCHAEMME04,\nGUJCHAEMME02,\nGUJRAJEMME01,\nGJCHARHCK01ERPCCMM05,\nGJRAJRHCK01ERPCCMM06	6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	planned					Enjoy Maity	Yes	SA (5-10 Min Volte / Data service may impact in worst case)	Testing/KPI :Pre & post testing required. GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 KPI - -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined - ERAB Modification SR ( Ericsson and Nokia both )  5G(NSA) KPIs - Node level - 5G SAU ( Eric , Nokia ) & attached-dcnr-subscriber (Cisco) - 5G Active Session ( Eric - MME & PCCMM ) - ERAB_Modification_SR_E (MME & PCCMM) GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 KPI - GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Nodes: GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 Google team aligned				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	103
115	70	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575963	Low	1-Extensive/Widespread	West	GJ		2	PCCSM05 & PCGUP05 LBO Traffic Loading Balancing from GUJ Ericsson DNSs	No	planned					Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	1	\N
116	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW	UWMORNCMM02,\nUWNOINCMM01,\nUWNOINDNSN02,\nUWNOINDNSN01,\nUWMORCK02NCMM03,\nUWMORCK03NCMM04,\nUWGNGCK01NCMM05,\nUWGNGCK02NCMM06	8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	unplanned					Enjoy Maity	Yes	SA-M2M services for migrated APN may be impacted for 30 min	Normal testing				No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	106
117	69	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	High	1-Extensive/Widespread	North	UPW		5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes	planned					Enjoy Maity	Yes						No	Yes		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
118	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ	GUJRAJEMME03,\nGUJCHAEMME04,\nGUJCHAEMME02,\nGUJRAJEMME01,\nGJCHARHCK01ERPCCMM05,\nGJRAJRHCK01ERPCCMM06	6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	unplanned					Enjoy Maity	Yes	SA (5-10 Min Volte / Data service may impact in worst case)	Testing/KPI :Pre & post testing required. GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 KPI - -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined - ERAB Modification SR ( Ericsson and Nokia both )  5G(NSA) KPIs - Node level - 5G SAU ( Eric , Nokia ) & attached-dcnr-subscriber (Cisco) - 5G Active Session ( Eric - MME & PCCMM ) - ERAB_Modification_SR_E (MME & PCCMM) GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 KPI - GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Nodes: GUJRAJEMME01,GUJCHAEMME02,GUJRAJEMME03,GUJCHAEMME04,GJCHARHCK01ERPCCMM05,GJRAJRHCK01ERPCCMM06 Google team aligned				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	103
119	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE	UEVARNCMM02,\nUEGANNCMM01,\nUEGANCK02NCMM05	3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No						Enjoy Maity	Yes	SA, In worst case voice and data services may be impacted for 30 mins	Nodes- UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5 SA, In worst case voice and data services may be impacted for 30 mins KPI & Testing - UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 UEGANCK02NCMM05---2401:4900:24:1c7a::5  ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session -ERAB_Modification_SR_E AMF: UEGANNCMM01---2401:4900:24:1c0c::5 UEVARNCMM02---2401:4900:24:1f1a::5 Initial Registration Success Rate_5G_SA_Nokia Inter AMF Mobility Registration Success Rate_5G_SA_Nokia Registered Subscriber__5G_SA_Nokia Service Request Success Rate_5G_SA_Nokia Basic testing to be done				No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	104
120	69	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	High	1-Extensive/Widespread	North	UPW		5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	Yes		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
121	69	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	High	1-Extensive/Widespread	North	UPW		5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes	unplanned					Enjoy Maity	Yes						No	Yes		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				f	1	\N
122	1	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005581184	High	1-Extensive/Widespread	North			5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	29
123	2	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005581091	High	1-Extensive/Widespread	North			5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	30
124	3	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580439	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	31
125	4	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005580438	Low	1-Extensive/Widespread	West	MP		3	M2M APN sugslloyd.iot Gateway Change in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	32
129	8	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579521	Critical	1-Extensive/Widespread	East	BH		10	Domain whitelisting in data expire and throttle rules in PCCSM	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	36
130	9	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579518	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	37
131	10	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579516	Critical	1-Extensive/Widespread	South	AP		3	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	38
132	11	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579503	Critical	1-Extensive/Widespread	East	WB		3	Domain whitelisting in data expire and throttle rules in PCGUP05, ROBKGPEPG02	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	39
133	12	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579280	High	1-Extensive/Widespread	West	RJ		11	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	40
134	13	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579274	Medium	2-Significant/Large	East	OR		4	IR IMSI definition in Nokia MME	No						Enjoy Maity	No						No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	41
135	14	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579268	High	1-Extensive/Widespread	East	WB		4	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				VAS	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	42
136	15	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579259	High	2-Significant/Large	South	AP		3	BRM and SP backup for IPWorks version update to 2.13 in AP DNS APVIJEDNS03	No						Enjoy Maity	No						Yes	No		Patch Update Prerequisite	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	43
137	16	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579249	High	1-Extensive/Widespread	East	NE		1	CR for PWS & CTUM learning Implementation in NEGUWRHCC01ERMME02	No						Enjoy Maity	Yes						Yes	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	44
138	17	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579241	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	45
139	18	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579226	High	1-Extensive/Widespread	East	NE		6	RMC value changes and revert back NE E// MMEs for NEGUWRHCC01ERMME02 update	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in MME due to Software Update	Ericsson/Nokia/DELL				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	46
140	19	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579212	High	1-Extensive/Widespread	West	MU		1	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No						Enjoy Maity	Yes						No	No		Subs. purging M2M	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	47
141	20	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579204	Critical	1-Extensive/Widespread	North	UPW		5	CMM gParm modify for traffic offload in Nokia CMMs as part of in UWMORCK02NCMM03	No						Enjoy Maity	Yes						Yes	Yes	RAN KPI	Parameter Definition/Changes MME/GGSN/EPDG/WMG	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	48
142	21	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579197	Critical	1-Extensive/Widespread	West	RJ		13	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	49
143	22	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579193	Medium	2-Significant/Large	East	BH		2	Test number routing & Test APN configuration in PCCSM12 for Gi DNS Testing	No						Enjoy Maity	No						No	No		APN Creation/Deletion/Modification	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	50
144	23	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579184	High	1-Extensive/Widespread	East	OR		2	IR S6a traffic routing from H-DRA to Oracle DSR in CMM-1&2	No						Enjoy Maity	Yes						No	No		LBO Migration  related Changes	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	51
145	24	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579182	High	1-Extensive/Widespread	West	MH		3	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	52
146	25	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579180	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	53
147	26	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579173	Critical	1-Extensive/Widespread	South	AP		3	vIPWorks Version Update  to 2.13 in AP DNS APVIJEDNS03	No						Enjoy Maity	Yes						Yes	Yes	IMS/DRA KPI	Software Update in DNS	Ericsson				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	54
148	27	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579169	High	2-Significant/Large	South	AP		3	S/W Package Loading for IPWorks version update to 2.13 in APVIJEDNS03	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Nokia/HP/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	55
149	28	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579166	Critical	1-Extensive/Widespread	East	WB		6	Network Name configuration in all ROB MME and PCCMM	No						Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	56
150	29	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579165	High	1-Extensive/Widespread	East	NE		4	CR_MME Update from 1.84 to 1.91 in NEGUWRHCC01ERMME02	No						Enjoy Maity	Yes						Yes	Yes		Software Update in MME (CiscO///21.28.M41)	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	57
151	30	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579161	High	2-Significant/Large	East	BH		4	Integration of GMLC & SMLC with new PCCMME10.	No						Enjoy Maity	No						No	No		MME Integration in SMPC	Ericsson				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	58
152	31	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579154	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	59
153	32	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005579150	Medium	2-Significant/Large	East	NE		4	CR_Package loading for MME 1.91 Update in NEGUWRHCC01ERMME02	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Nokia/Dell				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	60
154	33	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579140	High	2-Significant/Large	North	UPW		2	PBI000000269790:Alarm_Certificate Management, the Certificate is to Expire	No						Enjoy Maity	No						No	Yes	IMS/DRA KPI	New Learning implementation in SAPC	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	61
155	34	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579137	Critical	1-Extensive/Widespread	North	UPW		10	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	62
156	35	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579125	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	63
157	36	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579121	Low	1-Extensive/Widespread	West	MP		3	M2M APN migration in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	64
158	37	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579119	Low	1-Extensive/Widespread	West	MP		5	SOS APN Routing Removal from GGSN02	No						Enjoy Maity	Yes						No	No		APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	65
159	38	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579114	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	66
160	39	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005579108	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	67
161	40	MS	2026-09-15	23:00:00 - 06:00:00	CRQ000005579101	Critical	1-Extensive/Widespread	West	RJ		2	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Ericsson				VAS	2026-09-14 17:30:00+00	2026-09-15 00:30:00+00				t	2	68
162	41	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578993	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 5G SA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	69
163	42	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578982	Low	1-Extensive/Widespread	West	MP		3	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No						Enjoy Maity	Yes						Yes	No		Top-on Implementation	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	70
164	43	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578981	Medium	2-Significant/Large	North	UPW		5	PBI000000269363: 3 Learning implementation in UWN81NAAA01	No						Enjoy Maity	No						No	No		Learning implementation in CPAR	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	71
165	44	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578971	Medium	2-Significant/Large	East	NE		3	CR_Pre/Post BRM Backup for NEGUWRHCC01ERMME02 SW update	No						Enjoy Maity	No						Yes	No		Backup	Ericsson/Nokia/Dell/HP				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	72
166	45	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578964	High	1-Extensive/Widespread	South	TN		8	TNSERRHCK10ERPCCSM12 || NRF registration & whitelisting at NRF end	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	73
167	46	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578952	High	1-Extensive/Widespread	North	PB		8	TOPON wtg changes in PB Nokia DNS for HR GPOD1 entries removal & cache clear in MME.	No						Enjoy Maity	Yes						No	No		Top-On Weightage Changes  in DNS	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	74
168	47	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578912	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	75
169	48	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578795	Low	1-Extensive/Widespread	West	MP		5	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	2	76
170	49	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578775	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	77
171	50	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578589	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	78
172	51	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578539	Low	1-Extensive/Widespread	North	UPE		4	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-2	No						Enjoy Maity	No						No	Yes	IMS , Nokia , Eric DRA KPIs	FQDN Configuration in PCRF	Ericsson				VAS	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	79
173	52	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578494	High	1-Extensive/Widespread	East	NE		6	Subscribers movement in E\\\\ MMEs via Pool Move for NEGUWRHCC01ERMME02  update	No						Enjoy Maity	Yes						Yes	No		Subs.  Purging due to Software Update	Ericsson/Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	80
174	53	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578485	Critical	1-Extensive/Widespread	North	DL		2	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	81
175	54	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578452	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	82
176	55	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578415	Critical	1-Extensive/Widespread	North	DL		47	IMSI purging from all DL SPG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No						Enjoy Maity	Yes						Yes	Yes	IMS,OR DRA, SCP KPI	Subs. Purging due to Other Dependent Activities	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	83
177	56	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578393	Critical	1-Extensive/Widespread	West	RJ		24	CR for MIP6 FQDN Definition at DNS end for CP08 and 09 With Cache clear	No						Enjoy Maity	Yes						No	No		New Nokia CMG related Configuration	Cisco/Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	84
178	57	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578392	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	85
179	58	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578374	High	1-Extensive/Widespread	North	HR		5	CMM gParam modify for traffic Balancing in HR Nokia CMMs as part of HRLUDCK02NCMM02 upgrade	No						Enjoy Maity	Yes						Yes	No		Subs. offloading from  MME	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	86
180	59	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005578366	High	1-Extensive/Widespread	North	HR		5	Pre-post RC wt changes in HR CMM's/AMF's  for HRLUDCK02NCMM02 offloading/revert during upgrade	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	87
181	60	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578355	Low	2-Significant/Large	North	UPE		12	Gateway IP change for APN  & Non live APN defn in Nokia  DNS	No						Enjoy Maity	No						Yes	No		DNS entry addition of new APN-M2M	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	88
182	61	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578351	Low	2-Significant/Large	North	UPE		12	Gateway IP change for APN  & Non live APN defn in Cisco  DNS	No						Enjoy Maity	No						Yes	No		DNS entry addition of new APN-M2M	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	89
183	62	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578346	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	90
184	63	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005578313	Critical	1-Extensive/Widespread	North	DL		2	IMSI purging from all DL WMG's regard IMSI-40410059 Migration from SAPC Pair2 to DLCCPC-V Pair-1	No						Enjoy Maity	Yes						Yes	Yes	IMS,OR DRA, SCP KPI	Subs. Purging due to Other Dependent Activities	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	91
185	64	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577456	Medium	2-Significant/Large	East	BH		9	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	92
186	65	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577389	Low	1-Extensive/Widespread	North	UPE		15	UNUSSED APN deletion in Nokia CP02,CP05 & CP06	No						Enjoy Maity	No						No	No		APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	93
187	66	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005577305	High	1-Extensive/Widespread	West	MH		3	S10 Entry of MPBHPEMME01 remove from MAH DNSs	No						Enjoy Maity	Yes						Yes	Yes		S10 Entry Addition/Deletion/Modification in DNS	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	94
188	67	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005576956	Medium	2-Significant/Large	East	BH		5	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	95
189	68	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005576953	Medium	2-Significant/Large	East	OR		4	BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Cisco MME 5G IR LTE IR/VOLTE Launch - E2E	Cisco				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	96
190	69	MS	2026-09-15	23:00:00 - 07:00:00	CRQ000005576939	High	1-Extensive/Widespread	North	UPW		5	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	Yes		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-14 17:30:00+00	2026-09-15 01:30:00+00				t	2	121
191	70	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575963	Low	1-Extensive/Widespread	West	GJ		2	PCCSM05 & PCGUP05 LBO Traffic Loading Balancing from GUJ Ericsson DNSs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	2	115
192	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ		6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No						Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	3	118
193	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE		3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No						Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	3	119
194	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH		8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	3	110
195	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW		8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				f	3	116
196	71	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575862	Low	1-Extensive/Widespread	West	GJ		6	GCAP Value Change in Eric MME/MM to Traffic Loading on PCCSM05/PCGUP05	No	planned					Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	3	118
197	72	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005575213	Low	1-Extensive/Widespread	North	UPE		3	CR for Network Name configuration to “airtel” for Airtel PLMN only in all Nokia CMMs	No	planned					Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	3	119
198	73	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005574804	High	1-Extensive/Widespread	West	MH		8	CR for Non-Live SMF Instance ID Registration Post Verification for new PCCSM12	No	planned					Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP/IBM				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	3	110
199	74	MS	2026-09-15	00:00:00 - 06:00:00	CRQ000005506768	Critical	1-Extensive/Widespread	North	UPW		8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No	planned					Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-14 18:30:00+00	2026-09-15 00:30:00+00				t	3	116
200	1	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005581678	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
201	2	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005581101	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
202	3	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580869	High	1-Extensive/Widespread	West	RJ		11	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03 and cache clear at MME(Cisco)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
203	4	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580868	Critical	1-Extensive/Widespread	West	RJ		13	APN migration from mumspecc02erm2mepg04 to MHKHRNM2MCP03  and cache clear at MME(Nokia)	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
204	5	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580865	High	1-Extensive/Widespread	South	AP		2	PBI000000269790: learning for Alarm_Certificate Management Certificate is to Expire in AP SAPC Pair1	No						Enjoy Maity	Yes						No	No	IMS/Oracle DRA	New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
205	6	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580864	Critical	1-Extensive/Widespread	South	AP		3	Migration of APN:-gen.msedcl11.wbiot to MHKHRNM2MCP03 in AP E// DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
206	7	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580849	High	1-Extensive/Widespread	East	OR		6	New SMF ID &GW HN definition in CCPC Pair-3&4	No						Enjoy Maity	Yes						No	No		Host name addition in SAPC	Ericsson/Nokia/Cisco/Huawei/Dell/HP/IBM				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
207	8	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580821	High	1-Extensive/Widespread	North	HR		8	TOPON wtg changes in HR Nokia DNS for HR GPOD1 entries removal & cache clear in MME	No						Enjoy Maity	Yes						No	No		Top-On Weightage Changes  in DNS	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
208	9	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580817	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK CISCO DNS & Cache Clear in MMEs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Cisco				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
209	10	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580810	Low	1-Extensive/Widespread	West	MP		3	M2M APN migration in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
210	11	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580808	Low	1-Extensive/Widespread	West	MP		5	SOS APN Routing Removal from GGSN02	No						Enjoy Maity	Yes						No	No		APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
211	12	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580804	Low	1-Extensive/Widespread	West	MP		3	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No						Enjoy Maity	Yes						Yes	No		Top-on Implementation	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
212	13	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580803	High	2-Significant/Large	North	UPW		8	CR for Non-Live M2M APN definition in NOKIA DNS	No						Enjoy Maity	No						No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
213	14	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580796	High	1-Extensive/Widespread	South	KK		2	PBI000000269790: Alarm_Certificate Management, the Certificate is to Expire in KK SAPC Pair2	No						Enjoy Maity	Yes						No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
214	15	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580792	High	2-Significant/Large	South	KK		2	Multiple M2M Private APN Entry in Ericsson DNS (Non-Live)	No						Enjoy Maity	No						Yes	No		Private APN DNS Entry -NonLive	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
215	16	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580791	High	1-Extensive/Widespread	South	KK		1	SBc interface integration for CBC in KKMANGEMME04	No						Enjoy Maity	Yes						No	No	No testing & No KPI required for cache clear IP resolution need to check	New Ericsson MME related Configuration	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
216	17	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580788	Critical	1-Extensive/Widespread	West	RJ		2	CR for Gx event trigger suppression in Nokia JAICMG01 and CP02	No						Enjoy Maity	Yes						No	No		New Nokia CMG related Configuration	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
217	18	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580775	Critical	1-Extensive/Widespread	East	WB		1	CCAF Link Delete Create in KGPEPG02	No						Enjoy Maity	Yes						No	Yes	cCAF KPI	Link Creation/Changes	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
218	19	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580772	High	2-Significant/Large	East	OR		5	Test number routing in A2CP02  towards ASBC-31	No						Enjoy Maity	No						No	No		Test IMSI definition service in live nodes due to new node	Nokia/Cisco/Ericsson/Huawei/Dell/HP/IBM				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
219	20	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580761	High	1-Extensive/Widespread	South	KL		2	CR for License Loading in KL SAPC Pair-1	No						Enjoy Maity	Yes						No	No		License loading in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
220	21	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580752	Medium	2-Significant/Large	East	AS		1	CR_to remove local-plmn-csr-apn in ASGHERIWMG01	No						Enjoy Maity	No						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson/Nokia/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
221	22	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580731	High	1-Extensive/Widespread	South	TN		16	Domain whitelisting in data expire and throttle rules_E// EPG & E// PCCSM	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
222	23	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580713	Low	1-Extensive/Widespread	West	MP		6	Domain whitelisting in data expire and throttle rules in EPGs	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
223	24	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580594	High	2-Significant/Large	East	OR		4	Test number routing towards A2CP02,CMG-1&cisco SPG from all CMM	No						Enjoy Maity	No						No	No		Static Test IMSI Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
224	25	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580564	Critical	1-Extensive/Widespread	East	BH		6	Domain whitelisting in data expire and throttle rules in EPG & PCCSM11	No						Enjoy Maity	Yes						No	Yes	DRA KPI	DPI /SPI related Changes in GGSN	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
225	26	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580560	High	1-Extensive/Widespread	North	JK		8	Migration APN:-gen.msedcl11.wbiot to Nokia CMG MAH/RAJ Phase-3 in JK Nokia DNS & Cache Clear in CMMs	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
226	27	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580557	High	1-Extensive/Widespread	East	NE		2	CR_Gi DNS migration in NEJORRHCK04ERPCCSM02 Day 1	No						Enjoy Maity	Yes						No	No		IP Pool Addition/Deletion/Modification	Ericsson/Dell/Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
227	28	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580555	Critical	1-Extensive/Widespread	East	BH		9	Top On Weightage for LBO PCCSM16 Go Live in MME	No						Enjoy Maity	Yes						Yes	No		LBO Migration  related Changes	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
229	30	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580543	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
230	31	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580542	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
231	32	MS	2026-09-16	23:00:00 - 06:00:00	CRQ000005580532	Critical	1-Extensive/Widespread	West	RJ		2	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes						Enjoy Maity	Yes						Yes	Yes	IMS and DRA	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Ericsson				VAS	2026-09-15 17:30:00+00	2026-09-16 00:30:00+00				t	1	\N
232	33	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005580502	High	1-Extensive/Widespread	North	PB		19	Pre post sub balancing Sub balancing in PB GW's  as a part of  PBLUDNA2CP04 Upgrade	No						Enjoy Maity	Yes						Yes	Yes	Google/VOLTE	Subs. Purging due to Other Dependent Activities	Nokia/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
233	34	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580492	High	2-Significant/Large	South	KK		9	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
234	35	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580475	High	1-Extensive/Widespread	West	MU		1	M2M CR for subscriber clear gen.msedcl11.wbiot.APN in MUM M2M EPG	No						Enjoy Maity	Yes						No	No		Subs. purging M2M	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
235	36	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580472	High	1-Extensive/Widespread	South	KL		18	Domain whitelisting in data expire and throttle rules_KL Nokia & Cisco GW	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Nokia/Cisco				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
236	37	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580461	High	1-Extensive/Widespread	South	KL		8	CR for NF ID whitelisting in the NRF for the New non-live KLPOLCK06NCMM05	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
237	38	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580458	High	2-Significant/Large	North	HR		4	JIO new test IMSI routing in HR CMM's for ICR testing for HR circle	No						Enjoy Maity	No						No	No		Static Test IMSI Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
238	39	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580457	High	1-Extensive/Widespread	East	AS		1	GPL correction in ASGUWCC01EREPG05	No						Enjoy Maity	Yes						No	No		GPL	Ericsson/Nokia/Dell				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
239	40	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580441	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 5G SA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
240	41	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580436	Critical	1-Extensive/Widespread	North	UPW		8	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW NOKIA DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
241	42	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580422	Critical	1-Extensive/Widespread	East	BH		3	Top On Weightage for PCCSM16 Go-Live in DNS	No						Enjoy Maity	Yes						Yes	No		Top-On Weightage Changes  in DNS	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
242	43	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580416	High	2-Significant/Large	North	DL		30	CR to check the UPW & HR. inter PLMN reachability from DL AMF/SMF/MME/LPG	No						Enjoy Maity	No						No	No		Log & Trace Collection	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
243	44	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580396	Critical	1-Extensive/Widespread	North	UPW		10	CR for APN migration mumspecc02erm2mepg04 to MHKHRNM2MCP03 in UPW CISCO DNS Nodes	No						Enjoy Maity	Yes						No	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
244	45	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580392	High	2-Significant/Large	East	BH		9	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
245	46	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580390	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
246	47	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005580360	High	1-Extensive/Widespread	North	PB		8	TOPON wtg changes in PB Nokia DNS to offload/revert PBLUDNA2CP04 for Upgrade & cache clear in MME	No						Enjoy Maity	Yes						Yes	Yes	Google/VOLTE	Top-On Weightage Changes  in DNS	Nokia				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
247	48	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580338	High	1-Extensive/Widespread	West	MH		11	TAC LAC Modification in Eric MME's for CSFB optimization	No						Enjoy Maity	Yes						No	Yes		TAC LAC modification	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
248	49	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580190	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
249	50	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580186	Low	1-Extensive/Widespread	West	MP		5	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
250	51	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580177	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
251	52	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580174	Low	1-Extensive/Widespread	West	GJ		2	S10 Entry of MP MME remove in GUJ DNSs	No						Enjoy Maity	Yes						Yes	No		S10 Entry Addition/Deletion/Modification in DNS	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
252	53	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005580170	Critical	1-Extensive/Widespread	North	DL		2	CR for M2M APN migration(gen.msedcl11.wbiot) in DL DNS with cache clear	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
253	54	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579899	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
254	55	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579892	Critical	1-Extensive/Widespread	North	DL		1	CR for SBC wtg optimization in MAN SPG2	No						Enjoy Maity	Yes						No	Yes	IMS KPI	SBC Related Changes in Ericsson EPG	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
255	56	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579878	High	1-Extensive/Widespread	West	MH		8	Domain whitelisting in data expire and throttle rules in EPGs	No						Enjoy Maity	Yes						No	Yes		DPI /SPI related Changes in GGSN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
256	57	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579587	High	1-Extensive/Widespread	West	MH		3	gen.msedcl11.wbiot APN Migration to Nokia CMG(M2MCP03/M2MCP01)for go live from MAH Eric//DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
257	58	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579504	Low	1-Extensive/Widespread	North	UPE		4	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-1	No						Enjoy Maity	No						No	Yes	IMS , Nokia , Eric DRA KPIs	FQDN Configuration in PCRF	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
258	59	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579252	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
259	60	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005579246	Low	1-Extensive/Widespread	West	MP		3	M2M APN Gateway Change in DNS	No						Enjoy Maity	Yes						Yes	No		M2M : APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
260	61	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005579228	Low	1-Extensive/Widespread	North	UPE		7	CMM gParm modify for traffic offload in Nokia CMMs as per UEGANCK04NCMM07 Upgrade	No						Enjoy Maity	Yes						Yes	No		Subs. Purging due to Other Dependent Activities	Nokia				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
261	62	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005578916	High	1-Extensive/Widespread	East	AS		4	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
262	63	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005578904	Medium	2-Significant/Large	East	NE		4	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
263	64	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005578771	Critical	1-Extensive/Widespread	West	RJ		8	CMM gParam modify for traffic Balancing in Nokia CMMs as part of Jaipur CMM09 Upgrade	No						Enjoy Maity	Yes						Yes	Yes	IMS and DRA	Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
264	65	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005578546	Medium	2-Significant/Large	East	KO		5	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
265	66	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005578388	Low	1-Extensive/Widespread	West	GJ		2	5G home Traffic Balancing from GUJ DNSs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	1	\N
266	67	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005578360	Critical	1-Extensive/Widespread	West	RJ		8	BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Yes						Enjoy Maity	Yes						No	No		BPMS - RC Value Change Nokia CMM - Pre-Agg-Post - E2E	Nokia				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
267	68	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577478	High	1-Extensive/Widespread	North	UPE		7	BPMS - RC Value Change Nokia CMM - Pre-Post - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - RC Value Change Nokia CMM - Pre-Post - E2E	Nokia				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
268	69	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577474	Medium	2-Significant/Large	West	MU		1	BRM and SP backup for MUMCHAEDNS01 before and after activity	No						Enjoy Maity	No						Yes	No		Backup	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
269	70	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577445	Medium	2-Significant/Large	West	MU		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in MUMCHAEDNS01	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
270	71	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	High	1-Extensive/Widespread	West	MU		3	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No						Enjoy Maity	Yes						Yes	Yes	IMS & ORDRA team align	Software Update in DNS	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
271	72	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	Medium	2-Significant/Large	West	MU		5	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
272	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW		5	CR for 5G location Retrieval Enable in Nokia AAA	No						Enjoy Maity	No						No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
273	74	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	High	1-Extensive/Widespread	South	CH		2	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No						Enjoy Maity	Yes						No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
274	75	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	High	2-Significant/Large	North	UPW		10	CR for Non-Live M2M APN definition in CISCO DNS	No						Enjoy Maity	No						No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
275	76	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	High	2-Significant/Large	North	DL		1	Test IMSI routing in MAN MME1 towards DSR5/6	No						Enjoy Maity	No						No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
276	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW		5	CR for 5G location Retrieval Enable in Nokia AAA	No	planned					Enjoy Maity	No						No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
277	74	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	High	1-Extensive/Widespread	South	CH		2	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	planned					Enjoy Maity	Yes						No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
278	75	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	High	2-Significant/Large	North	UPW		10	CR for Non-Live M2M APN definition in CISCO DNS	No	planned					Enjoy Maity	No						No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
279	76	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	High	2-Significant/Large	North	DL		1	Test IMSI routing in MAN MME1 towards DSR5/6	No	planned					Enjoy Maity	No						No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	1	\N
280	76	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	High	2-Significant/Large	North	DL	DELMANEMME01	1	Test IMSI routing in MAN MME1 towards DSR5/6	No	planned					Enjoy Maity	No	Impact -- NSA	Test Plan				No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	279
281	76	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	High	2-Significant/Large	North	DL	DELMANEMME01	1	Test IMSI routing in MAN MME1 towards DSR5/6	No	planned					Enjoy Maity	No	Impact -- NSA	Test Plan				No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	279
282	75	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	High	2-Significant/Large	North	UPW	MAN-DC-ADNS-01,\nMER-MPN-SGSN-02,\nUPW01-NOI-S57-ULTRA-MME-01,\nUPW-MOD-vMME-01,\nMAN-DC-CDNS-01,\nMAN-DC-ADNS-02,\nMAN-DC-CDNS-02,\nUPW-MAN-DC-vMME-01,\nUPW-MOD-vMME-02,\nUPW-NOI-S57-vMME-02	10	CR for Non-Live M2M APN definition in CISCO DNS	No	planned					Enjoy Maity	No	NSA	Normal testing will be done				No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	278
283	75	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	High	2-Significant/Large	North	UPW	MAN-DC-ADNS-01,\nMER-MPN-SGSN-02,\nUPW01-NOI-S57-ULTRA-MME-01,\nUPW-MOD-vMME-01,\nMAN-DC-CDNS-01,\nMAN-DC-ADNS-02,\nMAN-DC-CDNS-02,\nUPW-MAN-DC-vMME-01,\nUPW-MOD-vMME-02,\nUPW-NOI-S57-vMME-02	10	CR for Non-Live M2M APN definition in CISCO DNS	No	planned					Enjoy Maity	No	NSA	Normal testing will be done				No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	278
284	74	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	High	1-Extensive/Widespread	South	CH	CHNSNTVSAPC02,\nCHNSIRVSAPC01	2	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	planned					Enjoy Maity	Yes	SA, in worst case 20 Mins Volte/voice services will be impacted	KPI:-( CHNSNTVSAPC02) CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx-AAR Success Rate Rx-RAR Success Rate Rx-STR Success rate PCF KPI: SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) CHN SAPC Pair-1 CHNSIRVSAPC01, CHNSNTVSAPC02 CHNSIRVSAPC01—non-preferred CHNSNTVSAPC02—preferred CHNOCDSR03, CHNOCDSR04 KPI: Diameter_DSR_Success_Rate IMS KPI & O-DRA KPI Aligned from circle end. Voice & Volte testing to be done by circle team.				No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	277
285	74	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	High	1-Extensive/Widespread	South	CH	CHNSNTVSAPC02,\nCHNSIRVSAPC01	2	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	planned					Enjoy Maity	Yes	SA, in worst case 20 Mins Volte/voice services will be impacted	KPI:-( CHNSNTVSAPC02) CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx-AAR Success Rate Rx-RAR Success Rate Rx-STR Success rate PCF KPI: SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) CHN SAPC Pair-1 CHNSIRVSAPC01, CHNSNTVSAPC02 CHNSIRVSAPC01—non-preferred CHNSNTVSAPC02—preferred CHNOCDSR03, CHNOCDSR04 KPI: Diameter_DSR_Success_Rate IMS KPI & O-DRA KPI Aligned from circle end. Voice & Volte testing to be done by circle team.				No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	277
286	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW	UWN81NAAA01-oam-0,\nUWN81NAAA01-app-1,\nUWN81NAAA01-oam-1,\nUWN81NAAA01,\nUWN81NAAA01-app-0	5	CR for 5G location Retrieval Enable in Nokia AAA	No	planned					Enjoy Maity	No	NSA	Testing :- Vowifi/VoLTE testing KPI Diameter AAA Success Rate, Diameter EAP request success Rate, Diameter Server Assignement Request success Rate, Diameter STR Success Rate, No.of Authenticated users Nodes - UPWNOICC01ERWMG01, DELNOICC01ERWMG01 DELMANRHCC03ERWMG02  Handoff Sessions Success Rate Initial Attach Sessions Success Rate Create Bearer Request Success rate Create Session Request Success rate Total User Count SAPC KPI:-UWNODVSAPC01 UWMANVSAPC02 UWMANVSAPC01 UWNODVSAPC02  CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx - AAR Success Rate Rx - RAR Success Rate Rx-ASR Success rate Rx-STR Success rate PCF KPI :-SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) DRA KPI:- Nokia DRA KPI alien by circle team				No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	276
287	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW	UWN81NAAA01-oam-0,\nUWN81NAAA01-app-1,\nUWN81NAAA01-oam-1,\nUWN81NAAA01,\nUWN81NAAA01-app-0	5	CR for 5G location Retrieval Enable in Nokia AAA	No	planned					Enjoy Maity	No	NSA	Testing :- Vowifi/VoLTE testing KPI Diameter AAA Success Rate, Diameter EAP request success Rate, Diameter Server Assignement Request success Rate, Diameter STR Success Rate, No.of Authenticated users Nodes - UPWNOICC01ERWMG01, DELNOICC01ERWMG01 DELMANRHCC03ERWMG02  Handoff Sessions Success Rate Initial Attach Sessions Success Rate Create Bearer Request Success rate Create Session Request Success rate Total User Count SAPC KPI:-UWNODVSAPC01 UWMANVSAPC02 UWMANVSAPC01 UWNODVSAPC02  CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx - AAR Success Rate Rx - RAR Success Rate Rx-ASR Success rate Rx-STR Success rate PCF KPI :-SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) DRA KPI:- Nokia DRA KPI alien by circle team				No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	2	276
288	72	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	Medium	2-Significant/Large	West	MU		5	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	planned					Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
289	71	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	High	1-Extensive/Widespread	West	MU		3	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	planned					Enjoy Maity	Yes						Yes	Yes	IMS & ORDRA team align	Software Update in DNS	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
290	76	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005510871	High	2-Significant/Large	North	DL	DELMANEMME01	1	Test IMSI routing in MAN MME1 towards DSR5/6	No	unplanned					Enjoy Maity	No	Impact -- NSA	Test Plan				No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	2	279
319	15	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583150	High	2-Significant/Large	North	PB		5	Multiple IR definition in PB CISCO MMEs.	No						Enjoy Maity	No						Yes	No		New IR launch	Cisco				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
291	75	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005574727	High	2-Significant/Large	North	UPW	MAN-DC-ADNS-01,\nMER-MPN-SGSN-02,\nUPW01-NOI-S57-ULTRA-MME-01,\nUPW-MOD-vMME-01,\nMAN-DC-CDNS-01,\nMAN-DC-ADNS-02,\nMAN-DC-CDNS-02,\nUPW-MAN-DC-vMME-01,\nUPW-MOD-vMME-02,\nUPW-NOI-S57-vMME-02	10	CR for Non-Live M2M APN definition in CISCO DNS	No	unplanned					Enjoy Maity	No	NSA	Normal testing will be done				No	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	2	278
292	74	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005575177	High	1-Extensive/Widespread	South	CH	CHNSNTVSAPC02,\nCHNSIRVSAPC01	2	PBI000000269790: Learning_Alarm_Certificate Management in CHN SAPC pair-01	No	unplanned					Enjoy Maity	Yes	SA, in worst case 20 Mins Volte/voice services will be impacted	KPI:-( CHNSNTVSAPC02) CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx-AAR Success Rate Rx-RAR Success Rate Rx-STR Success rate PCF KPI: SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) CHN SAPC Pair-1 CHNSIRVSAPC01, CHNSNTVSAPC02 CHNSIRVSAPC01—non-preferred CHNSNTVSAPC02—preferred CHNOCDSR03, CHNOCDSR04 KPI: Diameter_DSR_Success_Rate IMS KPI & O-DRA KPI Aligned from circle end. Voice & Volte testing to be done by circle team.				No	No		New Learning implementation in SAPC	Ericsson				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				t	2	277
293	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW	UWN81NAAA01-oam-0,\nUWN81NAAA01-app-1,\nUWN81NAAA01-oam-1,\nUWN81NAAA01,\nUWN81NAAA01-app-0	5	CR for 5G location Retrieval Enable in Nokia AAA	No	planned					Enjoy Maity	No	NSA	Testing :- Vowifi/VoLTE testing KPI Diameter AAA Success Rate, Diameter EAP request success Rate, Diameter Server Assignement Request success Rate, Diameter STR Success Rate, No.of Authenticated users Nodes - UPWNOICC01ERWMG01, DELNOICC01ERWMG01 DELMANRHCC03ERWMG02  Handoff Sessions Success Rate Initial Attach Sessions Success Rate Create Bearer Request Success rate Create Session Request Success rate Total User Count SAPC KPI:-UWNODVSAPC01 UWMANVSAPC02 UWMANVSAPC01 UWNODVSAPC02  CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx - AAR Success Rate Rx - RAR Success Rate Rx-ASR Success rate Rx-STR Success rate PCF KPI :-SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) DRA KPI:- Nokia DRA KPI alien by circle team				No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	3	287
294	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW	UWN81NAAA01-oam-0,\nUWN81NAAA01-app-1,\nUWN81NAAA01-oam-1,\nUWN81NAAA01,\nUWN81NAAA01-app-0	5	CR for 5G location Retrieval Enable in Nokia AAA	No	planned					Enjoy Maity	No	NSA	Testing :- Vowifi/VoLTE testing KPI Diameter AAA Success Rate, Diameter EAP request success Rate, Diameter Server Assignement Request success Rate, Diameter STR Success Rate, No.of Authenticated users Nodes - UPWNOICC01ERWMG01, DELNOICC01ERWMG01 DELMANRHCC03ERWMG02  Handoff Sessions Success Rate Initial Attach Sessions Success Rate Create Bearer Request Success rate Create Session Request Success rate Total User Count SAPC KPI:-UWNODVSAPC01 UWMANVSAPC02 UWMANVSAPC01 UWNODVSAPC02  CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx - AAR Success Rate Rx - RAR Success Rate Rx-ASR Success rate Rx-STR Success rate PCF KPI :-SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) DRA KPI:- Nokia DRA KPI alien by circle team				No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	3	287
295	72	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	Medium	2-Significant/Large	West	MU	MUMSPEEMME03,\nMUSPTRHCK01ERPCCMM04,\nMUMCHAEMME01,\nMUMSPEEMME02,\nMUMCHARHCK02ERPCCMM05	5	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	planned					Enjoy Maity	No	NSA	Test Plan & KPI: NA				Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	2	288
296	72	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	Medium	2-Significant/Large	West	MU	MUMSPEEMME03,\nMUSPTRHCK01ERPCCMM04,\nMUMCHAEMME01,\nMUMSPEEMME02,\nMUMCHARHCK02ERPCCMM05	5	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	planned					Enjoy Maity	No	NSA	Test Plan & KPI: NA				Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	2	288
297	71	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	High	1-Extensive/Widespread	West	MU	MUM-CHD-CS-ASR9K-R2,\nMUM-CHD-CS-ASR9K-R1,\nMUMCHAEDNS01	3	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	planned					Enjoy Maity	Yes	SA Activity:25-30 Mins Data & Voice services may be impacted in Worst case	Test plan & KPI:- Normal testing done from circle team through test number & need to check Post Eric MME KPI: MUMCHAEMME01, MUMSPEEMME02, MUMSPEEMME03, MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session(Eric- MME & PCCMM) -ERAB_Modification_SR_E(MME & PCCMM) MUMCHAEMME01, MUMSPEEMME02  - ASR_2G_Combined . -PDP_SR_2G_Combined . AMF: MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 Initial Registration Success Rate_5G_SA Interworking from 4G to 5G Registration Success Rate_5G_SA Service Request Sucess Rate_5G_SA 5GS to EPS Handover Using N26 Interface Success Rate_5G_SA Registered Subscriber_5G_SA. IMS & ORDRA to be aligned from Circle				Yes	Yes	IMS & ORDRA team align	Software Update in DNS	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	2	289
298	71	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	High	1-Extensive/Widespread	West	MU	MUM-CHD-CS-ASR9K-R2,\nMUM-CHD-CS-ASR9K-R1,\nMUMCHAEDNS01	3	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	planned					Enjoy Maity	Yes	SA Activity:25-30 Mins Data & Voice services may be impacted in Worst case	Test plan & KPI:- Normal testing done from circle team through test number & need to check Post Eric MME KPI: MUMCHAEMME01, MUMSPEEMME02, MUMSPEEMME03, MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session(Eric- MME & PCCMM) -ERAB_Modification_SR_E(MME & PCCMM) MUMCHAEMME01, MUMSPEEMME02  - ASR_2G_Combined . -PDP_SR_2G_Combined . AMF: MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 Initial Registration Success Rate_5G_SA Interworking from 4G to 5G Registration Success Rate_5G_SA Service Request Sucess Rate_5G_SA 5GS to EPS Handover Using N26 Interface Success Rate_5G_SA Registered Subscriber_5G_SA. IMS & ORDRA to be aligned from Circle				Yes	Yes	IMS & ORDRA team align	Software Update in DNS	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	2	289
299	70	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577445	Medium	2-Significant/Large	West	MU		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in MUMCHAEDNS01	No	planned					Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				f	1	\N
320	16	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583143	High	2-Significant/Large	North	HP		2	Volte IR launch (Polkomtel_Poland) definition in HP NOKIA CMM's	No						Enjoy Maity	No						No	No		New IR launch	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
300	71	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577282	High	1-Extensive/Widespread	West	MU	MUM-CHD-CS-ASR9K-R2,\nMUM-CHD-CS-ASR9K-R1,\nMUMCHAEDNS01	3	CR For vIPWorks Version Update from 2.11 to 2.13 in MUMCHAEDNS01	No	unplanned					Enjoy Maity	Yes	SA Activity:25-30 Mins Data & Voice services may be impacted in Worst case	Test plan & KPI:- Normal testing done from circle team through test number & need to check Post Eric MME KPI: MUMCHAEMME01, MUMSPEEMME02, MUMSPEEMME03, MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 -ASR_4G_Combined -PSR_4G_Combined -TAU_4G_Combined -Service Request SR_Combined -SAU 4G_Combined -5G Active Session(Eric- MME & PCCMM) -ERAB_Modification_SR_E(MME & PCCMM) MUMCHAEMME01, MUMSPEEMME02  - ASR_2G_Combined . -PDP_SR_2G_Combined . AMF: MUSPTRHCK01ERPCCMM04, MUMCHARHCK02ERPCCMM05 Initial Registration Success Rate_5G_SA Interworking from 4G to 5G Registration Success Rate_5G_SA Service Request Sucess Rate_5G_SA 5GS to EPS Handover Using N26 Interface Success Rate_5G_SA Registered Subscriber_5G_SA. IMS & ORDRA to be aligned from Circle				Yes	Yes	IMS & ORDRA team align	Software Update in DNS	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	2	289
301	69	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577474	Medium	2-Significant/Large	West	MU		1	BRM and SP backup for MUMCHAEDNS01 before and after activity	No	planned					Enjoy Maity	No						Yes	No		Backup	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
302	73	MS	2026-09-16	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW	UWN81NAAA01-oam-0,\nUWN81NAAA01-app-1,\nUWN81NAAA01-oam-1,\nUWN81NAAA01,\nUWN81NAAA01-app-0	5	CR for 5G location Retrieval Enable in Nokia AAA	No	unplanned					Enjoy Maity	No	NSA	Testing :- Vowifi/VoLTE testing KPI Diameter AAA Success Rate, Diameter EAP request success Rate, Diameter Server Assignement Request success Rate, Diameter STR Success Rate, No.of Authenticated users Nodes - UPWNOICC01ERWMG01, DELNOICC01ERWMG01 DELMANRHCC03ERWMG02  Handoff Sessions Success Rate Initial Attach Sessions Success Rate Create Bearer Request Success rate Create Session Request Success rate Total User Count SAPC KPI:-UWNODVSAPC01 UWMANVSAPC02 UWMANVSAPC01 UWNODVSAPC02  CCR-I Success Rate CCR-T Success Rate CCR-Update Success Rate Gx-RAR Success Rate Rx - AAR Success Rate Rx - RAR Success Rate Rx-ASR Success rate Rx-STR Success rate PCF KPI :-SM Policy Control Create Success Ratio (only Eric) SM Policy Control UpdateNotify Success Ratio (only Eric) DRA KPI:- Nokia DRA KPI alien by circle team				No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-15 18:30:00+00	2026-09-16 00:30:00+00				f	3	287
303	72	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577170	Medium	2-Significant/Large	West	MU	MUMSPEEMME03,\nMUSPTRHCK01ERPCCMM04,\nMUMCHAEMME01,\nMUMSPEEMME02,\nMUMCHARHCK02ERPCCMM05	5	Support CR for cache clear in MUM Eric MME Post IPWorks MUMCHAEDNS01 DNS 2.13 Update	No	unplanned					Enjoy Maity	No	NSA	Test Plan & KPI: NA				Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	2	288
304	70	MS	2026-09-16	23:00:00 - 07:00:00	CRQ000005577445	Medium	2-Significant/Large	West	MU		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in MUMCHAEDNS01	No	unplanned					Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/HP/Dell/Cisco				PS-CORE	2026-09-15 17:30:00+00	2026-09-16 01:30:00+00				t	1	\N
305	1	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583437	High	1-Extensive/Widespread	West	MU		1	M2M CR for new source IP pool addition in MUM M2M EPG FOR M2M gprsnac.com apn	No						Enjoy Maity	Yes						No	No		M2M : IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
306	2	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
307	3	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	High	2-Significant/Large	West	MU		5	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
308	4	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583423	High	2-Significant/Large	North	PB		6	Multiple IR definition in PB Nokia CMM	No						Enjoy Maity	No						Yes	No		New IR launch	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
309	5	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583421	Medium	2-Significant/Large	West	MU		1	M2M CR for new source IP pool addition in MUM M2M EPG FOR M2M gprsnac.com apn	No						Enjoy Maity	No						No	No		M2M : APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
310	6	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005583419	High	1-Extensive/Widespread	South	KL		3	TOPON changes for 2G in Cisco SGSN for KLCALNA2CP03 upgrade and revert	No						Enjoy Maity	Yes						Yes	No	No	Traffic diversions	Nokia/Cisco				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
311	7	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583345	High	1-Extensive/Widespread	North	PB		2	PBI000000268674:Learning RPC portmapper Service Detection Vulnerability in PB CMM01_LTMT2	No						Enjoy Maity	Yes						No	No		New Learning Implementation in SGSN/EPDG/MME	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
312	8	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583315	High	1-Extensive/Widespread	East	AS		6	CR_EPLMN definition in AS MMEs with PCCMM for 4G	No						Enjoy Maity	Yes						No	No		PLMN modification	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
313	9	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005583314	High	1-Extensive/Widespread	South	KL		14	CR for subscriber clear in KL GGSN Nodes post KLCALNA2CP03 upgrade	No						Enjoy Maity	Yes						Yes	Yes		Subs.  Purging due to Software Update	Nokia/Cisco				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
314	10	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583302	High	1-Extensive/Widespread	South	AP		2	PBI000000269790: learning for Alarm_Certificate Management Certificate is to Expire in AP SAPC Pair2	No						Enjoy Maity	Yes						No	No	IMS/Oracle DRA	New Learning implementation in SAPC	Ericsson				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
315	11	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583168	Medium	2-Significant/Large	East	WB		6	New ICR Test number definition in ROB MME&PCCMM	No						Enjoy Maity	No						No	No		Static Test IMSI Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
316	12	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583167	Critical	1-Extensive/Widespread	East	WB		2	CCAF Link Delete Create in ROBSILCC01EREPGCP03	No						Enjoy Maity	Yes						No	Yes	cCAF KPI	Link Creation/Changes	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
317	13	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583160	Critical	1-Extensive/Widespread	East	BH		30	PDP flushing in all GGSN for Home IMSI series migration from SAPC to CCPC and SAPC	No						Enjoy Maity	Yes						Yes	No		Subs. Purging due to Other Dependent Activities	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
318	14	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583153	High	1-Extensive/Widespread	West	MH		3	SMF 5G SA traffic weightage distribution for MHKHARHCK07ERPCCSM11 Go-live	No						Enjoy Maity	Yes						Yes	Yes		Capacity Balancing in SMF	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
321	17	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005583138	High	1-Extensive/Widespread	South	KL		16	TOPON changes for 5G,4G & IMS in DNS Nodes for KLCALNA2CP03 upgrade and revert with cacheclear	No						Enjoy Maity	Yes						Yes	Yes	No	Top-On Weightage Changes  in DNS due to Software Update	Nokia/Cisco				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
322	18	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583129	Medium	2-Significant/Large	South	TN		7	Static test IMSI routing in TN E// MMEs & PCCMMs for new Node PCCSM12	No						Enjoy Maity	No						No	No		Test IMSI definition service in live nodes due to new node	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
323	19	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583123	High	1-Extensive/Widespread	East	AS		4	CR_PCF Priority change in NESA CCPC Pair 2 (Jorhat Prefer)	No						Enjoy Maity	Yes						No	No		Preferred to Non-Preferred SAPC	Ericsson/Nokia/DELL/HP				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
324	20	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583116	High	1-Extensive/Widespread	North	HR		1	Migration of HR imsi (404960969) towards PB new OCDRA03_04 for S6a traffic from HR CMM02	No						Enjoy Maity	Yes						Yes	No		IMSI Migration from SGSN/MME	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
325	21	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583113	Critical	1-Extensive/Widespread	South	AP		5	PBI000000269910-Learning-CBC timers and buffers size change in Ericsson-AP MME & PCCMMs	No						Enjoy Maity	Yes						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
326	22	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582884	High	1-Extensive/Widespread	South	KK		1	SBc interface integration for CBC in KKMANGEMME04	No						Enjoy Maity	Yes						No	No	No testing & No KPI required for cache clear IP resolution need to check	New Ericsson MME related Configuration	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
327	23	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	Medium	2-Significant/Large	East	BH		9	CR for New IR Definition in MME & PCCMM	No						Enjoy Maity	No						No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
328	24	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582864	Medium	2-Significant/Large	West	MU		2	M2M CR FOr Multiple M2M APN Gateway IP change from MUM Eric DNS	No						Enjoy Maity	No						Yes	No		M2M : Private APN DNS Entry NonLive	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
329	25	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005582856	Critical	1-Extensive/Widespread	West	RJ		4	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Yes						Enjoy Maity	Yes						No	Yes	IMS and DRA	BPMS - Geo-Red Disable Enable in Ericsson SAPC - E2E	Ericsson				VAS	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
330	26	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582850	Low	1-Extensive/Widespread	West	MP		5	SOS APN Routing Removal from GGSN02	No						Enjoy Maity	Yes						No	No		APN Creation/Deletion/Modification	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
331	27	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582845	High	1-Extensive/Widespread	North	PB		4	New FWA MDU UE IP POOL ADDITION in PBLUDNA2CP02/ U03/U04 for testing	No						Enjoy Maity	Yes						No	No		New Nokia CMG related Configuration	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
332	28	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582840	High	2-Significant/Large	East	OR		8	MIP6 FQDN Definition for odbsvna2cp03 in Nokia DNS with Cache clear	No						Enjoy Maity	No						No	No		New Nokia CMG related Configuration	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
333	29	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582839	High	2-Significant/Large	East	OR		8	MIP6 FQDN Definition for odbsvna2cp03 in Cisco DNS with Cache clear	No						Enjoy Maity	No						No	No		New Nokia CMG related Configuration	Cisco				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
334	30	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005582831	High	1-Extensive/Widespread	East	OR		3	CMM-1,2,3 for traffic balancing with Gpara change Post CMM-4 upgrade	No						Enjoy Maity	Yes						Yes	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
335	31	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005582829	High	2-Significant/Large	East	OR		3	4G/5G RC change in CMM-1,2,3 for sw upgrade in CMM-4	No						Enjoy Maity	No						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
336	32	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582555	Critical	1-Extensive/Widespread	North	UPW		2	New_Learning: Alarm_Certificate Management, the Certificate is to Expire SAPC Pair 1 nodes	No						Enjoy Maity	Yes						No	Yes	IMS /DRA KPI	New Learning implementation in SAPC	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
337	33	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582539	High	1-Extensive/Widespread	East	AS		1	CR_IMS paging profile optimization in ASJORRHCK04ERPCCMM07	No						Enjoy Maity	Yes						No	No		Feature changes for perf. Improvement	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
338	34	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582538	High	1-Extensive/Widespread	North	HR		11	CR for Punjab CCPC Pair 01& 02 NRF registration with priority change & NF whitelisting of Amb CCPC	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
339	35	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582534	High	1-Extensive/Widespread	East	NE		2	Gi-DNS IP change in test apn in NEJORRHCK04ERPCCSM02	No						Enjoy Maity	Yes						No	No		IP Pool Addition/Deletion/Modification	Ericsson/Dell/Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
340	36	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582417	Low	1-Extensive/Widespread	North	UPE		3	IMEI TAC -35418669 routed from CFWA-11/12 CMG to CFWA-UPF03	No						Enjoy Maity	Yes						No	No		Parameter Definition/Changes MME/GGSN/EPDG/WMG	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
341	37	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582290	High	1-Extensive/Widespread	South	AP		2	Home Gy Traffic addition in APVIJRHCK01ERPCCSM05 towards Uppal & Siruseri  CAF (with Dlb0,1 & Dlb2)	No						Enjoy Maity	Yes						No	Yes	CCAF KPI	New service launch in existing nodes (DSA Solution rollout)	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
342	38	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582267	High	2-Significant/Large	North	UPW		1	Learning-Vulnerability mitigation in CMM(Elasticsearch Unrestricted Access Information Disclosure)	No						Enjoy Maity	No						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
343	39	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581700	Low	1-Extensive/Widespread	North	UPE		4	SMF N7 IP & NfInstanceID  for CMG CP07 & Gx Hostname defn for CMG CP08 / CP09 in CCPC Pair-1	No						Enjoy Maity	No						No	Yes	IMS , Nokia , Eric DRA KPIs	FQDN Configuration in PCRF	Ericsson				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
344	40	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581682	High	2-Significant/Large	West	RJ		9	Activity for Test Number routing at Nokia CMM end	No						Enjoy Maity	No						No	No		Test IMSI definition service in live nodes due to new node	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
345	41	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581681	Critical	1-Extensive/Widespread	West	RJ		1	CR for DSR Test Number Routing in RAJ-UDP-B2C-vSPG-01	No						Enjoy Maity	No						No	No		Test IMSI definition service in live nodes due to new node	Cisco				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
346	42	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581639	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
347	43	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581637	Critical	1-Extensive/Widespread	North	DL		2	Support CR for Subs Purging for Activity revert SM3 Home/LBO Postpaid GxGy migration towards DSR3/4	No						Enjoy Maity	Yes						Yes	Yes	IMS/DRA KPI	Subs. Purging due to Other Dependent Activities	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
348	44	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581627	Medium	2-Significant/Large	South	TN		7	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
349	45	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005581618	High	2-Significant/Large	South	CH		3	BRM and SP backup for CHNSIREDNS03 before and after activity	No						Enjoy Maity	No						Yes	No		Patch Update Prerequisite	Ericsson/Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
350	46	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005581617	Critical	1-Extensive/Widespread	South	CH		6	Traffic diversion from CHN E// MMEs & rollback for IPWorks DNS 2.13 Update in CHNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Traffic diversions	Ericsson/Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
351	47	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005581616	Critical	1-Extensive/Widespread	South	CH		3	vIPWorks Version Update to 2.11 to 2.13 in CHN E// DNS CHNSIREDNS03	No						Enjoy Maity	Yes						Yes	Yes		Software Update in DNS	Ericsson/Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
352	48	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005581615	High	2-Significant/Large	South	CH		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in CHNSIREDNS03	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Nokia				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
353	49	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581279	Critical	1-Extensive/Widespread	North	DL		1	CR for complete imsi 40410 migration towards DSR5/6 in PCCMM5 and purging regards rollback	No						Enjoy Maity	Yes						No	Yes	HSS KPI	IMSI Migration from SGSN/MME	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
354	50	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581276	Critical	1-Extensive/Widespread	North	DL		2	CR for MAN PCCSM3 Home/LBO Postpaid GxGy migration towards DSR3/4	No						Enjoy Maity	Yes						Yes	Yes	IMS/DRA KPI	LBO Migration  related Changes	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
355	51	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581267	Critical	1-Extensive/Widespread	North	DL		2	CR for IR PLMN IMS PGW wtg changes in EDNS/cache clear regard DL IRGW1 traffic optimization	No						Enjoy Maity	Yes						No	Yes	CRMS KPI	Top-On Weightage Changes  in DNS	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
356	52	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581117	Low	1-Extensive/Widespread	North	UPE		3	New IP Pool for airtelfwamdu of CP02 CMG ( UP05 / UP06) for Go Live	No						Enjoy Maity	Yes						No	Yes	BNG Confirmation	IP Pool Addition/Deletion/Modification	Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
357	53	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581094	High	2-Significant/Large	North	DL		2	M2M-CR for non-live M2M APN(sweetfhv.m2mm) DNS entry in DL DNS with Cache clear	No						Enjoy Maity	No						Yes	No		Private APN DNS Entry -NonLive	Ericsson / Cisco / HP / DELL / Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
358	54	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581083	High	1-Extensive/Widespread	South	CH		2	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Yes						Enjoy Maity	Yes						Yes	Yes	IMS	BPMS - Preferred & Non-Preferred Changes in E/// SAPC - E2E	Ericsson				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
359	55	MS	2026-09-17	23:00:00 - 07:00:00	CRQ000005581082	High	2-Significant/Large	South	CH		4	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 17:30:00+00	2026-09-17 01:30:00+00				t	1	\N
360	56	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005581041	Low	1-Extensive/Widespread	West	GJ		12	Non-Live SMF (SM07) Instance ID Registration De-registration through NF Screening	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
361	57	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005580798	High	2-Significant/Large	South	KK		9	New multiple operator launch for VOLTE/5G IR launch in KKMMEs/PCCMMs	No						Enjoy Maity	No						No	No	No testing & No KPI required for cache clear IP resolution need to check	IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
362	58	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005580797	High	1-Extensive/Widespread	South	KK		9	SGs pool addition for LAC- 26671,2,3,4,21791,2,3,5,6,7 (Hubli/MLR Pool VLRs) in KKMMEs-Ph-24	No						Enjoy Maity	Yes						No	No	No testing & No KPI required for cache clear IP resolution need to check	CSFB Related Changes	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
363	59	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005579589	Low	1-Extensive/Widespread	North	UPE		24	Unused TAC related configuration deletion in Cisco & Nokia  DNS	No						Enjoy Maity	Yes						No	Yes	RAN KPIs	Non-Live TAC/LAC/RAC Addition/Deletion/Modification in DNS	Cisco/Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
364	60	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005579241	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 4G & 5G NSA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	138
365	61	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005579154	Low	2-Significant/Large	West	MP		5	Cache Clear in MPCG E//MMEs	No						Enjoy Maity	No						Yes	No		Cache Clear in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	152
366	62	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005578993	Low	1-Extensive/Widespread	West	MP		3	PCCSM09 addition in DNS for 5G SA Go-Live	No						Enjoy Maity	Yes						Yes	No		New Ericsson EPG related Configuration	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	162
367	63	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005578982	Low	1-Extensive/Widespread	West	MP		3	5G SA Traffic weight modification in SMF for PCCSM09 Go-Live	No						Enjoy Maity	Yes						Yes	No		Top-on Implementation	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	163
368	64	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005578795	Low	1-Extensive/Widespread	West	MP		5	PCCSM09 Go-Live with LBO Traffic in MME & PCCMM	No						Enjoy Maity	Yes						Yes	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	169
369	65	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576881	Medium	2-Significant/Large	North	UPW		5	CR for 5G location Retrieval Enable in Nokia AAA	No						Enjoy Maity	No						No	No		Parameter related changes	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	4	302
370	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH		11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No						Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
371	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH		3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No						Enjoy Maity	Yes						Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
372	68	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005566714	Low	1-Extensive/Widespread	West	GJ		4	Support CR :blocking / Unblocking  the traffic from all Huawei /Nokia GGSNs to OCC-3	No						Enjoy Maity	Yes						Yes	No		OCC Blocking/Unblocking in GGSN	Huawei/Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
373	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH		3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes						Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
374	68	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005566714	Low	1-Extensive/Widespread	West	GJ		4	Support CR :blocking / Unblocking  the traffic from all Huawei /Nokia GGSNs to OCC-3	No	planned					Enjoy Maity	Yes						Yes	No		OCC Blocking/Unblocking in GGSN	Huawei/Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
375	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH		11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes						Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
376	68	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005566714	Low	1-Extensive/Widespread	West	GJ		4	Support CR :blocking / Unblocking  the traffic from all Huawei /Nokia GGSNs to OCC-3	No	unplanned					Enjoy Maity	Yes						Yes	No		OCC Blocking/Unblocking in GGSN	Huawei/Nokia				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	1	\N
377	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH	MAHNAGEDNS01,\nMAHPUNEDNS03,\nMAHKHAEDNS05	3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes	Impact-SA (30 Mins Data & Volte, services may be impacted) NO M2M Services Impact	Testing: -Fresh LU Volte, MO/MT Call,Data testing circle itself KPI:' GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR				Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	373
378	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH	MAHNAGEDNS01,\nMAHPUNEDNS03,\nMAHKHAEDNS05	3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes	Impact-SA (30 Mins Data & Volte, services may be impacted) NO M2M Services Impact	Testing: -Fresh LU Volte, MO/MT Call,Data testing circle itself KPI:' GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR				Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	373
379	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH	MAHNAGEMME01,\nMAHPUNEMME02,\nMAHPUNEMME04,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes	Impact-SA ( 30 Mins Data & Volte services may be impacted) NO M2M Services Impact	Testing: - Basic MO/MT/VOLTE call/Data testing circle itself				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	375
380	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH	MAHNAGEMME01,\nMAHPUNEMME02,\nMAHPUNEMME04,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned					Enjoy Maity	Yes	Impact-SA ( 30 Mins Data & Volte services may be impacted) NO M2M Services Impact	Testing: - Basic MO/MT/VOLTE call/Data testing circle itself				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	375
381	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH	MAHNAGEDNS01,\nMAHPUNEDNS03,\nMAHKHAEDNS05	3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA (30 Mins Data & Volte, services may be impacted) NO M2M Services Impact	Testing: -Fresh LU Volte, MO/MT Call,Data testing circle itself KPI:' GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR				Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	373
382	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH	MAHNAGEMME01,\nMAHPUNEMME02,\nMAHPUNEMME04,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA ( 30 Mins Data & Volte services may be impacted) NO M2M Services Impact	Testing: - Basic MO/MT/VOLTE call/Data testing circle itself				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	375
383	2	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
384	3	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	High	2-Significant/Large	West	MU		5	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
385	23	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	Medium	2-Significant/Large	East	BH		9	CR for New IR Definition in MME & PCCMM	No	planned					Enjoy Maity	No						No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
386	2	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	High	2-Significant/Large	West	MH		11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
387	3	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	High	2-Significant/Large	West	MU		5	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
388	23	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	Medium	2-Significant/Large	East	BH		9	CR for New IR Definition in MME & PCCMM	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No						No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	1	\N
389	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH	MAHNAGEDNS01,\nMAHPUNEDNS03,\nMAHKHAEDNS05	3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA (30 Mins Data & Volte, services may be impacted) NO M2M Services Impact	Testing: -Fresh LU Volte, MO/MT Call,Data testing circle itself KPI:' GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR				Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	3	381
390	67	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576793	High	1-Extensive/Widespread	West	MH	MAHNAGEDNS01,\nMAHPUNEDNS03,\nMAHKHAEDNS05	3	TOPON Weightage modification in E/DNS for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA (30 Mins Data & Volte, services may be impacted) NO M2M Services Impact	Testing: -Fresh LU Volte, MO/MT Call,Data testing circle itself KPI:' GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly Session Establishment Success Rate -Sx CP_CUPS Session Establishment Success Rate -Sx UP_CUPS Session Modification Success Rate -Sx_CUPS S4S11 Create Session SR				Yes	Yes	IMS, Google, BNG	Top-On Weightage Changes  in DNS	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	381
391	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH	MAHNAGEMME01,\nMAHPUNEMME02,\nMAHPUNEMME04,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA ( 30 Mins Data & Volte services may be impacted) NO M2M Services Impact	Testing: - Basic MO/MT/VOLTE call/Data testing circle itself				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	3	382
392	66	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005576797	High	1-Extensive/Widespread	West	MH	MAHNAGEMME01,\nMAHPUNEMME02,\nMAHPUNEMME04,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	GCAP Value Modification for MHKHARHCK07ERPCCSM11 Go-live	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	Yes	Impact-SA ( 30 Mins Data & Volte services may be impacted) NO M2M Services Impact	Testing: - Basic MO/MT/VOLTE call/Data testing circle itself				Yes	No		G-Cap value Change in MME	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	3	382
393	23	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	Medium	2-Significant/Large	East	BH	BIHBGPEMME02,\nBIHPATEMME01,\nBIHBGPEMME04,\nBHPATRHCK01ERPCCMM07,\nBIHRANEMME05,\nBIHPATEMME03,\nBHRANRHCK01ERPCCMM06,\nBHRPTRHCK02ERPCCMM08,\nBHPATRHCK06ERPCCMM09	9	CR for New IR Definition in MME & PCCMM	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	NSA	Testing Not Required				No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	388
394	23	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005582878	Medium	2-Significant/Large	East	BH	BIHBGPEMME02,\nBIHPATEMME01,\nBIHBGPEMME04,\nBHPATRHCK01ERPCCMM07,\nBIHRANEMME05,\nBIHPATEMME03,\nBHRANRHCK01ERPCCMM06,\nBHRPTRHCK02ERPCCMM08,\nBHPATRHCK06ERPCCMM09	9	CR for New IR Definition in MME & PCCMM	No	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	NSA	Testing Not Required				No	No		IR IMSI VOLTE/5G Addition/Deletion/Modification in MME	Ericsson/Huawei/Nokia/Cisco/Dell/HP				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	2	388
395	3	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	High	2-Significant/Large	West	MU	MUMSPEEMME03,\nMUSPTRHCK01ERPCCMM04,\nMUMSPEEMME02,\nMUMCHAEMME01,\nMUMCHARHCK02ERPCCMM05	5	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	NSA	Test plan & KPI:NA				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	387
396	3	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583425	High	2-Significant/Large	West	MU	MUMSPEEMME03,\nMUSPTRHCK01ERPCCMM04,\nMUMSPEEMME02,\nMUMCHAEMME01,\nMUMCHARHCK02ERPCCMM05	5	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	NSA	Test plan & KPI:NA				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	2	387
397	2	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	High	2-Significant/Large	West	MH	MAHPUNEMME04,\nMAHPUNEMME02,\nMAHNAGEMME01,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	Impact - NSA No services will be affected	Testing:-No testing Required. KPI:NO KPI Required.				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				f	2	386
398	2	MS	2026-09-17	00:00:00 - 06:00:00	CRQ000005583428	High	2-Significant/Large	West	MH	MAHPUNEMME04,\nMAHPUNEMME02,\nMAHNAGEMME01,\nMAHPUNEMME05,\nMAHESPEMME07,\nMAHNAGEMME06,\nMHNA2RHCK01ERPCCMM08,\nMAHPUNEMME03,\nMHKHARHCK01ERPCCMM09,\nMHKHARHCK05ERPCCMM10,\nMHKHARHCK08ERPCCMM11	11	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned	Enjoy Maity	Enjoy Maity			Enjoy Maity	No	Impact - NSA No services will be affected	Testing:-No testing Required. KPI:NO KPI Required.				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-16 18:30:00+00	2026-09-17 00:30:00+00				t	2	386
403	5	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597711	Critical	1-Extensive/Widespread	South	AP		6	New ASBC81 Go-live with AP Ericsson EPGs	No						Enjoy Maity	Yes						No	Yes	IMS/DRA KPI	SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
404	6	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597707	High	1-Extensive/Widespread	South	KL		8	CR for NF ID whitelisting in the NRF for the New non-live KLPOLCK06NCMM05	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
405	7	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005597523	High	1-Extensive/Widespread	West	MH		13	BPMS - Ericsson MME Update - E2E version 1.91	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS - Ericsson MME Update - E2E version 1.91	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
406	8	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597150	High	1-Extensive/Widespread	West	MU		5	CR for RC value change in MUM Eric MME for 4G & 5G traffic loading on PCCMM04	No						Enjoy Maity	Yes						No	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
407	9	MS	2026-09-30	23:00:00 - 06:00:00	CRQ000005597111	High	1-Extensive/Widespread	North	HR		4	N8 UDM HTTP2 to NAS 5G-MM CC Mapping Alignment to CC27 in HR AMF	No						Enjoy Maity	Yes						No	No		New Nokia CMM related Configuration	Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 00:30:00+00				t	1	\N
408	10	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596922	Medium	2-Significant/Large				2	RJ Circle_MPS cell update for migration	No						Enjoy Maity	No						Yes	Yes	Not required	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Ericsson				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
409	11	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596793	High	1-Extensive/Widespread	West	MH		13	BPMS - Ericsson MME Update Precheck - E2E	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS - Ericsson MME Update Precheck - E2E	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
410	12	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596790	Critical	1-Extensive/Widespread	West	MH		11	BPMS-Ericsson MME Update Pre Subs.clear & RC change - E2E	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS-Ericsson MME Update Pre Subs.clear & RC change - E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
411	13	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596788	High	1-Extensive/Widespread	South	KK		12	KKASBC80 traffic opening from KK Ericsson GWs 3,5,6,7,8,9	No						Enjoy Maity	Yes						No	Yes	IMS/DRA KPI	SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
412	14	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596787	High	2-Significant/Large	South	KK		2	jiobhometerv6 APN creation in KKMGRNM2MCP01/ KKMGRNM2MCP01U01	No						Enjoy Maity	No						Yes	No	No testing & No KPI required for cache clear IP resolution need to check	M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
413	15	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596786	High	2-Significant/Large	South	KK		5	PBI000000269920: Learning-Vulnerability mitigation in E// MMEs(SSH Weak MAC/KEY )	No						Enjoy Maity	No						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
414	16	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596784	High	1-Extensive/Widespread	South	KK		9	SGs pool addition for LAC- 26761,2,21812,4,5,26591,2,3,4,5 (Hubli/MLR Pool VLRs) in KKMMEs-Ph-26	No						Enjoy Maity	Yes						No	No	No testing & No KPI required for cache clear IP resolution need to check	CSFB Related Changes	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
415	17	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596770	High	2-Significant/Large	South	TN		3	System and User backup for IPWorks version update 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	No						Yes	No		Patch Update Prerequisite	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
416	18	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596766	High	1-Extensive/Widespread	South	TN		8	Traffic diversion from TN E// MMEs & Revertback for IPWorks DNS 2.13 Update in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Traffic diversions	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
417	19	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596756	Low	1-Extensive/Widespread	West	GJ		2	Domain whitelisting in data expire and throttle rules_GJCHANA2CP01U01	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
418	20	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596748	High	2-Significant/Large	North	DL		2	CR for New PCCSM7 host & p2p config in DL SAPC PAIR1	No						Enjoy Maity	No						No	Yes	IMS KPI, Oracle DRA KPI.	Host name addition in SAPC	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
419	21	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596719	Medium	2-Significant/Large	South	CH		2	New APN creation in  CHSIRNM2MCP02/ CHSIRNM2MCP02UP02 -etplgedv6	No						Enjoy Maity	No						No	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
421	23	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596668	High	1-Extensive/Widespread	South	CH		6	PBI000000269910:Buffer size increase in CHN MMEs to resolve issue with large number of cells for CBC	No						Enjoy Maity	Yes						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
422	24	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596667	High	1-Extensive/Widespread	South	TN		10	New Prepaid South CCAF config and test number routing in TNC_PCCSM	No						Enjoy Maity	Yes						No	No		Test IMSI definition service in live nodes due to new node	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
423	25	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596665	High	1-Extensive/Widespread	South	TN		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Software Update Package upload	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
425	27	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596632	High	1-Extensive/Widespread	West	MH		2	etplgedv6 APN Creation in MHKHRNM2MCP02_MHKHRNM2MCP02UP02	No						Enjoy Maity	Yes						No	No		M2M : APN Creation/Deletion/Modification	Nokia/Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
426	28	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596626	Critical	1-Extensive/Widespread	West	RJ		2	PBI000000269790:learning for Alarm_Certificate Management Certificate is to Expire in SAPC Pair-2	No						Enjoy Maity	Yes						No	Yes	IMS, Oracle DRA Team aligned	New Learning implementation in SAPC	Ericsson				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
427	29	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596602	Low	1-Extensive/Widespread	West	GJ		2	4G/5G home & FWA MDU Traffic Balancing from GUJ DNSs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
428	30	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596596	Medium	2-Significant/Large	North	DL		2	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
429	31	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596589	High	1-Extensive/Widespread	South	TN		3	TNSIREDNS03_ vIPWorks Version Update from 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Software Update in DNS	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
430	32	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596540	Medium	2-Significant/Large	West	MH		13	Software Package loading for MAHPUNEMME02 1.91 update	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
431	33	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596535	High	1-Extensive/Widespread	West	MH		11	RMC value changes in E//MMEs for MAHPUNEMME02 Ver. Update from 1.84 to 1.91	No						Enjoy Maity	Yes						Yes	Yes		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
432	34	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596508	Medium	2-Significant/Large	North	JK		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS Static TEST IMSI Define/routing/Modify Ericsson MME E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
433	35	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596461	High	1-Extensive/Widespread	West	MH		1	PWS & CTUM learning Implementation in MAHPUNEMME02	No						Enjoy Maity	Yes						Yes	Yes		New Learning Implementation in SGSN/EPDG/MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
434	36	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596458	High	1-Extensive/Widespread	West	MH		11	Subscribers movement in E//MMEs via Pool Move operation for MAHPUNEMME02 SW update	No						Enjoy Maity	Yes						Yes	Yes		Subs. offloading from  MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
435	37	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596440	High	2-Significant/Large	North	JK		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
436	38	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596426	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
437	39	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596300	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
438	40	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596099	Low	1-Extensive/Widespread	West	GJ		6	FWA MDU Traffic Loading & Balancing from GUJ MMEs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
439	41	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596035	High	1-Extensive/Widespread	South	AP		3	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
440	42	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595985	Low	1-Extensive/Widespread	North	UPE		5	Junk NB-IOT TACs deletion from Nokia CMMs ( 4000 / 4011)	No						Enjoy Maity	No						No	No		Non Live TAC-LAC Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
441	43	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595924	Medium	2-Significant/Large	North	DL		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
442	44	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595914	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
443	45	MS	2026-09-30	23:00:00 - 06:00:00	CRQ000005595557	Low	2-Significant/Large				100	MAH_2G_MPS CELL DATA UPLOAD ACTIVITY	No						Enjoy Maity	No						Yes	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-29 17:30:00+00	2026-09-30 00:30:00+00				t	1	\N
444	46	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005595334	Low	1-Extensive/Widespread	North	UPE		24	DNS weightages change in Nokia DNS & VAR DNS for Gangaganj Nokia CP05 CMG upgrade	No						Enjoy Maity	Yes						Yes	No	IMS / DRA / BNG KPIs	Top-On Weightage Changes  in DNS	Cisco/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
445	47	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005595150	Low	1-Extensive/Widespread	North	UPE		16	Subscribers offloading  & balancing  from UPE All GGSN for Gangaganj Nokia CP05 CMG	No						Enjoy Maity	Yes						Yes	No		Subs. Purging due to Other Dependent Activities	Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
446	48	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595109	Medium	2-Significant/Large	North	DL		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
447	49	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594425	High	1-Extensive/Widespread	South	CH		2	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
448	50	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594403	Medium	2-Significant/Large	West	GJ		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
449	51	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594171	High	1-Extensive/Widespread	South	TN		3	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
451	53	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005590783	Low	1-Extensive/Widespread	West	MP		7	New ASBC-33 Go-Live from E//PGWs	No						Enjoy Maity	Yes						No	No		SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
399	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP		4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No						Enjoy Maity	Yes						No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
400	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP		1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No						Enjoy Maity	Yes						Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
401	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP		2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No						Enjoy Maity	No						Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
402	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP		3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No						Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
420	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
424	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN		7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	1	\N
457	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN		7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	1	\N
450	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ		2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
458	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN		7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	unplanned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	1	\N
452	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP		4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes						No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
453	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP		1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes						Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
454	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP		2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No						Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
468	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP	APVIJNM2MCP01U01,\nAPVIJNM2MCP01	2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No	NSA, M2M services no impact	Non-live APN no testing required APVIJNM2MCP01,APVIJNM2MCP01U01 KPI GGSN PDP SR_Combained -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly (Througput Crtiteria > D,D-1, D-7 at node and circle level ( Nokia, Cisco & E )				Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	467
469	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP	APVIJNM2MCP01U01,\nAPVIJNM2MCP01	2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No	NSA, M2M services no impact	Non-live APN no testing required APVIJNM2MCP01,APVIJNM2MCP01U01 KPI GGSN PDP SR_Combained -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly (Througput Crtiteria > D,D-1, D-7 at node and circle level ( Nokia, Cisco & E )				Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	468
455	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP		3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
456	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
459	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ		2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes						Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
460	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN		7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	1	\N
461	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP	APVIJRHCK03ERPCGUP06,\nAPVIJRHCK03ERPCCSM06,\nAPVIJRHCK04ERPCGUP08,\nAPVIJRHCK04ERPCCSM08	4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes	SA,In Worst case 15-30 Min airtelfwamdu Services will be impacted	Basic testing will be done by circle APVIJRHCK03ERPCCSM06, APVIJRHCK03ERPCGUP06,APVIJRHCK04ERPCCSM08, APVIJRHCK04ERPCGUP08 KPI -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI -Session Establishment Success Rate -Sx CP_CUPS -Session Establishment Success Rate -Sx UP_CUPS -Session Modification Success Rate -Sx_CUPS -S4S11 Create Session SR 5G SA N1 PDU Session Establishment SR per Slice and APN_5G_SA Nchf Converged Charging Create Success Rate_5G_SA Nchf Converged Charging Update Success Rate_5G_SA Npcf SM Policy Control Create Success Rate_5G_SA Npcf SM Policy Control Update Success Rate_5G_SA FWA KPI GX_CCR_I SR Per APN_EPG3.X GX_CCR_T SR Per APN_EPG3.X GX_CCR_U SR Per APN_EPG3.X PGW Create Bearer SR Per APN_EPG3.X Active EPS Bearers per APN in the PGW-C_EPG3.X_Max FWA testing and BNG team aligned.				No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	452
462	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP	APVIJRHCK03ERPCGUP06,\nAPVIJRHCK03ERPCCSM06,\nAPVIJRHCK04ERPCGUP08,\nAPVIJRHCK04ERPCCSM08	4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes	SA,In Worst case 15-30 Min airtelfwamdu Services will be impacted	Basic testing will be done by circle APVIJRHCK03ERPCCSM06, APVIJRHCK03ERPCGUP06,APVIJRHCK04ERPCCSM08, APVIJRHCK04ERPCGUP08 KPI -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI -Session Establishment Success Rate -Sx CP_CUPS -Session Establishment Success Rate -Sx UP_CUPS -Session Modification Success Rate -Sx_CUPS -S4S11 Create Session SR 5G SA N1 PDU Session Establishment SR per Slice and APN_5G_SA Nchf Converged Charging Create Success Rate_5G_SA Nchf Converged Charging Update Success Rate_5G_SA Npcf SM Policy Control Create Success Rate_5G_SA Npcf SM Policy Control Update Success Rate_5G_SA FWA KPI GX_CCR_I SR Per APN_EPG3.X GX_CCR_T SR Per APN_EPG3.X GX_CCR_U SR Per APN_EPG3.X PGW Create Bearer SR Per APN_EPG3.X Active EPS Bearers per APN in the PGW-C_EPG3.X_Max FWA testing and BNG team aligned.				No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	461
463	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP	APVIJRHCK03ERPCGUP06,\nAPVIJRHCK03ERPCCSM06,\nAPVIJRHCK04ERPCGUP08,\nAPVIJRHCK04ERPCCSM08	4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes	SA,In Worst case 15-30 Min airtelfwamdu Services will be impacted	Basic testing will be done by circle APVIJRHCK03ERPCCSM06, APVIJRHCK03ERPCGUP06,APVIJRHCK04ERPCCSM08, APVIJRHCK04ERPCGUP08 KPI -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI -Session Establishment Success Rate -Sx CP_CUPS -Session Establishment Success Rate -Sx UP_CUPS -Session Modification Success Rate -Sx_CUPS -S4S11 Create Session SR 5G SA N1 PDU Session Establishment SR per Slice and APN_5G_SA Nchf Converged Charging Create Success Rate_5G_SA Nchf Converged Charging Update Success Rate_5G_SA Npcf SM Policy Control Create Success Rate_5G_SA Npcf SM Policy Control Update Success Rate_5G_SA FWA KPI GX_CCR_I SR Per APN_EPG3.X GX_CCR_T SR Per APN_EPG3.X GX_CCR_U SR Per APN_EPG3.X PGW Create Bearer SR Per APN_EPG3.X Active EPS Bearers per APN in the PGW-C_EPG3.X_Max FWA testing and BNG team aligned.				No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	462
464	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP	APGGSN1	1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be done by circle APGGSN1 KPI '-GGSN PDP SR_Combained -GGSN Thpt_Gbps_Combained_Hourly				Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	453
465	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP	APGGSN1	1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be done by circle APGGSN1 KPI '-GGSN PDP SR_Combained -GGSN Thpt_Gbps_Combained_Hourly				Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	464
466	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP	APGGSN1	1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be done by circle APGGSN1 KPI '-GGSN PDP SR_Combained -GGSN Thpt_Gbps_Combained_Hourly				Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	465
467	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP	APVIJNM2MCP01U01,\nAPVIJNM2MCP01	2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No	NSA, M2M services no impact	Non-live APN no testing required APVIJNM2MCP01,APVIJNM2MCP01U01 KPI GGSN PDP SR_Combained -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly (Througput Crtiteria > D,D-1, D-7 at node and circle level ( Nokia, Cisco & E )				Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	454
470	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP	APVIJEDNS03,\nAPUPLEDNS05,\nAPUPPEDNS01	3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be aligned by Ashish APN Resolution need to be Checked from MME & DNS - APUPPEDNS01,APVIJEDNS03,APUPLEDNS05,APUPPEMME01,APVIJEMME02,APUPPEMME03,APVIJEMME04,APVIJEMME05,APUPLRHCK01ERPCCMM06,APVIJRHCK01ERPCCMM07,APUPLRHCK03ERPCCMM08 APGGSN1,TNSANEEPG03 KPI -GGSN PDP SR_Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly GGSN PGW Bearer_Combained_Hourly GGSN SGW Bearer_Combained_Hourly				Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	455
471	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP	APVIJEDNS03,\nAPUPLEDNS05,\nAPUPPEDNS01	3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be aligned by Ashish APN Resolution need to be Checked from MME & DNS - APUPPEDNS01,APVIJEDNS03,APUPLEDNS05,APUPPEMME01,APVIJEMME02,APUPPEMME03,APVIJEMME04,APVIJEMME05,APUPLRHCK01ERPCCMM06,APVIJRHCK01ERPCCMM07,APUPLRHCK03ERPCCMM08 APGGSN1,TNSANEEPG03 KPI -GGSN PDP SR_Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly GGSN PGW Bearer_Combained_Hourly GGSN SGW Bearer_Combained_Hourly				Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	470
472	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP	APVIJEDNS03,\nAPUPLEDNS05,\nAPUPPEDNS01	3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be aligned by Ashish APN Resolution need to be Checked from MME & DNS - APUPPEDNS01,APVIJEDNS03,APUPLEDNS05,APUPPEMME01,APVIJEMME02,APUPPEMME03,APVIJEMME04,APVIJEMME05,APUPLRHCK01ERPCCMM06,APVIJRHCK01ERPCCMM07,APUPLRHCK03ERPCCMM08 APGGSN1,TNSANEEPG03 KPI -GGSN PDP SR_Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly GGSN PGW Bearer_Combained_Hourly GGSN SGW Bearer_Combained_Hourly				Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	471
473	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP	APUPPEMME01,\nAPVIJEMME02,\nAPVIJEMME05,\nAPVIJEMME04,\nAPUPLRHCK01ERPCCMM06,\nAPUPPEMME03,\nAPVIJRHCK01ERPCCMM07,\nAPUPLRHCK03ERPCCMM08	8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA, M2M services no impact	No testing required for cache clear				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	456
474	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP	APUPPEMME01,\nAPVIJEMME02,\nAPVIJEMME05,\nAPVIJEMME04,\nAPUPLRHCK01ERPCCMM06,\nAPUPPEMME03,\nAPVIJRHCK01ERPCCMM07,\nAPUPLRHCK03ERPCCMM08	8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA, M2M services no impact	No testing required for cache clear				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	473
475	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP	APUPPEMME01,\nAPVIJEMME02,\nAPVIJEMME05,\nAPVIJEMME04,\nAPUPLRHCK01ERPCCMM06,\nAPUPPEMME03,\nAPVIJRHCK01ERPCCMM07,\nAPUPLRHCK03ERPCCMM08	8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA, M2M services no impact	No testing required for cache clear				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	474
476	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ	GUJRAJEDNS01,\nGUJCHAEDNS03	2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes	SA ( 10 to 15 min Voice/Data Service impact in worst Case)	Test/KPI : Pre & post testing required. GUJCHAEDNS03,GUJRAJEDNS01 KPI : Resolution check from DNS & MME KPI - GJCHGRHCK01ERPCCSM02 / GJCHGRHCK01ERPCGUP03 / GJRJTRHCK01ERPCCSM03 / GUJRAJCC02EREPGUP02 / GJCHGRHCK03ERPCCSM04 / GJCHGRHCK03ERPCGUP04 / GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Node - GUJCHAEDNS03,GUJRAJEDNS01 Basic testing will be done by circle team. IMS team aligned.				Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	2	459
477	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ	GUJRAJEDNS01,\nGUJCHAEDNS03	2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes	SA ( 10 to 15 min Voice/Data Service impact in worst Case)	Test/KPI : Pre & post testing required. GUJCHAEDNS03,GUJRAJEDNS01 KPI : Resolution check from DNS & MME KPI - GJCHGRHCK01ERPCCSM02 / GJCHGRHCK01ERPCGUP03 / GJRJTRHCK01ERPCCSM03 / GUJRAJCC02EREPGUP02 / GJCHGRHCK03ERPCCSM04 / GJCHGRHCK03ERPCGUP04 / GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Node - GUJCHAEDNS03,GUJRAJEDNS01 Basic testing will be done by circle team. IMS team aligned.				Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	3	476
478	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ	GUJRAJEDNS01,\nGUJCHAEDNS03	2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes	SA ( 10 to 15 min Voice/Data Service impact in worst Case)	Test/KPI : Pre & post testing required. GUJCHAEDNS03,GUJRAJEDNS01 KPI : Resolution check from DNS & MME KPI - GJCHGRHCK01ERPCCSM02 / GJCHGRHCK01ERPCGUP03 / GJRJTRHCK01ERPCCSM03 / GUJRAJCC02EREPGUP02 / GJCHGRHCK03ERPCCSM04 / GJCHGRHCK03ERPCGUP04 / GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Node - GUJCHAEDNS03,GUJRAJEDNS01 Basic testing will be done by circle team. IMS team aligned.				Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	4	477
479	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN	TNSANEMME03,\nTNSIREMME02,\nTNPOLEMME01,\nTNSIREMME04,\nTNSIREMME05,\nTNSIRRHCK01ERPCCMM06,\nTNPOLRHCK01ERPCCMM07	7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA	No Test & No KPI Check				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	2	460
480	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN	TNSANEMME03,\nTNSIREMME02,\nTNPOLEMME01,\nTNSIREMME04,\nTNSIREMME05,\nTNSIRRHCK01ERPCCMM06,\nTNPOLRHCK01ERPCCMM07	7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA	No Test & No KPI Check				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	3	479
481	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN	TNSANEMME03,\nTNSIREMME02,\nTNPOLEMME01,\nTNSIREMME04,\nTNSIREMME05,\nTNSIRRHCK01ERPCCMM06,\nTNPOLRHCK01ERPCCMM07	7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA	No Test & No KPI Check				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	4	480
\.


--
-- Data for Name: selected_date_table; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.selected_date_table (id, sno, ms_project, execution_date, maintenance_window, cr_no, priority, risk, region, circle, node_details, node_count, activity_description, bpms_cr_yes_no, planning_status, activity_executor, auditor_name, activity_status, reason_for_rollback_cancel, technical_validator, service_affecting, impact, test_cases, kpi_name, kpi_spoc_night, kpi_spoc_morning, inter_domain_activity, inter_domain_kpi_required, inter_domain_measuring_kpis, activity_type, vendor, protocol, execution_type, cli_availability, team, scheduled_start_date, scheduled_end_date, niam_ticket_required, niam_node_type, additional_info, is_active, version, parent_reference_id) FROM stdin;
1582	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP		4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes						No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1589	1	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597809	High	1-Extensive/Widespread	South	AP	APVIJRHCK03ERPCGUP06,\nAPVIJRHCK03ERPCCSM06,\nAPVIJRHCK04ERPCGUP08,\nAPVIJRHCK04ERPCCSM08	4	APN airtelfwamdu.com IPV4 pools Unblock in AP PCCSM06 & PCCSM08	No	planned					Enjoy Maity	Yes	SA,In Worst case 15-30 Min airtelfwamdu Services will be impacted	Basic testing will be done by circle APVIJRHCK03ERPCCSM06, APVIJRHCK03ERPCGUP06,APVIJRHCK04ERPCCSM08, APVIJRHCK04ERPCGUP08 KPI -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly Ericsson -Sx KPI -Session Establishment Success Rate -Sx CP_CUPS -Session Establishment Success Rate -Sx UP_CUPS -Session Modification Success Rate -Sx_CUPS -S4S11 Create Session SR 5G SA N1 PDU Session Establishment SR per Slice and APN_5G_SA Nchf Converged Charging Create Success Rate_5G_SA Nchf Converged Charging Update Success Rate_5G_SA Npcf SM Policy Control Create Success Rate_5G_SA Npcf SM Policy Control Update Success Rate_5G_SA FWA KPI GX_CCR_I SR Per APN_EPG3.X GX_CCR_T SR Per APN_EPG3.X GX_CCR_U SR Per APN_EPG3.X PGW Create Bearer SR Per APN_EPG3.X Active EPS Bearers per APN in the PGW-C_EPG3.X_Max FWA testing and BNG team aligned.				No	No		IP Pool Addition/Deletion/Modification	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1582
1590	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP	APGGSN1	1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be done by circle APGGSN1 KPI '-GGSN PDP SR_Combained -GGSN Thpt_Gbps_Combained_Hourly				Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1583
1591	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP	APVIJNM2MCP01U01,\nAPVIJNM2MCP01	2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No	NSA, M2M services no impact	Non-live APN no testing required APVIJNM2MCP01,APVIJNM2MCP01U01 KPI GGSN PDP SR_Combained -GGSN GX SR _Combained -GGSN GY SR _Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly (Througput Crtiteria > D,D-1, D-7 at node and circle level ( Nokia, Cisco & E )				Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1584
1592	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP	APVIJEDNS03,\nAPUPLEDNS05,\nAPUPPEDNS01	3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes	SA,15-30 Min MPLS APN:-ghmc.ibigroup.com services will impact	Basic testing will be aligned by Ashish APN Resolution need to be Checked from MME & DNS - APUPPEDNS01,APVIJEDNS03,APUPLEDNS05,APUPPEMME01,APVIJEMME02,APUPPEMME03,APVIJEMME04,APVIJEMME05,APUPLRHCK01ERPCCMM06,APVIJRHCK01ERPCCMM07,APUPLRHCK03ERPCCMM08 APGGSN1,TNSANEEPG03 KPI -GGSN PDP SR_Combained -GGSN Bearer Creation SR _Combained -GGSN Thpt_Gbps_Combained_Hourly GGSN PGW Bearer_Combained_Hourly GGSN SGW Bearer_Combained_Hourly				Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1585
1593	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP	APUPPEMME01,\nAPVIJEMME02,\nAPVIJEMME05,\nAPVIJEMME04,\nAPUPLRHCK01ERPCCMM06,\nAPUPPEMME03,\nAPVIJRHCK01ERPCCMM07,\nAPUPLRHCK03ERPCCMM08	8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA, M2M services no impact	No testing required for cache clear				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1586
1594	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ	GUJRAJEDNS01,\nGUJCHAEDNS03	2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes	SA ( 10 to 15 min Voice/Data Service impact in worst Case)	Test/KPI : Pre & post testing required. GUJCHAEDNS03,GUJRAJEDNS01 KPI : Resolution check from DNS & MME KPI - GJCHGRHCK01ERPCCSM02 / GJCHGRHCK01ERPCGUP03 / GJRJTRHCK01ERPCCSM03 / GUJRAJCC02EREPGUP02 / GJCHGRHCK03ERPCCSM04 / GJCHGRHCK03ERPCGUP04 / GJRJTRHCK02ERPCCSM05 / GJRJTRHCK02ERPCGUP05 GGSN Bearer Creation SR _Combained GGSN PDP SR_Combained GGSN Thpt_Gbps_Combained_Hourly GGSN GX SR _Combained GGSN GY SR _Combained Node - GUJCHAEDNS03,GUJRAJEDNS01 Basic testing will be done by circle team. IMS team aligned.				Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	2	1587
1536	5	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597711	Critical	1-Extensive/Widespread	South	AP		6	New ASBC81 Go-live with AP Ericsson EPGs	No						Enjoy Maity	Yes						No	Yes	IMS/DRA KPI	SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1537	6	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597707	High	1-Extensive/Widespread	South	KL		8	CR for NF ID whitelisting in the NRF for the New non-live KLPOLCK06NCMM05	No						Enjoy Maity	Yes						No	No		New NRF Related configuration	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1538	7	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005597523	High	1-Extensive/Widespread	West	MH		13	BPMS - Ericsson MME Update - E2E version 1.91	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS - Ericsson MME Update - E2E version 1.91	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1539	8	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597150	High	1-Extensive/Widespread	West	MU		5	CR for RC value change in MUM Eric MME for 4G & 5G traffic loading on PCCMM04	No						Enjoy Maity	Yes						No	No		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1540	9	MS	2026-09-30	23:00:00 - 06:00:00	CRQ000005597111	High	1-Extensive/Widespread	North	HR		4	N8 UDM HTTP2 to NAS 5G-MM CC Mapping Alignment to CC27 in HR AMF	No						Enjoy Maity	Yes						No	No		New Nokia CMM related Configuration	Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1541	10	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596922	Medium	2-Significant/Large				2	RJ Circle_MPS cell update for migration	No						Enjoy Maity	No						Yes	Yes	Not required	BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Ericsson				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1542	11	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596793	High	1-Extensive/Widespread	West	MH		13	BPMS - Ericsson MME Update Precheck - E2E	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS - Ericsson MME Update Precheck - E2E	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1543	12	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596790	Critical	1-Extensive/Widespread	West	MH		11	BPMS-Ericsson MME Update Pre Subs.clear & RC change - E2E	Yes						Enjoy Maity	Yes						Yes	Yes		BPMS-Ericsson MME Update Pre Subs.clear & RC change - E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1544	13	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596788	High	1-Extensive/Widespread	South	KK		12	KKASBC80 traffic opening from KK Ericsson GWs 3,5,6,7,8,9	No						Enjoy Maity	Yes						No	Yes	IMS/DRA KPI	SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1545	14	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596787	High	2-Significant/Large	South	KK		2	jiobhometerv6 APN creation in KKMGRNM2MCP01/ KKMGRNM2MCP01U01	No						Enjoy Maity	No						Yes	No	No testing & No KPI required for cache clear IP resolution need to check	M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1546	15	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596786	High	2-Significant/Large	South	KK		5	PBI000000269920: Learning-Vulnerability mitigation in E// MMEs(SSH Weak MAC/KEY )	No						Enjoy Maity	No						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1547	16	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596784	High	1-Extensive/Widespread	South	KK		9	SGs pool addition for LAC- 26761,2,21812,4,5,26591,2,3,4,5 (Hubli/MLR Pool VLRs) in KKMMEs-Ph-26	No						Enjoy Maity	Yes						No	No	No testing & No KPI required for cache clear IP resolution need to check	CSFB Related Changes	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1548	17	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596770	High	2-Significant/Large	South	TN		3	System and User backup for IPWorks version update 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	No						Yes	No		Patch Update Prerequisite	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1549	18	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596766	High	1-Extensive/Widespread	South	TN		8	Traffic diversion from TN E// MMEs & Revertback for IPWorks DNS 2.13 Update in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Traffic diversions	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1550	19	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596756	Low	1-Extensive/Widespread	West	GJ		2	Domain whitelisting in data expire and throttle rules_GJCHANA2CP01U01	No						Enjoy Maity	Yes						No	No		DPI /SPI related Changes in GGSN	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1551	20	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596748	High	2-Significant/Large	North	DL		2	CR for New PCCSM7 host & p2p config in DL SAPC PAIR1	No						Enjoy Maity	No						No	Yes	IMS KPI, Oracle DRA KPI.	Host name addition in SAPC	Ericsson / Cisco / HP / DELL / Nokia				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1552	21	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596719	Medium	2-Significant/Large	South	CH		2	New APN creation in  CHSIRNM2MCP02/ CHSIRNM2MCP02UP02 -etplgedv6	No						Enjoy Maity	No						No	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1553	23	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596668	High	1-Extensive/Widespread	South	CH		6	PBI000000269910:Buffer size increase in CHN MMEs to resolve issue with large number of cells for CBC	No						Enjoy Maity	Yes						No	No		New Learning Implementation in SGSN/EPDG/MME	Ericsson/HP/IBM/Dell				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1554	24	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596667	High	1-Extensive/Widespread	South	TN		10	New Prepaid South CCAF config and test number routing in TNC_PCCSM	No						Enjoy Maity	Yes						No	No		Test IMSI definition service in live nodes due to new node	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1555	25	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596665	High	1-Extensive/Widespread	South	TN		3	S/W Package Loading for vIPWorks version update 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Software Update Package upload	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1556	27	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596632	High	1-Extensive/Widespread	West	MH		2	etplgedv6 APN Creation in MHKHRNM2MCP02_MHKHRNM2MCP02UP02	No						Enjoy Maity	Yes						No	No		M2M : APN Creation/Deletion/Modification	Nokia/Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1557	28	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596626	Critical	1-Extensive/Widespread	West	RJ		2	PBI000000269790:learning for Alarm_Certificate Management Certificate is to Expire in SAPC Pair-2	No						Enjoy Maity	Yes						No	Yes	IMS, Oracle DRA Team aligned	New Learning implementation in SAPC	Ericsson				VAS	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1558	29	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596602	Low	1-Extensive/Widespread	West	GJ		2	4G/5G home & FWA MDU Traffic Balancing from GUJ DNSs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1559	30	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596596	Medium	2-Significant/Large	North	DL		2	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1560	31	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596589	High	1-Extensive/Widespread	South	TN		3	TNSIREDNS03_ vIPWorks Version Update from 2.11 to 2.13 in TNSIREDNS03	No						Enjoy Maity	Yes						Yes	No		Software Update in DNS	Ericsson/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1561	32	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596540	Medium	2-Significant/Large	West	MH		13	Software Package loading for MAHPUNEMME02 1.91 update	No						Enjoy Maity	No						Yes	No		Software Update Package upload	Ericsson/Extreme/Cisco/Dell/HP				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1562	33	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596535	High	1-Extensive/Widespread	West	MH		11	RMC value changes in E//MMEs for MAHPUNEMME02 Ver. Update from 1.84 to 1.91	No						Enjoy Maity	Yes						Yes	Yes		RC Value Changes in Addition/Deletion/Modification in MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1563	34	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596508	Medium	2-Significant/Large	North	JK		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS Static TEST IMSI Define/routing/Modify Ericsson MME E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1564	35	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596461	High	1-Extensive/Widespread	West	MH		1	PWS & CTUM learning Implementation in MAHPUNEMME02	No						Enjoy Maity	Yes						Yes	Yes		New Learning Implementation in SGSN/EPDG/MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1565	36	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596458	High	1-Extensive/Widespread	West	MH		11	Subscribers movement in E//MMEs via Pool Move operation for MAHPUNEMME02 SW update	No						Enjoy Maity	Yes						Yes	Yes		Subs. offloading from  MME	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1566	37	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596440	High	2-Significant/Large	North	JK		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1567	38	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596426	High	2-Significant/Large	West	GJ		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1568	39	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596300	High	2-Significant/Large	South	KL		4	BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Yes						Enjoy Maity	No						No	No		BPMS - Test IMSI Addition_Modification in Nokia CMM - E2E	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1569	40	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596099	Low	1-Extensive/Widespread	West	GJ		6	FWA MDU Traffic Loading & Balancing from GUJ MMEs	No						Enjoy Maity	Yes						Yes	No		Traffic Balancing & Bypass	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1570	41	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596035	High	1-Extensive/Widespread	South	AP		3	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1571	42	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595985	Low	1-Extensive/Widespread	North	UPE		5	Junk NB-IOT TACs deletion from Nokia CMMs ( 4000 / 4011)	No						Enjoy Maity	No						No	No		Non Live TAC-LAC Addition/Deletion/Modification in MME	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1572	43	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595924	Medium	2-Significant/Large	North	DL		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1573	44	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595914	High	2-Significant/Large	North	DL		6	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes						Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1574	45	MS	2026-09-30	23:00:00 - 06:00:00	CRQ000005595557	Low	2-Significant/Large				100	MAH_2G_MPS CELL DATA UPLOAD ACTIVITY	No						Enjoy Maity	No						Yes	No		BPMS - MPS Cell Data Upload Ericsson & Nokia - E2E	Nokia				VAS	2026-09-29 17:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1575	46	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005595334	Low	1-Extensive/Widespread	North	UPE		24	DNS weightages change in Nokia DNS & VAR DNS for Gangaganj Nokia CP05 CMG upgrade	No						Enjoy Maity	Yes						Yes	No	IMS / DRA / BNG KPIs	Top-On Weightage Changes  in DNS	Cisco/Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1576	47	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005595150	Low	1-Extensive/Widespread	North	UPE		16	Subscribers offloading  & balancing  from UPE All GGSN for Gangaganj Nokia CP05 CMG	No						Enjoy Maity	Yes						Yes	No		Subs. Purging due to Other Dependent Activities	Nokia				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	1	\N
1577	48	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005595109	Medium	2-Significant/Large	North	DL		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1578	49	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594425	High	1-Extensive/Widespread	South	CH		2	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1579	50	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594403	Medium	2-Significant/Large	West	GJ		6	BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Yes						Enjoy Maity	No						No	No		BPMS -Test IMSI Add_Modify in Ericsson MME-PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1580	51	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005594171	High	1-Extensive/Widespread	South	TN		3	BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Yes						Enjoy Maity	Yes						Yes	No		BPMS - M2M_APN_ICR_Defn_in_Eric_DNS - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1581	53	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005590783	Low	1-Extensive/Widespread	West	MP		7	New ASBC-33 Go-Live from E//PGWs	No						Enjoy Maity	Yes						No	No		SBC Related Changes in Ericsson EPG	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				t	1	\N
1583	2	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597746	High	1-Extensive/Widespread	South	AP		1	PDP flush MPLS APN:-ghmc.ibigroup.com in APGGSN1 for Migration to TNSANEEPG03	No	planned					Enjoy Maity	Yes						Yes	No		Subs. clear of APN from  GGSN -M2M	Huawei				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1584	3	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597717	High	2-Significant/Large	South	AP		2	New APN jiobhometerv6 creation in AP Nokiam2mcmg Nodes APVIJNM2MCP01 & APVIJNM2MCP01U01	No	planned					Enjoy Maity	No						Yes	No		M2M : APN Creation/Deletion/Modification	Nokia				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1585	4	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005597713	Critical	1-Extensive/Widespread	South	AP		3	MPLS APN:-ghmc.ibigroup.com Migration from APGGSN1 to TNSANEEPG03 in AP Ericsson DNS	No	planned					Enjoy Maity	Yes						Yes	No		M2M : Migration of Private APN	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1586	22	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005596687	High	2-Significant/Large	South	AP		8	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1587	52	MS	2026-09-30	00:00:00 - 06:00:00	CRQ000005593896	Medium	2-Significant/Large	West	GJ		2	BPMS - Top-ON Weightage changes  in Ericsson DNS (Without Coordination) - E2E	Yes	planned					Enjoy Maity	Yes						Yes	No		BPMS -Top-ON WC in Ericsson DNS (W /Co) - E2E	Ericsson				PS-CORE	2026-09-29 18:30:00+00	2026-09-30 00:30:00+00				f	1	\N
1588	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN		7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No						Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				f	1	\N
1595	26	MS	2026-09-30	23:00:00 - 07:00:00	CRQ000005596644	High	2-Significant/Large	South	TN	TNSANEMME03,\nTNSIREMME02,\nTNPOLEMME01,\nTNSIREMME04,\nTNSIREMME05,\nTNSIRRHCK01ERPCCMM06,\nTNPOLRHCK01ERPCCMM07	7	BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Yes	planned					Enjoy Maity	No	NSA	No Test & No KPI Check				Yes	No		BPMS-Cache Clear Ericsson MME_PCCMM-E2E	Ericsson				PS-CORE	2026-09-29 17:30:00+00	2026-09-30 01:30:00+00				t	2	1588
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 52, true);


--
-- Name: cr_wise_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cr_wise_status_id_seq', 431, true);


--
-- Name: dashboard_automationtask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_automationtask_id_seq', 1, false);


--
-- Name: dashboard_flagtable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_flagtable_id_seq', 1, false);


--
-- Name: dashboard_tasklog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_tasklog_id_seq', 1, false);


--
-- Name: dashboard_taskrun_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_taskrun_id_seq', 1, false);


--
-- Name: dashboard_usermanagement_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_usermanagement_groups_id_seq', 1, false);


--
-- Name: dashboard_usermanagement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_usermanagement_id_seq', 1, true);


--
-- Name: dashboard_usermanagement_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_usermanagement_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 13, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 19, true);


--
-- Name: master_cr_database_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.master_cr_database_id_seq', 481, true);


--
-- Name: selected_date_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.selected_date_table_id_seq', 1595, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: cr_wise_status cr_wise_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_wise_status
    ADD CONSTRAINT cr_wise_status_pkey PRIMARY KEY (id);


--
-- Name: dashboard_automationtask dashboard_automationtask_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_automationtask
    ADD CONSTRAINT dashboard_automationtask_pkey PRIMARY KEY (id);


--
-- Name: dashboard_automationtask dashboard_automationtask_sequence_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_automationtask
    ADD CONSTRAINT dashboard_automationtask_sequence_no_key UNIQUE (sequence_no);


--
-- Name: dashboard_flagtable dashboard_flagtable_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_flagtable
    ADD CONSTRAINT dashboard_flagtable_pkey PRIMARY KEY (id);


--
-- Name: dashboard_flagtable dashboard_flagtable_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_flagtable
    ADD CONSTRAINT dashboard_flagtable_source_id_key UNIQUE (source_id);


--
-- Name: dashboard_tasklog dashboard_tasklog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_tasklog
    ADD CONSTRAINT dashboard_tasklog_pkey PRIMARY KEY (id);


--
-- Name: dashboard_taskrun dashboard_taskrun_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_taskrun
    ADD CONSTRAINT dashboard_taskrun_pkey PRIMARY KEY (id);


--
-- Name: dashboard_usermanagement dashboard_usermanagement_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement
    ADD CONSTRAINT dashboard_usermanagement_email_key UNIQUE (email);


--
-- Name: dashboard_usermanagement dashboard_usermanagement_employee_signum_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement
    ADD CONSTRAINT dashboard_usermanagement_employee_signum_key UNIQUE (employee_signum);


--
-- Name: dashboard_usermanagement_groups dashboard_usermanagement_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_groups
    ADD CONSTRAINT dashboard_usermanagement_groups_pkey PRIMARY KEY (id);


--
-- Name: dashboard_usermanagement dashboard_usermanagement_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement
    ADD CONSTRAINT dashboard_usermanagement_pkey PRIMARY KEY (id);


--
-- Name: dashboard_usermanagement_user_permissions dashboard_usermanagement_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_user_permissions
    ADD CONSTRAINT dashboard_usermanagement_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: dashboard_usermanagement_groups dashboard_usermanagement_usermanagement_id_group__bb8ef0b2_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_groups
    ADD CONSTRAINT dashboard_usermanagement_usermanagement_id_group__bb8ef0b2_uniq UNIQUE (usermanagement_id, group_id);


--
-- Name: dashboard_usermanagement_user_permissions dashboard_usermanagement_usermanagement_id_permis_0210ac3a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_user_permissions
    ADD CONSTRAINT dashboard_usermanagement_usermanagement_id_permis_0210ac3a_uniq UNIQUE (usermanagement_id, permission_id);


--
-- Name: dashboard_usermanagement dashboard_usermanagement_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement
    ADD CONSTRAINT dashboard_usermanagement_username_key UNIQUE (username);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: master_cr_database master_cr_database_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.master_cr_database
    ADD CONSTRAINT master_cr_database_pkey PRIMARY KEY (id);


--
-- Name: selected_date_table selected_date_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.selected_date_table
    ADD CONSTRAINT selected_date_table_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: cr_wise_status_parent_reference_id_90e13541; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX cr_wise_status_parent_reference_id_90e13541 ON public.cr_wise_status USING btree (parent_reference_id);


--
-- Name: dashboard_flagtable_source_id_4ee10c22_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_flagtable_source_id_4ee10c22_like ON public.dashboard_flagtable USING btree (source_id varchar_pattern_ops);


--
-- Name: dashboard_tasklog_run_id_388392fe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_tasklog_run_id_388392fe ON public.dashboard_tasklog USING btree (run_id);


--
-- Name: dashboard_taskrun_task_id_18965367; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_taskrun_task_id_18965367 ON public.dashboard_taskrun USING btree (task_id);


--
-- Name: dashboard_taskrun_triggered_by_id_5a8e4505; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_taskrun_triggered_by_id_5a8e4505 ON public.dashboard_taskrun USING btree (triggered_by_id);


--
-- Name: dashboard_usermanagement_email_93b9650d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_email_93b9650d_like ON public.dashboard_usermanagement USING btree (email varchar_pattern_ops);


--
-- Name: dashboard_usermanagement_employee_signum_da849a28_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_employee_signum_da849a28_like ON public.dashboard_usermanagement USING btree (employee_signum varchar_pattern_ops);


--
-- Name: dashboard_usermanagement_groups_group_id_bf06518f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_groups_group_id_bf06518f ON public.dashboard_usermanagement_groups USING btree (group_id);


--
-- Name: dashboard_usermanagement_groups_usermanagement_id_3d81d927; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_groups_usermanagement_id_3d81d927 ON public.dashboard_usermanagement_groups USING btree (usermanagement_id);


--
-- Name: dashboard_usermanagement_u_permission_id_55bf0ab7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_u_permission_id_55bf0ab7 ON public.dashboard_usermanagement_user_permissions USING btree (permission_id);


--
-- Name: dashboard_usermanagement_u_usermanagement_id_b0b733b3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_u_usermanagement_id_b0b733b3 ON public.dashboard_usermanagement_user_permissions USING btree (usermanagement_id);


--
-- Name: dashboard_usermanagement_username_5ccd2c4b_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_usermanagement_username_5ccd2c4b_like ON public.dashboard_usermanagement USING btree (username varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: master_cr_database_parent_reference_id_00ca09ec; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX master_cr_database_parent_reference_id_00ca09ec ON public.master_cr_database USING btree (parent_reference_id);


--
-- Name: selected_date_table_parent_reference_id_1f12c27e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX selected_date_table_parent_reference_id_1f12c27e ON public.selected_date_table USING btree (parent_reference_id);


--
-- Name: unique_active_cr_wise_status_no; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX unique_active_cr_wise_status_no ON public.cr_wise_status USING btree (cr_no) WHERE is_active;


--
-- Name: unique_active_master_cr_no; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX unique_active_master_cr_no ON public.master_cr_database USING btree (cr_no) WHERE is_active;


--
-- Name: unique_active_selected_table_cr_no; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX unique_active_selected_table_cr_no ON public.selected_date_table USING btree (cr_no) WHERE is_active;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cr_wise_status cr_wise_status_parent_reference_id_90e13541_fk_cr_wise_s; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cr_wise_status
    ADD CONSTRAINT cr_wise_status_parent_reference_id_90e13541_fk_cr_wise_s FOREIGN KEY (parent_reference_id) REFERENCES public.cr_wise_status(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_tasklog dashboard_tasklog_run_id_388392fe_fk_dashboard_taskrun_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_tasklog
    ADD CONSTRAINT dashboard_tasklog_run_id_388392fe_fk_dashboard_taskrun_id FOREIGN KEY (run_id) REFERENCES public.dashboard_taskrun(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_taskrun dashboard_taskrun_task_id_18965367_fk_dashboard; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_taskrun
    ADD CONSTRAINT dashboard_taskrun_task_id_18965367_fk_dashboard FOREIGN KEY (task_id) REFERENCES public.dashboard_automationtask(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_taskrun dashboard_taskrun_triggered_by_id_5a8e4505_fk_dashboard; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_taskrun
    ADD CONSTRAINT dashboard_taskrun_triggered_by_id_5a8e4505_fk_dashboard FOREIGN KEY (triggered_by_id) REFERENCES public.dashboard_usermanagement(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_usermanagement_groups dashboard_usermanage_group_id_bf06518f_fk_auth_grou; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_groups
    ADD CONSTRAINT dashboard_usermanage_group_id_bf06518f_fk_auth_grou FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_usermanagement_user_permissions dashboard_usermanage_permission_id_55bf0ab7_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_user_permissions
    ADD CONSTRAINT dashboard_usermanage_permission_id_55bf0ab7_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_usermanagement_groups dashboard_usermanage_usermanagement_id_3d81d927_fk_dashboard; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_groups
    ADD CONSTRAINT dashboard_usermanage_usermanagement_id_3d81d927_fk_dashboard FOREIGN KEY (usermanagement_id) REFERENCES public.dashboard_usermanagement(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_usermanagement_user_permissions dashboard_usermanage_usermanagement_id_b0b733b3_fk_dashboard; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_usermanagement_user_permissions
    ADD CONSTRAINT dashboard_usermanage_usermanagement_id_b0b733b3_fk_dashboard FOREIGN KEY (usermanagement_id) REFERENCES public.dashboard_usermanagement(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_dashboard; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_dashboard FOREIGN KEY (user_id) REFERENCES public.dashboard_usermanagement(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: master_cr_database master_cr_database_parent_reference_id_00ca09ec_fk_master_cr; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.master_cr_database
    ADD CONSTRAINT master_cr_database_parent_reference_id_00ca09ec_fk_master_cr FOREIGN KEY (parent_reference_id) REFERENCES public.master_cr_database(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: selected_date_table selected_date_table_parent_reference_id_1f12c27e_fk_selected_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.selected_date_table
    ADD CONSTRAINT selected_date_table_parent_reference_id_1f12c27e_fk_selected_ FOREIGN KEY (parent_reference_id) REFERENCES public.selected_date_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict i44dPgArMsOzMp0FiXwysf0qwWCXQkgLMaJs12n8Upehhh1TDC3EXijPHPVMUFE

