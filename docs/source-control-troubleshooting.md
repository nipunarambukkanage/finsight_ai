# Source control troubleshooting

The Git repository is the folder `C:\Users\Admin\NSR\cdazz\finsight_ai`. The
active editor file shown in the IDE is under
`C:\Users\Admin\.codex\attachments`, which is a different folder and does not
contain this repository. Open the repository folder itself in the IDE.

The current local branch is `main` and its remote is:

```text
https://github.com/nipunarambukkanage/finsight_ai.git
```

GitHub only shows commits that have been pushed. Use `git status` to see local
work, then review and publish it with:

```powershell
Set-Location C:\Users\Admin\NSR\cdazz\finsight_ai
git status
git add .
git commit -m "Prepare assessment deliverables and walkthrough guide"
git push origin main
```

Before pushing, check the staged file list and confirm that no credential files
are included. In the IDE, enable the Source Control view's untracked-file
display if it is hidden. Do not initialize a second repository; the existing
`.git` directory is already correct.
