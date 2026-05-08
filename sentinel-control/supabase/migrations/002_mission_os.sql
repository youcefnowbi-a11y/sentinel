create table if not exists mission_types (
    id text primary key,
    label text not null,
    description text not null,
    status text not null default 'enabled' check (status in ('enabled', 'disabled', 'lab_only')),
    artifact_schema jsonb not null default '{}'::jsonb,
    allowed_actions text[] not null default '{}',
    allowed_tools text[] not null default '{}',
    black_zone_actions text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists mission_authority_envelopes (
    id text primary key,
    user_id text not null,
    mission_type text not null references mission_types(id),
    mission_title text not null,
    mission_objective text not null,
    success_criteria text[] not null default '{}',
    mode text not null check (mode in ('safe', 'operator', 'power', 'autonomous')),
    allowed_systems text[] not null default '{}',
    allowed_tools text[] not null default '{}',
    allowed_actions text[] not null default '{}',
    forbidden_actions text[] not null default '{}',
    allowed_paths text[] not null default '{}',
    allowed_domains text[] not null default '{}',
    allowed_accounts text[] not null default '{}',
    allowed_data_types text[] not null default '{}',
    max_duration_minutes integer not null check (max_duration_minutes > 0),
    max_actions integer not null check (max_actions > 0),
    max_cost_usd double precision not null default 0 check (max_cost_usd >= 0),
    max_recipients integer not null default 0 check (max_recipients >= 0),
    risk_appetite_score double precision not null default 25 check (risk_appetite_score >= 0 and risk_appetite_score <= 100),
    escalation_triggers text[] not null default '{}',
    rollback_preference text not null default 'metadata_only',
    trace_level text not null default 'standard',
    emergency_stop_enabled boolean not null default true,
    source_run_id text null references agent_runs(id) on delete set null,
    created_at timestamptz not null default now(),
    expires_at timestamptz null,
    revoked_at timestamptz null
);

create table if not exists mission_states (
    mission_id text primary key references mission_authority_envelopes(id) on delete cascade,
    status text not null check (status in ('planned', 'running', 'paused', 'escalated', 'completed', 'failed', 'stopped', 'revoked')),
    current_step text null,
    action_count integer not null default 0 check (action_count >= 0),
    cost_used double precision not null default 0 check (cost_used >= 0),
    started_at timestamptz null,
    updated_at timestamptz not null default now(),
    ended_at timestamptz null
);

create table if not exists mission_actions (
    id text primary key,
    mission_id text not null references mission_authority_envelopes(id) on delete cascade,
    action_type text not null,
    tool text not null,
    intent text not null,
    target text null,
    input_json jsonb not null default '{}'::jsonb,
    expected_output text not null,
    reversibility text not null check (reversibility in ('read_only', 'draft', 'local_write_reversible', 'state_mutating_recoverable', 'irreversible')),
    externality text not null check (externality in ('internal_local', 'internal_connected_system', 'external_private', 'external_public')),
    sensitivity text not null check (sensitivity in ('public', 'internal', 'personal', 'secret', 'financial', 'identity')),
    estimated_cost double precision not null default 0 check (estimated_cost >= 0),
    confidence text not null check (confidence in ('high', 'medium', 'low', 'unknown')),
    risk_score double precision not null default 0 check (risk_score >= 0 and risk_score <= 100),
    route text null check (route in ('auto_execute', 'log_and_continue', 'escalate', 'block')),
    evidence_refs text[] not null default '{}',
    trace_id text null,
    created_at timestamptz not null default now(),
    executed_at timestamptz null
);

create table if not exists escalation_requests (
    id text primary key,
    mission_id text not null references mission_authority_envelopes(id) on delete cascade,
    action_id text null references mission_actions(id) on delete set null,
    reason text not null,
    user_question text not null,
    action_preview jsonb not null default '{}'::jsonb,
    impact_summary text not null,
    options text[] not null default array['approve_once','allow_for_this_mission','deny','take_over'],
    resolution text null check (resolution in ('approve_once', 'allow_for_this_mission', 'deny', 'take_over')),
    created_at timestamptz not null default now(),
    resolved_at timestamptz null
);

create table if not exists mission_artifacts (
    id text primary key,
    mission_id text not null references mission_authority_envelopes(id) on delete cascade,
    artifact_type text not null,
    path text not null,
    evidence_refs text[] not null default '{}',
    status text not null default 'created',
    created_by_action_id text null references mission_actions(id) on delete set null,
    can_rollback boolean not null default true,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists mission_trace_events (
    id text primary key,
    mission_id text not null references mission_authority_envelopes(id) on delete cascade,
    event_type text not null,
    actor text not null default 'sentinel',
    action_id text null references mission_actions(id) on delete set null,
    summary text not null,
    target text null,
    result jsonb not null default '{}'::jsonb,
    impact text null,
    reversible boolean not null default true,
    cost double precision not null default 0 check (cost >= 0),
    timestamp timestamptz not null default now(),
    created_at timestamptz not null default now()
);

create index if not exists idx_mission_authority_user_id on mission_authority_envelopes(user_id);
create index if not exists idx_mission_authority_type on mission_authority_envelopes(mission_type);
create index if not exists idx_mission_authority_source_run on mission_authority_envelopes(source_run_id);
create index if not exists idx_mission_states_status on mission_states(status);
create index if not exists idx_mission_actions_mission_id on mission_actions(mission_id);
create index if not exists idx_mission_actions_route on mission_actions(route);
create index if not exists idx_escalation_requests_mission_id on escalation_requests(mission_id);
create index if not exists idx_escalation_requests_resolved on escalation_requests(resolved_at);
create index if not exists idx_mission_artifacts_mission_id on mission_artifacts(mission_id);
create index if not exists idx_mission_trace_events_mission_id on mission_trace_events(mission_id);
create index if not exists idx_mission_trace_events_type on mission_trace_events(event_type);

insert into mission_types (
    id,
    label,
    description,
    status,
    artifact_schema,
    allowed_actions,
    allowed_tools,
    black_zone_actions
)
values
    (
        'gtm',
        'GTM Mission',
        'Creates a local first-customer GTM pack with outreach drafts, watchlist, roadmap, trace, and review gates.',
        'enabled',
        '{
          "required_artifact_types":["gtm_verdict","evidence","icp","competitor_gap","landing_copy","outreach_drafts","watchlist","roadmap"],
          "required_files":["00_VERDICT.md","01_EVIDENCE.md","02_ICP.md","03_COMPETITOR_GAPS.md","04_LANDING_PAGE_COPY.md","05_OUTREACH_MESSAGES.md","07_7_DAY_ROADMAP.md","08_WATCHLIST.md","mission_artifacts.json","mission_timeline.json","artifact_manifest.json"],
          "draft_only_files":["outreach_drafts.json"]
        }'::jsonb,
        array['create_project_folder','create_markdown_file','export_json','generate_gtm_pack','generate_landing_copy','generate_outreach_drafts_without_sending','create_watchlist','generate_research_questions','write_trace'],
        array['safe_file_writer'],
        array['run_shell_command','browser_submit_form','desktop_control','payment','dependency_install','credential_access','production_mutation']
    ),
    (
        'research_summary',
        'Research Summary Mission',
        'Minimal non-GTM mission proving the generic Mission OS can execute multiple registered mission types.',
        'lab_only',
        '{
          "required_artifact_types":["research_summary"],
          "required_files":["RESEARCH_SUMMARY.md","mission_artifacts.json","mission_timeline.json","artifact_manifest.json"],
          "draft_only_files":[]
        }'::jsonb,
        array['create_project_folder','create_markdown_file','write_trace'],
        array['safe_file_writer'],
        array['run_shell_command','browser_submit_form','desktop_control','payment','dependency_install','credential_access','production_mutation']
    )
on conflict (id) do update set
    label = excluded.label,
    description = excluded.description,
    status = excluded.status,
    artifact_schema = excluded.artifact_schema,
    allowed_actions = excluded.allowed_actions,
    allowed_tools = excluded.allowed_tools,
    black_zone_actions = excluded.black_zone_actions,
    updated_at = now();
