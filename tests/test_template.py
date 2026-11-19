from __future__ import annotations
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from bootstrap import ROOT, create_workspace
from tutor import engine
from tutor.cli import doctor
from tutor.store import read_json, write_json
from tutor.store import root as workspace_root
from tutor.hooks import hook_start


def workspace(tmp_path: Path) -> Path:
    project = tmp_path / 'study'
    project.mkdir()
    return create_workspace(project)


def configured(base: Path):
    engine.update_profile(base, {
        'student': {'name': 'Test', 'learning_goal': 'Conversar em inglês', 'target_cefr': 'B2'},
        'schedule': {'mode': 'fixed', 'duration_days': 90, 'days_per_week': 7,
                     'sessions_per_day': 1, 'minutes_per_session': 120},
        'voice_mode': 'text_only'})


def diagnosed(base: Path):
    for i in range(10):
        skill = ('grammar','vocabulary','reading','writing')[i%4]
        engine.record_diagnostic(base, skill, 'B1', f'Questão {i}', f'Resposta {i}',
                                 0.75, 'Feedback real', 'text')
    return engine.finish_diagnostic(base, {
        'grammar': 'B1', 'vocabulary':'B1','reading':'B1','writing':'B1',
        'listening':'not_assessed','speaking':'not_assessed'}, 'Relatório com evidências')


def test_public_template_has_no_student_config_or_data():
    assert (ROOT/'config.example.yaml').is_file()
    assert not (ROOT/'config.yaml').exists()
    assert not (ROOT/'data').exists()
    assert '/workspaces/' in (ROOT/'.gitignore').read_text(encoding='utf-8')
    assert len(list((ROOT/'.agents/skills').glob('*/SKILL.md'))) >= 12
    assert (ROOT/'.codex/hooks.json').is_file()


def test_bootstrap_creates_one_internal_workspace_and_preserves_it(tmp_path):
    project = tmp_path / 'study'
    project.mkdir()
    base = create_workspace(project)
    assert base == project / 'workspaces'
    assert (base/'config.yaml').exists()
    assert not (base/'data/state.json').exists()
    assert not (base/'tutor').exists()
    assert not (base/'.agents').exists()
    assert (base/'.gitignore').is_file()
    private_note = base / 'data' / 'private.txt'
    private_note.write_text('progresso local', encoding='utf-8')
    assert create_workspace(project) == base
    assert private_note.read_text(encoding='utf-8') == 'progresso local'


def test_bootstrap_refuses_to_overwrite_partial_workspace(tmp_path):
    project = tmp_path / 'study'
    partial = project / 'workspaces'
    partial.mkdir(parents=True)
    (partial / 'student-file.txt').write_text('keep', encoding='utf-8')
    with pytest.raises(FileExistsError, match='Revise-os'):
        create_workspace(project)


def test_bootstrap_rejects_workspace_symlink(tmp_path):
    project = tmp_path / 'study'
    project.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (project / 'workspaces').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='link simbólico'):
        create_workspace(project)
    assert not (outside / 'config.yaml').exists()


def test_bootstrap_keeps_current_codex_session_in_workspace(tmp_path):
    project = tmp_path / 'study'
    session = project / '.tutor' / 'session.json'
    session.parent.mkdir(parents=True)
    session.write_text('{"session_id":"current-chat"}\n', encoding='utf-8')
    base = create_workspace(project)
    assert read_json(base / '.tutor' / 'session.json') == {'session_id': 'current-chat'}


def test_root_detects_workspace_inside_project(tmp_path, monkeypatch):
    project = tmp_path / 'project'
    base = project / 'workspaces'
    base.mkdir(parents=True)
    (base / 'config.yaml').write_text('schema_version: 1\n', encoding='utf-8')
    monkeypatch.delenv('TUTOR_WORKSPACE', raising=False)
    monkeypatch.chdir(project)
    assert workspace_root() == base
    monkeypatch.chdir(base)
    assert workspace_root() == base


def test_doctor_checks_shared_project_files_from_workspace(tmp_path):
    base = workspace(tmp_path)
    result = doctor(base)
    assert not any(issue.startswith('Arquivo ausente:') for issue in result['issues'])


def test_start_hook_explains_how_to_initialize_workspace(tmp_path):
    output = hook_start(tmp_path, {})
    context = output['hookSpecificOutput']['additionalContext']
    assert 'python bootstrap.py workspace' in context


def test_config_and_leveling_requires_evidence(tmp_path):
    base = workspace(tmp_path)
    configured(base)
    with pytest.raises(ValueError, match='mínimo 10'):
        engine.finish_diagnostic(base, {'grammar':'B1'}, 'teste')
    report = diagnosed(base)
    assert report['levels']['reading'] == 'B1'
    assert any('listening' in x for x in report['limitations'])
    plan = engine.create_roadmap(base)
    assert plan['nominal_song_capacity'] == 30
    assert plan['goal'] == 'Conversar em inglês'


def test_song_day_notes_and_revisions(tmp_path):
    base = workspace(tmp_path)
    configured(base); diagnosed(base); engine.create_roadmap(base)
    first = engine.start_song(base, 'Example Song', 'Artist', 'https://example.org')
    assert first['day'] == 1
    with pytest.raises(ValueError, match='Finalize a música'):
        engine.start_song(base, 'Other Song', 'Other', '')
    note = engine.add_note(base, 'expression', 'figure out', 'entender',
                           'I figured it out.', 'aluno respondeu corretamente', ['chunk'])
    for day in (1, 2, 3):
        engine.begin_day(base, day)
        engine.checkpoint(base, day, 'test', f'resposta real {day}', 'feedback', 0.9)
        engine.end_day(base, day, 'Dia realizado e validado')
    final = engine.finish_song(base, 82, 5, 'not_assessed', 'not_assessed', 'Resultado textual')
    assert final['criteria']['comprehension'] is True
    assert final['criteria']['pronunciation'] is False
    assert engine.metrics(base)['songs_completed'] == 1
    reviews = read_json(base/'data/reviews.json', {})
    assert note['id'] in reviews
    assert reviews[note['id']]['due_date'] == (date.today()+timedelta(days=1)).isoformat()
    assert not engine.due_reviews(base)
    future = (date.today()+timedelta(days=1)).isoformat()
    assert len(engine.due_reviews(base, future)) == 1
    with pytest.raises(ValueError, match='ainda não venceu'):
        engine.grade_review(base, note['id'], True, 'correto')
    assert '[Música' in (base/note['file']).read_text(encoding='utf-8')


def test_continuous_plan_has_rolling_horizon(tmp_path):
    base = workspace(tmp_path)
    engine.update_profile(base, {
        'student': {'name': None, 'learning_goal':'Continuar aprendendo', 'target_cefr':None},
        'schedule': {'mode':'continuous','duration_days':None,
                     'days_per_week':5,'sessions_per_day':1,'minutes_per_session':45},
        'voice_mode':'external'})
    diagnosed(base)
    plan = engine.create_roadmap(base)
    assert plan['mode'] == 'continuous'
    assert plan['horizon_days'] == 90
    assert plan['nominal_song_capacity'] == int((90 * 5 / 7)//3)


def test_session_start_context_and_thread(tmp_path):
    base = workspace(tmp_path)
    configured(base); diagnosed(base); engine.create_roadmap(base)
    output = hook_start(base, {'session_id':'thread-1'})
    assert output['hookSpecificOutput']['hookEventName'] == 'SessionStart'
    record = engine.start_song(base,'A','B','')
    assert record['thread_id'] == 'thread-1'
    hook_start(base, {'session_id':'thread-2'})
    with pytest.raises(ValueError, match='outro chat'):
        engine.begin_day(base, 1)


def test_failed_note_without_song(tmp_path):
    base = workspace(tmp_path)
    with pytest.raises(ValueError, match='música ativa'):
        engine.add_note(base, 'expression','figure out','entender','example','evidence',[])


def test_hook_json_is_valid():
    hook = json.loads((ROOT/'.codex/hooks.json').read_text(encoding='utf-8'))
    assert 'SessionStart' in hook['hooks']
    assert 'SessionEnd' in hook['hooks']
    for event in hook['hooks'].values():
        assert event[0]['hooks'][0]['commandWindows'].startswith('py -3')


def test_roadmap_replan_preserves_previous_version(tmp_path):
    base = workspace(tmp_path)
    configured(base); diagnosed(base)
    first = engine.create_roadmap(base)
    second = engine.create_roadmap(base)
    assert len(second['history']) == 1
    assert second['history'][0]['generated_at'] == first['generated_at']


def test_second_song_must_use_another_thread(tmp_path):
    base = workspace(tmp_path)
    configured(base); diagnosed(base); engine.create_roadmap(base)
    hook_start(base, {'session_id':'one-thread'})
    engine.start_song(base, 'A song', 'Artist', '')
    for day in (1, 2, 3):
        engine.begin_day(base, day)
        engine.checkpoint(base, day, 'activity', 'real evidence', 'real feedback', None)
        engine.end_day(base, day, 'session summary')
    engine.finish_song(base, 80, 5, 'not_assessed', 'not_assessed', 'summary')
    with pytest.raises(ValueError, match='novo chat'):
        engine.start_song(base, 'B song', 'Artist', '')
    hook_start(base, {'session_id':'different-thread'})
    record = engine.start_song(base, 'B song', 'Artist', '')
    assert record['id'].startswith('002-')
