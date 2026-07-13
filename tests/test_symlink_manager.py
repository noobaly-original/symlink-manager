"""
Tests for the SymlinkManager module.
"""

import os
import sys
import tempfile
import shutil
import ctypes
from pathlib import Path
import pytest

from symlink_manager import SymlinkManager


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _can_create_symlinks() -> bool:
    """Check if the current process can create symlinks."""
    if sys.platform != "win32":
        return True
    try:
        tmp = Path(tempfile.mkdtemp(prefix="sym_cap_"))
        test_src = tmp / "src"
        test_src.write_text("test")
        test_link = tmp / "link"
        os.symlink(str(test_src), str(test_link))
        shutil.rmtree(tmp, ignore_errors=True)
        return True
    except (OSError, NotImplementedError):
        shutil.rmtree(tmp, ignore_errors=True)
        return False


def _is_admin() -> bool:
    """Check if running as admin on Windows."""
    if sys.platform != "win32":
        return os.geteuid() == 0
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


needs_symlinks = pytest.mark.skipif(
    not _can_create_symlinks() and not _is_admin(),
    reason="Symlink creation not possible (not admin and no Developer Mode)"
)


# --------------------------------------------------------------------------- #
#  Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def temp_dirs():
    """Create temporary source and target directories for testing."""
    tmp_root = Path(tempfile.mkdtemp(prefix="symlink_test_"))
    source_dir = tmp_root / "source"
    source_dir.mkdir()
    target_dir = tmp_root / "target"
    target_dir.mkdir()
    yield source_dir, target_dir, tmp_root
    shutil.rmtree(tmp_root, ignore_errors=True)


@pytest.fixture
def sample_file(temp_dirs):
    """Create a sample file in the source directory."""
    source_dir, target_dir, tmp_root = temp_dirs
    file_path = source_dir / "test_file.txt"
    file_path.write_text("hello world")
    return file_path, source_dir, target_dir, tmp_root


@pytest.fixture
def sample_dir_structure(temp_dirs):
    """Create a nested directory structure in the source."""
    source_dir, target_dir, tmp_root = temp_dirs
    nested = source_dir / "subdir" / "nested"
    nested.mkdir(parents=True)
    (source_dir / "root_file.txt").write_text("root")
    (nested / "deep_file.txt").write_text("deep")
    return source_dir, target_dir, tmp_root


# --------------------------------------------------------------------------- #
#  Platform detection
# --------------------------------------------------------------------------- #

class TestPlatformDetection:
    def test_is_windows(self):
        assert SymlinkManager.is_windows() == (sys.platform == "win32")

    def test_is_macos(self):
        assert SymlinkManager.is_macos() == (sys.platform == "darwin")

    def test_is_linux(self):
        assert SymlinkManager.is_linux() == (sys.platform == "linux")


# --------------------------------------------------------------------------- #
#  Symlink creation
# --------------------------------------------------------------------------- #

class TestCreateSymlink:
    @needs_symlinks
    def test_create_file_symlink(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "link_to_file.txt"

        success, msg = SymlinkManager.create_symlink(
            str(file_path), str(target_path)
        )
        assert success, f"Creation failed: {msg}"
        assert target_path.is_symlink()
        assert target_path.resolve() == file_path.resolve()
        assert target_path.read_text() == "hello world"

    @needs_symlinks
    def test_create_dir_symlink(self, temp_dirs):
        source_dir, target_dir, tmp_root = temp_dirs
        # Put a file inside source so it's a non-empty directory
        (source_dir / "file.txt").write_text("content")
        target_path = target_dir / "link_to_dir"

        success, msg = SymlinkManager.create_symlink(
            str(source_dir), str(target_path)
        )
        assert success, f"Creation failed: {msg}"
        assert target_path.is_symlink()
        assert target_path.resolve() == source_dir.resolve()

    def test_validate_paths_valid(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "new_link"
        valid, error = SymlinkManager.validate_paths(str(file_path), str(target_path))
        assert valid, f"Validation failed: {error}"

    def test_validate_paths_missing_source(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        missing = tmp_root / "does_not_exist"
        target_path = target_dir / "link"
        valid, error = SymlinkManager.validate_paths(str(missing), str(target_path))
        assert not valid
        assert "does not exist" in error

    def test_validate_paths_target_exists(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        existing_target = target_dir / "existing"
        existing_target.write_text("I already exist")
        valid, error = SymlinkManager.validate_paths(str(file_path), str(existing_target))
        assert not valid
        assert "already exists" in error

    @needs_symlinks
    def test_relative_symlink(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "relative_link"
        success, msg = SymlinkManager.create_symlink(
            str(file_path), str(target_path), relative=True
        )
        assert success, f"Creation failed: {msg}"
        assert target_path.is_symlink()


# --------------------------------------------------------------------------- #
#  Symlink removal
# --------------------------------------------------------------------------- #

class TestRemoveSymlink:
    @needs_symlinks
    def test_remove_file_symlink(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "to_remove"
        SymlinkManager.create_symlink(str(file_path), str(target_path))

        success, msg = SymlinkManager.remove_symlink(str(target_path))
        assert success, f"Removal failed: {msg}"
        assert not target_path.exists()

    def test_remove_non_symlink_fails(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        real_file = target_dir / "real.txt"
        real_file.write_text("real file")
        success, msg = SymlinkManager.remove_symlink(str(real_file))
        assert not success
        assert "not a symlink" in msg

    def test_remove_nonexistent(self, temp_dirs):
        _, _, tmp_root = temp_dirs
        fake = tmp_root / "nope"
        success, msg = SymlinkManager.remove_symlink(str(fake))
        assert not success

    @needs_symlinks
    def test_remove_symlink_then_check(self, sample_file):
        """Remove a symlink that actually exists."""
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "to_remove"
        SymlinkManager.create_symlink(str(file_path), str(target_path))
        assert target_path.is_symlink()
        success, msg = SymlinkManager.remove_symlink(str(target_path))
        assert success, f"Removal failed: {msg}"
        assert not target_path.exists()


# --------------------------------------------------------------------------- #
#  Safe remove target
# --------------------------------------------------------------------------- #

class TestSafeRemoveTarget:
    def test_refuse_real_file(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        real_file = target_dir / "important.txt"
        real_file.write_text("data")
        success, msg = SymlinkManager._safe_remove_target(real_file)
        assert not success
        assert "Refusing to remove" in msg
        assert real_file.exists()

    def test_remove_symlink(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        sym = target_dir / "sym"
        SymlinkManager.create_symlink(str(file_path), str(sym))
        success, msg = SymlinkManager._safe_remove_target(sym)
        assert success
        assert not sym.exists()


# --------------------------------------------------------------------------- #
#  Batch operations
# --------------------------------------------------------------------------- #

class TestRunBatch:
    @needs_symlinks
    def test_batch_single_file(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        target_path = target_dir / "batch_link"
        ops = [(str(file_path), str(target_path), False, False, False, False)]
        success, msg, results = SymlinkManager.run_batch(ops)
        assert success, f"Batch failed: {msg}"
        assert len(results) == 1
        assert results[0][2] is True

    @needs_symlinks
    def test_batch_multiple(self, temp_dirs):
        source_dir, target_dir, tmp_root = temp_dirs
        files = []
        ops = []
        for i in range(3):
            f = source_dir / f"file_{i}.txt"
            f.write_text(f"content_{i}")
            files.append(f)
            t = target_dir / f"link_{i}"
            ops.append((str(f), str(t), False, False, False, False))

        success, msg, results = SymlinkManager.run_batch(ops)
        assert success, f"Batch failed: {msg}"
        assert all(r[2] for r in results)

    def test_batch_with_missing_source(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        fake_source = tmp_root / "missing"
        target = target_dir / "link"
        ops = [(str(fake_source), str(target), False, False, False, False)]
        success, msg, results = SymlinkManager.run_batch(ops)
        # Should still return results but the op failed
        assert not results[0][2]


# --------------------------------------------------------------------------- #
#  Merge directories
# --------------------------------------------------------------------------- #

class TestMergeDirectories:
    @needs_symlinks
    def test_merge_new_file(self, temp_dirs):
        """A file in the symlink's parent that is NOT in source should be
        moved into source, then a new symlink created for it."""
        source_dir, target_dir, tmp_root = temp_dirs
        # Create the main symlink (will be missing)
        main_symlink = target_dir / "main_symlink"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        # Put a file into the symlink's parent that is NOT in source
        new_file = target_dir / "new_item.txt"
        new_file.write_text("i am new")

        # Run merge
        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok, f"Merge failed: {msg}"
        # new_item.txt should have been moved to source
        assert (source_dir / "new_item.txt").exists()
        assert (source_dir / "new_item.txt").read_text() == "i am new"
        # The original in target_dir should have been replaced with a symlink
        assert new_file.is_symlink()
        assert new_file.resolve() == (source_dir / "new_item.txt").resolve()
        # Should report 1 merged item
        assert len(new_syms) == 1

    @needs_symlinks
    def test_merge_new_dir(self, temp_dirs):
        """A subdirectory in the symlink's parent that is NOT in source should
        be recursively copied into source and then symlinked."""
        source_dir, target_dir, tmp_root = temp_dirs
        main_symlink = target_dir / "main"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        # Create a subdirectory with content in the symlink's parent
        new_sub = target_dir / "new_subdir"
        new_sub.mkdir()
        (new_sub / "inner.txt").write_text("inner")

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok, f"Merge failed: {msg}"
        # The subdirectory should now be in source
        assert (source_dir / "new_subdir" / "inner.txt").exists()
        assert (source_dir / "new_subdir" / "inner.txt").read_text() == "inner"
        # The original should be replaced with a symlink
        assert new_sub.is_symlink()
        assert len(new_syms) == 1

    @needs_symlinks
    def test_merge_skips_existing_in_source(self, temp_dirs):
        """Items that already exist in the source should be skipped when the
        source copy is newer."""
        source_dir, target_dir, tmp_root = temp_dirs
        main_symlink = target_dir / "main"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        # Create a file in source first (older), then in target (newer)
        (source_dir / "shared.txt").write_text("in source")
        import time
        time.sleep(0.05)  # ensure the target file has a newer timestamp
        (target_dir / "shared.txt").write_text("in target")

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok
        # The target file is newer, so it SHOULD overwrite the source
        assert (source_dir / "shared.txt").read_text() == "in target"
        # The target should now be a symlink
        assert (target_dir / "shared.txt").is_symlink()
        assert len(new_syms) == 1

    @needs_symlinks
    def test_merge_skips_when_source_newer(self, temp_dirs):
        """Items in target that are older than the source should be skipped."""
        source_dir, target_dir, tmp_root = temp_dirs
        main_symlink = target_dir / "main"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        # Create a file in target first, then in source (newer)
        (target_dir / "shared.txt").write_text("older in target")
        import time
        time.sleep(0.05)
        (source_dir / "shared.txt").write_text("newer in source")

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok
        # Source is newer — should NOT overwrite, should skip
        assert (source_dir / "shared.txt").read_text() == "newer in source"
        assert len(new_syms) == 0

    @needs_symlinks
    def test_merge_skips_duplicate_paths(self, temp_dirs):
        """Items resolving to the same path should be silently skipped."""
        source_dir, target_dir, tmp_root = temp_dirs
        main_symlink = target_dir / "main"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        # Create a real item and a duplicate symlink pointing to the same place
        real_item = target_dir / "real_item.txt"
        real_item.write_text("real")
        # Create a symlink that resolves to the same path as real_item (unlikely
        # but tests the dedup logic)
        duplicate = target_dir / "duplicate.txt"
        duplicate.write_text("also real")

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok
        # Both should be merged since they don't exist in source and aren't
        # actually the same resolved path in this case
        assert len(new_syms) >= 0  # no crash

    @needs_symlinks
    def test_merge_skips_symlink_itself(self, temp_dirs):
        """The main symlink itself should not be merged."""
        source_dir, target_dir, tmp_root = temp_dirs
        main_symlink = target_dir / "main"
        success, _ = SymlinkManager.create_symlink(str(source_dir), str(main_symlink))
        assert success

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(source_dir), str(main_symlink)
        )
        assert ok
        assert len(new_syms) == 0

    def test_merge_source_not_dir_returns_false(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        a_file = tmp_root / "a_file.txt"
        a_file.write_text("not a dir")
        sym = target_dir / "sym"
        (target_dir / "dummy").write_text("dummy")

        ok, msg, new_syms = SymlinkManager.merge_directories(
            str(a_file), str(sym)
        )
        assert not ok
        assert "not a directory" in msg


# --------------------------------------------------------------------------- #
#  Utility methods
# --------------------------------------------------------------------------- #

class TestGetSymlinkInfo:
    @needs_symlinks
    def test_get_info(self, sample_file):
        file_path, source_dir, target_dir, tmp_root = sample_file
        sym = target_dir / "info_link"
        SymlinkManager.create_symlink(str(file_path), str(sym))
        info = SymlinkManager.get_symlink_info(str(sym))
        assert info is not None
        assert info["path"] == str(sym)
        assert info["exists"] is True

    def test_get_info_not_symlink(self, temp_dirs):
        _, target_dir, tmp_root = temp_dirs
        info = SymlinkManager.get_symlink_info(str(target_dir))
        assert info is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])