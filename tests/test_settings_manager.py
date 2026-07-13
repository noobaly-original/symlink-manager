"""
Tests for the SettingsManager module.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import pytest

from settings_manager import SettingsManager


# --------------------------------------------------------------------------- #
#  Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def config_dir():
    """Create a temporary config directory for testing."""
    tmp = Path(tempfile.mkdtemp(prefix="symlink_settings_test_"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def settings_manager(config_dir):
    """Return a SettingsManager using a temporary config directory."""
    return SettingsManager(str(config_dir))


# --------------------------------------------------------------------------- #
#  Settings
# --------------------------------------------------------------------------- #

class TestSettings:
    def test_default_settings(self, settings_manager):
        """Should return defaults when no file exists."""
        assert settings_manager.get_setting('theme') == 'dark'
        assert settings_manager.get_setting('persist_symlinks') is False
        assert settings_manager.get_setting('persistence_interval') == 60
        assert settings_manager.get_setting('merge_management') is False

    def test_set_and_get_setting(self, settings_manager):
        """Setting a value should persist and be retrievable."""
        settings_manager.set_setting('theme', 'light')
        assert settings_manager.get_setting('theme') == 'light'

    def test_get_setting_default(self, settings_manager):
        """Getting a non-existent setting should return the default."""
        assert settings_manager.get_setting('nonexistent', 'fallback') == 'fallback'

    def test_settings_persist_to_disk(self, config_dir):
        """Settings should survive a new SettingsManager instance."""
        sm1 = SettingsManager(str(config_dir))
        sm1.set_setting('theme', 'monokai')
        del sm1

        sm2 = SettingsManager(str(config_dir))
        assert sm2.get_setting('theme') == 'monokai'


# --------------------------------------------------------------------------- #
#  History
# --------------------------------------------------------------------------- #

class TestHistory:
    def test_add_to_history(self, settings_manager):
        settings_manager.add_to_history('/some/path', 'source')
        history = settings_manager.get_history('sources', 10)
        assert '/some/path' in history

    def test_history_does_not_duplicate(self, settings_manager):
        settings_manager.add_to_history('/path', 'source')
        settings_manager.add_to_history('/path', 'source')
        history = settings_manager.get_history('sources', 10)
        assert history.count('/path') == 1

    def test_record_creation(self, settings_manager):
        settings_manager.record_creation('/src', '/tgt', True, 'OK')
        creations = settings_manager.get_history('creations', 10)
        assert len(creations) == 1
        assert creations[0]['source'] == '/src'
        assert creations[0]['target'] == '/tgt'
        assert creations[0]['success'] is True

    def test_clear_history(self, settings_manager):
        settings_manager.add_to_history('/src', 'source')
        settings_manager.clear_history('sources')
        history = settings_manager.get_history('sources', 10)
        assert len(history) == 0


# --------------------------------------------------------------------------- #
#  Symlink tracking
# --------------------------------------------------------------------------- #

class TestSymlinkTracking:
    def test_add_symlink(self, settings_manager):
        result = settings_manager.add_symlink('/source', '/target', notes='test')
        assert result is True
        all_links = settings_manager.get_all_symlinks()
        assert len(all_links) == 1
        assert all_links[0]['source'] == '/source'
        assert all_links[0]['target'] == '/target'

    def test_add_duplicate_target(self, settings_manager):
        settings_manager.add_symlink('/src', '/tgt')
        result = settings_manager.add_symlink('/src2', '/tgt')
        assert result is False  # duplicate target

    def test_remove_symlink(self, settings_manager):
        settings_manager.add_symlink('/src', '/tgt')
        result = settings_manager.remove_symlink('/tgt')
        assert result is True
        assert len(settings_manager.get_all_symlinks()) == 0

    def test_update_symlink_notes(self, settings_manager):
        settings_manager.add_symlink('/src', '/tgt', notes='original')
        settings_manager.update_symlink('/tgt', notes='updated')
        link = settings_manager.get_symlink_by_target('/tgt')
        assert link['notes'] == 'updated'

    def test_get_symlink_by_target(self, settings_manager):
        settings_manager.add_symlink('/src', '/tgt')
        link = settings_manager.get_symlink_by_target('/tgt')
        assert link is not None
        assert link['source'] == '/src'

    def test_get_symlink_by_target_missing(self, settings_manager):
        link = settings_manager.get_symlink_by_target('/nonexistent')
        assert link is None

    def test_verify_symlinks_returns_counts(self, settings_manager):
        """When no real symlinks exist on disk, verify should mark as missing."""
        settings_manager.add_symlink('/fake/source', '/fake/target')
        status = settings_manager.verify_symlinks()
        assert status['total'] == 1
        assert status['missing'] == 1


# --------------------------------------------------------------------------- #
#  Source-based merge
# --------------------------------------------------------------------------- #

class TestMergeSource:
    def test_is_merge_source_default_false(self, settings_manager):
        assert settings_manager.is_merge_source('/some/path') is False

    def test_set_merge_source_true(self, settings_manager):
        settings_manager.set_merge_source('/my/source', True)
        assert settings_manager.is_merge_source('/my/source') is True

    def test_set_merge_source_false(self, settings_manager):
        settings_manager.set_merge_source('/my/source', True)
        settings_manager.set_merge_source('/my/source', False)
        assert settings_manager.is_merge_source('/my/source') is False

    def test_merge_sources_persist(self, config_dir):
        sm1 = SettingsManager(str(config_dir))
        sm1.set_merge_source('/persist/src', True)
        del sm1

        sm2 = SettingsManager(str(config_dir))
        assert sm2.is_merge_source('/persist/src') is True


# --------------------------------------------------------------------------- #
#  Merge pairs
# --------------------------------------------------------------------------- #

class TestMergePairs:
    def test_get_merge_pairs_empty(self, settings_manager):
        assert settings_manager.get_merge_pairs() == []

    def test_add_merge_pair(self, settings_manager):
        result = settings_manager.add_merge_pair('/src', '/tgt')
        assert result is True
        pairs = settings_manager.get_merge_pairs()
        assert len(pairs) == 1
        assert pairs[0] == {'source': '/src', 'target': '/tgt'}

    def test_add_duplicate_pair(self, settings_manager):
        settings_manager.add_merge_pair('/src', '/tgt')
        result = settings_manager.add_merge_pair('/src', '/tgt')
        assert result is False

    def test_remove_merge_pair(self, settings_manager):
        settings_manager.add_merge_pair('/src', '/tgt')
        result = settings_manager.remove_merge_pair('/src', '/tgt')
        assert result is True
        assert settings_manager.get_merge_pairs() == []

    def test_remove_nonexistent_pair(self, settings_manager):
        result = settings_manager.remove_merge_pair('/nope', '/nope')
        assert result is False

    def test_merge_pairs_persist(self, config_dir):
        sm1 = SettingsManager(str(config_dir))
        sm1.add_merge_pair('/p/src', '/p/tgt')
        del sm1

        sm2 = SettingsManager(str(config_dir))
        pairs = sm2.get_merge_pairs()
        assert len(pairs) == 1
        assert pairs[0]['source'] == '/p/src'


# --------------------------------------------------------------------------- #
#  Persistent create/batch options
# --------------------------------------------------------------------------- #

class TestPersistentOptions:
    def test_create_admin_default(self, settings_manager):
        assert settings_manager.get_setting('create_admin', False) is False

    def test_batch_skip_errors_default(self, settings_manager):
        assert settings_manager.get_setting('batch_skip_errors', False) is False

    def test_batch_force_default(self, settings_manager):
        assert settings_manager.get_setting('batch_force', False) is False

    def test_create_relative_persists(self, config_dir):
        sm1 = SettingsManager(str(config_dir))
        sm1.set_setting('create_relative', True)
        del sm1
        sm2 = SettingsManager(str(config_dir))
        assert sm2.get_setting('create_relative') is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])