# issuePhorge Changelog

All notable changes to this project will be documented in this file. The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

### Added

- [Feature Name]: Description of the new feature being worked on.

### Changed

- [Component]: Description of what existing behavior was altered.

## [v1.0.0] - 2026-05-22

### Added

- Initial Release: Core functionality to convert Markdown outline/task lists into Gitea/GitHub issues.
- Interactive terminal configuration with persistent settings saved to `issuePhorge.conf`.
- Automatic repository label fetching and ID mapping.
- **TEST MODE**: Create only the first parsed issue to verify formatting and connection.
- **FULL MODE**: Batch create all parsed issues at once with regular continuation prompts.
- **FINIKY MODE**: Selectively choose which parsed headers to convert to issues via comma-separated selection.
- Support for ignoring specific header patterns (e.g., `# Phase`).
- Option to assign default users and labels to newly created issues.