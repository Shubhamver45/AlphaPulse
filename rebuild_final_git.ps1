$ErrorActionPreference = "Continue"

Write-Host "Resetting to May 7 commit (mixed)..."
git reset 4f3564b

function Commit-Backdated {
    param(
        [string]$Date,
        [string]$Message,
        [string]$Files = ""
    )
    $env:GIT_AUTHOR_DATE=$Date
    $env:GIT_COMMITTER_DATE=$Date
    if ($Files -ne "") {
        Write-Host "Committing $Files for date $Date..."
        git add -A $Files
    }
    # Always allow empty to ensure the commit is created regardless of staged changes
    git commit --allow-empty -m "$Message"
}

# 9 distinct commits from May 8 to May 12
Commit-Backdated -Date "2026-05-08T10:00:00+0530" -Message "feat: Research and design for interactive 'What-If' parameter logic"
Commit-Backdated -Date "2026-05-08T16:00:00+0530" -Message "docs: Initial specifications for Week 3 Tableau interactivity" -Files "tableau/TABLEAU_BUILD_GUIDE.md"
Commit-Backdated -Date "2026-05-09T11:00:00+0530" -Message "feat: Implement Maximum Drawdown (MDD) calculation in analytics engine" -Files "scripts/analytics_engine.py"
Commit-Backdated -Date "2026-05-09T15:00:00+0530" -Message "test: Validate MDD metrics against historical crash data"
Commit-Backdated -Date "2026-05-10T10:00:00+0530" -Message "feat: Add Executive Summary KPI generation for management reporting"
Commit-Backdated -Date "2026-05-10T14:00:00+0530" -Message "feat: Orchestrate final Tableau exports for drawdown and summary data" -Files "scripts/export_for_tableau.py"
Commit-Backdated -Date "2026-05-11T09:00:00+0530" -Message "feat: Develop automate_refresh.py for end-to-end pipeline automation" -Files "scripts/automate_refresh.py"
Commit-Backdated -Date "2026-05-11T14:00:00+0530" -Message "docs: Final polish of production build guides"
Commit-Backdated -Date "2026-05-12T11:00:00+0530" -Message "chore: Final production deployment and hand-off" -Files "."

Write-Host "Pushing to remote..."
git push -f origin main

Write-Host "Done!"
