from datetime import date
import pytest
from bootstrap import create_workspace
from tutor import mastery, cefr, study_time, analytics, migrations, review_policy, engine
from tutor.store import read_json, write_json, read_yaml, write_yaml


@pytest.fixture
def base(tmp_path):
    return create_workspace(tmp_path)


def configure(base):
    engine.update_profile(base, {
        'student': {'name': None, 'learning_goal': 'Conversation', 'target_cefr': 'B2'},
        'schedule': {'mode': 'continuous', 'duration_days': None, 'days_per_week': 5,
                     'sessions_per_day': 1, 'minutes_per_session': 120},
        'voice_mode': 'text_only'})
    for i in range(10):
        engine.record_diagnostic(base, 'reading', 'A2', f'Initial {i}', f'Answer {i}', .8, 'Feedback', 'text')
    engine.finish_diagnostic(base, {k:'A2' if k == 'reading' else 'not_assessed' for k in engine.SKILLS}, 'Initial')
    engine.create_roadmap(base)


def attempt(base, item, aid, mode, context, outcome='correct', assistance='independent', at=None):
    return mastery.record(base,item['id'],aid,mode,outcome,assistance,context,
                          'Question '+aid,'Answer '+aid,'Feedback',at=at)


def test_mastery_and_regression(base, monkeypatch):
    monkeypatch.setattr(mastery,'now',lambda:'2026-01-01T00:00:00+00:00')
    item = mastery.introduce(base,'phrasal_verb','figure out','solve',sense='solve')
    assert item['status']=='introduced'
    assert attempt(base,item,'1','comprehension','meaning')['status']=='understood'
    assert attempt(base,item,'2','application','practice',assistance='assisted')['status']=='practicing'
    assert attempt(base,item,'3','transfer','work')['status']=='practicing'
    assert attempt(base,item,'4','transfer','work')['status']=='practicing'
    assert attempt(base,item,'5','transfer','travel')['status']=='acquired'
    assert len(attempt(base,item,'5','transfer','travel')['attempts'])==5
    assert attempt(base,item,'6','review','home',at='2026-01-03T00:00:00+00:00')['status']=='acquired'
    assert attempt(base,item,'7','review','school',at='2026-01-07T00:00:00+00:00')['status']=='acquired'
    assert attempt(base,item,'8','review','shop',at='2026-01-15T00:00:00+00:00')['status']=='consolidated'
    assert attempt(base,item,'9','review','work',outcome='incorrect',at='2026-01-16T00:00:00+00:00')['status']=='practicing'
    assert mastery.summary(base)['acquired_total']==0


def test_assisted_and_alternative_not_mastery(base):
    item=mastery.introduce(base,'expression','used to','past habit')
    attempt(base,item,'a','transfer','work',assistance='assisted')
    result=attempt(base,item,'b','transfer','travel',outcome='not_observed')
    assert result['status']=='practicing'
    assert analytics.summary(base)['transfer']=={'value':0.0,'numerator':0,'sample_size':1}


def test_study_time_idempotence_and_unknown(base):
    a=study_time.begin(base,120,'s1')
    assert study_time.begin(base,120)['id']==a['id']
    study_time.record(base,'s1','a1','review',20)
    study_time.record(base,'s1','a1','review',20)
    with pytest.raises(ValueError):
        study_time.finish(base,'s1',10)
    study_time.finish(base,'s1',105)
    study_time.finish(base,'s1',105)
    study_time.begin(base,120,'s2')
    study_time.finish(base,'s2')
    stats=study_time.summary(base)
    assert stats['effective_minutes']==105
    assert stats['sessions_unknown_duration']==1
    assert stats['by_activity_minutes']=={'review':20,'unallocated':85}
    assert stats['adherence']==.875


def test_cefr_history_and_evidence(base):
    configure(base)
    assert cefr.current(base)['levels']['reading']['level']=='A2'
    row=cefr.begin(base)
    assert cefr.begin(base)['id']==row['id']
    with pytest.raises(ValueError):
        cefr.record(base,row['id'],'s','speaking','B1','oral','text',1,'Feedback')
    with pytest.raises(ValueError):
        cefr.finish(base,row['id'],{},'Premature')
    for i in range(10):
        cefr.record(base,row['id'],str(i),'reading','B1',f'New {i}',f'Answer {i}',.9,'Feedback')
    levels={k:'B1' if k=='reading' else 'not_assessed' for k in engine.SKILLS}
    cefr.finish(base,row['id'],levels,'Evidence')
    assert len(cefr.history(base))==2
    assert cefr.current(base)['levels']['reading']['level']=='B1'
    assert cefr.current(base)['global_cefr'] is None
    assert engine.create_roadmap(base,'Updated')['adaptation']['below_target']==['reading']


def test_migration_preserves_legacy_and_is_repeatable(base):
    cfg=read_yaml(base/'config.yaml')
    cfg['schema_version']=1
    write_yaml(base/'config.yaml',cfg)
    configure(base)
    engine.start_song(base,'Example','Artist','')
    note=engine.add_note(base,'expression','figure out','solve','Example','Evidence',[])
    source=base/note['file']
    before=source.read_bytes()
    result=migrations.migrate(base)
    assert result['schema_version']==2
    assert source.read_bytes()==before
    assert mastery.get(base,note['id'])['status']=='introduced'
    assert (base/'.tutor/migration-v1-backup'/note['file']).read_bytes()==before
    assert cefr.current(base)['levels']['reading']['level']=='A2'
    assert study_time.summary(base)['effective_minutes'] is None
    assert migrations.migrate(base)['status']=='already_current'


def test_review_links_evidence_and_is_idempotent(base):
    item=mastery.introduce(base,'expression','make sense','be logical')
    row=review_policy.schedule(base,item['id'])
    path=base/'data/reviews.json'
    queue=read_json(path)
    queue[row['note_id']]['due_date']=date.today().isoformat()
    write_json(path,queue)
    args=dict(attempt_id='r1',assistance='independent',context='work',question='Explain',answer='It makes sense')
    got=engine.grade_review(base,row['note_id'],True,'Correct',**args)
    assert got['step']==1
    assert engine.grade_review(base,row['note_id'],True,'Correct',**args)==got
    assert len(mastery.get(base,item['id'])['attempts'])==1
    assert analytics.summary(base)['retention']['value']==1


def test_integrated_song_and_analytics(base):
    configure(base)
    cycle=engine.start_song(base,'Example','Artist','')
    item=mastery.introduce(base,'expression','figure out','solve',song_id=cycle['id'])
    for day in (1,2,3):
        engine.begin_day(base,day)
        engine.checkpoint(base,day,'exercise','answer','feedback',.8,skill='reading',difficulty='B1',error_tag='tense')
        engine.end_day(base,day,'summary')
    for i in range(2):
        mastery.record(base,item['id'],str(i),'transfer','correct','independent',f'context {i}',
                       f'Question {i}',f'Answer {i}','Feedback',song_id=cycle['id'])
    final=engine.finish_song(base,85,5,'not_assessed','not_assessed','summary')
    assert final['active_expressions']==1
    assert not final['criteria']['expressions']
    assert item['id'] in read_json(base/'data/reviews.json')
    stats=engine.metrics(base)['learning']
    assert stats['songs_completed']==1
    assert stats['transfer']['sample_size']==2
    assert stats['performance_by_skill_difficulty'][0]['sample_size']==3
    assert stats['study']['effective_minutes'] is None


def test_cefr_due_by_confirmed_minutes(base):
    configure(base)
    for i in range(2):
        row=study_time.begin(base,900)
        study_time.finish(base,row['id'],900)
    assert cefr.due(base)['due']
