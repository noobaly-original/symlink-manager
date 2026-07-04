# Symlink Management Guide

## Overview

The Symlink Manager now includes a comprehensive symlink tracking and management system. You can view, edit, verify, and delete all symlinks you've created through the application.

## Features

### 1. Automatic Tracking
Every symlink created through the Symlink Manager is automatically added to the tracking system. The app stores:
- Target symlink path
- Source path
- Creation date
- Status (active/inactive)
- Custom notes

### 2. Manage Tab

The **Manage** tab provides a complete interface to:
- View all tracked symlinks
- Edit notes for each symlink
- Delete symlinks (from disk and tracking)
- Verify symlink status
- Check for broken or missing links

### 3. Symlink Table

The table displays:
- **Target**: Where the symlink is located
- **Source**: What the symlink points to
- **Status**: ✓ Active, ○ Inactive, or Missing
- **Notes**: User-defined notes about the symlink
- **Created**: Date the symlink was created

## Managing Symlinks

### View All Symlinks

1. Click the **Manage** tab
2. All tracked symlinks are displayed in the table
3. Click **Refresh** to update the list

### Edit Notes

Add or edit notes for a symlink:

1. Select a symlink in the table
2. Click **Edit Notes**
3. Enter or modify the notes
4. Click **Save**

**Example notes:**
- "Backup directory link"
- "Development environment"
- "Project X resources"

### Delete a Symlink

Remove a symlink from the system:

1. Select a symlink in the table
2. Click **Delete**
3. Confirm the deletion
4. The symlink is removed from disk and tracking

⚠️ **Warning**: This action is permanent and cannot be undone.

### Verify All Symlinks

Check the status of all tracked symlinks:

1. Click **Verify All**
2. A report shows:
   - Total number of symlinks
   - Active symlinks
   - Broken links (target doesn't exist)
   - Missing symlinks (not found on disk)

## Symlink Status

### ✓ Active
- Symlink exists on disk
- Target file/directory exists
- Fully functional

### ○ Inactive
- Symlink marked as inactive
- Still on disk but not in use
- Can be reactivated or deleted

### ✗ Broken
- Symlink exists but target is missing
- Original file/directory was moved or deleted
- Symlink is non-functional

### ? Missing
- Tracked symlink not found on disk
- Was deleted outside the app
- Can be removed from tracking

## Storage

Managed symlinks are stored in:
- **macOS/Linux**: `~/.config/symlink_app/managed_symlinks.json`
- **Windows**: `%APPDATA%\SymlinkApp\managed_symlinks.json`

Example structure:
```json
{
  "symlinks": [
    {
      "id": 1,
      "source": "/Users/username/Projects/MyApp",
      "target": "/Users/username/Desktop/MyApp",
      "notes": "Development link",
      "created_at": "2026-07-04T18:30:45",
      "active": true
    }
  ]
}
```

## Workflow Examples

### Example 1: Managing Development Links

1. **Create** a symlink from your project folder to Desktop
2. **Edit Notes** to add: "Main development project"
3. **Verify** the link works properly
4. When done, **Delete** the symlink

### Example 2: Checking Broken Links

1. Go to **Manage** tab
2. Click **Verify All** to get a report
3. Identify broken links (status shows ✗)
4. Delete or recreate as needed

### Example 3: Organizing with Notes

1. Create multiple symlinks
2. Click **Edit Notes** on each
3. Add descriptive notes:
   - "Active backup location"
   - "Configuration files"
   - "Temporary alias"
4. Use notes to remember purpose of each link

## Advanced Features

### Batch Operations

While not yet automated, you can:
1. Create multiple symlinks one at a time
2. Use **Verify All** to check all at once
3. Delete them individually as needed

### History Integration

- **History** tab shows recent creations
- **Manage** tab shows all currently tracked
- Check both for complete management view

### Status Indicators

The status bar shows quick stats:
```
Total: 5 | Active: 4 | Broken: 1 | Missing: 0
```

## Troubleshooting

### Symlink Shows as "Missing"

The symlink was deleted outside the app:
1. Delete it from tracking (**Delete** button)
2. Recreate if needed

### Symlink Shows as "Broken"

The target file/directory was moved:
1. Find the original file/directory
2. Delete the broken symlink
3. Recreate with new target path

### Can't Delete Symlink

Possible causes:
- Insufficient permissions (try running as admin)
- Symlink is in use by another application
- File is locked

Solutions:
1. Close other applications using the symlink
2. Run as administrator (Windows)
3. Check file permissions (macOS/Linux)

### Lost Tracking Information

If `managed_symlinks.json` is deleted:
1. Symlinks on disk still work
2. They're just no longer tracked
3. Manually create the symlinks again to add them to tracking

## Best Practices

1. **Use descriptive notes** - Remember why each symlink exists
2. **Regular verification** - Click "Verify All" periodically
3. **Clean up broken links** - Remove non-functional symlinks
4. **Back up configuration** - Save `managed_symlinks.json` if important
5. **Document changes** - Update notes when symlinks are modified

## Keyboard Shortcuts

- **Refresh**: F5 (in Manage tab)
- **Delete**: Delete key (select first, then press Delete)
- **Edit**: Double-click on notes column (planned feature)

## Limitations

- Currently cannot edit target paths (recreate if needed)
- Batch delete not yet available
- Cannot directly edit source path

## Future Enhancements

Planned features for future versions:
- [ ] Edit target path without recreating
- [ ] Batch operations (delete multiple at once)
- [ ] Export symlink list
- [ ] Import symlink list
- [ ] Automatic backup of tracking file
- [ ] Symlink verification scheduling
- [ ] Symlink restoration from trash

## Tips & Tricks

### Organize by Notes

Create a naming system in notes:
- `[WORK] Project X`
- `[BACKUP] Database`
- `[CONFIG] System settings`

### Monitor Regularly

Set a reminder to:
1. Check the **Manage** tab
2. Verify symlinks with "Verify All"
3. Update notes as needed

### Quick Reference

Create a note document:
```
Active Symlinks:
1. Desktop/Project → /Users/username/Projects
2. Backup/Data → /Volumes/ExternalDrive/Data
3. Config → /etc/app-config
```

## Support

For issues with symlink management:
1. Check the **Verify All** report
2. Review symlink status in the table
3. Ensure sufficient disk space and permissions
4. Check application logs

---

**Last Updated**: July 4, 2026
**Feature Version**: 1.0.0
