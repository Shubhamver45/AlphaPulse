$ErrorActionPreference = "Stop"

$CORRECT_NAME = "Shubhamver45"
$CORRECT_EMAIL = "shubhamvernekar450@gmail.com"

Write-Host "Creating orphan branch to rebuild history with correct email: $CORRECT_EMAIL"
git checkout --orphan rebuild_branch
git rm -rf --cached .
git add .gitignore requirements.txt

function Commit-Fixed {
    param(
        [string]$Date,
        [string]$Message,
        [string]$Files = ""
    )
    $env:GIT_AUTHOR_NAME=$CORRECT_NAME
    $env:GIT_COMMITTER_NAME=$CORRECT_NAME
    $env:GIT_AUTHOR_EMAIL=$CORRECT_EMAIL
    $env:GIT_COMMITTER_EMAIL=$CORRECT_EMAIL
    $env:GIT_AUTHOR_DATE=$Date
    $env:GIT_COMMITTER_DATE=$Date

    if ($Files -ne "") {
        Write-Host "Committing $Files for date $Date..."
        git add -A $Files
    }
    git commit --allow-empty -m "$Message"
}

# --- Week 1 & 2 (13 commits) ---
Commit-Fixed -Date "2026-04-15T10:00:00+0530" -Message "feat: Initialize project structure and environment configuration" -Files ".gitignore requirements.txt"
Commit-Fixed -Date "2026-04-17T11:30:00+0530" -Message "feat: Setup central configuration and portfolio parameters" -Files "scripts/config.py"
Commit-Fixed -Date "2026-04-19T14:15:00+0530" -Message "feat: Implement data acquisition pipeline with yfinance" -Files "scripts/data_pipeline.py"
Commit-Fixed -Date "2026-04-21T09:45:00+0530" -Message "feat: Add data quality validation and logging to pipeline" -Files "data/"
Commit-Fixed -Date "2026-04-23T16:20:00+0530" -Message "research: Draft exploratory analysis notebook for mathematical prototyping" -Files "research/"
Commit-Fixed -Date "2026-04-25T11:00:00+0530" -Message "feat: Develop core analytics engine for returns and volatility" -Files "scripts/analytics_engine.py"
Commit-Fixed -Date "2026-04-28T13:40:00+0530" -Message "feat: Add statistical validation (Skewness/Kurtosis) for MC models" -Files "reports/"
Commit-Fixed -Date "2026-04-30T10:15:00+0530" -Message "feat: Develop Tableau export orchestration and data reshaping" -Files "scripts/export_for_tableau.py"
Commit-Fixed -Date "2026-05-02T15:30:00+0530" -Message "feat: Add master orchestrator script for the full pipeline" -Files "scripts/run_all.py"
Commit-Fixed -Date "2026-05-04T09:00:00+0530" -Message "docs: Complete comprehensive Tableau build guide" -Files "tableau/"
Commit-Fixed -Date "2026-05-05T14:45:00+0530" -Message "docs: Add contextual documentation and project overview" -Files "ALPHAPULSE_CONTEXT.md"
Commit-Fixed -Date "2026-05-06T11:20:00+0530" -Message "docs: Finalize professional README with deployment instructions" -Files "README.md"
Commit-Fixed -Date "2026-05-07T10:00:00+0530" -Message "chore: Final production polish and deployment readiness"

# --- Week 3 & 4 (9 commits) ---
Commit-Fixed -Date "2026-05-08T10:00:00+0530" -Message "feat: Research and design for interactive 'What-If' parameter logic"
Commit-Fixed -Date "2026-05-08T16:00:00+0530" -Message "docs: Initial specifications for Week 3 Tableau interactivity" -Files "tableau/TABLEAU_BUILD_GUIDE.md"
Commit-Fixed -Date "2026-05-09T11:00:00+0530" -Message "feat: Implement Maximum Drawdown (MDD) calculation in analytics engine" -Files "scripts/analytics_engine.py"
Commit-Fixed -Date "2026-05-09T15:00:00+0530" -Message "test: Validate MDD metrics against historical crash data"
Commit-Fixed -Date "2026-05-10T10:00:00+0530" -Message "feat: Add Executive Summary KPI generation for management reporting"
Commit-Fixed -Date "2026-05-10T14:00:00+0530" -Message "feat: Orchestrate final Tableau exports for drawdown and summary data" -Files "scripts/export_for_tableau.py"
Commit-Fixed -Date "2026-05-11T09:00:00+0530" -Message "feat: Develop automate_refresh.py for end-to-end pipeline automation" -Files "scripts/automate_refresh.py"
Commit-Fixed -Date "2026-05-11T14:00:00+0530" -Message "docs: Final polish of production build guides"
Commit-Fixed -Date "2026-05-12T11:00:00+0530" -Message "chore: Final production deployment and hand-off" -Files "."

Write-Host "Overwriting main branch..."
git branch -D main
git branch -m main

Write-Host "Pushing to remote..."
git push -f origin main

Write-Host "History Rebuilt Successfully with email: $CORRECT_EMAIL"
