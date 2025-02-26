# issuePhorge

A simple yet powerful Python utility that converts Markdown task lists into Gitea/GitHub issues.

## Overview

issuePhorge is designed to streamline the process of converting structured Markdown documents into formal issues in your Git repository. It's particularly useful for teams who plan in Markdown and want to seamlessly transfer their planning documents into actionable tasks in their issue tracking system.

## Features

- **Header-Based Issue Creation**: Automatically converts specified header levels in your Markdown file into issue titles
- **Smart Content Parsing**: Uses everything between headers as the issue body, including task lists and code blocks
- **Flexible Header Selection**: Choose which header level (H1, H2, H3, etc.) should be treated as issue titles
- **Multiple Operating Modes**:
  - **TEST MODE**: Create only the first issue to verify configuration
  - **FULL MODE**: Create all issues at once
  - **FINIKY MODE**: Selectively choose which headers to convert to issues
- **Configuration Management**: Save your settings in `issuePhorge.conf` for future use
- **Automatic Label Handling**: Fetches and displays available labels from your repository and automatically maps label names to required IDs
- **Customizable Issue Parameters**: Set assignees and labels for created issues

## Requirements

- Python 3.6+
- Access to a Gitea or GitHub repository with appropriate permissions
- A valid API token for your Git service

## Installation

1. Download the `issuePhorge.py` script to your local machine
2. Make it executable:
   ```bash
   chmod +x issuePhorge.py
   ```
3. Run the script:
   ```bash
   ./issuePhorge.py
   ```

## Configuration

When you first run issuePhorge, you'll be prompted to configure various settings:

1. **Input File**: Path to your Markdown file containing tasks
2. **Header Level**: Which header level to use for issue titles (e.g., H1, H2, H3, etc.)
3. **Repository API URL**: The complete URL to your repository's Issues API endpoint
   - For Gitea: `https://your-gitea-instance.com/api/v1/repos/username/repository/issues`
   - For GitHub: `https://api.github.com/repos/username/repository/issues`
4. **API Token**: Your personal access token for the Git service
5. **Headers to Ignore**: Patterns for headers that should be excluded (e.g., "# Phase")
6. **Issue Assignee**: Default username to assign issues to
7. **Label Name**: Name of the label to apply to issues

All settings are saved to `issuePhorge.conf` in the same directory as the script.

## Usage

### Preparing Your Markdown File

Structure your Markdown file with consistent header levels. For example:

```markdown
# Project Overview

This is an overview of the project and won't become an issue.

## 1.1 Initial Repository Setup

### 1.1.1 Create Basic Structure
- [ ] Initialize git repository
- [ ] Add README.md with project description
- [ ] Create .gitignore file

## 1.2 Documentation Setup

### 1.2.1 Create Wiki Pages
- [ ] Create Project Overview page
- [ ] Add Development Guidelines
```

In this example, if you choose level 2 (##) as your header level, "1.1 Initial Repository Setup" and "1.2 Documentation Setup" will become issue titles, and everything beneath each until the next level 2 header will be included in the issue body.

### Running the Script

1. Execute `./issuePhorge.py`
2. Choose whether to use existing configuration or set up manually
3. If configuring manually, follow the prompts to set your preferences
4. Select an operating mode:
   - **TEST MODE**: Creates only the first issue
   - **FULL MODE**: Creates all issues
   - **FINIKY MODE**: Lets you choose specific headers to convert

### Example Workflow

1. Plan your project in a Markdown file with structured headers and task lists
2. Run issuePhorge and select your header level (e.g., ## for level 2 headers)
3. Configure your Git repository API details and preferences
4. Use TEST MODE to verify the first issue looks good
5. Use FULL MODE or FINIKY MODE to create the remaining issues
6. Check your repository's issue tracker to see the newly created issues

## Advanced Features

### Ignoring Specific Headers

You can specify header patterns to ignore, such as section dividers or overview sections that you don't want to convert to issues.

### Label Management

issuePhorge fetches all available labels from your repository and displays them for you to choose from. You only need to provide the label name - the script automatically handles finding and using the correct label ID required by the API.

### Batch Processing

When creating multiple issues, issuePhorge asks for confirmation every few issues, allowing you to monitor the creation process and stop if needed.

## Troubleshooting

- **API Connection Issues**: Verify your API URL and token are correct
- **No Headers Found**: Ensure your Markdown file contains headers at the level you selected
- **Label Not Found**: Check that the label name exactly matches one in your repository
- **Unexpected Formatting**: View the issue in TEST MODE before creating all issues

## License

issuePhorge is licensed under the GNU General Public License v3.0 (GPL-3.0). This means you can freely use, modify, and distribute this software, provided that:

1. You disclose the source code of your modifications
2. You license your modifications under the same GPL-3.0 license
3. You preserve the original copyright notices and disclaimers

See the LICENSE file for the complete text of the GPL-3.0 license.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on the project repository.

## Acknowledgments

issuePhorge was created to simplify the workflow of converting planning documents into actionable issues. Special thanks to all who contributed to its development and testing.
