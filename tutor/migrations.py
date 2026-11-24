"""Explicit, repeatable v1 -> v2 migration. No invented historical evidence."""
from pathlib import Path
import shutil
from .store import read_yaml, write_yaml, read_json, require_workspace
from . import mastery, cefr

DEFAULTS = {
    'mastery': {'independent_contexts': 2, 'consolidation_reviews': 3,
                'consolidation_days': 14, 'regression_failures': 1},
    'cefr_progression': {'songs_interval': 5, 'minutes_interval': 1800},
    'review_policy': {'maintenance_enabled': True, 'maintenance_days': [60, 90, 120, 180]}
}


def migrate(base: Path):
    require_workspace(base)
    cfg = read_yaml(base / 'config.yaml')
    version = cfg.get('schema_version')
    if version == 2:
        return {'status': 'already_current', 'schema_version': 2}
    if version != 1:
        raise ValueError('Schema não suportado')
    # Local backup outside data tree, inside ignored workspace. Keep first intact.
    backup = base / '.tutor/migration-v1-backup'
    if not backup.exists():
        staging = base / '.tutor/migration-v1-backup.tmp'
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        shutil.copy2(base / 'config.yaml', staging / 'config.yaml')
        if (base / 'data').is_dir():
            shutil.copytree(base / 'data', staging / 'data')
        staging.rename(backup)
    for note in read_json(base / 'data/notes/index.json', {}).values():
        mastery.legacy_note(base, note)
    cefr.preserve_placement(base)
    for key, defaults in DEFAULTS.items():
        cfg[key] = dict(defaults, **cfg.get(key, {}))
    cfg['schema_version'] = 2
    write_yaml(base / 'config.yaml', cfg)
    return {'status': 'migrated', 'schema_version': 2, 'backup': str(backup),
            'legacy_knowledge_count': len(mastery.items(base))}
