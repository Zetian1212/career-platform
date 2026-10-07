import json
from pathlib import Path
from app.services.profile import CoreProfileSnapshot, write_fallback_snapshot, get_profile_with_fallback


def test_profile_uses_snapshot_when_database_is_unavailable(tmp_path):
    snapshot_path = tmp_path / 'fallback.json'
    snapshot = CoreProfileSnapshot(
        profile={'name': 'Demo Candidate', 'headline': 'Engineer', 'summary': 'Summary'},
        links=[{'label': 'LinkedIn', 'url': 'https://linkedin.com'}],
        skills=[{'name': 'Python'}],
        highlights=['case study'],
    )
    write_fallback_snapshot(snapshot, snapshot_path)

    def fail_factory():
        raise RuntimeError('db unavailable')

    profile, degraded = get_profile_with_fallback(fail_factory, snapshot_path)
    assert degraded is True
    assert profile.profile['name'] == 'Demo Candidate'
    assert profile.links[0].url.startswith('https://')


def test_snapshot_contains_only_core_fields(tmp_path):
    snapshot_path = tmp_path / 'fallback.json'
    write_fallback_snapshot(CoreProfileSnapshot(profile={'name': 'Demo Candidate'}, links=[], skills=[], highlights=[]), snapshot_path)
    payload = json.loads(snapshot_path.read_text())
    assert set(payload) == {'profile', 'links', 'skills', 'highlights', 'education', 'generated_at'}
