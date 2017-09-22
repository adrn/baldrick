import time
from changebot.github_api import IssueHandler, RepoHandler


ISSUE_CLOSE_WARNING = """
Hi humans :wave: - this issue was labeled as **Close?** approximately 5 months ago. So..... any news? :newspaper_roll:

If you think this issue should not be closed, a maintainer should remove the **Close?** label - otherwise, I'm just gonna have to close this issue in a month. Your time starts now! Tick tock :clock10:

*If you believe I commented on this issue incorrectly, please report this [here](https://github.com/astropy/astropy-bot/issues)*
"""


def is_close_warning(message):
    return 'Hi humans :wave: - this issue was labeled as **Close?**' in message


ISSUE_CLOSE_EPILOGUE = """
:alarm_clock: Time's up! :alarm_clock:

I'm going to close this issue as per my previous message. But if you feel that we should really really keep this open, then feel free to re-open and remove the **Close?** label. But no one has done anything for 6 months, so... Just sayin!

*If this is the first time I am commenting on this issue, or if you believe I closed this issue incorrectly, please report this [here](https://github.com/astropy/astropy-bot/issues)*
"""


def is_close_epilogue(message):
    return ":alarm_clock: Time's up! :alarm_clock:" in message


def process_issues(repository, installation):

    from .webapp import app

    now = time.time()

    # Get issues labeled as 'Close?'
    repo = RepoHandler(repository, 'master', installation)
    issuelist = repo.get_issues('open', 'Close?')

    for n in issuelist:

        print(f'Checking {n}')

        issue = IssueHandler(repository, n, installation)
        labeled_time = issue.get_label_added_date('Close?')
        if labeled_time is None:
            continue

        dt = now - labeled_time

        if app.stale_issue_close and dt > app.stale_issue_close_seconds:
            comment_ids = issue.find_comments('astropy-bot[bot]', filter_keep=is_close_epilogue)
            if len(comment_ids) == 0:
                print(f'-> CLOSING issue {n}')
                issue.submit_comment(ISSUE_CLOSE_EPILOGUE)
                issue.close()
            else:
                print(f'-> Skipping issue {n} (already closed)')
        elif dt > app.stale_issue_warn_seconds:
            comment_ids = issue.find_comments('astropy-bot[bot]', filter_keep=is_close_warning)
            if len(comment_ids) == 0:
                print(f'-> WARNING issue {n}')
                issue.submit_comment(ISSUE_CLOSE_WARNING)
            else:
                print(f'-> Skipping issue {n} (already warned)')
        else:
            print(f'-> OK issue {n}')
